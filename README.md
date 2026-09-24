# tianzhi-classics

中华术数典籍的结构化数据集。

## 概述

术数典籍中的取用规则是确定的、可枚举的：《穷通宝鉴》以十天干配十二月令，列出
一百二十格调候取用；《金不换大运》于同样一百二十格给出喜忌天干与大运地支顺逆。
这些规则四百年来以文字形式流传，本数据集将其整理为机器可读的结构化数据。

数据随 [tianzhi-core](https://github.com/zaoxu001/tianzhi-core) 发布，算法直接
据此计算，计算结果携带出处标签，可逐条回溯至对应条目。

## 数据来源

| 典籍 | 时代 · 作者 | 提取内容 | 条目 |
| --- | --- | --- | --- |
| 窮通寶鑑（一名欄江網、造化元鑰） | 明 · 余春臺 輯 | 调候取用：日干 × 月令 | 120 |
| 金不換大運 | 清 · 佚名 | 喜忌天干、大运地支顺逆：日干 × 月令 | 120 |

均为公有领域古籍。仅提取规则，不转载原文；原文参考链接见 `catalog.json` 的
`ref` 字段。

## 数据结构

### 调候取用 `tianzhi_core/data/tiaohou.json`

两层映射，日干 → 月令 → 所取天干，按首要程度排序。

```json
{ "辛": { "午": ["壬", "己", "癸"] } }
```

### 喜忌与大运 `tianzhi_core/data/jinbuhuan.json`

两层映射，日干 → 月令 → 条目对象。

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

### 书目 `catalog.json`

| 字段 | 含义 |
| --- | --- |
| `slug` | 标识符 |
| `module` | 所属门类，见 `modules` |
| `title` `dynasty` `author` `alias` | 书名、时代、作者、别名 |
| `anchors` | 条目定位方式：`gan-month` 为日干 × 月令，`chapter` 为篇目 |
| `rules` | 规则表路径 |
| `ref` | 原文参考链接 |

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

亦可直接读取 JSON，数据随包分发于 `tianzhi_core/data/`。

算法输出的每条判据均带出处标签，格式为「书名·条目」：

```
穷通宝鉴·辛日午月      日干与月令即条目坐标
子平真诠·论用神        篇名即条目坐标
```

## 许可

数据部分为公有领域古籍中的规则，不构成受著作权保护的表达：条目内容为事实性
对应关系，编排体例出自原书。

现代点校本、白话译注及今人解读不在收录范围。

代码及元数据以 MIT 许可发布。

## 相关项目

- [tianzhi-core](https://github.com/zaoxu001/tianzhi-core) — 术数算法，MIT
- [tianzhi.live](https://tianzhi.live) — 在线排盘与研习
