---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F15 车道A·社区货源（聚宽 597 条人工版）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-035
map_node: FAC-E1A
---

# F15 · 车道A-社区货源

## 一、环节定义与边界
一句话：聚宽/掘金等社区策略源码收货→盘点归一→粗筛判定→灌考试台账（C1-C2 人工版流水线；图9 口径 built）。
上游供料=人工批量下载的社区源码目录（E:\数据下载\qmt聚宽策略\2020-2026聚宽600条源码）；下游消费=screen_c2.csv→c1_backtest.strategy_screen（intake_load_screen_c2 灌表）→E4 批测/C4 翻译漏斗。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | 本地源码目录（strategy_intake_inventory.py:48 _DEFAULT_SRC）；六个年度子目录实测在册：2020/2022/2023/2024/2025/2026 年度精选各 99-101 条 |
| 下游消费 | raw_manifest.csv（597 行实测）→normalized/<year>/ 归一副本（UTF-8）→screen_c2.csv（597 判定）→c1_backtest.strategy_screen 灌表（intake_load_screen_c2.py，幂等按 (screen_batch, strategy_id)）→C4 翻译批（35 条验收集=scripts/backtest/translated/ 人工件源头） |
| 自动化触发 | 无（人工收货+一次性盘点；图9 自认"C1 人工版"；Scrapling 爬虫=扩容候选未建） |
| 真源与注册表 | MOD-BT-035 在 path_ownership_map.yaml:35444 在册（inventory 头注自称 MOD-BT-035 一致）；SOP 真源=backtest_system_sop/sop_c_strategy_library_intake.md §1；图9 FAC-E1A build_status=built |
| 门禁与质量尺 | 破损/空文件记 unreadable 不修复不猜测（inventory :108-109）；原文件只读不删改；md5_12 内容指纹判重（dup_content 汇总）；平台特征启发式（聚宽 API 标记 11 种 :51-55）；产物落 gitignore 区（可再生，预注册类资产才进 git） |
| 当前运行状态 | **绿（存量）/停（增量）**。证据：raw_manifest 597 行（year 分布 2020→2026 全覆盖）；screen_c2.csv 597 行=381 candidate/216 excluded（七类硬排除，代码注释自证 2026-09-12 夜班批 commit 52cb9e8ab6）；**09-12 后零新增**——最近真实出货=2026-09-12 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 盘点归一 inventory（C1） | scripts/backtest/strategy_intake_inventory.py:78-128 | built（production 级，597 行实证） |
| 解码兜底 _decode（utf-8/gbk/gb18030/utf-16） | 同上:58-65 | built |
| 粗筛成绩灌表 intake_load_screen_c2（R3 收尾） | scripts/backtest/intake_load_screen_c2.py:24- | built（幂等灌 strategy_screen） |
| 网络爬虫（Scrapling 扩容） | — | **missing**（design_refs 声明候选，零代码） |
| 增量收货事件化 | — | missing（与 F14 事件触发器同根） |

## 四、堵点与病灶
1. **增量断流**：597 条是一次性人工收货，此后车道 A 零产能；根因=无爬虫+无收货事件；修法=Scrapling 爬虫立项（图9 已留 design_refs）或维持"人工批量投喂+inventory 增量跑"低配形态（inventory 现为全量重写语义，需加增量模式）；爬虫≈2-3 天、增量模式≈0.5 天；本车道可修（低配版）。
2. **源路径硬编码出盘**：_DEFAULT_SRC 指向 E:\ 数据目录（盘外依赖）——换机即断；修法=--src 参数已有，缺省值改配置项或收货入库 data 区；0.5 天。
3. **归一副本与 manifest 双写无事务**：中断态可能 manifest 有行而副本缺——现状未见事故，登记为低风险（inventory 可重跑自愈）。

## 五、提速与合并机会
- strategy_intake_inventory 与 lane 各台账同放 data/strategy_intake/（台账族统一）；无需合并。
- C2 粗筛判定规则（七类硬排除）是全厂唯一"进货硬排除"清单，可被 E2 预审引用为第 0 问（边界问已有）——提效点而非合并点。

## 六、自审闸三态
- **三态结论：built（图9 人工版口径成立）**——盘点/归一/粗筛/灌表四件全实证。若按"自动化社区进货"口径则 partial（爬虫+事件化缺），建议图9 在 algo_note 注明"人工版 built、爬虫未建"防口径歧义。
- **差什么才算 built（自动化口径）**：①Scrapling 爬虫件+源注册；②inventory 增量模式；③收货事件接 F14 编排。

## 七、复核命令
```bash
python -c "import csv;rows=list(csv.DictReader(open('data/strategy_intake/raw_manifest.csv',encoding='utf-8-sig')));print(len(rows), {r['year'] for r in rows})"
python scripts/backtest/strategy_intake_inventory.py --dry-run --src "E:\\数据下载\\qmt聚宽策略\\2020-2026聚宽600条源码"   # 盘点可复跑
python -c "import csv;rs=list(csv.DictReader(open('data/strategy_intake/screen_c2.csv',encoding='utf-8-sig')));from collections import Counter;print(Counter(r['decision'] if 'decision' in r else list(r.values())[-1] for r in rs))"
```
