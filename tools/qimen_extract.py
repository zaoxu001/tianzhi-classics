#!/usr/bin/env python3
"""从《遁甲演義》（四庫全書本）与《欽定協紀辨方書》卷三十五（四庫全書本）切出奇门条目，写入 qimen/entries/。

    python3 tools/qimen_extract.py            # 重切并覆盖
    python3 tools/qimen_extract.py --check    # 只核对入库的是否与重切一致

原文一字不改，只切分；每条注明卷与篇。四库本的换行是版面折行，不是分段，切出时直接接上；
行内的全角空格是原书的句读间隔，照留。

《遁甲演義》里画符、念呪、步罡、布籌一类的行法篇目不收（卷三「玉女反閉訣」以下、卷四全卷），
篇名记入 meta.skipped：那是宗教行法，不是推演之法，算法用不上，也不在本仓的收录范围内。
吉格各条正文里夹着的呪語照原文保留——切分不改原文，取用时由下游自行剔除。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qimen_source as src

ROOT = src.ROOT
OUT = os.path.join(ROOT, "qimen", "entries")

YANYI_EDITION = "维基文库录文（四庫全書本，文渊阁）；影像见 archive.org 06056496.cn、06056497.cn"
XIEJI_EDITION = "维基文库录文（四庫全書本）"


def text_of(key: str) -> str:
    t = src.fetch(key)
    t = re.sub(r"\{\{YL\|([^}]*)\}\}", r"\1", t)          # 年号模板只留字
    t = re.sub(r"\{\{SKQS (?:header|footer)[^}]*\}\}", "", t)
    t = re.sub(r"\{\{PD-old\}\}", "", t)
    t = src.clean(t)
    t = re.sub(r"</?poem>|</?onlyinclude>", "", t)
    t = re.sub(r"<子部[^>]*>", "", t)
    return t


def flat(s: str) -> str:
    """版面折行接上；去掉行首缩进与卷末题名"""
    lines = [l.strip("　 ") for l in s.split("\n")]
    lines = [l for l in lines if l and not re.fullmatch(r"(?:欽定四庫全書|遁甲演義卷[一二三四]〕?|明　程道生　撰|欽定協紀辨方書卷三十五〕?)", l)]
    return "".join(lines).strip()


def cut(text: str, marks: list) -> list:
    """marks：[(key, 起点标记)]，按出现先后切；最后一段到 end 标记或全文末"""
    pos = []
    for key, m in marks:
        i = text.find(m)
        if i < 0:
            raise SystemExit(f"找不到篇首标记 {m!r}")
        pos.append((i, i + len(m), key))
    pos.sort()
    out = []
    for n, (i, j, key) in enumerate(pos):
        end = pos[n + 1][0] if n + 1 < len(pos) else len(text)
        out.append((key, flat(text[j:end])))
    return out


H = lambda name: f"　　{name}〕"   # noqa: E731  篇名行

# ---------------- 遁甲演義 ----------------
VOL1 = ["遁甲源流", "年家竒門", "月家竒門", "日家竒門", "時家竒門", "烟波釣叟賦", "八門九星逐時移宫訣",
        "黄帝隂符經", "竒門原始", "遁甲神機賦", "超神接氣置閏訣", "超接引例", "又引證", "遁甲錯誤須檢㸃"]
VOL2 = [("天遁", "　　天遁\n"), "地遁", "人遁", "飛鳥跌穴", "青龍回首", "玉女守門", "三竒得使", "神遁", "鬼遁",
        "風遁", "雲遁", "龍遁", "虎遁", "天三門地四户", "地私門", "太衝天馬", "三詐五假", "亭亭白奸", "三勝宫五不擊",
        ("青龍逃走", H("三竒凶格") + "\n　　青龍逃走\n"), "白虎猖狂", "朱雀入江", "螣蛇跃蹻", "大隔", "小隔并嵗隔月隔日隔時隔", "刑隔", "勃隔",
        "熒入白", "白入熒", "伏干格", "飛干格", "伏宫格", "飛宫格", "六庚加宫六庚同宫格", "三竒受制", "五不遇",
        "三竒入墓", "六儀擊刑", "伏吟格", "反吟格", "門迫宫迫", ("天網四張格", "　　天網四張格"), "伏錯休囚"]
VOL3 = ["九星所屬", "五行旺相休囚", "天輔之時", "遁甲利客", "遁甲利主"] + \
       [f"九星{z}時尅應" for z in "子丑寅夘辰巳午未申酉戌亥"] + \
       ["天乙直符吉凶神説", "三竒喜怒", "冬至陽遁時竒起例", "夏至隂遁時竒起例", "推九星分野吉凶", "竒遁佈局法"]
# 卷二「太衝天馬」篇內，「以授時厯看審訂太陽過〕宫方可選用…」是该篇的续表，录文把半句当成了篇名；
# 卷二「亭亭白奸」篇內「日〕」同为表格残字。两处都不作篇首，留在所属篇内
VOL3_STOP = H("玉女反閉訣")
SKIPPED = {
    "卷三": ["玉女反閉訣", "術曰（籌法）", "十二日圖式", "起初布陣安籌呪", "禹罡式", "四縱五横法", "三竒呪", "又傳三竒呪併附録"],
    "卷四": ["隂陽二遁十八局圖（原书为图，录文无字）", "真人閉六戊法", "真人步斗法", "六甲隂符法", "禁敵法", "六甲所在神身", "六丁符式"],
}


def marks_of(heads):
    return [(h, H(h)) if isinstance(h, str) else h for h in heads]


def yanyi():
    items = []
    for vol, heads, stop in ((1, VOL1, None), (2, VOL2, None), (3, VOL3, VOL3_STOP)):
        t = text_of(f"yanyi-{vol}")
        if stop:
            t = t[:t.index(stop)]
        for key, body in cut(t, marks_of(heads)):
            items.append({"key": f"卷{'一二三'[vol - 1]}|{key}", "vol": vol, "chapter": key, "text": body})
    return {
        "book": "dunjiayanyi", "title": "遁甲演義", "author": "明 程道生 撰", "edition": YANYI_EDITION,
        "note": "四库全书正编所收唯一一部遁甲书。卷一起例与超神接氣置閏，卷二吉凶諸格（多附算例），卷三九星屬性、旺相、八神與兩則有年月日的完整布局算例。",
        "skipped": SKIPPED,
        "items": items,
    }


# ---------------- 欽定協紀辨方書 卷三十五 ----------------
def xieji():
    t = text_of("xieji-35")
    t = t[t.index(H("竒門三元歌")):t.rindex(H("欽定協紀辨方書卷三十五"))]
    marks = [("竒門三元歌", H("竒門三元歌")), ("陽遁歌", H("陽遁歌")), ("隂遁歌", H("隂遁歌")),
             ("八門九星定例歌", H("八門九星定例歌")), ("按語", "　　按竒門擇時之法"),
             ("陽遁一局式", "　　如陽遁一局甲子戊"), ("隂遁九局式", "　　如隂遁九局甲子戊")]
    items = []
    for key, body in cut(t, marks):
        if key == "按語":
            body = "按竒門擇時之法" + body
        elif key.endswith("式"):
            body = ("如陽遁一局甲子戊" if key.startswith("陽") else "如隂遁九局甲子戊") + body
        items.append({"key": f"卷三十五|{key}", "vol": 35, "chapter": key, "text": body})
    return {
        "book": "xiejibianfang", "title": "欽定協紀辨方書", "author": "清 允祿等 奉敕撰", "edition": XIEJI_EDITION,
        "note": "乾隆官修選擇書。卷三十五末附「竒門三元」：歌訣（與《烟波釣叟賦》同源而有異文）、陰陽遁局數歌、八門九星本位歌，"
                "按語詳述超神、置閏、接氣與飛布之法，並列陽一局、陰九局兩式。",
        "items": items,
    }


BUILDERS = {"dunjiayanyi.json": yanyi, "xiejibianfang-35.json": xieji}


def main(check: bool):
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for name, fn in BUILDERS.items():
        data = fn()
        path = os.path.join(OUT, name)
        body = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
        if check:
            same = os.path.exists(path) and open(path).read() == body
            print(("一致 " if same else "不一致 ") + name)
            bad += not same
        else:
            open(path, "w").write(body)
            print(f"{name}: {len(data['items'])} 条")
    return bad


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
