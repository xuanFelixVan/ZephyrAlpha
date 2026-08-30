# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.manual_calendar_events
# [DOMAIN] D_DATA
# [DEPENDENCIES] none（stdlib only；schema 真源 config/manual_calendar_events_schema.yaml 为文档性定义）
# [CONSUMERS] 一次性 IMPORT 脚本（17号 §6.3，本批次不施工 IMPORT 执行）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只校验不落库；错误带行号可定位；manual 三类之外的 event_type 一律拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不抛异常——返回 (valid_rows, errors)；文件不存在/编码错误→([], [error])
# [TESTS] tests/zephyr/data/test_manual_calendar_events.py
# [A_module] module_id=MOD-L00-004-MCE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: manual 日历事件 CSV
#   fields: event_date,event_type,description[,data_source]（utf-8-sig，# 注释行跳过）
# 层: 算法
# - id: A1
#   name_zh: 逐行格式校验
#   name_en: validate_manual_events_csv
#   intro: 列头核对→日期 ISO 格式+范围→event_type 白名单（manual 三类）→description 非空≤200→同键去重
# 层: 输出
# - id: O1
#   name_zh: 合法行 + 错误清单
#   name_en: (list[dict], list[str])
#   intro: 合法行可直接映射 calendar_event INSERT_COLUMNS；错误带 CSV 行号供台账修正
"""



manual 日历事件 CSV 录入校验（17号 §6.3，2026-08-20 AI-NIGHT-001 施工）。

裁定真源：17号 §6.3（v1.0.0 定稿）——fomc_meeting / major_meeting / stamp_duty_change
三个 manual event_type 采纳"方案① CSV 录入 + 一次性 IMPORT"为标准填充路径。
本模块只做格式定义的消费侧（校验函数）；CSV schema 真源见
config/manual_calendar_events_schema.yaml；一次性 IMPORT 执行不在本批次范围。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 str | Path
#   code: manual_calendar_events.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① validate_manual_events_csv
#   name_en: validate_manual_events_csv
#   intro: 校验 manual 日历事件 CSV，返回 (合法行, 错误清单)。
#   desc: 校验 manual 日历事件 CSV，返回 (合法行, 错误清单)。 Args: path: CSV 文件路径（utf-8-sig 容忍 BOM；# 开头注释行与空行跳过）。 R…；源码 L85-L152
#   inputs: path
#   outputs: tuple[list[dict[str, str]], list[str]]
# 层: 输出
# - id: O1
#   name_zh: tuple[list[dict[str, str]], list[str]]
#   name_en: tuple[list[dict[str, str]], list[str]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 一次性 IMPORT 脚本（17号 §6.3，本批次不施工 IMPORT 执行）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import csv
import datetime
from pathlib import Path

# 与 config/manual_calendar_events_schema.yaml 对齐（改 schema 须同步改这里）
ALLOWED_EVENT_TYPES = frozenset({"fomc_meeting", "major_meeting", "stamp_duty_change"})
REQUIRED_COLUMNS = frozenset({"event_date", "event_type", "description"})
OPTIONAL_COLUMNS = frozenset({"data_source"})
DATE_MIN = datetime.date(1990, 1, 1)
DATE_MAX = datetime.date(2100, 1, 1)
DESCRIPTION_MAX_LENGTH = 200
_COMMENT_PREFIX = "#"


def validate_manual_events_csv(
    path: str | Path,
) -> tuple[list[dict[str, str]], list[str]]:
    """校验 manual 日历事件 CSV，返回 (合法行, 错误清单)。

    Args:
        path: CSV 文件路径（utf-8-sig 容忍 BOM；# 开头注释行与空行跳过）。

    Returns:
        (valid_rows, errors)：
        - valid_rows: 合法行 dict 列表，键为 event_date/event_type/description/data_source，
          data_source 缺省补 "manual"；可直接映射 calendar_event INSERT_COLUMNS。
        - errors: 错误描述列表（带 CSV 物理行号，1 基）；任何错误存在时调用方应拒绝导入。
    """
    path = Path(path)
    if not path.is_file():
        return [], [f"文件不存在: {path}"]
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError) as e:
        return [], [f"文件读取/编码失败（须 utf-8）: {e}"]

    errors: list[str] = []
    valid_rows: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str]] = set()
    header: list[str] | None = None

    # 物理行号（1 基）跟踪：csv.reader 逐行消费，注释/空行也占行号
    for lineno, fields in enumerate(csv.reader(text.splitlines()), start=1):
        # 注释行/空行跳过
        if not fields or all(not f.strip() for f in fields):
            continue
        if fields[0].lstrip().startswith(_COMMENT_PREFIX):
            continue
        # 首个非注释非空行 = 列头
        if header is None:
            header = [f.strip() for f in fields]
            missing = REQUIRED_COLUMNS - set(header)
            if missing:
                errors.append(f"行 {lineno}: 列头缺少必需列 {sorted(missing)}")
                return [], errors  # 列头错误后续行无意义
            unknown = set(header) - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
            if unknown:
                errors.append(
                    f"行 {lineno}: 列头含未知列 {sorted(unknown)}（仅允许 event_date/event_type/description/data_source）"
                )
            continue

        row = dict(zip(header, (f.strip() for f in fields), strict=False))
        if len(fields) != len(header):
            errors.append(f"行 {lineno}: 列数 {len(fields)} 与列头 {len(header)} 不一致")
            continue

        if not _validate_row(lineno, row, errors):
            continue

        key = (row["event_date"], row["event_type"])
        if key in seen_keys:
            errors.append(f"行 {lineno}: 同键重复 (event_date={key[0]}, event_type={key[1]})")
            continue
        seen_keys.add(key)
        if not row.get("data_source"):
            row["data_source"] = "manual"
        valid_rows.append(row)

    if header is None:
        errors.append("文件无有效列头（全为注释/空行）")
    return valid_rows, errors


def _validate_row(lineno: int, row: dict[str, str], errors: list[str]) -> bool:
    """单行字段校验；合法返回 True，否则追加错误并返回 False。"""
    ok = True
    # event_date：ISO 严格格式 + 范围
    raw_date = row.get("event_date", "")
    try:
        d = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
        if not (DATE_MIN <= d <= DATE_MAX):
            errors.append(f"行 {lineno}: event_date {raw_date} 超出范围 [{DATE_MIN}, {DATE_MAX}]")
            ok = False
    except ValueError:
        errors.append(f"行 {lineno}: event_date 非法（须 YYYY-MM-DD）: {raw_date!r}")
        ok = False
    # event_type：manual 三类白名单
    event_type = row.get("event_type", "")
    if event_type not in ALLOWED_EVENT_TYPES:
        errors.append(
            f"行 {lineno}: event_type 非法（仅允许 {sorted(ALLOWED_EVENT_TYPES)}，"
            f"internal 派生类禁止走 CSV）: {event_type!r}"
        )
        ok = False
    # description：非空且 ≤200
    desc = row.get("description", "")
    if not desc:
        errors.append(f"行 {lineno}: description 为空")
        ok = False
    elif len(desc) > DESCRIPTION_MAX_LENGTH:
        errors.append(f"行 {lineno}: description 超长（{len(desc)} > {DESCRIPTION_MAX_LENGTH}）")
        ok = False
    # data_source：显式提供时必须为 manual
    ds = row.get("data_source", "")
    if ds and ds != "manual":
        errors.append(f"行 {lineno}: data_source 仅允许 manual: {ds!r}")
        ok = False
    return ok
