# [TTL] permanent
# [TESTS] tests/gov/governance/test_commit_message_utf8_chain.py
"""commit 消息编码链 UTF-8 强制红证测试（2026-10-10 st-chief3-20261009）。

工单来源：呈报表⑨"queue 通道 message-file 编码偶发乱码（工法缺陷登记）"。
红证判据（修前必红/修后全绿）：
  1. run_subprocess_hidden 缺省 encoding：Windows text=True 继承 locale(cp936)
     时，子进程 UTF-8 中文输出被 GBK 误读——修后缺省 utf-8 必须逐字往返。
  2. --message-file GBK 误写（双字节恰为合法 UTF-8 的"偶发乱码"确定性形态）
     必须拒读（exit 1），禁静默解码成乱码。
  3. BOM 化写端（PowerShell 5.1 Set-Content 常发 UTF-16LE）确定性转码接受。
  4. git log 中文 commit 消息读回（check_commit_message._get_pr_commits）
     必须按 utf-8 解码逐字一致（修前 GBK 误读=消息账对账失真）。
  5. text=False 字节模式不受 encoding 缺省影响（git show 字节比较场景契约）。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _REPO_ROOT / "scripts"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def git_commit_mod():
    return _load_module(_SCRIPTS / "git_commit.py", "git_commit_mod_under_test")


@pytest.fixture(scope="module")
def ccm_mod():
    sys.path.insert(0, str(_SCRIPTS / "governance"))
    return _load_module(_SCRIPTS / "governance" / "check_commit_message.py", "ccm_mod_under_test")


def test_run_subprocess_hidden_defaults_utf8():
    """缺省 encoding=utf-8：子进程 UTF-8 中文输出逐字往返（修前 cp936 必红）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    child = "import sys; sys.stdout.reconfigure(encoding='utf-8');print('网关中文ok')"
    r = run_subprocess_hidden([sys.executable, "-c", child])
    assert r.returncode == 0
    assert r.stdout.strip() == "网关中文ok"


def test_run_subprocess_hidden_bytes_mode_untouched():
    """text=False 时 encoding 缺省不得注入（字节模式契约不被破坏）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    r = run_subprocess_hidden([sys.executable, "-c", "print('bytes-mode')"], text=False)
    assert isinstance(r.stdout, bytes)
    assert b"bytes-mode" in r.stdout


def test_read_message_file_utf8_roundtrip(git_commit_mod, tmp_path):
    """UTF-8 无 BOM 契约面：中文+非 BMP 字符逐字往返。"""
    f = tmp_path / "msg.txt"
    want = "修复编码：一试点 ✓"
    f.write_bytes(want.encode("utf-8"))
    rc, msg = git_commit_mod._read_message_file(f)
    assert rc is None
    assert msg == want


def test_read_message_file_gbk_rejected(git_commit_mod, tmp_path, capsys):
    """GBK 误写双字节（b'\\xd2\\xbb' 恰为合法 UTF-8=U+04BB）必须拒读，禁静默乱码。"""
    f = tmp_path / "msg_gbk.txt"
    f.write_bytes("一".encode("gbk"))
    rc, msg = git_commit_mod._read_message_file(f)
    assert rc == 1
    assert msg == ""
    err = capsys.readouterr().err
    assert "UTF-8" in err and "字节签名" in err


def test_read_message_file_utf16_bom_accepted(git_commit_mod, tmp_path):
    """UTF-16LE BOM 写端（PowerShell 5.1 Set-Content 常发）确定性转码接受。"""
    import codecs

    f = tmp_path / "msg_u16.txt"
    want = "中文消息十六"
    f.write_bytes(codecs.BOM_UTF16_LE + want.encode("utf-16-le"))
    rc, msg = git_commit_mod._read_message_file(f)
    assert rc is None
    assert msg == want


def test_git_log_chinese_readback_utf8(ccm_mod, tmp_path):
    """全链往返锚：-F UTF-8 中文提交 → git log 读回逐字一致（修前 GBK 误读必红）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
        "HOME": str(tmp_path),
    }

    def _git(*args: str, **kw):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            env=env,
            **kw,
        )

    _git("init", "-q")
    (repo / "a.txt").write_text("1", encoding="utf-8")
    _git("add", "a.txt")
    _git("commit", "-q", "-m", "base")
    (repo / "b.txt").write_text("2", encoding="utf-8")
    _git("add", "b.txt")
    msg_file = tmp_path / "zh_msg.txt"
    want = "修复编码链：中文消息往返红证 ✓"
    msg_file.write_bytes(want.encode("utf-8"))
    _git("commit", "-q", "--no-gpg-sign", "-F", str(msg_file))

    head = _git("rev-parse", "HEAD").stdout.strip()
    base = _git("rev-parse", "HEAD~1").stdout.strip()
    cwd_orig = Path.cwd()
    try:
        import os

        os.chdir(repo)  # _get_pr_commits 依赖 cwd 仓
        commits = ccm_mod._get_pr_commits(base, head)
    finally:
        os.chdir(cwd_orig)
    assert len(commits) == 1
    sha, message = commits[0]
    assert sha == head
    assert want in message
