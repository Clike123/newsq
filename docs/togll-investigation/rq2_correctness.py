import os, json, glob, xml.etree.ElementTree as ET
from collections import defaultdict
# per-project oracle input counts from inference results
res_base = r'H:\togll-inv\artifacts\RQ2\inference\results'
inputs = {}
for proj in os.listdir(res_base):
    for fn in glob.glob(os.path.join(res_base, proj, 'codeparrot_tc_mut_doc.json')):
        inputs[proj] = len(json.load(open(fn)))
# surefire pass/fail aggregation
sf_base = r'H:\togll-inv\artifacts\RQ2\Final_project_with_togll_tests'
print(f'{"project":32s} {"inputs":>7s} {"tests":>6s} {"fail":>5s} {"err":>5s} {"pass":>6s} {"pass/inp":>8s} {"pass/run":>8s}')
means = []
for proj in sorted(inputs):
    pdir = os.path.join(sf_base, proj)
    if not os.path.isdir(pdir):
        continue
    tests = failures = errors = skipped = 0
    for xml in glob.glob(os.path.join(pdir, '**', 'TEST-*.xml'), recursive=True):
        try:
            r = ET.parse(xml).getroot()
            tests += int(r.get('tests', 0)); failures += int(r.get('failures', 0))
            errors += int(r.get('errors', 0)); skipped += int(r.get('skipped', 0))
        except Exception:
            pass
    passed = tests - failures - errors - skipped
    inp = inputs[proj]
    r1 = passed / inp * 100 if inp else 0
    r2 = passed / tests * 100 if tests else 0
    means.append(r1)
    print(f'{proj:32s} {inp:7d} {tests:6d} {failures:5d} {errors:5d} {passed:6d} {r1:7.1f}% {r2:7.1f}%')
print(f'\nmean pass/inputs across projects: {sum(means)/len(means):.1f}%  (paper TOGLL mean ~63%)')
print('paper anchors: commons-numbers 74.7%, http-request 83%')
