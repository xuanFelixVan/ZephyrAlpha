# [A_test] module_id: SRC-TST-1711 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_symbol_index
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_symbol_index.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path

from zephyr.gov_code_quality.code_dedup.symbol_index import SymbolIndex


class TestSymbolIndex:
    def test_instantiation(self):
        si = SymbolIndex()
        assert si._functions == {}
        assert si._classes == {}
        assert si._imports == {}

    def test_index_file_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("import os\nfrom pathlib import Path\n\ndef hello():\n    pass\n\nclass MyClass:\n    pass\n")
            f.flush()
            path = f.name
        try:
            si = SymbolIndex()
            si.index_file(path)
            assert len(si.lookup_function("hello")) == 1
            assert len(si.lookup_class("MyClass")) == 1
            assert len(si.lookup_import("os")) == 1
            assert len(si.lookup_import("pathlib")) == 1
        finally:
            Path(path).unlink()

    def test_index_file_nonexistent(self):
        si = SymbolIndex()
        si.index_file("/nonexistent/file.py")
        assert si.stats()["functions"] == 0

    def test_index_file_non_python(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as f:
            f.write("not python")
            f.flush()
            path = f.name
        try:
            si = SymbolIndex()
            si.index_file(path)
            assert si.stats()["functions"] == 0
        finally:
            Path(path).unlink()

    def test_index_file_syntax_error(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def broken(:\n")
            f.flush()
            path = f.name
        try:
            si = SymbolIndex()
            si.index_file(path)
            assert si.stats()["functions"] == 0
        finally:
            Path(path).unlink()

    def test_lookup_function_not_found(self):
        si = SymbolIndex()
        assert si.lookup_function("nonexistent") == []

    def test_lookup_class_not_found(self):
        si = SymbolIndex()
        assert si.lookup_class("nonexistent") == []

    def test_lookup_import_not_found(self):
        si = SymbolIndex()
        assert si.lookup_import("nonexistent") == []

    def test_stats_empty(self):
        si = SymbolIndex()
        stats = si.stats()
        assert stats["functions"] == 0
        assert stats["classes"] == 0
        assert stats["imports"] == 0

    def test_stats_after_indexing(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("import os\n\ndef foo():\n    pass\n\ndef bar():\n    pass\n\nclass Baz:\n    pass\n")
            f.flush()
            path = f.name
        try:
            si = SymbolIndex()
            si.index_file(path)
            stats = si.stats()
            assert stats["functions"] == 2
            assert stats["classes"] == 1
            assert stats["imports"] == 1
        finally:
            Path(path).unlink()

    def test_multiple_files_same_function(self):
        si = SymbolIndex()
        for name in ["a", "b"]:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
                f.write("def common_func():\n    pass\n")
                f.flush()
                si.index_file(f.name)
        result = si.lookup_function("common_func")
        assert len(result) == 2

    def test_index_file_path_object(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("def test_func():\n    pass\n")
            f.flush()
            path = Path(f.name)
        try:
            si = SymbolIndex()
            si.index_file(path)
            assert len(si.lookup_function("test_func")) == 1
        finally:
            path.unlink()
