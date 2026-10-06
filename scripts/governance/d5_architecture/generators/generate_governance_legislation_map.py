# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §governance_legislation_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_governance_legislation_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   （CLI 生成器按需触发，PERM-TRIGGER 手动模式铁律归 task_bound；同族先例=generate_strategy_card_lifecycle_map）
# [DEPENDENCIES] yaml；zephyr.governance.registry_ledger（REG-RULING-001 账本读面：payload.status 分布/取代链/快照版本/行数现算单一真源）+ zephyr.shared.io.file_utils.safe_write_text（热文件 CAS 写，AGENTS 硬规则13）——详单见下方详情块
# [CONSUMERS] config/governance_legislation_map.yaml（唯一产出）+ validate_governance_legislation_map（CV-05 counts 对拍反向核对）+ GOVERNANCE-LEGISLATION-MAP gate 触发面 + 对抗测试幂等实证
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 幂等=同账本态逐字节等（generated_at 恒为 effective_from 定值，禁壁钟——RULE-SCHEMA-TZ）；账本只读、写出面仅 --out 一处；结构层=骨架 §1/§2/§3 契约镜像（禁二次创作），实例层=账本现算（裁定实例=数据行非节点，INV-1 同款，计数只进 counts）；PG 不可达=报错退出不崩（禁静默产出半张图）
# [MODIFY-GUARD] 状态/机构/迁移/禁边编号以骨架为契约（增删先回写骨架同步校验器）；本件禁复制校验器判据
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 账本不可达/册投影不可读=返码1（不写盘）；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_governance_legislation_map_adversarial.py
# create-guard-not-dup: 裁定#486 准入的图16 生成器（立法流状态机镜像，结构契约=fig16 骨架 §1-§3），与 strategy_card_lifecycle（卡域）/governance_operations（运行时域）生成器无职责重叠——本件管立法条目状态面
#
# —— 详情块（14 字段头 30 行窗内，长文降为详情）——
#   结构真源：docs/_working/map_build/fig16_legislation/00_skeleton.md（§1 六态 + §2 九机构 +
#   §3 九合法迁移 + 七禁止边 = 语义契约，本生成器只做机读镜像不做二次创作）；
#   实例真源：PG 账本 registry_entry（REG-RULING-001，7f0beccac4 cutover 后唯一机械真源）——
#   active 行 payload.status 分布 / retired 行数 / superseded_by 取代链 / 快照版本 / 投影面行数；
#   读面=zephyr.governance.registry_ledger.api._open_default_conn（只读 SELECT，禁写）；
#   消费方：validate_governance_legislation_map（CV-05 counts==现算对拍）；
#   src/zephyr/gov_enforcement/commit_gates/map_family/governance_legislation_map_gate（触发面之一）；
#   tests/governance/d5_architecture/test_governance_legislation_map_adversarial.py（幂等实证）；
#   派生方向恒为 骨架+账本 → 图 YAML（禁手改图不回生成，校验器判红）；
#   人工语义层（laws/boundary/ssot_note）由常量持有随每次生成重写，实例层（counts）全部现算；
#   禁硬编码中英翻译字典；禁 datetime.now()/time.time()（RULE-SCHEMA-TZ）

"""图16 治理立法流图生成器（机生·幂等·禁取时）。

两条流水线，全部现算：
1. 结构镜像：骨架 §1/§2/§3 四张表 → states / machinery / transitions / forbidden_edges
   （编号与语义原样搬，禁二次创作）；
2. 账本对账：PG registry_entry（REG-RULING-001）→ counts（by_status 分布 / 行数 /
   取代链数 / 快照版本 / 投影面条目数），裁定实例一条不进 nodes（INV-1 同款）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402

MAP_REL = "config/governance_legislation_map.yaml"
SKELETON_REL = "docs/_working/map_build/fig16_legislation/00_skeleton.md"
RULING_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"

OUTPUT_PATH = _REPO_ROOT / MAP_REL

# 生成的确定时戳（禁壁钟；=RULING #486 effective_from 当日零点）
GENERATED_AT = "2026-10-05T00:00:00+08:00"

# ---------------------------------------------------------------------------
# 结构层：骨架 §1-§3 契约镜像（编号/语义与骨架逐条对应，禁二次创作）
# ---------------------------------------------------------------------------

STATES = [
    {
        "state_id": "D16-S1",
        "value": "draft",
        "name_zh": "草案 draft",
        "terminal": False,
        "note_zh": "已占号登记、尚未生效；审批通道不认（仅 active 放行）",
        "source_anchors": [
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
            "src/zephyr/gov_enforcement/commit_gates/approval_resolver.py",
        ],
    },
    {
        "state_id": "D16-S2",
        "value": "active",
        "name_zh": "生效中 active",
        "terminal": False,
        "note_zh": "主通道在册态；唯一能承载 approved_paths 授权与被门禁74认可引用的状态",
        "source_anchors": ["src/zephyr/gov_enforcement/commit_gates/approval_resolver.py"],
    },
    {
        "state_id": "D16-S3",
        "value": "superseded",
        "name_zh": "被取代 superseded",
        "terminal": True,
        "note_zh": "新裁定取代旧裁定；superseded_by 必填（#20-D 铁律9）",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "state_id": "D16-S4",
        "value": "deprecated",
        "name_zh": "已废弃 deprecated",
        "terminal": True,
        "note_zh": "四值枚举内预留废弃位；当前零实例（结构性预留，非自造）",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "state_id": "D16-S5",
        "value": "void",
        "name_zh": "撞号墓碑 void",
        "terminal": True,
        "note_zh": "枚举外观测旁支：撞号处置留痕 tombstone，非裁定（占号防复用）",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "state_id": "D16-S6",
        "value": "decided",
        "name_zh": "已决归档 decided",
        "terminal": True,
        "note_zh": "枚举外观测旁支：战役代裁/呈裁执行完毕归档，不再构成活授权",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
]

MACHINERY = [
    {
        "node_id": "D16-N1",
        "name_zh": "呈报口",
        "note_zh": "立项卡/总包令/呈裁件把立法意图送入链路；立项卡呈批制后 GO/NO-GO 权在 Owner（裁定#486 ②）",
        "source_anchors": [
            "docs/_working/map_build/22_fig15_card_lifecycle_charter.md",
            "docs/_working/map_census/00_panorama_map_census_v1.md",
        ],
    },
    {
        "node_id": "D16-N2",
        "name_zh": "取号器",
        "note_zh": "裁定#NNN 原子占号：--next 幂等查询/--claim O_EXCL 独占/--release 仅本会话；编号不回收",
        "source_anchors": ["scripts/governance/next_ruling_id.py"],
    },
    {
        "node_id": "D16-N3",
        "name_zh": "意图API",
        "note_zh": "register/update/retire 按条目声明；接口负面清单（禁整册写）；CAS 409 拒绝记事件；retire 强制 authority_ref",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "node_id": "D16-N4",
        "name_zh": "同commit原子门74",
        "note_zh": "新增 裁定#NNN 引用必须在册且册面同 commit；L1 编号空洞 warn；L2 原子性 hard block（priority=74）",
        "source_anchors": ["src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py"],
    },
    {
        "node_id": "D16-N5",
        "name_zh": "publish快照",
        "note_zh": "active 条目集发布为不可变快照；同 content_sha=noop 幂等；身份键置首防 jsonb 重排",
        "source_anchors": ["src/zephyr/governance/registry_ledger/baseline.py"],
    },
    {
        "node_id": "D16-N6",
        "name_zh": "render投影",
        "note_zh": "册 yaml=PG 投影（PG-wins 回滚盘面私改）；render 通道单写者；cutover=7f0beccac4",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "node_id": "D16-N7",
        "name_zh": "消费方索引",
        "note_zh": "审批通道（_ruling_channel：active+expires_at+approved_paths）、reference 类 gates、取号分母、对齐清单挂轴",
        "source_anchors": [
            "src/zephyr/gov_enforcement/commit_gates/approval_resolver.py",
            "scripts/governance/next_ruling_id.py",
        ],
    },
    {
        "node_id": "D16-N8",
        "name_zh": "取代链",
        "note_zh": "superseded_by 单向指针 + related_rulings 双向关联，议题-裁定互溯（#20-D 铁律9/10）",
        "source_anchors": [
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
            "scripts/governance/next_ruling_id.py",
        ],
    },
    {
        "node_id": "D16-N9",
        "name_zh": "复活禁令",
        "note_zh": "编号不回收、跳号永不复用；复活=新号+related_rulings 指回（跨实例边）；撞号=void 墓碑（裁定#485 ①制度化）",
        "source_anchors": [
            "scripts/governance/next_ruling_id.py",
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
        ],
    },
]

TRANSITIONS = [
    {
        "transition_id": "D16-T1",
        "from_state": [],
        "to_state": "draft",
        "name_zh": "∅→draft",
        "note_zh": "register(status=draft)，占号后草案先行；先例=裁定#1",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "transition_id": "D16-T2",
        "from_state": [],
        "to_state": "active",
        "name_zh": "∅→active",
        "note_zh": "register(status=active) 直批登记（主通道）；凭证=Owner 批文/呈裁批",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "transition_id": "D16-T3",
        "from_state": [],
        "to_state": "decided",
        "name_zh": "∅→decided",
        "note_zh": "register(status=decided) 随批即决（战役代裁形态）；先例=裁定#404/#407",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "transition_id": "D16-T4",
        "from_state": [],
        "to_state": "void",
        "name_zh": "∅→void",
        "note_zh": "register(status=void) 撞号墓碑随处置批登记；先例=裁定#408",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "transition_id": "D16-T5",
        "from_state": ["draft"],
        "to_state": "active",
        "name_zh": "draft→active",
        "note_zh": "update 状态翻转（草案过批生效）",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "transition_id": "D16-T6",
        "from_state": ["active"],
        "to_state": "superseded",
        "name_zh": "active→superseded",
        "note_zh": "update + superseded_by 必填（#20-D 铁律9）",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "transition_id": "D16-T7",
        "from_state": ["active"],
        "to_state": "deprecated",
        "name_zh": "active→deprecated",
        "note_zh": "update 废弃（枚举预留位，零实例）",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "transition_id": "D16-T8",
        "from_state": ["active"],
        "to_state": "decided",
        "name_zh": "active→decided",
        "note_zh": "update 执行完毕归档；先例=#409 族归档形态",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "transition_id": "D16-T9",
        "from_state": [],
        "to_state": "active",
        "name_zh": "∅→active（跨实例）",
        "cross_instance": True,
        "note_zh": "复活=新号 register + related_rulings 指回旧号；旧号状态不变（编号不回收的合法出路，图15 D15-M17 同构）",
        "source_anchors": ["scripts/governance/next_ruling_id.py"],
    },
]

FORBIDDEN_EDGES = [
    {
        "edge_id": "D16-X1",
        "rule_zh": "任何态→active 同号就地复活（改旧条目翻回 active=伪造授权）",
        "note_zh": "CONFLICT_DUPLICATE 409（同号异指纹）机械拒；OK_NOOP 仅同键同指纹",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "edge_id": "D16-X2",
        "rule_zh": "superseded→active 撤销取代（取代链单向不可逆）",
        "note_zh": "update 须 reason+审计，翻转为伪造",
        "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
    },
    {
        "edge_id": "D16-X3",
        "rule_zh": "未占号登记（grep-and-claim 占位复辟）",
        "note_zh": "取号器分母感知（--next 列在途占号）",
        "source_anchors": ["scripts/governance/next_ruling_id.py"],
    },
    {
        "edge_id": "D16-X4",
        "rule_zh": "未登记先引用（悬空 裁定#NNN）",
        "note_zh": "RULING-REFERENCE gate74 L2 hard block（#20-B/#20-G）",
        "source_anchors": ["src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py"],
    },
    {
        "edge_id": "D16-X5",
        "rule_zh": "整册写绕过意图API（write_whole_registry 型接口）",
        "note_zh": "接口负面清单（API 不存在该接口面）",
        "source_anchors": ["src/zephyr/governance/registry_ledger/api.py"],
    },
    {
        "edge_id": "D16-X6",
        "rule_zh": "册 yaml 手改偏离账本（绕开 render 单写者私改投影）",
        "note_zh": "PG-wins render 回滚=伪影",
        "source_anchors": ["src/zephyr/governance/registry_ledger/baseline.py"],
    },
    {
        "edge_id": "D16-X7",
        "rule_zh": "占号转让/复用/回收（跳号永不复用）",
        "note_zh": "O_EXCL 独占+释放≠可复用；裁定#485 ①跳号台账",
        "source_anchors": ["scripts/governance/next_ruling_id.py"],
    },
]

# ---------------------------------------------------------------------------
# 人工语义层（骨架 §0/§4/§6 契约；随每次生成重写）
# ---------------------------------------------------------------------------

SEMANTIC_LAYER = {
    "ssot_note_zh": (
        "真源方向：骨架 §1-§3（状态/机构/迁移/禁边语义契约）+ PG 账本 REG-RULING-001（实例唯一机械真源，"
        "7f0beccac4 cutover）→ 本图 YAML（派生件，禁手改后不回生成）。裁定实例=数据行非节点（INV-1 同款），"
        "实例计数只进 counts 段且全部账本现算。结构层=骨架契约镜像，禁二次创作。"
    ),
    "laws": [
        "编号唯一不回收：复活唯一口=新号+related_rulings 指回（#20-D 铁律2，D16-N9/X1/T9）",
        "登记必经意图API：接口负面清单禁整册写；CAS 409 拒绝必记事件（D16-N3/X5）",
        "引用必同 commit 原子：RULING-REFERENCE gate74 L2 hard block（#20-B/#20-G，D16-N4/X4）",
        "取代必有链：superseded_by 必填且单向不可逆（#20-D 铁律9，D16-N8/X2/T6）",
        "投影非真源：册 yaml=PG 投影，PG-wins；手改投影=伪影（D16-N6/X6）",
        "计数只进 counts：散文写死数字判红；实例对拍只对生成时点负责（结构面硬/实例面 CLI live 硬）",
    ],
    "boundary": [
        "不含裁定正文（内容真源=ruling_registry 条目本身；INV-1 型 40 字滑窗归校验器）",
        "不含图10 GOMAP 运行时面（治理运行地图管运行进程，本图管立法条目；词汇零交 w5_1 不并）",
        "不含门禁引擎内部判据（N4/N7 只登记门存在与优先级事实，判据改动走各自真源文件）",
        "不含 deep_adjudication 呈报侧六步入表闸语义（D16-N1 只存指针；呈报判据真源=deep_adjudication_method_policy.md）",
    ],
}


# ---------------------------------------------------------------------------
# 实例层：PG 账本现算（counts）
# ---------------------------------------------------------------------------


def read_ledger_counts() -> dict:
    """读 REG-RULING-001 账本现算 counts（只读 SELECT；PG 不可达抛 RuntimeError）。"""
    from collections import Counter

    from zephyr.governance.registry_ledger import api as ledger_api
    from zephyr.governance.registry_ledger.registry_ledger_ddl import SCHEMA_NAME

    try:
        conn = ledger_api._open_default_conn()
    except Exception as e:  # noqa: BLE001 — 账本不可达=环境异常，报错退出不静默
        raise RuntimeError(f"PG 账本不可达（counts 无法现算，禁静默产半张图）: {type(e).__name__}: {e}") from e
    try:
        with conn.cursor() as cur:
            t = ledger_api._t("registry_entry", SCHEMA_NAME)
            cur.execute(
                f"SELECT payload->>'status', count(*) FROM {t} "  # noqa: bare-sql  只读 SELECT 账本读面，表名为 registry_ledger 模块常量拼接，SQL 真源集中该模块本件无写面
                "WHERE registry_id=%s AND status='active' GROUP BY 1",
                ("REG-RULING-001",),
            )
            by_status = {status: int(n) for status, n in cur.fetchall()}
            cur.execute(
                f"SELECT count(*) FROM {t} WHERE registry_id=%s AND status='active'",  # noqa: bare-sql  只读 SELECT 账本读面，表名为 registry_ledger 模块常量拼接，SQL 真源集中该模块本件无写面
                ("REG-RULING-001",),
            )
            rows_active = int(cur.fetchone()[0])
            cur.execute(
                f"SELECT count(*) FROM {t} WHERE registry_id=%s AND status='retired'",  # noqa: bare-sql  只读 SELECT 账本读面，表名为 registry_ledger 模块常量拼接，SQL 真源集中该模块本件无写面
                ("REG-RULING-001",),
            )
            rows_retired = int(cur.fetchone()[0])
            ts = ledger_api._t("registry_snapshot", SCHEMA_NAME)
            cur.execute(
                f"SELECT coalesce(max(snapshot_version), 0) FROM {ts} WHERE registry_id=%s",  # noqa: bare-sql  只读 SELECT 账本读面，表名为 registry_ledger 模块常量拼接，SQL 真源集中该模块本件无写面
                ("REG-RULING-001",),
            )
            snapshot_version = int(cur.fetchone()[0])
    finally:
        conn.close()

    entries = yaml.safe_load((_REPO_ROOT / RULING_REGISTRY_REL).read_text(encoding="utf-8"))["entries"]
    chains = sum(1 for e in entries if e.get("superseded_by"))
    return {
        "entries_total": len(entries),
        "ledger_rows_active": rows_active,
        "ledger_rows_retired": rows_retired,
        "by_status": {k: by_status[k] for k in sorted(by_status)},
        "superseded_by_chains": chains,
        "snapshot_version": snapshot_version,
        "by_state_caliber_zh": "账本现算基准=registry_entry active 行 payload.status（retired 行已离册不计数）；"
        "投影面 entries_total 与 ledger_rows_active 允许一个 render 在途窗口的偏差（D16-N6）",
    }


def build_document(counts: dict) -> dict:
    """组装图文档（结构层常量+实例层现算；同账本态逐字节等=幂等）。"""
    doc = {
        "schema_version": "0.1",
        "map_id": "governance_legislation_map",
        "name_zh": "治理立法流图",
        "nickname": "立法流",
        "effective_from": "2026-10-05",
        "generator": "scripts/governance/d5_architecture/generators/generate_governance_legislation_map.py",
        "generated_at": GENERATED_AT,
        "gate_id": "GOVERNANCE-LEGISLATION-MAP",
        "admission_ruling": "裁定#486",
        "derived_from": [
            "docs/_working/map_build/fig16_legislation/00_skeleton.md",
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
            "docs/_working/map_census/00_panorama_map_census_v1.md",
            "src/zephyr/governance/registry_ledger/api.py",
        ],
    }
    doc.update(SEMANTIC_LAYER)
    doc["states"] = STATES
    doc["machinery"] = MACHINERY
    doc["transitions"] = TRANSITIONS
    doc["forbidden_edges"] = FORBIDDEN_EDGES
    doc["counts"] = counts
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="图16 治理立法流图生成器（机生·幂等）")
    parser.add_argument(
        "--out", default=str(OUTPUT_PATH), help="输出路径（默认 config/governance_legislation_map.yaml）"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，零写入")
    args = parser.parse_args(argv)

    counts = read_ledger_counts()
    doc = build_document(counts)
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=110)
    header = (
        f"# 治理立法流图（governance_legislation_map，图16）——由 {Path(__file__).name} 机生。\n"
        f"# 真源=骨架 §1-§3（状态/机构/迁移/禁边语义契约）+ PG 账本 REG-RULING-001（实例唯一机械真源）。\n"
        f"# 准入=裁定#486 ①（Owner 2026-10-05 双批）；本文件禁手改后不回生成（counts 一致性判红）。\n"
    )
    out = Path(args.out)
    print(
        f"states={len(STATES)} machinery={len(MACHINERY)} transitions={len(TRANSITIONS)} "
        f"forbidden={len(FORBIDDEN_EDGES)} counts.by_status={counts['by_status']}"
    )
    if args.dry_run:
        print("dry-run: 零写入")
        return 0
    if out.exists():
        old = out.read_text(encoding="utf-8")
        if old == header + text:
            print("幂等命中：输出与现盘逐字节等，零写入")
            return 0
    result = safe_write_text(out, header + text, repo_root=_REPO_ROOT)
    print(f"written: {out} ok={getattr(result, 'written', result)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
