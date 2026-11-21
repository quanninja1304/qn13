"""P-N3 (rules v1, locked 2026-11-21 at commit 8d1df20) Part B: attention interventions in AVICI scm-v0.

Installs a subclass of haiku.MultiHeadAttention (same module name 'multi_head_attention', so parameter paths are
unchanged) whose __call__ is a verbatim copy of Haiku 0.0.13 plus intervention hooks:
  PLAIN : no change (must reproduce the original output bitwise, gate B0)
  V0    : value zeroing for target queries -> padding keys: softmax over all keys, then zero those weights
  KO    : attention knockout: mask target-query -> padding-key logits before softmax
Layers are identified by the explicit block index b (call order inside one trace, 0..15): variable axis iff b is even,
layer l = b // 2 + 1 (gate B4 checks the token-axis length). Interventions are applied whenever selected, also without
padding (then the mask is all-True and the multiplier all-ones: gate B3 checks this is a bitwise no-op).
"""
import os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]
ENV = ART / 'n1_models_cpu'

CFG = dict(mode='PLAIN', layers=frozenset(), dT=None, counter=0, record=[])


def _patched_call(self, query, key, value, mask=None):
    import jax, jax.numpy as jnp, haiku as hk
    b = CFG['counter']; CFG['counter'] += 1
    *leading_dims, sequence_length, _ = query.shape
    projection = self._linear_projection
    query_heads = projection(query, self.key_size, "query")
    key_heads = projection(key, self.key_size, "key")
    value_heads = projection(value, self.value_size, "value")
    attn_logits = jnp.einsum("...thd,...Thd->...htT", query_heads, key_heads)
    attn_logits = attn_logits / np.sqrt(self.key_size).astype(key.dtype)
    if mask is not None:
        if mask.ndim != attn_logits.ndim:
            raise ValueError(f"Mask dimensionality {mask.ndim} must match logits dimensionality {attn_logits.ndim}.")
        attn_logits = jnp.where(mask, attn_logits, -1e30)
    var_axis = (b % 2 == 0)
    layer = b // 2 + 1 if var_axis else None
    CFG['record'].append((b, var_axis, int(sequence_length)))
    active = var_axis and CFG['mode'] in ('V0', 'KO') and layer in CFG['layers']
    if active and CFG['mode'] == 'KO':
        keep = np.ones((sequence_length, sequence_length), bool); keep[:CFG['dT'], CFG['dT']:] = False
        attn_logits = jnp.where(keep, attn_logits, -1e30)
    attn_weights = jax.nn.softmax(attn_logits)
    if active and CFG['mode'] == 'V0':
        keep = np.ones((sequence_length, sequence_length), np.float32); keep[:CFG['dT'], CFG['dT']:] = 0.0
        attn_weights = attn_weights * keep
    attn = jnp.einsum("...htT,...Thd->...thd", attn_weights, value_heads)
    attn = jnp.reshape(attn, (*leading_dims, sequence_length, -1))
    final_projection = hk.Linear(self.model_size, w_init=self.w_init, with_bias=self.with_bias, b_init=self.b_init)
    return final_projection(attn)


_base = {}


def base_model():
    """Load the checkpoint once (original Haiku code path) and install the patch."""
    if 'm' not in _base:
        import avici, haiku as hk
        _base['orig_cls'] = hk.MultiHeadAttention
        _base['m'] = avici.load_pretrained(checkpoint_dir=str(ENV / 'checkpoints/avici/scm-v0'), expects_counts=False)

        class PatchedMultiHeadAttention(_base['orig_cls']):
            def __init__(self, *args, name=None, **kwargs):
                super().__init__(*args, name=name or 'multi_head_attention', **kwargs)

            def __call__(self, query, key, value, mask=None):
                return _patched_call(self, query, key, value, mask)

        hk.MultiHeadAttention = PatchedMultiHeadAttention   # avici.model looks it up at trace time
    return _base['m']


def make_model():
    """A fresh AVICIModel instance sharing the loaded parameters. Both jit caches are fresh: AVICIModel.__call_main__
    (static self) and InferenceModel.infer_edge_logprobs (static self), hence the shallow copy of the InferenceModel."""
    import copy
    from avici.pretrain import AVICIModel
    m = base_model()
    return AVICIModel(params=m.params, model=copy.copy(m._model), expects_counts=m.expects_counts,
                      standardizer=m._standardizer)


_seen = {}


def run(model, x, mode='PLAIN', layers=(), dT=None):
    """Forward with a given intervention; the configuration is baked in at the model instance's first trace.
    Guard: the first call of an instance for an input shape must trace (otherwise a stale cached trace was reused),
    and later calls must keep the same configuration."""
    cfg = (mode, frozenset(layers), dT)
    key = (id(model), tuple(x.shape))
    if key in _seen and _seen[key] != cfg:
        raise RuntimeError(f'configuration changed on a traced instance: {_seen[key]} -> {cfg}')
    CFG.update(mode=mode, layers=frozenset(layers), dT=dT, counter=0, record=[])
    p = np.asarray(model(x=x), dtype=np.float64)
    rec = list(CFG['record'])
    if key not in _seen and len(rec) != 16:
        raise RuntimeError(f'stale trace: first call of a fresh instance did not trace (record {len(rec)})')
    _seen[key] = cfg
    return p, rec
