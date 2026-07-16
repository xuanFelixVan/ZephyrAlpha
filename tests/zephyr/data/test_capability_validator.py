"""capability_validator 契约测试（裁定 #ARCH-CH-022 Phase 4.5）。

测试内容：
- CapabilityContract / _normalize_capabilities 归一化（provider_base 侧）
- validate_task_capability_contracts 三条规则（CAP-NOT-FOUND / CAP-NULL-SYMBOLS / CAP-INCREMENTAL）
- has_blocking_violations / format_violations
- AST 路由能力提取（extract_route_capabilities / _route_caps_from_tree）
- AST meta 能力提取（extract_meta_capabilities / _meta_caps_from_tree）
- 路由-meta 一致性校验（check_route_meta_consistency / check_route_meta_consistency_content）
  - 三 provider 路由模式覆盖：frozenset（akshare）/ 多字典（miniqmt）/ if-elif 链（ifind）
  - AnnAssign（类属性 meta）+ Assign（实例级 self.meta）双检测
  - fail-open：文件不存在 / 解析失败
  - 一致 / 路由漏声明 / meta 死声明 三场景

不依赖真实 SDK / tasks.yaml，用临时文件 + 内联代码片段。
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.zephyr.data.capability_validator import (
    Violation,
    validate_task_capability_contracts,
    has_blocking_violations,
    format_violations,
    extract_route_capabilities,
    extract_meta_capabilities,
    check_route_meta_consistency,
    check_route_meta_consistency_content,
    _route_caps_from_tree,
    _meta_caps_from_tree,
)
from src.zephyr.data.provider_base import (
    CapabilityContract,
    DataSourceMeta,
    _normalize_capabilities,
)


# ============== CapabilityContract / _normalize_capabilities ==============

class TestNormalizeCapabilities:
    """capabilities 字段归一化（list[str | CapabilityContract] -> list[CapabilityContract]）。"""

    def test_all_strings_normalized_to_default_contract(self):
        """纯字符串列表归一化为默认 CapabilityContract（所有标志取默认值）。"""
        result = _normalize_capabilities(["kline_daily", "money_flow"])
        assert len(result) == 2
        assert all(isinstance(c, CapabilityContract) for c in result)
        assert result[0].capability_id == "kline_daily"
        assert result[0].supports_symbols_null is False  # 默认 False
        assert result[0].supports_incremental is True  # 默认 True

    def test_capability_contract_passed_through(self):
        """CapabilityContract 实例直接保留，不重新构造。"""
        cc = CapabilityContract("top10_shareholders", supports_symbols_null=True)
        result = _normalize_capabilities([cc])
        assert result[0] is cc

    def test_mixed_list_normalized(self):
        """字符串与 CapabilityContract 混合列表归一化。"""
        result = _normalize_capabilities([
            "kline_daily",
            CapabilityContract("balance_sheet", supports_symbols_null=True),
        ])
        assert result[0].capability_id == "kline_daily"
        assert result[0].supports_symbols_null is False
        assert result[1].capability_id == "balance_sheet"
        assert result[1].supports_symbols_null is True

    def test_invalid_type_raises_type_error(self):
        """非 str / CapabilityContract 元素抛 TypeError。"""
        with pytest.raises(TypeError):
            _normalize_capabilities([123])

    def test_data_source_meta_post_init_normalizes(self):
        """DataSourceMeta.__post_init__ 自动归一化 capabilities。"""
        meta = DataSourceMeta(
            name="test", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["kline_daily", CapabilityContract("money_flow", supports_symbols_null=True)],
        )
        # capability_contracts 属性返回归一化后的 list[CapabilityContract]
        contracts = meta.capability_contracts
        assert all(isinstance(c, CapabilityContract) for c in contracts)
        assert contracts[0].capability_id == "kline_daily"
        assert contracts[1].supports_symbols_null is True

    def test_get_capability_contract_returns_none_if_not_found(self):
        """get_capability_contract 不存在时返回 None。"""
        meta = DataSourceMeta(
            name="test", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["kline_daily"],
        )
        assert meta.get_capability_contract("kline_daily") is not None
        assert meta.get_capability_contract("not_exist") is None

    def test_capabilities_as_strings_backward_compat(self):
        """capabilities_as_strings 返回字符串列表（向后兼容）。"""
        meta = DataSourceMeta(
            name="test", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["kline_daily", CapabilityContract("money_flow", supports_symbols_null=True)],
        )
        assert meta.capabilities_as_strings() == ["kline_daily", "money_flow"]


# ============== validate_task_capability_contracts 三条规则 ==============

def _make_meta(caps: list) -> DataSourceMeta:
    """构造测试用 DataSourceMeta。"""
    return DataSourceMeta(
        name="test", display_name="t", auth_type="anonymous",
        requires_process=False, thread_safety="shared", rate_limit_default=0,
        capabilities=caps,
    )


class TestValidateTaskCapabilityContracts:
    """validate_task_capability_contracts 三条规则（ERROR / WARN / WARN）。"""

    def test_empty_tasks_no_violations(self):
        """空 tasks 列表返回空违规列表。"""
        assert validate_task_capability_contracts([], {}) == []

    def test_disabled_task_skipped(self):
        """disabled 任务跳过校验。"""
        task = {
            "task_id": "t1", "source": "test", "capability": "not_exist",
            "extra": {"disabled": True},
        }
        metas = {"test": _make_meta(["kline_daily"])}
        assert validate_task_capability_contracts([task], metas) == []

    def test_unknown_source_skipped(self):
        """source 不在 metas 中跳过（由 scheduler._validate_provider_and_policy 处理）。"""
        task = {"task_id": "t1", "source": "unknown", "capability": "x"}
        assert validate_task_capability_contracts([task], {}) == []

    def test_no_capability_field_skipped(self):
        """无 capability 字段的 task 不校验。"""
        task = {"task_id": "t1", "source": "test"}
        metas = {"test": _make_meta(["kline_daily"])}
        assert validate_task_capability_contracts([task], metas) == []

    def test_rule1_capability_not_found_error(self):
        """规则1: capability 不存在 -> ERROR（阻断）。"""
        task = {"task_id": "t1", "source": "test", "capability": "not_exist"}
        metas = {"test": _make_meta(["kline_daily"])}
        violations = validate_task_capability_contracts([task], metas)
        assert len(violations) == 1
        assert violations[0].severity == "ERROR"
        assert violations[0].rule_id == "CAP-NOT-FOUND"
        assert violations[0].capability_id == "not_exist"
        assert violations[0].task_id == "t1"

    def test_rule1_task_id_reads_task_id_field(self):
        """task_id 读取优先级：task_id > id > '?'（治本 task_id 读取 bug）。"""
        # 只有 id 字段
        task_id_only = {"id": "from_id", "source": "test", "capability": "not_exist"}
        metas = {"test": _make_meta(["kline_daily"])}
        v = validate_task_capability_contracts([task_id_only], metas)
        assert v[0].task_id == "from_id"
        # task_id 优先于 id
        task_both = {"task_id": "from_task_id", "id": "from_id",
                     "source": "test", "capability": "not_exist"}
        v = validate_task_capability_contracts([task_both], metas)
        assert v[0].task_id == "from_task_id"

    def test_rule2_symbols_null_warn_when_not_declared(self):
        """规则2: symbols=null + supports_symbols_null=False -> WARN。"""
        task = {"task_id": "t1", "source": "test", "capability": "kline_daily",
                "symbols": None}
        metas = {"test": _make_meta(["kline_daily"])}  # 默认 supports_symbols_null=False
        violations = validate_task_capability_contracts([task], metas)
        assert len(violations) == 1
        assert violations[0].severity == "WARN"
        assert violations[0].rule_id == "CAP-NULL-SYMBOLS"

    def test_rule2_symbols_null_pass_when_declared(self):
        """规则2: symbols=null + supports_symbols_null=True -> PASS。"""
        task = {"task_id": "t1", "source": "test", "capability": "top10",
                "symbols": None}
        metas = {"test": _make_meta([
            CapabilityContract("top10", supports_symbols_null=True),
        ])}
        assert validate_task_capability_contracts([task], metas) == []

    def test_rule2_symbols_non_null_skipped(self):
        """规则2: symbols 非 null 不校验。"""
        task = {"task_id": "t1", "source": "test", "capability": "kline_daily",
                "symbols": ["000001.SZ"]}
        metas = {"test": _make_meta(["kline_daily"])}
        assert validate_task_capability_contracts([task], metas) == []

    def test_rule3_incremental_warn_when_not_declared(self):
        """规则3: incremental=true + supports_incremental=False -> WARN。"""
        task = {"task_id": "t1", "source": "test", "capability": "macro",
                "symbols": ["000001.SZ"], "extra": {"incremental": True}}
        metas = {"test": _make_meta([
            CapabilityContract("macro", supports_incremental=False),
        ])}
        violations = validate_task_capability_contracts([task], metas)
        assert len(violations) == 1
        assert violations[0].severity == "WARN"
        assert violations[0].rule_id == "CAP-INCREMENTAL"

    def test_rule3_full_refresh_skipped(self):
        """规则3: incremental=false（全量模式）不校验增量。"""
        task = {"task_id": "t1", "source": "test", "capability": "macro",
                "symbols": ["000001.SZ"], "extra": {"incremental": False}}
        metas = {"test": _make_meta([
            CapabilityContract("macro", supports_incremental=False),
        ])}
        assert validate_task_capability_contracts([task], metas) == []

    def test_rule1_error_skips_rule2_rule3(self):
        """规则1 ERROR 后跳过规则2/3（不重复报）。"""
        task = {"task_id": "t1", "source": "test", "capability": "not_exist",
                "symbols": None, "extra": {"incremental": True}}
        metas = {"test": _make_meta(["kline_daily"])}
        violations = validate_task_capability_contracts([task], metas)
        # 只有规则1的 ERROR，规则2/3 不重复报
        assert len(violations) == 1
        assert violations[0].rule_id == "CAP-NOT-FOUND"


class TestHasBlockingViolations:
    """has_blocking_violations / format_violations。"""

    def test_empty_no_blocking(self):
        assert has_blocking_violations([]) is False

    def test_warn_only_no_blocking(self):
        v = [Violation("WARN", "msg", "t1", "cap", "RULE")]
        assert has_blocking_violations(v) is False

    def test_error_blocks(self):
        v = [Violation("ERROR", "msg", "t1", "cap", "RULE")]
        assert has_blocking_violations(v) is True

    def test_mixed_blocks(self):
        v = [
            Violation("WARN", "w", "t1", "c1", "R1"),
            Violation("ERROR", "e", "t2", "c2", "R2"),
        ]
        assert has_blocking_violations(v) is True

    def test_format_violations_empty(self):
        assert format_violations([]) == "无契约违规"

    def test_format_violations_non_empty(self):
        v = [Violation("ERROR", "msg here", "t1", "cap1", "CAP-NOT-FOUND")]
        result = format_violations(v)
        assert "共 1 条违规" in result
        assert "[ERROR]" in result
        assert "CAP-NOT-FOUND" in result
        assert "task=t1" in result
        assert "cap=cap1" in result


# ============== AST 路由能力提取 ==============

_AKSHARE_STYLE = textwrap.dedent('''
    """akshare 风格：frozenset(_AKSHARE_CAPABILITIES)。"""
    _AKSHARE_CAPABILITIES = frozenset({
        "kline_daily", "money_flow", "stock_list",
    })


    class AKShareProvider:
        meta: DataSourceMeta = DataSourceMeta(
            name="akshare", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["kline_daily", "money_flow", "stock_list"],
        )

        def fetch(self, payload, policy):
            capability = payload.extra.get("capability")
            if capability in _AKSHARE_CAPABILITIES:
                pass
''')

_MINIQMT_STYLE = textwrap.dedent('''
    """miniqmt 风格：多字典 _KLINE_CAPABILITIES / _DIRECT_ROUTES。"""
    _KLINE_CAPABILITIES = {
        "kline_daily": "method_a",
        "kline_1min": "method_b",
    }
    _DIRECT_ROUTES = {
        "adj_factor": "_fetch_adj",
        "index_constituent": "_fetch_index",
    }


    class MiniQMTProvider:
        meta: DataSourceMeta = DataSourceMeta(
            name="miniqmt", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["kline_daily", "kline_1min", "adj_factor", "index_constituent"],
        )
''')

_IFIND_STYLE = textwrap.dedent('''
    """ifind 风格：if-elif 链 (capability == "xxx")。"""
    class IFindProvider:
        meta: DataSourceMeta = DataSourceMeta(
            name="ifind", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["daily_valuation", "kline_daily", "money_flow"],
        )

        def fetch(self, payload, policy):
            capability = payload.extra.get("capability")
            if capability == "daily_valuation":
                pass
            elif capability == "kline_daily":
                pass
            elif capability == "money_flow":
                pass
''')

_INCONSISTENT_STYLE = textwrap.dedent('''
    """不一致：路由支持 kline_daily 但 meta 只声明 money_flow；meta 死声明 not_in_route。"""
    _KLINE_CAPABILITIES = {"kline_daily": "method_a"}


    class BadProvider:
        meta: DataSourceMeta = DataSourceMeta(
            name="bad", display_name="t", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
            capabilities=["money_flow", "not_in_route"],
        )
''')

_SYNTAX_ERROR_CONTENT = "class Broken(\n"

_INSTANCE_META_STYLE = textwrap.dedent('''
    """实例级 self.meta = ... (Assign with Attribute target)。"""
    _ROUTES = {"kline_daily": "method"}


    class InstanceMetaProvider:
        def __init__(self):
            self.meta = DataSourceMeta(
                name="inst", display_name="t", auth_type="anonymous",
                requires_process=False, thread_safety="shared", rate_limit_default=0,
                capabilities=["kline_daily"],
            )
''')


class TestExtractRouteCapabilities:
    """extract_route_capabilities / _route_caps_from_tree 路由能力提取。"""

    def test_akshare_frozenset_style(self):
        """akshare 风格：frozenset({...}) 路由变量。"""
        caps = check_route_meta_consistency_content(_AKSHARE_STYLE)
        # akshare 一致，无违规
        assert caps == []

    def test_route_caps_extracted_from_frozenset(self):
        import ast
        tree = ast.parse(_AKSHARE_STYLE)
        caps = _route_caps_from_tree(tree)
        assert caps == {"kline_daily", "money_flow", "stock_list"}

    def test_route_caps_extracted_from_multiple_dicts(self):
        """miniqmt 风格：多个字典变量合并。"""
        import ast
        tree = ast.parse(_MINIQMT_STYLE)
        caps = _route_caps_from_tree(tree)
        assert caps == {"kline_daily", "kline_1min", "adj_factor", "index_constituent"}

    def test_route_caps_extracted_from_if_elif(self):
        """ifind 风格：if-elif 链 (capability == "xxx")。"""
        import ast
        tree = ast.parse(_IFIND_STYLE)
        caps = _route_caps_from_tree(tree)
        assert caps == {"daily_valuation", "kline_daily", "money_flow"}

    def test_route_caps_combined_dict_and_compare(self):
        """混合模式：字典变量 + if-elif 比较都提取。"""
        content = textwrap.dedent('''
            _ROUTES = {"cap_a": "m"}
            def fetch(self, payload, policy):
                capability = payload.extra.get("capability")
                if capability == "cap_b":
                    pass
                elif capability in {"cap_c", "cap_d"}:
                    pass
        ''')
        import ast
        tree = ast.parse(content)
        caps = _route_caps_from_tree(tree)
        assert caps == {"cap_a", "cap_b", "cap_c", "cap_d"}


class TestExtractMetaCapabilities:
    """extract_meta_capabilities / _meta_caps_from_tree meta 能力提取。"""

    def test_meta_caps_from_annassign(self):
        """类属性 meta: DataSourceMeta = ... (AnnAssign) 检测。"""
        import ast
        tree = ast.parse(_MINIQMT_STYLE)
        caps = _meta_caps_from_tree(tree)
        assert caps == {"kline_daily", "kline_1min", "adj_factor", "index_constituent"}

    def test_meta_caps_from_assign_attribute(self):
        """实例级 self.meta = ... (Assign with Attribute target) 检测。"""
        import ast
        tree = ast.parse(_INSTANCE_META_STYLE)
        caps = _meta_caps_from_tree(tree)
        assert caps == {"kline_daily"}

    def test_meta_caps_capability_contract_first_arg(self):
        """CapabilityContract("xxx", ...) 第一参数提取。"""
        content = textwrap.dedent('''
            from src.zephyr.data.provider_base import DataSourceMeta, CapabilityContract

            class P:
                meta: DataSourceMeta = DataSourceMeta(
                    name="p", display_name="t", auth_type="anonymous",
                    requires_process=False, thread_safety="shared", rate_limit_default=0,
                    capabilities=[
                        "str_cap",
                        CapabilityContract("contract_cap", supports_symbols_null=True),
                    ],
                )
        ''')
        import ast
        tree = ast.parse(content)
        caps = _meta_caps_from_tree(tree)
        assert caps == {"str_cap", "contract_cap"}


class TestCheckRouteMetaConsistency:
    """check_route_meta_consistency / check_route_meta_consistency_content 一致性校验。"""

    def test_consistent_akshare_style(self):
        """akshare 风格一致：无违规。"""
        assert check_route_meta_consistency_content(_AKSHARE_STYLE) == []

    def test_consistent_miniqmt_style(self):
        """miniqmt 风格一致：无违规。"""
        assert check_route_meta_consistency_content(_MINIQMT_STYLE) == []

    def test_consistent_ifind_style(self):
        """ifind 风格一致：无违规。"""
        assert check_route_meta_consistency_content(_IFIND_STYLE) == []

    def test_inconsistent_route_not_in_meta(self):
        """路由支持但 meta 遗漏声明（本次 8 条 ERROR 根因）。"""
        violations = check_route_meta_consistency_content(_INCONSISTENT_STYLE)
        assert len(violations) == 2
        # 路由支持 kline_daily 但 meta 遗漏
        assert any("kline_daily" in v and "未声明" in v for v in violations)
        # meta 死声明 not_in_route
        assert any("not_in_route" in v and "死声明" in v for v in violations)

    def test_syntax_error_fail_open(self):
        """语法错误 fail-open 返回空列表。"""
        assert check_route_meta_consistency_content(_SYNTAX_ERROR_CONTENT) == []

    def test_file_path_api_matches_content_api(self, tmp_path: Path):
        """check_route_meta_consistency(file_path) 与 content 版本结果一致。"""
        f = tmp_path / "test_provider.py"
        f.write_text(_AKSHARE_STYLE, encoding="utf-8")
        assert check_route_meta_consistency(f) == check_route_meta_consistency_content(_AKSHARE_STYLE)

    def test_file_not_exist_fail_open(self, tmp_path: Path):
        """文件不存在 fail-open 返回空列表。"""
        non_exist = tmp_path / "not_exist.py"
        assert check_route_meta_consistency(non_exist) == []

    def test_extract_route_capabilities_none_on_missing_file(self, tmp_path: Path):
        """extract_route_capabilities 文件不存在返回 None。"""
        assert extract_route_capabilities(tmp_path / "not_exist.py") is None

    def test_extract_meta_capabilities_none_on_missing_file(self, tmp_path: Path):
        """extract_meta_capabilities 文件不存在返回 None。"""
        assert extract_meta_capabilities(tmp_path / "not_exist.py") is None

    def test_three_real_providers_consistent(self):
        """集成测试：3 个真实 provider 文件全部 CONSISTENT（治本本次 8 条 ERROR 修复后）。"""
        from src.zephyr.shared.io.paths import REPO_ROOT
        providers = [
            ("akshare", REPO_ROOT / "src" / "zephyr" / "data" / "implementations" / "akshare_provider.py"),
            ("miniqmt", REPO_ROOT / "src" / "zephyr" / "data" / "implementations" / "miniqmt_provider.py"),
            ("ifind", REPO_ROOT / "src" / "zephyr" / "data" / "implementations" / "ifind_provider.py"),
        ]
        for name, path in providers:
            if not path.exists():
                pytest.skip(f"{name} provider 文件不存在: {path}")
            violations = check_route_meta_consistency(path)
            assert violations == [], f"{name} provider 路由-meta 不一致: {violations}"
