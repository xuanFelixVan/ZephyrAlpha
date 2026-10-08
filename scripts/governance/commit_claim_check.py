# [BLUEPRINT] MOD-GOV-116 | scripts/governance/commit_claim_check.py | §st-govfix-g1-20261007-F3
# [MODULE] scripts.governance.commit_claim_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib（pathlib/re/os）；无 zephyr 依赖（纯函数，锁外零副作用零网络）
# [CONSUMERS] scripts.git_commit.py（_enqueue_mode 与直连路径，Rx-1 同位挂钩）；手工 CLI 复查
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 只读纯函数；缺陷类判据保守（袋内零代码文件+消息提及代码路径才触发，引用即算提及——复审成本=加 [docs-only] 一词，漏放成本=假账入库）；v1 只判缺陷类（袋零代码），不做逐文件核对（消息引用上下文文件的合法场景多，逐文件核对=假红风暴，留 v2 登记）
# [MODIFY-GUARD] CODE_EXTS/DOCS_ONLY_MARKER 变更须同步 tests/governance/test_commit_claim_check.py
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_message_claims 纯函数不上抛（异常输入按放行返回 None，设施故障 fail-open 由调用方兜底——对齐 Rx-1 ruff_preclean 口径）
# [TESTS] tests/governance/test_commit_claim_check.py
# [A_module] module_id=MOD-GOV-116 | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""commit_claim_check — 「commit message 声称代码变更但袋无代码」复查门（F3 最小版）。

病灶（st-govfix-g1 车道 F3 项）：提交消息声称修复/新增了代码（如
"ch_data.py:212 regime_series() 改 SMA200 优先"），但提交袋（staged files）
里根本没有该代码文件——消息账与代码账脱钩，审计面出现"宣称已修实际未修"的假账。

机制位（自定）：Rx-1 ruff_preclean 同位——git_commit.py 入队/直连两路径的
锁外预检，秒级快败；权威语义=把「消息声称代码变更」与「袋内代码文件数」
机械对账，脱钩即拒（exit 8），迫使提交人二选一：

  1. 把声称的代码文件真入袋（正道）；
  2. 纯文档/翻牌/登记类提交在消息加 ``[docs-only]`` 标记（显式申报，门放行）。

判据（保守，防假红）：
- 声称=消息中出现带代码扩展名的路径 token（反引号 token 不要求含 /；裸 token
  要求含 /，如 ``scripts/foo/bar.py``）；
- 袋代码文件=staged 清单中扩展名属 CODE_EXTS 者（测试 .py 同算代码——
  gate+自家测试同批合法）；
- 袋内 ≥1 个代码文件即放行（不做逐文件核对，v1 只拦「袋零代码」缺陷类）。

逃生：消息含 ``[docs-only]``（大小写不敏感）｜env ``ZEPHYR_COMMIT_CLAIM_CHECK=0``｜
``--skip-preflight``（诊断逃生，与既有预检同口径）｜设施异常 fail-open 放行。
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

#: 代码扩展名真源（.py/.yaml/.yml/.ps1/.sql/.toml/.json/.sh/.bat/.cmd/.js/.ts）
CODE_EXTS: frozenset[str] = frozenset(
    {".py", ".yaml", ".yml", ".ps1", ".sql", ".toml", ".json", ".sh", ".bat", ".cmd", ".js", ".ts"}
)
#: docs-only 显式申报标记（含此标记的消息跳过复查）
DOCS_ONLY_MARKER = "[docs-only]"
#: env 回退开关（"0"/"false"/"off"=停用）
CLAIM_CHECK_ENV = "ZEPHYR_COMMIT_CLAIM_CHECK"

_BARE_CODE_PATH_RE = re.compile(
    r"[A-Za-z0-9_\-.]+/[A-Za-z0-9_\-./]+\.(?:py|yaml|yml|ps1|sql|toml|json|sh|bat|cmd|js|ts)\b"
)
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")


def claim_check_enabled() -> bool:
    """env 开关：ZEPHYR_COMMIT_CLAIM_CHECK 缺省 ON，"0"/"false"/"off"=回退。"""
    return os.environ.get(CLAIM_CHECK_ENV, "").strip().lower() not in {"0", "false", "off"}


def claimed_code_paths(message: str) -> list[str]:
    """提取消息中声称的代码路径（反引号 token 不限斜杠；裸 token 须含 /）。去重保序。"""
    out: list[str] = []
    for tok in _BACKTICK_RE.findall(message or ""):
        t = tok.strip()
        if t and Path(t).suffix.lower() in CODE_EXTS and not t.startswith("git "):
            out.append(t)
    for tok in _BARE_CODE_PATH_RE.findall(message or ""):
        out.append(tok)
    seen: set[str] = set()
    uniq = []
    for t in out:
        k = t.replace("\\", "/")
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    return uniq


def bag_code_files(files: list[str]) -> list[str]:
    """袋内代码文件清单（按扩展名；路径分隔符无关）。"""
    return [f for f in (files or []) if Path(str(f).replace("\\", "/")).suffix.lower() in CODE_EXTS]


def check_message_claims(message: str, files: list[str]) -> str | None:
    """对账：消息声称代码变更 vs 袋内代码文件。None=放行；str=拒收处方（含修复指令）。"""
    msg = message or ""
    if DOCS_ONLY_MARKER in msg.lower():
        return None
    claims = claimed_code_paths(msg)
    if not claims:
        return None
    if bag_code_files(files):
        return None
    shown = ", ".join(claims[:5]) + ("…" if len(claims) > 5 else "")
    return (
        f"MESSAGE-CLAIMS-CODE-BAG-EMPTY: 消息提及代码文件 [{shown}] 但提交袋内 0 个代码文件"
        "（消息账与代码账脱钩）。二选一：①把声称的代码文件真入袋；"
        "②纯文档/翻牌/登记类提交在消息加 [docs-only] 显式申报（或删去代码路径引用）。"
    )


def main(argv: list[str] | None = None) -> int:
    """手工复查 CLI：--message-file F --files a,b,c（或 stdin 喂消息）。0=OK，3=违规。"""
    import argparse

    ap = argparse.ArgumentParser(description="commit message vs 提交袋代码对账复查")
    ap.add_argument("--message-file", default="", help="提交消息文件路径（缺省读 stdin）")
    ap.add_argument("--message", default="", help="直接传消息文本")
    ap.add_argument("--files", required=True, help="逗号分隔的提交袋文件清单")
    args = ap.parse_args(argv)
    if args.message:
        msg = args.message
    elif args.message_file:
        msg = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
    else:
        msg = sys.stdin.read()
    files = [f.strip() for f in args.files.split(",") if f.strip()]
    verdict = check_message_claims(msg, files)
    if verdict is None:
        print("CLAIM-CHECK-OK")
        return 0
    print(verdict, file=sys.stderr)
    return 3


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: AI/Owner 会话按需调用的 permanent 手工复查 CLI（离线对账单条消息用，非 cron/非 daemon/非常驻服务；生产消费面=git_commit.py 两处挂钩自动触发）
    raise SystemExit(main())
