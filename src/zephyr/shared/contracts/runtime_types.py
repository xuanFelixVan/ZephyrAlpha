# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.1
# [MODULE] zephyr.shared.contracts.runtime_types
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.base_config
# [CONSUMERS] scripts.construction.start_brain;scripts.a2a_full_verification;scripts.construction.local_layer_daemon;zephyr.trading
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] RuntimeConfig是纯数据模型;由zephyr.trading.runtime_config重新导出以保持向后兼容
# [MODIFY-GUARD] src/zephyr/runtime/runtime_config.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_runtime_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.shared.schema.base_config import BASE_CONFIG
from zephyr.shared.io.paths import REPO_ROOT

DATA_DIR = REPO_ROOT / "data"


class RuntimeConfig(BaseModel):
    model_config = BASE_CONFIG

    poll_interval: float = Field(default=5.0, description="调和循环轮询间隔(秒)")
    dashboard_enabled: bool = Field(default=True, description="TUI 状态面板")
    night_shift_storage_path: Path = Field(
        default=DATA_DIR / "night_shift_queue.jsonl",
        description="夜班登记表持久化路径",
    )
    audit_log_dir: Path = Field(default=DATA_DIR / "audit_logs", description="AI 审计日志目录")
    capability_card_dir: Path = Field(default=DATA_DIR / "capability_cards", description="能力卡片目录")
    work_dag_dir: Path = Field(default=DATA_DIR / "work_dags", description="工作 DAG 目录")
    dream_archive_dir: Path = Field(default=DATA_DIR / "dream_archive", description="知识固化归档目录")
    feedback_proposal_dir: Path = Field(default=DATA_DIR / "feedback_proposals", description="进化提案目录")
    health_snapshot_dir: Path = Field(default=DATA_DIR / "health_snapshots", description="健康快照目录")
    # circadian_state_path 已移除：CircadianScheduler 定时调度机制废除（2026-06-26裁定），不再持久化调度状态。

    auto_start_l2: bool = Field(default=True, description="启动时自动启动 L2 本地模型")
    auto_start_l3: bool = Field(default=False, description="启动时自动启动 L3 API（默认关闭，夜班激活）")
    trae_heartbeat_url: str = Field(default="", description="Trae IDE 心跳检测 URL")

    enable_dream_cycle: bool = Field(default=True, description="启用知识固化")
    enable_feedback_loop: bool = Field(default=True, description="启用反馈闭环")
    enable_stop_gate: bool = Field(default=True, description="启用质量闸门")
    enable_git_auto_commit: bool = Field(default=False, description="启用自动 Git 提交")
    work_orchestrator_enabled: bool = Field(default=True, description="启用工作编排子系统")
    enable_auto_onboarding: bool = Field(default=True, description="启用自动接入子系统")

    max_parallel_l1: int = Field(default=1, description="L1(Trae) 最大并行槽位")
    max_parallel_l2: int = Field(default=3, description="L2(Local) 最大并行槽位")
    max_parallel_l3: int = Field(default=2, description="L3(API) 最大并行槽位")

    max_daily_l3_activations: int = Field(default=10, description="AutoIntegrator 每天最多临时激活 L3 次数")

    ultimate_goal: str = Field(
        default="全域接入：项目中每一个模块、系统、脚本都在大脑管辖范围内，孤儿率=0%",
        description="终极目标——写入大脑配置，所有 AI 可读取",
    )

    ollama_base_url: str = Field(default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), description="Ollama API 地址")
    ollama_embed_model: str = Field(default="bge-m3", description="Ollama 嵌入模型")
    ollama_chat_model: str = Field(default="qwen3:8b", description="Ollama 推理模型")

    working_hours_start: int = Field(default=9, description="工作时间开始(时)")
    working_hours_end: int = Field(default=21, description="工作时间结束(时)")
    human_detection_method: str = Field(
        default="time_window",
        description="人类检测方式: heartbeat | manual_switch | time_window",
    )


__all__ = ["DATA_DIR", "RuntimeConfig"]
