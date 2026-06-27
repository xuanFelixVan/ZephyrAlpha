"""生成各批次的文件清单——基于 git status --porcelain 输出。

批次:
  2: docs/ 修改文件（排除 _working/）
  3: scripts/ 修改文件
  4: src/ 修改文件
  5: tests/ 修改文件 + 新增 P2 回归测试
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git_status() -> list[str]:
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    return r.stdout.splitlines()


def parse(status_lines: list[str]) -> dict[str, list[str]]:
    """返回 {category: [relpath, ...]}."""
    out: dict[str, list[str]] = {
        "docs_mod": [], "scripts_mod": [], "src_mod": [], "tests_mod": [],
        "tests_new_p2": [],
    }
    p2_new_tests = {
        "tests/red_blue/test_concurrent_mv_guard.py",
        "tests/test_git_commit_concurrent.py",
        "tests/test_task_repo_gateway_e2e.py",
    }
    for line in status_lines:
        if not line.strip():
            continue
        xy = line[:2]
        path = line[3:].strip().strip('"')
        # rename
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip().strip('"')
        # skip untracked for now (handled separately)
        if xy == "??":
            if path in p2_new_tests:
                out["tests_new_p2"].append(path)
            continue
        # skip deleted (handled by git add automatically)
        # categorize
        if path.startswith("docs/_working/"):
            continue  # already committed in batch 1
        if path.startswith("docs/"):
            out["docs_mod"].append(path)
        elif path.startswith("scripts/"):
            out["scripts_mod"].append(path)
        elif path.startswith("src/"):
            out["src_mod"].append(path)
        elif path.startswith("tests/"):
            out["tests_mod"].append(path)
    return out


def write_list(name: str, files: list[str]) -> None:
    p = ROOT / "docs" / "_working" / f"_list_{name}.txt"
    p.write_text("\n".join(files) + "\n", encoding="utf-8")
    print(f"  {name}: {len(files)} files -> {p.relative_to(ROOT)}")


def main() -> None:
    lines = git_status()
    cats = parse(lines)
    print("== 文件清单生成 ==")
    write_list("commit2_docs", cats["docs_mod"])
    write_list("commit3_scripts", cats["scripts_mod"])
    write_list("commit4_src", cats["src_mod"])
    write_list("commit5_tests_mod", cats["tests_mod"])
    write_list("commit6_tests_new", cats["tests_new_p2"])
    total = sum(len(v) for v in cats.values())
    print(f"== 总计: {total} files ==")


if __name__ == "__main__":
    main()
