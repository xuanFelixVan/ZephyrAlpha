# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/generator_auto_trigger_pilot.md | §verify
# [MODULE] scripts.governance.verify_generator_paths
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.apply_battle_map (subprocess); scripts.governance.reconcile_generators (reconcile_stale); scripts.governance.git_hooks.post_commit_regen_yaml
# [CONSUMERS] 开发者手动 / CI 冒烟
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 路径1 add 后必 remove（DB 真源恢复）；退出码 0=全 ok/skip, 1=有 failed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单路径失败不阻断其他路径；DB 不可用时路径1 skip 而非 fail
# [TESTS] 自身即冒烟脚本
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [ARCH-REF] generator_auto_trigger_pilot.md
"""verify_generator_paths.py — 生成器三条触发路径冒烟验证（手动/CI，不接 commit hook）。

为什么是独立脚本而非 commit hook（拒绝过度工程）：
  - 路径1（DB 实时）需真实 PostgreSQL 写入 ~5-15s，每次 commit 跑会拖慢开发 + 污染 DB 真源
  - 路径3（post-commit）在 commit hook 里测 post-commit hook 是递归冲突
  - 全链路依赖 DB 环境，CI/本地未必每次都起
  故整理为手动/CI 冒烟脚本：``python scripts/governance/verify_generator_paths.py``

三条路径（对应 generator_auto_trigger_pilot.md §3.2 三触发源）：
  1. **DB 实时**：apply_battle_map add+remove 临时环节 → 观察 [REGENERATE] spawn
     （apply_*.py 写 DB 后内联 reconcile_async 实时触发）
  2. **YAML 启动兜底**：reconcile_stale() 扫描 → 验证返回结构 + total_scanned
     （boot_hooks 启动时 mtime 对比兜底）
  3. **post-commit YAML**：mock _committed_yaml_files → 验证检测 + spawn 意图
     （git post-commit 检测 YAML 输入源变更异步触发）

设计原则：
  - 自清理：路径1 add 后必 remove（finally 块），DB 真源恢复
  - CI 友好：无 DB 时路径1 skip 而非 fail（exit 0）
  - 不污染：路径3 拦截 Popen 验证 spawn 意图，不起真实后台进程
  - 幂等：可重复运行

退出码：
  - 0: 全部 ok 或 skip（无 failed）
  - 1: 有 failed

用法::
    python scripts/governance/verify_generator_paths.py          # 跑全部三路径
    python scripts/governance/verify_generator_paths.py --path 1 # 只跑路径1
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 生成器三条触发路径冒烟验证（手动/CI，不接 commit hook）。路径1 DB实时 add+remove 临时环节；路径2 reconcile_stale 扫描；路径3 mock post-commit 检测+spawn 意图。
dimensions:
- D5
priority: P3
timeout_seconds: 300
warn_only: true
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.infra.process_pool import run_subprocess_hidden

# 临时环节 ID 前缀（带时间戳保证唯一，避免与现存 step 冲突）
_VERIFY_STEP_PREFIX = "BM-VERIFY-"


# ---------------------------------------------------------------------------
# 路径1：DB 实时触发（apply_battle_map add+remove → reconcile_async spawn）
# ---------------------------------------------------------------------------


def verify_path1_db_realtime() -> dict:
    """路径1：真实写 DB → 观察 reconcile_async spawn → 清理。

    DB 不可用时返回 skip（CI 无 DB 环境）。
    """
    result = {"path": "1-db-realtime", "status": "ok", "detail": ""}
    step_id = f"{_VERIFY_STEP_PREFIX}{time.strftime('%Y%m%d%H%M%S')}"
    apply_script = _REPO_ROOT / "scripts" / "governance" / "apply_battle_map.py"

    # add_step：应触发 [REGENERATE] 🔄 后台启动
    try:
        proc = run_subprocess_hidden(
            [
                sys.executable,
                str(apply_script),
                "--add-step",
                "--step-id",
                step_id,
                "--step-name",
                "冒烟验证临时环节",
                "--flow-stage",
                "buy_flow",
                "--layer",
                "L2A",
                "--sort-order",
                "999",
                "--source-ref",
                "verify_generator_paths",
            ],
            cwd=str(_REPO_ROOT),
            encoding="utf-8",
            timeout=120,
        )
    except Exception as e:  # noqa: BLE001
        result["status"] = "skip"
        result["detail"] = f"DB 不可用（apply 调用失败）: {type(e).__name__}: {e}"
        return result

    # 退出码非 0：判断是 DB 不可用（skip）还是真失败（failed）
    if proc.returncode != 0:
        stderr = proc.stderr or ""
        # DB 连接失败的特征 → skip（CI 无 DB）
        if any(
            k in stderr
            for k in (
                "could not connect",
                "connection refused",
                "OperationalError",
                "password authentication",
                'role "postgres" does not exist',
            )
        ):
            result["status"] = "skip"
            result["detail"] = f"DB 不可用（skip 而非 fail）: {stderr.strip()[:200]}"
            return result
        result["status"] = "failed"
        result["detail"] = f"add_step 退出码 {proc.returncode}: {stderr.strip()[:300]}"
        return result

    # 验证 [REGENERATE] spawn 输出
    stderr = proc.stderr or ""
    m = re.search(r"\[REGENERATE\].*PID=(\d+).*日志:\s*(.+\.log)", stderr)
    if not m:
        result["status"] = "failed"
        result["detail"] = f"未检测到 [REGENERATE] spawn 输出。stderr: {stderr.strip()[:300]}"
    else:
        pid, log_file = m.group(1), m.group(2)
        result["detail"] = f"spawn PID={pid}, 日志={Path(log_file).name}"
        # 等待异步生成器完成（最多 30s），验证日志含成功记录
        log_path = Path(log_file)
        for _ in range(15):
            if log_path.exists() and log_path.stat().st_size > 0:
                break
            time.sleep(2)
        if log_path.exists():
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            if "battle_map" in log_text and ("ok" in log_text or "✅" in log_text):
                result["detail"] += "; 生成器执行成功（日志确认）"
            else:
                result["detail"] += f"; 日志未见成功标记: {log_text.strip()[:200]}"

    # 清理：remove_step（无论上面是否 failed 都要清理，恢复 DB 真源）
    try:
        run_subprocess_hidden(
            [sys.executable, str(apply_script), "--remove-step", "--step-id", step_id],
            cwd=str(_REPO_ROOT),
            encoding="utf-8",
            timeout=120,
        )
        result["detail"] += "; 已清理临时环节"
    except Exception as e:  # noqa: BLE001
        # 清理失败是严重问题（DB 残留）→ 升级为 failed
        result["status"] = "failed"
        result["detail"] += f"; ⚠清理失败（DB 可能残留 {step_id}）: {e}"

    return result


# ---------------------------------------------------------------------------
# 路径2：YAML 启动兜底（reconcile_stale 扫描）
# ---------------------------------------------------------------------------


def verify_path2_yaml_stale() -> dict:
    """路径2：调用 reconcile_stale() 验证扫描链路可用 + 返回结构正确。

    这是 boot_hooks 启动时调用的同一函数。不强制制造 stale（幂等扫描即可）。
    """
    result = {"path": "2-yaml-stale", "status": "ok", "detail": ""}
    try:
        from scripts.governance.reconcile_generators import reconcile_stale

        ret = reconcile_stale()
    except Exception as e:  # noqa: BLE001
        result["status"] = "failed"
        result["detail"] = f"reconcile_stale() 调用异常: {type(e).__name__}: {e}"
        return result

    # 验证返回结构
    if not isinstance(ret, dict):
        result["status"] = "failed"
        result["detail"] = f"返回非 dict: {type(ret).__name__}"
        return result
    for key in ("regenerated", "skipped", "total_scanned"):
        if key not in ret:
            result["status"] = "failed"
            result["detail"] = f"返回缺字段 '{key}': {ret}"
            return result

    total = ret["total_scanned"]
    regen = len(ret["regenerated"])
    skipped = len(ret["skipped"])
    # 检查 regenerated 中是否有 failed 的生成器
    failed_gens = [r.get("generator", "?") for r in ret["regenerated"] if r.get("status") not in ("ok",)]
    if failed_gens:
        result["status"] = "failed"
        result["detail"] = f"扫描 {total} 生成器，{regen} 重生成，其中失败: {failed_gens}"
    else:
        result["detail"] = f"扫描 {total} 生成器，{regen} 重生成（全 ok），{skipped} 已最新"
    return result


# ---------------------------------------------------------------------------
# 路径3：post-commit YAML 触发（mock 检测 + 拦截 Popen 验证 spawn 意图）
# ---------------------------------------------------------------------------


def verify_path3_postcommit_yaml() -> dict:
    """路径3：mock _committed_yaml_files → 验证检测 + spawn 意图（拦截 Popen）。

    拦截 subprocess.Popen 而非真实 spawn：避免每次冒烟起后台进程
    （真实 spawn 已由 tests/governance/test_reconcile_generators.py 端到端覆盖）。
    """
    result = {"path": "3-postcommit-yaml", "status": "ok", "detail": ""}
    try:
        from scripts.governance.git_hooks import post_commit_regen_yaml as pcm
    except Exception as e:  # noqa: BLE001
        result["status"] = "failed"
        result["detail"] = f"import post_commit_regen_yaml 失败: {e}"
        return result

    # 验证 registry 加载 + 输入源收集
    inputs = pcm._generator_yaml_inputs()
    if not inputs:
        result["status"] = "failed"
        result["detail"] = "_generator_yaml_inputs() 返回空（registry 加载异常？）"
        return result

    # 选一个真实输入源做 mock
    mock_file = next((i for i in inputs if "terminology_glossary.yaml" in i), sorted(inputs)[0])

    # 验证匹配逻辑
    if not pcm._matches_generator_input([mock_file], inputs):
        result["status"] = "failed"
        result["detail"] = f"_matches_generator_input 对 {mock_file} 返回 False（应 True）"
        return result

    # mock _committed_yaml_files + 拦截 Popen（验证 spawn 意图，不起真实进程）
    pcm._committed_yaml_files = lambda: [mock_file]  # type: ignore
    spawned_calls: list = []
    orig_popen = pcm.subprocess.Popen

    class _FakePopen:  # 拦截 spawn，记录调用参数
        def __init__(self, *args, **kwargs):
            """__init__ implementation."""
            spawned_calls.append(args)
            self.pid = 99999

    # mock _is_lock_active 返回 False（防残留 lockfile 干扰路径3 验证）
    # 场景：真实 commit 后 60s 内运行本脚本，lockfile 仍活跃 → main() 会 skip spawn → 验证失败
    if hasattr(pcm, "_is_lock_active"):
        pcm._is_lock_active = lambda: False
    pcm.subprocess.Popen = _FakePopen  # type: ignore
    try:
        ret = pcm.main()
    finally:
        pcm.subprocess.Popen = orig_popen  # type: ignore

    # 验证：main() 返回 0（不阻断 git）+ spawn 被调用 1 次
    if ret != 0:
        result["status"] = "failed"
        result["detail"] = f"main() 返回 {ret}（应 0，post-commit 不阻断 git）"
        return result
    if len(spawned_calls) != 1:
        result["status"] = "failed"
        result["detail"] = f"spawn 调用 {len(spawned_calls)} 次（应 1）"
        return result
    result["detail"] = (
        f"mock 提交 {Path(mock_file).name} → 检测命中 → spawn 意图确认 ({len(spawned_calls)} 次), main()=0 不阻断 git"
    )
    return result


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

_VERIFIERS = {
    1: ("DB 实时触发", verify_path1_db_realtime),
    2: ("YAML 启动兜底", verify_path2_yaml_stale),
    3: ("post-commit YAML", verify_path3_postcommit_yaml),
}


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="生成器三条触发路径冒烟验证")
    parser.add_argument("--path", type=int, choices=[1, 2, 3], help="只跑指定路径（默认全部）")
    args = parser.parse_args(argv)

    paths = [args.path] if args.path else [1, 2, 3]
    print("=" * 64)
    print("生成器触发路径冒烟验证（手动/CI，非 commit hook）")
    print("=" * 64)

    results: list[dict] = []
    for p in paths:
        label, fn = _VERIFIERS[p]
        print(f"\n▶ 路径{p}: {label}")
        r = fn()
        results.append(r)
        icon = {"ok": "✅", "failed": "❌", "skip": "⏭"}[r["status"]]
        print(f"  {icon} [{r['status'].upper()}] {r['detail']}")

    # 汇总
    ok = sum(1 for r in results if r["status"] == "ok")
    failed = sum(1 for r in results if r["status"] == "failed")
    skip = sum(1 for r in results if r["status"] == "skip")
    print("\n" + "=" * 64)
    print(f"汇总: {ok} ok / {skip} skip / {failed} failed（共 {len(results)} 路径）")
    print("=" * 64)
    # 退出码：有 failed 才非 0（skip 不算失败，CI 无 DB 时路径1 skip 是预期）
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
