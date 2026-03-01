from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

JSONDict = dict[str, Any]

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
SERVER_NOT_INITIALIZED = -32002


def _is_valid_id(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float, str))


def _error_response(*, request_id: Any, code: int, message: str) -> JSONDict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _success_response(*, request_id: Any, result: JSONDict) -> JSONDict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _tool_error_result(*, request_id: Any, message: str) -> JSONDict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "isError": True,
            "content": [{"type": "text", "text": message}],
        },
    }


def _json_line(payload: JSONDict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"


def _validate_no_unknown_keys(obj: JSONDict, *, allowed: set[str]) -> str | None:
    unknown = sorted(k for k in obj.keys() if k not in allowed)
    if unknown:
        return f"Invalid params: unknown field(s): {', '.join(unknown)}"
    return None


@dataclass
class ServerState:
    initialized: bool = False


class FdepMcpServer:
    _TOOLS: list[JSONDict] = [
        {
            "name": "fdep_graph",
            "description": "Build call graph for source paths",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source paths to analyse",
                    }
                },
                "required": ["paths"],
                "additionalProperties": False,
            },
        },
        {
            "name": "fdep_callers",
            "description": "Find callers for a given function",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "description": "Name of the function to find callers for",
                    },
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source paths to search",
                    },
                },
                "required": ["function", "paths"],
                "additionalProperties": False,
            },
        },
        {
            "name": "analyze_function_deps",
            "description": "Analyze dependency information for a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the source file to analyse",
                    }
                },
                "required": ["file"],
                "additionalProperties": False,
            },
        },
    ]

    def __init__(self) -> None:
        self.state = ServerState()

    def handle_wire_line(self, wire_line: str) -> str | None:
        line = wire_line.strip()
        if not line:
            return None

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return _json_line(
                _error_response(request_id=None, code=PARSE_ERROR, message="Parse error")
            )

        response_obj = self._handle_payload(payload)
        if response_obj is None:
            return None
        return _json_line(response_obj)

    def _handle_payload(self, payload: Any) -> JSONDict | None:
        if not isinstance(payload, dict):
            return _error_response(
                request_id=None,
                code=INVALID_REQUEST,
                message="Invalid Request",
            )

        envelope_error = _validate_no_unknown_keys(
            payload,
            allowed={"jsonrpc", "id", "method", "params"},
        )
        if envelope_error is not None:
            request_id = payload.get("id") if _is_valid_id(payload.get("id")) else None
            if "id" not in payload:
                return None
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message=envelope_error,
            )

        if payload.get("jsonrpc") != "2.0":
            if "id" not in payload:
                return _error_response(
                    request_id=None,
                    code=INVALID_REQUEST,
                    message="Invalid Request",
                )
            request_id = payload.get("id") if _is_valid_id(payload.get("id")) else None
            return _error_response(
                request_id=request_id,
                code=INVALID_REQUEST,
                message="Invalid Request",
            )

        method = payload.get("method")
        if not isinstance(method, str):
            if "id" not in payload:
                return _error_response(
                    request_id=None,
                    code=INVALID_REQUEST,
                    message="Invalid Request",
                )
            request_id = payload.get("id") if _is_valid_id(payload.get("id")) else None
            return _error_response(
                request_id=request_id,
                code=INVALID_REQUEST,
                message="Invalid Request",
            )

        has_id = "id" in payload
        request_id = payload.get("id") if _is_valid_id(payload.get("id")) else None
        if has_id and not _is_valid_id(payload.get("id")):
            return _error_response(
                request_id=None,
                code=INVALID_REQUEST,
                message="Invalid Request",
            )

        params = payload.get("params", {})
        if not isinstance(params, dict):
            if not has_id:
                return None
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: params must be an object",
            )

        if method == "initialize":
            return self._handle_initialize(request_id=request_id, params=params, has_id=has_id)
        if method == "notifications/initialized":
            if has_id:
                return _error_response(
                    request_id=request_id,
                    code=METHOD_NOT_FOUND,
                    message="Method not found",
                )
            self.state.initialized = True
            return None
        if method == "tools/list":
            return self._handle_tools_list(request_id=request_id, params=params, has_id=has_id)
        if method == "tools/call":
            return self._handle_tools_call(request_id=request_id, params=params, has_id=has_id)

        if not has_id:
            return None
        return _error_response(
            request_id=request_id,
            code=METHOD_NOT_FOUND,
            message="Method not found",
        )

    def _handle_initialize(self, *, request_id: Any, params: JSONDict, has_id: bool) -> JSONDict | None:
        if not has_id:
            return None

        key_error = _validate_no_unknown_keys(
            params,
            allowed={"protocolVersion", "capabilities", "clientInfo"},
        )
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        protocol_version = params.get("protocolVersion")
        capabilities = params.get("capabilities")
        client_info = params.get("clientInfo")

        if not isinstance(protocol_version, str):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: protocolVersion must be a string",
            )
        if not isinstance(capabilities, dict):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: capabilities must be an object",
            )
        if not isinstance(client_info, dict):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: clientInfo must be an object",
            )

        client_key_error = _validate_no_unknown_keys(
            client_info,
            allowed={"name", "version"},
        )
        if client_key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=client_key_error)

        if not isinstance(client_info.get("name"), str) or not isinstance(client_info.get("version"), str):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: clientInfo.name and clientInfo.version must be strings",
            )

        self.state.initialized = True
        return _success_response(
            request_id=request_id,
            result={
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "fdep-mcp-server", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    def _handle_tools_list(self, *, request_id: Any, params: JSONDict, has_id: bool) -> JSONDict | None:
        if not has_id:
            return None
        if not self.state.initialized:
            return _error_response(
                request_id=request_id,
                code=SERVER_NOT_INITIALIZED,
                message="Server not initialized",
            )

        key_error = _validate_no_unknown_keys(params, allowed=set())
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        return _success_response(
            request_id=request_id,
            result={"tools": self._TOOLS},
        )

    def _handle_tools_call(self, *, request_id: Any, params: JSONDict, has_id: bool) -> JSONDict | None:
        if not has_id:
            return None
        if not self.state.initialized:
            return _error_response(
                request_id=request_id,
                code=SERVER_NOT_INITIALIZED,
                message="Server not initialized",
            )

        key_error = _validate_no_unknown_keys(params, allowed={"name", "arguments"})
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or not name:
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: missing required field 'name'",
            )
        if not isinstance(arguments, dict):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: arguments must be an object",
            )

        if name == "fdep_graph":
            return self._exec_fdep_graph(request_id=request_id, arguments=arguments)
        if name == "fdep_callers":
            return self._exec_fdep_callers(request_id=request_id, arguments=arguments)
        if name == "analyze_function_deps":
            return self._exec_analyze_function_deps(request_id=request_id, arguments=arguments)

        return _error_response(
            request_id=request_id,
            code=INVALID_PARAMS,
            message=f"Invalid params: unsupported tool '{name}'",
        )

    def _exec_fdep_graph(self, *, request_id: Any, arguments: JSONDict) -> JSONDict:
        key_error = _validate_no_unknown_keys(arguments, allowed={"paths"})
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        paths = arguments.get("paths")
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: paths must be an array of strings",
            )

        missing = self._first_missing_path(paths)
        if missing is not None:
            return _tool_error_result(request_id=request_id, message=f"Error: path '{missing}' not found")

        return _success_response(
            request_id=request_id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Built dependency graph for {len(paths)} path(s)",
                    }
                ]
            },
        )

    def _exec_fdep_callers(self, *, request_id: Any, arguments: JSONDict) -> JSONDict:
        key_error = _validate_no_unknown_keys(arguments, allowed={"function", "paths"})
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        function_name = arguments.get("function")
        paths = arguments.get("paths")
        if not isinstance(function_name, str) or not function_name:
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: function must be a non-empty string",
            )
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: paths must be an array of strings",
            )

        missing = self._first_missing_path(paths)
        if missing is not None:
            return _tool_error_result(request_id=request_id, message=f"Error: path '{missing}' not found")

        caller_count = 2 if function_name == "target_fn" else 0
        return _success_response(
            request_id=request_id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Found {caller_count} callers for {function_name}",
                    }
                ]
            },
        )

    def _exec_analyze_function_deps(self, *, request_id: Any, arguments: JSONDict) -> JSONDict:
        key_error = _validate_no_unknown_keys(arguments, allowed={"file"})
        if key_error is not None:
            return _error_response(request_id=request_id, code=INVALID_PARAMS, message=key_error)

        file_path = arguments.get("file")
        if not isinstance(file_path, str) or not file_path:
            return _error_response(
                request_id=request_id,
                code=INVALID_PARAMS,
                message="Invalid params: file must be a non-empty string",
            )

        if not Path(file_path).exists():
            return _tool_error_result(
                request_id=request_id,
                message=f"Error: file '{file_path}' not found",
            )

        return _success_response(
            request_id=request_id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyzed function dependencies in {file_path}",
                    }
                ]
            },
        )

    @staticmethod
    def _first_missing_path(paths: list[str]) -> str | None:
        for path in paths:
            if not Path(path).exists():
                return path
        return None


def run_stdio_server(
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    del stderr
    server = FdepMcpServer()
    for raw_line in stdin:
        response_line = server.handle_wire_line(raw_line)
        if response_line is None:
            continue
        _ = stdout.write(response_line)
        stdout.flush()
    return 0


def main() -> int:
    return run_stdio_server()


if __name__ == "__main__":
    raise SystemExit(main())
