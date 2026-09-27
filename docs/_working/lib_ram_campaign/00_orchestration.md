---
ttl: task_bound
title: 图书馆"放入内存条"专项·骨架与波次（承 FMS 战役后续工作 #6）
created: 2026-09-27
sid: st-fms-tc-20260927
---

# 00 骨架（本册=环节地图与波次真源；规格细则在 §九 定版原文与各簿）

**使命**：把图书馆从"每查询现开 PG 连接 + SQL 即关"改为**有界**内存常驻 + 本地快照回落，
Owner 定版红线=**无界缓存禁止**（`docs/_working/fms_overhaul/99_delivery_report.md` §九）。

## 一、环节地图（七簿=挖矿面；四批=施工面）

| 簿 | 环节 | 落点 | 自审三态（挖矿代理交回，总筹复核） |
|---|---|---|---|
| S1 | 账本世代指纹机制 | `S1_version_stamp/README.md` | 挖干（指纹=max(event_id) 3.45ms 优于 max(built_at) 15.9ms；SQL 须做共享常量） |
| S2 | Librarian 世代缓存层 | `S2_librarian_cache/README.md` | 未干（G3 消费面进程驻留性普查缺） |
| S3 | 本地快照层 | `S3_snapshot_layer/README.md` | 未干（G1 格式 bench 未跑） |
| S4 | 门禁消费面 | `S4_gate_consumers/README.md` | 未干（探针频次未定量、`check_capability_duplicates` 未逐行） |
| S5 | 常驻服务可行性 | `S5_resident_service/README.md` | 未干（api_server 端口/HTTP 往返未测） |
| S6 | 与 st-p1b 协调面 | `S6_coordination/README.md` | 未干（对方会话是否活跃未取证） |
| S7 | 红蓝验收设计 | `S7_redblue_acceptance/README.md` | 未干（B3 基线阻塞未解） |

| 批 | 内容 | 本班态 |
|---|---|---|
| R1 | 世代缓存层（≤2 代常量封死 + single-flight + 原子切换） | 施工中（并发代理） |
| R2 | 本地快照层（`data/library_snapshots/`，留 2 份，崩溃安全 7 步序，版本列必备） | 施工中（并发代理） |
| R3 | 常驻查询服务（--max-memory-mb 512 硬顶 + reaper 水位） | **不做**，理由见 §三 |
| R4（新增建议） | `lookup.py:35` 重 import 链惰性化 | 未排，收益 >R1 二十倍，见 §三 |

## 二、五支柱映射（本专项不脱离 FMS 战役公理）

- 单写者：指纹 SQL 一处共享常量，禁分头复制；
- 生成闭环：快照刷新挂既有事件链（备份成功链/生成链尾步），禁新增计划任务（根宪法 §9.3）；
- 棘轮：快照/缓存不参与违规计数，但读侧降级必须显式标记（禁"回落当健康"）；
- 生命周期隔离：快照家=`data/library_snapshots/`（中性区），禁落 `.runtime`（24h TTL）与 G/F（USB）；
- 墓碑去向：R2 快照必须带版本列，防"旧行覆盖修正行"同型事故复发。

## 三、判据修正呈报（总筹，2026-09-27 10:3x，Owner 睡眠窗内不自改）

Owner §九 第三层触发判据=「②之后 **CLI 延迟仍 >10ms** 才做常驻服务」。两路挖矿代理独立实测同一结论 [亲验]：

| 实测项 | 读数 |
|---|---:|
| `python -c pass` 裸解释器启动 | 26–30 ms |
| CLI `python -m zephyr.library.lookup` 中位总耗时 | 2570 ms（5 次 2453–2835） |
| 其中 import 链 | ≈2550 ms（1356 模块；`lookup.py:35` 拉入 gate_engine 479ms/admission_controller 302ms 等与查询无关件） |
| 其中 PG 取连接 + 单条 SQL | 45–55 ms + 6–9 ms |
| 其中 `lookup_assets` 端到端 | ≈110 ms |

**结论：判据按字面不可满足且方向相反。** 任何"每次查询起一个进程"的形态物理下限就是 26–30 ms，
永远 >10 ms → 字面执行必然触发常驻服务；而 PG 侧只占 CLI 总耗时 ≈4%，世代缓存对 CLI 的收益上限就是 4%。
两条失败模式都是返工：(a) 把治理域真源缓存挂进 api_server（D_FRONTEND，付域越界+写端点授权扩面）只省 4%；
(b) 用 CLI 墙钟验收，测出"几乎没变快"而误判 S2/S3 设计失败。

**总筹处置**：
- 只施工 R1+R2（对"同进程多次查账/常驻消费方"是真收益，均不新增进程、不碰生产流转）；
- **R3 不做**：新增常驻面与 reaper 天生冲突（实测 `process_reaper.py:176-177` `age>6h 且 CPU<0.5%` 即杀），
  且新增生产进程属根宪法 §5 生产流转门位，Owner 睡眠窗内不自裁；
- 请 Owner 醒后二选一：①判据改写为"常驻/进程内客户端单次查询 P50<10ms，CLI 形态另立 <3s 口径"；
  ②维持原判据但接受字面恒触发常驻层，并另批 reaper 豁免设计；
- 更高 ROI 建议：`lookup.py:35` 重 import 链惰性化可省 ≈2.5s（世代缓存的 20 倍以上），列为 R4 优先于 R3；
  本班不与 R1 同时改 `lookup.py`，避免双写手撞车。

## 四、波次与验收

- 施工并发 ≤2 路（R1/R2 文件所有权互斥：R1=`librarian.py`/世代模块，R2=`snapshot_store.py`）；
- 验收=新测试全绿 + `tests/library` 回归绿 + 门禁消费面套（`tests/gov_enforcement/read_side`、
  `tests/governance/generators/test_regen_clean_check.py`）仍绿；红蓝按 S7 簿 5 红 3 蓝落码；
- 连续两轮问题=0 才算过；一切提交经 `scripts/git_commit.py --session st-fms-tc-20260927`。
