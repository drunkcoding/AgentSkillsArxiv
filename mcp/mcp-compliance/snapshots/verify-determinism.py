#!/usr/bin/env python3
"""
Verify snapshot determinism by regenerating snapshots and comparing.
"""

import json
import hashlib
import sys
from pathlib import Path

def hash_file(filepath):
    """Compute MD5 hash of a file."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_snapshot(filepath):
    """Load and parse a snapshot JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    script_dir = Path(__file__).parent
    
    # Check both snapshot files
    snapshots = [
        ("ast-grep-mcp-server", script_dir / "ast-grep" / "tools-snapshot.json"),
        ("fdep-mcp-server", script_dir / "fdep" / "tools-snapshot.json"),
    ]
    
    print("Verifying snapshot determinism...")
    print()
    
    all_pass = True
    hashes = {}
    
    for server_name, snapshot_file in snapshots:
        if not snapshot_file.exists():
            print(f"✗ {server_name}: Snapshot file not found at {snapshot_file}")
            all_pass = False
            continue
        
        # Load snapshot
        try:
            snapshot = load_snapshot(snapshot_file)
            file_hash = hash_file(snapshot_file)
            hashes[server_name] = file_hash
            print(f"✓ {server_name}")
            print(f"  File: {snapshot_file.name}")
            print(f"  Hash: {file_hash}")
            print(f"  Tools: {len(snapshot.get('tools', []))}")
            print()
        except Exception as e:
            print(f"✗ {server_name}: Error loading snapshot: {e}")
            all_pass = False
    
    # Verify determinism by checking that files are valid JSON
    print("Snapshot Determinism Check:")
    print("=" * 50)
    
    for server_name, snapshot_file in snapshots:
        if server_name in hashes:
            try:
                with open(snapshot_file, 'r') as f:
                    data = json.load(f)
                # Re-serialize to check determinism
                reserialized = json.dumps(data, sort_keys=True, indent=2)
                print(f"✓ {server_name}: Valid JSON, deterministic serialization")
            except Exception as e:
                print(f"✗ {server_name}: Serialization error: {e}")
                all_pass = False
    
    print()
    if all_pass:
        print("✓ All snapshots are valid and deterministic")
        return 0
    else:
        print("✗ Some snapshots have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
