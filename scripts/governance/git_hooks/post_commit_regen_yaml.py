# [A_test] module_id: MOD-GOV_post_commit_regen_yaml | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/generator_auto_trigger_pilot.md | §
# [MODULE] scripts.governance.git_hooks.post_commit_regen_yaml
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.reconcile_generators (reconcile_stale via subprocess); docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml (只读 yaml input_sources)
# [CONSUMERS] .git/hooks/post-commit (sourced 调用)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何异常→静默退出 0（post-commit hook 不得阻断 git 操作）
# [TESTS] tests/governance/test_reconcile_generators.py::TestPostCommitRegenYaml
# [TTL] permanent
# [ARCH-REF] generator_auto_trigger_pilot.md §缺口#3
"""post_commit_regen_yaml.py — post-commit YAML 变更触发器（治本缺口#3）

病根
----
YAML 真源（module_translation_registry.yaml / battle_map_domain_policy.yaml /
cross_layer_contracts.yaml / data_sources_registry.yaml 等）手编后无 apply 调用，
boot_hooks 仅在交易运行时启动时 mtime 扫描兜底。纯 CLI / governance 脚本场景改
YAML 后，派生文档不重生成，直到下次交易运行时启动——漂移窗口可达数小时/数天。

治本
----
post-commit 检测本次 commit 是否改动生成器的 YAML 输入源，是则异步 spawn
``reconcile_generators.py --stale``（非阻塞，日志落 .runtime/logs/）。

- **精确匹配**：只检查 generator_registry.yaml 中 ``yaml:`` 前缀的 input_sources，
  避免每次提交任意 YAML 都触发（rule_catalog 等 YAML 不是生成器输入）。
- **幂等**：reconcile_stale 内部 mtime 对比，仅重生成 stale 产物。
- **非阻塞**：Popen detached（Windows CREATE_NO_WINDOW），post-commit 立即返回。
- **逃生通道**：ZEPHYR_SKIP_REGENERATE=1 跳过（批量提交场景）。
- **绝不阻断**：任何异常静默 exit 0（post-commit hook 不得阻断 git 操作）。

时序
----
本脚本在 post-commit 中**先于** post_commit_guard.sh 执行（guard 可能 git reset）。
- guard 放行（exit 0）→ commit 保留，YAML 变更已落库，重生成正确。
- guard reset（非 GW commit）→ soft reset 保留改动在 staging，YAML 文件本身仍
  变更，重生成仍正确（生成器读文件内容，不依赖 commit 是否保留）。

安装
----
在 ``.git/hooks/post-commit`` 中、guard 块**之前**追加::

    # POST-COMMIT-YAML-REGEN（治本缺口#3：YAML 变更实时触发重生成）
    if [ -f "scripts/governance/git_hooks/post_commit_regen_yaml.py" ]; then
        python scripts/governance/git_hooks/post_commit_regen_yaml.py >/dev/null 2>&1 || true
    fi

Usage::

    python scripts/governance/git_hooks/post_commit_regen_yaml.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "generator_registry.yaml"
)
_ORCHESTRATOR = _REPO_ROOT / "scripts" / "governance" / "reconcile_generators.py"


def _committed_yaml_files() -> list[str]:
    """返回本次 commit 改动的 .yaml/.yml 文件列表（相对 repo root）。

    首次提交（无 HEAD~1）时 git diff 会失败→返回空（不触发）。
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AMR", "HEAD~1", "HEAD"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if proc.returncode != 0:
            return []
    except Exception:  # noqa: BLE001 — post-commit 不得阻断
        return []
    return [
        f.replace("\\", "/").strip()
        for f in proc.stdout.splitlines()
        if f.lower().endswith((".yaml", ".yml"))
    ]


def _generator_yaml_inputs() -> set[str]:
    """从 generator_registry.yaml 收集所有 yaml: 前缀的输入源路径（归一化）。"""
    inputs: set[str] = set()
    try:
        import yaml  # type: ignore[import-untyped]
        if not _REGISTRY_YAML.is_file():
            return inputs
        data = yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
        for gen in data.get("generators", []):
            for src in gen.get("input_sources", []):
                if isinstance(src, str) and src.startswith("yaml:"):
                    path_str = src.split(":", 1)[1].split("#")[0].strip()
                    inputs.add(path_str.replace("\\", "/"))
    except Exception:  # noqa: BLE001
        return inputs
    return inputs


def _matches_generator_input(committed: list[str], inputs: set[str]) -> bool:
    """committed 文件是否命中任一生成器 yaml 输入源（精确或前缀匹配）。"""
    for c in committed:
        for inp in inputs:
            if c == inp or c.startswith(inp.rstrip("/") + "/"):
                return True
    return False


def main() -> int:
    """post-commit 入口：检测 YAML 变更 → 异步 spawn reconcile_stale。

    Returns:
        0（始终——post-commit 不得阻断 git；失败仅记日志）
    """
    # 顶层兜底：post-commit hook 绝不阻断 git 操作（§ERROR_CONTRACT）
    try:
        # 逃生通道
        if os.environ.get("ZEPHYR_SKIP_REGENERATE") == "1":
            return 0

        committed = _committed_yaml_files()
        if not committed:
            return 0

        inputs = _generator_yaml_inputs()
        if not inputs or not _matches_generator_input(committed, inputs):
            return 0  # 改动的 YAML 不是任何生成器的输入源，跳过

        # 异步 spawn reconcile_stale（非阻塞）
        log_dir = _REPO_ROOT / ".runtime" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"post_commit_regen_yaml_{ts}.log"

        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            log_handle = open(log_file, "w", encoding="utf-8")
            log_handle.write(
                f"[POST-COMMIT-REGEN] 检测到生成器 YAML 输入源变更，异步触发 reconcile_stale\n"
                f"[POST-COMMIT-REGEN] 变更文件: {committed}\n"
            )
            log_handle.flush()
            proc = subprocess.Popen(  # noqa: S603 — 受控 _ORCHESTRATOR
                [sys.executable, str(_ORCHESTRATOR), "--stale"],
                cwd=str(_REPO_ROOT),
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
            log_handle.close()  # 父进程关闭副本；子进程已继承
            # 不等待——post-commit 立即返回
            sys.stderr.write(
                f"[POST-COMMIT-REGEN] 🔄 YAML 变更触发后台重生成 "
                f"PID={proc.pid} 日志: {log_file}\n"
            )
        except Exception as e:  # noqa: BLE001 — spawn 失败不阻断
            sys.stderr.write(
                f"[POST-COMMIT-REGEN] WARNING: 触发失败（不阻断 commit）: {e}\n"
            )
    except Exception as e:  # noqa: BLE001 — 顶层兜底：任何异常都不阻断 git
        sys.stderr.write(
            f"[POST-COMMIT-REGEN] WARNING: 内部异常（不阻断 commit）: {e}\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
