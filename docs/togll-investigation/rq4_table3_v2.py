import os, xml.etree.ElementTree as ET
from collections import defaultdict
base = r'H:\togll-inv\artifacts\RQ4\artifacts_with_es_togll_tests'
data = defaultdict(lambda: defaultdict(dict))
nfiles = 0
for root, dirs, files in os.walk(base):
    if 'mutations.xml' not in files:
        continue
    r = root.replace(os.sep, '/')
    variant = 'llm_oracle' if '/llm_oracle/' in r else ('no_oracle' if '/no_oracle/' in r else 'plain')
    proj = os.path.relpath(root, base).split(os.sep)[0]
    nfiles += 1
    try:
        for m in ET.parse(os.path.join(root, 'mutations.xml')).getroot().iter('mutation'):
            key = (m.findtext('sourceFile'), m.findtext('mutatedClass'), m.findtext('mutatedMethod'),
                   m.findtext('mutator'), m.findtext('lineNumber'), m.findtext('description'), proj)
            st = m.get('status', '?')
            # if duplicate exact key, KILLED wins over non-killed (conservative aggregation)
            if key in data[proj][variant] and data[proj][variant][key] == 'KILLED':
                continue
            data[proj][variant][key] = st
    except Exception:
        pass

def killed(d):
    return {k for k, v in d.items() if v == 'KILLED'}

NAMEMAP = {'async-http-client':'async-http','JSON-java':'json','commons-beanutils-1.9.4':'beanutils','commons-collections4-4.4-src':'collections4','commons-configuration2-2.8.0-src':'configuration','commons-dbutils-1.7':'dbutils','commons-imaging-1.0-alpha3-src':'imaging','commons-lang3-3.12.0-src':'lang3','commons-jexl3-3.2.1-src':'jexl3','commons-net-3.8.0':'net','commons-pool2-2.11.1-src':'pool2','commons-numbers-1.0-src':'numbers','commons-rng-1.4-src':'rng','commons-jcs3-3.1-src':'jcs3','commons-validator-1.7':'validator','commons-vfs-2.9.0':'vfs2','commons-weaver-2.0-src':'weaver','http-request':'http','joda-time':'joda-time','jsoup':'jsoup','scribejava':'scribejava','spark':'spark','springside4':'springside4','bcel-6.5.0-src':'bcel'}
PAPER = {'http':(64,38,29,3),'json':(328,110,249,31),'beanutils':(551,46,516,11),'collections4':(248,104,162,18),'dbutils':(108,14,98,4),'jsoup':(598,177,509,88),'imaging':(1869,629,1315,75),'lang3':(2301,397,2063,159),'configuration':(271,51,266,46),'jexl3':(697,73,638,14),'joda-time':(1545,446,1323,224),'net':(747,175,592,20),'pool2':(155,8,150,3),'spark':(407,63,355,11),'validator':(602,52,560,10),'scribejava':(172,31,143,2),'bcel':(1122,467,698,43),'numbers':(871,168,726,23),'springside4':(1160,243,938,21),'vfs2':(339,37,310,8),'rng':(554,158,527,131),'jcs3':(621,81,548,8),'async-http':(69,10,59,0),'weaver':(20,2,18,0)}
print(f'{"project":15s} {"evoA":>6s}{"(paper)":>9s} {"evoU":>6s}{"(paper)":>9s} {"togllA":>7s}{"(paper)":>9s} {"togllU":>7s}{"(paper)":>9s}')
tot = [0]*4; totp = [0]*4; total_mutants = 0
rows = []
for proj in sorted(data):
    v = data[proj]
    if not all(k in v for k in ('plain', 'llm_oracle', 'no_oracle')):
        continue
    total_mutants += len(v['plain'])
    k_no = killed(v['no_oracle']); k_evo = killed(v['plain']); k_tog = killed(v['llm_oracle'])
    ea = k_evo - k_no; ta = k_tog - k_no
    eu = ea - ta; tu = ta - ea
    short = NAMEMAP.get(proj, proj)
    p = PAPER.get(short, (0,0,0,0))
    rows.append((short, len(ea), p[0], len(eu), p[1], len(ta), p[2], len(tu), p[3]))
    tot[0]+=len(ea); tot[1]+=len(eu); tot[2]+=len(ta); tot[3]+=len(tu)
    totp[0]+=p[0]; totp[1]+=p[1]; totp[2]+=p[2]; totp[3]+=p[3]
for r in sorted(rows):
    print(f'{r[0]:15s} {r[1]:6d}({r[2]:7d}) {r[3]:6d}({r[4]:7d}) {r[5]:7d}({r[6]:7d}) {r[7]:7d}({r[8]:7d})')
print(f'{"TOTAL":15s} {tot[0]:6d}({totp[0]:7d}) {tot[1]:6d}({totp[1]:7d}) {tot[2]:7d}({totp[2]:7d}) {tot[3]:7d}({totp[3]:7d})')
print(f'mutant universe (plain keys): {total_mutants}, paper says 69,793')
