# 天秩典籍 · tianzhi-classics

东方术数原典的公有领域版本，以及它们与算法的对应关系。

天秩（[tianzhi.live](https://tianzhi.live)）的算法里每一条有出处的规则都来自这些书。
这个仓库把书本身、以及「算法的哪一条对应书里的哪一段」记下来，让结论可以回溯到原文。

## 收录标准

只收**原典**，且必须是已进入公有领域的版本。

- 收：清代及以前的原书，作者逝世逾七十年，版本本身无现代著作权。
- 不收：现代点校本、白话译注、今人注解、出版社影印本的版式。
  这些的著作权在整理者与出版方手里，收录会带来法律风险。

每一部书记明来源与版本依据，见 `catalog.json` 的 `source` 与 `license` 字段。
拿不准来源的，宁可不收。

## PDF 放在 Release，不在仓库里

扫描本动辄几十上百 MB。直接提交进仓库，git 历史里每个版本都会留一份，删不掉，
仓库很快会撑过 GitHub 建议的 1GB 上限。

所以 PDF 一律作为 **Release Asset** 发布：单文件上限 2GB，不计入仓库体积，
走 GitHub 自己的 CDN。仓库里只留清单和文本，永远只有几百 KB。

下载地址的拼法：

```
https://github.com/zaoxu001/tianzhi-classics/releases/download/<release>/<asset>
```

两者都在 `catalog.json` 里每本书的 `pdf` 字段下。

## 锚点：算法怎么指回原文

`anchors` 字段说明一本书的段落用什么方式定位，不同的书编排方式不同：

| 取值 | 含义 | 用在 |
| --- | --- | --- |
| `gan-month` | 日干 × 月令，120 格 | 穷通宝鉴 |
| `geju` | 按格局分章 | 子平真诠 |
| `chapter` | 按篇目 | 其余 |

`gan-month` 这一类不需要人工标注。《穷通宝鉴》本身就是十天干乘十二月令编成的
120 格，算法里的调候用神表跟它逐格对应，所以「日干 + 月支」直接就是条目编号——
排盘算出丁日生丑月，锚点就是 `丁-丑`，无需中间的映射表。这也是调候会成为第一个
打通的模块的原因。

## 目录

```
catalog.json      书目清单：元数据、PDF 位置、锚点方式
texts/<slug>.json 原文摘录，结构跟着该书的 anchors 走
```

`texts/qiongtong.json` 的形状与 `tianzhi_core/data/tiaohou.json` 同构，
一层日干、一层月令，便于逐格比对：

```json
{ "丁": { "丑": "丁火……原文" } }
```

## 相关

- [tianzhi-core](https://github.com/zaoxu001/tianzhi-core) — 算法本身，可独立使用
- [tianzhi.live](https://tianzhi.live) — 在线排盘与研习
