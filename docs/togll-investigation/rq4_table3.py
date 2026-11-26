import os, xml.etree.ElementTree as ET
from collections import defaultdict
base = r'H:\togll-inv\artifacts\RQ4\artifacts_with_es_togll_tests'
# per project, per variant: {mutant_key: status}
data = defaultdict(lambda: defaultdict(dict))
for root, dirs, files in os.walk(base):
    if 'mutations.xml' not in files:
        continue
    r = root.replace(os.sep, '/')
    variant = 'llm_oracle' if '/llm_oracle/' in r else ('no_oracle' if '/no_oracle/' in r else 'plain')
    proj = os.path.relpath(root, base).split(os.sep)[0]
    try:
        for m in ET.parse(os.path.join(root, 'mutations.xml')).getroot().iter('mutation'):
            def gt(tag):
                e = m.find(tag)
                return e.text if e is not None and e.text else ''
            key = (gt('mutatedClass'), gt('mutatedMethod'), gt('mutator'), gt('index'), gt('block'))
            data[proj][variant][key] = m.get('status', '?')
    except Exception:
        pass

def killed(d):
    return {k for k, v in d.items() if v == 'KILLED'}

print(f'{"project":30s} {"evoAssert":>9s} {"evoUniq":>8s} {"togllAssert":>11s} {"togllUniq":>9s}')
tot = [0, 0, 0, 0]
for proj in sorted(data):
    v = data[proj]
    if 'llm_oracle' not in v or 'plain' not in v or 'no_oracle' not in v:
        continue
    k_no = killed(v['no_oracle'])
    k_evo = killed(v['plain'])
    k_togll = killed(v['llm_oracle'])
    # assertion-attributed kills: killed in X but not killed in no_oracle
    evo_assert = k_evo - k_no
    togll_assert = k_togll - k_no
    evo_uniq = evo_assert - togll_assert
    togll_uniq = togll_assert - evo_assert
    print(f'{proj:30s} {len(evo_assert):9d} {len(evo_uniq):8d} {len(togll_assert):11d} {len(togll_uniq):9d}')
    tot[0] += len(evo_assert); tot[1] += len(evo_uniq); tot[2] += len(togll_assert); tot[3] += len(togll_uniq)
print(f'{"TOTAL":30s} {tot[0]:9d} {tot[1]:8d} {tot[2]:11d} {tot[3]:9d}')
