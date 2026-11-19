"""Download official, pinned N1 checkpoints; stream to disk and verify hashes.

Run from repo root with a Python environment containing requests.
No model is loaded or executed by this script.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import time
import requests

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'artifacts/n1_models_cpu/checkpoints'
AVICI_REV = '3bcf141a2d016d17d8b4d217de74e7e2a95afbef'
CDFM_REV = 'fd3ac4f72e617c9b2165082493f2494c9f980d04'
JOBS = []
for variant in ('scm-v0', 'neurips-linear', 'neurips-rff', 'neurips-grn'):
    for filename in ('checkpoint_0300000.pkl', 'config.yaml', 'kwargs.json'):
        JOBS.append((f'avici/{variant}/{filename}', f'https://huggingface.co/larslorch/avici/resolve/{AVICI_REV}/{variant}/{filename}', None))
for filename in ('model.safetensors', 'config.json', 'README.md'):
    JOBS.append((f'cdfm/{filename}', f'https://huggingface.co/DMIRLAB/CDFM/resolve/{CDFM_REV}/{filename}', None))
JOBS.append(('foundcause/checkpoint.pt', 'https://github.com/amazon-science/foundcause/releases/download/checkpoint-2026-11/checkpoint.pt', '703defa18043514873fe2a487f6b4498c0492a978c77bba1376f4e02f31edc04'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fetch(job):
    rel, url, expected = job
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.part')
    if not path.exists():
        for attempt in range(3):
            try:
                with requests.get(url, stream=True, timeout=(30, 120)) as response:
                    response.raise_for_status()
                    expected_size = response.headers.get('Content-Length')
                    with tmp.open('wb') as stream:
                        for block in response.iter_content(1024 * 1024):
                            stream.write(block)
                    if expected_size and tmp.stat().st_size != int(expected_size):
                        raise IOError(f'Length mismatch for {rel}')
                tmp.replace(path)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)
    actual = digest(path)
    if expected and actual != expected:
        raise IOError(f'SHA256 mismatch: {rel}')
    result = {'path': path.relative_to(ROOT).as_posix(), 'source_url': url,
              'bytes': path.stat().st_size, 'sha256': actual,
              'publisher_sha256': expected, 'status': 'downloaded_and_hashed'}
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    # Two streams limit pressure on this 8 GB Windows machine.
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(fetch, JOBS))
    manifest = {'avici_revision': AVICI_REV, 'cdfm_revision': CDFM_REV,
                'foundcause_release': 'checkpoint-2026-11', 'files': results,
                'total_bytes': sum(x['bytes'] for x in results)}
    (DEST.parent / 'checkpoint_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
