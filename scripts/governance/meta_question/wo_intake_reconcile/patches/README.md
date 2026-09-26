# WO-001/002/003 补丁包（st-metaq-gc-20260924）

> 为什么是补丁包：目标文件 `src/zephyr/governance/meta_question/registry.py`、`scripts/governance/check_meta_question_*.py`
> 均为**已在工作区、未落 HEAD** 的在队列件（实测 `git cat-file -e HEAD:<路径>` 全部失败、`git status` 全部 `??`）。
> 直接改=被后落袋覆盖或触发连坐。本包由总包在**相关袋落地之后**统一施加。
> 所有 `.patch` 已在本班用过 `git apply --check` 验证（对当前工作区字节态零冲突）。

## 施加前置（顺序不可颠倒）

1. **队列先行**：q-0004（registry/exam_ops/snapshot + 两个 check 脚本所在袋）必须已落 HEAD，
   否则 `git apply` 会因基线字节不符而失败（这正是补丁包要等的原因）。
2. **W4 册先落**：`data/registers/metaq_source_line/source_line_registry.yaml` 与本包同批提交
   （册缺失时 registry 走 fail-closed 降级，功能不炸，但 WO-001 验收不成立）。
3. **creation_token**：本批新增 7 个文件（见下"新增文件清单"）须先 `batch_creation_tokens.py`
   登记再投递（CREATE-GUARD 读主树册，登记后立即投递压窗口）。
4. **翻译册**：4 个新 .py 须 `add_module_translation.py --path <py> --domain D_GOV_SCRIPTS|D_GOVERNANCE --name-zh --plain-zh`
   （TRANSLATION-COVERAGE gate 拦）。

## 补丁清单

### 0001-wo001-registry-degraded-stub-to-real-check.patch
- **目标**：`src/zephyr/governance/meta_question/registry.py`（+349 diff 行，函数级新增，无 SQL 改动）
- **改什么**：把"五要素机检通过即无条件 `degraded.append(...)`"改为**真检**——
  要素1 查 W4 机器可读册（`line_ref` 在册 **且** 每个 `data_sources` 命中册面 token 宇宙）；
  要素5 查该册 `pit_asof_declared`（问题触及的每条线都声明了可用 as-of 时戳机制）；
  要素3 查 `functional_domain_registry` ∪ 七层枚举（该要素真源不在 W4，见 10§3 行3）。
  命中即不登记；未命中仍登记降级痕，并把 `evidence` 从常量
  `W4_source_line_registry_pending` 改为 `real_check_miss:<逐项点名>`（册不可用时保留原常量字符串）。
- **新增公共面**：`load_source_line_register(path=None)`、构造参数 `source_line_register_path`（测试注入口）。
- **施加时机**：q-0004 落 HEAD 后，与 `data/registers/metaq_source_line/` 同批。
- **风险**：
  1. **复考判据口径**：PQ-0004 复考统计 `what=degraded_check` 的**事件数**（不是 evidence 字符串）——
     evidence 文案已变，按旧字符串过滤会误判 0。
  2. 在册 `tests/governance/meta_question/test_registry.py::test_register_assigns_serial_qid_and_audits`
     的"降级痕必留"断言：**已实测不红**（其 `_valid_question` 无 `line_ref`、`data_sources=["src.quote.daily"]`
     三项真检全不成立→仍产生 degraded_check），并由本包新增测试
     `test_legacy_ungrounded_fixture_still_degrades` 锁死该回归护栏。
  3. 真检册漂移（`counts.lines` ≠ 条目数）时读侧判不可用→全要素降级（fail-closed 方向选定"降级而非放行"）。
- **验证**：`python -m pytest tests/governance/meta_question/wo_intake_reconcile/test_registry_real_check.py -q`
  （本包施加前 7 例整件 skip，施加后自动生效；本班已用"预加载打过补丁的模块"仿真跑过 **7 passed**）。

### 0002-wo003-campaign-regime-95-ratified.patch
- **目标**：`scripts/governance/check_meta_question_status_band.py`
- **改什么**：`CAMPAIGN_ANSWERED_MAX_PCT=95.0` **数值不变、语义转正**——头注释/模块 docstring/
  常量注释/`_CAMPAIGN_NOTE`/argparse help/自测用例名六处"占位、待 Owner 裁定"文案改为裁定值与出处；
  并新增 `--selftest` 红腿一例 `{"answered": 283}`（单态 100% 在 campaign 带必判红，锁死 95 帽的牙齿）。
- **施加时机**：q-0007 落 HEAD 后。与 Owner 六裁定之六的 `ruling_registry` 登记**同批**（见下"非 diff 登记件 B"）。
- **风险**：`--selftest` 用例数 9→10，若有外部台账记死"9/9"需同步（02_final_ledger 心跳行有"红蓝边界自测 9/9"字样，
  属历史事实记录，不改；新记录写 10/10）。
- **验证**：`python scripts/governance/check_meta_question_status_band.py --selftest` → `SELFTEST: 10/10 通过`。

### 0003-schedule-metaq-audit-reconcile-daily-task.patch
- **目标**：**新建** `scripts/register_metaq_audit_reconcile_task.ps1`（83 行，纯 ASCII 已通过字节校验）
- **改什么**：对账器进排班。载体=Windows 计划任务 `ZephyrAlpha_MetaqAuditReconcile`，每日 03:50 跑
  `pythonw scripts/governance/check_meta_question_audit_reconcile.py --days 1`，stdout/stderr 落
  `tmp/metaq_audit_reconcile_report.log`（`run_fulltree_gate_audit.py` 的 tmp/ 报告先例）。
- **为什么落 `scripts/` 根**：排班真源四源之一是 `scripts/register_*.ps1`，
  `generate_resource_profile_registry.py` 按该 glob 收编入 `config/resource_profile_registry.yaml`
  （GENERATED 册禁手改）——放子目录=生成器看不见=幽灵任务。
- **施加时机**：q-0006 落 HEAD 后（任务依赖对账脚本本体存在）。落盘后须人跑一次注册命令才算真排班：
  `powershell -ExecutionPolicy Bypass -File scripts\register_metaq_audit_reconcile_task.ps1`
  （RULE-GUARDIAN：计划任务注册属写操作，须在 reaper 计划任务存活前提下执行）。
- **风险**：03:50 与 GateFullTreeAudit 03:30/生成器 04:00 档共窗——本任务是秒级只读，互斥组无冲突；
  若排班闸报冲突，改 `03:55` 即可（同文件一行）。
- **验证**：`schtasks /query /tn ZephyrAlpha_MetaqAuditReconcile /v /fo LIST` +
  `python scripts/governance/generators/generate_resource_profile_registry.py --check`（新实体应被自动收编）。

### 0004-wo002-daily-reconcile-window-in-policy-table.patch
- **目标**：`docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md` §4 频率表行6 + 判据段
- **改什么**：账本双轨对账节奏由"季度窗"改为"**每日增量窗（排班件）＋季度窗全量清零**"，
  并记收紧理由与载体选择（消除 0003 与政策册的文档矛盾；判据本身按日定义）。
- **施加时机**：与 0003 **同批**（排班落地即政策落地，禁一先一后造成自相矛盾窗口期）。
- **风险**：政策文档变更，涉本战役外的消费方（04_construction_map 台账引用频率）——纯加严不放松，无下游破坏面。

## 非 diff 登记件（热册/保护路径，按"整条目+施加位置"交付）

### A. ROOR 收录（`docs/registry_of_registries.yaml`，tier 与 REG-METAQ-001 同层，紧随其后插入）

```yaml
      - registry_id: REG-METAQ-002   # 号若被占，按登记时册内最大号顺延
        name: W4 源线谱机器可读册（meta_question 入库闸命中真源）
        physical_path: data/registers/metaq_source_line/source_line_registry.yaml
        format: yaml（真源=docs/_working/chain_piling_campaign/02_source_line_registry.md 人读册；本册机生禁手改）
        maintenance: auto （scripts/governance/meta_question/wo_intake_reconcile/generate_source_line_register.py 机生）
        entry_count: 0   # 由生成器 counts.lines 字段提供，勿手写
        counting_rule: 册头部 counts.lines 字段（与 §1 三档总表条目数经生成器对账）
        status: active
        description: 入库闸五要素机检要素1/要素5 的命中真源（10_intake_gate_design.md §3），同时是《模板生成器设计》
          11§2 TPL-U-001 取值域 domain_ref=source_line_registry（line/signal_vocab 槽）的机器可读面。净零：本册=02 号件 md
          的派生视图，非第二张真源（md §6.3 早已把"YAML 化"列为 W2/W6 施工件，禁另建重复注册表条款已遵守）。
        owned_by: governance
```

### B. Owner 六裁定之六登记（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`，追加到 entries 末尾）

```yaml
- ruling_id: 裁定#<下一空号>
  title: 'meta_question campaign regime answered 上限裁 95（283 问战役施工批六裁定之六，WO-003 监控器占位转正）'
  date: '2026-09-24'
  category: governance
  status: active
  summary: >-
    PQ-0099 工作簿 §4 二选一取 (b) 双 regime 双带（不取 (a) 豁免窗：机制不留免检窗，只留更宽但仍有牙的带）。
    campaign 带 answered 上限=95%（default 70% 不变），单状态 ≤80% 帽与下限 30% 双带共用不放宽；
    100% 单态例已入 --selftest 红腿。回常态带的前置=持续入题机制（WO-003② intake_batch）上线使状态分布多态并存后另登裁定。
  related_files:
    - scripts/governance/check_meta_question_status_band.py
    - tests/governance/meta_question/wo_intake_reconcile/test_registry_real_check.py
    - docs/_working/meta_question_answers/build/WO-001-003.yaml
```

> 注意（前车之鉴）：号未登记前，任何文件里写 `裁定#<数字>` 裸引用会自触 REFERENCE-INTEGRITY  gate。
> 本包与案卷一律用"Owner 2026-09-24 战役施工批六裁定之六"文字指称，登记号落定后再由总包补锚。

## 新增文件清单（本包之外，直接可投递）

| 文件 | 用途 | 登记义务 |
|------|------|---------|
| `scripts/governance/meta_question/wo_intake_reconcile/generate_source_line_register.py` | W4 md→机器可读册生成器+七项自校验 | token+翻译册 |
| `scripts/governance/meta_question/wo_intake_reconcile/replay_audit_to_jsonl.py` | PG→JSONL 回放补账臂（20§2.2 pg_only 处置） | token+翻译册 |
| `scripts/governance/meta_question/wo_intake_reconcile/intake_batch.py` | 持续入题驱动器（10§5.1 限流/§7 正门） | token+翻译册 |
| `data/registers/metaq_source_line/source_line_registry.yaml` | W4 机器可读册（机生件） | token+ROOR 收录（上件 A） |
| `tests/governance/meta_question/wo_intake_reconcile/`（4 个测试文件） | 39 passed/7 skip（仿真态 46 全绿） | tests/ 豁免 CREATE-GUARD |

## 施加后一次性动作（不属补丁，属运维）

```bash
# 双轨缺行补账（实测缺 283 行，全在 2026-09-24 的"Phase0 分诊认领"直连 SQL 批）
python scripts/governance/meta_question/wo_intake_reconcile/replay_audit_to_jsonl.py            # dry-run 先看数
python scripts/governance/meta_question/wo_intake_reconcile/replay_audit_to_jsonl.py --apply    # 追加（幂等，只增不改）
python scripts/governance/check_meta_question_audit_reconcile.py                      # 必 exit 0
```

本班**未**对生产追加账执行 `--apply`：已用生产账副本全量验证补账后逐日差归零、字节与原行逐字一致
（红腿删 2 行→补回字节相同；蓝腿幂等重跑零追加），落库动作留给总包与 0003 排班同窗执行。
