#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.d5_architecture.generators.generate_policies
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 单向派生; runtime_id 作 key; 跳过空 policy
# [MODIFY-GUARD] 本脚本由autopilot执行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失->exit 1; 生成成功->exit 0
# [TESTS] tests/governance/test_generate_policies.py
# [TTL] permanent
"""
#183: 从 data_sources_registry.yaml 派生 policies.yaml

真源：architecture_model/data/data_sources_registry.yaml
派生物：src/zephyr/data/config/policies.yaml

派生逻辑：
  遍历 data_sources，对每个有非空 policy 的数据源，
  用 runtime_id 作 key，提取 policy 字段，写入 policies.yaml

跳过 policy: {} 的数据源（如 DS-BAIDUYUN/DS-NEWSAPI/DS-YFINANCE/DS-STOOQ），
因为它们不需要调用策略（非 API 源或已废弃）。

触发：改 data_sources_registry.yaml → commit → reconciler → 本生成器 → policies.yaml 重生
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装")
    sys.exit(1)

# 从 _shared.constants 导入 REPO_ROOT（SSoT，禁止重新定义）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

SOURCE_YAML = REPO_ROOT / "architecture_model" / "data" / "data_sources_registry.yaml"
OUTPUT_YAML = REPO_ROOT / "src" / "zephyr" / "data" / "config" / "policies.yaml"


def generate():
    """从 data_sources_registry.yaml 派生 policies.yaml"""
    if not SOURCE_YAML.exists():
        print(f"[ERROR] 真源不存在: {SOURCE_YAML}")
        sys.exit(1)

    with open(SOURCE_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    sources = data.get("data_sources", [])
    policies = {}
    skipped = []

    for src in sources:
        runtime_id = src.get("runtime_id")
        policy = src.get("policy")
        if not runtime_id:
            continue
        if not policy:
            skipped.append(src.get("id", runtime_id))
            continue
        policies[runtime_id] = policy

    # 写入派生物
    OUTPUT_YAML.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md",
        "# [MODULE] zephyr.data.config.policies",
        "# [DOMAIN] D_DATA",
        "# [TTL] permanent",
        "# 派生物（#183）：由 generate_policies.py 从 data_sources_registry.yaml 派生",
        f"# 真源：architecture_model/data/data_sources_registry.yaml v{data.get('version', '?')}",
        "# 禁止手工修改此文件——改真源后由 reconciler 自动重生",
        "# policy_registry.py 的 maybe_reload 会在 mtime 变化时热更新",
        "",
    ]

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        f.write("\n".join(header) + "\n")
        yaml.dump(policies, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"[OK] 派生 {len(policies)} 个数据源策略 → {OUTPUT_YAML}")
    if skipped:
        print(f"  跳过 {len(skipped)} 个无策略数据源: {', '.join(skipped)}")


if __name__ == "__main__":
    generate()
