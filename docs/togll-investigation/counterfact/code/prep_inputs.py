# prepare per-defect input CSVs for the full counterfactual experiment
# for each defect in the artifact assertion_prefix group: with_oracle (original) + no_oracle (blanked)
import csv, json, pathlib, runpy, hashlib
root = pathlib.Path(__file__).parent
source = pathlib.Path('H:/togll-inv/artifacts/RQ5/bug_detection/TOGLL/assertion_prefix/oracle_preds.csv')
rows = list(csv.DictReader(source.open(encoding='utf8')))
print('rows:', len(rows))
mod = runpy.run_path('H:/togll-inv/toga-repo/eval/rq3/gen_tests_from_metadata.py')
def rendered(r):
    s = '@Test\n' + mod['get_prefix'](r['test_prefix'])
    if r['except_pred'] == '1': return mod['insert_try_catch'](s)
    if r['assert_pred']:
        a = r['assert_pred']
        if 'assertEquals' in r['test_prefix'] and ('assertTrue' in a or 'assertFalse' in a):
            a = mod['bool_assert_to_equals'](a)
        return mod['insert_assertion'](s, a)
    return s + '\n    }'
import javalang
def key(r):
    tokens = [(type(t).__name__, t.value) for t in javalang.tokenizer.tokenize(rendered(r))]
    return hashlib.sha256(json.dumps([r['project'], r['bug_num'], r['test_name'].split('::')[0], tokens]).encode()).hexdigest()
defects = sorted({(r['project'], r['bug_num']) for r in rows})
print('defects:', len(defects))
groups = {}
for r in rows:
    for variant in ['with_oracle', 'no_oracle']:
        t = r.copy()
        if variant == 'no_oracle':
            t['except_pred'] = '0'; t['assert_pred'] = ''
        run_id = f"{r['project']}-{r['bug_num']}_{variant}"
        gkey = (run_id, key(t))
        if gkey in groups:
            groups[gkey]['original_ids'].append(r['id'])
            continue
        groups[gkey] = dict(run_id=run_id, variant=variant, project=r['project'], bug_num=r['bug_num'],
                            original_ids=[r['id']], rows=[t])
# merge rows per run_id (dedup within defect+variant)
runs = {}
for g in groups.values():
    runs.setdefault(g['run_id'], dict(run_id=g['run_id'], variant=g['variant'], project=g['project'],
                                      bug_num=g['bug_num'], rows=[], idmap=[]))
    runs[g['run_id']]['rows'].extend(g['rows'][:1])  # one physical row per distinct token-content
    runs[g['run_id']]['idmap'].append({'ids': g['original_ids']})
outdir = root/'inputs'; outdir.mkdir(exist_ok=True)
plan = []
for rid, run in sorted(runs.items()):
    fn = rid + '.csv'
    with (outdir/fn).open('w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(run['rows'][0])); w.writeheader()
        for row in run['rows']: w.writerow(row)
    plan.append(dict(run_id=rid, input=fn, project=run['project'], bug_num=run['bug_num'],
                     variant=run['variant'], n_rows=len(run['rows']), idmap=run['idmap']))
(root/'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf8')
nwo = sum(1 for p in plan if p['variant']=='with_oracle'); nno = len(plan)-nwo
print(json.dumps(dict(runs=len(plan), with_oracle=nwo, no_oracle=nno,
                      total_physical_rows=sum(p['n_rows'] for p in plan)), indent=2))
