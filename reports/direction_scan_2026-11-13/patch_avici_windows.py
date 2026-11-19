"""Two compatibility fixes for pinned AVICI 40fb30d; no inference math changes.

1. Delay the Windows-unavailable Plasma error until an async training buffer is used.
2. Correct the local-checkpoint config assertion to match load_checkpoint().
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / 'artifacts/n1_models_cpu/repos/avici'


def replace_once(relative, old, new):
    path = REPO / relative
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError(f'Unexpected upstream content: {relative}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once('avici/buffer.py', 'import pyarrow.plasma as plasma', '''try:
    import pyarrow.plasma as plasma
except ModuleNotFoundError as exc:
    if exc.name not in {"pyarrow.plasma", "pyarrow._plasma"}:
        raise

    class _UnavailablePlasma:
        def __getattr__(self, name):
            raise RuntimeError(
                "AVICI asynchronous training buffers require pyarrow.plasma, "
                "which is unavailable in the Windows wheel. Pretrained inference "
                "and synchronous simulate_data do not use Plasma."
            )

    plasma = _UnavailablePlasma()''')
replace_once('avici/pretrain.py',
             'assert (root_path.parent / CHECKPOINT_KWARGS).exists()',
             'assert (root_path / CHECKPOINT_KWARGS).exists()')
print('Applied AVICI Windows import and local-path compatibility fixes.')
