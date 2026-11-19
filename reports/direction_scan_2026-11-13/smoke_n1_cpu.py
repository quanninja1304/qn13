"""Tiny installation checks only: no N1 or C1 hypothesis is tested here."""
import os
os.environ.setdefault('JAX_PLATFORMS', 'cpu')
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '-1')
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('MKL_NUM_THREADS', '2')
os.environ.setdefault('TF_NUM_INTRAOP_THREADS', '2')
os.environ.setdefault('TF_NUM_INTEROP_THREADS', '1')
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
os.environ.setdefault('HF_HUB_OFFLINE', '1')

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/n1_models_cpu'
parser = argparse.ArgumentParser()
parser.add_argument('model', choices=['imports', 'avici', 'cdfm', 'foundcause'])
args = parser.parse_args()
start = time.perf_counter()
result = {'check': args.model, 'purpose': 'installation_smoke_only', 'status': 'running'}

try:
    import numpy as np
    import psutil
    rng = np.random.default_rng(13)
    x = rng.normal(size=(32, 3)).astype(np.float32)
    if args.model == 'imports':
        import importlib.metadata as md
        import jax
        import torch
        import avici
        import cdfm
        import causallearn
        result['versions'] = {n: md.version(n) for n in ['jax', 'jaxlib', 'torch', 'numpy', 'avici', 'cdfm-base', 'dm-haiku', 'optax', 'tensorflow']}
        result['jax_devices'] = [str(d) for d in jax.devices()]
        result['torch_cuda_build'] = torch.version.cuda
        assert torch.version.cuda is None
        assert all(d.platform == 'cpu' for d in jax.devices())
    elif args.model == 'avici':
        import avici
        model = avici.load_pretrained(checkpoint_dir=str(BASE/'checkpoints/avici/scm-v0'), expects_counts=False)
        p = np.asarray(model(x=x))
        result['output_shape'] = list(p.shape)
        result['finite'] = bool(np.isfinite(p).all())
        assert p.shape == (3, 3) and result['finite']
    elif args.model == 'cdfm':
        import torch
        from cdfm import CDFM
        torch.set_num_threads(2)
        model = CDFM.from_pretrained(str(BASE/'checkpoints/cdfm'), device='cpu')
        output = model.predict(x, threshold=0.5)
        result['output_shape'] = list(output.probabilities.shape)
        result['finite'] = bool(np.isfinite(output.probabilities).all())
        assert output.probabilities.shape == (3, 3) and result['finite']
    else:
        import torch
        torch.set_num_threads(2)
        sys.path.insert(0, str(BASE/'repos/foundcause'))
        from foundcause import ModelConfig, CausalDiscoveryTransformer, predict
        # mmap + meta avoids allocating a second 139M-parameter copy.
        checkpoint = torch.load(BASE/'checkpoints/foundcause/checkpoint.pt', map_location='cpu', weights_only=True, mmap=True)
        with torch.device('meta'):
            model = CausalDiscoveryTransformer(ModelConfig())
        model.load_state_dict(checkpoint['model_state_dict'], strict=True, assign=True)
        model.eval()
        result['parameters'] = sum(p.numel() for p in model.parameters())
        with torch.inference_mode():
            output = predict(model, x, torch.device('cpu'), n_runs=1, max_samples=32)
        p = np.asarray(output['probabilities'])
        result['output_shape'] = list(p.shape)
        result['finite'] = bool(np.isfinite(p).all())
        assert p.shape == (3, 3) and result['finite']
    result['status'] = 'passed'
    result['rss_bytes_at_end'] = psutil.Process().memory_info().rss
except Exception as exc:
    import traceback
    result['status'] = 'failed'
    result['error'] = repr(exc)
    result['traceback'] = traceback.format_exc()
finally:
    result['seconds'] = time.perf_counter() - start
    target = BASE/'logs'/f'smoke_{args.model}.json'
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)
if result['status'] != 'passed':
    sys.exit(1)
