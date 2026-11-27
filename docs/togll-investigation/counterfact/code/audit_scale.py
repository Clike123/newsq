# full-scale counterfactual audit — adapted from E3 logic, per-defect isolated runs
# usage: python3 audit_scale.py   (runs on server, inside counterfact_full)
import pathlib, json, csv, re, sys
ROOT = pathlib.Path('/mnt/hdd/bocchi_hdd/togll_rq5/counterfact_full')
RQ = ROOT/'payload/eval/rq3'
plan = json.loads((ROOT/'plan.json').read_text())

def parse_trigger_file(f):
    if not f.exists(): return None, 'missing_trigger_log'
    failures = {}
    for block in re.split(r'^---\s*', f.read_text(errors='replace'), flags=re.M):
        if not block.strip(): continue
        key = block.strip().splitlines()[0].strip()
        if key in failures: return None, 'duplicate_trigger_identity'
        failures[key] = block.strip()
    return failures, None

def suite_valid(log, project, bug):
    secs = [x for x in log.split('Executing test suite: ')[1:] if x.startswith(f'{project}-{bug}b-toga.{bug}.tar.bz2')]
    if len(secs) != 1: return False, 'suite_section_count_' + str(len(secs))
    s = secs[0]
    ok = all(re.search(r'Check out program version: ' + re.escape(f'{project}-{bug}{v}') + r'\.+ OK', s) for v in 'bf')
    if not ok: return False, 'checkout_failed'
    ok = all(len(re.findall(r'Running ant \(' + a + r'\)\.+ OK', s)) == 2 for a in ['compile', 'compile.gen.tests', 'run.gen.tests'])
    if not ok: return False, 'compile_or_run_not_ok'
    return True, None

def attr(trace, cls, oracle_line):
    if not trace: return 'NO_FAILURE'
    if 'ExceptionInInitializerError' in trace or 'NoClassDefFoundError' in trace: return 'HARNESS_OR_ENVIRONMENT'
    frames = re.findall(re.escape(cls) + r'\.java:(\d+)', trace)
    if not frames: return 'UNKNOWN'
    line = int(frames[0])
    if oracle_line is None or line < oracle_line: return 'PREFIX_EXCEPTION'
    if line == oracle_line:
        first = trace.splitlines()[1] if len(trace.splitlines()) > 1 else ''
        if 'AssertionError' in first or 'AssertionFailedError' in first or 'ComparisonFailure' in first: return 'ORACLE_ASSERTION'
        return 'ORACLE_EVALUATION_EXCEPTION'
    return 'UNKNOWN'

def methods(java):
    text = java.read_text(errors='replace')
    out = []
    package = re.search(r'^package\s+([^;]+);', text, re.M)
    package = package[1] if package else ''
    for m in re.finditer(r'public void (test\w+)\(\s*\)', text):
        out.append((package + '.' + java.stem + '::' + m.group(1)))
    return out

def oracle_lines(java):
    # first assert* line number per test method, approximated per-file scan
    text = java.read_text(errors='replace').splitlines()
    res = {}; cur = None
    for i, ln in enumerate(text, 1):
        mm = re.search(r'public void (test\w+)\(', ln)
        if mm: cur = mm.group(1)
        if cur and re.search(r'\bassert\w*\s*\(', ln) and (cur not in res):
            res[cur] = i
    return res

results = []
for item in plan:
    name = item['run_id']; case = RQ/'cases'/name
    gen = case/'generated'
    rec = dict(run_id=name, project=item['project'], bug_num=item['bug_num'], variant=item['variant'],
               n_rows=item['n_rows'], ids=[i for grp in item['idmap'] for i in grp['ids']])
    elog = case/'evaluate.log'
    if not elog.exists():
        rec.update(valid=False, reason='no_evaluate_log', observations=[]); results.append(rec); continue
    log = elog.read_text(errors='replace')
    valid, reason = suite_valid(log, item['project'], item['bug_num'])
    rec['valid'] = valid; rec['reason'] = reason
    obs = []
    bugdir = gen/'aggregated_d4j_tests'/item['project']/'toga'/item['bug_num']
    javas = list(bugdir.rglob('*ESTest.java')) if bugdir.exists() else []
    javas = [j for j in javas if 'scaffolding' not in j.name]
    trig = {}
    errs = []
    for v in 'bf':
        t, e = parse_trigger_file(gen/'results/bug_detection_log'/item['project']/'toga'/(item['bug_num']+v+'.'+item['bug_num']+'.trigger.log'))
        trig[v] = t or {}; 
        if e: errs.append(e)
    for j in javas:
        ols = oracle_lines(j)
        for tn in methods(j):
            meth = tn.split('::')[1]
            o = {'test_name': tn}
            for v, lbl in [('b','buggy'), ('f','fixed')]:
                tr = trig[v].get(tn, '')
                state = ('FAIL' if tr else 'PASS') if valid else 'UNKNOWN'
                a = attr(tr, j.stem, ols.get(meth))
                if tr and a in ('UNKNOWN', 'HARNESS_OR_ENVIRONMENT'): state = 'UNKNOWN'
                if not valid: a = 'EXECUTION_NOT_VALIDATED'
                o[lbl] = state; o[lbl + '_attr'] = a
            o['detects'] = (o['buggy'] == 'FAIL' and o['fixed'] == 'PASS') if 'UNKNOWN' not in (o['buggy'], o['fixed']) else None
            obs.append(o)
    rec['observations'] = obs
    rec['trig_errors'] = errs
    results.append(rec)

# defect-level aggregation
def any_det(vals):
    vals = list(vals)
    if not vals: return None
    if True in vals: return True
    if None in vals: return None
    return False
def incr(w, p):
    if w is False or p is True: return False
    if w is True and p is False: return True
    return None
defects = {}
for r in results:
    key = (r['project'], r['bug_num'])
    d = defects.setdefault(key, {})
    d[r['variant']] = r
out_rows = []
for (proj, bug), d in sorted(defects.items()):
    row = {'project': proj, 'bug_num': bug}
    for v in ['with_oracle', 'no_oracle']:
        r = d.get(v)
        if not r: row[v + '_det'] = 'MISSING_RUN'; continue
        dets = [o['detects'] for o in r['observations']]
        row[v + '_det'] = any_det(dets)
        row[v + '_valid'] = r['valid']
        row[v + '_n_obs'] = len(r['observations'])
        row[v + '_n_unknown'] = sum(1 for x in dets if x is None)
    w, p = row.get('with_oracle_det'), row.get('no_oracle_det')
    w = {'True': True, 'False': False}.get(str(w), w if w in (True, False) else None if w is None else 'MISSING')
    row['net_new'] = incr(w == True if isinstance(w, bool) else w, p) if not isinstance(w, str) else 'NA'
    out_rows.append(row)
(ROOT/'audit_scale_results.json').write_text(json.dumps(results, indent=1, default=str), encoding='utf8')
(ROOT/'audit_scale_defects.json').write_text(json.dumps(out_rows, indent=1, default=str), encoding='utf8')
# summary
n_valid_w = sum(1 for r in out_rows if r.get('with_oracle_valid') is True)
det_w = sum(1 for r in out_rows if r.get('with_oracle_det') is True or str(r.get('with_oracle_det')) == 'True')
det_p = sum(1 for r in out_rows if str(r.get('no_oracle_det')) == 'True')
print(json.dumps({'defects': len(out_rows), 'with_valid': n_valid_w, 'with_detects': det_w, 'prefix_detects': det_p}, indent=1))
