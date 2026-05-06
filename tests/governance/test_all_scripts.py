"""治理脚本全集冒烟测试 — 参数化测试 117 个注册脚本

覆盖 D-B-01a~D-B-02（exit code 语义、--help 可用、--warn-only 不崩溃）。
每个注册脚本至少验证 3 个基本命令：
1. --help          → exit 0
2. --warn-only     → exit 0 或 1（不崩溃）
3. --jsonl         → 如支持则输出有效 JSONL（exit 0/1），不支持则 exit 2（不计入失败）
"""

from __future__ import annotations

import json
import subprocess
import sys
import time

import pytest


def _load_test_cases(script_entries: list[dict]) -> list[tuple[str, int, str, str]]:
    return [
        (e["name"], e.get("timeout_seconds", 60), e.get("description", ""), ",".join(e.get("dimensions", [])))
        for e in script_entries
    ]


class TestAllScripts:
    @pytest.fixture(scope="class")
    def test_cases(self, script_entries: list[dict]) -> list[tuple[str, int, str, str]]:
        return _load_test_cases(script_entries)

    def test_script_count(self, test_cases):
        assert len(test_cases) >= 100, f"注册脚本数异常: {len(test_cases)}"

    def test_help_all_scripts(self, repo_root, gov_dir, test_cases):
        failed: list[str] = []
        for script_name, timeout, _, _ in test_cases:
            script_path = gov_dir / script_name
            if not script_path.exists():
                failed.append(f"{script_name}: 文件不存在")
                continue
            r = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=min(timeout, 30),
                cwd=str(repo_root),
                encoding="utf-8",
                errors="replace",
            )
            if r.returncode != 0:
                failed.append(f"{script_name}: --help exit={r.returncode}")
        if failed:
            pytest.fail(f"{len(failed)}/{len(test_cases)} 脚本 --help 失败:\n" + "\n".join(failed[:15]))

    def test_warn_only_all_scripts(self, repo_root, gov_dir, test_cases):
        failed: list[str] = []
        crashed: list[str] = []
        for script_name, timeout, _, _ in test_cases:
            script_path = gov_dir / script_name
            if not script_path.exists():
                continue
            try:
                r = subprocess.run(
                    [sys.executable, str(script_path), "--warn-only"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(repo_root),
                    encoding="utf-8",
                    errors="replace",
                )
            except subprocess.TimeoutExpired:
                failed.append(f"{script_name}: 超时 ({timeout}s)")
                continue
            if r.returncode == 2:
                crashed.append(f"{script_name}: exit=2 stderr={r.stderr[:100]}")
            elif r.returncode not in (0, 1):
                failed.append(f"{script_name}: 异常 exit={r.returncode}")
        msg_parts = []
        if crashed:
            msg_parts.append(f"\n  崩溃脚本 ({len(crashed)}):\n    " + "\n    ".join(crashed[:10]))
        if failed:
            msg_parts.append(f"\n  异常脚本 ({len(failed)}):\n    " + "\n    ".join(failed[:10]))
        if msg_parts:
            pytest.fail("".join(msg_parts))

    def test_jsonl_all_scripts(self, repo_root, gov_dir, test_cases):
        supported = 0
        unsupported = 0
        invalid_jsonl: list[str] = []
        for script_name, timeout, _, _ in test_cases:
            script_path = gov_dir / script_name
            if not script_path.exists():
                continue
            try:
                r = subprocess.run(
                    [sys.executable, str(script_path), "--warn-only", "--jsonl"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(repo_root),
                    encoding="utf-8",
                    errors="replace",
                )
            except subprocess.TimeoutExpired:
                invalid_jsonl.append(f"{script_name}: 超时")
                continue
            if r.returncode == 2:
                unsupported += 1
                continue
            if r.stdout.strip() and r.stdout.strip()[0] == "{":
                supported += 1
                for line in r.stdout.strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "severity" not in data:
                            invalid_jsonl.append(f"{script_name}: JSONL 缺少 severity: {str(data)[:80]}")
                    except json.JSONDecodeError:
                        invalid_jsonl.append(f"{script_name}: 无效 JSONL: {line[:80]}")
            else:
                unsupported += 1
        print(f"\n  --jsonl 支持: {supported}/{supported+unsupported} 脚本")
        if invalid_jsonl:
            pytest.fail(f"{len(invalid_jsonl)} 脚本 JSONL 输出无效:\n" + "\n".join(invalid_jsonl[:10]))


@pytest.mark.slow
class TestAllScriptsWithTiming(TestAllScripts):
    def test_timing_report(self, repo_root, gov_dir, test_cases):
        timings: list[tuple[float, str]] = []
        for script_name, timeout, _, _ in test_cases:
            script_path = gov_dir / script_name
            if not script_path.exists():
                continue
            t0 = time.perf_counter()
            try:
                subprocess.run(
                    [sys.executable, str(script_path), "--warn-only"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(repo_root),
                    encoding="utf-8",
                    errors="replace",
                )
            except subprocess.TimeoutExpired:
                pass
            elapsed = time.perf_counter() - t0
            timings.append((elapsed, script_name))

        timings.sort(reverse=True)
        print("\n  最慢 10 个脚本:")
        for elapsed, name in timings[:10]:
            print(f"    {elapsed:.1f}s  {name}")
