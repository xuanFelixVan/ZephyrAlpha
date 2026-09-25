---
ttl: task_bound
lane: M1 数据链（补挖波，接续 st-commitspeed-tbl-20260924）
segment: F08 冷库归档运维——built（待深挖确认）四项待确认点收敛（总册 P2）
mined_at: 2026-09-25
session: st-ailayer-fullflow-d
---

# 09_f08_cold_storage_confirm — 冷库归档 built 确认补挖册（F08）

> **与既有册关系**：04_cold_storage.md 已挖干 D8/D9 并主张收编；本册只答总册 F08 状态列的"**built（待深挖确认）**"之"待确认"三事：①归档机械是否真活（运行证据）②04 册 S1"drawers.jsonl G: 笔误"再判定③双库并存（F/G）与口径漂移。引用 04 册结论不重挖。

## 一、环节定义与边界

一句话（补挖口径）：F:/zephyr_cold Parquet 冷库+archiver 三阶段归档链的**运行中确认**；上游=F06 老分区（archiver list 实证 2515 分区进出），下游=长周期回测补历史原料（20_raw 新条实证）。

## 二、六向台账（增量面，基础面见 04 册）

| 向 | 内容与实证 |
|---|---|
| 上游输入 | CH c1_market 老分区（archiver list 实测 **2515 个分区**全部"已验证+已删除"双 ✓：kline_60min 自 2000-06 起 2026-08-10 归档 → kline_etf_30min 至 2011-04 于 **2026-09-24 02:07** 归档——归档链三天前还在真实进出）；库外语料（altdata 语料线+研报+C4 PDF 缓存迁入） |
| 下游消费 | **长周期回测供料实证**：drawers.jsonl 第 10 行（2026-09-24）20_raw/etf_lof_minute_history_20260924（5,467,846,518B，ETF/LOF 分钟 zip 族 2005-2025，"CH c1_market 分钟表仅 2021-07（ETF）/2019-01（LOF）起——本族含 2005 起历史段=未来补历史入 CH 原料"原文注）——总册 F08"下游=长周期回测"从推测变实证；restore_partition 回灌（04 册已锚 :793） |
| 自动化触发 | 归档=手动/事件 CLI（04 册已记，确认不变）；备份族三计划任务 Ready（04 册）；**迁移类事件实际高频**：drawers.jsonl 近四条全是迁入/归档登记（09-21 整迁+09-24 三笔） |
| 真源与注册表 | manifest=00_manifest/drawers.jsonl **现 10 行**（04 册读时 5 行，append-only 增长中）；架构登记 INFRA-STORE-003；保留合同 data_retention_contract.yaml（CFG-data_retention_contract，在盘实核）； lifecycle 字段（hot_90d/permanent）在 business_data_categories.yaml :27/:49 实核——04 册 §五.1 自动化候选单的表驱动基础成立 |
| 门禁与质量尺 | 五重安全阀 v1.3.0（04 册已挖）；本册增量实证：09-24 三笔迁入的登记注记均带件数+字节全等/sha256 抽样对账（C4 缓存 60,245 件 56.6GB"件数字节全等+20 件 sha256 抽样全等"原文）——对账纪律在实战中执行 |
| 当前运行状态 | **绿（built 确认成立）**。机械活（2515 分区+09-24 最新归档）；登记活（manifest 10 行增长）；对账活（迁移注记自带验证数据）；存储战术活（09-21 G→F 整迁按 Owner 定案执行） |

## 三、待确认三事取证

### ① 归档机械运行证据（答"built"）

- `python scripts/ch/archiver.py list`（只读）实测 2515 分区全 ✓✓；时间跨度证明非一次性工程：最早批 2026-08-10（kline_60min 2000-06 起），最新批 **2026-09-24T02:07**（kline_etf_30min 2011-04）。
- 04 册"ETF/LOF 分钟史已归档 c1_market 10 目录"与此互证。

### ② 04 册 S1"drawers.jsonl 第 5 行 G: 笔误"——**判定反转：非笔误，是迁移前化石**

- F:/zephyr_cold/00_manifest/drawers.jsonl 现 **10 行**；第 4-6 行为 2026-09-18 同批登记（chinawuliu 运价快照+irm 互动易/调研纪要），其中第 5-6 行 path 写 `G:/zephyr_cold/...`——登记当时数据**确实在 G**（G 侧同 manifest 6 行可对照，2026-09-18 起零增长=冻结）。
- 第 7 行（2026-09-21）整迁登记 source 原文："G:/zephyr_cold 整体迁入（a3 阶段1.2，**Owner 定案 F=冷储专项**）……95,194 文件/137.6G 共同文件字节全等……目录结构 1:1 保留"——manifest 连同数据 1:1 搬家，G: 路径行是**历史事实**，append-only/immutable 原则下**不可改也不应改**。
- **修法更正**：04 册 S1 的修法"核实物后修正 manifest 行（safe_write_text CAS）"**撤销**；改为：不动 manifest，在 storage_map.md 或冷库 README 加一行"09-18 条目中的 G: 路径=迁移前旧址，现位于 F 同路径"检索注（0.1 天）。

### ③ 双库并存与口径漂移

- G:/zephyr_cold 仍存活（只读保留，drawers.jsonl 冻结在 6 行），按第 7 行登记"G 侧只读保留 30 天至 **2026-10-21**"——到期处置已挂 04 册 S5 遗留清单，本册确认日历真实存在。
- **新口径漂移一件**：data_source_onboarding_sop.md §12（v1.1.0，2026-09-18 增补）通篇写"冷=G:\zephyr_cold（3.7T）"——晚于 storage_map.md（INFRA-STORE-003 定案 F 冷储/G 备份）的口径被 SOP 反向固化，属文档矛盾=事故（宪法 §4.4）；且 §12 末段存量迁移令路径文本损坏（`\r` 转义事故：`\research_reports` 存为乱码字节 0xC2 0x81+`esearch_reports`，:164-166 cat -A 实证）。修册项归 07 册 O5 同批。

## 四、堵点与病灶（增量）

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| S1' | 04 册 S1 判定反转（见 §三②） | 04 册读时 manifest 仅 5 行且未及 09-21 整迁登记语境 | 撤销"修正 manifest 行"修法，改检索注；本册即改判凭证 | 0.1 天 | 是 |
| S7 | SOP §12 冷库盘符过时+路径文本损坏 | 09-21 迁移后未回扫 SOP；写入转义事故 | 与 07 册 O5 同批 safe_write_text 修正 | 0.2 天 | 是 |
| S8 | 50_archive/by_project 快速膨胀（现 6 项：altdata_p1/p2、zephyralpha、c4_exam_pdf_cache 56.6GB、final3 会话目录×2） | 会话/项目级归档无容量分层约定 | RETENTION 契约补 by_project 层 TTL/容量条款（提请，归数据审计专项） | 0.5 天 | 提请 |

## 五、提速与合并机会

（04 册 §五 两条有效不重复）增补一条：G 侧只读保留窗（至 2026-10-21）到期前，rolling_archive_reconciler 对账范围应明确"只对 F 侧"，防双库对账误报——现无配置区分。

## 六、自审闸三态

**built 确认成立，待确认点全部收敛**：建议总册 F08 状态列改 `built（已确认，2026-09-25 补挖波）`；04 册 S1 按本册 §三② 改判；S7 修册可直开；S8 提请。零新裁定需要。

## 七、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python scripts/ch/archiver.py list | grep -c "✓"                    # 2515 分区双✓
python scripts/ch/archiver.py list | tail -2                        # 最新 2026-09-24 etf_30min
wc -l F:/zephyr_cold/00_manifest/drawers.jsonl G:/zephyr_cold/00_manifest/drawers.jsonl  # 10 vs 6
sed -n '7,10p' F:/zephyr_cold/00_manifest/drawers.jsonl             # 整迁登记+三笔 09-24 迁入
sed -n '164,166p' docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md | cat -A | head -3  # §12 乱码实证
grep -n "lifecycle" docs/03_modules/_cross_layer/database/business_data_categories.yaml | head -3  # hot_90d 表驱动基础
```
