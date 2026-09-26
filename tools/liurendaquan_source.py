#!/usr/bin/env python3
"""《六壬大全》录文：从维基文库取十二卷的 wikitext，缓存到本地，供抽取与核对脚本共用。

    python3 tools/liurendaquan_source.py          # 下载缺的卷
    LRDQ_CACHE=/path python3 ...                  # 换缓存目录（默认 .cache/liurendaquan，不入库）

录文不入库：底本在维基文库，谁都能重取；仓库只收从中切出的条目与切法。
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("LRDQ_CACHE") or os.path.join(ROOT, ".cache", "liurendaquan")
API = "https://zh.wikisource.org/w/api.php"
PAGE = "六壬大全 (四庫全書本)/卷{:02d}"


def fetch(vol: int) -> str:
    """某一卷的 wikitext；有缓存用缓存"""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{vol:02d}.txt")
    if not os.path.exists(path):
        q = urllib.parse.urlencode({"action": "parse", "page": PAGE.format(vol), "prop": "wikitext",
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


def volume(vol: int) -> str:
    return clean(fetch(vol))


if __name__ == "__main__":
    for v in range(1, 13):
        n = len(fetch(v))
        print(f"卷{v:02d} {n} 字符 → {CACHE}")
