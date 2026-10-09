# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §creation_token 批量登记
# [MODULE] scripts.governance.d3_metadata.batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/pathlib/re/subprocess/sys/datetime）；yaml；
#   zephyr.governance.registry_ledger.api（register，lazy）；
#   zephyr.governance.registry_ledger.baseline（publish_snapshot，lazy）；
#   zephyr.governance.registry_projection.projection_generator（run，lazy）；
#   zephyr.infrastructure.database_service（load_registered 账本只读面，lazy）
# [CONSUMERS] 拆分批/批量新增文件会话（CREATE-GUARD 批量登记通道）；
#   进程内：scaffold.py:1266、dead_letter_doctor.py:605（insert_block/build_block/load_registered/
#   _creation_tokens_section/resolve_anchor/_TOKEN_RE/_REGISTRY 兼容面）；
#   子进程：register_asset.py、factory_intake_pipeline.py（CLI 参数兼容）；只读：lock_files.py:1746（detect_file_type）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 直写轨退役（裁定#502，st-regsolo-20261010）：本工具不再是 YAML 写者——
#   内部全走意图 API 三步 register→publish_snapshot→projection render（热册唯一合法写者=生成器，
#   PG 账本=唯一真源）；YAML 直写路径（插入锚/CAS/守恒闸/回滚）整体删除，守恒语义由账本层立法下沉
#   （api.register 幂等 OK_NOOP/CONFLICT_DUPLICATE 拒绝 + 投影四象限 PG-wins）；纯意图语义（只登记不删除，
#   系统不存在"把册里少掉的条目解释为删除"的路径）；--dry-run 零写（仅账本只读扫描）；
#   token 格式 {capability}-{stem}-{YYYYMMDD} 全局唯一；W4 宽前缀防呆保留（>50 条或跨一级目录须
#   先 --dry-run 预览确认再显式 --wide-prefix）；--anchor-capability 收下忽略（账本无插入锚语义）；
#   --merge-evaluation 随 payload 登记进账本（裁定#375）；PG 不可达=登记失败 exit 1（绝不降级直写）；
#   --emit-guide 只查不改保留
# [MODIFY-GUARD] 2026-10-09 st-regsolo-20261010 直写轨退役改写（裁定#502）：insert_block 语义从
#   "YAML 纯插入"改"账本登记+投影重打"，签名兼容（block, anchor_capability, expect_files）不变；
#   原插入锚点/守恒闸/回滚私函数随直写路径删除（消费方仅测试，同批重写）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 库层=TokenInsertError（block 解析失败/token 非法/账本登记失败/投影重打失败/
#   语义落位校验失败 expect_files 未入账本）；CLI 层捕获转 exit 1；PG 不可达不降级不直写
# [TESTS] tests/gov/governance/d3_metadata/test_batch_creation_tokens.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（creation_token 批量登记通道=意图 API 薄壳，非 cron/非 daemon/非常驻服务）
"""batch_creation_tokens — creation_token 批量登记工具（意图 API 单口写薄壳，裁定#502）。

历史病根（为何退役直写轨）：本工具曾直写 capability_canonical_file_registry.yaml，
而该册 2026-09 起真源=PG registry_ledger 账本、YAML=机生投影——直写即账本永远欠账，
账本侧 publish/render 一到就把直写内容冲掉（10-09 三起 token 蒸发/-271 回滚险情的
共同增量源）。2026-10-05 register_asset.py 曾试图接意图 API，但客户端脚本
register_tokens_ledger.py 从未存在（幻影），rc!=0 每次静默 fallback 回本工具直写。
裁定#502 退役直写轨：本工具改为意图 API 薄壳，三步全部内置——

    1. api.register（逐条目意图登记；幂等：同键同指纹=OK_NOOP 跳过）
    2. baseline.publish_snapshot（账本快照发布；noop 幂等）
    3. registry_projection render（投影重打；PG-wins 四象限全自动）

用法::

    # 登记某目录下全部未登记文件（untracked + 已 tracked 但账本无条目）
    python scripts/governance/d3_metadata/batch_creation_tokens.py \\
        --prefix docs/_working/xt_lab --created-by my-session --capability xtreme_lab \\
        --merge-evaluation "grep+计划任务+注册表三查零同域消费方，新对象"

    # 预览（零写入）
    python scripts/governance/d3_metadata/batch_creation_tokens.py ... --dry-run

兼容性：CLI 参数与进程内函数签名（insert_block/build_block/load_registered/
_creation_tokens_section/resolve_anchor/TokenInsertError）保持——scaffold.py 与
dead_letter_doctor.py 零改动续用；insert_block 语义=YAML 纯插入→账本登记+投影重打。
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
_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_REGISTRY = _REPO / _REGISTRY_REL
_REGISTRY_ID = "REG-CAPCAN-001"  # 投影管理册（与 projection_generator._DEFAULT_REGISTRY_ID 同源）
_FAMILY = "creation_tokens"
_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
# W4 防呆（2026-09-22 注册表事故，emomine 481 条误扫治本）：计划登记数超限或前缀
# 扫出多个一级目录 → 非显式 --wide-prefix 拒绝执行（先 --dry-run 预览贴回确认）。
_WIDE_PREFIX_ENTRY_LIMIT = 50

# 账本 active 面 file 集查询（§5.160.2 SQL 集中化：参数化常量，真源=registry_ledger schema）
_SQL_ACTIVE_TOKEN_FILES = (
    "SELECT payload->>'file' AS f FROM registry_ledger.registry_entry "
    "WHERE registry_id=%s AND family_key=%s AND status='active'"
)


class TokenInsertError(RuntimeError):
    """creation_token 登记失败（block 解析/token 非法/账本登记/投影重打/落位校验失败）。

    库层语义=异常（scaffold 等进程内调用方捕获降级）；CLI 层捕获后转 exit 1。
    （类名保留直写时代拼写作兼容面，语义=意图 API 登记失败契约。）
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


def _registered_files_from_ledger() -> set[str] | None:
    """账本 active 条目的 file 集（只读）；PG 不可达返回 None（调用方退投影面读）。"""
    try:
        from zephyr.infrastructure.database_service import DatabaseService

        conn = DatabaseService().get_depgraph_conn(read_only=True)
        try:
            with conn.cursor() as cur:
                cur.execute(_SQL_ACTIVE_TOKEN_FILES, (_REGISTRY_ID, _FAMILY))
                rows = cur.fetchall()
        finally:
            conn.close()
        files: set[str] = set()
        for row in rows:
            v = row["f"] if isinstance(row, dict) else row[0]
            if v:
                files.add(str(v).replace("\\", "/"))
        return files
    except Exception:  # noqa: BLE001 — 读面 fail-open 退投影（登记面另 fail-closed）
        return None


def load_registered() -> set[str]:
    """已登记 file 集：账本（真源）优先，PG 不可读退投影 YAML（读面 fail-open）。

    幂等判据走账本：投影可能落后账本（他道已 register 未落地），以投影判幂等会
    虚报待登记清单——api.register 同键同指纹本就 OK_NOOP，重复登记无害，但清单
    校准到账本更准。
    """
    from_ledger = _registered_files_from_ledger()
    if from_ledger is not None:
        return from_ledger
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
    行——立项合并评估声明的登记载体（真源=账本条目本身，不建新册）。
    产出仍=YAML 列表项文本（兼容面），由 _parse_block_entries 解析回 payload 字典。
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
    """定位投影册 creation_tokens 段边界 [start, end)（字符偏移）——纯解析兼容面。

    直写轨退役后本函数仅剩只读消费（scaffold/dead_letter_doctor/orphan_reconciler
    的段边界判读）；写路径已不存在（账本无插入锚语义）。

    Raises:
        TokenInsertError: 段头不存在。
    """
    m_head = re.compile(r"(?:^|\n)creation_tokens:\n").search(text)
    if not m_head:
        raise TokenInsertError("registry 无 creation_tokens 段")
    start = m_head.end()
    m = re.compile(r"\n[a-z_]+:\n").search(text, start)
    end = m.start() + 1 if m else len(text)
    return start, end


def resolve_anchor(section: str, wanted: str) -> str:
    """兼容垫片（直写轨退役，裁定#502）：账本无插入锚语义，恒返回期望锚名。

    原"段内锚点回退"逻辑服务于 YAML 插入位计算；登记走账本后锚位概念消亡，
    恒等返回让 scaffold/dead_letter_doctor 调用点零改动。
    """
    return wanted


def _parse_block_entries(block: str) -> list[dict]:
    """block 文本（YAML 列表项）→ payload 字典列表；结构不符 fail-closed。"""
    try:
        entries = yaml.safe_load(block)
    except Exception as exc:  # noqa: BLE001 — block 构造端已保证合法，防御手拼
        raise TokenInsertError(f"block 非 YAML 列表（{type(exc).__name__}: {str(exc)[:120]}）") from exc
    if not isinstance(entries, list) or not entries:
        raise TokenInsertError("block 解析结果非非空列表")
    out: list[dict] = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            raise TokenInsertError(f"第 {i} 条不是 mapping")
        for key in ("file", "token"):
            if not str(e.get(key, "")).strip():
                raise TokenInsertError(f"第 {i} 条缺必填键 {key}")
        if not _TOKEN_RE.match(str(e["token"])):
            raise TokenInsertError(f"第 {i} 条 token 非法格式: {e['token']}")
        out.append({k: v for k, v in e.items() if v is not None})
    return out


def insert_block(block: str, anchor_capability: str, expect_files: list[str] | None = None) -> None:
    """意图 API 三步登记（裁定#502 直写轨退役）：register 逐条→publish→render。

    签名兼容（block, anchor_capability, expect_files），``anchor_capability`` 收下
    忽略（账本无插入锚语义）。逐条登记幂等：同键同指纹=OK_NOOP 静默跳过；同键异
    指纹=CONFLICT_DUPLICATE 记 WARN 继续（账本条目为准，投影重打自动归一——直写
    时代差异条目在退役过渡期常态）。任一条目登记抛错（PG 不可达等）即 TokenInsertError，
    已登记条目保留（逐条事务，重跑幂等）。发布+重打后语义落位校验：expect_files 必须
    全部出现在账本 active 面，缺失=TokenInsertError（登记丢失显形，不静默）。

    Raises:
        TokenInsertError: block 解析/token 非法/账本登记失败/投影重打失败/落位校验失败。
    """
    from zephyr.governance.registry_ledger import api
    from zephyr.governance.registry_ledger.baseline import publish_snapshot

    entries = _parse_block_entries(block)
    if not entries:
        return
    session_id = str(entries[0].get("created_by") or "batch_creation_tokens")
    reason = (
        f"creation_token batch registration via ledger API frontdoor "
        f"(capability={entries[0].get('capability', '?')}, n={len(entries)}, ruling=502)"
    )
    registered = noop = conflict = 0
    for e in entries:
        try:
            result = api.register(
                _REGISTRY_ID,
                _FAMILY,
                e,
                reason=reason,
                session_id=session_id,
                actor_kind="agent",
            )
        except Exception as exc:  # noqa: BLE001 — PG 不可达等编程/环境异常归一库层契约（不降级直写）
            raise TokenInsertError(f"账本登记异常 {e.get('file')}: {type(exc).__name__}: {exc}") from exc
        if result.code == api.OK:
            registered += 1
        elif result.code == api.OK_NOOP:
            noop += 1
        elif result.code == api.CONFLICT_DUPLICATE:
            conflict += 1
            print(
                f"WARN: CONFLICT_DUPLICATE {e.get('file')} (token={e.get('token')})——"
                "账本已有同键异指纹条目，以账本为准（投影重打归一）；如需变更走 api.update",
                file=sys.stderr,
            )
        else:
            raise TokenInsertError(f"账本登记失败 {e.get('file')}: {result.code} {result.detail}")
    published = publish_snapshot(_REGISTRY_ID, repo_root=_REPO, session_id=session_id)
    print(
        f"登记: 新增 {registered} 幂等跳过 {noop} 冲突WARN {conflict}；"
        f"publish_snapshot v{published.get('snapshot_version')} (noop={published.get('noop')})"
    )
    _render_projection(session_id)
    _verify_landing(expect_files)


def _render_projection(actor_session: str) -> None:
    """投影重打（唯一合法写者=生成器，PG-wins 四象限全自动）；失败归一 TokenInsertError。"""
    from zephyr.governance.registry_projection.projection_generator import run as projection_run

    report = projection_run(
        _REPO,
        mode="render",
        registry_id=_REGISTRY_ID,
        physical_path=_REGISTRY_REL,
        actor_session=actor_session or "batch_creation_tokens",
    )
    if not report.ok and report.quadrant not in ("clean", "armed_initial"):
        raise TokenInsertError(
            f"投影重打未过（quadrant={report.quadrant}）: {report.detail}；证据={report.evidence_path}"
        )
    print(f"投影重打: quadrant={report.quadrant} wrote={report.wrote}")


def _verify_landing(expect_files: list[str] | None) -> None:
    """语义落位校验：expect_files 必须全部在账本 active 面（缺失=登记丢失，fail-closed）。"""
    if not expect_files:
        return
    landed = _registered_files_from_ledger()
    if landed is None:
        raise TokenInsertError("落位校验不可用（PG 只读面不可达）——登记结果未证实，请人工核对账本")
    missing = [f for f in expect_files if f.replace("\\", "/") not in landed]
    if missing:
        raise TokenInsertError(f"{len(missing)} 条未落位账本 active 面: {missing[:3]}")


def _wide_prefix_issues(files: list[str]) -> list[str]:
    """W4 宽前缀判定：计划登记数超限 或 扫描结果跨多个一级目录 → 出拒执行理由。"""
    issues: list[str] = []
    if len(files) > _WIDE_PREFIX_ENTRY_LIMIT:
        issues.append(f"计划登记 {len(files)} 条 > 上限 {_WIDE_PREFIX_ENTRY_LIMIT}")
    top_dirs = {p.replace("\\", "/").split("/", 1)[0] for p in files if p}
    if len(top_dirs) > 1:
        issues.append(f"前缀扫出 {len(top_dirs)} 个一级目录: {sorted(top_dirs)[:5]}")
    return issues


# === 提交指路指南递送接口（②，2026-09-24 st-commitsys-20260924） ===
# Owner 定调「拦截成本前移为指引成本」：token 登记仪式时点按路径类型递送对应
# checklist 段（规则递送）。加法面：只新增 stdout 输出，不改任何登记语义；
# 指南源册解析失败时降级为一行指针（绝不影响登记主流程）。
_GUIDE_SOURCES = _REPO / "docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources"
_GUIDE_REL = "docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md"


_TYPE_RULES = [
    ("tests/", ".py", "new_test_py"),
    ("src/zephyr/", ".py", "new_src_py"),
    ("scripts/", ".py", "new_script_py"),
    ("docs/01_policies_and_standards/rules/", ".yaml", "rules_yaml"),
]
_OTHER_ASSET_EXTS = (".json", ".sh", ".mmd")


def detect_file_type(rel_path: str) -> str | None:
    """按路径判定文件类型（表驱动；与 file_type_checklists_registry.yaml type_id 对齐，未分类返回 None）。"""
    p = rel_path.replace("\\", "/").lower()
    for prefix, ext, type_id in _TYPE_RULES:
        if p.startswith(prefix) and p.endswith(ext):
            return type_id
    if "_registry/catalogs/" in p and p.endswith((".yaml", ".yml")):
        return "registry_yaml"
    if p.startswith("docs/_working/") and p.endswith(".md"):
        return "working_md"
    if p.endswith(".md"):
        return "formal_md"
    if p.endswith((".yaml", ".yml")):
        return "config_yaml"
    if p.endswith(".ps1"):
        return "ps1"
    if p.endswith(_OTHER_ASSET_EXTS):
        return "other_new_asset"
    return None


def print_guide_for_path(rel_path: str) -> None:
    """打印该路径类型对应的 checklist 段 + 通用前置（fail-open 降级为指针行）。"""
    try:
        doc = yaml.safe_load((_GUIDE_SOURCES / "file_type_checklists_registry.yaml").read_text(encoding="utf-8")) or {}
        type_id = detect_file_type(rel_path)
        sections = []
        uni = doc.get("universal") or {}
        if uni:
            sections.append(("通用前置（每笔提交）", uni))
        sec = next(
            (s for s in (doc.get("file_types") or []) if s.get("type_id") == type_id),
            None,
        )
        if sec:
            sections.append((f"{sec.get('type_id')} — {sec.get('title', '')}", sec))
        print("=== 提交指路（指南递送）===")
        for title, s in sections:
            print(f"--- {title} ---")
            for step in s.get("steps", []) or []:
                print(f"  1. {step}")
            refs = s.get("gate_refs") or []
            if refs:
                print(f"  关联门禁: {', '.join(refs)}")
        print(f"  指南全文（机生禁手改）: {_GUIDE_REL}")
    except Exception as exc:  # noqa: BLE001 — 递送是加法面，故障零影响登记主流程
        print(f"=== 提交指路（降级）=== 指南全文: {_GUIDE_REL}（递送详情不可用: {type(exc).__name__}）")


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(
        description="creation_token 批量登记（CREATE-GUARD 批量通道=意图 API 薄壳：register→publish→render，裁定#502）"
    )
    ap.add_argument("--prefix", required=True, help="目录/路径前缀（相对仓库根，如 docs/_working/xt_lab）")
    ap.add_argument("--created-by", required=True, help="登记会话名（如 my-session）")
    ap.add_argument("--capability", required=True, help="能力名（token 前缀，如 xtreme_lab）")
    ap.add_argument(
        "--anchor-capability",
        default=None,
        help="（已退役，收下忽略）直写时代插入锚点参数；账本登记无插入锚语义（裁定#502）",
    )
    ap.add_argument(
        "--merge-evaluation",
        default=None,
        help="合并评估结论一句话（裁定#375 四判据，随 payload 登记进账本；缺省仅提示补填）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只列计划，零写入")
    ap.add_argument(
        "--wide-prefix",
        action="store_true",
        help="宽前缀确认旗（W4 防呆）：计划登记 >50 条或跨多个一级目录时，须先 --dry-run "
        "预览并把输出贴回 Owner/会话确认，再显式带本旗实跑（emomine 481 条误扫治本）",
    )
    ap.add_argument(
        "--emit-guide",
        default=None,
        metavar="PATH",
        help="只查不改：按路径类型打印提交指路 checklist 段（提交前自检正门；登记成功后也会自动递送）",
    )
    args = ap.parse_args()

    if args.emit_guide:
        print_guide_for_path(args.emit_guide)
        return 0

    if args.anchor_capability:
        print("NOTICE: --anchor-capability 已随直写轨退役（裁定#502），参数收下忽略（账本无插入锚语义）")

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
            "或事后走 api.update 在账本条目补字段（投影手改无效）。"
        )

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    block = build_block(files, args.created_by, args.capability, today, merge_evaluation=args.merge_evaluation)
    print(f"计划登记 {len(files)} 条（capability={args.capability}, created_by={args.created_by}）:")
    for f in files[:10]:
        print(f"  {f}")
    if len(files) > 10:
        print(f"  ...（共 {len(files)}）")

    # W4 防呆（2026-09-22 注册表事故，emomine 481 条误扫治本）：宽前缀批须显式确认。
    # dry-run 是预览通道不受限；实跑（账本登记）前拦截。
    wide_issues = _wide_prefix_issues(files)
    if wide_issues:
        if not args.dry_run and not args.wide_prefix:
            print(
                "FAIL: 宽前缀批拦截（W4 防呆）: " + "；".join(wide_issues) + "\n"
                "确认流程：①先加 --dry-run 预览完整清单；②把输出贴回 Owner/会话确认；"
                "③确认后显式加 --wide-prefix 重新实跑。",
                file=sys.stderr,
            )
            return 1
        if args.wide_prefix:
            print(f"WARN: --wide-prefix 显式确认宽前缀批: {'；'.join(wide_issues)}")

    if args.dry_run:
        print("DRY-RUN：零写入")
        return 0

    try:
        insert_block(block, args.anchor_capability or args.capability, expect_files=files)
    except TokenInsertError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: 已登记 {len(files)} 条（意图 API 三步 register→publish→render）")
    print_guide_for_path(args.prefix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
