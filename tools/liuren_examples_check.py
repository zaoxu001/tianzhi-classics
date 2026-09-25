#!/usr/bin/env python3
"""从《六壬大全》（维基文库四库本录文）课经卷五至卷八抽出起例课，逐一与取传算法比对三传。

    用法：先把卷05–卷08 的维基文本存到 D 目录（api.php?action=parse&prop=wikitext），
    再指定取传实现所在的路径，运行即可。结果写到 D/examples.json。
"""
import re, sys, json
sys.path.insert(0, '/home/zimeiti/work/tz-promo/src')
import liuren as L
D='/tmp/claude-0/-home-zimeiti/0c095ab0-9374-4991-b7ce-6591f7e4ae09/scratchpad/lrdq/'
ZHI='子丑寅卯辰巳午未申酉戌亥'; GAN='甲乙丙丁戊己庚辛壬癸'
VAR={'夘':'卯','邜':'卯','戍':'戌','已':'巳'}
def clean(v):
    w=open(D+f'{v}.txt').read(); w=re.sub(r'<!--.*?-->','',w,flags=re.S)
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
        heads=re.findall(r'【([^】]{1,10})】',t[:m.start()])
        res.append(dict(vol=v,sec=heads[-1] if heads else '',gz=gz,yj=yj,zs=zs,want=want,got=got,method=meth,ctx=t[m.start():m.end()+60]))
json.dump(res,open(D+'examples.json','w'),ensure_ascii=False,indent=1)
ok=[r for r in res if r['want']==r['got']]
print(f'抽出课例 {len(res)} 个，三传相合 {len(ok)}，不合 {len(res)-len(ok)}')
for r in res:
    if r['want']!=r['got']: print(f"  卷{r['vol']} 〈{r['sec']}〉 {r['gz']}日 {r['yj']}将加{r['zs']}  大全 {r['want']}  程序 {r['got']}({r['method']})")
