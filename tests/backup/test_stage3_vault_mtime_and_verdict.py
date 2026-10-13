# [MODULE] tests.backup.test_stage3_vault_mtime_and_verdict
# [TTL] task_bound
# [STARTUP] on_demand_test（仅 pytest 触发，零 scheduled_task）
# [CONSUMERS] pytest；案卷 docs/_working/total_command_closeout/wave4/dr_chain_report.md §4.2/§4.3
#   （mtime/只读位那一半的常驻尺＝tests/data/dr/test_backup_copy_share.py，本文件不再复刻）
# [DOMAIN] D_INFRA_RUNTIME
# [BLUEPRINT] MOD-TEST-STAGE3-VAULT | docs/_working/total_command_closeout/wave4/dr_chain_report.md | §4.2
# [DEPENDENCIES] scripts/backup/backup.ps1 (STAGE 3 判据行 + STAGE 4 state 键面), powershell
# [MATURITY] n/a
# [MODIFY-GUARD] none（只读校验/生成器，无状态写盘）
# [STABILITY] stable
# [SAFETY] n/a
# [AI_AUTONOMY] n/a
# [ERROR_CONTRACT] n/a
# [TESTS] n/a
# [INVARIANTS] 被测判据从 scripts/backup/backup.ps1 **原文抽取**后执行（禁复刻第二套判据）；
#   真值表钉的是 shipped 语义，不是"设计意图"——改判据必先改本表并同步消费方
#   scripts/ch/rolling_archive_reconciler.py（硬判 last_backup_status != ok 才放行轮转）与
#   scripts/backup/backup_daily_trigger.ps1（SLO 只认 ok/failed）；
#   全程只写 pytest tmp_path，禁触 F:/G: 真实备份盘；禁任何删除动作；只读探测
"""P-27/X-17 灾备逐件失败口径的回归网（波 4.2/4.3 → 维护六班第 13 条对齐 shipped）。

大白话：夜间备份给 30 多万个文件拍快照，"有一个文件没搬成"到底该把整轮判成
失败还是判成"交付了但带伤"，2026-09 那批测册是按**当时写好的脚本**立的尺；
那版脚本死在队列里从没入库，而盘上真跑的脚本随后用另外三条路把同一个病治了
（见下"实况"），于是这 9 支尺一直红着——红的不是生产，是尺指向了一个不存在的函数。
本文件按 Owner 令三 v2 第 13 条的第二条路（从未存在→改测册对齐真实键集）重写。

实况（三证，全部实测可复核）
----------------------------
1. 测册由 88890cb6801（2026-09-30）入库；配套脚本腿＝队列 blob
   d882e1314ade9ab70d0cf6ecc5028e327e881d3bce8f6437280125804c831e00（63,276 B，带
   Set-VaultMtime/$structural/last_backup_partial_items），被 ≥9 只死信携带，
   对 backup.ps1 全史 45 版逐版 sha256 比对**零命中**＝从未落地。
2. 该腿要治的病已被后续三件治掉/拆走：
   - 只读位源使 mtime 写回炸 → H04 `Copy-FileShareTolerant`（cad41feb2f 09-29）
     从复制层断根；覆盖收编在常驻尺 tests/data/dr/test_backup_copy_share.py，
     本文件不再复刻（净零：同域重复簇收敛唯一）。
   - 瞬态逐件失败一票否决 → E-2 `source_missing`（10-09）、E-6 `share_locked`
     （10-09，注释自证历史 vault 失败里 15/17 属此类）、`vanished`（09-15）三条
     通道已被逐条摘出 `$linkFail`；残差 `$linkFail` 按构造＝结构性。
3. `partial` 档与 wave-4 四键从未落地，且 `registration_needs.yaml` W4-R3 至今
   把它们挂在"键名须先登记再被读"。

代价面（落这条路的代价，在册）
------------------------------
- 若日后出现**第四类**未被摘出的瞬态失败，整轮仍会被判 failed（过度报警方向，
  非静默）；本表的 `test_wave4_partial_state_keys_stay_consistent_with_consumers`
  会在"落了键却没落消费方"时报警，反向漂移有尺。
- 救回旧腿＝给 `last_backup_status` 引入 partial 且 overall 仍为 ok ⇒
  `rolling_archive_reconciler.py:121` 的 `!= "ok"` 轮转闸放行、日检 SLO 不再报警
  ＝弱化判据，本班不做，交备份线按 W4-R3 定策。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT  # SSoT：本文件原自算 parents[N]，与 canonical 等值

PS1 = REPO_ROOT / "scripts" / "backup" / "backup.ps1"

pytestmark = pytest.mark.skipif(not PS1.exists(), reason="backup.ps1 absent")

# wave-4（dr_chain_report §4.3）设计过但从未落地的 state 键
WAVE4_UNSHIPPED_STATE_KEYS = (
    "last_backup_partial_items",
    "last_code_backup_snapshot_mode",
)
# 落这些键时必须一起改的消费方（"键名先登记再被读"，W4-R3）
WAVE4_CONSUMER = "scripts/backup/backup_reconciler.py"


def _ps_text() -> str:
    return PS1.read_text(encoding="utf-8")


def _extract_veto_line() -> str:
    """抽 shipped 整轮判据行；抽不到＝判据被改名/删除＝本尺红。"""
    m = re.search(r"(?m)^\s*(\$vaultOk = .*)$", _ps_text())
    assert m, "shipping backup.ps1 lost the $vaultOk aggregate verdict line"
    return m.group(1).strip()


def _stage4_block() -> str:
    head = "# ==================== STAGE 4: Report"
    assert head in _ps_text(), "shipping backup.ps1 lost the STAGE 4 report section"
    return _ps_text()[_ps_text().index(head) :]


def _run_ps(tmp_path: Path, body: str) -> str:
    script = tmp_path / "probe.ps1"
    script.write_text(body, encoding="utf-8")
    res = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert res.returncode == 0, f"powershell failed rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res.stdout


@pytest.mark.parametrize(
    ("rc", "link_fail", "want"),
    [
        (16, 0, "failed"),  # robocopy 硬错＝整轮没交付
        (8, 0, "failed"),  # robocopy 有文件失败＝结构性
        (0, 0, "ok"),
        (0, 1, "failed"),  # 残差逐件失败＝按构造属结构性，一票否决是有意保留
        (0, 100, "failed"),  # 逐件全失败＝整轮没交付
        (7, 0, "ok"),  # rc<8 的 INFO 档不否决
    ],
)
def test_vault_verdict_matrix(tmp_path: Path, rc: int, link_fail: int, want: str) -> None:
    """真值表跑在**抽取的 shipped 判据**上：钉现状，不钉设计意图。"""
    body = f"""
$rcCode={rc}; $linkFail={link_fail}
{_extract_veto_line()}
$out = if ($vaultOk) {{ 'ok' }} else {{ 'failed' }}
Write-Output ("VERDICT=" + $out)
"""
    out = _run_ps(tmp_path, body)
    assert f"VERDICT={want}" in out, out


def test_transient_channels_stay_out_of_the_veto() -> None:
    """三条瞬态通道（vanished/share_locked/source_missing）必须仍不进否决式。

    病根复现守卫：2026-09-26 一轮 336,678 件里 1 件失败就把整轮判 failed。治本
    口径是把瞬态逐条摘出 `$linkFail`；谁把它们塞回否决式＝新一轮过度报警，本尺红。
    """
    line = _extract_veto_line()
    assert "$rcCode" in line and "$linkFail" in line, line
    for transient in ("$vanished", "$shareLocked", "source_missing"):
        assert transient not in line, f"transient channel {transient} re-entered the veto: {line}"
    stage3 = _ps_text()
    for carved in ("$vanished++", "$shareLocked++"):
        assert carved in stage3, f"{carved} gone -- a transient class lost its carve-out"


def test_stage4_state_keys_match_shipped_set() -> None:
    """STAGE 4 汇总：否决谓词只认 failed，state 键面 = shipped 真键集（E-5 三分）。"""
    stage4 = _stage4_block()
    assert '-eq "failed"' in stage4, "aggregate veto must stay keyed on failed only"
    for key in ("last_backup_status", "last_attempt_status", "last_success_status"):
        # 精确到 Add-Member 位，不用裸子串——"改名成 last_attempt_status_renamed"
        # 仍含裸子串，会让本尺假绿（红证实测过一次）。
        assert f"-NotePropertyName {key} -NotePropertyValue" in stage4, (
            f"backup_state.json key {key} renamed or dropped"
        )
    # code_backup 的可解释性字段（分因通道）必须在，否则 failed 无法归因
    for field in ("failures=$linkFail", "vanished=$vanished", "share_locked=$shareLocked"):
        assert field in _ps_text(), f"code_backup lost interpretability field {field}"


def test_wave4_partial_state_keys_stay_consistent_with_consumers() -> None:
    """wave-4 四键若被落地，必须与消费方同批——防"键名漂移"复发（W4-R3）。

    现状＝键不在脚本里（本班按实测判定）；若备份线日后落 partial 档，本尺要求
    `backup_reconciler.py` 同步读该键，否则"写了没人读"＝新的静默失真。
    """
    text = _ps_text()
    shipped = [k for k in WAVE4_UNSHIPPED_STATE_KEYS if k in text]
    if not shipped:
        return
    consumer = (REPO_ROOT / WAVE4_CONSUMER).read_text(encoding="utf-8")
    unread = [k for k in shipped if k not in consumer]
    assert not unread, (
        f"{WAVE4_CONSUMER} must read the state keys it depends on; unread: {unread} "
        "(see docs/_working/total_command_closeout/wave4/registration_needs.yaml W4-R3)"
    )
