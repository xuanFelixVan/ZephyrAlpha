# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §creation_token 批量登记
# [MODULE] scripts.governance.d3_metadata.batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/pathlib/re）；yaml
# [CONSUMERS] 拆分批/批量新增文件会话（CREATE-GUARD 批量登记通道，极限红蓝对抗 F1 治本）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯插入（只追加 creation_tokens 条目，绝不修改/删除既有条目）；幂等（已登记文件跳过）；
#   token 格式 {capability}-{stem}-{YYYYMMDD} 全局唯一；--dry-run 零写入
# [MODIFY-GUARD] 插入锚点=creation_tokens 段内 capability 锚行（找不到时 fail-closed 拒写）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 锚点缺失/registry 不可读 → exit 1（fail-closed，绝不盲插）
# [TESTS] tests/governance/d3_metadata/test_batch_creation_tokens.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（creation_token 批量登记通道，非 cron/非 daemon/非常驻服务），拆分批/批量建文件场景由会话显式触发
"""batch_creation_tokens — creation_token 批量登记工具（2026-09-13 极限红蓝对抗 F1 治本）。

病根：CREATE-GUARD 要求每个新增文件登记一条 creation_token——拆分批/批量建文件
场景（历史 78 moved+113 rewritten、极限测试 121 文件=242 条）逐条手写不可持续，
此前靠临时脚本拼装，无幂等保证、无官方通道。

用法::

    # 登记某目录下全部未登记文件（untracked + 已 tracked 但 registry 无条目）
    python scripts/governance/d3_metadata/batch_creation_tokens.py \\
        --prefix docs/_working/xt_lab --created-by my-session --capability xtreme_lab

    # 预览（零写入）
    python scripts/governance/d3_metadata/batch_creation_tokens.py ... --dry-run
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_REGISTRY = _REPO / "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def _git_output(*args: str) -> list[str]:
    r = subprocess.run(  # noqa: bare-subprocess  轻量登记工具直调 git ls-files，避免反向依赖 zephyr.shared（拉入 process_pool 重依赖），窗口闪现无影响
        ["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(_REPO)
    )
    return [ln for ln in r.stdout.splitlines() if ln.strip()] if r.returncode == 0 else []


def scan_unregistered(prefix: str, registered: set[str]) -> list[str]:
    """前缀下未登记文件清单 = git ls-files（tracked）∪ untracked，去已登记。"""
    tracked = [p.replace("\\", "/") for p in _git_output("ls-files", "--", prefix)]
    untracked = [p.replace("\\", "/") for p in _git_output("ls-files", "--others", "--exclude-standard", "--", prefix)]
    seen: set[str] = set()
    out: list[str] = []
    for p in tracked + untracked:
        if p not in seen and p not in registered:
            seen.add(p)
            out.append(p)
    return sorted(out)


def load_registered() -> set[str]:
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    return {str(e.get("file", "")) for e in (data.get("creation_tokens") or [])}


def build_block(files: list[str], created_by: str, capability: str, today: str) -> str:
    lines: list[str] = []
    cap_norm = capability.strip().lower().replace("_", "-")
    for f in files:
        stem = Path(f).stem.lower().replace("_", "-")
        stem = re.sub(r"[^a-z0-9-]", "", stem) or "file"
        token = f"{cap_norm}-{stem}-{today}"
        if not _TOKEN_RE.match(token):
            print(f"FAIL: token 非法格式: {token}", file=sys.stderr)
            sys.exit(1)
        lines.append(f"- file: {f}\n  token: {token}\n  created_by: {created_by}\n  capability: {capability}")
    return "\n".join(lines) + "\n"


def _creation_tokens_section(text: str) -> tuple[int, int]:
    """定位 creation_tokens 段边界 [start, end)（字符偏移）。

    2026-09-13 实弹教训（factory-bottleneck 批 CREATE-GUARD 阻断实证）：registry 在
    creation_tokens 段**之后**还有 di_seam_exemptions 等段落，其中混有 593 条历史
    错位 token 条目（含 `capability:` 行）——全文件 rfind/findall 锚点会命中死区，
    插入条目落进 di_seam_exemptions 语义死区（CREATE-GUARD 读不到=登记丢失）。
    治本：一切锚点搜索 MUST 限定本段边界内。
    """
    m_head = re.compile(r"(?:^|\n)creation_tokens:\n").search(text)
    if not m_head:
        print("FAIL: registry 无 creation_tokens 段，拒写（fail-closed）", file=sys.stderr)
        sys.exit(1)
    start = m_head.end()
    m = re.compile(r"\n[a-z_]+:\n").search(text, start)
    end = m.start() + 1 if m else len(text)
    return start, end


def insert_block(block: str, anchor_capability: str) -> None:
    """纯插入：锚定 creation_tokens **段内**最后一条 capability: <anchor> 行之后。

    锚点行找不到（段内）→ fail-closed 拒绝写入（防盲插/防落段外死区）。
    写入走 safe_write_text（CAS+原子写）+ 重试——2026-09-14 四连炸实证：裸 write_text
    全文重写在读改写窗口被他会话并发写交割，文件头/尾部结构反复炸裂。
    """
    import hashlib
    import time

    from zephyr.shared.io.file_utils import safe_write_text

    for attempt in range(5):
        raw = _REGISTRY.read_bytes()
        text = raw.decode("utf-8").replace("\r\n", "\n")
        base_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        sec_start, sec_end = _creation_tokens_section(text)
        section = text[sec_start:sec_end]
        rel = section.rfind(f"  capability: {anchor_capability}\n")
        if rel < 0:
            print(
                f"FAIL: 锚点 capability: {anchor_capability} 不在 creation_tokens 段内，拒写（fail-closed）",
                file=sys.stderr,
            )
            sys.exit(1)
        line_end = sec_start + section.find("\n", rel)
        new_text = text[: line_end + 1] + block + text[line_end + 1 :]
        try:
            res = safe_write_text(_REGISTRY, new_text, expected_base_sha256=base_sha, newline="")
            print(f"落盘: {res.written} (CAS attempt {attempt + 1})")
            return
        except Exception as exc:  # noqa: BLE001 — CAS 冲突重读基线重放
            print(f"WARN: 写入冲突 ({type(exc).__name__})，重读基线重放 (attempt {attempt + 1})")
            time.sleep(3)
    print("FAIL: 5 次 CAS 重试仍冲突——有会话高频写此文件，稍后再试", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    ap = argparse.ArgumentParser(description="creation_token 批量登记（CREATE-GUARD 批量通道，纯插入幂等）")
    ap.add_argument("--prefix", required=True, help="目录/路径前缀（相对仓库根，如 docs/_working/xt_lab）")
    ap.add_argument("--created-by", required=True, help="登记会话名（如 my-session）")
    ap.add_argument("--capability", required=True, help="能力名（token 前缀，如 xtreme_lab）")
    ap.add_argument("--anchor-capability", default=None, help="插入锚点（creation_tokens 段内既有 capability 名；缺省=capability 同名或段内最后一条）")
    ap.add_argument("--dry-run", action="store_true", help="只列计划，零写入")
    args = ap.parse_args()

    if not _REGISTRY.exists():
        print("FAIL: registry 不可达", file=sys.stderr)
        return 1
    registered = load_registered()
    files = scan_unregistered(args.prefix, registered)
    if not files:
        print("无待登记文件（全部已登记或前缀为空）")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    block = build_block(files, args.created_by, args.capability, today)
    print(f"计划登记 {len(files)} 条（capability={args.capability}, created_by={args.created_by}）:")
    for f in files[:10]:
        print(f"  {f}")
    if len(files) > 10:
        print(f"  ...（共 {len(files)}）")

    if args.dry_run:
        print("DRY-RUN：零写入")
        return 0

    # 锚点回退：仅限 creation_tokens 段内最后一条 capability（段外死区命中=锚点 bug 根因）
    text = _REGISTRY.read_text(encoding="utf-8")
    sec_start, sec_end = _creation_tokens_section(text)
    section = text[sec_start:sec_end]
    anchor = args.anchor_capability or args.capability
    if f"  capability: {anchor}\n" not in section:
        m = re.findall(r"  capability: (\S+)\n", section)
        if not m:
            print("FAIL: creation_tokens 段内无任何 capability 锚点", file=sys.stderr)
            return 1
        anchor = m[-1]
    insert_block(block, anchor)
    # 落盘后双自检：①YAML 完整性 ②语义落位（新文件必须解析进 creation_tokens 段——
    # 实弹教训：插进 di_seam_exemptions 死区时 YAML 仍合法但登记丢失）
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    registered_now = {str(e.get("file", "")) for e in (data.get("creation_tokens") or [])}
    missing = [f for f in files if f not in registered_now]
    if missing:
        print(f"FAIL: 语义自检不过——{len(missing)} 条未落位 creation_tokens 段: {missing[:3]}", file=sys.stderr)
        return 1
    print(f"OK: 已插入 {len(files)} 条（锚点 capability: {anchor}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
