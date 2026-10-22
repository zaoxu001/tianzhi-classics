#!/usr/bin/env python3
"""奇门诸书录文：从维基文库取 wikitext，缓存到本地，供抽取与核对脚本共用。

    python3 tools/qimen_source.py               # 下载缺的
    QIMEN_CACHE=/path python3 ...               # 换缓存目录（默认 .cache/qimen，不入库）

所据：
  遁甲演義 (四庫全書本) 卷1–4      明 程道生撰。四库正编所收唯一一部遁甲书，本仓奇门的主底本
  欽定協紀辨方書 (四庫全書本) 卷35  清 允祿等奉敕撰。「遁甲」一门：超神接氣置閏、九星八門、八神
  煙波釣叟歌                       舊題宋 趙普撰，明 羅通刪定。通行歌訣，作旁證
  奇門遁甲統宗                     明清坊間彙編，作流派層旁證

录文不入库：底本在维基文库，谁都能重取；仓库只收从中切出的条目与切法。
维基文库录文为 CC BY-SA，本仓只摘句标注出处，今译自撰。影像底本见 catalog.json。
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("QIMEN_CACHE") or os.path.join(ROOT, ".cache", "qimen")
API = "https://zh.wikisource.org/w/api.php"

PAGES = {
    "yanyi-1": "遁甲演義 (四庫全書本)/卷1",
    "yanyi-2": "遁甲演義 (四庫全書本)/卷2",
    "yanyi-3": "遁甲演義 (四庫全書本)/卷3",
    "yanyi-4": "遁甲演義 (四庫全書本)/卷4",
    "xieji-35": "欽定協紀辨方書 (四庫全書本)/卷35",
    "yanbo": "煙波釣叟歌",
    "tongzong": "奇門遁甲統宗",
}


def fetch(key: str) -> str:
    """某一篇的 wikitext；有缓存用缓存"""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{key}.txt")
    if not os.path.exists(path):
        q = urllib.parse.urlencode({"action": "parse", "page": PAGES[key], "prop": "wikitext",
                                    "format": "json", "formatversion": 2})
        req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": "tianzhi-classics/1.0"})
        for wait in (0, 5, 15, 45):          # 维基文库限频，被拒就等一会儿再取
            time.sleep(wait or 1)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    text = json.load(r)["parse"]["wikitext"]
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or wait == 45:
                    raise
        open(path, "w").write(text)
    return open(path).read()


def clean(text: str) -> str:
    """去掉模板外壳：注文作〔〕，缺字作□，锚点只留文字。不改原文用字"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\{\{SK notes\|", "〔", text)
    text = re.sub(r"\{\{SKchar\|\d+\}\}", "□", text)
    text = text.replace("}}", "〕")
    return re.sub(r"\{\{SK anchor\|", "", text)


def text(key: str) -> str:
    return clean(fetch(key))


if __name__ == "__main__":
    for k in PAGES:
        print(f"{k:10s} {len(fetch(k)):7d} 字符  {PAGES[k]}")
