---
ttl: task_bound
---

# NotImplementedError 分类处置归档（STR-02 / 92号清单 §5.6）

- 日期：2026-08-22
- 工单：STR-02（92号清单 §5.6）
- 范围：`src/zephyr/` 全仓 `raise NotImplementedError` 实证 29 处 / 19 文件（复核口径：含 3 处 docstring 历史注记——详见族 A2）
- 处置原则：本单为分析+登记，src 零代码改动；CAND 条目经 `.runtime/p2_fragments/str02.md` 片段提交统筹集中写入注册表
- 治理依据：`trae_007_anti_hallucination_behavior.yaml`——禁止占位符，`@abstractmethod` 豁免是唯一合法场景；`onboarding_detail.md` §豁免：抽象基类 `@abstractmethod` + `raise NotImplementedError` 声明接口契约属合法

## 一、分类汇总统计

| 分类 | 处数 | 文件数 | 动作 |
|------|---:|---:|------|
| 合法免责（ABC 基类契约/可选覆盖钩子，行业标准模板方法范式） | 13 | 10 | 零动作 |
| deferred（security/access_control stub 族，单人单信任域无 RBAC 需求） | 13 | 6 | 族级 CAND 登记 2 条（CAND-SEC-002/003 草案见片段） |
| 历史注记（docstring 记述已治本 stub，非活 raise） | 3 | 3 | 零动作 |
| CAND（新增功能桩） | 0 | 0 | security 族已并入 deferred，无其余真功能桩 |
| design_maturity 漂移登记 | — | 6 | 仅登记本报告 §四，不改文件 |
| **合计** | **29** | **19** | |

## 二、族 A：security/access_control（16 处 / 9 文件）

### A1. 活 stub raise → deferred（13 处 / 6 文件）

6 个文件均为同一自动生成范式：文件头 `[MATURITY] production`，docstring `Stub module: ... — implementation pending.`，函数体 `def xxx(*args, **kwargs): raise NotImplementedError("... not implemented")`；`[CONSUMERS] N/A (all consumers verified as phantom)`；蓝图 `agent_role_based_access_control/blueprint.md` 模块表自标 `stub (pending ARCH-036)`。92号清单口径：单人单信任域无 RBAC 需求，触发条件=多账户/多用户上线，故族级 deferred 登记而非施工。

| # | 文件:行 | 上下文摘要 | 分类 | 理由 |
|---|---------|-----------|------|------|
| 1 | compliance_matrix.py:38 | `compliant_items(*args, **kwargs)` stub 函数 | deferred | MOD-INF-018 合规矩阵查询桩，无消费者，多账户/多用户上线前无需求 |
| 2 | compliance_matrix.py:43 | `get_by_reg_id(*args, **kwargs)` stub 函数 | deferred | 同上 |
| 3 | compliance_matrix.py:48 | `non_compliant_items(*args, **kwargs)` stub 函数 | deferred | 同上 |
| 4 | defense_depth.py:38 | `all_enabled(*args, **kwargs)` stub 函数 | deferred | MOD-INF-018 纵深防御层查询桩，无消费者 |
| 5 | defense_depth.py:43 | `get_layer(*args, **kwargs)` stub 函数 | deferred | 同上 |
| 6 | defense_depth.py:48 | `get_layer_by_level(*args, **kwargs)` stub 函数 | deferred | 同上 |
| 7 | guards/anti_pattern_guard.py:22 | `benchmark_before_optimize` stub 函数 | deferred | MOD-INF-018 反模式守卫桩（先 benchmark 后优化），无消费者 |
| 8 | guards/anti_pattern_guard.py:27 | `check_lock_before_write` stub 函数 | deferred | 同上（写前查锁） |
| 9 | guards/anti_pattern_guard.py:32 | `scan_silent_ignore` stub 函数 | deferred | 同上（扫描静默忽略） |
| 10 | environment_manager.py:38 | `get_env(*args, **kwargs)` stub 函数 | deferred | MOD-INF-018 环境管理桩，无消费者 |
| 11 | environment_manager.py:43 | `switch_env(*args, **kwargs)` stub 函数 | deferred | 同上 |
| 12 | session_lifecycle.py:44 | `get_state_def(*args, **kwargs)` stub 函数 | deferred | MOD-INF-018 会话生命周期桩，无消费者 |
| 13 | secrets_lifecycle.py:34 | `auto_clean_build(*args, **kwargs)` stub 函数 | deferred | MOD-INF-018 密钥生命周期桩，无消费者 |

### A2. docstring 历史注记 → 零动作（3 处 / 3 文件）

三处 `NotImplementedError` 字符串仅出现在模块 docstring 的"治本（2026-07-18）"记述中（"原模块为 stub（... raise NotImplementedError）"），**非活代码**；三模块均已按测试契约实现完整逻辑且有消费者与不变量声明。

| # | 文件:行 | 上下文摘要 | 分类 | 理由 |
|---|---------|-----------|------|------|
| 14 | a2a_check.py:19 | docstring 记述历史 stub；`verify_a2a_pair` 已实现五条契约规则 | 历史注记 | 2026-07-18 已治本，活代码零 raise，零动作 |
| 15 | capability_check.py:19 | docstring 记述历史 stub；`verify_capability_scope` 已实现四条优先级规则 | 历史注记 | 同上 |
| 16 | approver_check.py:19 | docstring 记述历史 stub；`verify_approver` 已实现三条规则 | 历史注记 | 同上 |

## 三、族 B：其余 13 处 / 10 文件 → 全部合法免责

均为抽象基类/接口契约的模板方法或可选覆盖钩子：子类必须（或可选）实现，基类 raise 是行业标准范式，符合 `trae_007` 豁免精神（部分未逐字挂 `@abstractmethod`，但类为 `abc.ABC` 或文档明示"子类实现/可选覆盖"，与工单给出的 connectors/base.py、protocols.py、trainer_base.py 范例同款）。

| # | 文件:行 | 上下文摘要 | 分类 | 理由 |
|---|---------|-----------|------|------|
| 17 | infrastructure/auto_fix_engine/models.py:202 | `BaseFixer.scan()` 修复器基类契约（pydantic BaseModel） | 合法免责 | 子类实现扫描逻辑，基类 raise 声明契约；MOD-INF-031 production 有测试 |
| 18 | infrastructure/auto_fix_engine/models.py:205 | `BaseFixer.fix(target, dry_run)` | 合法免责 | 同上 |
| 19 | infrastructure/auto_fix_engine/models.py:208 | `BaseFixer.validate(target)` | 合法免责 | 同上 |
| 20 | infrastructure/auto_fix_engine/models.py:211 | `BaseFixer.rollback(target)` | 合法免责 | 同上 |
| 21 | risk/risk_manager.py:97 | `RiskManagerBase.snapshot()`（abc.ABC 可覆盖钩子） | 合法免责 | 消息明示"需要子类实现——风控度量基础设施就绪后方可激活"，属设计的可选扩展点，非偷懒桩 |
| 22 | market_data/connectors/base.py:390 | `MarketDataConnector.fetch_daily_kline()` | 合法免责 | 模板方法：先做 CONNECTED 状态校验再 raise"子类必须实现"；docstring 及蓝图明示子类实现点 |
| 23 | ml_train/trainer_base.py:71 | `ModelTrainerBase.save_model()`（abc.ABC 可选覆盖） | 合法免责 | 工单范例同款；train/validate 已挂 @abstractmethod，save_model 为可选钩子 |
| 24 | ml_train/inference_base.py:54 | `InferenceEngineBase.batch_predict()`（abc.ABC 可选覆盖） | 合法免责 | 同上；predict 已挂 @abstractmethod |
| 25 | regime/validation/phase2/confidence_calibrator.py:173 | `Calibrator.from_dict()` 类方法（ABC 可选序列化钩子） | 合法免责 | fit/transform 已挂 @abstractmethod；from_dict 为可选持久化钩子，消息指明子类名。文件头 MATURITY=design，无漂移 |
| 26 | reporting/analytics_base.py:75 | `TCAEngineBase.analyze_batch()`（abc.ABC 可选覆盖） | 合法免责 | analyze 已挂 @abstractmethod，批量为可选优化钩子 |
| 27 | position/core/strategy_book.py:725 | `StrategyBook.select_stocks()` 模板方法 | 合法免责 | 30_multi_strategy_concurrency.md §评估表已明示"select_stocks 为子类抽象接口（NotImplementedError 属模板方法正常设计，非骨架）" |
| 28 | shared/contracts/protocols.py:169 | `IntegrityVerifier.verify_chain()` 共享契约钩子 | 合法免责 | 工单范例同款；MOD-INF-016 契约层（stability=frozen），结构接口由实现方填充 |
| 29 | shared/lifecycle/state_machine.py:133 | `TransitionGuard.check()` 泛型守卫基类 | 合法免责 | MOD-INF-038 统一状态机基类，守卫逻辑须由各领域子类定义；同族 SideEffect 钩子用 pass 属可选语义，check 必须子类给出故 raise |

## 四、design_maturity 漂移登记（仅登记，不改文件）

1. **6 个 access_control stub 文件头标 `[MATURITY] production`**（compliance_matrix / defense_depth / environment_manager / session_lifecycle / secrets_lifecycle / guards/anti_pattern_guard），与自身 docstring `Stub module — implementation pending` 及蓝图模块表 `stub (pending ARCH-036)` 口径矛盾。按实证成熟度应标 design（或 skeleton）。本单纪律不改 src 文件头，登记待统筹裁定：是随 CAND-SEC-002/003 deferred 条目一并把文件头 maturity 降为 design，还是维持现状以"族级 deferred"口径覆盖。
2. **蓝图 §1.1 autogen 索引表自相矛盾**：`agent_role_based_access_control/blueprint.md` §1.1（sync_blueprint_code_index.py 从 depgraph.nodes `build_status=generated` 派生）将上述 6 个 stub 文件标 `✅ 已实现`，而同蓝图模块表标 `stub (pending ARCH-036)`。根因疑似 depgraph 节点 build_status 与磁盘实证不一致，登记待 ARCH-036 或 depgraph 运营态修正时联动处理。
3. confidence_calibrator.py 文件头 `[MATURITY] design` 与实现完整度（Stage 1/2 主流程已实现并有测试）相比偏保守，但无自相矛盾，不登记为漂移、不动。

## 五、CAND 登记指引

- 片段路径：`.runtime/p2_fragments/str02.md`（统筹集中写入 `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`）
- 拟登记 2 条 deferred：
  - **CAND-SEC-002** access_control 合规矩阵与纵深防御查询族（compliance_matrix 3 处 + defense_depth 3 处）
  - **CAND-SEC-003** access_control 运行时桩族（environment_manager 2 + session_lifecycle 1 + secrets_lifecycle 1 + anti_pattern_guard 3）
- 号段避让：已 grep 注册表，现存仅 CAND-SEC-001，002/003 无冲突
- 触发条件（两条同一口径）：多账户/多用户上线（92号清单 §5.6）；反模式守卫另挂安全治理扫描基建需求
