# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_capability_symbol_gate
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-TEST-DATA-SYMGATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""声明-实现符号一致性双向 gate 单元测试（17 号 §5.8 施工项 4）。

覆盖:
  - 正向：self._fetch_xxx 路由调用未定义 → 违规；已定义 → 通过
  - 反向：frozenset/dict/set 路由变量 + meta capabilities（str/CapabilityContract）
    声明的 capability 无 _fetch_<cap> → 违规；有实现 → 通过
  - 双向同扫：两类违规一次返回
  - 退化：语法错误 fail-open 空；无类无声明空；非 self 调用/非 _fetch 前缀不校验；
    async 方法定义计入
  - 验收：模拟 17 号两历史 bug 形态（internal 半截工程 + akshare 声明残留）均可检出
"""
from __future__ import annotations

from zephyr.data.capability_symbol_gate import (
    check_declaration_impl_consistency,
    check_declaration_impl_consistency_content,
)

GOOD_PROVIDER = '''
class P:
    def fetch(self, capability, payload):
        if capability == "kline_daily":
            return self._fetch_kline_daily(payload)
        return self._fetch_trade_calendar(payload)

    def _fetch_kline_daily(self, payload):
        return []

    def _fetch_trade_calendar(self, payload):
        return []
'''

FORWARD_VIOLATION = '''
class P:
    def fetch(self, capability, payload):
        return self._fetch_hk_trade_calendar(payload)
'''

REVERSE_FROZENSET = '''
_KLINE_CAPABILITIES = frozenset({"kline_daily", "kline_weekly"})


class P:
    def fetch(self, capability, payload):
        return self._fetch_kline_daily(payload)

    def _fetch_kline_daily(self, payload):
        return []
'''

REVERSE_META_CONTRACT = '''
class P:
    meta = IngestProviderMeta(
        name="akshare",
        capabilities=[
            "trade_calendar",
            CapabilityContract("ipo_calendar", supports_symbols_null=True),
        ],
    )

    def _fetch_trade_calendar(self, payload):
        return []
'''

REVERSE_DICT_ROUTES = '''
_DIRECT_ROUTES = {"margin_target": "_fetch_margin_target"}


class P:
    pass
'''


class TestForward:
    def test_route_call_defined_passes(self):
        assert check_declaration_impl_consistency_content(GOOD_PROVIDER) == []

    def test_route_call_missing_detected(self):
        """internal_compute 式半截工程（17 号 §4.2 AttributeError 形态）可检出。"""
        violations = check_declaration_impl_consistency_content(FORWARD_VIOLATION)
        assert len(violations) == 1
        assert "_fetch_hk_trade_calendar" in violations[0]
        assert "未定义" in violations[0]

    def test_async_method_def_counts(self):
        content = '''
class P:
    def fetch(self, capability, payload):
        return self._fetch_tick(payload)

    async def _fetch_tick(self, payload):
        return []
'''
        assert check_declaration_impl_consistency_content(content) == []

    def test_non_self_and_non_fetch_calls_ignored(self):
        content = '''
class P:
    def fetch(self, capability, payload):
        helper(payload)
        return self.compute(payload)

    def compute(self, payload):
        return []
'''
        assert check_declaration_impl_consistency_content(content) == []


class TestReverse:
    def test_frozenset_decl_missing_method(self):
        """akshare L169 式声明残留：frozenset 声明 kline_weekly 无 _fetch_kline_weekly。"""
        violations = check_declaration_impl_consistency_content(REVERSE_FROZENSET)
        assert len(violations) == 1
        assert "kline_weekly" in violations[0]
        assert "_fetch_kline_weekly" in violations[0]
        assert "声明残留" in violations[0]

    def test_meta_capability_contract_missing_method(self):
        """meta capabilities：str 声明有实现 / CapabilityContract 声明无实现 → 仅报后者。"""
        violations = check_declaration_impl_consistency_content(REVERSE_META_CONTRACT)
        assert len(violations) == 1
        assert "ipo_calendar" in violations[0]

    def test_dict_route_var_declaration(self):
        violations = check_declaration_impl_consistency_content(REVERSE_DICT_ROUTES)
        assert len(violations) == 1
        assert "margin_target" in violations[0]

    def test_set_route_var_declaration(self):
        content = '_ROUTES = {"trade_calendar"}\n\n\nclass P:\n    pass\n'
        violations = check_declaration_impl_consistency_content(content)
        assert any("trade_calendar" in v for v in violations)


class TestBothDirections:
    def test_both_violations_one_scan(self):
        content = '''
_GHOST_CAPABILITIES = frozenset({"ghost_capability"})


class P:
    def fetch(self, capability, payload):
        return self._fetch_missing(payload)
'''
        violations = check_declaration_impl_consistency_content(content)
        assert len(violations) == 2
        assert any("_fetch_missing" in v for v in violations)
        assert any("ghost_capability" in v for v in violations)


class TestRouteFormExemptions:
    """真实 provider 路由形态校准（2026-08-20 实证）：参数化路由表/共享方法路由/纯 meta 字符串不算残留。"""

    def test_shared_method_routing_exempt(self):
        """miniqmt 形态：frozenset + capability in <var> 共享方法路由 → 不算残留。"""
        content = '''
_KLINE_1D_CAPABILITIES = frozenset({"kline_hk_daily", "kline_futures"})


class P:
    def fetch(self, capability, payload):
        if capability in _KLINE_1D_CAPABILITIES:
            yield from self._fetch_kline(payload, policy, "1d")

    def _fetch_kline(self, payload, policy, period):
        return []
'''
        assert check_declaration_impl_consistency_content(content) == []

    def test_param_dict_route_table_exempt(self):
        """miniqmt 形态：dict 参数化路由表（tuple/非 _fetch_ 值）+ in <var> → 不算残留。"""
        content = '''
_KLINE_CAPABILITIES = {
    "kline_daily": ("1d", "沪深A股"),
    "kline_1min": ("1m", "沪深A股"),
}


class P:
    def fetch(self, capability, payload):
        if capability in _KLINE_CAPABILITIES:
            period, sector = _KLINE_CAPABILITIES[capability]
            yield from self._fetch_kline(payload, policy, period)

    def _fetch_kline(self, payload, policy, period):
        return []
'''
        assert check_declaration_impl_consistency_content(content) == []

    def test_plain_meta_strings_not_checked(self):
        """memo §5.5 范围外：纯 meta 字符串声明（无 frozenset/Contract）不查。"""
        content = '''
class P:
    meta = IngestProviderMeta(name="eia", capabilities=["eia_petroleum", "eia_full"])

    def fetch(self, capability, payload):
        if capability == "eia_petroleum":
            return []
        return []
'''
        assert check_declaration_impl_consistency_content(content) == []

    def test_dynamic_dispatch_still_catches_residue(self):
        """akshare 形态：getattr(self, f"_fetch_{cap}") 动态分发 → frozenset 声明必须有 _fetch_<cap>。"""
        content = '''
_AKSHARE_CAPABILITIES = frozenset({"trade_calendar", "ghost_cap"})


class P:
    def fetch(self, payload, policy):
        cap = payload.extra.get("capability")
        if cap in _AKSHARE_CAPABILITIES:
            yield from getattr(self, f"_fetch_{cap}")(payload, policy)

    def _fetch_trade_calendar(self, payload, policy):
        return []
'''
        violations = check_declaration_impl_consistency_content(content)
        assert len(violations) == 1
        assert "ghost_cap" in violations[0]

    def test_dict_method_ref_missing_detected(self):
        """miniqmt _DIRECT_ROUTES 形态：dict 方法引用不存在 → 正向违规。"""
        content = '''
_DIRECT_ROUTES = {"adj_factor": "_fetch_adj_factor", "ghost": "_fetch_ghost"}


class P:
    def fetch(self, capability, payload):
        if capability in _DIRECT_ROUTES:
            yield from getattr(self, _DIRECT_ROUTES[capability])(payload, policy)

    def _fetch_adj_factor(self, payload, policy):
        return []
'''
        violations = check_declaration_impl_consistency_content(content)
        assert len(violations) == 1
        assert "_fetch_ghost" in violations[0]


class TestDegenerate:
    def test_syntax_error_fail_open(self):
        assert check_declaration_impl_consistency_content("def broken(:\n") == []

    def test_empty_content(self):
        assert check_declaration_impl_consistency_content("") == []

    def test_file_variant(self, tmp_path):
        p = tmp_path / "provider.py"
        p.write_text(FORWARD_VIOLATION, encoding="utf-8")
        assert len(check_declaration_impl_consistency(p)) == 1

    def test_file_missing_fail_open(self, tmp_path):
        assert check_declaration_impl_consistency(tmp_path / "nope.py") == []
