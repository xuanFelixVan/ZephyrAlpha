# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（YAML 驱动自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注册表结构硬化门禁——staged 版本必须 yaml.safe_load 通过 且 顶层根键唯一（yaml.compose
#   节点树判重，PyYAML 对重复根键静默取后者的盲区由本检查补上）；capability 注册表另有 di_seam_exemptions
#   末位+creation_tokens list 两断言。解析失败/结构破坏 → fail-closed 阻断（2026-09-14 立：同名键嵌套
#   creation_tokens(L883) 与顶层(L4987) 共存+EOF 尾追悬挂条目致全库解析炸四连（9ca0f62b95 修/1edeea81b4 修/
#   a5883d01 修/94aa4111 批内修）；2026-09-15 扩：data_asset_registry.yaml 双 datasets 根键（L752/755，
#   PyYAML 静默取后者，前段插条目被解析层忽略）随 st-patgov 合并批入库（件3），watch 面同步扩入+根键唯一
#   硬化；正确追加姿势=插既有根键的列表尾+提交前必验 parse；阻断与放行均落审计 .runtime/gate_audit/registry_yaml_parse.jsonl；
#   2026-10-09 扩（A-12 治本）：capability 册加 token 级只增不减守门——HEAD 顶层
#   creation_tokens 复合身份（file|token=）相对 staged 差集非空 → 阻断（投影指纹只证
#   staged==PG 投影，不证投影未落后 HEAD；直提 render-sync 整档覆盖抹他道 token 的
#   病根封堵）；白名单=[allow-mass-deletion:reason≥10字]（与 REGISTRY-MASS-DELETION
#   同标记）；HEAD 缺失/解析失败 fail-open
#   2026-10-14 真源对齐（st-maint7-20261014 P0-2②）：差集不再直接判死——逐条问 PG
#   registry_ledger（REG-CAPCAN-001／family_key=creation_tokens，键=复合身份加 file= 前缀），
#   仅真源 status='active' 者计入阻断；PG 查无／已 retire 者＝HEAD 挂的是退役残留，
#   投影按真源剔除属合法收敛，放行并落审计 event=head_token_lag_pg_cleared（实证形态＝
#   10-13 夜 6 袋全被同一条 retired token 拦死）。账本不可达／查询异常／非复合身份
#   ⇒ 全条照旧阻断（只加对账不放行，与 create_guard T4 第三源同哲学）
#   2026-10-15 分级与共析（st-perfz2-20261015 P0-1，Owner 今晚 st-diskp0 总包图纸①）：
#   ①结构序检查降 warn——顶层非 mapping／根键重复／di_seam_exemptions 缺失或非末位／
#   creation_tokens 非 list 四类结构序问题改 logger.warning+审计（warn_issues 字段）放行，
#   **仅 yaml.safe_load 语法错误 fail-closed**（投影私改 tamper 与 A-12 token 滞后两执法
#   面不属结构序，照旧阻断；preflight_merge_terminal 判据零变化——merge 通道仍全量阻断）；
#   ②共析接共享缓存——staged 字节经 _capability_registry_io.parse_registry_text_cached
#   喂入（键=盘面 path+mtime_ns+size，sha256 校验把关；staged≠盘面只返回不回填），与
#   CREATE-GUARD/SSOT/OVERLAP 同册一次 yaml.safe_load（96,697 行册单次 ~4.8s，实测每轮
#   全链解析 5→3 次、不变轮 3→0）；staged identities 从共享 data 派生零重析，HEAD identities
#   按内容 sha 进程内 memo（HEAD 文本不可变，纯 memo 判据零变化）
# [MODIFY-GUARD] gate_id="REGISTRY-YAML-PARSE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；
#   2026-10-10 st-maint1-20261010 件③：新增公开判据函数 preflight_merge_terminal（merge 通道补检，
#   git merge-tree 算合并终态字节+就地复用本门 _structural_issues，两条 merge 通道共用单一真源）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 失败/文件不可读 → fail-open 跳过（encoding 类 gate 覆盖）；staged 版本 YAML 语法解析失败/投影私改（tamper）/token 滞后（A-12）→ fail-closed 阻断（passed=False，报错附正确追加姿势教学）；结构序四类（非 mapping/根键重复/exemptions 末位/creation_tokens list）→ 降 warn 放行+审计（st-perfz2-20261015 P0-1 分级）；审计写失败静默降级。preflight_merge_terminal 永不抛异常——git/装载失败归 state="unavailable" 交调用方（调用方默认同样阻断，禁把"跑不动"读成"通过"），其判据零变化（merge 通道仍全量阻断）
# [TESTS] tests/governance/commit_gates/test_registry_yaml_parse_gate.py; tests/gov/governance/rule_bridge/test_session_worktree_merge_preflight.py（merge 通道补检红蓝，含生产通道）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L
# [TTL] permanent
"""registry_yaml_parse_gate.py — 注册表结构硬化门禁（防尾追悬挂/防重复根键）
# [ALGO_FLOW]

背景（2026-09-14，同病四连）：
    capability_canonical_file_registry.yaml 顶层键序=[schema_version…capabilities,
    creation_tokens, di_seam_exemptions]——di_seam_exemptions 在 creation_tokens 之后，
    EOF 追加 token 条目必落错段（悬挂在 exemptions 之后），全库 YAML 解析炸：
    capability_lookup 挂、所有读该表的会话挂。2026-09-13/14 四次同病
    （pattern 会话修一次/sim 会话修一次/st-sopreorg 修两次），口头纪律+"提交前验 parse"
    的约定反复失守 → 硬化为 commit gate。

扩面（2026-09-15，图形库治理上报件3）：
    data_asset_registry.yaml 双 `datasets:` 根键（L752 空 null 键/L755 真块）——
    PyYAML 对重复根键静默取后者，人工/工具往前段插条目会被解析层无感忽略。
    合并批入库后，watch 面扩入该文件，并新增**顶层根键唯一**断言（yaml.compose
    节点树判重——safe_load 对重复键静默覆盖，节点树才同时保留两个），
    capability 注册表同享此检查。

检测逻辑（对 staged 文本，按档案分档）：
    capability_registry 档：
        1. yaml.safe_load 通过（解析炸直接阻断——唯一 fail-closed 结构判据）
        2. 顶层根键唯一（yaml.compose 判重）
        3. 顶层 di_seam_exemptions 键存在且为末位键（尾追悬挂判别式）
        4. creation_tokens 键存在且为 list（结构走样拦截）
    data_asset_registry 档：
        1. yaml.safe_load 通过
        2. 顶层根键唯一

    st-perfz2-20261015 P0-1 分级：上述 2/3/4 与"顶层非 mapping"四类**结构序检查降
    warn**（logger.warning+审计 warn_issues，放行不阻断）——结构序走样是"投影器次序
    病"，由投影器侧真源修复，不再把无辜提交人挡在门外；仅语法错误 fail-closed。
    另两类执法面（tamper 投影私改/A-12 token 滞后）不属结构序，照旧阻断。

触发范围：staged 命中 _WATCH_FILES（capability_canonical_file_registry.yaml /
data_asset_registry.yaml，两个高频追加热注册表）——紧范围不加宽（净删防护由
REGISTRY-MASS-DELETION 负责，编码由 ENCODING-SAFETY 负责）。

无逃生标记：解析炸/根键重复的注册表没有"先合入再修"的合法场景——修复后在同一
commit 重新 staged 即可（gate 看的是 staged 终态）。

Usage::

    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
        make_registry_yaml_parse_gate,
    )
    registry.register(make_registry_yaml_parse_gate())
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _build_own_scope,
    _norm_rel,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_registry_yaml_parse_gate", "preflight_merge_terminal"]

# 审计落点（.runtime/gate_audit/ 家族惯例）
_AUDIT_REL = ".runtime/gate_audit/registry_yaml_parse.jsonl"

# 热追加目标 watch 表 → 结构断言档案（紧范围不加宽；净删防护归 REGISTRY-MASS-DELETION，
# 编码归 ENCODING-SAFETY）。capability=全量断言；data_asset=parse+根键唯一；
# hot_registry_basic=parse+根键唯一（结构面）+投影 tamper 判别（tamper 对全部 watch 面
# 生效，不分支档案——staged≠状态文件指纹即拦，2026-10-09 C 件扩面裁定#502 战役）。
# P0 七册扩面（st-regsolo-20261010）：六册在挂；module_translation_registry 暂缓——
# 他会话（st-dexp）活跃持有直写面，watch 上线即砖其合法流，随翻译登记改道意图 API
# 后同批上线（translate 轨退役=本战役 A2 车道）。
_WATCH_FILES: dict[str, str] = {
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml": "capability_registry",
    "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml": "hot_registry_basic",
    "architecture_model/contracts/error_code_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml": "hot_registry_basic",
}

# 向后兼容别名（capability 注册表=首 watch 目标）
_WATCH_FILE = next(iter(_WATCH_FILES))

# 教学信息（阻断时给出正确姿势，治"每次重新发明修法"）
_TEACH = (
    "正确追加姿势：条目插在既有根键的列表尾（capability 注册表的 token 条目插 "
    "creation_tokens 列表尾=di_seam_exemptions: 行之前，注意 L883 有一个嵌套同名键勿错插），"
    "顶层根键禁止重复（PyYAML 静默取后者，前段插条目会被解析层无感忽略），"
    "插入后必须 yaml.safe_load 验证通过再提交"
)

# ── W-M1 投影执法扩展（st-wm1-buildB-20260923）───────────────────────────────
# 投影管理册（状态文件存在=已武装）私改检测：staged blob sha ≠ 投影状态文件
# content_sha256 → 阻断。判别真源=本地状态文件（PG 宕机照样抓私改，丙号文 §3.2
# 执法层契约：门禁只读 staged blob + 状态文件两个便宜物，零 PG 依赖）。
# 未武装（状态文件缺失/损坏/registry_path 不符）→ fail-open 零行为（cutover 前
# 登记正门仍是 batch_creation_tokens 直写，全量兼容）。生成器自身提交天然
# staged==S 通过。挂本文件不新增 gate（净零红线），own-scope 由 _build_own_scope 既有。
_PROJECTION_STATE_REL = ".runtime/projection/registry_projection_state.json"


def _projection_tamper_issue(gateway, watch_file: str) -> str | None:
    """投影私改判别（返回问题文案或 None=通过/不适用）。永不抛异常。

    状态文件双形态（PD-1 v2）：v2 map（registries 键控多册）逐条目匹配本册；
    v1 单册平铺兼容。本册无条目=别册（fail-open 零行为）。
    """
    try:
        import json

        from zephyr.shared.io.file_utils import content_sha256

        root = Path(getattr(gateway, "project_root", "."))
        state_file = root / _PROJECTION_STATE_REL
        if not state_file.exists():
            return None  # 未武装：投影管理未启用，零行为
        state = json.loads(state_file.read_text(encoding="utf-8"))
        entry: dict | None = None
        registries = state.get("registries")
        if isinstance(registries, dict) and registries:
            for key, value in registries.items():
                if not isinstance(value, dict):
                    continue
                candidate = str(value.get("registry_path") or key)
                if candidate and _norm_rel(gateway, candidate) == _norm_rel(gateway, watch_file):
                    entry = value
                    break
            if entry is None:
                return None  # v2 在挂但本册无条目：别册/未武装本册
        else:
            state_registry = str(state.get("registry_path", ""))
            if not state_registry or _norm_rel(gateway, state_registry) != _norm_rel(gateway, watch_file):
                return None  # 状态文件登记的是别册
            entry = state
        expected = entry.get("content_sha256")
        if not expected:
            return None  # 状态损坏 → fail-open（daemon 层兜底抓）
        staged_text = _read_staged_file(gateway, watch_file)
        if staged_text is None:
            return None  # 读失败 fail-open（encoding 类 gate 覆盖）
        if content_sha256(staged_text) != expected:
            return (
                "staged 内容与投影状态文件指纹不符（私改投影册无效）——"
                "此文件是 PG 账本投影：改动请走意图 API 登记+生成器重打（"
                "python scripts/governance/registry_projection/registry_projection_generator.py --render）"
            )
    except Exception:  # noqa: BLE001 — 执法扩展整体 fail-open
        logger.debug("projection tamper check fail-open", exc_info=True)
        return None
    return None


# ── A-12 直提通道 token 级只增不减守门（st-chiefc-20261009，2026-10-09）────────
# 病根：capability 册是机生投影（REGISTRY-YAML-PARSE 强制 staged==投影状态指纹），
# 但指纹只证「staged==PG 投影」，不证「投影未落后于 HEAD」——batch_creation_tokens
# 直写轨（gate 可见 PG 不知）与他道 api.register 轨在「入队→落地」窗内互相覆盖，
# 直提 render-sync 整文件 commit 把 HEAD 有而投影无的 token 整批抹掉（实弹：5 token
# 三次被抹，死信再产根因）。本守门=投影指纹之外的第二判据：HEAD 顶层 creation_tokens
# 复合身份（file|token=，与合并器 _merge_entry_identity 同构）相对 staged 的差集非空
# → 阻断；白名单=[allow-mass-deletion:reason≥10字]（与 REGISTRY-MASS-DELETION 同
# 标记同语义——合法退役经 PG retire 后重打投影时用同一标记过两门）。HEAD 缺失/读取
# 失败/解析失败 → fail-open。挂本文件不新增 gate（净零红线），own-scope 既有。
_PROJECTION_LAG_MARKER_RE = re.compile(r"\[allow-mass-deletion:([^\]]{10,})\]")

# SQL 集中化（§5.160.2 NO-BARE-SQL，对标 create_guard._SQL_PG_ACTIVE_TOKEN_BY_FILE 同规格）：
# {schema} 由调用点 format 注入，参数化 %s 承载 registry_id/family_key/entry_key 值。
# 与 create_guard 那条的差别=精确键匹配（对账单条身份），非按 file 前缀问存在。
_SQL_PG_ACTIVE_TOKEN_BY_KEY = (
    "SELECT 1 FROM {schema}.registry_entry "
    "WHERE registry_id=%s AND family_key=%s AND status='active' AND entry_key=%s LIMIT 1"
)


def _creation_token_identities(text: str, data: object = None) -> dict[str, str] | None:
    """顶层 creation_tokens 条目复合身份集（file|token= → 展示名）。解析失败/结构不符 → None。

    st-perfz2 P0-1：``data`` 给定时（共享缓存已解析的同一字节产物）零重析直接派生；
    None 时保持旧行为自行 safe_load（HEAD 面等无共享键的字节）。
    """
    if data is None:
        try:
            import yaml

            data = yaml.safe_load(text)
        except Exception:  # noqa: BLE001 — 解析失败由 _structural_issues 报告
            return None
    if not isinstance(data, dict):
        return None
    ct = data.get("creation_tokens")
    if not isinstance(ct, list):
        return None
    out: dict[str, str] = {}
    for entry in ct:
        if not isinstance(entry, dict):
            continue
        file_v = entry.get("file")
        token_v = entry.get("token")
        if isinstance(file_v, str) and isinstance(token_v, (str, int, float)):
            out[f"{file_v}|token={token_v}"] = f"{file_v} (token={token_v})"
        else:
            for v in entry.values():  # 无 file/token 对 → 退首标量单键（存在级比对）
                if isinstance(v, (str, int, float, bool)):
                    out[str(v)] = str(v)
                    break
    return out


def _pg_endorsed_token_ids(gateway, missing_ids: list[str]) -> tuple[set[str], str]:
    """问 PG 账本：HEAD 有而投影无的条目里，哪些**真源仍背书**（该留在拦截止里）。

    病根实证（非推测）：10-13 夜 6 只死信全被同一条拦——
    ``docs/_working/tdm_goal_structure_research_2026_10_13.md`` 的 token 条目。查 PG：
    该 entry ``status='retired'``（真源 15470 active／181 retired），而当时 HEAD 的
    YAML 还挂着它的退役残留，新重打的投影已按真源剔除 ⇒ 本守门拿**滞后的 HEAD** 当
    基准，把六个无辜袋连杀三轮以上。令卡处方＝"token 真源＝PG，判据读面与真源方向
    对齐，禁投影滞后判死"（Owner 在册正解：改喂给闸的输入指向，不弱化判据）。

    判据方向（只加对账，不松门禁）：
      1. 真源 ``status='active'`` 命中该复合键 ⇒ 该条目确实该在投影里，staged 缺它＝
         真整档回退 ⇒ 留在拦截止（照拦，本体不动）；
      2. 真源查无／已 retire ⇒ HEAD 里那份是退役残留，投影按真源剔除＝合法收敛 ⇒ 放行；
      3. 同 file 有其他 active 条目而精确键未命中（键形漂移）⇒ 保守照拦；
      4. 账本不可达／驱动异常／查询异常 ⇒ **全部按 active 处理（照拦）**，绝不让
         "读不到账本"变成放行（与 create_guard T4 第三源同哲学）；
      5. 非复合身份（``_creation_token_identities`` 的退化单键形态）无法与 PG entry_key
         对账 ⇒ 照拦（宁不误放）。

    registry_id/family_key/SQL 形态沿 create_guard 的在册单点（``_SQL_PG_ACTIVE_TOKEN_BY_FILE``
    + ``_CREATION_TOKEN_REGISTRY_ID``，ROOR 同物理路径双挂号取正源常量的理由见其注释），
    故对本模块零新增真源；懒加载 import 避免给 gate 装载链添依赖。永不抛异常。
    """
    composite = [k for k in missing_ids if "|token=" in k]
    degenerate = [k for k in missing_ids if "|token=" not in k]
    if not composite:
        return set(missing_ids), "无复合身份可对账（退化形态全照拦）"
    try:
        # 私约复用：create_guard 不 import 本模块（无环），取其在册 SQL/registry_id 单点
        from zephyr.gov_enforcement.commit_gates.create_guard import (
            _CREATION_TOKEN_REGISTRY_ID,
            _SQL_PG_ACTIVE_TOKEN_BY_FILE,
        )
        from zephyr.governance.registry_ledger.registry_ledger_ddl import SCHEMA_NAME
        from zephyr.infrastructure.database_service import DatabaseService
    except Exception as exc:  # noqa: BLE001 — 账本侧不可达=全照拦
        logger.warning(
            "REGISTRY-YAML-PARSE: PG 真源对账不可达（%s: %s），按投影口径照拦。",
            type(exc).__name__,
            str(exc)[:160],
        )
        return set(missing_ids), "PG 账本不可达（照拦）"

    endorsed: set[str] = set()
    sql_exact = _SQL_PG_ACTIVE_TOKEN_BY_KEY.format(schema=SCHEMA_NAME)
    sql_file = _SQL_PG_ACTIVE_TOKEN_BY_FILE.format(schema=SCHEMA_NAME)
    conn = None
    try:
        conn = DatabaseService().get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            for ident in composite:
                cur.execute(sql_exact, (_CREATION_TOKEN_REGISTRY_ID, "creation_tokens", f"file={ident}"))
                if cur.fetchone() is not None:
                    endorsed.add(ident)
                    continue
                file_part = ident.split("|token=", 1)[0]
                cur.execute(sql_file, (_CREATION_TOKEN_REGISTRY_ID, "creation_tokens", f"file={file_part}|%"))
                if cur.fetchone() is not None:
                    endorsed.add(ident)  # 键形漂移保守面：同 file 有 active 条目 ⇒ 照拦
    except Exception as exc:  # noqa: BLE001 — 查询异常=全照拦，禁止读不到即放行
        logger.warning(
            "REGISTRY-YAML-PARSE: PG 真源对账查询异常（%s: %s），按投影口径照拦。",
            type(exc).__name__,
            str(exc)[:160],
        )
        return set(missing_ids), "PG 查询异常（照拦）"
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 — 只读连接回收失败不影响已取定的判定
                logger.debug("PG token 对账连接回收失败（忽略）", exc_info=True)
    endorsed |= set(degenerate)
    cleared_n = len(missing_ids) - len(endorsed)
    return endorsed, f"PG 对账：{len(endorsed)} 条 active 照拦／{cleared_n} 条真源不背书放行"


def _head_token_lag_issue(
    gateway, watch_file: str, staged_text: str, message: str, staged_data: object = None
) -> str | None:
    """直提通道 capability 册 token 级只增不减判别（返回问题文案或 None=通过/不适用）。永不抛异常。

    st-perfz2 P0-1：staged 侧 identities 从共享缓存 data 派生（零重析）；HEAD 侧文本
    按 sha 进程内 memo（HEAD 文本不可变——同 sha 必同 identities，纯 memo 判据零变化）。
    """
    try:
        result = gateway.run_git(["git", "show", f"HEAD:{watch_file}"])
        if result.returncode != 0:
            return None  # 新文件/无 HEAD → fail-open
        head_text = result.stdout
        head_ids = _identities_cached(head_text)
        staged_ids = _creation_token_identities(staged_text, data=staged_data)
        if head_ids is None or staged_ids is None:
            return None  # 判不了 → fail-open（结构面由 _structural_issues 把守）
        missing = sorted(set(head_ids) - set(staged_ids))
        if not missing:
            return None
        # 真源对齐（st-maint7-20261014 P0-2②）：HEAD 是滞后面，不是真源——差集里哪些条目
        # 该存在由 PG 账本判；真源已 retire 的残留不再把无辜袋判死（详见函数 docstring）。
        endorsed, pg_note = _pg_endorsed_token_ids(gateway, missing)
        cleared = [k for k in missing if k not in endorsed]
        if cleared:
            logger.warning(
                "REGISTRY-YAML-PARSE: %s 相对 HEAD 少 %d 条，其中 %d 条经 PG 真源判定不该在投影里"
                "（退役残留/真源查无），不按回退判死: %s",
                watch_file,
                len(missing),
                len(cleared),
                "; ".join(head_ids[k] for k in cleared[:3]),
            )
            _audit(
                gateway,
                {
                    "event": "head_token_lag_pg_cleared",
                    "file": watch_file,
                    "missing_total": len(missing),
                    "cleared_by_pg": cleared[:20],
                    "still_blocking": [head_ids[k] for k in missing if k in endorsed][:20],
                    "pg_note": pg_note,
                },
            )
        missing = [k for k in missing if k in endorsed]
        if not missing:
            return None
        if _PROJECTION_LAG_MARKER_RE.search(message or ""):
            logger.warning(
                "REGISTRY-YAML-PARSE: %s 相对 HEAD 少 %d 条 token，message 标记放行（合法退役须 PG retire 对账）",
                watch_file,
                len(missing),
            )
            return None
        sample = "; ".join(head_ids[k] for k in missing[:5])
        return (
            f"相对 HEAD 少 {len(missing)} 条 creation_token（如 {sample}）——直提整档覆盖"
            f"会抹掉他道已落条目（陈旧投影/双轨滞后）。修法：PG 登记（api.register）后"
            f"重打投影（registry_projection_generator --render）再提交；确属合法退役"
            f"（PG retire 已对账）：commit message 加 [allow-mass-deletion:<reason≥10字>]"
            f"［PG 对账状态：{pg_note}］"
        )
    except Exception:  # noqa: BLE001 — 执法扩展整体 fail-open
        logger.debug("head token lag check fail-open", exc_info=True)
        return None


def _audit(gateway, record: dict) -> None:
    """审计落盘（jsonl append；fail-open：写失败不阻断）。"""
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "registry_yaml_parse.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        logger.debug("REGISTRY-YAML-PARSE audit write failed (non-blocking)", exc_info=True)


def _duplicate_root_keys(text: str) -> list[str]:
    """yaml.compose 节点树判重——safe_load 对重复根键静默取后者，节点树才同时保留两个。

    永不抛异常（compose 失败返回空=由 safe_load 断言兜底报解析失败）。
    """
    try:
        import yaml

        node = yaml.compose(text)
    except Exception:  # noqa: BLE001 — 解析失败由 _structural_issues 的 safe_load 断言报告
        return []
    if node is None or not hasattr(node, "value") or not isinstance(node.value, list):
        return []  # 非 MappingNode（Scalar/Sequence）→ 无根键可判重
    seen: set[str] = set()
    dups: list[str] = []
    for key_node, _ in node.value:
        k = str(getattr(key_node, "value", ""))
        if k in seen and k not in dups:
            dups.append(k)
        seen.add(k)
    return dups


_PARSE_CACHE: dict[str, tuple[str, list[str]]] = {}
_PARSE_CACHE_MAX = 8

# ── st-perfz2-20261015 P0-1 共析面 ────────────────────────────────────────────
# yaml.compose 与 safe_load 同价（96,697 行册各 ~4.8s）——根键判重结果按内容 sha 进程内
# memo（同 sha 必同节点树，纯 memo 判据零变化）；有界溢出整表弃（缓存不是判据真源）。
_DUPKEYS_CACHE: dict[str, list[str]] = {}
_DUPKEYS_CACHE_MAX = 16

# HEAD 文本 identities memo（HEAD blob 不可变；同 sha 必同身份集）。键=text sha256 前 24 位。
_HEAD_IDENTITIES_CACHE: dict[str, dict[str, str] | None] = {}
_HEAD_IDENTITIES_CACHE_MAX = 8


def _text_cache_key(text: str, profile: str) -> str:
    import hashlib as _hl

    return f"{profile}:{_hl.sha256(text.encode('utf-8', errors='replace')).hexdigest()[:24]}"


def _identities_cached(text: str) -> dict[str, str] | None:
    """HEAD 文本 identities（sha 键 memo；None 结果同样入 memo——负结果对不可变文本是稳态）。"""
    try:
        key = _text_cache_key(text, "identities")
        if key in _HEAD_IDENTITIES_CACHE:
            return _HEAD_IDENTITIES_CACHE[key]
        ids = _creation_token_identities(text)
    except Exception:  # noqa: BLE001 — memo 设施故障退直析（fail-open 不改判定）
        return _creation_token_identities(text)
    if len(_HEAD_IDENTITIES_CACHE) >= _HEAD_IDENTITIES_CACHE_MAX:
        _HEAD_IDENTITIES_CACHE.clear()
    _HEAD_IDENTITIES_CACHE[key] = ids
    return ids


def _duplicate_root_keys_cached(text: str, cache_key: str) -> list[str]:
    """根键判重 sha-memo 版（同内容跨轮零 compose）。"""
    try:
        cached = _DUPKEYS_CACHE.get(cache_key)
        if cached is not None:
            return list(cached)
        dups = _duplicate_root_keys(text)
    except Exception:  # noqa: BLE001 — memo 故障退直算
        return _duplicate_root_keys(text)
    if len(_DUPKEYS_CACHE) >= _DUPKEYS_CACHE_MAX:
        _DUPKEYS_CACHE.clear()
    _DUPKEYS_CACHE[cache_key] = list(dups)
    return dups


def _shared_registry_data(gateway, watch_file: str, staged_text: str) -> tuple[object, object]:
    """staged 字节喂共享解析缓存（st-perfz2 P0-1）。返回 (data, exc)，永不抛异常。

    盘面锚序与 create_guard._load_capability_registry 同款（主仓根→project_root）——
    键=盘面 (path, mtime_ns, size)，与 CREATE-GUARD/SSOT/OVERLAP 同一条目：它们先解析过
    （staged==盘面常态）本门零解析命中。staged≠盘面时 parse_registry_text_cached 只返回
    不回填（sha 把关，防毒化盘面真源条目）。锚设施/共享模块故障 → (None, None)，
    _structural_issues 自行 safe_load（退旧路径，fail-open 不改判定）。
    """
    try:
        from pathlib import Path as _P

        from zephyr.gov_enforcement.commit_gates._capability_registry_io import (
            parse_registry_text_cached,
        )
        from zephyr.shared.io.paths import anchor_main_root

        root = _P(str(getattr(gateway, "project_root", ".") or "."))
        try:
            main_root = anchor_main_root(root)
        except Exception:  # noqa: BLE001 — 锚设施异常退 project_root
            main_root = root
        for base in (main_root, root):
            cand = base / watch_file
            try:
                if cand.exists():
                    return parse_registry_text_cached(cand, staged_text)
            except OSError:
                continue
        import yaml

        return yaml.safe_load(staged_text), None  # 无盘面锚=纯解析（无键不缓存）
    except Exception:  # noqa: BLE001 — 共析设施故障退旧路径（_structural_issues 自析）
        return None, None


def _is_syntax_issue(issue: str) -> bool:
    """结构序降级（st-perfz2 P0-1）分级判别：仅 yaml.safe_load 语法错误属 fail-closed 级。"""
    return issue.startswith("yaml.safe_load 解析失败")


def _structural_issues(text: str, profile: str, data: object = None) -> list[str]:
    """二层⑦缓存（Owner 全批 2026-10-05）：13k 条热册 yaml.safe_load 每次 ~2s，
    同内容重复解析 36 次/天=白跑 72s。以 sha256(text) 为键缓存结果，命中即返。
    fail-open：缓存写入失败静默跳过（安全不降级=每次都全量解析）。

    st-perfz2 P0-1：``data`` 给定时（共享缓存产物）跳过本函数自己的 safe_load——
    一次解析喂 safe_load 断言+compose 判重两判据；compose 结果亦按 sha memo。
    """
    _key = _text_cache_key(text, profile)
    _cached = _PARSE_CACHE.get(_key)
    if _cached is not None:
        return list(_cached)
    """对 staged 文本做档案化断言 → 问题清单（空=通过）。永不抛异常。

    capability_registry 档：parse + 根键唯一 + exemptions 末位 + creation_tokens list。
    data_asset_registry 档：parse + 根键唯一。
    """
    issues: list[str] = []
    if data is None:
        try:
            import yaml

            data = yaml.safe_load(text)
        except Exception as exc:  # noqa: BLE001 — 解析失败=阻断本体
            issues.append(f"yaml.safe_load 解析失败: {str(exc)[:160]}")
            if len(_PARSE_CACHE) < _PARSE_CACHE_MAX * 2:
                _PARSE_CACHE[_key] = list(issues)
            return issues
    if not isinstance(data, dict):
        issues.append(f"顶层不是 mapping（实际 {type(data).__name__}）")
        if len(_PARSE_CACHE) < _PARSE_CACHE_MAX * 2:
            _PARSE_CACHE[_key] = list(issues)
        return issues
    dups = _duplicate_root_keys_cached(text, _key)
    if dups:
        issues.append(f"顶层根键重复: {dups}（PyYAML 静默取后者——前段条目会被解析层无感忽略，必须合并为单键）")
    if profile == "capability_registry":
        keys = list(data.keys())
        if "di_seam_exemptions" not in keys:
            issues.append("顶层 di_seam_exemptions 键缺失")
        elif keys[-1] != "di_seam_exemptions":
            issues.append(f"di_seam_exemptions 不是末位顶层键（当前末位={keys[-1]!r}，键序={keys[-3:]}）")
        ct = data.get("creation_tokens")
        if not isinstance(ct, list):
            issues.append(f"creation_tokens 不是 list（实际 {type(ct).__name__}）")
    if len(_PARSE_CACHE) < _PARSE_CACHE_MAX * 2:
        _PARSE_CACHE[_key] = list(issues)
    return issues


def preflight_merge_terminal(run_git: object, target_ref: str, other_ref: str) -> tuple[list[str], str]:
    """merge 通道补检（A-14，st-maint1-20261010 件③）：对**合并终态字节**跑本门同一判据。

    为什么需要它（不是重复造轮）：`git merge` 结构性不触发 pre-commit hooks，而
    rule_bridge/session_worktree 又自 2026-07-20 #ARCH-WORKTREE-PRE-MERGE-SYSPATH-001
    起 `_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True` 把 pre-merge 的 commit gate **整体跳过**——
    两条叠加＝merge 是门禁零覆盖通道。2026-10-10 一枚 R5 投影同步袋正是经此通道把
    "顶层 di_seam_exemptions 键缺失"的剥光 CAP 册烤进 dev（e0c72f63c4），随后全仓
    新建件入库被同签名熔断连堵 6 次。

    与原治本的兼容：#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001 的病根是 subprocess-based gate
    在主工作区 sys.path 下 import 失败。本检不启 subprocess gate、不碰 index、不 reset
    HEAD——只用 `git merge-tree --write-tree` 在对象库算合并终态，再就地调用本模块自己的
    `_structural_issues`（判据真源单口，禁调用方复制逻辑），sys.path 病根不适用。

    参数：`run_git(args: list[str]) -> 带 returncode/stdout 的对象`（调用方提供 git 通道，
    本函数与仓根/工作区解耦，车道与主区同一实现）。
    返回 `(问题清单, 状态)`；状态 ∈ {checked, unavailable, conflict}：
      - checked＝判据已跑到，清单非空即结构性违规（**永不可越权**）；
      - unavailable＝补检跑不动（git 过旧/取不到树/判据装载失败），调用方默认同样阻断，
        仅显式越权旗可放行并留痕；
      - conflict＝合并本身有冲突（merge-tree rc=1），终态未定，交回 git 正常流程，
        此处不抢判以免把"待人工解冲突"误报成结构违规。
    """
    issues: list[str] = []
    mt = run_git(["merge-tree", "--write-tree", target_ref, other_ref])  # type: ignore[operator]
    rc = int(getattr(mt, "returncode", 1))
    raw = ((getattr(mt, "stdout", "") or "") + (getattr(mt, "stderr", "") or "")).strip()
    if rc > 1 or not raw:
        return [f"merge-tree 不可执行（rc={rc}）: {raw[:200] or '无输出'}"], "unavailable"
    if rc == 1:
        return [], "conflict"
    tree = raw.splitlines()[0].strip()

    diff = run_git(["diff", "--name-only", tree, target_ref])  # type: ignore[operator]
    if int(getattr(diff, "returncode", 1)) != 0:
        return [f"合并树差分不可执行（rc={getattr(diff, 'returncode', '?')}）"], "unavailable"
    changed = {ln.strip() for ln in (getattr(diff, "stdout", "") or "").splitlines() if ln.strip()}

    for rel, profile in _WATCH_FILES.items():
        if rel not in changed:
            continue  # 本次 merge 未触碰该册——既有病不连坐本次合并（own-diff 作用域，宪法 §3.1）
        show = run_git(["show", f"{tree}:{rel}"])  # type: ignore[operator]
        if int(getattr(show, "returncode", 1)) != 0:
            issues.append(f"{rel}: 合并树内取不到该册字节（rc={getattr(show, 'returncode', '?')}）")
            continue
        for msg in _structural_issues(getattr(show, "stdout", "") or "", profile):
            issues.append(f"{rel} 合并终态结构校验未过: {msg}（教学：{_TEACH}）")
    return issues, "checked"


def make_registry_yaml_parse_gate() -> GateSpec:
    """构造 REGISTRY-YAML-PARSE pre-commit 门禁（priority=54）。

    staged 热注册表按档案断言（parse 通过/根键唯一/capability 注册表另查 exemptions
    末位+creation_tokens list）任一不满足 → fail-closed 阻断+教学信息；
    读失败/git 异常 → fail-open 跳过。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        try:
            result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
            if result.returncode != 0:
                return True, ""  # fail-open：git 失败不阻断
            staged_yaml = [
                f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(".yaml")
            ]
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("REGISTRY-YAML-PARSE fail-open: git diff 异常", exc_info=True)
            return True, ""

        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            staged_yaml = [f for f in staged_yaml if _norm_rel(gateway, f) in own_scope]

        watched = [(f, profile) for f, profile in _WATCH_FILES.items() if f in staged_yaml]
        if not watched:
            return True, ""

        # st-perfz2 P0-1 结构序降级分档：blocking=语法错误+tamper+token 滞后（fail-closed 不变）；
        # 结构序四类（非 mapping/根键重复/exemptions 末位/creation_tokens list）降 warn 放行。
        all_issues: list[tuple[str, list[str]]] = []
        warn_issues: list[tuple[str, list[str]]] = []
        for watch_file, profile in watched:
            staged_text = _read_staged_file(gateway, watch_file)
            if staged_text is None:
                continue  # fail-open：读失败（encoding 类 gate 覆盖）
            shared_data, _shared_err = _shared_registry_data(gateway, watch_file, staged_text)
            issues = _structural_issues(staged_text, profile, data=shared_data)
            syntax = [i for i in issues if _is_syntax_issue(i)]
            structural = [i for i in issues if not _is_syntax_issue(i)]
            tamper = _projection_tamper_issue(gateway, watch_file)
            if tamper:
                syntax.append(tamper)
            if profile == "capability_registry":
                # A-12 直提通道守门：投影指纹只证 staged==PG 投影，不证投影未落后 HEAD——
                # token 级只增不减补上双轨滞后窗（复用 own-scope：外来 staged 不拦，§3.1）
                lag = _head_token_lag_issue(
                    gateway, watch_file, staged_text, str(kwargs.get("commit_message") or ""), staged_data=shared_data
                )
                if lag:
                    syntax.append(lag)
            if syntax:
                all_issues.append((watch_file, syntax))
            if structural:
                warn_issues.append((watch_file, structural))

        for f, w in warn_issues:
            logger.warning(
                "REGISTRY-YAML-PARSE 结构序警告（降 warn 放行，st-perfz2 P0-1）: %s: %s",
                f,
                "; ".join(w),
            )
        _audit(
            gateway,
            {
                "timestamp": int(time.time()),
                "gate": "REGISTRY-YAML-PARSE",
                "action": "block" if all_issues else "pass",
                "session_id": session_id or "?",
                "files": {f: issues for f, issues in all_issues} if all_issues else [f for f, _ in watched],
                **({"warn_issues": {f: w for f, w in warn_issues}} if warn_issues else {}),
            },
        )
        if not all_issues:
            if warn_issues:
                warn_detail = "\n".join(
                    line
                    for f, w in warn_issues
                    for line in (f"REGISTRY-YAML-PARSE（warn，不阻断）: {f}:", *(f"  - {i}" for i in w))
                )
                return True, warn_detail
            return True, ""
        detail = "\n".join(
            line
            for f, issues in all_issues
            for line in (f"REGISTRY-YAML-PARSE: {f} 结构校验未过:", *(f"  - {i}" for i in issues))
        )
        if warn_issues:
            detail += "\n" + "\n".join(
                line
                for f, w in warn_issues
                for line in (f"REGISTRY-YAML-PARSE（warn，不阻断）: {f}:", *(f"  - {i}" for i in w))
            )
        msg = f"{detail}\n  {_TEACH}"
        logger.error(msg)
        return False, msg

    return GateSpec(
        gate_id="REGISTRY-YAML-PARSE",
        check=_check,
        priority=54,
    )
