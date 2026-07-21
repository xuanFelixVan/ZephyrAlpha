# [A_test] module_id: MOD-GOV_auto_task_generator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_auto_task_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_auto_task_generator.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.trading.auto_task_generator import AutoTaskGenerator


class TestAutoTaskGeneratorInit:
    def test_default_init(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        assert gen.stats == {"generated": 0, "submitted": 0, "skipped": 0}
        assert gen._max_batch == 12
        assert gen._max_queue_depth == 50

    def test_custom_params(self, tmp_path):
        gen = AutoTaskGenerator(
            project_root=tmp_path,
            max_batch=5,
            max_queue_depth=20,
            cooldown_s=60.0,
        )
        assert gen._max_batch == 5
        assert gen._max_queue_depth == 20
        assert gen._cooldown == 60.0

    def test_project_root_as_string(self, tmp_path):
        gen = AutoTaskGenerator(project_root=str(tmp_path))
        assert gen._root == tmp_path


class TestAutoTaskGeneratorScanSources:
    def test_scan_finds_py_files(self, tmp_path):
        src = tmp_path / "src" / "zephyr" / "mypkg"
        src.mkdir(parents=True)
        (src / "mod1.py").write_text("def foo(): pass", encoding="utf-8")
        (src / "mod2.py").write_text("class Bar: pass", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path, max_queue_depth=50)
        gen._scan_sources()
        assert len(gen._file_queue) >= 2

    def test_scan_respects_queue_depth(self, tmp_path):
        src = tmp_path / "src" / "zephyr" / "pkg"
        src.mkdir(parents=True)
        for i in range(10):
            (src / f"mod{i}.py").write_text(f"x{i} = 1", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path, max_queue_depth=3)
        gen._scan_sources()
        assert len(gen._file_queue) <= 3

    def test_scan_deduplicates(self, tmp_path):
        src = tmp_path / "src" / "zephyr" / "pkg"
        src.mkdir(parents=True)
        (src / "unique.py").write_text("x = 1", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path)
        gen._scan_sources()
        first_count = len(gen._file_queue)
        gen._scan_sources()
        assert len(gen._file_queue) == first_count


class TestAutoTaskGeneratorFileToTasks:
    def test_py_file_generates_tasks(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("src/zephyr/mypkg/analyzer.py"), "def analyze(): pass")
        assert len(tasks) >= 2
        capabilities = [t[1] for t in tasks]
        assert "task_classification" in capabilities
        assert "tag_completion" in capabilities

    def test_py_file_short_name_no_naming(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("src/zephyr/mypkg/ab.py"), "x = 1")
        capabilities = [t[1] for t in tasks]
        assert "naming_suggest" not in capabilities

    def test_py_file_long_name_includes_naming(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("src/zephyr/mypkg/analyzer.py"), "x = 1")
        capabilities = [t[1] for t in tasks]
        assert "naming_suggest" in capabilities

    def test_yaml_file_generates_tasks(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("arch/model.yaml"), "key: value")
        assert len(tasks) == 2
        capabilities = [t[1] for t in tasks]
        assert "summary_extraction" in capabilities
        assert "tag_completion" in capabilities

    def test_md_file_generates_tasks(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("docs/readme.md"), "# Hello")
        assert len(tasks) == 2
        capabilities = [t[1] for t in tasks]
        assert "summary_extraction" in capabilities

    def test_unknown_extension_no_tasks(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        tasks = gen._file_to_tasks(Path("data/file.csv"), "a,b,c")
        assert len(tasks) == 0


class TestAutoTaskGeneratorDrainQueue:
    def test_drain_with_none_scheduler(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        gen._file_queue.append(tmp_path / "fake.py")
        result = gen._drain_queue(None)
        assert result == 0

    def test_drain_submits_tasks(self, tmp_path):
        src = tmp_path / "src" / "zephyr" / "pkg"
        src.mkdir(parents=True)
        py_file = src / "mod.py"
        py_file.write_text("def hello(): pass", encoding="utf-8")

        gen = AutoTaskGenerator(project_root=tmp_path, max_batch=10)
        gen._file_queue.append(py_file)
        scheduler = MagicMock()
        count = gen._drain_queue(scheduler)
        assert count >= 1
        assert scheduler.enqueue.call_count >= 1

    def test_drain_skips_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path)
        gen._file_queue.append(empty_file)
        scheduler = MagicMock()
        count = gen._drain_queue(scheduler)
        assert count == 0
        assert gen._stats["skipped"] >= 1


class TestAutoTaskGeneratorGenerateAndSubmit:
    def test_generate_and_submit_cooldown(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path, cooldown_s=9999.0)
        gen._last_scan_ts = 9999999999.0
        result = gen.generate_and_submit(MagicMock())
        assert result == 0

    def test_generate_and_submit_force(self, tmp_path):
        src = tmp_path / "src" / "zephyr" / "pkg"
        src.mkdir(parents=True)
        (src / "mod.py").write_text("x = 1", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path, cooldown_s=9999.0, max_batch=10)
        result = gen.generate_and_submit(MagicMock(), force=True)
        assert result >= 1


class TestAutoTaskGeneratorFileHash:
    def test_file_hash_deterministic(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        h1 = AutoTaskGenerator._file_hash(f)
        h2 = AutoTaskGenerator._file_hash(f)
        assert h1 == h2
        assert len(h1) == 16

    def test_file_hash_different_files(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x = 1", encoding="utf-8")
        f2.write_text("y = 2", encoding="utf-8")
        assert AutoTaskGenerator._file_hash(f1) != AutoTaskGenerator._file_hash(f2)


class TestAutoTaskGeneratorReadFileSnippet:
    def test_read_existing_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("hello world", encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path)
        content = gen._read_file_snippet(f)
        assert content == "hello world"

    def test_read_nonexistent_file(self, tmp_path):
        gen = AutoTaskGenerator(project_root=tmp_path)
        content = gen._read_file_snippet(tmp_path / "nonexistent.py")
        assert content == ""

    def test_read_truncates_long_file(self, tmp_path):
        f = tmp_path / "long.py"
        f.write_text("x" * 2000, encoding="utf-8")
        gen = AutoTaskGenerator(project_root=tmp_path)
        content = gen._read_file_snippet(f, max_chars=100)
        assert len(content) == 100
