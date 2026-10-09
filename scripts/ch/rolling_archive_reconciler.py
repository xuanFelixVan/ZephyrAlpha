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


CH_BACKUP_MAX_AGE_H = 26  # CH 段 24h 节律 + 2h  slack
BACKUP_CONFIG_FILE = PROJECT_ROOT / "scripts" / "backup" / "backup_config.yaml"
VHDX_GROWTH_SERIES = PROJECT_ROOT / "data" / "audit-trail" / "vhdx_growth_series.jsonl"


def _load_backup_state() -> dict[str, Any]:
    try:
        with open(BACKUP_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _age_hours(ts: Any) -> float | None:
    if not ts:
        return None
    try:
        last = datetime.fromisoformat(str(ts))
    except (TypeError, ValueError):
        return None
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last).total_seconds() / 3600


def _ch_newest_backup_created_age_h() -> tuple[float | None, str]:
    """读 CH 服务端 system.backups 最近一条 BACKUP_CREATED 的距今小时数。

    为什么不看 backup_state.json 的时间戳：2026-10-09 实测——该文件
    ``last_ch_backup_time`` 停在 10-08T07:37，而 CH 服务端记着 10-09 01:05→01:37Z
    一条 BACKUP_CREATED（389.67 GB）。原因=成功那轮在写回 Stage 4 之前死掉，
    账本时间戳没推进。**用账本判新鲜度会把好链判红**，故尺锚在服务端事实。
    """
    import http.client

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
                "SELECT dateDiff('second', max(end_time), now()) "
                "FROM system.backups WHERE status='BACKUP_CREATED' FORMAT TSV"
            ),
            headers={"X-ClickHouse-User": user, "X-ClickHouse-Key": pwd},
        )
        raw = conn.getresponse().read().decode("utf-8", "replace").strip()
        conn.close()
    except Exception as e:  # noqa: BLE001
        return None, f"system.backups 采集失败: {e.__class__.__name__}"
    if not raw or not raw.replace(".", "").replace("-", "").isdigit():
        # fail-closed：无数据/非数都判红，绝不当"新鲜"放行（CH 出错可能返回空串）
        return None, f"system.backups 无有效读数(fail-closed): {raw[:60]!r}"
    return round(float(raw) / 3600, 1), "ok"


def ch_chain_fresh(max_age_h: int = CH_BACKUP_MAX_AGE_H) -> tuple[bool, str]:
    """预检专用：CH 恢复链新鲜度探针（裁定#380④ 仪表修正 #2，2026-10-09）。

    为什么不复用 ``_backup_fresh``：整轮备份节律 8h 而 CH 段 24h，写侧把
    "本轮未到 CH 节律" 正常记成 ``last_ch_backup_status=skipped``
    （backup.ps1:482），字符串比较 ``== 'ok'`` ⇒ **完全健康的链每天约 2/3 时段被
    误标红**（09-27 预检单即红在此）。本探针改判"服务端最近一条 BACKUP_CREATED
    距今时长"，锚在事实而非账本旗，且采集失败一律判红（fail-closed）。

    与阀#1 的边界：``_backup_fresh`` 仍服务归档阀#1（:329）**语义不动**——
    "只在 CH 刚备份完才允许删分区" 是刻意保守，改它会静默提高删除频率，
    属数据操作门位，不在仪表修正范围内（见 99_delivery 裁定回执）。
    """
    age_h, why = _ch_newest_backup_created_age_h()
    if age_h is None:
        return False, f"CH 链不可判({why})"
    st = _load_backup_state()
    verified = bool(st.get("last_ch_backup_verified"))
    if age_h > max_age_h:
        return False, f"CH 链陈旧 {age_h:.0f}h (>{max_age_h}h, 源=system.backups)"
    if not verified:
        return False, f"CH 链 {age_h:.0f}h 内新鲜但 last_ch_backup_verified 非真"
    return True, f"CH 链新鲜 {age_h:.0f}h (system.backups) + verified"


def last_compaction_days() -> tuple[float | None, str]:
    """距上次成功压缩的天数——真源=backup_state.json（仪表修正 #1）。

    修因：原判据从 ``load_state()``（rolling_archive_state.json）取
    ``last_vhdx_compaction``，而压缩成功记录实际写在 backup_state.json
    （``last_vhdx_compaction`` / ``last_vhdx_compaction_result=ok`` /
    ``last_vhdx_compaction_reclaimed_gb``）⇒ 该指标**恒 None**、``due`` **恒真**，
    "距上次压缩 ≥90 天" 这条触发条件从未生效过。
    """
    st = _load_backup_state()
    if str(st.get("last_vhdx_compaction_result") or "") != "ok":
        return None, "无 last_vhdx_compaction_result=ok 记录"
    age_h = _age_hours(st.get("last_vhdx_compaction"))
    if age_h is None:
        return None, "last_vhdx_compaction 时间戳不可解析"
    return round(age_h / 24, 1), "ok"


def d_drive_red_line_gb() -> tuple[float | None, str]:
    """从 capacity_guard 机读块取 D 盘红线（仪表修正 #3 的读者）。

    修因：注释（backup_config.yaml:130）声明红线含 D≥50G/E≥50G，但机读块
    ``capacity_guard.min_free_gb`` 只登记 F/G ⇒ D 线**无任何机读读者**，
    D 跌到 33.6G 无人拦。本函数是那把尺的读者之一（不新增第二真源）。
    """
    try:
        with open(BACKUP_CONFIG_FILE, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None, "backup_config.yaml 不可读"
    mins = (cfg.get("capacity_guard") or {}).get("min_free_gb") or {}
    val = mins.get("D")
    if val is None:
        return None, "capacity_guard.min_free_gb 缺 D 键"
    try:
        return float(val), "ok"
    except (TypeError, ValueError):
        return None, "D 键值非数"


def record_vhdx_growth(vhdx_gb: Any, d_free_gb: Any) -> dict[str, Any]:
    """每日体积哨兵（仪表修正 #4）：记 vhdx/D 剩余并算日差与红线判定。

    为什么要：日预检只存当日快照、无差分，于是"vhdx 以 3.9GiB/天回填、
    一次压缩约撑 8 个月"这类说法既无法证伪也没被证过——实测既有序列
    （vhdx_precheck_*.md 的 vhdx_size_gb）显示 10-03→10-09 六天基本持平
    （584.7→586.5），而压缩后头两天曾回弹 +13~16 GiB/天。增速**不是常数**，
    必须逐日记账才谈得上排窗。
    """
    rec: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vhdx_gb": vhdx_gb,
        "d_free_gb": d_free_gb,
        "delta_vs_prev_gb": None,
        "d_red_line_gb": None,
        "d_below_red_line": None,
    }
    prev = None
    if VHDX_GROWTH_SERIES.exists():
        try:
            lines = [x for x in VHDX_GROWTH_SERIES.read_text(encoding="utf-8").splitlines() if x.strip()]
            prev = json.loads(lines[-1]) if lines else None
        except (json.JSONDecodeError, OSError):
            prev = None
    if isinstance(vhdx_gb, (int, float)) and prev and isinstance(prev.get("vhdx_gb"), (int, float)):
        rec["delta_vs_prev_gb"] = round(vhdx_gb - prev["vhdx_gb"], 2)
    line, why = d_drive_red_line_gb()
    rec["d_red_line_gb"] = line
    rec["d_red_line_reason"] = why
    if line is not None and isinstance(d_free_gb, (int, float)):
        rec["d_below_red_line"] = bool(d_free_gb < line)
    VHDX_GROWTH_SERIES.parent.mkdir(parents=True, exist_ok=True)
    with open(VHDX_GROWTH_SERIES, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


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


def vhdx_precheck(notify_only: bool = True, force: bool = False) -> dict[str, Any]:
    """vhdx 季度压缩预检单（裁定#380④：只提醒不执行，实际压缩等 Owner 点名）。

    随备份成功事件运行（backup.ps1 STAGE 4b 同窗）；触发条件=季初首 7 天内
    或距上次成功压缩 ≥90 天。输出=预检单 md（五项指标）+控制台提醒一行，
    绝不自动停机/压缩。
    """
    import subprocess

    today = datetime.now()
    quarter_start_month = (today.month - 1) // 3 * 3 + 1
    in_quarter_start = today.day <= 7 and today.month == quarter_start_month
    days_since, days_why = last_compaction_days()
    due = in_quarter_start or (days_since is None or days_since >= 90)

    precheck: dict[str, Any] = {
        "date": today.isoformat(),
        "due": due,
        "in_quarter_start_window": in_quarter_start,
        "days_since_last_compaction": days_since,
        "days_since_source_note": days_why,
    }
    # 注：`due` 只 gate **预检单成文**，不 gate 采集——日增速哨兵必须天天记，
    # 否则"距上次压缩 <90 天"的年份里序列会整段断掉（仪表修正 #4 的本意）。
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

    d_free: Any = None
    try:
        out_d = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-Volume -DriveLetter D).SizeRemaining/1GB"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        d_free = round(float(out_d.stdout.strip()), 2)
        precheck["d_free_gb"] = d_free
    except Exception:  # noqa: BLE001
        precheck["d_free_gb"] = "采集失败"

    # 仪表修正 #4：逐日体积/增速哨兵（含 D 红线判定，D 线自此有了机读读者）
    try:
        growth = record_vhdx_growth(precheck.get("vhdx_size_gb"), d_free)
        precheck["vhdx_delta_gb"] = growth.get("delta_vs_prev_gb")
        precheck["d_red_line_gb"] = growth.get("d_red_line_gb")
        precheck["d_below_red_line"] = growth.get("d_below_red_line")
    except Exception as e:  # noqa: BLE001 — 哨兵故障不得连累预检本体
        precheck["vhdx_growth_probe_error"] = f"{e.__class__.__name__}: {str(e)[:120]}"

    # 仪表修正 #2：预检不再用"整体备份旗/节律 skip"当 CH 链判据，并列出**全部**红项
    # （原实现只回填 _backup_fresh() 的第一个红字符串，会把 CH 项一起藏掉）
    red_items: list[str] = []
    ok_ch, why_ch = ch_chain_fresh()
    precheck["ch_chain_fresh"] = ok_ch
    precheck["ch_chain_note"] = why_ch
    if not ok_ch:
        red_items.append(f"ch_chain: {why_ch}")
    ok_all, why_all = _backup_fresh()
    precheck["backup_flag_overall"] = why_all if ok_all else f"failed ({why_all})"
    if not ok_all:
        red_items.append(f"overall_backup_flag: {why_all}（注=整轮旗含非 CH 阶段，非 CH 链判据，见 ch_chain_note）")
    precheck["ready_for_owner_window"] = bool(ok_ch)
    precheck["blocking_items"] = red_items
    precheck["note"] = (
        "提醒条目——绝不自动执行压缩；实际停机压缩等 Owner 点名（裁定#380④/#381）。"
        "排窗须按实测增速与回收量（5.5/42.16 GiB 两次实跑、停机 4.3-4.8h），"
        "勿用 guest 空闲空间倒推收益，勿用本单旧口径'60-120 分钟'。"
    )

    if not (due or force):
        # 未到期：采集与日序列已记账，但不生成预检单（免噪音）
        return precheck

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    precheck_file = PLAN_DIR / f"vhdx_precheck_{today.strftime('%Y%m%d')}.md"
    with open(precheck_file, "w", encoding="utf-8") as f:
        f.write("---\nttl: task_bound\n---\n# vhdx 季度压缩预检单（自动生成·提醒条目）\n\n```json\n")
        f.write(json.dumps(precheck, ensure_ascii=False, indent=1))
        f.write(
            "\n```\n\nCH 链新鲜时呈 Owner 点名压缩（全局冻结档）。"
            "**停机窗请按实跑口径 4.3-4.8 小时排**（09-28=17440s／09-30=15373s），"
            "勿用旧文案 60-120 分钟；回收量按 5.5~42 GiB 区间保守排，"
            "勿用 guest 空闲空间倒推。\n"
        )
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
    p.add_argument("--force-precheck", action="store_true", help="即使未到期也重写当日预检单（仪表改版后纠旧单用）")
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
        print(json.dumps(vhdx_precheck(force=args.force_precheck), ensure_ascii=False, indent=1))
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
