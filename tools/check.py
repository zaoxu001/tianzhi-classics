#!/usr/bin/env python3
"""校验本仓的数据与 tianzhi-core 一致。

数据在两个地方各有一份：这里是数据集的发布形态，tianzhi-core 里是算法运行时
实际读的那份。两份分处两个仓库，不校验迟早漂移，而漂移之后页面上写一套、算出来
另一套，比没有数据更糟。

三个随包文件逐字节比对；其余几张表是从算法的常量导出的，这里重新导出再比对。

取用法则那两份（ditian-rules、shenfeng-rules）的条文是人写的，机器无从比对，
但里面的阈值必须跟代码一致——阈值一漂，数据上写的判据就不是算法实际在用的判据。
所以逐个核对 thresholds 里的 value。

    pip install tianzhi-core
    python tools/check.py

一致则退出码 0，否则逐项列出差异并返回 1。
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def plain(v):
    """把库里的 dataclass、tuple、frozenset 归一成 JSON 能表达的形状。"""
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return {k: plain(x) for k, x in dataclasses.asdict(v).items()}
    if isinstance(v, frozenset):
        return sorted(sorted(x) if isinstance(x, frozenset) else x for x in v)
    if isinstance(v, set):
        return sorted(v)
    if isinstance(v, (tuple, list)):
        return [plain(x) for x in v]
    if isinstance(v, dict):
        return {k: plain(x) for k, x in v.items()}
    return v


def pairs(d):
    """合是无序的一对，库里用 frozenset 当键，JSON 没有这种键，改成数组。"""
    return sorted(({"pair": sorted(k), "into": v} for k, v in d.items()),
                  key=lambda x: x["pair"])


def expected() -> dict[str, object]:
    from importlib import resources

    from tianzhi_core.bazi import geju, shensha
    from tianzhi_core.core import ganzhi

    out: dict[str, object] = {}
    # 随包的三份，以库里那份为准
    for name in ("tiaohou.json", "jinbuhuan.json", "siling.json"):
        with resources.files("tianzhi_core.data").joinpath(name).open(encoding="utf-8") as f:
            out[f"bazi/{name}"] = json.load(f)
    out["bazi/geju-ops.json"] = plain(geju.PATTERN_OPS)
    out["bazi/geju-alias.json"] = plain(geju.PATTERN_ALIAS)
    out["bazi/shensha-tianyi.json"] = plain(shensha.TIAN_YI)
    out["bazi/shensha-wenchang.json"] = plain(shensha.WEN_CHANG)
    out["bazi/shensha-lushen.json"] = plain(shensha.LU_SHEN)
    out["bazi/shensha-tiande.json"] = plain(shensha.TIAN_DE)
    out["bazi/shensha-yuede.json"] = plain(shensha.YUE_DE)
    out["bazi/ganzhi.json"] = {
        "jiazi": plain(ganzhi.JIAZI),
        "gan_wuxing": plain(ganzhi.GAN_WUXING),
        "zhi_wuxing": plain(ganzhi.ZHI_WUXING),
        "hidden": plain(ganzhi.HIDDEN),
        "changsheng": plain(ganzhi.CHANGSHENG),
        "gan_he": pairs(ganzhi.GAN_HE),
        "zhi_liuhe": pairs(ganzhi.ZHI_LIUHE),
        "zhi_chong": plain(ganzhi.ZHI_CHONG),
        "zhi_hai": plain(ganzhi.ZHI_HAI),
        "yangren": plain(ganzhi.YANGREN),
        "wangxiang": plain(ganzhi.WANGXIANG),
    }
    return out


#: 取用法则里的阈值 → 代码中的常量。阈值是算法的判据，写进数据就得跟代码同源。
THRESHOLDS: dict[str, list[tuple[str, str, str, str]]] = {
    "bazi/ditian-rules.json": [
        ("从象", "follow_weak_ratio", "yongshen", "FOLLOW_WEAK_RATIO"),
        ("从象", "follow_strong_ratio", "yongshen", "FOLLOW_STRONG_RATIO"),
        ("化象", "share_yes", "interact", "TRANSFORM_SHARE_YES"),
        ("化象", "share_no", "interact", "TRANSFORM_SHARE_NO"),
        ("通关", "min_share", "yongshen", "TONGGUAN_MIN_SHARE"),
        ("通关", "balance_max", "yongshen", "TONGGUAN_BALANCE_MAX"),
    ],
    "bazi/shenfeng-rules.json": [
        ("病药", "bing_margin", "yongshen", "BING_MARGIN"),
    ],
}


def check_anchors() -> list[str]:
    """原文锚点表里的干支五行须与库一致，否则拼出来的锚点会指错地方。"""
    from tianzhi_core.core import ganzhi

    path = ROOT / "bazi/ref-anchors.json"
    if not path.exists():
        return ["bazi/ref-anchors.json：本仓缺这个文件"]
    with path.open(encoding="utf-8") as f:
        doc = json.load(f)
    got = doc.get("qiongtong", {}).get("wuxing_of_gan")
    if got != dict(ganzhi.GAN_WUXING):
        return ["bazi/ref-anchors.json：wuxing_of_gan 与 ganzhi.GAN_WUXING 不一致"]
    return []


def check_thresholds() -> list[str]:
    from importlib import import_module

    bad = []
    for rel, items in THRESHOLDS.items():
        path = ROOT / rel
        if not path.exists():
            bad.append(f"{rel}：本仓缺这个文件")
            continue
        with path.open(encoding="utf-8") as f:
            doc = json.load(f)
        for rule, key, module, const in items:
            got = doc.get(rule, {}).get("thresholds", {}).get(key, {}).get("value")
            want = getattr(import_module(f"tianzhi_core.bazi.{module}"), const)
            if got != want:
                bad.append(f"{rel} {rule}.{key}：数据为 {got}，代码 {const} 为 {want}")
    return bad


def main() -> int:
    try:
        want = expected()
    except ModuleNotFoundError:
        print("需要先装上 tianzhi-core：pip install tianzhi-core", file=sys.stderr)
        return 2

    bad = []
    for rel, value in want.items():
        path = ROOT / rel
        if not path.exists():
            bad.append(f"{rel}：本仓缺这个文件")
            continue
        with path.open(encoding="utf-8") as f:
            got = json.load(f)
        if got != value:
            bad.append(f"{rel}：与 tianzhi-core 不一致")

    bad += check_thresholds()
    bad += check_anchors()

    # 反过来也查一遍：本仓有、校验清单里没有的文件，说明清单忘了更新
    listed = ({ROOT / r for r in want} | {ROOT / r for r in THRESHOLDS}
              | {ROOT / "bazi/ref-anchors.json"})
    # bazi/entries/ 下是自原书提取的条目，没有对应的代码常量可比，跳过
    for path in sorted((ROOT / "bazi").glob("*.json")):
        if path not in listed:
            bad.append(f"bazi/{path.name}：不在校验清单里，tools/check.py 忘了更新")

    if bad:
        print("数据不一致：", file=sys.stderr)
        for line in bad:
            print("  " + line, file=sys.stderr)
        return 1
    print(f"一致，共 {len(want) + len(THRESHOLDS)} 个文件，"
          f"{sum(len(v) for v in THRESHOLDS.values())} 项阈值")
    return 0


if __name__ == "__main__":
    sys.exit(main())
