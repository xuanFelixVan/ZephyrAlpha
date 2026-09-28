---
ttl: task_bound
title: L09 案卷 F93 — PG 图书馆（librarian/lookup/collectors/relations；供数轴 potential_consumers 二次清零维持）
session: zc-l09-20260927
---

# F93 PG 图书馆（J 段 A8，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | collectors/ 全量采集（本日 lib_assets=**44,779 行**，较 wiring_gap 09-27 晨间口径 44,773 又 +6——采集在续跑）；lib_events=**1,960,397 行**（事件账本活） |
| 下游消费 | `python -m zephyr.library.lookup` 查询面；**capability_lookup.py 引用 zephyr.library.lookup（本日 grep 实证=F91↔F93 互链边）**；机生面=generate_front_door.py/generate_library_index.py 两生成器→docs/library/{FRONT_DOOR,INDEX}.md |
| 自动化触发 | 采集=批量/再生成触发（library_regen_reconciler.py 在包内=再生对账件）；查询=按需；血肉编目走 SOP 手工+机生混合 |
| 真源与注册表 | 存储=PG **public** schema `lib_assets`/`lib_events` 双表（本日 information_schema 实证仅此二表，无独立 library schema——骨架"PG 图书馆"系泛称）；DDL 常量真源=ledger_schema.py:67 CREATE TABLE lib_assets（MOD-LIB-001） |
| 门禁与质量尺 | upsert COALESCE 保护（ledger_schema.py:118-123 fingerprint/generation 语义）；血肉编目 SOP=`docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md`（本日实存） |
| 当前运行状态 | **黄**：馆体绿（4.4 万资产+196 万事件+采集续跑）；**供数轴红**：potential_consumers>0 = **0 行**（本日复算），09-24 #410② 回填的 68 条消费方记录已被清空（wiring_gap §2.6 回归维持） |

## 二、子模块三级枚举（src/zephyr/library/ 实扫 6 件+目录）

1. `librarian.py`：馆长体（依赖声明=zephyr.library.schema+depgraph_schema.get_depgraph_pg_connection，头注实锚）。
2. `lookup.py`：查询面（骨架锚点；被 capability_lookup 消费）。
3. `ledger_schema.py`：总账 DDL 常量+身份派生纯函数（lib_assets upsert 全字段 COALESCE 保真）。
4. `relations.py`：关系面（资产间关系/引用边）。
5. `collectors/`：采集器族（资产发现→登记→事件写入）。
6. `library_regen_reconciler.py`：再生对账件（事件触发对账入口）。
7. 机生产物：`docs/library/FRONT_DOOR.md`+`INDEX.md`+backup/code/data 等分册（本日 ls 实存）。

## 三、接线四态独立复核

- **采集入库=已接线（活性实证）**：行数 44,773→44,779 同日增长；lib_events 196 万行。
- **查询消费=半接线**：代码消费方仅 capability_lookup+两生成器；**potential_consumers 字段全空**——"谁该吃这份资产"的供数轴二次清零（wiring_gap §2.6：#410② 回填 68 条被 09-25~27 全量重采集清空，HEAD upsert 有 COALESCE 保护、采集器不携字段 ⇒ 元凶疑似 ingest 进程吃启动时刻旧代码）。
- **对账件=在位但未阻再清**：library_regen_reconciler.py 存在，然清零回归仍发生——对账粒度未覆盖 potential_consumers 字段（或未被触发）。
- **SOP 面=已接线**：血肉编目 SOP 实存，机生两册在 docs/library/。

## 骨架勘误

1. 骨架"built"须加供数轴黄旗：**馆体 built、消费登记轴（potential_consumers）处于清零回归态**——"图书馆查出来没接管线的有多少"这一 Owner 问句的数据基础当前为空。
2. 存储位置细化：无独立 `library` schema，真身=PG **public**.lib_assets/lib_events 两表（信息面检索时常被 schema 名误导）。
3. 行数时点更新：44,773（晨间清单）→44,779（本卷探针），采集活性旁证。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | potential_consumers 二次清零回归（68 条存证在 lib_events） | 按 wiring_gap §2.6 处置：**定位清零元凶与机械重放 68 条同袋**（否则重放后再被清）——施工归 library/采集车道 | P1 |
| 2 | regen reconciler 未拦字段级清零 | 对账粒度扩到 potential_consumers 非空不变量（或采集器携带字段透传） | P1 |
| 3 | 代码消费方仅 4 个（lookup 实际采用率低） | 随 F91 互链边扩消费面；不作硬指标 | P2 |

## 五、自审闸三态

**挖干（六件穷举+双表行数+消费方 grep 反查+SOP 实存）✅；待裁（缺口#1 元凶定位与重放时序归采集车道/Owner）；待挖（collectors 逐采集器深挖——P2，wiring_gap 已给机判名单，本卷不重挖）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute('SELECT count(*) FROM public.lib_assets'); print(cur.fetchall()); cur.execute('SELECT count(*) FROM public.lib_assets WHERE cardinality(potential_consumers)>0'); print(cur.fetchall()); cur.execute('SELECT count(*) FROM public.lib_events'); print(cur.fetchall()); c.close()"
ls src/zephyr/library/
ls docs/library/ | head -5
grep -rn "zephyr.library.lookup\|from zephyr.library" src/zephyr/governance/capability_lookup.py | head -2
```
