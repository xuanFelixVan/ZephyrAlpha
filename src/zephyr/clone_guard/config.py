# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §6
# [MODULE] zephyr.clone_guard.config
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pathlib; yaml
# [CONSUMERS] zephyr.clone_guard.orchestrator; zephyr.clone_guard.engines.echo_guard_adapter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] clone_guard.yml 是 CloneGuard 统一配置 SSoT；配置缺失时使用安全默认值（extract 级阻断 + 30s 超时）
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置加载失败返回安全默认值（不抛异常）
# [TESTS] tests/clone_guard/test_config.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



CloneGuard 配置加载器——从 clone_guard.yml 读取统一配置。

配置缺失或解析失败时使用安全默认值（extract 级阻断 + 30s 超时 + echo-guard 启用）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root，类型注解 Path
#   code: config.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CloneGuardConfig
#   name_en: CloneGuardConfig
#   intro: CloneGuard 统一配置（从 clone_guard.yml 加载）。
#   desc: CloneGuard 统一配置（从 clone_guard.yml 加载）。；公共方法（定义序）: block_severities；源码 L75-L146
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② load_config
#   name_en: load_config
#   intro: 从 repo_root/clone_guard.yml 加载配置，失败时返回安全默认值。
#   desc: 从 repo_root/clone_guard.yml 加载配置，失败时返回安全默认值。 Args: repo_root: 仓库根目录路径。 Returns: CloneGuar…；源码 L149-L218
#   inputs: repo_root
#   outputs: CloneGuardConfig
# 层: 输出
# - id: O1
#   name_zh: CloneGuardConfig
#   name_en: CloneGuardConfig
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.clone_guard.orchestrator; zephyr.clone_guard.engines.echo_guard_adapter
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

__all__ = ["CloneGuardConfig", "load_config"]

_DEFAULT_CONFIG_PATH = "clone_guard.yml"


@dataclass(frozen=True)
class CloneGuardConfig:
    """CloneGuard 统一配置（从 clone_guard.yml 加载）。"""

    # Layer 1: pre-commit 拦截
    pre_commit_timeout_sec: int = 30
    fail_on_severity: str = "extract"  # extract=硬阻断, review=警告, none=不阻断
    echo_guard_enabled: bool = True

    # ── Phase B 补齐：ast-grep 显式字段（从隐式规则目录推断改为显式）──
    ast_grep_enabled: bool = True

    # ── Phase B 补齐：reDUP（L1 第3引擎 + L2 语义克隆 T3/T4）──
    redup_enabled: bool = True
    redup_min_sim: float = 0.85  # §3.3 --min-sim 0.85
    redup_max_groups: int = 0  # §3.3 --max-groups 0（0=不限组数）
    redup_mode: str = "changed-only"  # "changed-only" (L1) / "semantic" (L2)
    # reDUP L1 changed-only 模式的 base ref——redup scan --changed-only --base-ref <ref>
    # 默认 HEAD；pre-commit 钩子按实际合并基设置（如 origin/dev... 或 merge-base）
    redup_base_ref: str = "HEAD"

    # ── Phase C：mcrit（L2 索引底座 + L0 查重加速）──
    mcrit_enabled: bool = False  # 默认 False——L2 审计才启用，L1 不用
    mcrit_index_path: str = ".mcrit/index.db"
    mcrit_query_threshold: float = 0.7

    # ── Phase C：Vendetect（L3 跨仓库合规审计，AGPL 独立工具）──
    vendetect_enabled: bool = False  # 默认 False——按需触发
    vendetect_remote_url: str | None = None

    # ── Phase C：relate（L2/L3 快速预筛加速器，Path B: datasketch MinHash LSH）──
    relate_enabled: bool = False  # 默认 False——加速器，可选
    relate_index_path: str = ".relate/index"  # 保留（未来磁盘持久化预留）；MVP 进程内索引
    relate_top_k: int = 10
    relate_threshold: float = 0.7  # LSH 候选阈值（MinHash Jaccard 估计）
    relate_num_perm: int = 128  # MinHash 排列数（精度/性能权衡，128≈标准值）
    relate_shingle_size: int = 5  # k-gram shingle 大小（token 数）

    # 降级策略
    fail_closed: bool = False  # echo-guard 全部超时/崩溃时是否阻断（False=warn-only 兜底）

    # ── acknowledged 白名单写入路径（治本 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS）──
    # True=走 echo-guard acknowledge CLI（PyYAML 重写丢注释，诊断/兼容用）
    # False=项目层 ruamel.yaml round-trip 写 echo-guard.yml acknowledged 段（保留注释，默认）
    acknowledge_via_cli: bool = False

    # ── Layer 2/3 超时（比 L1 宽松）──
    audit_timeout_sec: int = 300  # L2 全量审计 5 分钟
    compare_timeout_sec: int = 600  # L3 跨仓库 10 分钟

    # 聚合策略（Phase B——多引擎结果合并）
    filter_minority: bool = False  # True=过滤仅单引擎报告的 findings，False=保留但标记 consensus="single"

    # 运行环境（L1 离线优先——HF_HUB_OFFLINE=1 强制 Tier 1 AST 哈希检测，跳过模型下载）
    env: dict[str, str] = field(default_factory=dict)

    # 忽略路径（除 echo-guard.yml 自身排除规则外）
    ignore_paths: tuple[str, ...] = (
        "tests/",
        "docs/",
        ".runtime/",
        ".echo-guard/",
        "**/_generated/",
    )

    @property
    def block_severities(self) -> set[str]:
        """返回应硬阻断的严重性集合。"""
        if self.fail_on_severity == "extract":
            return {"extract"}
        if self.fail_on_severity == "review":
            return {"extract", "review"}
        return set()


def load_config(repo_root: Path) -> CloneGuardConfig:
    """从 repo_root/clone_guard.yml 加载配置，失败时返回安全默认值。

    Args:
        repo_root: 仓库根目录路径。

    Returns:
        CloneGuardConfig 实例（加载失败时返回默认值）。
    """
    config_path = repo_root / _DEFAULT_CONFIG_PATH
    if not config_path.exists():
        logger.debug("clone_guard.yml 不存在(%s)，使用默认配置", config_path)
        return CloneGuardConfig()

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001  配置解析失败用默认值
        logger.warning("clone_guard.yml 解析失败(%s: %s)，使用默认配置", type(e).__name__, e)
        return CloneGuardConfig()

    if not isinstance(raw, dict):
        logger.warning("clone_guard.yml 顶层非 dict，使用默认配置")
        return CloneGuardConfig()

    # 安全提取字段——只认已知的 key，忽略未知 key
    pre_commit = raw.get("pre_commit", {}) or {}
    severity = raw.get("severity", {}) or {}
    aggregation = raw.get("aggregation", {}) or {}
    audit = raw.get("audit", {}) or {}
    compare = raw.get("compare", {}) or {}
    env_raw = raw.get("env", {}) or {}
    env = {str(k): str(v) for k, v in env_raw.items()} if isinstance(env_raw, dict) else {}

    # 引擎配置子节（蓝图 §6.1 嵌套结构 pre_commit.engines.* / audit.engines.* / compare.*）
    pc_engines = pre_commit.get("engines", {}) or {}
    eg_cfg = pc_engines.get("echo_guard", {}) or {}
    sg_cfg = pc_engines.get("ast_grep", {}) or {}
    rd_cfg = pc_engines.get("redup", {}) or {}
    audit_engines = audit.get("engines", {}) or {}
    mcrit_cfg = audit_engines.get("mcrit", {}) or {}

    return CloneGuardConfig(
        pre_commit_timeout_sec=int(pre_commit.get("timeout_sec", 30)),
        fail_on_severity=str(pre_commit.get("fail_on", severity.get("extract", "extract"))),
        echo_guard_enabled=bool(eg_cfg.get("enabled", pre_commit.get("echo_guard_enabled", True))),
        ast_grep_enabled=bool(sg_cfg.get("enabled", True)),
        redup_enabled=bool(rd_cfg.get("enabled", True)),
        redup_min_sim=float(rd_cfg.get("min_sim", 0.85)),
        redup_max_groups=int(rd_cfg.get("max_groups", 0)),
        redup_mode=str(rd_cfg.get("mode", "changed-only")),
        redup_base_ref=str(rd_cfg.get("base_ref", "HEAD")),
        mcrit_enabled=bool(mcrit_cfg.get("enabled", False)),
        mcrit_index_path=str(mcrit_cfg.get("index_path", ".mcrit/index.db")),
        mcrit_query_threshold=float(mcrit_cfg.get("query_threshold", 0.7)),
        vendetect_enabled=bool(compare.get("vendetect_cross_repo", False)),
        vendetect_remote_url=compare.get("vendetect_remote_url"),
        relate_enabled=bool(compare.get("relate_prescreen", False)),
        relate_index_path=str(compare.get("relate_index_path", ".relate/index")),
        relate_top_k=int(compare.get("relate_top_k", 10)),
        relate_threshold=float(compare.get("relate_threshold", 0.7)),
        relate_num_perm=int(compare.get("relate_num_perm", 128)),
        relate_shingle_size=int(compare.get("relate_shingle_size", 5)),
        audit_timeout_sec=int(audit.get("timeout_sec", 300)),
        compare_timeout_sec=int(compare.get("timeout_sec", 600)),
        fail_closed=bool(pre_commit.get("fail_closed", False)),
        acknowledge_via_cli=bool(pre_commit.get("acknowledge_via_cli", False)),
        filter_minority=bool(aggregation.get("filter_minority", False)),
        env=env,
        ignore_paths=tuple(raw.get("ignore_paths", ()) or CloneGuardConfig().ignore_paths),
    )
