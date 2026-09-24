# tianzhi-classics

中华术数典籍的结构化数据集。

## 概述

术数典籍中的取用规则是确定的、可枚举的：《穷通宝鉴》以十天干配十二月令，列出
一百二十格调候取用；《子平真诠》就八格分别指明顺用逆用、相神与忌神；《三命通会》
《协纪辨方书》载各神煞的起例。这些规则数百年来以文字形式流传，本数据集将其整理
为机器可读的结构化数据。

数据随 [tianzhi-core](https://github.com/zaoxu001/tianzhi-core) 发布，算法直接
据此计算，计算结果携带出处标签，可逐条回溯至对应条目。

## 数据来源

| 典籍 | 时代 · 作者 | 提取内容 | 条目 | 文件 |
| --- | --- | --- | --- | --- |
| 窮通寶鑑（一名欄江網、造化元鑰） | 明 · 余春臺 輯 | 调候取用：日干 × 月令 | 120 | `bazi/tiaohou.json` |
| 金不換大運 | 清 · 佚名 | 喜忌天干、大运地支顺逆：日干 × 月令 | 120 | `bazi/jinbuhuan.json` |
| 子平真詮 | 清 · 沈孝瞻 | 八格的顺用逆用、相神与忌神 | 8 | `bazi/geju-ops.json` |
| 滴天髓 | 明 · 劉基 | 从象、化象、通关的判别条件与阈值 | 3 | `bazi/ditian-rules.json` |
| 神峰通考 | 明 · 張楠 | 病药的判别条件与阈值 | 1 | `bazi/shenfeng-rules.json` |
| 三命通會 | 明 · 萬民英 | 天乙贵人起例 | 10 | `bazi/shensha-tianyi.json` |
| 淵海子平 | 宋 · 徐子平 | 文昌贵人起例 | 10 | `bazi/shensha-wenchang.json` |
| 協紀辨方書 | 清 · 允祿 等 奉敕撰 | 天德、月德贵人起例 | 24 | `bazi/shensha-tiande.json`<br>`bazi/shensha-yuede.json` |

另有干支体系的基础对应关系，为诸书通用，非某一部所独出：六十甲子、干支五行、
地支藏干、十二长生、天干五合、地支六合六冲六害、阳刃、旺相休囚死（`bazi/ganzhi.json`），
禄神起例（`bazi/shensha-lushen.json`），人元司令分日（`bazi/siling.json`，各家
天数有异，此为其中一种）。

均为公有领域古籍。仅提取规则，不转载原文；原文参考链接见 `catalog.json` 的
`ref` 字段。

## 目录

```
catalog.json        书目：各书来历、所属门类、整理出的数据文件、原文参考链接
bazi/               八字
tools/check.py      校验本仓数据与 tianzhi-core 一致
```

术数分门，`catalog.json` 的 `modules` 列出门类，每部书以 `module` 归属其一。

## 数据结构

### 调候取用 `bazi/tiaohou.json`

日干 → 月令 → 所取天干，按首要程度排序。

```json
{ "辛": { "午": ["壬", "己", "癸"] } }
```

### 喜忌与大运 `bazi/jinbuhuan.json`

日干 → 月令 → 条目。

```json
{ "辛": { "午": { "xi": ["壬"], "ji": ["丁"],
                  "dayun_xi": ["亥", "子", "寅", "卯"],
                  "dayun_ji": ["申", "酉"],
                  "note": "喜根深" } } }
```

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `xi` | string[] | 喜用天干 |
| `ji` | string[] | 忌见天干 |
| `dayun_xi` | string[] | 大运顺行的地支 |
| `dayun_ji` | string[] | 大运逆行的地支 |
| `note` | string | 原书附注 |

### 格局顺逆 `bazi/geju-ops.json`

格名 → 条目。

```json
{ "财格": { "name": "财格", "mode": "顺",
            "generate": ["食神"], "protect": ["正官"],
            "taboo": ["比肩", "劫财"],
            "note": "财喜食神以相生，生官以护财；忌比劫分夺",
            "source": "子平真诠·论用神" } }
```

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `mode` | string | `顺` 或 `逆`。善者顺用，不善者逆用 |
| `generate` | string[] | 相生之神 |
| `protect` | string[] | 护卫之神 |
| `taboo` | string[] | 忌见之神 |
| `note` | string | 该条的依据 |
| `source` | string | 出处 |

`bazi/geju-alias.json` 为格名别称至正名的映射。

### 取用法则 `bazi/ditian-rules.json` `bazi/shenfeng-rules.json`

并非所有典籍的内容都是查表形态。《滴天髓》论从象、化象、通关，《神峰通考》论
病药，讲的是「什么条件下该怎么取」，条目形如条件与动作。

```json
{ "从象": {
    "source": "滴天髓·从象",
    "quote": "从得真者只论从，从神又有吉和凶。",
    "applies_to": "取用",
    "rules": [
      { "name": "从弱",
        "when": ["同党占比低于 follow_weak_ratio", "日主无强根"],
        "then": "不扶日主，从其旺神（取泄、耗、克日主者中最旺的一行）" }
    ],
    "thresholds": {
      "follow_weak_ratio": { "value": 0.12, "from": "本包取值，可调" }
    } } }
```

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `source` | string | 出处 |
| `quote` | string | 原文成句；未引原文者为空，另以 `quote_note` 说明 |
| `applies_to` | string | 该法则作用于哪一环 |
| `rules[].when` | string[] | 全部成立方才适用 |
| `rules[].then` | string | 成立后如何取用 |
| `thresholds` | object | 判别所用的数值 |
| `thresholds.*.from` | string | 该数值的来历。标「本包取值」者为工程取值，非典籍所定 |

典籍言理不言数，落到可计算的程序上必须给出具体阈值。`from` 字段把两者分开：
哪些是书上说的，哪些是本包定的，不相混淆。这些阈值与代码同源，由 `tools/check.py`
核对。

### 神煞起例 `bazi/shensha-*.json`

以所查之干或支为键，落处为值。

```json
{ "甲": ["丑", "未"] }
```

### 干支基础 `bazi/ganzhi.json`

单文件多表，键为表名。

| 表 | 形状 | 说明 |
| --- | --- | --- |
| `jiazi` | string[60] | 六十甲子，自甲子起 |
| `gan_wuxing` `zhi_wuxing` | 干支 → 五行 | |
| `hidden` | 地支 → [[干, 位]] | 藏干，位为 `本`／`中`／`余` |
| `changsheng` | string[12] | 十二长生次第 |
| `gan_he` `zhi_liuhe` | [{pair, into}] | 合为无序一对，`into` 为合化之行 |
| `zhi_chong` `zhi_hai` | 地支 → 地支 | |
| `yangren` | 阳干 → 地支 | 阴干是否有刃各家分歧，此处只列阳刃 |
| `wangxiang` | string[5] | 旺相休囚死 |

### 人元司令 `bazi/siling.json`

月支 → 依次司令的天干与所占日数。

```json
{ "丑": [ { "gan": "癸", "days": 9 },
          { "gan": "辛", "days": 3 },
          { "gan": "己", "days": 18 } ] }
```

## 使用

```bash
pip install tianzhi-core
```

```python
from tianzhi_core.bazi import tiaohou

tiaohou.climate_gods("辛", "午")
# ClimateGods(day_gan='辛', month_zhi='午', gans=('壬', '己', '癸'),
#             primary='壬', elements=('水', '土'), source='穷通宝鉴')
```

亦可直接读取本仓 JSON，或读取随包分发于 `tianzhi_core/data/` 的同一份数据。

算法输出的每条判据均带出处标签，格式为「书名·条目」：

```
穷通宝鉴·辛日午月      日干与月令即条目坐标
子平真诠·论用神        篇名即条目坐标
```

## 校验

数据在本仓与 tianzhi-core 各有一份，前者是数据集的发布形态，后者是算法运行时
实际读取的那份。两份分处两个仓库，需定期校验，以免漂移。

```bash
python tools/check.py
```

随包的三份逐字节比对；其余几张表由算法常量导出，脚本重新导出后比对；取用法则
两份的条文是人写的，机器无从比对，但其中的阈值逐项核对——阈值一漂，数据上写的
判据就不是算法实际在用的判据。脚本并会反查本仓是否有文件漏在清单之外。

一致则退出码 0，否则逐项列出差异。

## 许可

数据部分为公有领域古籍中的规则，不构成受著作权保护的表达：条目内容为事实性
对应关系，编排体例出自原书。

现代点校本、白话译注及今人解读不在收录范围。

代码及元数据以 MIT 许可发布。

## 相关项目

- [tianzhi-core](https://github.com/zaoxu001/tianzhi-core) — 术数算法，MIT
- [tianzhi.live](https://tianzhi.live) — 在线排盘与研习
