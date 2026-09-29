# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.test_ch_probe_json_serialization_canary
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest；json/datetime/decimal；importlib 动态加载 scripts/governance/data_supply/ch_probe.py
# [CONSUMERS] pytest;CI_pipeline
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 探针落盘必能序列化 Date/Datetime/Decimal；去掉 default=_jsonable 时必抛（尺能红）；Decimal 走定点字符串禁科学计数法
# [MODIFY-GUARD] 判据本体在 ch_probe._jsonable，本测试只做红蓝双向证明
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即 pytest 非零；探针模块不可加载时报错而非静默跳过
# [TESTS] 本件即测试
# [TTL] task_bound
"""W-180.4 标准探针的序列化红蓝测试（本役实测缺陷：Date/Decimal 列让整批探针崩）。

探针是判据类读数的强制通道，探针崩＝读数面同时失效，
所以"崩"必须比"读到 0"更显式——本测试锁两件事：修好时能序列化，人为拆掉 default 时必红。
"""

from __future__ import annotations

import datetime as dt
import decimal
import importlib.util
import json
from pathlib import Path

import pytest

_PROBE = Path(__file__).resolve().parents[2] / "scripts/governance/data_supply/ch_probe.py"


def _load_probe():
    spec = importlib.util.spec_from_file_location("ch_probe_under_test", _PROBE)
    assert spec and spec.loader, f"探针模块不可加载: {_PROBE}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_probe_serializes_date_and_decimal() -> None:
    probe = _load_probe()
    payload = {
        "rows": [[dt.date(2026, 9, 3), decimal.Decimal("1.50")]],
        "ts": dt.datetime(2026, 9, 27, 2, 40),
    }
    out = json.loads(json.dumps(payload, ensure_ascii=False, default=probe._jsonable))
    assert out["rows"][0] == ["2026-09-03", "1.50"]  # Decimal 定点字符串，非 '1.5E+00'
    assert out["ts"] == "2026-09-27T02:40:00"


def test_ruler_goes_red_without_the_fallback() -> None:
    """红证：拿掉 default=_jsonable 必须抛——否则本测试无判别力（R-5 能红判据模板）。"""
    payload = {"rows": [[dt.date(2026, 9, 3), decimal.Decimal("1.50")]]}
    with pytest.raises(TypeError):
        json.dumps(payload, ensure_ascii=False)


def test_probe_helper_survives_datetime_name_shadowing() -> None:
    """红证②：ch_probe 里 `from datetime import datetime` 遮蔽了模块名，
    助手若写成 datetime.date 字面量会 AttributeError——这里锁它不再依赖该写法。"""
    probe = _load_probe()

    class _Opaque:
        pass

    out = probe._jsonable(_Opaque())
    assert isinstance(out, str) and out  # 兜底分支：转字符串而非抛异常
    assert json.dumps({"x": _Opaque()}, default=probe._jsonable)  # 整包可序列化
