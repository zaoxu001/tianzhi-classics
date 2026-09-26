#!/usr/bin/env python3
"""从《六壬大全》（维基文库四库本录文）课经卷五至卷八抽出起例课，逐一与取传算法比对三传。

    python3 tools/liuren_examples_check.py
录文由 tools/liurendaquan_source.py 取自维基文库并缓存；取传用 tianzhi-core（pip install tianzhi-core）。
结果写到缓存目录下的 examples.json。
"""
import re, sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from liurendaquan_source import CACHE, fetch
from tianzhi_core.liuren import pan as L
D=CACHE+'/'
ZHI='子丑寅卯辰巳午未申酉戌亥'; GAN='甲乙丙丁戊己庚辛壬癸'
VAR={'夘':'卯','邜':'卯','戍':'戌','已':'巳'}
def clean(v):
    w=fetch(int(v)); w=re.sub(r'<!--.*?-->','',w,flags=re.S)
    for _ in range(3): w=re.sub(r'\{\{SK ?notes\|([^{}]*)\}\}',r'〔\1〕',w)
    w=re.sub(r'\{\{SK anchor\|([^{}]*)\}\}',r'【\1】',w); w=re.sub(r'\{\{[^{}]*\}\}|<[^>]+>','',w)
    w=re.sub(r'[　\s]+','',w)
    for a,b in VAR.items(): w=w.replace(a,b)
    return w
pat=re.compile(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日([子丑寅卯辰巳午未申酉戌亥])時([子丑寅卯辰巳午未申酉戌亥])將')
B=r'[（〔][^（）〔〕]{1,3}[）〕]'
seg=re.compile(B+r'([子丑寅卯辰巳午未申酉戌亥])'+B+r'([子丑寅卯辰巳午未申酉戌亥])'+B+r'([子丑寅卯辰巳午未申酉戌亥])')
def run(gz,yj,zs):
    tdp=L.build_tian_di_pan(yj,zs); cls=L.build_four_classes(gz[0],gz[1],tdp); c=L.get_three_chuan(cls,tdp,gz[0],gz[1])
    return c['chu']+c['zhong']+c['mo'], c['method']
res=[]
for v in ['05','06','07','08']:
    t=clean(v)
    for m in pat.finditer(t):
        gz,zs,yj=m.groups()
        if (GAN.index(gz[0])%2)!=(ZHI.index(gz[1])%2): continue
        s=seg.search(t[m.end():m.end()+220])
        if not s: continue
        want=''.join(s.groups()); got,meth=run(gz,yj,zs)
        if got!=want and run(gz,zs,yj)[0]==want:   # 底本将、时互倒：按书中所列课式取
            got,meth=run(gz,zs,yj); meth+='·将时互倒'
        heads=re.findall(r'【([^】]{1,10})】',t[:m.start()])
        res.append(dict(vol=v,sec=heads[-1] if heads else '',gz=gz,yj=yj,zs=zs,want=want,got=got,method=meth,ctx=t[m.start():m.end()+60]))
json.dump(res,open(D+'examples.json','w'),ensure_ascii=False,indent=1)
ok=[r for r in res if r['want']==r['got']]
print(f'抽出课例 {len(res)} 个，三传相合 {len(ok)}，不合 {len(res)-len(ok)}')
for r in res:
    if r['method'].endswith('将时互倒'): print(f"  卷{r['vol']} {r['gz']}日：底本将、时互倒，按所列课式相合")
for r in res:
    if r['want']!=r['got']: print(f"  卷{r['vol']} 〈{r['sec']}〉 {r['gz']}日 {r['yj']}将加{r['zs']}  大全 {r['want']}  程序 {r['got']}({r['method']})")
