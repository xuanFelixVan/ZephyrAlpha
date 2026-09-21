---
ttl: task_bound
title: 深度审查作业簿——先报告后交易闸
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：先报告后交易闸（K08）

- 状态: **已审**
- 级别: P0｜类型: 闸门（监管红线 C-002）
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/compliance/compliance_report_registry.py:133`（ReportGate.check :144-170）；登记表 `docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml`
- 生产调用方（实测 grep）: 代码面已接线——`ex_core/order_manager.py:70,153,166,329`（submit 前置闸，`report_gate=None` 时跳过）；**但 `report_gate=` 注入全仓 src+scripts 零命中**：`start_paper_session.py:492`、`qmt_trading_session.py:110`、`qmt_file_bridge_integration.py:50`、`app_panel.py:524` 五处 OrderManager() 全部无参构造→闸在生产任何装配中均为 None=永不运行
- 登记表现状: **6 项义务 broker_ack 全部 false（0/6 确认）**
- 测试文件: tests/compliance/test_compliance_report_registry.py（7 用例全绿）
- 运行结果: `python -m pytest tests/compliance/test_compliance_report_registry.py -q` → 7 passed（Python 3.12.8）

## 1 对象快照

- **范围**：登记表加载（ComplianceReportRegistry）+ 门禁（ReportGate.check）+ 唯一消费面（OrderManager submit 前置闸）+ 登记 YAML 数据本身。
- **排除项**：C-004 合规闸其余件（清单/纪律/操纵检测）、declaration_guard（日申报笔数闸，同点注入模式）。
- **材料缺项声明**：运行时证据包未取；miniQMT 通道真实速率上限未实测（模式 #13）。
- **测试覆盖概况**：7 用例（BLOCK/PASS/Fail-Closed/缺项聚合）质量可（信任）；无"注入缺位"类测试（测试不可能覆盖装配层没做的事）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C/E | **监管红线闸生产未武装（P0）**：order_manager 的闸位是可选注入（`if self._report_gate is not None` 跳过语义，头注 INVARIANT"门禁未注入不影响既有行为"），而全仓五处 OrderManager 构造无一处注入 report_gate；登记 YAML 中 6 项义务 broker_ack 全 false → 当前生产任何一条订单路径都不做"先报告后交易"校验，0/6 已确认状态下交易可照常进行 | order_manager.py:153,166,329-340；grep "report_gate=" src/scripts 非测试=0；YAML 6×`broker_ack: false` | **P0** | `grep -rn "report_gate=" src/ scripts/ --include=*.py`（零命中）；构造 OrderManager() 后提交订单→无 C-002 校验日志 |
| D | **跨对象速率口径矛盾（模式 #1/#4）**：登记表 RPT-MAX-ORDER-RATE 内容真源自述"miniQMT 通道上限 **10 笔/秒**…内部限频 **≤15 笔/秒**见 24 号 §3.7，取通道值填报"——即向监管口径填 10 笔/秒，而 K01 清算链实际限频默认 15 笔/秒（注释还称"A 股 2026 新规 15 笔/秒"，见 rpt_k02 §3 对新规口径的证伪）。三处数字（申报 10 / 内部 15 / "新规 15"）两两不一致；若通道真限 10 笔/秒，清算分片 15 笔/秒会在熔断这一最不能出错的时刻吃到通道拒单 | compliance_report_registry.yaml（RPT-MAX-ORDER-RATE 条目+order_min_dwell_us 注释）；stop_loss.py:287,311 | **P1** | 对读 YAML 条目与 stop_loss 默认参数；实单 smoke 验证通道速率上限（模式 #13） |
| A | bool 强转假 PASS 边界：`broker_ack=bool(raw.get("broker_ack", False))`——YAML 写成带引号字符串 `broker_ack: "false"` 时 bool("false")=True → 门禁误 PASS。登记表定位为"人工/AI 编辑 YAML 回填确认位"，引号笔误是现实输入 | compliance_report_registry.py:119,117（required 同模式但方向安全） | **P2** | YAML 置 `broker_ack: "false"` 跑 check→PASS |
| A | load_items 结构异常逃逸：`raw["item_id"]` 缺键→KeyError、YAML 顶层为标量/列表→AttributeError——均非 ComplianceReportError，check() 只捕后者→异常穿透到 OrderManager.submit（无结构化 BLOCK；方向上订单仍发不出=意外 fail-closed，但报错语义脏） | compliance_report_registry.py:110,106-108,144-155 | P2 | 登记表临时改为 `- name: x`（缺 item_id）→submit 抛 KeyError 而非 ComplianceGateBlockError |
| A | 门禁主逻辑正确：不可读=BLOCK（Fail-Closed）、缺项聚合输出、决策枚举不可变、留痕走 ComplianceLogger | compliance_report_registry.py:144-170 | 已查无 | 已有测试 |
| B | 上游=YAML 登记表（git 版本化=审计 trail 好）；reported_at 仅记录不参与判定（broker_ack 单真源）——语义清晰；但 YAML 位于 docs 注册表目录，按 RULE-SSOT"规则=YAML"口径正确 | compliance_report_registry.py:50-57 | 已查无 | 读码 |
| C | 下游：ComplianceGateBlockError(ZA-EX-0011) 拒发路径结构化（ERROR 日志+异常），与 declaration_guard/操纵冻结同点位串联——设计面完整，唯独输入缺注入（C 轴 P0） | order_manager.py:322-357 | 已计 P0 | 读码 |
| E | 假阳性过关：本 P0 即终极"该拦没拦"；次级=bool 强转（P2）；静默失败=check 内 ComplianceReportError 转 BLOCK 不静默（好）；order_min_dwell_us() 的 yaml.safe_load 无 try（与 load_items 不对称），但该方法无生产调用方 | compliance_report_registry.py:124-130 | P3 | grep order_min_dwell_us 调用=0 |
| E | 重复触发/时序：check 每单实时读文件（无缓存陈旧问题——代价是每单一次文件 IO，个人低频可接受）；无状态幂等 | compliance_report_registry.py:147 | 已查无 | — |
| A.3 | 测试：7 用例覆盖三类决策+缺项聚合；未覆盖字符串真值/结构异常/注入缺位 | tests/compliance/test_compliance_report_registry.py | P3 | 补用例建议 |
| D | 模块头 `MATURITY=design` 与其承载的监管红线地位及作业簿 P0 定级不一致（stable/stability 字段亦如此）——状态标注漂移 | compliance_report_registry.py:7,10 | P3 | 读头注 |

## 3 SOTA 对照（轴 F）

- **先报告后交易（program trading registration prior to trading）**：中国证监会《证券市场程序化交易管理规定（试行）》+沪深北交易所实施细则确立程序化交易者报告制度（未报告不得开展程序化交易）——本模块登记的 6 项义务与细则报告要素同构（K02 §3 已引细则原文 URL：上交所官网 2025 实施细则；发布方=上交所/证监会，2024-2025）。**对等已有**（合规映射正确）。
- 监管闸默认应 fail-closed（gate 必须显式武装而非可选注入）：业界合规系统惯例（SOX/SEC 15c3-5 market access 的 pre-trade control 必须默认启用）——本件可选注入+默认 None 的取向与该惯例相悖，**立卡候选**（装配层默认构造 ReportGate()，或启动自检强制校验注入）。

## 4 缺陷清单（按严重级排序）

1. **[P0] C-002 先报告后交易闸生产未武装**：现状→闸代码完整+测试绿+order_manager 闸位在，但零处注入+0/6 确认位。影响→实盘/模拟通道开启即违反程序化交易报告制度（监管红线）；爆炸半径=全账户合规暴露（非资金直接损失，但属"闸门失效"类）。建议修法→①装配层（start_paper_session/qmt_trading_session）OrderManager 构造注入 `ReportGate()`；②0/6→6/6 人工报送后回填 broker_ack（含 Owner 门位）；③启动自检：report_gate=None 且 broker 有实单能力→CRITICAL 拒启。验证法→§2 C/E 轴两条 grep+注入后跑一单看 C-002 日志。
2. **[P1] 申报速率三口径矛盾（10 填报/15 内部/"新规 15"注释）**：建议统一到通道实测值（实单 smoke 定上限，模式 #13），清算限频改为 ≤min(通道,内部) 并同步三处文本。验证法→实单速率 smoke+三处 grep。
3. **[P2] 两条打包**：broker_ack 字符串真值化（改 `raw.get("broker_ack") is True` 或类型断言）；load_items 结构异常包进 ComplianceReportError。
4. **[P3] 三条打包**：order_min_dwell_us() 无调用方+异常不对称；MATURITY 标注漂移；缺三类边界测试。

## 5 挂起疑问

1. 未注入是否为模拟盘阶段的有意豁免（"模拟盘不需要监管报送"）？若是，需在装配处显式注释+实盘切换 checklist 中设卡（否则切换时静默带病上线）——需 Owner 裁定并登记。
2. RPT-MAX-ORDER-RATE 的"通道上限 10 笔/秒"出处是券商合同还是文档推断？需实测锚定（挂 K01 挂起疑问联动）。
3. 6 项义务的报送状态（是否已在券商渠道实际报送）属线下事实，系统 0/6 与线下真实进度是否一致需 Owner 确认。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；E 轴五问逐条；数学面简单（布尔门禁）已过。
- 长尾清单：① declaration_guard（日申报笔数闸）本体未审（同点注入模式，恐同样未武装——值得同法复查：grep declaration_guard= 注入）；② manipulation_realtime_monitor 冻结闸注入状态未查；③ ComplianceLogger 落盘路径与 TTL 未审。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P0 闸码完整但report_gate=全仓零注入+0/6项broker_ack=监管红线C-002未武装: 挂起登记(武装前置=券商ack数据流;盲武装=全拒单)。晨报置顶。
