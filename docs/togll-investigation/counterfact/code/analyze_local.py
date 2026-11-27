# defect-level counterfactual analysis — consumes audit_scale_results.json (downloaded from server)
import json, sys
res = json.loads(open(sys.argv[1] if len(sys.argv)>1 else 'audit_scale_results.json', encoding='utf-8').read())

def any_det(vals):
    vals = list(vals)
    if not vals: return None
    if True in vals: return True
    if None in vals: return None
    return False
def incr(w, p):
    # Kleene: I = w AND (NOT p)
    if w is False or p is True: return False
    if w is True and p is False: return True
    return None

defects = {}
for r in res:
    defects.setdefault((r['project'], r['bug_num']), {})[r['variant']] = r

rows = []
for (proj, bug), d in sorted(defects.items()):
    row = {'project': proj, 'bug_num': int(bug)}
    for v in ['with_oracle', 'no_oracle']:
        r = d.get(v)
        if not r:
            row[v] = {'det': 'MISSING'}; continue
        dets = [o['detects'] for o in r['observations']]
        attrs = [o['buggy_attr'] for o in r['observations'] if o['detects'] is True]
        row[v] = {'det': any_det(dets), 'valid': r['valid'], 'reason': r.get('reason'),
                  'n_obs': len(r['observations']), 'n_unk': sum(1 for x in dets if x is None),
                  'det_attrs': sorted(set(attrs))}
    w, p = row['with_oracle'].get('det'), row['no_oracle'].get('det')
    w = w if w in (True, False) or w is None else 'MISSING'
    p = p if p in (True, False) or p is None else 'MISSING'
    row['net_new'] = incr(w, p) if 'MISSING' not in (w, p) else 'MISSING'
    rows.append(row)

# headline stats
def val(row, v): return row[v].get('det')
n = len(rows)
w_true = [r for r in rows if val(r,'with_oracle') is True]
p_true = [r for r in rows if val(r,'no_oracle') is True]
net_new_true = [r for r in rows if r['net_new'] is True]
net_new_false = [r for r in rows if r['net_new'] is False]
net_new_unk = [r for r in rows if r['net_new'] is None]
w_invalid = sum(1 for r in rows if r['with_oracle'].get('valid') is not True)
p_invalid = sum(1 for r in rows if r['no_oracle'].get('valid') is not True)
print(f'defects: {n}')
print(f'with_oracle detects (defect-level): {len(w_true)}')
print(f'no_oracle detects (prefix-only):    {len(p_true)}')
print(f'net_new TRUE (oracle adds detection):  {len(net_new_true)}')
print(f'net_new FALSE (no added value):        {len(net_new_false)}')
print(f'net_new UNKNOWN:                       {len(net_new_unk)}')
print(f'invalid runs: with={w_invalid} no={p_invalid}')
print()
print('=== defects where oracle adds detection (net_new TRUE):')
for r in net_new_true: print(' ', r['project'], r['bug_num'], r['with_oracle'].get('det_attrs'))
print('=== prefix-only detections among with_oracle detections:')
both = [r for r in w_true if val(r,'no_oracle') is True]
print(f'  prefix can independently detect {len(both)} of {len(w_true)} with-oracle detections')
for r in both: print(' ', r['project'], r['bug_num'], 'with_attrs:', r['with_oracle'].get('det_attrs'))
print('=== with-oracle detection attribution distribution (defect-level, any detection):')
from collections import Counter
c = Counter()
for r in w_true:
    for a in r['with_oracle'].get('det_attrs', []): c[a] += 1
print(dict(c))
json.dump(rows, open('defect_level_analysis.json', 'w'), indent=1)
