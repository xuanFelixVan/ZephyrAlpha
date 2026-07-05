# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback._manifest
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF__manifest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-021 Rollback System — 模块文件清单 (_manifest_)。

本文件声明模块内所有 .py 文件及其职责，对齐 blueprint §3 文件组成表。
版本: 0.10.0
最后更新: 2026-05-06
"""

MANIFEST = {
    "module_id": "MOD-INF-021",
    "version": "0.10.0",
    "code_directory": "src/zephyr/infrastructure/rollback/",
    "files": [
        {
            "file": "rollback_executor.py",
            "responsibility": "回滚执行器——四级回滚操作封装（full_revert/partial_revert/discard/hard_reset）+ forward-fix 评估 + preflight_check + preview + 全局锁管理 + 依赖影响分析",
            "blind_spots": ["B2", "B4", "B5", "B9", "B48", "B51"],
        },
        {
            "file": "rollback_verifier.py",
            "responsibility": "回滚验证器——G0 门禁 + __pycache__ 清理 + DB 一致性自愈 + 逐行 differential check",
            "blind_spots": ["B3", "B16", "B53"],
        },
        {
            "file": "auto_rollback_trigger.py",
            "responsibility": "自动回滚触发器——监听 auto_guard 后验结果 + 失败信号三分类（hard/soft/transient）",
            "blind_spots": ["B15"],
        },
        {
            "file": "rollback_state_machine.py",
            "responsibility": "回滚状态机——步骤级状态追踪（PENDING/SUCCESS/FAILED/RETRYING）+ 部分失败恢复 + in_flight 文件管理",
            "blind_spots": ["B42", "B43"],
        },
        {
            "file": "forward_fix_runner.py",
            "responsibility": "Forward-Fix 执行器——回滚的替代决策路径：优先产生 FIX commit 而非 revert",
            "blind_spots": ["B51"],
        },
        {
            "file": "rollback_simulator.py",
            "responsibility": "回滚模拟器——在临时 git worktree 中模拟回滚流程，CI 集成",
            "blind_spots": ["B11"],
        },
        {
            "file": "rollback_drill.py",
            "responsibility": "回滚演练调度器——每周定时 DiRT 演练 + 混沌场景注入（GC 并发/SQLite 锁/磁盘满载）",
            "blind_spots": ["B41", "B52"],
        },
        {
            "file": "rollback_loop_detector.py",
            "responsibility": "循环检测器——同一 (task, gate) 组合 >3 次/h → 暂停 + 升级",
            "blind_spots": ["B6"],
        },
        {
            "file": "agent_cooldown.py",
            "responsibility": "Agent 隔离器——回滚后 5min 禁止修改被回滚文件",
            "blind_spots": ["B8"],
        },
        {
            "file": "rollback_lock.py",
            "responsibility": "全局锁——rollback.lock + SQLite advisory lock + 队列管理 + 优先级排序",
            "blind_spots": ["B9", "B40"],
        },
        {
            "file": "kill_switch.py",
            "responsibility": "三级 Kill Switch 管理器——L1 Session Kill / L2 Skill Kill / L3 Global Kill + 自动递进升级",
            "blind_spots": ["B46"],
        },
        {
            "file": "sqlite_dumper.py",
            "responsibility": "SQLite dump 工具——schema + data → JSONL（Merkle 树签名 + HMAC）/ JSONL → 重建 SQLite + 完整性验证",
            "blind_spots": ["B1", "B3", "B49"],
        },
        {
            "file": "rollback_dashboard.py",
            "responsibility": "回滚仪表盘——生成 Markdown 零依赖仪表盘 + IM 推送",
            "blind_spots": ["B47"],
        },
        {
            "file": "rollback_context_restorer.py",
            "responsibility": "上下文恢复器——回滚后注入 AI 会话恢复 prompt",
            "blind_spots": ["B44"],
        },
        {
            "file": "rollback_budget.py",
            "responsibility": "回滚预算管理器——并发限制 / 日配额 / 预算耗尽切换 forward-fix",
            "blind_spots": ["B55"],
        },
        {
            "file": "checkpoint_gc.py",
            "responsibility": "Checkpoint GC——快照保留策略（max 100 / max 90 天）+ 定期清理",
            "blind_spots": ["B50"],
        },
        {
            "file": "rollback_bootstrap.py",
            "responsibility": "自举回滚器——零依赖最小化回滚 + chmod 444 只读锁定",
            "blind_spots": ["B56"],
        },
    ],
    "directories": [
        {
            "path": "data/rollback/db_snapshots/",
            "description": "SQLite 快照存放目录——{commit_sha}.jsonl，由 git track",
            "blind_spots": ["B1", "B3"],
        },
        {
            "path": "data/rollback/down/",
            "description": "Down-migration 脚本目录——{commit_sha}.sh / {commit_sha}.ps1，自动生成",
            "blind_spots": ["B45"],
        },
        {
            "path": "data/rollback/rollback_metrics.db",
            "description": "回滚指标——MTTR / 频率 / 成功率 / 冲突记录 / drill 结果",
            "blind_spots": ["B12"],
        },
        {
            "path": ".zephyr/rollback_in_flight/",
            "description": "回滚 flight 记录目录——幂等保护 + 崩溃恢复",
            "blind_spots": ["B43"],
        },
    ],
    "total_py_files": 17,
    "total_dirs": 4,
}
