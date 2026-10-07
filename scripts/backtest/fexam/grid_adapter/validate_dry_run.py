# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 网格考干跑验证（只读校验不占卡）
# [MODULE] scripts.backtest.fexam.grid_adapter.validate_dry_run.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
# -*- coding: utf-8 -*-
"""F道·干跑验证面（st-matrix-20261006 / F lane）。

只读验证发射的 subspace 配置合法性（不真跑回测、不占 GPU）：
  V1 结构校验   纯 dict[str,[str]]、轴名/取值 ⊆ schema（禁造轴名的显式判据——
                执行器过滤语义下未知键只会静默滤空，必须显式查）
  V2 计数校验   GridCompiler 只读编译+执行器同语义过滤计数 == meta.expected_cells
  V3 预算校验   执行器 _apply_prereg_budget 原函数钳制通过（冻结册真源）
  V4 只读校验面 factory_grid_executor --verify-counts（台账对账尺，禁写）
  V5 只读校验面 compute_window_gate check --purpose f06_grid_batch（E0 问闸预演）
  V6 启动器预演 fire_grid.py（dry-run 模式逐行门检快照）

产出：dry_run_validation.log（全文）+ dry_run_verdict.json（机读判决）。
退出码：0=全部 V1-V3 过（V4/V5/V6=留痕参考不阻断配置合法性）。

用法：python validate_dry_run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[3]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))

sys.path.insert(0, str(_HERE))
import emit_configs  # noqa: E402  复用同目录发射器的真源装载与校验函数

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

LOG_PATH = _HERE / "dry_run_validation.log"
VERDICT_PATH = _HERE / "dry_run_verdict.json"
_LINES: list[str] = []


def out(msg: str = "") -> None:
    print(msg)
    _LINES.append(msg)


def main() -> int:
    axes, _schema = emit_configs.load_schema_axes()
    roster = emit_configs._load_yaml(emit_configs.ROSTER_PATH)
    cfg_dir = _HERE / "grid_configs"
    verdict: dict = {"checks": [], "surfaces": {}}
    ok = True

    metas = sorted(cfg_dir.glob("*.meta.yaml"))
    out(f"=== F道 干跑验证 @ {__import__('time').strftime('%Y-%m-%dT%H:%M:%S')} ===")
    out(f"配置目录: {cfg_dir}  meta 数={len(metas)}")
    for m in metas:
        meta = yaml.safe_load(m.read_text(encoding="utf-8"))
        name = meta["family"]
        jpath = cfg_dir / meta["subspace_file"]
        sub = json.loads(jpath.read_text(encoding="utf-8"))
        rec: dict = {"family": name, "subspace_file": jpath.name}

        # V1 结构/合法性
        v1 = isinstance(sub, dict) and all(
            isinstance(k, str) and isinstance(v, list) and v and all(isinstance(x, str) for x in v)
            for k, v in sub.items()
        )
        bad_axes = [k for k in sub if k not in axes]
        bad_vals = {k: [x for x in v if x not in axes.get(k, [])] for k, v in sub.items() if k in axes}
        bad_vals = {k: v for k, v in bad_vals.items() if v}
        v1 = v1 and not bad_axes and not bad_vals
        rec["V1_schema_legal"] = v1
        rec["V1_bad_axes"] = bad_axes
        rec["V1_bad_values"] = bad_vals

        # V2 计数一致（GridCompiler 只读编译，零 DB/GPU）
        cells = emit_configs.count_cells(sub)
        rec["V2_cells"] = cells
        rec["V2_matches_meta"] = cells == int(meta["expected_cells"])

        # V3 预算钳制（执行器原函数，冻结册真源）
        try:
            import factory_grid_executor as fge

            n = fge._apply_prereg_budget("", cells)
            rec["V3_clamped_n"] = n
            rec["V3_budget_ok"] = n >= cells
        except SystemExit as exc:
            rec["V3_budget_ok"] = False
            rec["V3_error"] = str(exc)
        row_ok = v1 and rec["V2_matches_meta"] and rec.get("V3_budget_ok", False)
        rec["row_ok"] = row_ok
        ok = ok and row_ok
        verdict["checks"].append(rec)
        out(
            f"[{name}] V1={'PASS' if v1 else 'FAIL'} V2={cells}格(核{'PASS' if rec['V2_matches_meta'] else 'FAIL'}) "
            f"V3={'PASS' if rec.get('V3_budget_ok') else 'FAIL'} -> {'PASS' if row_ok else 'FAIL'}"
        )

    # V4 执行器只读对账尺（--verify-counts 禁写）
    out("--- V4 factory_grid_executor --verify-counts（只读对账尺） ---")
    p = run_subprocess_hidden(
        [sys.executable, str(_REPO / "scripts" / "backtest" / "factory_grid_executor.py"), "--verify-counts"],
        timeout=300,
        cwd=str(_REPO),
    )
    tail = "\n".join((p.stdout or "").strip().splitlines()[-12:])
    out(tail or "(no stdout)")
    if p.stderr.strip():
        out("[stderr] " + p.stderr.strip()[:400])
    verdict["surfaces"]["verify_counts"] = {
        "rc": p.returncode,
        "note": "台账对账（历史批缺口=数据治理项，非本批配置合法性判据）",
    }
    out(f"V4 rc={p.returncode}（留痕参考，不阻断配置合法性）")

    # V5 E0 问闸预演（只读 check）
    out("--- V5 compute_window_gate check --purpose f06_grid_batch（只读预演） ---")
    p = run_subprocess_hidden(
        [
            sys.executable,
            str(_REPO / "scripts" / "backtest" / "compute_window_gate.py"),
            "check",
            "--purpose",
            "f06_grid_batch",
            "--compute-class",
            "local_gpu",
        ],
        timeout=120,
        cwd=str(_REPO),
    )
    out((p.stdout or "").strip()[:600])
    verdict["surfaces"]["window_gate"] = {"rc": p.returncode, "stdout_head": (p.stdout or "")[:400]}
    out(f"V5 rc={p.returncode}（0=当前窗放行 3=当前窗拒；真点火由执行器 E0 在发车时刻再问）")

    # V6 启动器 dry-run 预演（门检快照，零 GPU）
    out("--- V6 fire_grid.py dry-run 预演 ---")
    p = run_subprocess_hidden([sys.executable, str(_HERE / "fire_grid.py")], timeout=300, cwd=str(_HERE))
    out((p.stdout or "").strip()[-2000:])
    verdict["surfaces"]["fire_dry_run"] = {"rc": p.returncode}

    verdict["all_config_checks_pass"] = ok
    VERDICT_PATH.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG_PATH.write_text("\n".join(_LINES) + "\n", encoding="utf-8")
    out(f"=== 干跑结论: {'PASS' if ok else 'FAIL'} ===")
    out(f"日志: {LOG_PATH}")
    out(f"判决: {VERDICT_PATH}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
