---
ttl: task_bound
title: L09 案卷 F88 — LSG 安全网关（十层纵深+双捕防线；静态网在岗、运行时网四模式引导死）
session: zc-l09-20260927
updated: 2026-09-29
---

# F88 LSG 安全网关（J 段 A3，骨架态=built/P0）（标题"运行时网四模式引导死"已过时，见刷新批注——运行时网已在岗）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 全部业务 LLM 调用方（scan_input/full_scan/scan_agent_action）；rules=宪法 §9.2+RULE-LSG-001；fail_open_layers 外部化于 `config/llm_security_gateway.yaml`（#353②，gateway.py:95 出厂 {l6_observability,l7_validation}） |
| 下游消费 | openai/anthropic/litellm/langchain 四库 patch 面（runtime_interceptor.py:420-425 _PATCHERS）；违规出口=BareLLMCallError（ZA-SC-0022，:86-93） |
| 自动化触发 | 第一捕 GATE-20=pre-commit AST 门（.pre-commit-config.yaml:707 gate-20-llm-security-gateway，行号较 M4 记 681 漂移）；第二捕=解释器启动引导——**本日四模式复核仍全死**（usercustomize 不存在+meta_path finder NONE+is_installed False） |
| 真源与注册表 | gateway.py:139 LSGSecurityGateway（480 行，10 层实例化）；引导链=sitecustomize.py:57-59（仓内，Python 3.11+ python -c 下死代码）+usercustomize（仓外全局，不入版本控制） |
| 门禁与质量尺 | tests/llm_security/test_runtime_interceptor.py；kill-switch=ZEPHYR_RUNTIME_GATE=0（:81,:505+sitecustomize:47 双重尊重） |
| 当前运行状态 | **红（防线半失位，维持收口册01 判定）**：静态 GATE-20 在岗；运行时网整体不在岗；L4 HMAC 未配置降级（M4-03） |

## 二、子模块三级枚举（llm_security 包面）

1. 网关本体：`gateway.py`（10 层顺序链式 _evaluate_chain，fail-closed，层缺失/超时10s/异常→非 fail-open 层一律 DENY；grant_allowance TTL 30s 令牌，:122-136）。
2. 拦截面：`runtime_interceptor.py`（537 行；meta_path finder+monkey-patch+令牌双存储 contextvar/threading.local:106-108；allow_llm_call 逃生门:207-266）。
3. 纵深层：layers/l0_supply_chain…l8_multi_agent（L0 供应链/L1 输入/L2 提示/L2a 进程沙箱/L3 输出/L4 智能体/L5 资源/L6 可观测/L7 自保护/L8 多智能体，gateway.py:39-52 逐层 import）。
4. 配套件：input_sanitizer/adversarial_robustness/alignment_scorer/behavior_audit_logger/sensitivity_classifier/solo_dev_safety_net/poisoning_monitor/lsg_pattern_tracker+red_team_corpus.yaml+dashboard/。
5. 引导件：`sitecustomize.py`（仓根 63 行）+`scripts/setup_dev_env.py:59-77`（usercustomize 生成器）。

## 三、接线四态独立复核

- **GATE-20 静态网=已接线**：pre-commit 入口在案（本日未重放 hook，引 M3/收口册01 双源）。
- **运行时拦截器=建成未接线（本日复核维持）**：`is_installed()=False`、usercustomize `exists=False`、finder=NONE 三探针全复现 DP-1；30s 令牌/混合存储等机制全部空转。
- **patch 面=半接线**：DP-7 双网同漏（openai 2.36.0 responses.create 不在 patch 白名单也不在 GATE-20 签名）；DP-6 白名单仅四库；DP-15 LSG-import 单行豁免可绕。
- **15 条死路径清单=维持**（接续收口01 全清单 A/B/C 三级），本日无一条证据显示已修。

## 骨架勘误

1. 骨架"built（M3：拦截仅 4 库+python -c 死路径）"偏轻：收口册01 已升格为**15 条死路径+运行时网全模式不在岗（红）**——本日三探针复核维持，built 字面应读作"网关本体 built、防线 partial"。
2. 行号漂移登记：GATE-20 pre-commit 入口 681→707；其余死路径 file:line 以收口册01 为准（本日未逐条重放，抽查 DP-1/DP-2 一致）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 运行时网全模式未引导（DP-1/DP-2） | 跑 setup_dev_env 落 usercustomize+冷启动序列校验行+is_installed() 自证告警（收口册01 修法①）——**P0 级唯一修复** | **P0** |
| 2 | L4 HMAC 密钥未配置（AgentSecurityLayer 降级） | 经 secrets.py 配 ZEPHYR_LSG_L4_HMAC_SECRET（Owner） | P1 |
| 3 | responses.create 双网同漏（DP-7） | GATE-20 签名+patch 面各加一行（修法②③） | P1 |
| 4 | kill-switch 单 env 全局关闭+patch fail-open（DP-3/4） | kill-switch 加审计留痕；其余设计取舍维持 | P2 |

## 五、自审闸三态

**挖干（三探针本日复跑+15 死路径引收口册01 逐条 file:line）✅；待裁（无——修法①为配置级，施工须走流程，本车道只读未动）；零 LLM 外呼，全部证据=静态读取+解释器内省。**

## 六、复跑命令

```bash
python -c "from zephyr.security.llm_defense.llm_security.runtime_interceptor import is_installed; print(is_installed())"   # False
python -c "import site,os; print(os.path.exists(os.path.join(site.getusersitepackages(),'usercustomize.py')))"             # False
python -c "import sys; print([type(f).__name__ for f in sys.meta_path if 'LLMGuard' in type(f).__name__] or 'NONE')"        # NONE
sed -n '707p' .pre-commit-config.yaml
python -c "from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway; print(len(LSGSecurityGateway()._layers))"  # 10
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更（i 段最大翻面卷）
- `46063bade4`（09-29 F88·DP-7 双网同漏补）：GATE-20 _BARE_LLM_SIGNATURES+responses.create（含链式 suffix2 分支关键修——三段链带客户端名永不匹配，必须走两段分支）+runtime_interceptor _patch_openai 增 Responses/AsyncResponses.create 守卫——**缺口 3 翻面**；留账：F88 P0（usercustomize 落环境=机器级配置变更须走流程/Owner 窗）、DP-6 白名单扩库清单（案卷未点名扩库目标，不擅自发明范围）。
- **运行时网三探针今日复测全转绿**：is_installed()=True／usercustomize 存在（mtime 2026-09-29 07:46 落环境）／meta_path finder=[_LLMGuardFinder] 活跃——§一"本日四模式复核仍全死"与 §三"运行时拦截器=建成未接线（维持）"**已翻面**。

### 缺口清单状态修订
- 缺口 1（运行时网全模式未引导，P0 唯一修复）：**翻面**——usercustomize 已落+finder 活跃；机器级配置变更的流程追认留 Owner 窗账（46063bade4 留痕）。
- 缺口 3（DP-7 双网同漏）：**翻面**（46063bade4）。
- 缺口 2（L4 HMAC 未配置）：本刷新未复测，维持。
- 缺口 4（kill-switch 单 env+patch fail-open）：维持；DP-6 扩库留账。
- 15 死路径清单：DP-1/DP-2/DP-7 三条已闭，其余未逐条重放。

### 自审闸三态
- **挖干（维持）**；标题"运行时网四模式引导死"与 §一/§三"红（防线半失位）/运行时网整体不在岗"**已过时**——运行时网在岗（红→绿），缺口 1/3 两条翻面；§六复跑命令前 3 条期望值已反转（False→True），勿据旧期望误判回退。
