# [BLUEPRINT] MOD-INF-043 | docs/_working/cold_backup_automation/00_master_plan.md | §5
# [MODULE] scripts.ch.rolling_archive_reconciler
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] scripts.ch.archiver; zephyr.infrastructure.database_service(经archiver HTTP通道)
# [CONSUMERS] backup.ps1(备份成功钩子); GitCommitGateway._reconciliation_registry(事件挂载预留)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 参数真源=契约§rolling_archive禁码内第二真源 | 五重安全阀顺序不可换缺一即跳 | 归档线=保留期+1月滞回 | 批限量≤3分区且≤30G | 连续3分区失败熔断 | kill旗一键回退手动 | shadow只读禁drop
# [MODIFY-GUARD] gate_id="ROLLING-ARCHIVE-RECONCILER"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一安全阀失败→跳过本批(不抛); 熔断开启→拒绝执行; 契约缺失→拒绝启动
# [TESTS] tests/scripts/ch/test_rolling_archive_reconciler.py
# [A_module] module_id=MOD-INF-043-RA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rolling_archive_reconciler.py — 滚动归档事件触发器（备份成功事件链，禁 cron）。

大白话：早上备份成功后，机器看一眼"有没有整月的旧行情满保留期了"——有就先抄两份
（F 冷库主库 + G 镜像）、逐行核对无误，才删掉热库里那份原件。数据本身永远在冷库躺着。

三档模式（裁定#380⑤：同日全流程试跑）：
  shadow    只读：列出过线分区生成计划单，不 export 不 drop
  semi      计划单 + --confirm 确认后执行（搬前确认流）
  full_auto 五重安全阀全自动（kill 旗/熔断可随时一键回退手动）

五重安全阀（顺序不可换，缺一即跳过本批）：备份新鲜→export→verify→第二副本→批限量。
触发事件：backup.ps1 成功收尾钩子（每日 06:00 兜底 + post-commit 备份链），
不新增任何 schtasks/Timer/sleep-loop（宪法红线；backup_daily_trigger.ps1 为合法先例）。

Usage::

    python scripts/ch/rolling_archive_reconciler.py --mode shadow
    python scripts/ch/rolling_archive_reconciler.py --mode semi --confirm
    python scripts/ch/rolling_archive_reconciler.py --mode full_auto
    python scripts/ch/rolling_archive_reconciler.py --kill      # 一键回退手动
    python scripts/ch/rolling_archive_reconciler.py --resume    # 熔断复位
    python scripts/ch/rolling_archive_reconciler.py --mode full_auto --inject-backup-failure   # 红蓝注入
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))
from zephyr.shared.io.paths import PROJECT_ROOT  # canonical SSoT（禁本地重定义）

sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "ch"))

import archiver  # noqa: E402  同目录唯一通道复用（export/verify/drop 现成函数）

CONTRACT_FILE = (
    PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "data_retention_contract.yaml"
)
BACKUP_STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state.json"
STATE_FILE = PROJECT_ROOT / "data" / "databases" / "rolling_archive_state.json"
PLAN_DIR = PROJECT_ROOT / "docs" / "_working" / "disk_reorg_campaign"  # 预检单落点
SHADOW_PLAN_FILE = PROJECT_ROOT / "data" / "audit-trail" / "rolling_archive_plan_shadow.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rolling_archive")

__all__ = [
    "load_contract_params",
    "load_state",
    "update_state",
    "list_past_line_partitions",
    "evaluate",
    "build_parser",
    "main",
]


def load_contract_params() -> dict[str, Any]:
    """从契约 §rolling_archive 加载参数（INV-RET-006：真源=契约，禁码内第二真源）。"""
    with open(CONTRACT_FILE, encoding="utf-8") as f:
        contract = yaml.safe_load(f) or {}
    params = contract.get("rolling_archive")
    if not params:
        raise RuntimeError(f"契约缺失 §rolling_archive（{CONTRACT_FILE}）——滚动归档拒绝启动")
    return params


def load_state() -> dict[str, Any]:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"consecutive_failures": 0, "kill_switch": False}


def update_state(**kwargs: Any) -> None:
    state = load_state()
    state.update(kwargs)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _backup_fresh(inject_backup_failure: bool = False) -> tuple[bool, str]:
    """安全阀1：当日备份 ok 且 CH 阶段 ok（备份新鲜是归档第一道阀，非可选项）。"""
    if inject_backup_failure:
        return False, "注入：备份失败（红蓝演练）"
    try:
        with open(BACKUP_STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False, "backup_state.json 不可读"
    if st.get("last_backup_status") != "ok":
        return False, f"last_backup_status={st.get('last_backup_status')}"
    if st.get("last_ch_backup_status") != "ok":
        return False, f"last_ch_backup_status={st.get('last_ch_backup_status')}"
    ts = st.get("last_backup_time")
    if ts:
        try:
            last = datetime.fromisoformat(ts)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            age_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600
            if age_h > 36:
                return False, f"备份陈旧 {age_h:.0f}h (>36h)"
        except (ValueError, TypeError):
            return False, "last_backup_time 损坏"
    return True, "backup ok(含 CH)"


def list_past_line_partitions(params: dict[str, Any]) -> list[dict[str, Any]]:
    """列出过线分区：完整月分区且 partition_end < 今天-(保留期+滞回)。只读。"""
    import http.client

    import zephyr.data.ch_config as ch_cfg
    from zephyr.shared.security.secrets import get_secret_or_default

    ch_cfg.ensure_ch_env_loaded()
    host = get_secret_or_default("CLICKHOUSE_HOST", "")
    port = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))
    user = get_secret_or_default("CLICKHOUSE_USER", "default")
    pwd = get_secret_or_default("CLICKHOUSE_PASSWORD", "")

    def q(sql: str) -> str:
        conn = http.client.HTTPConnection(host, port, timeout=120)
        conn.request("POST", "/", body=sql, headers={"X-ClickHouse-User": user, "X-ClickHouse-Key": pwd})
        r = conn.getresponse()
        data = r.read().decode("utf-8", "replace")
        conn.close()
        if r.status != 200:
            raise RuntimeError(f"CH {r.status}: {data[:300]}")
        return data

    lines = params.get("retention_lines_months", {})
    hysteresis = int(params.get("hysteresis_months", 1))
    excluded = set(params.get("excluded_tables", []))
    today = datetime.now()
    now_month_index = today.year * 12 + (today.month - 1)  # 月数计数

    def _cutoff_yyyymm(keep_months: int) -> int:
        idx = now_month_index - keep_months - hysteresis
        return (idx // 12) * 100 + (idx % 12) + 1  # 还原为 YYYYMM 整数

    candidates: list[dict[str, Any]] = []
    parts = q(
        "SELECT database, table, partition, sum(rows), sum(bytes_on_disk) "
        "FROM system.parts WHERE active AND database IN ('c1_market','c3_fundamental') "
        "GROUP BY database, table, partition FORMAT TSV"
    )
    seen: dict[tuple[str, str], list[tuple[str, int, int]]] = {}
    for line in parts.splitlines():
        db, table, part, rows, bytes_ = line.split("\t")
        if table in excluded or table not in lines:
            continue
        seen.setdefault((db, table), []).append((part, int(rows), int(bytes_)))
    for (db, table), plist in seen.items():
        keep_months = int(lines[table])
        cutoff = _cutoff_yyyymm(keep_months)
        for part, rows, bytes_ in plist:
            ym = _partition_end_ym(part)
            if ym is None or ym >= cutoff:  # 非完整月分区或未过线→跳过
                continue
            candidates.append(
                {
                    "database": db,
                    "table": table,
                    "partition": part,
                    "rows": rows,
                    "bytes_on_disk": bytes_,
                    "line_months": keep_months,
                    "hysteresis_months": hysteresis,
                }
            )
    candidates.sort(key=lambda c: (c["table"], c["partition"]))
    return candidates


def _partition_end_ym(partition: str) -> int | None:
    """解析分区串为 YYYYMM 整数；元组/非月分区返回 None（只动完整月分区）。"""
    p = partition.strip().strip("'").replace("\\", "")
    if not p.isdigit() or len(p) not in (6, 8):
        return None
    ym = int(p[:6])
    return ym


def _second_copy(src: Path, mirror_root: Path, rel: Path) -> tuple[bool, str]:
    """安全阀4：第二副本落 G 镜像并核验（size 全等+首中尾三段 sha256 抽检）。"""
    dst = mirror_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if src.stat().st_size != dst.stat().st_size:
        return False, f"size mismatch {src.stat().st_size} != {dst.stat().st_size}"
    for offset in (0, max(0, src.stat().st_size // 2), max(0, src.stat().st_size - (1 << 20))):
        h1 = _chunk_sha256(src, offset)
        h2 = _chunk_sha256(dst, offset)
        if h1 != h2:
            return False, f"sha256 抽检不符 @offset={offset}"
    return True, f"mirrored -> {dst}"


def _chunk_sha256(path: Path, offset: int, length: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(offset)
        h.update(f.read(length))
    return h.hexdigest()


def _plan_batch(params: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    """筛选过线分区并按批限量（≤N 分区且 ≤M 字节）截批。"""
    candidates = list_past_line_partitions(params)
    max_parts = int(params.get("batch_max_partitions", 3))
    max_bytes = int(params.get("batch_max_bytes", 30_000_000_000))
    batch: list[dict[str, Any]] = []
    total = 0
    for c in candidates:
        if len(batch) >= max_parts or total + c["bytes_on_disk"] > max_bytes:
            result["skipped"].append({**c, "reason": "批限量（留下一事件）"})
            continue
        batch.append(c)
        total += c["bytes_on_disk"]
    result["candidates_total"] = len(candidates)
    result["batch"] = batch
    result["batch_bytes"] = total
    return batch


def _execute_partition(
    c: dict[str, Any], params: dict[str, Any], inject_verify_mismatch: bool, fails: int
) -> tuple[str, int, str | None]:
    """执行单分区五阀链，返回 (结果描述, 新失败计数, 熔断标记)。"""
    db, table, part = c["database"], c["table"], c["partition"]
    qualified = f"{db}.{table}"  # archiver 全部 API 吃 db.table 全称（manifest 同口径）
    # period 仅用于元组分区表（technical_indicator 族）；本处候选全部为 yyyymm 数字
    # 分区（元组分区串已在 list 阶段被 _partition_end_ym 排除），恒传 None——
    # archiver._require_period 对非元组表传 period 会硬拒。
    period = None
    breaker_failures = int(params.get("circuit_breaker_failures", 3))
    try:
        if inject_verify_mismatch:
            fails += 1
            update_state(consecutive_failures=fails)
            if fails >= breaker_failures:
                update_state(circuit_open=True)
                return "verify_mismatch(注入)——拒绝 drop，记失败", fails, "熔断开启（注入触发）"
            return "verify_mismatch(注入)——拒绝 drop，记失败", fails, None
        pq = archiver.export_partition(qualified, part, period=period)
        if pq is None or not pq.exists() or not archiver.verify_partition(qualified, part, pq, period=period):
            if pq is not None and pq.exists():
                pq.unlink()
            raise RuntimeError("export/verify 未通过——残件已清")
        rows = archiver._parquet_rows(pq)
        ch_size = archiver._ch_partition_size_bytes(qualified, part, period=period)
        mirror_root = Path(params.get("mirror_root", "G:/zephyr_cold/60_mirror/zephyr_cold_archive"))
        ok2, msg2 = _second_copy(pq, mirror_root, pq.relative_to(archiver.ARCHIVE_ROOT))
        if not ok2:
            raise RuntimeError(f"第二副本未过: {msg2}")
        if not archiver.drop_partition(qualified, part, period=period):
            raise RuntimeError("drop 未成功")
        archiver._append_manifest(
            archiver._manifest_record(
                qualified, part, pq, dropped=True, period=period, rows=rows, ch_size_bytes=ch_size
            )
        )
        return f"archived+dropped; {msg2}", 0, None
    except Exception as e:  # noqa: BLE001 — 任一失败该分区记 retry，连续失败熔断
        fails += 1
        update_state(consecutive_failures=fails)
        circuit = "熔断开启（连续 3 分区失败）" if fails >= breaker_failures else None
        if circuit:
            update_state(circuit_open=True)
        return f"failed: {e}", fails, circuit


def evaluate(
    mode: str, confirm: bool = False, inject_backup_failure: bool = False, inject_verify_mismatch: bool = False
) -> dict[str, Any]:
    """主评估：安全阀→计划→（按档位）执行。返回结构化结果供台账/回执。"""
    params = load_contract_params()
    state = load_state()
    result: dict[str, Any] = {
        "mode": mode,
        "ts": datetime.now().isoformat(),
        "candidates": [],
        "executed": [],
        "skipped": [],
        "valve1": None,
        "circuit": None,
    }

    if state.get("kill_switch"):
        result["valve1"] = "kill"
        result["note"] = "kill_switch 置位——一键回退手动模式，整批跳过"
        return result
    if state.get("circuit_open"):
        result["valve1"] = "circuit_open"
        result["note"] = "熔断开启（连续失败≥阈值）——需 --resume 人工复位"
        return result

    ok, why = _backup_fresh(inject_backup_failure)
    result["valve1"] = f"{'PASS' if ok else 'SKIP'}: {why}"
    if not ok:
        return result  # 整批跳过，次日再评

    batch = _plan_batch(params, result)
    if not batch:
        result["note"] = "无过线分区或全被批限量挡下"
        return result

    if mode == "shadow":
        PLAN_DIR.mkdir(parents=True, exist_ok=True)
        plan = SHADOW_PLAN_FILE
        with open(plan, "a", encoding="utf-8") as f:
            for c in batch:
                f.write(json.dumps({"ts": result["ts"], **c}, ensure_ascii=False) + "\n")
        result["plan_file"] = str(plan)
        result["note"] = f"shadow：计划单已写 {len(batch)} 分区（只读，未 export 未 drop）"
        return result

    if mode == "semi" and not confirm:
        result["note"] = f"semi：{len(batch)} 分区待确认——加 --confirm 执行（搬前确认流）"
        return result

    fails = int(state.get("consecutive_failures", 0))
    for c in batch:
        desc, fails, circuit = _execute_partition(c, params, inject_verify_mismatch, fails)
        result["executed"].append({**c, "result": desc})
        if circuit:
            result["circuit"] = circuit
            break
    return result


def vhdx_precheck(notify_only: bool = True) -> dict[str, Any]:
    """vhdx 季度压缩预检单（裁定#380④：只提醒不执行，实际压缩等 Owner 点名）。

    随备份成功事件运行（backup.ps1 STAGE 4b 同窗）；触发条件=季初首 7 天内
    或距上次成功压缩 ≥90 天。输出=预检单 md（五项指标）+控制台提醒一行，
    绝不自动停机/压缩。
    """
    import subprocess

    today = datetime.now()
    quarter_start_month = (today.month - 1) // 3 * 3 + 1
    in_quarter_start = today.day <= 7 and today.month == quarter_start_month
    state_ = load_state()
    last_comp = state_.get("last_vhdx_compaction")  # ISO 日期串，无=从未记录
    days_since = None
    if last_comp:
        try:
            days_since = (today - datetime.fromisoformat(last_comp)).days
        except (ValueError, TypeError):
            days_since = None
    due = in_quarter_start or (days_since is None or days_since >= 90)

    precheck: dict[str, Any] = {
        "date": today.isoformat(),
        "due": due,
        "in_quarter_start_window": in_quarter_start,
        "days_since_last_compaction": days_since,
    }
    if not due:
        return precheck

    # 五项指标（只读采集）
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded
        from zephyr.shared.security.secrets import get_secret_or_default

        ensure_ch_env_loaded()
        host = get_secret_or_default("CLICKHOUSE_HOST", "")
        port = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))
        user = get_secret_or_default("CLICKHOUSE_USER", "default")
        pwd = get_secret_or_default("CLICKHOUSE_PASSWORD", "")
        conn = http.client.HTTPConnection(host, port, timeout=60)
        conn.request(
            "POST",
            "/",
            body=(
                "SELECT round(free_space/1e9,1), round(total_space/1e9,1) FROM system.disks "
                "WHERE name='default' FORMAT TSV"
            ),
            headers={"X-ClickHouse-User": user, "X-ClickHouse-Key": pwd},
        )
        r = conn.getresponse()
        free_gb, total_gb = r.read().decode().strip().split("\t")
        conn.close()
        precheck["vm_internal_free_gb"] = float(free_gb)
        precheck["vm_internal_total_gb"] = float(total_gb)
    except Exception as e:  # noqa: BLE001
        precheck["vm_internal_free_gb"] = f"采集失败: {e.__class__.__name__}"

    try:
        out = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                '(Get-VHD -Path "D:\\HyperV\\VMs\\zephyr-ch\\data.vhdx").FileSize/1GB',
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        precheck["vhdx_size_gb"] = round(float(out.stdout.strip()), 1)
    except Exception:  # noqa: BLE001
        precheck["vhdx_size_gb"] = "采集失败(需管理员)"

    precheck["backup_fresh"] = _backup_fresh()[1]
    precheck["note"] = "提醒条目——绝不自动执行压缩；实际停机压缩等 Owner 点名（裁定#380④/#381）"

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    precheck_file = PLAN_DIR / f"vhdx_precheck_{today.strftime('%Y%m%d')}.md"
    with open(precheck_file, "w", encoding="utf-8") as f:
        f.write("---\nttl: task_bound\n---\n# vhdx 季度压缩预检单（自动生成·提醒条目）\n\n```json\n")
        f.write(json.dumps(precheck, ensure_ascii=False, indent=1))
        f.write("\n```\n\n五项全绿时呈 Owner 点名压缩（停机 60-120 分钟窗，全局冻结档）。\n")
    precheck["precheck_file"] = str(precheck_file)
    print(f"[vhdx-precheck] 到期提醒：预检单已生成 {precheck_file}（仅提醒，不执行）")
    return precheck


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="滚动归档 reconciler（备份成功事件链）")
    p.add_argument("--mode", choices=["shadow", "semi", "full_auto"], default="shadow")
    p.add_argument("--confirm", action="store_true", help="semi 档确认执行")
    p.add_argument("--kill", action="store_true", help="一键回退手动模式")
    p.add_argument("--resume", action="store_true", help="熔断复位+解除 kill")
    p.add_argument("--precheck", action="store_true", help="vhdx 季度压缩预检单（提醒条目，不执行）")
    p.add_argument("--inject-backup-failure", action="store_true", help="红蓝注入：伪造备份失败")
    p.add_argument("--inject-verify-mismatch", action="store_true", help="红蓝注入：伪造对账不符")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.kill:
        update_state(kill_switch=True)
        print("kill_switch=true —— 已回退手动模式")
        return 0
    if args.resume:
        update_state(kill_switch=False, circuit_open=False, consecutive_failures=0)
        print("kill/circuit 已复位")
        return 0
    if args.precheck:
        print(json.dumps(vhdx_precheck(), ensure_ascii=False, indent=1))
        return 0
    result = evaluate(
        args.mode,
        confirm=args.confirm,
        inject_backup_failure=args.inject_backup_failure,
        inject_verify_mismatch=args.inject_verify_mismatch,
    )
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  真实触发载体=backup.ps1 STAGE 4b 备份成功事件钩子（裁定#387），manual CLI 仅供演练与巡检
    raise SystemExit(main())
