"""Smoke tests for fdep-mcp-server.

Tests basic import and startup paths for the fdep MCP server.
"""

import pytest
from pathlib import Path


class TestImports:
    """Test basic module imports."""

    def test_compliance_baseline_import(self):
        """Test that compliance baseline module can be imported."""
        from fdep_mcp.compliance_baseline import read_shared_compliance_baseline
        
        assert callable(read_shared_compliance_baseline)

    def test_compliance_baseline_loads(self):
        """Test that compliance baseline can be loaded and contains expected structure."""
        from fdep_mcp.compliance_baseline import read_shared_compliance_baseline
        
        baseline = read_shared_compliance_baseline()
        
        # Verify baseline is a dict
        assert isinstance(baseline, dict)
        
        # Verify baseline has expected top-level keys
        assert "protocol_target" in baseline
        assert "strictness_matrix" in baseline


class TestModuleStructure:
    """Test module structure and organization."""

    def test_fdep_mcp_package_exists(self):
        """Test that fdep_mcp package is properly structured."""
        from fdep_mcp import compliance_baseline
        
        assert compliance_baseline is not None

    def test_baseline_file_path_exists(self):
        """Test that the shared baseline policy file exists."""
        from fdep_mcp.compliance_baseline import SHARED_COMPLIANCE_BASELINE_PATH
        
        assert SHARED_COMPLIANCE_BASELINE_PATH.exists()
        assert SHARED_COMPLIANCE_BASELINE_PATH.is_file()
        assert SHARED_COMPLIANCE_BASELINE_PATH.suffix == ".json"
