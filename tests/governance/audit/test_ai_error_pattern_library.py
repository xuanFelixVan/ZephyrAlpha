# [A_test] module_id: SRC-TST-3005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_ai_error_pattern_library.py — P4-1 ai_error_pattern_library 单测。

覆盖 7 个测试类 / 47 测试：
1. ``TestErrorPatternDataclass`` (6) — from_dict / dominant_severity / unexpected_ratio
2. ``TestLibraryLoad`` (5) — 空路径 / 不存在文件 / 有效 JSON / 损坏 JSON / 字段缺失
3. ``TestLibraryQuery`` (13) — get_pattern / find_patterns / top_patterns / match_pattern / is_known_pattern
4. ``TestSuggestAction`` (11) — 各 persistence×severity 组合 / source 补充 / 未知 pattern_id
5. ``TestLibraryProperties`` (7) — total_patterns / total_events / last_updated / is_empty / reload
6. ``TestGetDefaultLibrary`` (3) — 默认路径 / 自定义 project_root / 缺失文件
7. ``TestComputePatternIdIntegration`` (1) — 验证 match_pattern 与 compute_error_pattern_id 一致性

P4-1（#ARCH-PREVENTABILITY-LAYER-001 Phase 4，2026-07-20）
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.governance.audit.ai_error_pattern_library import (
    AIErrorPatternLibrary,
    ErrorPattern,
    get_default_library,
)
from zephyr.governance.audit.error_pattern_consumer_reconciler import (
    compute_error_pattern_id,
)


def _make_pattern_dict(
    pattern_id: str = "EP-aabbccddeeff0011",
    error_type: str = "ConnectionError",
    persistence: str = "transient",
    source: str = "dependency",
    count: int = 5,
    first_seen: str = "2026-07-20T10:00:00+00:00",
    last_seen: str = "2026-07-20T11:00:00+00:00",
    expectation_dist: dict | None = None,
    severity_dist: dict | None = None,
) -> dict:
    """构造聚合 JSON 中单条 pattern 的 dict。

    注意：使用 ``is None`` 判断而非 ``or``，避免空 dict {} 被当作 falsy
    替换为默认值（修复回归：test_unexpected_ratio_zero_total 失败）。
    """
    return {
        "pattern_id": pattern_id,
        "error_type": error_type,
        "persistence": persistence,
        "source": source,
        "count": count,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "expectation_dist": expectation_dist if expectation_dist is not None else {"expected": 2, "unexpected": 3},
        "severity_dist": severity_dist if severity_dist is not None else {"degraded": 1, "blocking": 4},
    }


def _write_aggregate(path: Path, patterns: list[dict], total_events: int = 0, last_updated: int = 1700000000) -> None:
    """构造完整的聚合 JSON 文件并写入 path。"""
    data = {
        "version": "1.0",
        "last_updated": last_updated,
        "total_events": total_events,
        "patterns": patterns,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# =====================================================================
# 1. TestErrorPatternDataclass — from_dict / dominant_severity / unexpected_ratio
# =====================================================================


class TestErrorPatternDataclass:
    """ErrorPattern dataclass 行为测试。"""

    def test_from_dict_full(self) -> None:
        d = _make_pattern_dict()
        pat = ErrorPattern.from_dict(d)
        assert pat.pattern_id == "EP-aabbccddeeff0011"
        assert pat.error_type == "ConnectionError"
        assert pat.persistence == "transient"
        assert pat.source == "dependency"
        assert pat.count == 5
        assert pat.first_seen.startswith("2026-07-20")
        assert pat.last_seen.startswith("2026-07-20")
        assert pat.expectation_dist == {"expected": 2, "unexpected": 3}
        assert pat.severity_dist == {"degraded": 1, "blocking": 4}

    def test_from_dict_missing_fields(self) -> None:
        """缺失字段使用默认值（fail-open）。"""
        pat = ErrorPattern.from_dict({"pattern_id": "EP-x"})
        assert pat.pattern_id == "EP-x"
        assert pat.error_type == ""
        assert pat.persistence == ""
        assert pat.source == ""
        assert pat.count == 0
        assert pat.first_seen == ""
        assert pat.last_seen == ""
        assert pat.expectation_dist == {}
        assert pat.severity_dist == {}

    def test_from_dict_type_mismatch(self) -> None:
        """类型不匹配尝试强转，转换失败跳过该字段。"""
        d = {
            "pattern_id": "EP-y",
            "error_type": "ValueError",
            "count": "not_a_number",  # 无法转 int
            "expectation_dist": "not_a_dict",  # 非 dict
            "severity_dist": {"fatal": "3", "blocking": 2},  # 混合类型
        }
        pat = ErrorPattern.from_dict(d)
        assert pat.count == 0  # 转换失败回退默认
        assert pat.expectation_dist == {}  # 非 dict 回退空
        assert pat.severity_dist == {"fatal": 3, "blocking": 2}  # 字符串数字强转

    def test_dominant_severity_basic(self) -> None:
        pat = ErrorPattern.from_dict(_make_pattern_dict(severity_dist={"degraded": 1, "blocking": 4, "fatal": 2}))
        assert pat.dominant_severity == "blocking"

    def test_dominant_severity_tie(self) -> None:
        """平局取字典序最小（degraded < fatal）。"""
        pat = ErrorPattern.from_dict(_make_pattern_dict(severity_dist={"fatal": 3, "degraded": 3}))
        assert pat.dominant_severity == "degraded"

    def test_dominant_severity_empty(self) -> None:
        """空 severity_dist 返回 'unknown'。"""
        pat = ErrorPattern.from_dict(_make_pattern_dict(severity_dist={}))
        assert pat.dominant_severity == "unknown"

    def test_unexpected_ratio_basic(self) -> None:
        pat = ErrorPattern.from_dict(
            _make_pattern_dict(expectation_dist={"expected": 2, "unexpected": 3, "unknown": 5})
        )
        # 3 / (2 + 3 + 5) = 0.3
        assert pat.unexpected_ratio == pytest.approx(0.3)

    def test_unexpected_ratio_zero_unexpected(self) -> None:
        pat = ErrorPattern.from_dict(_make_pattern_dict(expectation_dist={"expected": 5, "unknown": 5}))
        assert pat.unexpected_ratio == 0.0

    def test_unexpected_ratio_zero_total(self) -> None:
        """空 expectation_dist 返回 0.0（关键回归点）。"""
        pat = ErrorPattern.from_dict(_make_pattern_dict(expectation_dist={}))
        assert pat.unexpected_ratio == 0.0


# =====================================================================
# 2. TestLibraryLoad — 加载场景
# =====================================================================


class TestLibraryLoad:
    """AIErrorPatternLibrary 加载行为测试（fail-open）。"""

    def test_load_file_not_exist(self, tmp_path: Path) -> None:
        """文件不存在时降级为空库。"""
        lib = AIErrorPatternLibrary(tmp_path / "missing.json")
        assert lib.is_empty is True
        assert lib.total_patterns == 0
        assert lib.total_events == 0
        assert lib.last_updated == 0

    def test_load_valid_json(self, tmp_path: Path) -> None:
        """有效 JSON 正常加载。"""
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [_make_pattern_dict()], total_events=5)
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is False
        assert lib.total_patterns == 1
        assert lib.total_events == 5
        assert lib.last_updated == 1700000000

    def test_load_corrupt_json(self, tmp_path: Path) -> None:
        """JSON 损坏降级为空库。"""
        path = tmp_path / "aggregated_patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not valid json", encoding="utf-8")
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is True

    def test_load_root_not_dict(self, tmp_path: Path) -> None:
        """根不是 dict 降级为空库。"""
        path = tmp_path / "aggregated_patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is True

    def test_load_patterns_field_not_list(self, tmp_path: Path) -> None:
        """patterns 字段非 list 降级为空库。"""
        path = tmp_path / "aggregated_patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": "1.0", "patterns": "should_be_list"}), encoding="utf-8")
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is True

    def test_load_skips_pattern_without_id(self, tmp_path: Path) -> None:
        """pattern_id 为空的条目被跳过。"""
        path = tmp_path / "aggregated_patterns.json"
        d1 = _make_pattern_dict()
        d2 = _make_pattern_dict()
        d2["pattern_id"] = ""  # 空 ID
        _write_aggregate(path, [d1, d2])
        lib = AIErrorPatternLibrary(path)
        assert lib.total_patterns == 1  # 只加载了 d1


# =====================================================================
# 3. TestLibraryQuery — 查询方法
# =====================================================================


class TestLibraryQuery:
    """AIErrorPatternLibrary 查询方法测试。"""

    def _build_lib(self, tmp_path: Path) -> AIErrorPatternLibrary:
        pid_aaa = compute_error_pattern_id("ConnectionError", "transient", "dependency")
        pid_bbb = compute_error_pattern_id("ValueError", "permanent", "internal")
        pid_ccc = compute_error_pattern_id("ConnectionError", "intermittent", "server")
        patterns = [
            _make_pattern_dict(
                pattern_id=pid_aaa, error_type="ConnectionError", persistence="transient", source="dependency", count=3
            ),
            _make_pattern_dict(
                pattern_id=pid_bbb, error_type="ValueError", persistence="permanent", source="internal", count=10
            ),
            _make_pattern_dict(
                pattern_id=pid_ccc, error_type="ConnectionError", persistence="intermittent", source="server", count=5
            ),
        ]
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, patterns, total_events=18)
        return AIErrorPatternLibrary(path)

    def test_get_pattern_known(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        pid = compute_error_pattern_id("ValueError", "permanent", "internal")
        pat = lib.get_pattern(pid)
        assert pat is not None
        assert pat.error_type == "ValueError"
        assert pat.count == 10

    def test_get_pattern_unknown(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        assert lib.get_pattern("EP-doesnotexist") is None

    def test_find_patterns_by_error_type(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns(error_type="ConnectionError")
        assert len(result) == 2
        # 按 count 降序：5 在 3 之前
        assert result[0].count == 5
        assert result[1].count == 3

    def test_find_patterns_by_persistence(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns(persistence="permanent")
        assert len(result) == 1
        assert result[0].error_type == "ValueError"

    def test_find_patterns_by_source(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns(source="dependency")
        assert len(result) == 1
        assert result[0].persistence == "transient"

    def test_find_patterns_combined(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns(error_type="ConnectionError", persistence="transient")
        assert len(result) == 1
        assert result[0].source == "dependency"

    def test_find_patterns_no_match(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns(error_type="DoesNotExist")
        assert result == []

    def test_find_patterns_no_filter_returns_all(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.find_patterns()
        assert len(result) == 3
        # 按 count 降序：10, 5, 3
        assert [p.count for p in result] == [10, 5, 3]

    def test_top_patterns_basic(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.top_patterns(n=2)
        assert len(result) == 2
        assert result[0].count == 10
        assert result[1].count == 5

    def test_top_patterns_n_larger_than_size(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        result = lib.top_patterns(n=10)
        assert len(result) == 3

    def test_top_patterns_n_zero(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        assert lib.top_patterns(n=0) == []

    def test_top_patterns_n_negative(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        assert lib.top_patterns(n=-1) == []

    def test_match_pattern_known(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        pat = lib.match_pattern("ConnectionError", "transient", "dependency")
        assert pat is not None
        assert pat.count == 3

    def test_match_pattern_unknown(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        pat = lib.match_pattern("DoesNotExist", "transient", "dependency")
        assert pat is None

    def test_is_known_pattern_true(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        assert lib.is_known_pattern("ConnectionError", "transient", "dependency") is True

    def test_is_known_pattern_false(self, tmp_path: Path) -> None:
        lib = self._build_lib(tmp_path)
        assert lib.is_known_pattern("DoesNotExist", "transient", "dependency") is False


# =====================================================================
# 4. TestSuggestAction — 修复建议规则
# =====================================================================


class TestSuggestAction:
    """AIErrorPatternLibrary.suggest_action / _suggest_action_for_pattern 测试。"""

    def _make_lib_with(self, tmp_path: Path, pat_dict: dict) -> AIErrorPatternLibrary:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [pat_dict])
        return AIErrorPatternLibrary(path)

    def test_permanent_blocking(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E1", "permanent", "internal")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="permanent",
                source="internal",
                severity_dist={"blocking": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "立即修复" in action
        assert "permanent" in action
        assert "检查内部逻辑" in action  # source=internal hint

    def test_permanent_fatal(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E2", "permanent", "internal")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="permanent",
                source="internal",
                severity_dist={"fatal": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "立即修复" in action
        assert "fatal" in action

    def test_permanent_degraded(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E3", "permanent", "internal")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="permanent",
                source="internal",
                severity_dist={"degraded": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "排查根因" in action

    def test_intermittent(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E4", "intermittent", "server")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="intermittent",
                source="server",
                severity_dist={"blocking": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "监控" in action
        assert "intermittent" in action
        assert "服务端" in action  # source=server hint

    def test_transient_blocking(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E5", "transient", "dependency")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="transient",
                source="dependency",
                severity_dist={"blocking": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "重试" in action
        assert "指数退避" in action
        assert "依赖服务" in action  # source=dependency hint

    def test_transient_fatal(self, tmp_path: Path) -> None:
        """transient + fatal 同样走 '重试 + 指数退避' 分支。"""
        pid = compute_error_pattern_id("E6", "transient", "dependency")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="transient",
                source="dependency",
                severity_dist={"fatal": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "重试" in action
        assert "fatal" in action

    def test_transient_degraded(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E7", "transient", "internal")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="transient",
                source="internal",
                severity_dist={"degraded": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "监控趋势" in action

    def test_source_client_hint(self, tmp_path: Path) -> None:
        pid = compute_error_pattern_id("E8", "permanent", "client")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="permanent",
                source="client",
                severity_dist={"blocking": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "客户端输入" in action

    def test_unknown_source_no_hint(self, tmp_path: Path) -> None:
        """未知 source 不追加 hint。"""
        pid = compute_error_pattern_id("E9", "transient", "weird_source")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="transient",
                source="weird_source",
                severity_dist={"degraded": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "监控趋势" in action
        assert "；" not in action  # 无 hint 不加分号

    def test_unknown_pattern_id(self, tmp_path: Path) -> None:
        lib = self._make_lib_with(tmp_path, _make_pattern_dict())
        action = lib.suggest_action("EP-doesnotexist")
        assert "未知模式" in action

    def test_unknown_persistence(self, tmp_path: Path) -> None:
        """persistence 不在已知枚举中走 '未知 persistence' 分支。"""
        pid = compute_error_pattern_id("E10", "weird_persistence", "internal")
        lib = self._make_lib_with(
            tmp_path,
            _make_pattern_dict(
                pattern_id=pid,
                persistence="weird_persistence",
                source="internal",
                severity_dist={"degraded": 5},
            ),
        )
        action = lib.suggest_action(pid)
        assert "未知 persistence" in action


# =====================================================================
# 5. TestLibraryProperties — properties / reload
# =====================================================================


class TestLibraryProperties:
    """AIErrorPatternLibrary properties 与 reload 测试。"""

    def test_total_patterns(self, tmp_path: Path) -> None:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [_make_pattern_dict(), _make_pattern_dict(pattern_id="EP-other")])
        lib = AIErrorPatternLibrary(path)
        assert lib.total_patterns == 2

    def test_total_events(self, tmp_path: Path) -> None:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [_make_pattern_dict()], total_events=42)
        lib = AIErrorPatternLibrary(path)
        assert lib.total_events == 42

    def test_total_events_default_zero(self, tmp_path: Path) -> None:
        """total_events 字段缺失时为 0。"""
        path = tmp_path / "aggregated_patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": "1.0", "patterns": []}), encoding="utf-8")
        lib = AIErrorPatternLibrary(path)
        assert lib.total_events == 0

    def test_last_updated(self, tmp_path: Path) -> None:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [], last_updated=1700000123)
        lib = AIErrorPatternLibrary(path)
        assert lib.last_updated == 1700000123

    def test_is_empty_true_when_no_patterns(self, tmp_path: Path) -> None:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [])
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is True

    def test_is_empty_false_when_has_patterns(self, tmp_path: Path) -> None:
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [_make_pattern_dict()])
        lib = AIErrorPatternLibrary(path)
        assert lib.is_empty is False

    def test_reload_picks_up_changes(self, tmp_path: Path) -> None:
        """reload 后从磁盘重新加载，反映最新内容。"""
        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(path, [_make_pattern_dict()], total_events=1)
        lib = AIErrorPatternLibrary(path)
        assert lib.total_patterns == 1

        # 写入新内容
        _write_aggregate(path, [_make_pattern_dict(), _make_pattern_dict(pattern_id="EP-second")], total_events=2)
        # 未 reload 时仍为旧值
        assert lib.total_patterns == 1
        # reload 后反映新值
        lib.reload()
        assert lib.total_patterns == 2
        assert lib.total_events == 2


# =====================================================================
# 6. TestGetDefaultLibrary — get_default_library 工厂
# =====================================================================


class TestGetDefaultLibrary:
    """get_default_library 工厂函数测试。"""

    def test_default_uses_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """None project_root 时使用 cwd。"""
        monkeypatch.chdir(tmp_path)
        # 不创建文件，应返回空库（fail-open）
        lib = get_default_library()
        assert lib.is_empty is True
        # 验证路径正确
        expected_path = tmp_path / ".runtime" / "ai_error_patterns" / "aggregated_patterns.json"
        assert lib.path == expected_path  # noqa: SLF001 — 测试需要验证内部路径

    def test_custom_project_root(self, tmp_path: Path) -> None:
        """显式 project_root 优先。"""
        lib = get_default_library(project_root=tmp_path)
        expected_path = tmp_path / ".runtime" / "ai_error_patterns" / "aggregated_patterns.json"
        assert lib.path == expected_path  # noqa: SLF001
        assert lib.is_empty is True

    def test_loads_existing_file(self, tmp_path: Path) -> None:
        """project_root 下存在聚合文件时正常加载。"""
        patterns_path = tmp_path / ".runtime" / "ai_error_patterns" / "aggregated_patterns.json"
        _write_aggregate(patterns_path, [_make_pattern_dict()], total_events=5)
        lib = get_default_library(project_root=tmp_path)
        assert lib.is_empty is False
        assert lib.total_patterns == 1
        assert lib.total_events == 5


# =====================================================================
# 7. TestComputePatternIdIntegration — match_pattern 与 compute_error_pattern_id 一致性
# =====================================================================


class TestComputePatternIdIntegration:
    """验证 AIErrorPatternLibrary.match_pattern 与 compute_error_pattern_id 一致性。"""

    def test_match_pattern_uses_compute_error_pattern_id(self, tmp_path: Path) -> None:
        """match_pattern 计算的 pattern_id 必须与 compute_error_pattern_id 一致。"""
        # 构造一个库，其中 pattern_id 使用 compute_error_pattern_id 生成
        error_type = "ModuleNotFoundError"
        persistence = "permanent"
        source = "internal"
        expected_pid = compute_error_pattern_id(error_type, persistence, source)

        path = tmp_path / "aggregated_patterns.json"
        _write_aggregate(
            path,
            [
                _make_pattern_dict(
                    pattern_id=expected_pid,
                    error_type=error_type,
                    persistence=persistence,
                    source=source,
                    count=99,
                )
            ],
        )
        lib = AIErrorPatternLibrary(path)

        # 使用三元组 match，应命中 expected_pid 对应的 pattern
        pat = lib.match_pattern(error_type, persistence, source)
        assert pat is not None
        assert pat.pattern_id == expected_pid
        assert pat.count == 99
