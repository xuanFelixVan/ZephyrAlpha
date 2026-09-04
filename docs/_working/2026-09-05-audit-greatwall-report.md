---
ttl: task_bound
---

> **任务**：ZephyrAlpha 全项目审计治本长城任务 · 总控执行（AI-00）
> **签发**：Owner 与总控强模型联合签发，2026-09-05；Owner 离线（约 8h），全程自主裁定授权
> **基本法**：d:\ZephyrAlpha\docs\audit_prompts_20_ai.md（6135 行，受保护只读）+ 本指令无人值守增强层
> **状态**：进行中。本文件为进度唯一真源，上下文被压缩后以本文件恢复状态。

---

# 一、执行摘要

- 模式裁定：**MODE-B 直接全自动闭环**（探测：无活跃在途 session（heartbeat≥5d）+ 主仓 29 孤儿文件裁定基线收编后干净）
- 波次：6 批（4+4+4+4+4+1）修复波，MODE-B 无只审波
- 进度：波次 1（AI-01~04）已回收，四域均"通过"（各连续 2 轮零问题），总控抽验 8/8 相符
- 总问题数 / 已修复数：波次 1 合计发现 31 项 → 修复 26 项（另 5 项跨域移交/待 Owner），作废重派 0

# 二、每域详细汇报 ×21

（每域小节：域编号 / 责任区 / 轮次记录 / 问题清单 / 修复内容+commit hash / 自主裁定+依据 / 避让项 / 遗留项 / 复检结论 / 总控抽验结果）

## AI-01 根目录文件域
- worktree：D:\ZephyrAlpha\.worktrees\AI-AUDIT01-001（分支 ai/AI-AUDIT01-001/task-audit01-autofix）；commit a467a16552
- 轮次：R1 发现 9（P1×4/P2×5）→修复 9→复检 2（并行编辑竞态自伤）→修复 3→R2 全量复检 0。连续 2 轮零问题。
- 修复：①echo-guard.yml 单反斜杠非法转义致 YAML 断裂+acknowledge/prune 白名单机制整体失效（84 行机械修复，68 条目复活、0 死链）②requirements.txt 镜像漂移补 scikit-learn/tzdata（26/26 对齐）③.gitignore 补 config/.env.* 通配（check-ignore 4 路径实测）④.dockerignore 同口收口⑤SECRETS.md 手写计数第二真源删除+补 2 服务行⑥.env.example 补 2 行（62/62 零漂移）⑦pre-commit gate-bp-place description 失真修正⑧GATE-C2 死注释清除（67 hooks 无重 id）⑨README 08_knowledge 表述修正。验证：pytest tests/clone_guard 370 passed。
- 自主裁定：转义修语义非改格式；删计数非回填；通配替代枚举；[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] 挂靠（issue 已登记）；僵尸提交锁走 ZEPHYR_FORCE_DELETE=1 授权通道。
- 共享收口上交：①gateway worktree 锁释放被 ops_guard 结构性阻断（.worktrees 保护区 vs .ailocks 锁；except OSError 接不住 DeleteBlockedError）②主仓 7 派生脏文件③依赖镜像无门禁（备案）④echo-guard 配置解析失败建议升告警。
- 遗留 0；总控抽验：a467a16552 stat/echo-guard 双解析/check-ignore 实测——**相符**。

## AI-02 配置+架构元域
- worktree：D:\ZephyrAlpha\.worktrees\AI-AUDIT02-001；commit 7cc8e4c238
- 轮次：R1 发现 4→修复 4→复检 3 处 IDE 脏缓冲区回写冲掉+noqa 残留 1→二次补修→R2 全量复检 0（214 文件全量）。
- 修复：①governance.yml phase_manager import 旧路径 ImportError→改 ops_governance（修复后 58 checks 跑通）②noqa_exempt_registry 行号漂移×2（1081/220，UNREGISTERED 2→0）③project_rules.md 资产数字漂移回填（模块 7106/脚本 755/门禁 86/模板 11/MCP 12，实测命令留痕）+蓝图幽灵入口改指物理蓝图④onboarding_detail.md 同源数字+死链标注。message 含 [ARCH-APPROVAL:#ARCH-DOCDRIFT-001]。
- 自主裁定：EX/XS 内部"重号"判格式族误报（Owner 豁免在案不越权）；tool_contracts 契约层码判非登记范围（六断言 6 passed）；ZA-KB-0003/0004 deprecated 合规；gateway 锁误拦不做域内代码修复。
- 共享收口上交：S1（高危）registry_consistency_contract REG-001/REG-002 幽灵路径（check_registry_consistency.py 实测 FileNotFoundError，CI Tier2 必红；REG-002 蓝图登记真源收编**待 Owner 裁定**）；S2 vocab WARN 16 条（src 8+scripts 8，跨域移交）；S3 src 三处"待登记"死注释（qnn_two_stage/patchtst_density_encoder/core_satellite_allocator，实际码已登记）；S4 regime_detector 5 异常类+chip_distribution_engine 头注声明 error_code 但实现缺失；S6 gateway 锁缺陷（与 AI-01/03/04 同型）。
- 遗留：worktree 内 .ailocks 残锁 1（TTL 自愈，非入仓文件）；总控抽验：governance.yml import 行/noqa 1081 实测——**相符**。

## AI-03 运行时+临时+日志+产物域
- worktree：D:\ZephyrAlpha\.worktrees\AI-03（分支 ai/AI-03/task-audit03-autofix）；commits 2c0e8d137f / b319b3f742 / 8925b516e5
- 轮次：R1 发现 9 类→修复 9→R2 发现 1+派生波收编→R3~R5 被 reconciler 延迟波干扰→R6/R7 连续 2 轮全量零问题（九项电池全绿）。
- 修复：①dm200912_query_domains.py task_bound 孤儿退役删除（脚本 755→753）②migrate_illegal_doctype.py 退役删除（doc_type 门禁 8414→8609 绿）③三注册表死条目删除 24 行④retire_tmp_artifacts.py 扩展第五通道 --failures-days（data/failures 11496 文件无界增长治本，默认 90d）⑤arch_guard/manifest 双表头漂移对齐⑥fix_naming_manual.py [MODULE] 修正⑦主仓残留 5 目录 safe_rmtree（v//test_dir//metadata//access//preprocessed_configs，24h 零回生）⑧panorama_exempt_list 死条目（R2 补漏）⑨派生同步收编。
- 自主裁定：fix_naming_manual 保留（任务未完）；QMT 施工三脚本保留（Draft 未验收）；_diag/ 22 件保留待 Owner（不可再生环境信息）；runtime/phase2_reports 保留 N/A；data/failures 90d 保守；worktree 内损坏资产索引波（24346→9341）git restore 还原不入 git；capability_lookup 无通道用 [no-lookup:] 白名单标记。
- 共享收口上交：①depgraph 主仓 DB 删 MOD-GOV_DM200912_QUERY_DOMAINS 节点②merge 后主仓必跑派生再生（asset index/path_ownership_map/10 蓝图五图段；**警告：worktree 环境再生产出损坏资产索引，必须在主仓重跑**）③gateway 锁缺陷根修建议 bulk_delete_approved 通道+生成器时间戳非幂等（now()）churn④三公共登记表串行提醒。
- 遗留 1：D:\ZephyrAlpha\_diag\（22 文件）待 Owner 裁定。总控抽验：HEAD 无两死脚本/panorama 死条目 grep=0——**相符**。

## AI-04 数据域
- worktree：D:\ZephyrAlpha\.worktrees\AI-AUDIT04-001；commit 79ab155070
- 轮次：R1 发现 9（4 修+3 系统性遗留+2 误判排除）→修复 4（5 文件 11 行表头真源）→R1 复检 0（338 tests 全绿）→R2 复检 0。连续 2 轮零问题。
- 修复：raw_data_cache/cache.py+__init__、failover/manager.py、connectors/base.py、autoload.py 的 [CONSUMERS]/MATURITY 失实修正（production→testing，D_EX_SOR/包入口宣称删除）。pytest tests/market_data 285 passed。
- 自主裁定：sqlite3.connect 自有单文件库判非违规；auction_data_manager/三采集器实证非僵尸；5 文件表头修而非 15+ 全改（装配批去留待 Owner）；拒绝 [no-lookup:]/BYPASS/FORCE_DELETE 冒用，走真实 capability_lookup 通道。
- 共享收口上交：①gateway 锁 P0（同型）②MATURITY 变更后 depgraph 节点重建+_domain_mkt_data 蓝图 frontmatter/§0.6 同步③三遗留 salvage 涉及 module_translation_registry/capability_canonical_file_registry/wiring_registry 条目删改。
- 遗留 3（跨域手术，附五信号证据）：market_data vendor/connector/failover/autoload 零生产装配集群；redundant_source/recovery.py+sqlite_fallback.py 僵尸；data_governance/security/alt_data 33 模块"运行时装配批"君子协定失效。总控抽验：base.py [CONSUMERS] 行实测已删 D_EX_SOR（残留仅审计注记）——**相符**。

## AI-05 执行模拟域
（待回收）

## AI-06 交易域
（待回收）

## AI-07 回测研究ML域
（待回收）

## AI-08 因子信号域
（待回收）

## AI-09 风控合规安全域
（待回收）

## AI-10 组合持仓域
（待回收）

## AI-11 治理-规则+安全韧性
（待回收）

## AI-12 治理-审计+语义行为
（待回收）

## AI-13 治理-其余
（待回收）

## AI-14 基础设施
（待回收）

## AI-15 共享层
（待回收）

## AI-16 自治集成前端
（待回收）

## AI-17 政策架构文档
（待回收）

## AI-18 模块文档工作区
（待回收）

## AI-19 测试
（待回收）

## AI-20 脚本
（待回收）

## AI-21 五图表头语义对齐（横切域）
（待回收）

# 三、共享收口执行记录

（各域上交清单的合并台账；总控串行执行后在每条后追加执行记录）

## 已收口（总控执行）
1. 主仓 29 孤儿文件基线收编：commit 1642570d + 派生尾差 9e0cb5d5（开工裁定，见第五节#1）。

## 待总控串行执行（波次收齐后统一处理）
- G1（P0 工具链，AI-01/02/03/04 四域同型实证）：GitCommitGateway worktree 锁自锁——ops_guard PROTECTED_PREFIXES 含 .worktrees 误拦 gateway 自家 <worktree>/.ailocks/git_commit_global.lock 清理；gateway __exit__ except OSError 接不住 DeleteBlockedError。根修归 AI-20 脚本域（已作线索下发）：锁锚定主仓 .ailocks 或 ops_guard 豁免 .ailocks；补 except 类型。
- G2（AI-02 S1，高危）：docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml REG-001/REG-002 幽灵路径（module-registry.yaml git 历史从未存在、blueprint_registry.yaml 全仓不存在）→ check_registry_consistency.py FileNotFoundError，CI Tier2 必红。收口=改指实证存在路径；REG-002 蓝图登记真源收编待 Owner。
- G3（AI-03）：depgraph 主仓 DB 删 MOD-GOV_DM200912_QUERY_DOMAINS 文件级节点（path_ownership_map L206 引用残留）。
- G4（AI-03/AI-04）：merge 后主仓必跑派生再生（unified-asset-index/classified/scans、path_ownership_map、_domain_mkt_data 等蓝图 frontmatter/§0.6、10 蓝图五图派生段）；⚠ worktree 环境再生会产出损坏资产索引（24346→9341 实证），必须主仓环境重跑。
- G5（AI-04 遗留 salvage，涉共享登记表）：market_data 零生产装配集群/redundant_source+sqlite_fallback 僵尸/33 模块装配批君子协定失效——涉 module_translation_registry/capability_canonical_file_registry/wiring_registry/depgraph 手术，待 Owner 裁定后批量执行。
- G6（AI-01 备案）：requirements.txt↔pyproject 漂移无自动门禁；echo-guard 配置解析失败建议升告警——交 AI-20/AI-11 权衡，不轻增 gate。

## 跨域线索下发记录（派单时附带）
- →AI-06：ex_sor 对 market_data failover/connectors 接线宣称失实（AI-04 表头实证）；integration/failover_coordinator.py:29 注释提及 failover.manager 未 import。
- →AI-07：qnn_two_stage.py L132 / patchtst_density_encoder.py L122 死注释"待登记"（实际已用已登记码 ZA-MLT-0012/0013）。
- →AI-08：regime_detector.py 5 异常类声明 ZA-REGIME-0001~0005/0050~0052 类内无 error_code；chip_distribution_engine.py 头注 [ERROR_CONTRACT] 无异常类。
- →AI-10：core_satellite_allocator.py L147 死注释"待登记"（实际已用 ZA-POS-0027）。
- →AI-20：G1 gateway 锁 P0 根修；script_manifest/rule_index 生成器 now() 非幂等 churn；scripts 侧 vocab WARN 8 条。
- →AI-14/15/16：src 侧 vocab WARN 8 条（knowledge_classifier×3、_g04_ops_check、dashboard api_server/alert_center、reflctrl_gate×2、process_reaper）按域认领。

# 四、全局验证结果

（align_all 结论 / pre-commit / git status / worktree 清单=空）

# 五、自主裁定清单

1. **基线收编裁定（2026-09-05 开工时）**：主仓 29 个孤儿变更文件（3 staged + 25 unstaged 并集，mtime 09-03~09-05 01:19）裁定为 Owner 前会话遗留 WIP + 后台 reconciler 派生写，予以收编提交。依据：①无活跃 session 认领（.runtime/sessions heartbeat 全部 ≥5 天前，最近 gp1closure_20260831）；②RULE-TWENTY「写完即提交」铁律——不 commit 是实证风险源（Mode D 丢失 7% 教训）；③审计子代理 worktree 基于 HEAD 创建，悬挂变更将永不被审计且后续 merge 必冲突；④git 历史可回滚，收编为安全操作；⑤抽样验证内容连贯正当（reconciler 资产索引重生成 23990→24346、S4 头注入、last_updated 推进、手册/蓝图语义修正）。结论：主仓干净后裁定 MODE-B 直接全自动闭环。

# 六、待 Owner 裁定清单

1. D:\ZephyrAlpha\_diag\ 22 文件去留（AI-03）：2026-08-06 交易环境一次性诊断 PS1+系统状态备份，全仓零引用、含不可再生 Owner 机器配置信息、git 无备份、删除不可逆——按"拿不准不蛮干"保留并登记。
2. AI-04 三项 salvage（market_data 零生产装配集群 / redundant_source recovery+sqlite_fallback 僵尸 / 33 模块"运行时装配批"君子协定失效）：均需共享登记表+depgraph+多测试文件跨域手术，且涉机制去留（装配批、RecoveryManager 进程内轮询守护结构性违规）——表头已修真防误信，批量退役待 Owner。
3. registry_consistency_contract REG-002 蓝图登记真源收编（AI-02）：物理蓝图存在但无 registry 载体，涉 docs 域与 ROOR 同步机制。
4. EX/XS 错误码格式归一（既有豁免延续，AI-02 复核确认维持不越权）。

# 七、浅审与存疑标记清单

- AI-01：AGENTS.md 相关段落抽查、sitecustomize.py 10.4 六者核对——浅审-待强模型复核。
- AI-02：S1/S4 语义级漂移判定（幽灵路径/表头-实现漂移）、30 文件治理锚定抽样——浅审-待强模型复核。
- AI-03：心跳三件套活体实测结论、红蓝对抗蓝队结论——浅审-待强模型复核。
- AI-04：装配批失效/MATURITY 失实语义判定、30 文件 10.4 抽样——浅审-待强模型复核。
- 各域 10.4 六者交叉语义核对与 AI-21 五图表头对齐结论一律"浅审-待强模型复核"（附加纪律 d 强制）。
- 零问题存疑域：暂无（波次 1 四域均有实质发现与修复，非全零）。

# 八、验证命令附录

（总控可一键重跑复核的命令清单，含预期输出）
