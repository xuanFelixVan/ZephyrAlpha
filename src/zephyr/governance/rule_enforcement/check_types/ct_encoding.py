# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_encoding
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_encoding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

EncodingHandler — EncodingHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class EncodingHandler(CheckTypeHandler):
    name = "encoding"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations = []

        deliverables = list(task.deliverables or [])

        dep_paths = [project_root / p for p in deliverables]

        for fp in dep_paths:
            try:
                raw = fp.read_bytes()

            except FileNotFoundError:
                continue

            if raw.startswith(b"\xef\xbb\xbf"):
                violations.append({"message": f"BOM detected: {fp}", "severity": check.severity})

            try:
                raw.decode("utf-8")
            except UnicodeDecodeError as e:
                violations.append({"message": f"Non-UTF-8: {fp}: {e}", "severity": check.severity})

            if _detect_mojibake_bytes(raw):
                violations.append(
                    {
                        "message": f"GBK-as-UTF-8 mojibake: {fp} — file contains double-encoded garbled text",
                        "severity": check.severity,
                    }
                )

        return violations


def _detect_mojibake_bytes(raw: bytes) -> bool:
    """Detect GBK-as-UTF-8 double-encoding mojibake in raw bytes.

    Detection methods:
    1. Known mojibake character sequences (high confidence)
    2. Round-trip via GBK on CJK segments (2a: clean, 2b: with U+FFFD)
    3. U+FFFD in CJK context (replacement chars adjacent to CJK)
    4. Statistical fallback (abnormal CJK distribution)
    """
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if not content.strip():
        return False
    # Method 1: known markers
    MOJIBAKE_MARKERS = [
        "\u9516\u65a4\u62f7",  # 锟斤拷
        "\u93d4\u63d2\u53c2",
        "\u93d4\u659c\u7280\u6362",
        "\u93d4\u529c\u00b0\u20ac",
        "\u94c6\u003f",
    ]
    if any(m in content for m in MOJIBAKE_MARKERS):
        return True
    # Method 2: round-trip via GBK (CJK segments only)
    import re as _re

    # 2a: test segments WITHOUT U+FFFD
    clean_content = content.replace("\ufffd", "")
    if clean_content.strip():
        cjk_segments = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]+", clean_content)
        for seg in cjk_segments:
            if len(seg) < 2:
                continue
            try:
                gbk_bytes = seg.encode("gbk")
                try:
                    roundtrip = gbk_bytes.decode("utf-8")
                    if roundtrip != seg:
                        orig_cjk = sum(1 for c in seg if 0x4E00 <= ord(c) <= 0x9FFF)
                        rt_cjk = sum(1 for c in roundtrip if 0x4E00 <= ord(c) <= 0x9FFF)
                        if rt_cjk > 0 and orig_cjk > 0:
                            rt_cjk_density = rt_cjk / len(roundtrip)
                            orig_cjk_density = orig_cjk / len(seg)
                            if rt_cjk_density >= orig_cjk_density:
                                return True
                except UnicodeDecodeError:
                    # Partial decode may reveal mojibake
                    try:
                        partial_rt = gbk_bytes.decode("utf-8", errors="replace")
                        partial_cjk = sum(1 for c in partial_rt if 0x4E00 <= ord(c) <= 0x9FFF and c != "\ufffd")
                        if partial_cjk >= 3:
                            return True
                    except Exception:
                        pass
            except UnicodeEncodeError:
                pass
    # 2b: test segments WITH U+FFFD — split at U+FFFD and test sub-segments
    if "\ufffd" in content:
        cjk_with_replacement = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\ufffd]+", content)
        for seg in cjk_with_replacement:
            if "\ufffd" not in seg:
                continue
            sub_segs = [s for s in seg.split("\ufffd") if len(s) >= 2]
            for sub in sub_segs:
                try:
                    gbk_bytes = sub.encode("gbk")
                    try:
                        roundtrip = gbk_bytes.decode("utf-8")
                        if roundtrip != sub:
                            orig_cjk = sum(1 for c in sub if 0x4E00 <= ord(c) <= 0x9FFF)
                            rt_cjk = sum(1 for c in roundtrip if 0x4E00 <= ord(c) <= 0x9FFF)
                            if rt_cjk > 0 and orig_cjk > 0:
                                rt_cjk_density = rt_cjk / len(roundtrip)
                                orig_cjk_density = orig_cjk / len(sub)
                                if rt_cjk_density >= orig_cjk_density:
                                    return True
                    except UnicodeDecodeError:
                        pass
                except UnicodeEncodeError:
                    pass
    # Method 3: U+FFFD in CJK context
    if "\ufffd" in content:
        cjk_context = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]\ufffd|\ufffd[\u4e00-\u9fff\u3400-\u4dbf]", content)
        if len(cjk_context) >= 2:
            return True
    # Method 4: statistical fallback
    total_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x9FFF)
    if total_cjk < 50:
        return False
    common_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x77FF)
    gbk_ext_cjk = sum(1 for c in content if 0x9400 <= ord(c) <= 0x9FFF)
    if gbk_ext_cjk / total_cjk > 0.50 and common_cjk / total_cjk < 0.30:
        return True
    return False
