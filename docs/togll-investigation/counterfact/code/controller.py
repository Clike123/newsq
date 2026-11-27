# parallel counterfactual pipeline controller — nice 19, isolated tmp per run
import pathlib, json, subprocess, time, os, signal, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).resolve().parent
RQ = ROOT/'payload/eval/rq3'
PY = '/mnt/hdd/bocchi_hdd/togll_rq5/py310env/python/bin/python'
OLD = pathlib.Path('/mnt/hdd/bocchi_hdd/togll_rq5/env/payload')
plan = json.loads((ROOT/'plan.json').read_text())
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
if only: plan = [p for p in plan if p['run_id'] in only]
status = []; started = time.time()
import threading
lock = threading.Lock()
def save():
    with lock:
        p = ROOT/'status.tmp'; p.write_text(json.dumps({'started': started, 'updated': time.time(), 'runs': status}, indent=2)); p.replace(ROOT/'status.json')
def execute(item):
    name = item['run_id']; rel = 'cases/'+name+'/generated'; case = RQ/'cases'/name
    if (ROOT/'done'/name).exists(): return
    case.mkdir(parents=True, exist_ok=True)
    record = dict(item, stages=[], started=time.time())
    with lock: status.append(record)
    save()
    env = os.environ.copy()
    env['D4J_TMP_DIR'] = str(ROOT/'tmp'/name); env['PYTHONHASHSEED'] = '0'; env['PYTHONUNBUFFERED'] = '1'
    jdk = '/mnt/hdd/bocchi_hdd/togll_rq5/env/jdk8'
    env['JAVA_HOME'] = jdk
    env['PATH'] = jdk + '/bin:' + '/mnt/hdd/bocchi_hdd/togll_rq5/audit_incremental_20261126_v1/defects4j/framework/bin' + ':' + env.get('PATH', '')
    pathlib.Path(env['D4J_TMP_DIR']).mkdir(parents=True, exist_ok=True)
    commands = [
        ('generate', [PY, 'gen_tests_from_metadata.py', str(ROOT/'inputs'/item['input']), str(OLD/'data/evosuite_regression_all'), '--output_dir', rel, '--d4j_path', str(OLD/'defects4j/framework/projects')]),
        ('aggregate', [PY, 'aggregate_test_cases.py', rel]),
        ('evaluate', [PY, 'eval_tests.py', rel+'/aggregated_d4j_tests', '-o', rel+'/results', '-t', '900', '-v']),
        ('collect', [PY, 'collect_test_results.py', rel])]
    for stage, argv in commands:
        argv = ['nice', '-n', '19'] + argv
        rec = {'stage': stage, 'started': time.time()}; record['stages'].append(rec); save()
        with (case/(stage+'.log')).open('wb') as log:
            p = subprocess.Popen(argv, cwd=RQ, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try: rec['exit_code'] = p.wait(timeout=2400)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL); p.wait(); rec['exit_code'] = p.returncode; rec['timeout'] = True
        rec['seconds'] = time.time()-rec['started']; save()
        if rec['exit_code'] != 0: break
    record['finished'] = time.time(); save()
    (ROOT/'done'/name).mkdir(parents=True, exist_ok=True)
(ROOT/'done').mkdir(exist_ok=True)
with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(execute, plan))
(ROOT/'DONE').write_text(str(time.time()))
print('ALL DONE', time.time()-started)
