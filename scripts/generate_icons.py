#!/usr/bin/env python3
"""Generate proportional icon derivatives on macOS without changing the original.

Uses the system sips utility; normal website builds only copy these assets.
"""
from pathlib import Path
import struct
import subprocess

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
SOURCE = ASSETS / 'AppIcon-1024.png'
if not SOURCE.is_file():
    raise SystemExit(f'Missing official icon: {SOURCE}')

for name, size in [
    ('brand-icon-96.png', 96),
    ('favicon-16x16.png', 16),
    ('favicon-32x32.png', 32),
    ('favicon-48x48.png', 48),
    ('apple-touch-icon.png', 180),
]:
    subprocess.run([
        'sips', '-z', str(size), str(size), str(SOURCE),
        '--out', str(ASSETS / name),
    ], check=True, capture_output=True)

# ICO supports embedded PNG images. Package the exact generated PNG bytes.
sizes = [16, 32, 48]
offset = 6 + 16 * len(sizes)
entries, images = [], []
for size in sizes:
    data = (ASSETS / f'favicon-{size}x{size}.png').read_bytes()
    entries.append(struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(data), offset))
    images.append(data)
    offset += len(data)
(ASSETS / 'favicon.ico').write_bytes(
    struct.pack('<HHH', 0, 1, len(sizes)) + b''.join(entries) + b''.join(images)
)
print('Generated brand icon, 16/32/48px favicons, ICO, and 180px touch icon.')
