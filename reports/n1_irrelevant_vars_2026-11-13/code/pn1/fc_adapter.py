"""FoundCause schedule adapter (rules v2.1 §A5).

Builds `predict_sched(..., base=B)` from the *source* of foundcause.predict (rev d937cbf) by replacing the
hard-coded schedule seed `42 + run_i` with `base + run_i`. Nothing else changes. Validity condition (RN0):
predict_sched(base=42) must reproduce the package API within 1e-6 on every DEV system.
"""
import inspect, textwrap
import foundcause as _fc

_src = textwrap.dedent(inspect.getsource(_fc.predict))
_n = _src.count('42 + run_i')
assert _n == 3, f'expected 3 schedule-seed sites, found {_n}'
_src = _src.replace('def predict(model, X, device,', 'def predict_sched(model, X, device, base=42,', 1)
_src = _src.replace('42 + run_i', 'base + run_i')
# recursive call for duplicate handling must stay on the same schedule
_src = _src.replace('sub = predict(model,', 'sub = predict_sched(model,')
_src = _src.replace('device, temperature=temperature, n_runs=n_runs,', 'device, base=base, temperature=temperature, n_runs=n_runs,', 1)
_ns = dict(vars(_fc))
exec(compile(_src, '<fc_adapter>', 'exec'), _ns)
predict_sched = _ns['predict_sched']
SOURCE = _src
