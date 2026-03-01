"""SSH tunnel + remote/local opencode serve lifecycle manager."""

from __future__ import annotations

import logging
import random
import secrets
import shutil
import subprocess
import time
import os
from pathlib import Path
from typing import Any

from config import (
    HEALTH_CHECK_TIMEOUT,
    REMOTE_PORT_MAX,
    REMOTE_PORT_MIN,
    SSH_RETRY_DELAY,
    SSH_RETRY_MAX,
)
from opencode_client import OpenCodeClient, OpenCodeError

log = logging.getLogger(__name__)


class SSHTunnelError(Exception):
    """SSH tunnel or remote process errors."""


class FolderNotFoundError(SSHTunnelError):
    """Remote folder does not exist and no clone URL provided."""


class RemoteOpenCode:
    """Manage the full lifecycle of a remote opencode serve instance.

    1. (Optional) git clone on remote if folder missing
    2. Launch opencode serve on remote via SSH (localhost-only)
    3. Establish SSH tunnel for local access
    4. Health-check until ready
    5. Teardown on completion or failure
    6. Retry with fresh port+password on disconnect
    """

    def __init__(
        self,
        host: str,
        folder: str,
        clone_url: str | None = None,
    ) -> None:
        self.host = host
        self.folder = folder
        self.clone_url = clone_url

        self._remote_port: int = 0
        self._local_port: int = 0
        self._password: str = ""
        self._serve_proc: subprocess.Popen[bytes] | None = None
        self._tunnel_proc: subprocess.Popen[bytes] | None = None
        self._client: OpenCodeClient | None = None

    @property
    def client(self) -> OpenCodeClient | None:
        return self._client

    @property
    def local_port(self) -> int:
        return self._local_port

    @property
    def remote_port(self) -> int:
        return self._remote_port

    @property
    def password(self) -> str:
        return self._password

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> OpenCodeClient:
        """Launch remote opencode serve + SSH tunnel. Returns a ready client."""
        self._remote_port = random.randint(REMOTE_PORT_MIN, REMOTE_PORT_MAX)
        self._local_port = random.randint(REMOTE_PORT_MIN, REMOTE_PORT_MAX)
        self._password = secrets.token_urlsafe(32)

        # Ensure folder exists (clone if needed)
        self._ensure_folder()

        # Launch remote opencode serve
        self._start_remote_serve()

        # Establish SSH tunnel
        self._start_tunnel()

        # Wait for health
        self._client = OpenCodeClient(
            f"http://127.0.0.1:{self._local_port}",
            self._password,
        )
        if not self._client.wait_healthy(timeout=HEALTH_CHECK_TIMEOUT):
            self.kill()
            raise SSHTunnelError(
                f"opencode serve on {self.host} did not become healthy "
                f"within {HEALTH_CHECK_TIMEOUT}s"
            )

        log.info(
            "Remote opencode ready: %s:%d → localhost:%d",
            self.host,
            self._remote_port,
            self._local_port,
        )
        return self._client

    def is_alive(self) -> bool:
        """Check if both SSH processes are still running."""
        if self._tunnel_proc and self._tunnel_proc.poll() is not None:
            return False
        if self._serve_proc and self._serve_proc.poll() is not None:
            return False
        if self._client:
            try:
                return self._client.health()
            except OpenCodeError:
                return False
        return False

    def kill(self) -> None:
        """Tear down tunnel and remote serve process."""
        # Kill local tunnel
        if self._tunnel_proc:
            try:
                self._tunnel_proc.terminate()
                self._tunnel_proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    self._tunnel_proc.kill()
                except ProcessLookupError:
                    pass
            self._tunnel_proc = None

        # Kill local serve-over-ssh process
        if self._serve_proc:
            try:
                self._serve_proc.terminate()
                self._serve_proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    self._serve_proc.kill()
                except ProcessLookupError:
                    pass
            self._serve_proc = None

        # Kill remote opencode serve (best effort)
        if self._remote_port:
            try:
                subprocess.run(
                    [
                        "ssh",
                        self.host,
                        f"pkill -f 'opencode serve --port {self._remote_port}'",
                    ],
                    timeout=10,
                    capture_output=True,
                )
            except (subprocess.TimeoutExpired, OSError):
                pass

        self._client = None
        log.info("Killed remote opencode on %s (port %d)", self.host, self._remote_port)

    def restart(self) -> OpenCodeClient:
        """Kill and re-launch with fresh port + password. Raises after max retries."""
        last_error: Exception | None = None

        for attempt in range(1, SSH_RETRY_MAX + 1):
            log.info(
                "Restart attempt %d/%d for %s",
                attempt,
                SSH_RETRY_MAX,
                self.host,
            )
            self.kill()
            time.sleep(SSH_RETRY_DELAY)
            try:
                return self.start()
            except SSHTunnelError as e:
                last_error = e
                log.warning("Restart attempt %d failed: %s", attempt, e)

        raise SSHTunnelError(
            f"Failed to restart after {SSH_RETRY_MAX} attempts on {self.host}: "
            f"{last_error}"
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_folder(self) -> None:
        """Check if remote folder exists; clone if clone_url provided."""
        result = subprocess.run(
            ["ssh", self.host, f"test -d {self.folder}"],
            capture_output=True,
            timeout=30,
        )

        if result.returncode == 0:
            return  # Folder exists

        if self.clone_url:
            log.info("Cloning %s on %s → %s", self.clone_url, self.host, self.folder)
            clone_result = subprocess.run(
                [
                    "ssh",
                    self.host,
                    f"git clone {self.clone_url} {self.folder}",
                ],
                capture_output=True,
                timeout=120,
                text=True,
            )
            if clone_result.returncode != 0:
                raise SSHTunnelError(
                    f"git clone failed on {self.host}: {clone_result.stderr}"
                )
            return

        raise FolderNotFoundError(
            f"Folder '{self.folder}' not found on {self.host}. "
            "Add a 'Clone: <git_url>' line to the task content, "
            "or create the folder manually."
        )

    def _start_remote_serve(self) -> None:
        """Launch opencode serve on the remote host via SSH."""
        cmd = [
            "ssh",
            self.host,
            (
                f"cd {self.folder} && "
                f"OPENCODE_SERVER_PASSWORD={self._password} "
                f"opencode serve "
                f"--port {self._remote_port} "
                f"--hostname 127.0.0.1"
            ),
        ]

        self._serve_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        # Give it a moment to start
        time.sleep(2)

        if self._serve_proc.poll() is not None:
            stderr = (self._serve_proc.stderr or b"").read() if self._serve_proc.stderr else b""
            err_text = stderr.decode(errors="replace") if isinstance(stderr, bytes) else str(stderr)
            raise SSHTunnelError(
                f"opencode serve exited immediately on {self.host}: {err_text}"
            )

    def _start_tunnel(self) -> None:
        """Establish SSH tunnel: local_port → remote 127.0.0.1:remote_port."""
        cmd = [
            "ssh",
            "-N",  # no remote command
            "-L",
            f"{self._local_port}:127.0.0.1:{self._remote_port}",
            self.host,
        ]

        self._tunnel_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        # Give tunnel a moment
        time.sleep(1)

        if self._tunnel_proc.poll() is not None:
            stderr = (self._tunnel_proc.stderr or b"").read() if self._tunnel_proc.stderr else b""
            err_text = stderr.decode(errors="replace") if isinstance(stderr, bytes) else str(stderr)
            raise SSHTunnelError(
                f"SSH tunnel to {self.host} failed: {err_text}"
            )



# ---------------------------------------------------------------------------
# Local variant (no SSH)
# ---------------------------------------------------------------------------


class LocalOpenCode:
    """Manage a local opencode serve instance (same machine, no SSH).

    Same public interface as RemoteOpenCode so the dispatcher can use either
    interchangeably.

    1. (Optional) git clone if folder missing
    2. Launch opencode serve locally on a random port
    3. Health-check until ready
    4. Teardown on completion or failure
    5. Retry with fresh port+password
    """

    def __init__(
        self,
        folder: str,
        clone_url: str | None = None,
    ) -> None:
        self.host = "local"
        self.folder = folder
        self.clone_url = clone_url

        self._port: int = 0
        self._password: str = ""
        self._serve_proc: subprocess.Popen[bytes] | None = None
        self._client: OpenCodeClient | None = None

    @property
    def client(self) -> OpenCodeClient | None:
        return self._client

    @property
    def local_port(self) -> int:
        return self._port

    @property
    def remote_port(self) -> int:
        # For interface compat — local has no separate remote port
        return self._port

    @property
    def password(self) -> str:
        return self._password

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> OpenCodeClient:
        """Launch local opencode serve. Returns a ready client."""
        self._port = random.randint(REMOTE_PORT_MIN, REMOTE_PORT_MAX)
        self._password = secrets.token_urlsafe(32)

        self._ensure_folder()
        self._start_serve()

        self._client = OpenCodeClient(
            f"http://127.0.0.1:{self._port}",
            self._password,
        )
        if not self._client.wait_healthy(timeout=HEALTH_CHECK_TIMEOUT):
            self.kill()
            raise SSHTunnelError(
                f"Local opencode serve did not become healthy "
                f"within {HEALTH_CHECK_TIMEOUT}s"
            )

        log.info("Local opencode ready on port %d in %s", self._port, self.folder)
        return self._client

    def is_alive(self) -> bool:
        """Check if the local serve process is still running."""
        if self._serve_proc and self._serve_proc.poll() is not None:
            return False
        if self._client:
            try:
                return self._client.health()
            except OpenCodeError:
                return False
        return False

    def kill(self) -> None:
        """Terminate the local opencode serve process."""
        if self._serve_proc:
            try:
                self._serve_proc.terminate()
                self._serve_proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    self._serve_proc.kill()
                except ProcessLookupError:
                    pass
            self._serve_proc = None

        self._client = None
        log.info("Killed local opencode (port %d)", self._port)

    def restart(self) -> OpenCodeClient:
        """Kill and re-launch with fresh port + password."""
        last_error: Exception | None = None

        for attempt in range(1, SSH_RETRY_MAX + 1):
            log.info("Local restart attempt %d/%d", attempt, SSH_RETRY_MAX)
            self.kill()
            time.sleep(SSH_RETRY_DELAY)
            try:
                return self.start()
            except SSHTunnelError as e:
                last_error = e
                log.warning("Local restart attempt %d failed: %s", attempt, e)

        raise SSHTunnelError(
            f"Failed to restart local opencode after {SSH_RETRY_MAX} attempts: "
            f"{last_error}"
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_folder(self) -> None:
        """Check if local folder exists; clone if clone_url provided."""
        folder_path = Path(os.path.expanduser(self.folder))

        if folder_path.is_dir():
            return

        if self.clone_url:
            log.info("Cloning %s → %s", self.clone_url, folder_path)
            clone_result = subprocess.run(
                ["git", "clone", self.clone_url, str(folder_path)],
                capture_output=True,
                timeout=120,
                text=True,
            )
            if clone_result.returncode != 0:
                raise SSHTunnelError(
                    f"git clone failed locally: {clone_result.stderr}"
                )
            return

        raise FolderNotFoundError(
            f"Folder '{self.folder}' not found locally. "
            "Add a 'Clone: <git_url>' line to the task content, "
            "or create the folder manually."
        )

    def _start_serve(self) -> None:
        """Launch opencode serve on this machine."""
        folder_path = os.path.expanduser(self.folder)

        env = os.environ.copy()
        env["OPENCODE_SERVER_PASSWORD"] = self._password

        cmd = [
            "opencode", "serve",
            "--port", str(self._port),
            "--hostname", "127.0.0.1",
        ]

        self._serve_proc = subprocess.Popen(
            cmd,
            cwd=folder_path,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        # Give it a moment to start
        time.sleep(2)

        if self._serve_proc.poll() is not None:
            stderr = (
                (self._serve_proc.stderr or b"").read()
                if self._serve_proc.stderr
                else b""
            )
            err_text = (
                stderr.decode(errors="replace")
                if isinstance(stderr, bytes)
                else str(stderr)
            )
            raise SSHTunnelError(
                f"Local opencode serve exited immediately: {err_text}"
            )