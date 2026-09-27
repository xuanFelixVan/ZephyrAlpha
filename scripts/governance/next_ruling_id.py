# [BLUEPRINT] MOD-INF-037 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | §裁定编号分配铁律
# [MODULE] scripts.governance.next_ruling_id
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.encoding; zephyr.shared.io.paths (REPO_ROOT 仓根唯一真源); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 裁定#NNN 取号器（Z-38 P0 落地，2026-09-27 st-chief4x-govtool-20260927）：只读真源 docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml，本工具**永不写册**（登记必经 RULING-REFERENCE 门同 commit 原子通道，裁定#20-B/G）。--next 幂等零副作用：返回 max(在册主号)+1 并列出在途占号（advisory，不作分配承诺）；--claim 原子占号：O_EXCL 独占创建 .runtime/ruling_claims/claim_<N>.json（候选号=max(在册主号, 在途占号)+1，被占则递增重试），占号文件含 session/UTC 时间戳/pid，防并发取同号；--release 仅删本 session 自占号文件；编号不回收铁律（裁定#20-D #2）：占号文件不设 TTL 过期回收，stale 占号由人工 --release 处置；--check 悬空扫描：只报告不删改（Z-33 清雷=另批正式通道），语义对齐 ruling_reference_gate._RULING_REF_RE（裁定#NNN / #NNN-X，ruling_id 键锚定防 related_rulings 误报）；扫描文件类型 .py/.yaml/.yml/.md（对齐 RULING-REFERENCE 门），tests/ 目录豁免（对齐门豁免区）
# [MODIFY-GUARD] gate_id="N/A"（只读查询器+runtime 占号文件写，非门禁）
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] --next/--check 纯读，异常降级为 rc=2+stderr 指引（永不部分写）；--claim 竞态边界：O_EXCL 原子性保证同候选号仅一 session 成功，败者自动递增重试（上限=名册条目数+1000 防死循环）；名册缺失/不可读=rc=2（不猜测号段）；剩余竞态窗口=占号后未登记即崩溃留下 stale 占号文件——后续 --next/--claim 均感知并跳过该号（编号不回收），人工 --release 或正式登记后自然消解
# [TESTS] tests/governance/test_next_ruling_id.py
# [A_module] module_id=MOD-INF-037 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
next_ruling_id.py — 裁定#NNN 取号器（Z-38 / 波 5.2）

三件断言尺（Z-38 裁定）：在册最大号 + 在途占号感知 + O_EXCL 原子占号。

真源与边界
----------
- 裁定号唯一真源：docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
  （entries[].ruling_id = "裁定#NNN" 或 "裁定#NNN-X" 子裁定）。
- 本工具永不写册：正式登记必经 ruling_registry.yaml 与引用件同 commit 原子提交
  （裁定#20-B L2，RULING-REFERENCE 门 priority=74 强制）。
- 在途占号：.runtime/ruling_claims/claim_<N>.json（O_EXCL 独占创建）。
  占号≠登记：占号只防并发取同号，正式登记仍走册+同 commit 通道。

Usage::

    python scripts/governance/next_ruling_id.py --next                 # 幂等查询：下一可用号+在途占号
    python scripts/governance/next_ruling_id.py --claim --session SID  # 原子占号（防并发取同号）
    python scripts/governance/next_ruling_id.py --release N --session SID  # 释放本 session 占号
    python scripts/governance/next_ruling_id.py --check PATH [PATH ..] # 悬空裁定号扫描（只报告）

退出码：0=成功/无悬空；1=--check 发现悬空号 或 --claim 全候选号被占；2=环境/用法错误。

悬空号现状（2026-09-27 首跑，Z-33）：#414/#415 曾被六图役 worktree 自赋（HEAD 册查无、
HEAD 树零引用），主区 alignment_checklist.md 现文本已无该二号引用——清雷结论见
docs/01_policies_and_standards/_registry/reports/ 同批对账报告或本工具 --check 实跑输出。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

# _SRC_BOOTSTRAP 只为 import 定位本 worktree 的包面（防 editable 安装把 zephyr 硬锚主仓），
# 仓根本身**不在此重算**——REPO_ROOT 真源=zephyr.shared.io.paths（SSOT-REDEFINITION 对症）。
_SRC_BOOTSTRAP = Path(__file__).resolve().parents[2] / "src"
if _SRC_BOOTSTRAP.exists() and str(_SRC_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_SRC_BOOTSTRAP))
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地 parents[2] 重定义）
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__manifest__ = """
dimensions: [D1]
priority: P2
timeout_seconds: 30
args:
  - {flag: --next, type: bool, description: "幂等查询下一可用裁定号（零副作用）"}
  - {flag: --claim, type: bool, description: "原子占号（O_EXCL，防并发取同号）"}
  - {flag: --release, type: int, description: "释放本 session 占用的指定号"}
  - {flag: --session, type: str, description: "session id（--claim/--release 必带，留痕）"}
  - {flag: --check, type: bool, description: "扫描悬空裁定#NNN 引用（只报告不删）"}
  - {flag: --json, type: bool, description: "机器可读 JSON 输出"}
  - {flag: paths, type: list, description: "--check 扫描目标（文件/目录）"}
warn_only: false
"""

REGISTRY_REL = Path("docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml")
CLAIM_DIR_REL = Path(".runtime/ruling_claims")
#: 对齐 ruling_reference_gate._RULING_REF_RE：裁定#NNN / #NNN-X（纯数字+字母后缀）
_RULING_REF_RE = re.compile(r"裁定#(\d+(?:-[A-Z]+)?)")
#: ruling_id 声明键锚定（防 related_rulings/正文引用误入号段与在册集合——grep-and-claim 旧病反噬）
_RULING_ID_DECL_RE = re.compile(r"ruling_id\s*:\s*[\"']?裁定#(\d+(?:-[A-Z]+)?)[\"']?")
#: --check 扫描的文件后缀（对齐 RULING-REFERENCE 门扫描面）
_SCAN_SUFFIXES = {".py", ".yaml", ".yml", ".md"}
#: --check 豁免目录（对齐门豁免区：tests/ 不扫）
_SCAN_EXCLUDED_DIRS = {"tests", ".git", ".runtime", ".aidrafts", ".worktrees", "node_modules", "__pycache__"}
#: --claim 递增重试上限（防极端满号段死循环）
_CLAIM_RETRY_LIMIT = 1000


class _DetailsCarryingError:
    """敏感上下文走 details 不进消息文本（§5.99.20 治本，仓库既有 idiom 同形）。

    与 ``src/zephyr/ai_layer/**/policy.py`` 等 16 处同构：消息只留人类可读通用摘要，
    路径等上下文进 ``details`` dict；CLI 渲染用 :func:`_describe_error`。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = dict(details or {})


class RulingRegistryMissingError(_DetailsCarryingError, FileNotFoundError):
    """裁定册缺失（fail-closed：不猜测号段）。isinstance FileNotFoundError 语义不变。"""


class RulingRegistryEmptyError(_DetailsCarryingError, ValueError):
    """裁定册零 ruling_id 声明（fail-closed）。isinstance ValueError 语义不变。"""


def _describe_error(exc: BaseException) -> str:
    """stderr 行渲染：通用消息 + details 明细（路径只在这里落地，不进异常消息）。"""
    details = getattr(exc, "details", None) or {}
    tail = "".join(f" {k}={v}" for k, v in sorted(details.items()))
    return f"ERROR: {exc}{tail}"


def _registry_path(repo_root: Path) -> Path:
    return repo_root / REGISTRY_REL


def read_registered_numbers(repo_root: Path) -> tuple[set[str], int, int]:
    """读册：返回 (已登记完整号集合如 {'413','19-A'}, 在册最大主号, 条目总数)。

    在册集合与号段计算只锚定 ruling_id 声明键（文本级正则，鲁棒于引号变体）——
    related_rulings/summary 里的 裁定#NNN 引用不入集合（防 grep-and-claim 旧病反噬：
    册内悬空引用被误计为在册号）。册缺失/不可读抛 FileNotFoundError——不猜测号段（fail-closed）。
    """
    path = _registry_path(repo_root)
    if not path.exists():
        raise RulingRegistryMissingError("ruling registry not found", details={"path": str(path)})
    text = path.read_text(encoding="utf-8")
    declared = _RULING_ID_DECL_RE.findall(text)
    if not declared:
        raise RulingRegistryEmptyError("ruling registry has no ruling_id entries", details={"path": str(path)})
    full_ids: set[str] = set(declared)
    max_main = max(int(d.split("-", 1)[0]) for d in declared)
    return full_ids, max_main, len(declared)


def read_inflight_claims(claim_dir: Path) -> dict[int, dict]:
    """读在途占号：{号: claim 元数据}。损坏文件按占号感知保留（编号不回收），payload 置 error 标记。"""
    claims: dict[int, dict] = {}
    if not claim_dir.exists():
        return claims
    for f in sorted(claim_dir.glob("claim_*.json")):
        m = re.fullmatch(r"claim_(\d+)\.json", f.name)
        if not m:
            continue
        n = int(m.group(1))
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 占号感知优先于 payload 完整性
            payload = {"error": "unreadable claim payload（占号仍被感知，编号不回收）"}
        claims[n] = payload
    return claims


def cmd_next(repo_root: Path, as_json: bool = False) -> int:
    """--next：幂等零副作用。下一候选号=max(在册主号, 在途占号)+1。"""
    full_ids, max_main, entry_count = read_registered_numbers(repo_root)
    claims = read_inflight_claims(repo_root / CLAIM_DIR_REL)
    next_candidate = max([max_main, *claims.keys(), 0]) + 1
    if as_json:
        payload = {
            "next_candidate": next_candidate,
            "max_registered_main": max_main,
            "registered_entry_count": entry_count,
            "inflight_claims": {str(k): v for k, v in sorted(claims.items())},
            "registry": str(REGISTRY_REL),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(f"在册最大主号: #{max_main}（登记条目 {entry_count} 条）")
    if claims:
        print(f"在途占号 {len(claims)} 个（编号不回收，分配时跳过）:")
        for n, meta in sorted(claims.items()):
            print(f"  #{n}: {meta}")
    else:
        print("在途占号: 无")
    print(f"下一可用号: 裁定#{next_candidate}")
    print("（advisory 查询，不作分配承诺；正式取号用 --claim，登记必经册+同 commit 原子通道）")
    return 0


def cmd_claim(repo_root: Path, session: str) -> int:
    """--claim：O_EXCL 原子占号。候选号=max(在册主号, 在途占号)+1，被占递增重试。"""
    if not session or not session.strip():
        print("ERROR: --claim 必须带非空 --session（占号留痕，防死会话 stale 占号无法归责）", file=sys.stderr)
        return 2
    full_ids, max_main, _ = read_registered_numbers(repo_root)
    claim_dir = repo_root / CLAIM_DIR_REL
    claim_dir.mkdir(parents=True, exist_ok=True)
    claims = read_inflight_claims(claim_dir)
    candidate = max([max_main, *claims.keys(), 0]) + 1
    for _ in range(_CLAIM_RETRY_LIMIT):
        payload = {
            "ruling_id": f"裁定#{candidate}",
            "session": session,
            "claimed_at": now_utc().isoformat(),
            "pid": os.getpid(),
        }
        target = claim_dir / f"claim_{candidate}.json"
        try:
            fd = os.open(str(target), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            candidate += 1  # 在途占号感知：被占即递增，O_EXCL 保证同号仅一 session 成功
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"已占号: 裁定#{candidate}（session={session}）")
        print(f"占号文件: {target}")
        print("登记义务: 该号须与 ruling_registry.yaml 新条目同 commit 正式登记（裁定#20-B 原子性）；")
        print("废弃占号用 --release 释放（编号不回收铁律下释放≠可复用——复用会与登记记录冲突，禁）。")
        return 0
    print(f"ERROR: 连续 {_CLAIM_RETRY_LIMIT} 个候选号均被占（异常满号段），拒绝继续", file=sys.stderr)
    return 1


def cmd_release(repo_root: Path, number: int, session: str) -> int:
    """--release：仅删本 session 自占号文件（他 session 占号不可代删）。"""
    if not session or not session.strip():
        print("ERROR: --release 必须带非空 --session（仅可释放自己的占号）", file=sys.stderr)
        return 2
    target = repo_root / CLAIM_DIR_REL / f"claim_{number}.json"
    if not target.exists():
        print(f"占号文件不存在（本就无占用或已释放）: #{number}")
        return 0
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 损坏占号文件按非本 session 处置
        payload = {}
    if payload.get("session") != session:
        print(
            f"ERROR: #{number} 占号者={payload.get('session')!r}，非本 session（{session!r}），拒绝代删",
            file=sys.stderr,
        )
        return 2
    target.unlink()
    print(f"已释放占号: #{number}（session={session}）。注意: 编号不回收——若该号已正式登记，释放≠复用。")
    return 0


def _iter_scannable_files(targets: list[Path]) -> list[Path]:
    """展开扫描目标：文件直收，目录递归（豁免区+后缀过滤，对齐 RULING-REFERENCE 门）。"""
    files: list[Path] = []
    for t in targets:
        if t.is_file():
            files.append(t)
        elif t.is_dir():
            for root, dirs, names in os.walk(t):
                dirs[:] = [d for d in dirs if d not in _SCAN_EXCLUDED_DIRS]
                files.extend(Path(root) / n for n in names if Path(n).suffix in _SCAN_SUFFIXES)
    return sorted(set(files))


def cmd_check(repo_root: Path, targets: list[Path], as_json: bool = False) -> int:
    """--check：扫描 悬空裁定#NNN 引用（册外号）。只报告不删改（Z-33 清雷=另批正式通道）。

    判悬空规则：引用完整号（含字母后缀）不在册=悬空（dangling-suffix 记主号缺/后缀缺两态）。
    """
    full_ids, max_main, _ = read_registered_numbers(repo_root)
    files = _iter_scannable_files(targets)
    dangling: list[dict] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in _RULING_REF_RE.finditer(text):
            ref = m.group(1)
            if ref in full_ids:
                continue
            main = ref.split("-", 1)[0]
            kind = "main-missing" if main not in {i.split("-", 1)[0] for i in full_ids} else "suffix-missing"
            line = text.count("\n", 0, m.start()) + 1
            dangling.append({"file": str(f), "line": line, "ref": f"裁定#{ref}", "kind": kind})
    if as_json:
        print(
            json.dumps(
                {"scanned_files": len(files), "dangling_count": len(dangling), "dangling": dangling},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"扫描文件 {len(files)} 个；在册完整号 {len(full_ids)} 个（最大主号 #{max_main}）")
        if not dangling:
            print("悬空裁定号: 无（全部引用在册）")
        else:
            print(f"悬空裁定号引用 {len(dangling)} 处（只报告不删，清雷须走正式登记通道）:")
            for d in dangling:
                print(f"  {d['file']}:{d['line']}  {d['ref']}  [{d['kind']}]")
    return 1 if dangling else 0


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="裁定#NNN 取号器（Z-38）：--next/--claim/--release/--check")
    parser.add_argument("--next", action="store_true", help="幂等查询下一可用号（零副作用）")
    parser.add_argument("--claim", action="store_true", help="原子占号（O_EXCL，防并发取同号）")
    parser.add_argument("--release", type=int, metavar="N", help="释放本 session 占用的号 N")
    parser.add_argument("--session", type=str, default="", help="session id（--claim/--release 必带）")
    parser.add_argument("--check", action="store_true", help="扫描悬空裁定#NNN 引用（只报告）")
    parser.add_argument("--json", action="store_true", help="机器可读 JSON 输出（--next/--check）")
    parser.add_argument("paths", nargs="*", type=Path, help="--check 扫描目标（文件/目录，可多个）")
    args = parser.parse_args(argv)
    repo_root = REPO_ROOT
    modes = [args.next, args.claim, args.release is not None, args.check]
    if sum(modes) != 1:
        parser.error("必须且只能选择一个模式: --next / --claim / --release N / --check")
    try:
        if args.next:
            return cmd_next(repo_root, as_json=args.json)
        if args.claim:
            return cmd_claim(repo_root, args.session)
        if args.release is not None:
            return cmd_release(repo_root, args.release, args.session)
        if args.check:
            if not args.paths:
                parser.error("--check 至少需要一个扫描目标（文件或目录）")
            for p in args.paths:
                if not p.exists():
                    print(f"ERROR: 扫描目标不存在: {p}", file=sys.stderr)
                    return 2
            return cmd_check(repo_root, list(args.paths), as_json=args.json)
    except FileNotFoundError as e:
        print(_describe_error(e), file=sys.stderr)
        return 2
    except ValueError as e:
        print(_describe_error(e), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
