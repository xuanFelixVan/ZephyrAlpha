# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §creation_token 批量登记
# [MODULE] scripts.governance.d3_metadata.batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/pathlib/re）；yaml
# [CONSUMERS] 拆分批/批量新增文件会话（CREATE-GUARD 批量登记通道，极限红蓝对抗 F1 治本）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯插入（只追加 creation_tokens 条目，绝不修改/删除既有条目）；幂等（已登记文件跳过）；
#   token 格式 {capability}-{stem}-{YYYYMMDD} 全局唯一；--dry-run 零写入；
#   写后 yaml.safe_load+语义落位+条目数守恒三自检，失败即回滚写前字节（2026-09-15 治理上报件1 收口；
#   条目数守恒=本文件 2026-09-19 B22 治本新增，判据见 _mass_deletion_issues）；
#   基底相对 HEAD 净删条目 ⇒ 写前即拒（fail-safe 方向=故障退化为不写，绝不"照写+只 warning"）；
#   --merge-evaluation 可选（裁定#375 合并评估结论一句话，写入每条 token 的 merge_evaluation
#   字段；缺省不阻断仅提示补填——CREATE-GUARD 对缺字段新建件 warn+审计）
# [MODIFY-GUARD] 插入锚点=creation_tokens 段内 capability 锚行（找不到时 fail-closed 拒写）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 库层=TokenInsertError（锚点缺失 fail-closed/CAS 耗尽/写后自检失败已回滚/
#   条目数净减即拒（含"少了哪几条"定位清单））；CLI 层捕获转 exit 1，绝不盲插
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
        --prefix docs/_working/xt_lab --created-by my-session --capability xtreme_lab \\
        --merge-evaluation "grep+计划任务+注册表三查零同域消费方，新对象"

    # 预览（零写入）
    python scripts/governance/d3_metadata/batch_creation_tokens.py ... --dry-run

--merge-evaluation（裁定#375，2026-09-20）：立项合并评估结论一句话，写入每条
token 的 ``merge_evaluation`` 字段（真源=token 条目本身，不建新册）。缺省不阻断，
仅提示补填——CREATE-GUARD 对缺该字段的新建资产 warn+审计（首期 warn-only）。

写侧"只增不减"自检（2026-09-19 全流通战役 B22 治本）
------------------------------------------------------
病根（本役实弹 R-063 / Q-7）：本工具曾把 ``st-ruledisp`` 会话**刚进 HEAD 的 4 行 token
整条吃掉**，还自报"落盘 True (CAS)"——纯插入的字符串拼接挡不住"基底本身是陈旧快照"
和"回滚覆写"两条蒸发路径，而 ``REGISTRY-MASS-DELETION`` 只管提交面，管不到写盘这一步。

现加两道守恒闸（条目身份 = ``(file, token)`` 二元组，判据真源 ``_entry_keys_of_text``）：
  ① **写前**：盘上基底相对 **HEAD** 已缺条目 ⇒ 立即拒写（本次写只会把这层蒸发固化成
     "合法提交"），错误信息逐条列出缺了哪几条；
  ② **写后**：落盘结果相对"写前基底 ∪ HEAD"出现净减 ⇒ 拒写并回滚到写前字节。
回滚自身走 CAS：若回滚窗口内又有会话推进过磁盘，则**放弃回滚**（绝不整片覆写他人新写），
在报错里说明"未回滚、需人工分诊"。fail-safe 方向＝**故障退化为不写**，不是"照写 + 只 warning"。
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


class TokenInsertError(RuntimeError):
    """creation_token 插入失败（锚点缺失 fail-closed / CAS 耗尽 / 写后校验失败已回滚）。

    库层语义=异常（scaffold 等进程内调用方捕获降级）；CLI 层捕获后转 exit 1。
    """


def _git_output(*args: str) -> list[str]:
    """_git_output implementation."""
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
    """load_registered implementation."""
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    return {str(e.get("file", "")) for e in (data.get("creation_tokens") or [])}


def _yaml_quote(text: str) -> str:
    """合并评估一句话转 YAML 双引号标量（压平换行+转义反斜杠/双引号，保持单行）。"""
    flat = " ".join(text.split())
    return '"' + flat.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_block(
    files: list[str], created_by: str, capability: str, today: str, merge_evaluation: str | None = None
) -> str:
    """build_block implementation.

    merge_evaluation（裁定#375）：非空时每条 token 追加 ``merge_evaluation: "<一句话>"``
    行——立项合并评估声明的登记载体（真源=token 条目本身，不建新册）。
    """
    lines: list[str] = []
    cap_norm = capability.strip().lower().replace("_", "-")
    for f in files:
        stem = Path(f).stem.lower().replace("_", "-")
        stem = re.sub(r"[^a-z0-9-]", "", stem) or "file"
        token = f"{cap_norm}-{stem}-{today}"
        if not _TOKEN_RE.match(token):
            print(f"FAIL: token 非法格式: {token}", file=sys.stderr)
            sys.exit(1)
        entry = f"- file: {f}\n  token: {token}\n  created_by: {created_by}\n  capability: {capability}"
        if merge_evaluation:
            entry += f"\n  merge_evaluation: {_yaml_quote(merge_evaluation)}"
        lines.append(entry)
    return "\n".join(lines) + "\n"


def _creation_tokens_section(text: str) -> tuple[int, int]:
    """定位 creation_tokens 段边界 [start, end)（字符偏移）。

    2026-09-13 实弹教训（factory-bottleneck 批 CREATE-GUARD 阻断实证）：registry 在
    creation_tokens 段**之后**还有 di_seam_exemptions 等段落，其中混有 593 条历史
    错位 token 条目（含 `capability:` 行）——全文件 rfind/findall 锚点会命中死区，
    插入条目落进 di_seam_exemptions 语义死区（CREATE-GUARD 读不到=登记丢失）。
    治本：一切锚点搜索 MUST 限定本段边界内。

    Raises:
        TokenInsertError: 段头不存在（fail-closed 拒写）。
    """
    m_head = re.compile(r"(?:^|\n)creation_tokens:\n").search(text)
    if not m_head:
        raise TokenInsertError("registry 无 creation_tokens 段，拒写（fail-closed）")
    start = m_head.end()
    m = re.compile(r"\n[a-z_]+:\n").search(text, start)
    end = m.start() + 1 if m else len(text)
    return start, end


def resolve_anchor(section: str, wanted: str) -> str:
    """锚点回退：capability 同名行优先，缺省回退段内最后一条 capability。

    （段外死区命中=锚点 bug 根因，故回退候选只从段内取。）

    Raises:
        TokenInsertError: 段内无任何 capability 锚点。
    """
    if f"  capability: {wanted}\n" in section:
        return wanted
    m = re.findall(r"  capability: (\S+)\n", section)
    if not m:
        raise TokenInsertError("creation_tokens 段内无任何 capability 锚点")
    return m[-1]


def _post_write_issues(expect_files: list[str] | None) -> list[str]:
    """写后自检：①yaml parse 完整性 ②语义落位（expect_files 必须解析进 creation_tokens 段）。

    返回问题清单（空=通过）。②是实弹教训的判别式——插进 di_seam_exemptions 死区时
    YAML 仍合法但登记丢失，纯 parse 检查抓不住。
    """
    try:
        data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 解析失败=问题本体
        return [f"yaml.safe_load 解析失败: {str(exc)[:160]}"]
    if not isinstance(data, dict):
        return [f"顶层不是 mapping（实际 {type(data).__name__}）"]
    if expect_files:
        landed = {
            str(e.get("file", "")).replace("\\", "/")
            for e in (data.get("creation_tokens") or [])
            if isinstance(e, dict)
        }
        missing = [f for f in expect_files if f not in landed]
        if missing:
            return [f"{len(missing)} 条未落位 creation_tokens 段: {missing[:3]}"]
    return []


def _rollback(pre_bytes: bytes, expect_sha: str = "") -> bool:
    """回滚到写前字节（B22 治本：由"整片覆写"改走基底校验）。

    ``expect_sha`` = 本次写入落成后的哈希（``SafeWriteResult.after_sha256``）。回滚前先比
    当前磁盘哈希：不一致说明窗口内又有会话推进过磁盘，此时**放弃回滚并返回 False**——
    整片覆写别人刚写的条目，比留着本次坏写更坏（R-063 的回滚面就是第二次蒸发）。
    调用方拿到 False 必须在报错里写明"未回滚，需人工分诊"。

    Args:
        pre_bytes: 写前原始字节（原样回写，行尾不重排）。
        expect_sha: 期望的当前磁盘哈希（LF 文本口径，与 content_sha256 同）；空串=不校验。

    Returns:
        True=已回滚到写前字节；False=磁盘已被推进，未回滚。
    """
    from zephyr.shared.io.file_utils import atomic_write, content_sha256

    pre_text = pre_bytes.decode("utf-8")
    if expect_sha and content_sha256(_REGISTRY.read_text(encoding="utf-8")) != expect_sha:
        print("FAIL: 回滚被拒（写后窗口内磁盘又被推进，整片覆写会造成第二次蒸发）——未回滚，需人工分诊", file=sys.stderr)
        return False
    atomic_write(_REGISTRY, pre_text, newline="")
    return True


def _entry_keys_of_text(text: str) -> set[tuple[str, str]] | None:
    """creation_tokens 条目身份集 = {(file, token)}；解析失败返回 None（由 parse 自检负责报）。"""
    try:
        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败本体由 _post_write_issues 报，这里只表"数不出来"
        return None
    if not isinstance(data, dict):
        return None
    return {
        (str(e.get("file", "")), str(e.get("token", "")))
        for e in (data.get("creation_tokens") or [])
        if isinstance(e, dict)
    }


def _registry_rel() -> str:
    """registry 相对 _REPO 的 POSIX 路径（HEAD 对照用；_REPO 被测试改写时自动跟随）。"""
    try:
        return _REGISTRY.resolve().relative_to(_REPO.resolve()).as_posix()
    except Exception:  # noqa: BLE001 — 不在同根下（临时副本）→ 退化为文件名，HEAD 读不到即跳过对照
        return _REGISTRY.name


def _head_entry_keys() -> set[tuple[str, str]] | None:
    """HEAD 版 registry 的条目集；非 git 环境/临时副本读不到 → None（跳过该对照面，不造假基线）。"""
    lines = _git_output("show", f"HEAD:{_registry_rel()}")
    if not lines:
        return None
    return _entry_keys_of_text("\n".join(lines) + "\n")


def _lost_entries_issue(lost: list[tuple[str, str]], verdict: str) -> list[str]:
    """把"少了哪几条"折成一条定位信息（file::token 二元组，最多列 5 条）——两条闸共用一份文案真源。"""
    shown = "; ".join(f"{f}::{t}" for f, t in lost[:5])
    more = f"（另有 {len(lost) - 5} 条）" if len(lost) > 5 else ""
    return [f"creation_tokens {verdict} 条（判据=只增不减）——少了: {shown}{more}"]


def _mass_deletion_issues(keep: set[tuple[str, str]] | None, stage: str) -> list[str]:
    """写后闸：落盘结果相对 keep（写前基底 ∪ HEAD）净减 ⇒ 出违规清单。

    Returns:
        问题清单（空=通过）。HEAD 不可读时 keep 只剩写前基底，不造假基线。
    """
    if not keep:
        return []
    post = _entry_keys_of_text(_REGISTRY.read_text(encoding="utf-8"))
    if post is None:
        return []  # 解析失败由 _post_write_issues 报，不在此重复计
    lost = sorted(keep - post)
    return _lost_entries_issue(lost, f"{stage} 净减 {len(lost)}") if lost else []


def _stale_base_issues(head_keys: set[tuple[str, str]] | None, base_keys: set[tuple[str, str]] | None) -> list[str]:
    """写前闸：盘上基底相对 HEAD 已缺条目 ⇒ 出违规清单（本次写只会把蒸发固化成"合法提交"）。

    Returns:
        问题清单（空=通过）。HEAD 不可读（临时副本/非 git 环境）时跳过对照，不造假基线。
    """
    if not head_keys or base_keys is None:
        return []
    lost = sorted(head_keys - base_keys)
    if not lost:
        return []
    issues = _lost_entries_issue(lost, f"写前基底相对 HEAD 缺 {len(lost)}")
    issues[0] += (
        "；成因＝陈旧整文件快照压在盘上（本役 R-063/Q-7 同型）。"
        "正解＝先按手册 §4 分诊**只把缺的这几条增量补回盘上基底**再重跑本工具；"
        "禁 `git checkout HEAD -- <registry>` 整片覆盖——盘上可能同时有其它会话尚未进 HEAD 的"
        "新条目，整片覆盖就是第二次蒸发（B23 同训）。也禁强行放行：写下去即一次跨会话静默删条目。"
    )
    return issues


def insert_block(block: str, anchor_capability: str, expect_files: list[str] | None = None) -> None:
    """纯插入：锚定 creation_tokens **段内**最后一条 capability: <anchor> 行之后。

    锚点行找不到（段内）→ fail-closed 拒绝写入（防盲插/防落段外死区）。
    写入走 safe_write_text（CAS+原子写）+ 重试——2026-09-14 四连炸实证：裸 write_text
    全文重写在读改写窗口被他会话并发写交割，文件头/尾部结构反复炸裂。
    写后 _post_write_issues 双自检（2026-09-15 治理上报件1 统一收口），失败即回滚
    写前字节并抛 TokenInsertError——不重试（重试=二次插入重复条目）。
    B22 治本追加条目数守恒闸（判据 _stale_base_issues / _mass_deletion_issues）：
    写前比"盘上基底 vs HEAD"、写后比"落盘结果 vs 写前基底∪HEAD"，任一净减即拒写。

    Raises:
        TokenInsertError: 锚点缺失 / CAS 5 次耗尽 / 写后自检失败（已回滚）/
            creation_tokens 条目数净减（拒写，含"少了哪几条"定位清单）。
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
            raise TokenInsertError(
                f"锚点 capability: {anchor_capability} 不在 creation_tokens 段内，拒写（fail-closed）"
            )
        # B22 写前闸：盘上基底相对 HEAD 已经缺条目 ⇒ 本次"纯插入"只会把蒸发固化成合法提交
        base_keys = _entry_keys_of_text(text)
        head_keys = _head_entry_keys()
        stale = _stale_base_issues(head_keys, base_keys)
        if stale:
            raise TokenInsertError("写前自检不过，未落盘任何改动（fail-safe=不写）: " + "; ".join(stale))
        keep = set(base_keys or set()) | set(head_keys or set())
        line_end = sec_start + section.find("\n", rel)
        new_text = text[: line_end + 1] + block + text[line_end + 1 :]
        try:
            res = safe_write_text(_REGISTRY, new_text, expected_base_sha256=base_sha, newline="")
            print(f"落盘: {res.written} (CAS attempt {attempt + 1})")
            written_sha = res.after_sha256
        except Exception as exc:  # noqa: BLE001 — CAS 冲突重读基线重放
            print(f"WARN: 写入冲突 ({type(exc).__name__})，重读基线重放 (attempt {attempt + 1})")
            time.sleep(3)
            continue
        issues = _post_write_issues(expect_files) + _mass_deletion_issues(keep, "写后 vs 写前基底∪HEAD")
        if issues:
            restored = _rollback(raw, written_sha)
            tail = "" if restored else "（⚠ 回滚亦被拒：磁盘已被其他会话推进，未回滚，需人工分诊）"
            raise TokenInsertError(
                f"写后自检不过，{'已回滚写前字节' if restored else '未回滚'}（fail-safe=不写）: "
                + "; ".join(issues)
                + tail
            )
        return
    raise TokenInsertError("5 次 CAS 重试仍冲突——有会话高频写此文件，稍后再试")


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="creation_token 批量登记（CREATE-GUARD 批量通道，纯插入幂等）")
    ap.add_argument("--prefix", required=True, help="目录/路径前缀（相对仓库根，如 docs/_working/xt_lab）")
    ap.add_argument("--created-by", required=True, help="登记会话名（如 my-session）")
    ap.add_argument("--capability", required=True, help="能力名（token 前缀，如 xtreme_lab）")
    ap.add_argument(
        "--anchor-capability",
        default=None,
        help="插入锚点（creation_tokens 段内既有 capability 名；缺省=capability 同名或段内最后一条）",
    )
    ap.add_argument(
        "--merge-evaluation",
        default=None,
        help="合并评估结论一句话（裁定#375 四判据，写入每条 token 的 merge_evaluation 字段；缺省仅提示补填）",
    )
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

    if not args.merge_evaluation:
        print(
            "提示：未提供 --merge-evaluation——裁定#375 内收判据（同真源可派生→必并｜零触发零消费→"
            "退役｜同域重复簇→收敛唯一｜跨域不同对象→不并）要求立项时做合并评估；CREATE-GUARD 对缺 "
            'merge_evaluation 的新建件将 warn+审计。补填：--merge-evaluation "<结论一句话>"'
            "或事后在 registry 条目补字段。"
        )

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    block = build_block(files, args.created_by, args.capability, today, merge_evaluation=args.merge_evaluation)
    print(f"计划登记 {len(files)} 条（capability={args.capability}, created_by={args.created_by}）:")
    for f in files[:10]:
        print(f"  {f}")
    if len(files) > 10:
        print(f"  ...（共 {len(files)}）")

    if args.dry_run:
        print("DRY-RUN：零写入")
        return 0

    # 锚点回退：仅限 creation_tokens 段内最后一条 capability（段外死区命中=锚点 bug 根因）
    try:
        text = _REGISTRY.read_text(encoding="utf-8")
        sec_start, sec_end = _creation_tokens_section(text)
        anchor = resolve_anchor(text[sec_start:sec_end], args.anchor_capability or args.capability)
        insert_block(block, anchor, expect_files=files)
    except TokenInsertError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: 已插入 {len(files)} 条（锚点 capability: {anchor}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
