#!/usr/bin/env python3
"""从《紫微斗数全书》（维基文库录文）切出条目，写入 ziwei/entries/。

    python3 tools/ziwei_extract.py            # 重切并覆盖
    python3 tools/ziwei_extract.py --check    # 只核对入库的是否与重切一致

原文一字不改，只切分；每条注明卷与篇。派生表（如庙旺利陷）标 derived，并写明从哪几句读出。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ziweiquanshu_source import ROOT, fetch

OUT = os.path.join(ROOT, "ziwei", "entries")
ZHI = "子丑寅卯辰巳午未申酉戌亥"
BOOK = "ziweiquanshu"


def lines_of(text):
    """去掉 wiki 标记，按行给出（保留原文用字与标点）"""
    t = re.sub(r"</?poem>|</?nowiki>|<onlyinclude>|</onlyinclude>|\{\{[^{}]*\}\}", "", text)
    t = t.replace("'''", "")
    return [l.rstrip() for l in t.split("\n")]


def section(text, start, end=None):
    i = text.index(start); j = text.index(end, i + len(start)) if end else len(text)
    return text[i:j]


# ---------------- 卷二 · 安身命例：安星诸诀 ----------------
HEAD = re.compile(r"^\s*((?:安|起|定|论|六十|天空地劫)[^，。：:\s]{1,16}?)(?:\s+(.{1,16}))?\s*$")


def anxing():
    t = fetch("卷二")
    sec = section(t, "===安身命例===", "===一 命宫===")
    # 五张定紫微的宫位图单独解析，这里先剔掉，免得把图里的字当诀文
    body = re.sub(r"<nowiki>.*?</nowiki>", "", sec, flags=re.S)
    items, cur = [], None
    for l in lines_of(body)[1:]:
        s = l.strip()
        if not s or s.startswith("=") or set(s) <= set("-|+ "):
            continue
        m = HEAD.match(s)
        if m and "，" not in s and len(s) <= 26:
            cur = {"key": m.group(1), "note": (m.group(2) or "").strip(), "text": ""}
            items.append(cur); continue
        if s.startswith("安长生、"):   # 长生十二神一句录文无标题，接在安封诰诀后；单列，key 为整理者所加
            cur = {"key": "安长生十二神", "note": "标题为整理者所加", "text": ""}; items.append(cur)
        if cur is None:
            cur = {"key": "安身命例", "note": "", "text": ""}; items.append(cur)
        cur["text"] += (("\n" if cur["text"] else "") + s)
    return [dict(it, vol=2, chapter="安身命例") for it in items if it["text"]]


# ---------------- 卷二 · 五行局定紫微 ----------------
def ziwei_ju():
    t = fetch("卷二")
    sec = section(t, "===安身命例===", "===一 命宫===")
    out = []
    for m in re.finditer(r"<poem>((?:(?!<poem>).)*?)</poem>\s*<nowiki>(.*?)</nowiki>", sec, flags=re.S):
        verse, grid = m.group(1).strip(), m.group(2)
        name = re.search(r"([水木金土火][二三四五六]局)", grid).group(1)
        rows, block = [], []
        for l in grid.split("\n"):
            if re.match(r"^\s*-", l) or not l.strip():
                if block: rows.append(block); block = []
                continue
            if "|" in l: block.append(l)
        if block: rows.append(block)
        days = {}
        for b in rows:
            segs = [[c for c in l.split("|")[1:-1]] for l in b]
            ncol = len(segs[0])
            for c in range(ncol):
                col = [s[c] if c < len(s) else "" for s in segs]
                txt = [x.strip() for x in col]
                br = next((x[-1] for x in txt if x and x[-1] in ZHI), None)
                ch = [x for x in txt if x and x[-1] not in ZHI]
                if not br or len(ch) < 2:
                    continue
                a, bb = ch[0], ch[1]
                for i in range(min(len(a), len(bb))):
                    days[a[i] + bb[i]] = br
        out.append({"key": name, "verse": verse, "days": days, "vol": 2, "chapter": "安身命例"})
    return out


# ---------------- 卷二 · 十二宫逐星论断 ----------------
PALACES = ["命宫", "兄弟", "妻妾", "子女", "财帛", "疾厄", "迁移", "奴仆", "官禄", "田宅", "福德", "父母"]
MAIN = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]
AUX = ["文昌", "文曲", "左辅", "右弼", "禄存", "天魁", "天钺", "擎羊", "陀罗", "羊玲", "火星", "铃星", "天马", "化禄", "化权", "化科", "化忌",
       "天空", "地劫", "斗君", "天刑", "天姚", "三台", "八座", "红鸾", "天喜"]
STARS = MAIN + AUX
ALIAS = {"廉真": "廉贞"}   # 录文里廉贞多写作廉真
LEVEL = [("入庙", "庙"), ("庙", "庙"), ("旺地", "旺"), ("旺", "旺"), ("得地", "得"), ("利益", "利"), ("和平", "平"), ("陷地", "陷"), ("陷", "陷")]


def star_at(s):
    s = s.lstrip()
    for a, b in ALIAS.items():
        if s.startswith(a): return b
    return next((x for x in STARS if s.startswith(x)), None)


COMBO = {"左辅右弼": ["左辅", "右弼"], "魁钺": ["天魁", "天钺"], "羊陀": ["擎羊", "陀罗"], "羊铃": ["擎羊", "铃星"], "羊玲": ["擎羊", "铃星"]}


def stars_at(s):
    """段首所论的星：合称拆开，单星照 star_at"""
    for k, v in COMBO.items():
        if s.startswith(k): return v
    st = star_at(s)
    return [st] if st else []


def gong():
    t = fetch("卷二")
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"===\s*([^=\n]+?)\s*===", t)]
    out = []
    for k, (pos, name) in enumerate(heads):
        pal = next((p for p in PALACES if p in name.replace(" ", "")), None)
        if not pal: continue
        end = heads[k + 1][0] if k + 1 < len(heads) else len(t)
        body = t[pos + len(name) + 6:end]
        if pal == "命宫":
            out += ming(body)
        else:
            # 一行以「，」收尾的，下一行是续句（「七杀同……」是说与七杀同宫）；以「。」收尾才另起一段。
            # 段首是星名（或「左辅右弼」「魁钺」这类合称）就归那颗星；各宫开头不点星名的是总论
            # 宫末「定公卿」一类无标点的小题，其下是诗诀：小题连同诗句单列一条，不按诗句首字归星
            cur, cont, verse = None, False, False
            for l in lines_of(body):
                s = l.strip()
                if not s or s.startswith("<"): continue
                if not re.search(r"[，。、]", s):
                    cur = {"palace": pal, "star": s, "stars": [], "text": s}; out.append(cur); verse = True; cont = True; continue
                if cur is not None and (cont or verse):
                    cur["text"] += "\n" + s; cont = s.endswith("，"); verse = False; continue
                sts = stars_at(s)
                if not sts and cur is not None and cur["star"] == "总论":   # 总论连段
                    cur["text"] += "\n" + s
                else:
                    combo = next((k for k in COMBO if s.startswith(k)), None)
                    cur = {"palace": pal, "star": combo or (sts[0] if sts else "总论"), "stars": sts, "text": s}; out.append(cur)
                cont = s.endswith("，")
    for o in out: o.update(vol=2, chapter=o["palace"] if o["palace"] != "命宫" else "命宫")
    return out


def ming(body):
    """命宫一节：每颗星一段——星性总论、十二宫庙旺与所喜生年、入男命 / 女命 / 限吉凶诀"""
    ls = lines_of(body); out, cur, mode, seen = [], None, "text", set()   # 命宫里每颗星只起一段；再出现的星名是上一段的续文
    for l in ls:
        s = l.strip()
        if not s: continue
        st = star_at(s)
        m = re.match(r"^(\S+?)入(男命|女命|限)吉凶诀", s)
        if m:
            mode = {"男命": "male", "女命": "female", "限": "xian"}[m.group(2)]; cur.setdefault(mode, ""); continue
        if st and st not in seen and not l.startswith(" ") and not m and ("属" in s[:6] or s[len(st):len(st) + 1] in "土木火金水，"):
            cur = {"palace": "命宫", "star": st, "text": s, "branches": []}; out.append(cur); seen.add(st); mode = "text"; continue
        if cur is None: continue
        if mode == "text" and l.startswith(" ") and "宫" in s:
            cur["branches"].append(s); continue
        if mode == "text": cur["text"] += "\n" + s
        else: cur[mode] += ("\n" if cur[mode] else "") + s
    return out


def miaowang(ming_items):
    """庙旺利陷表：从命宫一节各星的「某宫入庙 / 旺地 / 得地 / 利益 / 和平 / 陷地」读出。derived"""
    table, src = {}, {}
    for it in ming_items:
        st = it["star"]; row = table.setdefault(st, {})
        for b in it.get("branches", []):
            for m in re.finditer(r"([子丑寅卯辰巳午未申酉戌亥]+)宫(" + "|".join(k for k, _ in LEVEL) + r")", b):
                lv = dict(LEVEL)[m.group(2)]
                for z in m.group(1): row.setdefault(z, lv); src.setdefault(st, {}).setdefault(z, b)
        # 四煞等无分宫小节，庙陷写在正文末：「辰戌丑未入庙」「子午卯酉陷地」
        for l in it["text"].split("\n"):
            m = re.match(r"^([子丑寅卯辰巳午未申酉戌亥]{2,})(" + "|".join(k for k, _ in LEVEL) + r")", l)
            if m:
                for z in m.group(1): row.setdefault(z, dict(LEVEL)[m.group(2)]); src.setdefault(st, {}).setdefault(z, l)
    return table, src


# ---------------- 卷一、卷三：按篇切 ----------------
FU = ("太微賦", "形性賦", "增補太微賦", "斗數骨髓賦", "斗数骨随赋", "女命骨髓賦", "女命骨髓赋")


def by_heading(vol):
    t = fetch(vol)
    heads = [(m.start(), m.end(), len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(={2,4})\s*([^=\n]+?)\s*={2,4}\s*$", t, flags=re.M)]
    out = []
    for k, (s, e, lvl, name) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(t)
        text = "\n".join(l.strip() for l in lines_of(t[e:end]) if l.strip())
        if not text or name.startswith("紫微斗") : continue
        it = {"key": name, "vol": int("一二三".index(vol[1]) + 1), "chapter": name, "text": text}
        if name in FU or name.endswith("赋") or name.endswith("賦"):
            it["lines"] = [x for x in re.split(r"(?<=[。！？])", text.replace("\n", "")) if x.strip()]
        out.append(it)
    return out


def build():
    g = gong(); mw, mw_src = miaowang([x for x in g if x["palace"] == "命宫"])
    return {
        "anxing": {"note": "卷二「安身命例」所载安星诸诀，按诀切分，原文照录。", "items": anxing()},
        "ju": {"note": "卷二五行局定紫微图（水二局至火六局），原图为字符画，此处按宫读出每日紫微所在。"
                       "录文有两处与诀文不合，见 ziwei/collation.json。", "items": ziwei_ju()},
        "gong": {"note": "卷二十二宫逐星论断：命宫一节每星含总论、十二支宫庙旺与所喜生年、入男命女命入限吉凶诀；其余各宫按段切：段首星名为 star，stars 列出所论各星（「左辅右弼」「魁钺」「羊陀」等合称拆开）；不点星名的为「总论」；官禄宫末「定公卿」等小题连诗诀各为一条。以「，」收尾的行与下行同段（「七杀同……」是说与七杀同宫，非另起）。", "items": g},
        "miaowang": {"note": "庙旺利陷表（derived）：从卷二命宫一节各星「某宫入庙 / 旺地 / 得地 / 利益 / 和平 / 陷地」读出；四煞无分宫小节者取正文末「辰戌丑未入庙」等句。"
                             "火星书中按生年论（「寅午戌人宜，申子辰人陷」），不入此表。书中那一宫没写的留空，不从他书补。src 为每格所据原句。", "provenance": "derived", "table": mw, "src": mw_src},
        "juan1": {"note": "卷一：赋文（太微赋、形性赋、骨髓赋、女命骨髓赋等，另按句切出 lines）、诸星问答、格局诸论，按篇切分。", "items": by_heading("卷一")},
        "juan3": {"note": "卷三：谈星要论、限运、杂论，按篇切分。", "items": by_heading("卷三")},
    }


def main(check=False):
    doc = build(); bad = []
    for name, d in doc.items():
        path = os.path.join(OUT, f"{BOOK}-{name}.json")
        body = {"book": BOOK, "edition": "维基文库录文（依现代排印本，卷二卷三为简体）；底本明南阳堂刊本，出入见 collation", **d}
        if check:
            if not os.path.exists(path) or json.load(open(path)) != body: bad.append(name)
        else:
            os.makedirs(OUT, exist_ok=True); json.dump(body, open(path, "w"), ensure_ascii=False, indent=1)
            n = len(d.get("items", d.get("table", {})))
            print(f"{name:9s} {n:4d} → {path}")
    if check:
        print("一致" if not bad else f"不一致：{bad}"); sys.exit(1 if bad else 0)


if __name__ == "__main__" and ("--check" in sys.argv or len(sys.argv) >= 1):
    main("--check" in sys.argv)
