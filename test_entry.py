#!/usr/bin/env python3
"""Checks for the news-image-20261122 entry.

Runs main.py twice into two fresh directories and asserts:
  - both runs write entry.png,
  - the two files are byte-identical (deterministic output),
  - the file is at most 1 MiB,
  - it is a whole PNG, 1024x1024 pixels.

Usage: python3 test_entry.py
"""

import hashlib
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BYTES = 1048576


def run_once(outdir):
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    env = dict(os.environ)
    env['MAKEFUN_OUTPUT_DIR'] = outdir
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, 'main.py')],
        env=env, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise SystemExit(f'main.py failed:\n{proc.stdout}\n{proc.stderr}')
    path = os.path.join(outdir, 'entry.png')
    if not os.path.exists(path):
        raise SystemExit(f'main.py wrote no entry.png in {outdir}')
    with open(path, 'rb') as f:
        return f.read()


def check_png(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('not a PNG file')
    if len(data) < 8 + 25:
        raise SystemExit('PNG too short for IHDR')
    width, height = struct.unpack('>II', data[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit(f'dimensions {width}x{height}, expected 1024x1024')
    if data[-12:] != b'\x00\x00\x00\x00IEND\xaeB`\x82':
        raise SystemExit('PNG does not end with a valid IEND chunk')


def main():
    first = run_once(os.path.join(HERE, '.test-out-1'))
    second = run_once(os.path.join(HERE, '.test-out-2'))
    if first != second:
        raise SystemExit('two runs wrote different bytes')
    if len(first) > MAX_BYTES:
        raise SystemExit(f'entry.png is {len(first)} bytes, over 1 MiB')
    check_png(first)
    sha = hashlib.sha256(first).hexdigest()
    print(f'OK: two runs byte-identical, {len(first)} bytes, '
          f'1024x1024 PNG, sha256 {sha}')
    shutil.rmtree(os.path.join(HERE, '.test-out-1'))
    shutil.rmtree(os.path.join(HERE, '.test-out-2'))


if __name__ == '__main__':
    main()
