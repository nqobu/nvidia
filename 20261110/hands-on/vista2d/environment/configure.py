"""Stage fixed upstream source and checkpoints; no lesson scripts or inference."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path, algorithm):
    result = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(part)
    return result.hexdigest()


def checkpoint(asset):
    path = ROOT / asset['path']
    if path.exists():
        if digest(path, 'md5') != asset['md5']:
            raise RuntimeError('Existing checkpoint differs; preserved: ' + str(path))
        print('Verified existing:', path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.part')
    if temporary.exists():
        raise RuntimeError('Existing partial download preserved: ' + str(temporary))
    try:
        with urllib.request.urlopen(asset['url'], timeout=120) as response, temporary.open('xb') as output:
            while part := response.read(1024 * 1024):
                output.write(part)
        if digest(temporary, 'md5') != asset['md5']:
            raise RuntimeError('Downloaded checkpoint checksum mismatch: ' + asset['name'])
        temporary.replace(path)
        print('Downloaded and verified:', path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-downloads', action='store_true', help='Configure source/Python only; weights must already exist before the lesson.')
    options = parser.parse_args()
    assets = json.loads((ROOT / 'assets.json').read_text())
    source = assets['vista_source']
    target = ROOT / source['path']
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--no-checkout', source['url'], str(target)], check=True)
        subprocess.run(['git', '-C', str(target), 'checkout', source['commit']], check=True)
    revision = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != source['commit']:
        raise RuntimeError('Existing source differs; preserved. Expected: ' + source['commit'])
    if not options.skip_downloads:
        for asset in assets['checkpoints']:
            checkpoint(asset)
    configuration = ROOT / 'classroom.json'
    data = json.loads(configuration.read_text())
    data['vista2d']['python'] = sys.executable
    configuration.write_text(json.dumps(data, indent=2) + '\n')
    print('Configured model Python:', sys.executable)
    print('Next: open notebooks/01_cellular_image_analysis.ipynb with this environment.')


if __name__ == '__main__':
    main()
