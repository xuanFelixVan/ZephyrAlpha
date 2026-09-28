# [BLUEPRINT] MOD-CMP-019 | (blueprint pending: 随施工闭环批补齐) | 43_compliance_discipline §3.3
# [MODULE] zephyr.compliance.checklist_evidence
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + zephyr.shared.io.file_utils + zephyr.shared.io.paths + zephyr.shared.security.secrets
# [CONSUMERS] scripts/start_paper_session.py（assemble_session 写侧①/②引导+写侧②逐批透传）; zephyr.ex_core.trading_session（限额回执处逐批落证）; 盘前人工 ack CLI（python -m zephyr.compliance.checklist_evidence ack）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 证据文件=最新一条即真源（atomic_write 原子落盘）; 证据缺失/损坏/交易日不符/字段不实/HMAC 不过=一律按未完成处理（fail-closed，缺项由 discipline_must_do_checker 判 INTRADAY HARD_BLOCK，裁定值勿改）; ack 禁明文恒真：confirmed_by/ack_source 来源标注必填，ZEPHYR_COMPLIANCE_ACK_KEY 在场时强制 HMAC-SHA256（RULE-SECRETS 经 secrets.py 取，禁裸 getenv）
# [MODIFY-GUARD] 43_compliance_discipline.md §3.3（INTRADAY 三腿完成度信号的生产真源）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChecklistEvidenceError(ZA-CMP-0020)
# [TESTS] tests/compliance/test_checklist_evidence.py
# [TTL] permanent

"""
C-004 清单闸 INTRADAY 三腿完成度证据的生产写侧（43 号 §3.3，F62 排雷案卷雷三）。

雷三结论：``signal_compliance_check``/``risk_param_confirm``/``position_limit_verify``
三个 item key 全仓零生产写者——checker 接空 provider=每轮整批拒单，接恒真 provider=
假闸。本模块补齐写侧，三条腿各有一个证据文件（``<item_key>.json``，最新一条即真源）：

  - 写侧① risk_param_confirm（机器）：RiskLimits 装配成功处由 assemble_session 落证
    （时间戳 + 快照 idempotency_key + limit 集）。
  - 写侧② position_limit_verify（机器）：assemble_session 装配引导落证一次（解除
    "首批自锁"——清单闸在逐单限额检查**之前**评估，若证据只能由限额检查产生，则
    首批必因缺证被 Hard Block，写者永无执行机会=死锁），此后 trading_session 每次
    逐单限额验证处刷新执行回执（symbol/blocked 明细）。
  - 写侧③ signal_compliance_check（人工）：复用"拍板"范式最薄版——盘前人工经 ack
    CLI 落确认件，confirmed_by/ack_source 来源标注必填；配置 ack 密钥时强制
    HMAC-SHA256 防手改，未配置时 auth_mode 明示 source_annotation_only（降级可见，
    不伪装强证据）。

读侧 = :class:`ChecklistEvidenceProvider`（``CompletionProvider`` 形态），按交易日
取证：任何缺失/损坏/日期不符/验签不过都按"该腿未完成"返回，不抛不吞——缺项汇入
checker 的 INTRADAY Hard Block 语义（诚实失败方向）。非 INTRADAY 时点本批无写者，
诚实回空集（对应时点未装配，不属本批施工面）。

测试隔离：全部路径可注入（base_dir），测试 MUST 传 tmp_path——根宪法 §9 第 6 条
禁测试写生产 data/。

Version: 1.0.0

# [ALGO_FLOW] external: docs/03_modules/_domain_compliance/algo_flow/checklist_evidence.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from zephyr.compliance.discipline_must_do_checker import (
    REQUIRED_ITEMS,
    ChecklistCheckpoint,
)
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write
from zephyr.shared.io.paths import MAIN_REPO_ROOT
from zephyr.shared.security.secrets import get_secret_or_default

#: 生产证据目录（锚定主仓，与 KillSwitchLite/compliance_log 同仓级锚定口径——
#: 单实例 paper 系统无 worktree 路径歧义；测试经 base_dir 注入 tmp_path）
DEFAULT_EVIDENCE_DIR: Path = MAIN_REPO_ROOT / "data" / "compliance_log" / "checklist"

#: ack HMAC 密钥的 secret 键名（.env / 环境变量经 secrets.py 统一读取）
# create-guard-not-dup: 本模块 ACK_KEY 是清单闸人工确认证据的 HMAC 签名密钥（防证据被手改），与 runtime_llm_call_interceptor 的 LLM 调用拦截能力零功能重叠，纯关键词误伤
ACK_SECRET_KEY: str = "ZEPHYR_COMPLIANCE_ACK_KEY"

#: auth_mode 字段值：HMAC-SHA256 验签模式（密钥在场时的强制形态）
_AUTH_HMAC: str = "hmac_sha256"

#: auth_mode 字段值：仅来源标注模式（密钥缺席时的明示降级，不冒充强证据）
_AUTH_SOURCE_ONLY: str = "source_annotation_only"

_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


class ChecklistEvidenceError(ZephyrBaseError):
    """清单证据写侧错误。"""

    error_code = "ZA-CMP-0020"


def today_shanghai(now: datetime | None = None) -> date:
    """A 股交易日口径日期（北京时区；UTC 时刻换算当日）。"""
    return (now or datetime.now(timezone.utc)).astimezone(_SHANGHAI_TZ).date()


def _canonical_bytes(payload: dict) -> bytes:
    """HMAC 签名/验签的规范化字节（sort_keys 消除键序歧义）。"""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _ack_key() -> str:
    """ack HMAC 密钥（RULE-SECRETS 唯一合法通道；缺席=空串→source 标注模式）。"""
    return get_secret_or_default(ACK_SECRET_KEY, "")


class ChecklistEvidenceWriter:
    """三腿完成度证据写者（唯一写入口；base_dir 可注入，测试 MUST 给 tmp_path）。

    证据文件语义="最新一条即真源"（JsonStateStore 同款），原子写防半写残file
    （雷二 :53 的教训：非原子写+中途被杀=烂 JSON）。写失败上抛
    :class:`ChecklistEvidenceError`——证据写不出必须出声，不得静默假装已留痕。
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = Path(base_dir) if base_dir is not None else DEFAULT_EVIDENCE_DIR

    @property
    def base_dir(self) -> Path:
        """证据目录（只读）。"""
        return self._base_dir

    def _write(self, item_key: str, trade_date: date, payload: dict, *, signer=None) -> Path:
        record = {
            "item_key": item_key,
            "trade_date": trade_date.isoformat(),
            "ts": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        if signer is not None:
            # 签名钩子在**全量记录装配后**生效（含 item_key/trade_date/ts）——
            # 与读侧"record 去 hmac 字段重算"严格同一口径，签半截载荷=验签必败
            record = signer(record)
        path = self._base_dir / f"{item_key}.json"
        try:
            atomic_write(path, json.dumps(record, ensure_ascii=False, sort_keys=True, default=str))
        except OSError as exc:
            raise ChecklistEvidenceError(
                "清单证据写入失败",
                details={"path": str(path), "error": str(exc)},
            ) from exc
        return path

    def write_risk_param_confirm(
        self,
        snapshot_id: str,
        limits: dict,
        *,
        trade_date: date | None = None,
        source: str,
    ) -> Path:
        """写侧①：RiskLimits 装配成功证据（时间戳+快照 id+limit 集）。

        Args:
            snapshot_id: RiskLimits.idempotency_key（快照身份）。
            limits: limit 集（max_single_position 等实际生效限额）。
            trade_date: 交易日；None=北京时区今天。
            source: 写者标识（模块.函数），必填留痕。
        """
        if not source.strip():
            raise ChecklistEvidenceError("写侧① source 必填（无写者标识不受理）")
        return self._write(
            "risk_param_confirm",
            trade_date or today_shanghai(),
            {"writer": source, "snapshot_id": snapshot_id, "limits": limits},
        )

    def write_position_limit_verify(
        self,
        snapshot_id: str,
        *,
        trade_date: date | None = None,
        source: str,
        detail: dict | None = None,
    ) -> Path:
        """写侧②：仓位限额验证执行证据（装配引导与逐批回执共用本入口）。

        Args:
            snapshot_id: 所验证的 RiskLimits.idempotency_key。
            trade_date: 交易日；None=北京时区今天。
            source: 写者标识；逐批回执处带 symbol/blocked 明细入 detail。
            detail: 执行明细（如 {"symbol": ..., "blocked": ...}）。
        """
        if not source.strip():
            raise ChecklistEvidenceError("写侧② source 必填（无写者标识不受理）")
        return self._write(
            "position_limit_verify",
            trade_date or today_shanghai(),
            {"writer": source, "snapshot_id": snapshot_id, "detail": detail or {}},
        )

    def write_signal_compliance_ack(
        self,
        confirmed_by: str,
        *,
        note: str = "",
        trade_date: date | None = None,
        ack_source: str,
    ) -> Path:
        """写侧③：人工拍板确认件（signal_compliance_check，禁明文恒真）。

        来源标注（confirmed_by/ack_source）必填非空；ZEPHYR_COMPLIANCE_ACK_KEY
        在场时对去掉 hmac 字段后的规范化载荷做 HMAC-SHA256 并记录 auth_mode，
        缺席时 auth_mode=source_annotation_only 明示降级形态。

        Args:
            confirmed_by: 确认人（人工拍板者，留痕）。
            note: 备注（本次确认覆盖的信号/检查口径）。
            trade_date: 交易日；None=北京时区今天。
            ack_source: 确认通道（如 manual_ack_cli），留痕。
        """
        if not confirmed_by.strip() or not ack_source.strip():
            raise ChecklistEvidenceError("写侧③ confirmed_by/ack_source 必填（无来源不受理）")
        payload: dict = {
            "writer": ack_source,
            "confirmed_by": confirmed_by.strip(),
            "ack_source": ack_source,
            "note": note,
        }
        return self._write(
            "signal_compliance_check",
            trade_date or today_shanghai(),
            payload,
            signer=self._sign_ack,
        )

    @staticmethod
    def _sign_ack(record: dict) -> dict:
        """ack 签名钩子：密钥在场=对全量记录（去 hmac）HMAC-SHA256；缺席=明示降级。"""
        key = _ack_key()
        if key:
            record["auth_mode"] = _AUTH_HMAC
            record["hmac"] = hmac.new(key.encode("utf-8"), _canonical_bytes(record), hashlib.sha256).hexdigest()
        else:
            record["auth_mode"] = _AUTH_SOURCE_ONLY
        return record


def _verify_hmac(record: dict, key: str) -> bool:
    """验签：去掉 hmac 字段重算规范化载荷比对（恒时比较）；密钥缺席=不可验证。"""
    stored = record.get("hmac")
    if not isinstance(stored, str) or not stored or not key:
        return False
    body = {k: v for k, v in record.items() if k != "hmac"}
    expected = hmac.new(key.encode("utf-8"), _canonical_bytes(body), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, stored)


class ChecklistEvidenceProvider:
    """完成度信号源（``CompletionProvider`` 形态）：读证据目录产出已完成 key 集。

    判定全 fail-closed：文件缺失/JSON 损坏/交易日不符/item_key 不符/写者标识
    缺失/HMAC 不过/来源标注缺失 → 该腿记为**未完成**（不抛异常——缺项由
    checker 按 INTRADAY Hard Block 语义处置，与本模块 INVARIANTS 一致）。
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = Path(base_dir) if base_dir is not None else DEFAULT_EVIDENCE_DIR

    @property
    def base_dir(self) -> Path:
        """证据目录（只读）。"""
        return self._base_dir

    def __call__(self, checkpoint: ChecklistCheckpoint, trade_date: date) -> set[str]:
        if checkpoint is not ChecklistCheckpoint.INTRADAY:
            # 本批只施工 INTRADAY 三腿写侧；其余时点无写者腿，诚实回空
            # （对应时点在装配面明示未装，不属本批施工面——43 号 §3.3）
            return set()
        return {key for key in REQUIRED_ITEMS[checkpoint] if self._is_completed(key, trade_date)}

    def _is_completed(self, item_key: str, trade_date: date) -> bool:
        path = self._base_dir / f"{item_key}.json"
        if not path.is_file():
            return False
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return False
        if not isinstance(raw, dict):
            return False
        if raw.get("item_key") != item_key:
            return False
        if raw.get("trade_date") != trade_date.isoformat():
            return False
        if not str(raw.get("writer") or "").strip():
            return False
        mode = raw.get("auth_mode")
        if mode == _AUTH_HMAC:
            return _verify_hmac(raw, _ack_key())
        if mode == _AUTH_SOURCE_ONLY:
            return bool(str(raw.get("confirmed_by") or "").strip())
        return True  # 机器写者（写侧①②）：writer 字段已验非空


def build_parser() -> argparse.ArgumentParser:
    """ack CLI 参数面（盘前人工拍板入口 + 当日三腿状态查读）。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.compliance.checklist_evidence",
        description="C-004 清单闸证据写侧：人工确认（ack）与当日完成度查读（status）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ack = sub.add_parser("ack", help="写侧③：落 signal_compliance_check 人工拍板确认件")
    ack.add_argument("--confirmed-by", required=True, help="确认人（必填，留痕来源）")
    ack.add_argument("--note", default="", help="备注（本次确认覆盖的信号/检查口径）")
    ack.add_argument("--trade-date", default=None, help="交易日 YYYY-MM-DD（默认北京时区今天）")
    ack.add_argument(
        "--base-dir", default=None, help="证据目录覆盖（测试/运维用；默认主仓 data/compliance_log/checklist）"
    )

    status = sub.add_parser("status", help="打印当日 INTRADAY 三腿完成度（供盘前人工核对）")
    status.add_argument("--trade-date", default=None, help="交易日 YYYY-MM-DD（默认北京时区今天）")
    status.add_argument("--base-dir", default=None, help="证据目录覆盖（测试/运维用）")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：ack=写确认件；status=读当日三腿状态。"""
    args = build_parser().parse_args(argv)
    trade_date: date | None = None
    if args.trade_date:
        try:
            trade_date = date.fromisoformat(args.trade_date)
        except ValueError as exc:
            raise SystemExit(f"[CHECKLIST] --trade-date 格式非法（须 YYYY-MM-DD）: {args.trade_date}") from exc
    base_dir = Path(args.base_dir) if args.base_dir else None

    if args.command == "ack":
        confirmed_by = (args.confirmed_by or "").strip()
        if not confirmed_by:
            raise SystemExit("[CHECKLIST] --confirmed-by 必填非空（禁明文恒真，无来源不受理）")
        writer = ChecklistEvidenceWriter(base_dir)
        path = writer.write_signal_compliance_ack(
            confirmed_by,
            note=args.note,
            trade_date=trade_date,
            ack_source="manual_ack_cli",
        )
        print(f"[CHECKLIST-ACK] signal_compliance_check 确认件已落盘: {path}")
        return 0

    # status：当日三腿完成度一览（不判定不处置，处置语义归 checker）
    provider = ChecklistEvidenceProvider(base_dir)
    td = trade_date or today_shanghai()
    completed = provider(ChecklistCheckpoint.INTRADAY, td)
    print(f"[CHECKLIST-STATUS] trade_date={td.isoformat()} base_dir={provider.base_dir}")
    for key in REQUIRED_ITEMS[ChecklistCheckpoint.INTRADAY]:
        mark = "DONE" if key in completed else "MISSING"
        print(f"[CHECKLIST-STATUS]   {key}: {mark}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
