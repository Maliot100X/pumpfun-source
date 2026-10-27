#!/usr/bin/env python3
"""Verify the selected main-Pump source against its sealed, reproduced checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'repro/pump/main-contract-round35-20261027'
MANIFEST_SHA256 = '0f25225d54c4438bc5062656219440b305c5e9f3a128bf4c6b2e1ac638ffe649'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    root = Path(root).resolve()
    package = root / PACKAGE
    assert sha(package / 'MANIFEST.json') == MANIFEST_SHA256
    checkpoint = json.loads((package / 'CHECKPOINT.json').read_text())
    status = json.loads((root / 'repro/status.json').read_text())['pump']
    assert status['candidate_artifact'] == PACKAGE + '/candidate.so'
    assert status['candidate_sha256'] == checkpoint['candidate_sha256']
    assert status['symbols_sha256'] == checkpoint['unstripped_sha256']
    assert not status['full_byte_equality'] and not checkpoint['goal_complete']
    for name, expected in checkpoint['primary_source_sha256'].items():
        path = root / 'programs/pump' / name
        assert not path.is_symlink() and sha(path) == expected, name
    actual = {str(path.relative_to(root / 'programs/pump'))
              for path in (root / 'programs/pump').rglob('*')
              if path.is_file() and not {'target', '.git'}.intersection(path.parts)
              and (path.suffix == '.rs' or path.name in ('Cargo.toml', 'Cargo.lock'))}
    assert actual == set(checkpoint['primary_source_sha256'])
    subprocess.run([sys.executable, '-B', str(package / 'verify.py')],
                   cwd=root, check=True)
    return {'status': 'PASS', 'program': 'pump',
            'candidate_sha256': checkpoint['candidate_sha256'],
            'source_files': len(actual),
            'normalized_windows': checkpoint['normalized_windows'],
            'original_windows': checkpoint['original_windows'],
            'whole_elf_equal': False, 'goal_complete': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(verify(args.repo), indent=2))
