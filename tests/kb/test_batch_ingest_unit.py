# [A_test] module_id: SRC-TST-1979 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-596 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_batch_ingest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
测试套件：批量入库（T-2-14）
==============================
覆盖 ≥ 5 条：
1. 从 YAML 列表批量入库
2. 从 dict 格式批量入库
3. 成功率计算
4. 缺失文件跳过
5. 空 YAML 返回零结果
6. 入库报告 Markdown 输出
7. 从程序列表批量入库
"""


from pathlib import Path

import pytest
import yaml

from zephyr.gov_kb.batch_ingest import BatchIngestor
from zephyr.gov_kb.ingest import IngestGate


@pytest.fixture()
def ingest_gate(kb_root: Path) -> IngestGate:
    return IngestGate(kb_root=kb_root)


@pytest.fixture()
def ingestor(ingest_gate: IngestGate, tmp_path: Path) -> BatchIngestor:
    return BatchIngestor(ingest_gate=ingest_gate, repo_root=tmp_path)


def _make_md(
    tmp_path: Path,
    name: str,
    module_id: str = "KE-600",
    title: str = "测试",
    category: str = "best_practice",
) -> Path:
    body = "这是足够长的测试内容，用于通过最小内容长度检查。" * 5
    content = f"---\nmodule_id: {module_id}\ntitle: {title}\ncategory: {category}\nttl: task_bound\n---\n\n{body}\n"
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_batch_ingest_from_yaml_list(ingestor: BatchIngestor, tmp_path: Path) -> None:
    _make_md(tmp_path, "a.md", "KE-601", "条目A")
    _make_md(tmp_path, "b.md", "KE-602", "条目B")

    yaml_path = tmp_path / "candidates.yaml"
    data = [
        {"module_id": "KE-601", "title": "条目A", "category": "best_practice", "source_file": "a.md", "priority": "P0"},
        {"module_id": "KE-602", "title": "条目B", "category": "best_practice", "source_file": "b.md", "priority": "P1"},
    ]
    yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8", newline="\n")

    report = ingestor.ingest_from_yaml(yaml_path)
    assert report.total == 2
    assert report.succeeded == 2
    assert report.success_rate == 1.0


def test_batch_ingest_from_yaml_dict(ingestor: BatchIngestor, tmp_path: Path) -> None:
    _make_md(tmp_path, "c.md", "KE-603", "条目C")

    yaml_path = tmp_path / "candidates.yaml"
    data = {
        "KE-603": {
            "title": "条目C",
            "category": "best_practice",
            "source_file": "c.md",
            "priority": "P0",
        },
    }
    yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8", newline="\n")

    report = ingestor.ingest_from_yaml(yaml_path)
    assert report.total == 1
    assert report.succeeded == 1


def test_batch_ingest_missing_files_skipped(ingestor: BatchIngestor, tmp_path: Path) -> None:
    yaml_path = tmp_path / "candidates.yaml"
    data = [
        {
            "module_id": "KE-604",
            "title": "Missing",
            "category": "test",
            "source_file": "nonexistent.md",
            "priority": "P0",
        },
    ]
    yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8", newline="\n")

    report = ingestor.ingest_from_yaml(yaml_path)
    assert report.skipped >= 1


def test_batch_ingest_empty_yaml(ingestor: BatchIngestor, tmp_path: Path) -> None:
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("[]", encoding="utf-8", newline="\n")

    report = ingestor.ingest_from_yaml(yaml_path)
    assert report.total == 0


def test_batch_ingest_nonexistent_yaml(ingestor: BatchIngestor, tmp_path: Path) -> None:
    report = ingestor.ingest_from_yaml(tmp_path / "ghost.yaml")
    assert report.failed == 1


def test_batch_ingest_report_markdown(ingestor: BatchIngestor, tmp_path: Path) -> None:
    _make_md(tmp_path, "d.md", "KE-605", "条目D")

    yaml_path = tmp_path / "candidates.yaml"
    data = [
        {"module_id": "KE-605", "title": "条目D", "category": "best_practice", "source_file": "d.md", "priority": "P0"},
    ]
    yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8", newline="\n")

    report = ingestor.ingest_from_yaml(yaml_path)
    md = report.to_markdown()
    assert "批量入库报告" in md
    assert "KE-605" in md


def test_batch_ingest_from_list(ingestor: BatchIngestor, tmp_path: Path) -> None:
    _make_md(tmp_path, "e.md", "KE-606", "条目E")

    candidates = [
        {"module_id": "KE-606", "title": "条目E", "category": "best_practice", "source_file": "e.md", "priority": "P0"},
    ]
    report = ingestor.ingest_from_list(candidates)
    assert report.total == 1
    assert report.succeeded == 1
