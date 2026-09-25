---
ttl: task_bound
---

# M3 分册 04 · 门禁 vs 运行时覆盖真空

> 挖掘 2026-09-25 ｜ 车道 M3 ｜ 只读挖矿，零 commit。
> 方法：对每个危险面问两遍——pre-commit 门拦不拦？进程运行时拦不拦？只登记"单侧覆盖"面。

## 一、环节定义与边界

一句话：pre-commit 静态门禁体系（真源=commit_speedup C1 卷宗，本册只引用）与运行时拦截器族
（本战役 01 分册）之间的双向真空清单——"只有门没有运行时"与"只有运行时没有门"。

## 二、六向台账

| 向 | 内容 |
|---|---|
| 上游输入 | C1 卷宗 102 现役门清单 + 01 分册护栏族 + 02 分册 reconciler 兜底面 |
| 下游消费 | Owner 裁定清单（pending_rulings 口径）、施工批次排期 |
| 自动化触发 | 无（本册为分析结论） |
| 真源与注册表 | 本册；被引证据 file:line 均在 01/02/03 分册 |
| 门禁与质量尺 | 纵深防御原则：钱/密钥/删除面要求双侧覆盖 |
| 当前运行状态 | 黄（真空 top3 如下，均为结构性而非配置性） |

## 三、真空矩阵（危险面 × 双侧覆盖）

| 危险面 | pre-commit 门 | 运行时拦 | 判定 |
|---|---|---|---|
| 裸调 LLM（四大库 openai/anthropic/litellm/langchain） | GATE-20 AST | runtime_interceptor monkeypatch | **双侧**（范例面） |
| 裸调 LLM（其他 SDK/裸 HTTP） | GATE-20（AST 可见 import 时可拦） | **无**（httpx/requests/urllib 直连端点、google-genai/cohere/mistral/zhipu/dashscope 均不在 _PATCHERS） | **真空** |
| 危险删除（声明制进程内） | 删除域 gate | ops_guard in-process 补丁——**仅 5 入口安装** | **半真空**（入口外进程裸奔） |
| git 危险命令 | GIT-DANGEROUS 门 | git_guard alias——alias 未装即无拦，事后只有 git_guard_bypass_reconciler **检测**（reflog 对账，L2.3） | **半真空**（防在前、检测在后，中间态裸奔） |
| plumbing 绕过 | POST-COMMIT-GUARD 防伪 + GW 标记 forged 判定 | 无进程级拦（emergency_commit 是合法通道自带五护栏） | 双侧（含审计补偿） |
| 裸 duckdb / 裸 SQL | bare_sql_gate（C1 卷宗在册） | **无运行时拦**（无 duckdb.connect patch/审计钩子；实测 src 内 offline_store.py:329 直连 ：memory: 存活） | **真空**（宪法 §9.1 明令红线却只有单侧门） |
| 裸 getenv / 硬编码密钥 | NO-BARE-GETENV/NO-SECRET-HARDCODE 等 6 门（C1"不建议删"密钥面） | **无运行时拦**（os.environ 读无 patch；secret_registry_drift reconciler 只对账 registry↔.env↔era 三方漂移，post-commit warn） | **半真空**（门+事后对账，无进程内拦截） |
| KillSwitch 风控 | — | 进程内存单例，崩溃归零、不跨进程 | **单侧且弱**（01 分册 B2） |
| 会话 claim/锁 | WORKTREE-REQUIRED/CLAIM-REQUIRED 门（并发毁伤面，C1 有效拦截榜） | SessionRegistry/lock_files 运行时 claim + TTL/stale/salvage | 双侧（范例面） |
| reconciler 删除能力 | — | file_ops 声明制 + DeleteBlockedError→critical_warn（T1①） | 运行时侧独立成体系（门侧无对应，属"只有运行时"） |
| 排班/能力/翻译漂移 | 各对应 gate（warn→阻断前移的 3 台已升级） | reconciler 存量对账（gate 防蔓延+reconciler 清存量互补模式） | 双侧互补（范例模式：blueprint_id_legacy 注释原话"gate 防蔓延，reconciler 清存量"） |

## 四、覆盖真空 Top3（按资金/数据风险排序）

### T1 裸 duckdb 无运行时拦截（数据面）
- 现状：宪法 §9.1 "禁裸 duckdb——一律 DatabaseService" 是运维红线；pre-commit 有 bare_sql_gate；
  运行时**零拦截零审计**（无 import 钩子无 connect patch）。实测 `src/zephyr/factor/offline_store.py:329`
  `duckdb.connect(":memory:")` 存活（内存态或属豁免灰区，但无登记通道佐证）。
- 修法草案：对齐 runtime_interceptor 模式做 duckdb.connect monkeypatch（DatabaseService 白名单放行令牌），
  或最低配：ops_guard 式审计-only in-process 钩子入 5 个既有安装点。工作量 M。
- 是否本车道可修：是（模式有范例，runtime_interceptor 全套可平移）。

### T2 删除原语 in-process 补丁仅 5 入口安装（删除面）
- 现状：ops_guard 补丁只在 reconcile_worker/session_worktree×2/commit_queue/git_commit 安装；
  任何其他入口（dashboard、data 管线、临时脚本）内 `os.remove`/`shutil.rmtree` 打 src/ 或注册表
  **运行时无感**，只剩 analyze_delete_command 的命令文本分析面（且该面靠外层 harness 调用）。
- 修法草案：usercustomize（B1 同载体）安装 audit-only 版全局补丁；生产 enforce 版仍限 5 入口。
  工作量 S-M。本车道可修。

### T3 LLM 裸调运行时面只覆盖 4 库（LLM 面）
- 现状：_PATCHERS 仅 openai/anthropic/litellm/langchain（runtime_interceptor.py:420-425）；
  裸 HTTP 客户端直连 LLM 端点完全在拦截面外；且 `python -c` 场景拦截器根本不安装（sitecustomize 死路径，
  usercustomize 仓外手工）。GATE-20 静态门对"运行时从外部取代码再 exec"自认不可见（模块 docstring 原话）。
- 修法草案：① _PATCHERS 增补项目实际在用的其余 SDK（先查依赖清单再定）；② LSG 网关层把
  outbound LLM 域名走 outbound_data_sanitizer 出口净面（已有模块，未与 LSG 挂链——待查证后立项）；
  ③ usercustomize 安装入 setup_dev_env 固化。工作量 M。部分本车道可修（②挂链属 M4 车道）。

## 五、其他登记（非 top3 但在案）
1. env 单因子信任面：FORCE_DELETE/SERIALIZER_MODE/FAST_PATH 三个授权 env 均无身份绑定（01 分册 B5）——
   已有 git_guard_bypass_reconciler 事后对账兜底一半。
2. KillSwitch 持久化缺失（B2）——待裁。
3. reconciler 家族对"运行时 DB 写入"类漂移的触发改良已开始（GATE-DOMAIN-DOC trigger 改造，:5791），
   但同类"DB 写入不产生 commit"的面还有多少未普查——待 M1/M8 车道交叉。

## 六、自审闸三态
**挖干可施工**（T1/T2 有平移范例+file:line 实证；T3② 挂链属 M4 待协调；KillSwitch/env 信任两项待裁）。

## 七、复核命令
```bash
grep -n "_PATCHERS" src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py | head -2   # 4 库清单
grep -rn "install_inprocess_enforcement" src/ scripts/ --include="*.py" | grep -v def | grep -v test | wc -l   # 5 入口
grep -rn "duckdb.connect" src/zephyr --include="*.py" | head        # 直连点存活证明
sed -n '17,30p' sitecustomize.py                                    # python -c 死路径自认
```
