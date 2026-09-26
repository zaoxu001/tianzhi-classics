#!/usr/bin/env python3
"""《紫微斗数全书》录文：从维基文库取三卷的 wikitext，缓存到本地，供抽取脚本共用。

    python3 tools/ziweiquanshu_source.py          # 下载缺的卷
    ZWQS_CACHE=/path python3 ...                  # 换缓存目录（默认 .cache/ziweiquanshu，不入库）

维基文库本是依某现代排印本录入的（加了标点，卷二卷三为简体），不是底本。
底本取明南阳堂刊本《新鋟希夷陳先生紫微斗數全書》七卷（1600，Internet Archive 有扫描），
录文与底本的出入逐条记在 ziwei/collation.json。
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("ZWQS_CACHE") or os.path.join(ROOT, ".cache", "ziweiquanshu")
API = "https://zh.wikisource.org/w/api.php"
VOLS = ["卷一", "卷二", "卷三"]


def fetch(vol: str) -> str:
    """某一卷的 wikitext；有缓存用缓存"""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{vol}.txt")
    if not os.path.exists(path):
        q = urllib.parse.urlencode({"action": "parse", "page": f"紫微斗數全書/{vol}", "prop": "wikitext",
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


if __name__ == "__main__":
    for v in VOLS:
        print(v, len(fetch(v)), "字符 →", CACHE)
