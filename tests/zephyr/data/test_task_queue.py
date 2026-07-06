"""task_queue 单测（MOD-L00-004 阶段2）。

测试内容：
- load_yaml 从 yaml 加载任务
- _detect_cycle DAG 无环检测
- get_ready_tasks 就绪任务判定
- mark_running/mark_completed/mark_failed 状态变更
- BLOCKED 传播（前置失败→后续 BLOCKED）
- is_done/has_failed/summary 完成检测
- 线程安全

用 tmp_path fixture 隔离测试 yaml。
"""
import threading
import pytest

from src.zephyr.data.task_queue import (
    TaskQueue,
    PENDING,
    RUNNING,
    SUCCESS,
    FAILED,
    BLOCKED,
)


@pytest.fixture
def queue():
    """空 TaskQueue。"""
    return TaskQueue()


class TestLoadYaml:
    """load_yaml 测试。"""

    def test_load_valid_yaml(self, queue, tmp_path):
        yaml_content = """
tasks:
  - task_id: task_a
    table: t1
    source: ifind
    schedule: daily_kline
    dependencies: []
  - task_id: task_b
    table: t2
    source: ifind
    schedule: daily_kline
    dependencies: ["task_a"]
"""
        p = tmp_path / "tasks.yaml"
        p.write_text(yaml_content, encoding="utf-8")
        queue.load_yaml(p)
        assert len(queue.list_all()) == 2

    def test_load_empty_yaml(self, queue, tmp_path):
        """空任务清单应抛 ValueError。"""
        p = tmp_path / "empty.yaml"
        p.write_text("tasks: []", encoding="utf-8")
        with pytest.raises(ValueError):
            queue.load_yaml(p)

    def test_load_real_tasks_yaml(self, queue):
        """加载真实的 config/tasks.yaml。"""
        from pathlib import Path
        real_yaml = Path(__file__).parent.parent.parent.parent / "src" / "zephyr" / "data" / "config" / "tasks.yaml"
        if real_yaml.exists():
            queue.load_yaml(real_yaml)
            tasks = queue.list_all()
            assert len(tasks) == 61
            # adj_factor 应无依赖
            assert queue.get_task("adj_factor_incremental")["dependencies"] == []
            # kline_daily_hfq 应依赖 adj_factor
            assert "adj_factor_incremental" in queue.get_task("kline_daily_hfq_incremental")["dependencies"]


class TestDagCycleDetection:
    """DAG 无环检测测试。"""

    def test_no_cycle(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.add_task({"task_id": "c", "dependencies": ["b"]})
        # 无异常即通过（load_yaml 会检测，但 add_task 不检测）
        # 手动检测
        assert queue._detect_cycle() is None

    def test_has_cycle(self, queue):
        queue.add_task({"task_id": "a", "dependencies": ["c"]})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.add_task({"task_id": "c", "dependencies": ["b"]})
        cycle = queue._detect_cycle()
        assert cycle is not None
        assert len(cycle) >= 3

    def test_self_cycle(self, queue):
        queue.add_task({"task_id": "a", "dependencies": ["a"]})
        cycle = queue._detect_cycle()
        assert cycle is not None

    def test_cycle_raises_on_load(self, queue, tmp_path):
        """load_yaml 时有环应抛 ValueError。"""
        yaml_content = """
tasks:
  - task_id: a
    dependencies: ["c"]
  - task_id: b
    dependencies: ["a"]
  - task_id: c
    dependencies: ["b"]
"""
        p = tmp_path / "cycle.yaml"
        p.write_text(yaml_content, encoding="utf-8")
        with pytest.raises(ValueError, match="有环"):
            queue.load_yaml(p)


class TestGetReadyTasks:
    """get_ready_tasks 测试。"""

    def test_no_deps_ready(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": []})
        ready = queue.get_ready_tasks()
        assert set(ready) == {"a", "b"}

    def test_with_deps_not_ready(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        ready = queue.get_ready_tasks()
        assert ready == ["a"]  # b 依赖 a，a 未完成

    def test_with_deps_ready_after_complete(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.mark_running("a")
        assert queue.get_ready_tasks() == []  # a 在跑，b 不就绪
        queue.mark_completed("a")
        ready = queue.get_ready_tasks()
        assert ready == ["b"]  # a 完成，b 就绪

    def test_blocked_on_failure(self, queue):
        """前置失败 → 后续 BLOCKED。"""
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.mark_failed("a")
        ready = queue.get_ready_tasks()
        assert ready == []  # b 不应就绪
        assert queue.get_status("b") == BLOCKED

    def test_multi_deps_all_required(self, queue):
        """多个前置需全部 SUCCESS。"""
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": []})
        queue.add_task({"task_id": "c", "dependencies": ["a", "b"]})
        queue.mark_completed("a")
        ready = queue.get_ready_tasks()
        assert ready == ["b"]  # c 不就绪（b 未完成）
        queue.mark_completed("b")
        ready = queue.get_ready_tasks()
        assert ready == ["c"]


class TestStatusChanges:
    """状态变更测试。"""

    def test_mark_running(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.mark_running("a")
        assert queue.get_status("a") == RUNNING

    def test_mark_completed(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.mark_completed("a")
        assert queue.get_status("a") == SUCCESS

    def test_mark_failed(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.mark_failed("a")
        assert queue.get_status("a") == FAILED

    def test_unknown_task_raises(self, queue):
        with pytest.raises(KeyError):
            queue.mark_running("nonexistent")

    def test_reset_single(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.mark_completed("a")
        queue.reset("a")
        assert queue.get_status("a") == PENDING

    def test_reset_all(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": []})
        queue.mark_completed("a")
        queue.mark_failed("b")
        queue.reset()
        assert queue.get_status("a") == PENDING
        assert queue.get_status("b") == PENDING


class TestCompletion:
    """完成检测测试。"""

    def test_is_done_all_success(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        assert not queue.is_done()
        queue.mark_completed("a")
        assert not queue.is_done()
        queue.mark_completed("b")
        assert queue.is_done()

    def test_is_done_with_failure(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.mark_failed("a")
        queue.get_ready_tasks()  # 触发 b → BLOCKED
        assert queue.is_done()  # FAILED + BLOCKED 都是终态

    def test_has_failed(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        assert not queue.has_failed()
        queue.mark_failed("a")
        assert queue.has_failed()

    def test_summary(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": ["a"]})
        queue.add_task({"task_id": "c", "dependencies": []})
        queue.mark_completed("a")
        queue.mark_running("c")
        s = queue.summary()
        assert s.get(SUCCESS) == 1
        assert s.get(RUNNING) == 1
        assert s.get(PENDING) == 1


class TestThreadSafety:
    """线程安全测试。"""

    def test_concurrent_mark_complete(self, queue):
        queue.add_task({"task_id": "a", "dependencies": []})
        queue.add_task({"task_id": "b", "dependencies": []})

        def worker(tid):
            queue.mark_running(tid)
            queue.mark_completed(tid)

        threads = [threading.Thread(target=worker, args=(t,)) for t in ["a", "b"]]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert queue.get_status("a") == SUCCESS
        assert queue.get_status("b") == SUCCESS
