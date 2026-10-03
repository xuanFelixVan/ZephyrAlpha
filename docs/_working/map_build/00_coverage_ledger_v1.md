---
ttl: task_bound
completes_when: 总线join覆盖账本checker落地并首跑出全量归属表后，本v1被其取代
title: 纵轴覆盖账本 v1——模块全集×六图挂载面机械对账
owner: ZephyrAlpha-Owner
---

# 纵轴覆盖账本 v1：模块全集 × 六图挂载面（2026-10-02 机械对账）

> Owner 目标：全项目模块被纵轴全景图包含。本账本=v1 机械对账（正则键型统计），
> v2=depgraph 总线 join checker（MOD-* → module 精确归属），取代本件。

## 1. 宇宙与挂载面（2026-10-02 实测）

| 图 | 键型 | 模块引用 | src路径 | scripts | 节点数(name_zh) |
|----|------|---------|---------|---------|----------------|
| GOMAP（治理运行） | dotted+src | 378 | 367 | 80 | 12层 |
| TDM（交易决策） | MOD总线 | 105 | 111 | 5 | 184 |
| FACTORY（策略生产） | MOD总线 | 32 | 0 | 0 | 27 |
| 图11 交付流水线 | MOD+路径 | 8 | 12 | 9 | 34 |
| 图12 数据供给链 | MOD+路径 | 9 | 48 | 10 | 61 |
| 图13 交易日循环 | MOD+路径 | 13 | 22 | 2 | 53 |

## 2. 结论：六图=骨架已成、血肉严重稀疏

1. 宇宙基准=GOMAP 机生清单（counts 声明 442 模块；文本可提取 378 dotted+367 路径）。
2. GOMAP 自账：wired 245 + dynamic 15 + by_header 88 = 348/442，**suspect_orphans 94**。
3. 新三图每张仅显式挂 9~48 个引用——**环节骨架齐了，模块挂载血肉没填**。
4. TDM 是挂载大户（105 MOD 键），FACTORY 32 键次之。
5. 精确"每模块属于哪张图"必须走 depgraph 总线 join（MOD-*→module 路径），纯文本正则只能到本 v1 粒度。

## 3. 缺口三件套（Owner 四目标对应）

| 缺口 | 内容 | 动作 |
|------|------|------|
| A 转正批 | 图11/12/13 未入 §3、无校验器/gate（挂轴0次） | 四件套收尾（FACTORY-MAP 配方） |
| B 总线join账本 | MOD-*→module 精确归属+孤儿簇分组 | align_all 新节/checker 立项 |
| C 挂载血肉填充 | 新三图按环节挖矿补 mounts；GOMAP 94 孤儿入图或退役 | 每图一个填充车道 |

## 4. 归属表（v2 由 join checker 自动产出）

格式：`module_id | 纵轴归属图 | wiring_status | 缺口动作`。本 v1 留空待 join checker——
禁止手工填表（宪法 §9.5），表由生成器产出。
## 5. 宇宙口径终批补记（2026-10-03，裁定#481）

Owner 已批：主账=src/zephyr .py（__init__. 并入父包，非空者计）+scripts .py+frontend
js/html ≈5,200；辅账=tests（跟随被测对象）+docs（图书馆管）；全仓 19,281 禁作分母。
GOMAP counts=运行时视图口径并行保留。**#9 join checker 的分母自此法定**，归属总表
施工可开工（设计稿见 20 号文件）。
