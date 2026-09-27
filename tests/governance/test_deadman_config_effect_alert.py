# [A_test] module_id: MOD-GOV_deadman_config_effect_alert | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/boot_autostart_architecture.md | §deadman 读取面
# [MODULE] tests.governance.test_deadman_config_effect_alert
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_deadman_config_effect_alert.py — deadman 读取 ConfigCheck 判决的配对回归（F132 治本 2026-09-27）。

病根：ZephyrAlpha_ConfigCheck 每日 08:05 真报 mismatch 退 exit 1（09-27 实测 308 条），
但判决只落 data/failures 人读面 + tmp 报告文件，无自动消费腿——"跑了且报了，没人听"。
治本=挂进既有 deadman 一次性哨兵（只读他人写的报告，判据单源在 config_effect_checker.py）。
本尺锁住这条腿：删掉 deadman 的 config_effect 段 → RED 测试立即红。

全部经 DEADMAN_TMP_DIR 注入 tmp_path（宪法 §9-6 测试隔离，不触生产 tmp/）。
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "deadman_switch.ps1"


def _run_deadman(tmp_dir: Path) -> subprocess.CompletedProcess[str]:
    env = {"DEADMAN_TMP_DIR": str(tmp_dir)}
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        env={**__import__("os").environ, **env},
    )


def _seed(tmp_dir: Path, report: dict | None) -> None:
    """fresh heartbeats（静音三条服务腿）+ 指定 config_effect 报告。"""
    now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for name in ("scheduler", "tick_subscriber", "ch_health_probe"):
        (tmp_dir / f"{name}.heartbeat").write_text(f"{now_s}|test\n", encoding="utf-8")
    # 盘中 biz 腿在测试机多半非交易时段跳过；保险给一个新鲜件
    biz = {"last_tick_ts": now_s, "is_trading_day": False, "today_rows": 0, "resub_count": 0}
    (tmp_dir / "tick_subscriber_biz.heartbeat").write_text(json.dumps(biz), encoding="utf-8")
    live = {"ts": now_s, "is_trading_day": False, "running": True}
    (tmp_dir / "live_strategy_biz.heartbeat").write_text(json.dumps(live), encoding="utf-8")
    target = tmp_dir / "config_effect_check_report.json"
    if report is None:
        target.unlink(missing_ok=True)
    else:
        target.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")


def _alert_text(tmp_dir: Path) -> str:
    log = tmp_dir / "deadman_switch_alerts.log"
    return log.read_text(encoding="utf-8") if log.exists() else ""


def test_mismatch_report_triggers_config_effect_alert(tmp_path: Path) -> None:
    """红样：status=mismatch 的报告必须产生 config_effect_check 告警行。"""
    _seed(
        tmp_path,
        {
            "status": "mismatch",
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "summary": "不一致（308 条）",
        },
    )
    r = _run_deadman(tmp_path)
    assert r.returncode == 0, r.stderr[-300:]
    text = _alert_text(tmp_path)
    assert "config_effect_check: MISMATCH" in text, text or "(alert log 缺失=读取腿断了)"


def test_ok_report_triggers_no_config_effect_alert(tmp_path: Path) -> None:
    """绿样：status=ok 不得产生任何 config_effect 告警（无假红）。"""
    _seed(
        tmp_path, {"status": "ok", "checked_at": datetime.now().isoformat(timespec="seconds"), "summary": "一致（绿）"}
    )
    r = _run_deadman(tmp_path)
    assert r.returncode == 0, r.stderr[-300:]
    assert "config_effect_check" not in _alert_text(tmp_path)


def test_same_verdict_alerts_once_only(tmp_path: Path) -> None:
    """冷却：同一判决（status+checked_at 签名不变）连跑两次只告警一次，5min 节奏不刷屏。"""
    report = {"status": "mismatch", "checked_at": "2026-09-27T08:05:06+08:00", "summary": "s"}
    _seed(tmp_path, report)
    _run_deadman(tmp_path)
    _seed(tmp_path, report)  # 心跳重新 fresh（防第二跑混入他腿），报告同签名
    _run_deadman(tmp_path)
    assert _alert_text(tmp_path).count("config_effect_check: MISMATCH") == 1


def test_missing_report_alerts_fail_closed_after_live(tmp_path: Path) -> None:
    """fail-closed：通道曾出过告警（sig 在册）后报告消失 → MISSING 告警不得静默。"""
    report = {"status": "mismatch", "checked_at": "2026-09-27T08:05:06+08:00", "summary": "s"}
    _seed(tmp_path, report)
    _run_deadman(tmp_path)  # 首红 → 落 sig
    _seed(tmp_path, None)  # 报告消失（任务被停/tmp 被清）
    _run_deadman(tmp_path)
    assert "config_effect_check: report MISSING" in _alert_text(tmp_path)


def test_missing_report_before_first_alert_is_silent(tmp_path: Path) -> None:
    """从未上线（无 sig）时报告缺席=特征缺席非故障：不告警，且外来测试沙盒日志保持干净。"""
    _seed(tmp_path, None)
    _run_deadman(tmp_path)
    assert "config_effect_check" not in _alert_text(tmp_path)
