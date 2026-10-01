# [A_test] module_id: MOD-TEST_no_stale_agents_numbered_refs_in_scripts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.blueprint.test_no_stale_agents_numbered_refs_in_scripts
# [INVARIANTS] scripts/ 与 src/ 全部受版本管理的源文件不得含 AGENTS.md §编号引用（稳定锚=规则名 RULE-XXX/真源路径）；扫描覆盖非空；生成产物不参与扫描但须自证为生成头
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 零写入零网络零数据库——纯只读源码扫描；git 不可用时 fail-loud（不静默放行）
# [TESTS] python -m pytest tests/blueprint/test_no_stale_agents_numbered_refs_in_scripts.py -q
# [TTL] permanent
"""失效 AGENTS.md §编号引用防回潮全域钉（2026-09-16，lane st-anchor-fix-20260916）。

病根：L0 宪法 2026-09-12 替换 1639 行 v1 后，AGENTS.md 的 §编号体系整体失效
（现仅存 0~9 号散文章节 + 规则名 RULE-XXX）。生成器/闸门源码里写死的
"AGENTS.md §6.1" 一类引用会随模板/描述回填继续扩散，人/AI 按引用跳转必撞死链。

既有两道钉（test_normalize_blueprint_autogen_anchors / test_sync_blueprint_code_index_template）
只覆盖 syncer/全景/模板三处源头；本钉把口径扩到 scripts/ 与 src/ 的全部受版本管理源文件，
与既有钉共用同一正则（不导入它们，避免测试间耦合）。

排除口径（写死在常量、可审计）：
  1. `scripts/_archive/` —— 归档区（历史冻结，不参与治理）。
  2. 自动生成产物 —— 文件头自带"自动生成/DO NOT EDIT/generated_by"声明者。
     这类文件由其生成器单向派生（如 scripts/governance/script_manifest.yaml ←
     scripts/governance/generators/generate_script_manifest.py、
     scripts/script-manifest.yaml ← scripts/generate_manifest.py），源头被本钉钉死后
     重跑生成器即自然收敛；手改生成产物反而会被下次重建覆盖（违 RULE-SSOT）。
本测试零写入、零网络、零数据库。
"""

from __future__ import annotations

import re
import subprocess

import pytest

from zephyr.shared.io.paths import REPO_ROOT

# 失效引用形态钉：AGENTS.md 后紧跟 §编号（L0 宪法起禁写死 §编号，稳定锚=规则名 RULE-XXX）
# —— 与 tests/blueprint/test_normalize_blueprint_autogen_anchors.py 同口径，此处独立声明不跨测试导入
STALE_AGENTS_NUMBERED_REF = re.compile(r"AGENTS\.md\s*§\s*\d")

SCAN_ROOTS = ("scripts", "src")
EXCLUDED_PREFIXES = ("scripts/_archive/",)

# 自动生成产物签名（只认文件头前三行的显式整文件生成声明，杜绝把普通源文件误判为产物）
GENERATED_HEADER_LINES = 3
GENERATED_MARKERS = re.compile(
    r"^\s*#*\s*(auto-?generated|自动生成)|generated_by\s*:|BEGIN\s+CODGEN"
    r"|do\s*not\s*edit\s*manually|人工编辑无效",
    re.IGNORECASE | re.MULTILINE,
)

# 扫描覆盖下限（防"扫描器空转也算通过"的假绿：scripts+src 受版本管理文件远超此数）
MIN_SCANNED_FILES = 500


def _tracked_files() -> list[str]:
    """返回 scripts/ 与 src/ 下全部受版本管理的相对路径（git ls-files，零网络）。"""
    proc = subprocess.run(
        ["git", "ls-files", "-z", *SCAN_ROOTS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(f"git ls-files 失败（本钉 fail-loud，不放行）: {proc.stderr.strip()}")
    return sorted(p for p in proc.stdout.split("\0") if p)


def _is_generated_artifact(text: str) -> bool:
    """判定是否为「文件头自证」的自动生成产物（只看前若干行，避免正文偶然命中）。"""
    head = "\n".join(text.splitlines()[:GENERATED_HEADER_LINES])
    return bool(GENERATED_MARKERS.search(head))


def _scan_targets() -> tuple[list[str], list[str]]:
    """把受版本管理文件分为「参与扫描」与「按头签名跳过」两类。"""
    scanned: list[str] = []
    skipped: list[str] = []
    for rel in _tracked_files():
        if rel.startswith(EXCLUDED_PREFIXES):
            continue
        path = REPO_ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            # 非文本/二进制（图标、字体、视频等）不参与文本引用扫描
            continue
        (skipped if _is_generated_artifact(text) else scanned).append(rel)
    return scanned, skipped


@pytest.fixture(scope="module")
def scan_result() -> tuple[list[str], list[str], list[str]]:
    """一次扫描，全模块复用（纯读，不写任何路径）。"""
    scanned, skipped = _scan_targets()
    findings: list[str] = []
    for rel in scanned:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if STALE_AGENTS_NUMBERED_REF.search(line):
                findings.append(f"{rel}:{lineno}: {line.strip()[:110]}")
    return scanned, skipped, findings


class TestScanCoverageSanity:
    """钉扎①：扫描真的覆盖到 scripts/ 与 src/ 的源文件（防空转假绿）。"""

    def test_scanned_file_set_is_non_trivial(self, scan_result):
        scanned, skipped, _ = scan_result
        assert len(scanned) >= MIN_SCANNED_FILES, f"扫描面异常收窄（仅 {len(scanned)} 个文件）"

    def test_both_scan_roots_present(self, scan_result):
        scanned, _, _ = scan_result
        roots = {rel.split("/", 1)[0] for rel in scanned}
        assert {"scripts", "src"} <= roots, f"扫描根缺失: {roots}"

    def test_archive_prefix_never_scanned(self, scan_result):
        scanned, _, _ = scan_result
        assert not [rel for rel in scanned if rel.startswith(EXCLUDED_PREFIXES)]

    def test_skipped_files_self_declare_as_generated(self, scan_result):
        """排除口径可审计：每个被跳过的文件必须真的在文件头自证为自动生成产物。"""
        _, skipped, _ = scan_result
        for rel in skipped:
            head = "\n".join((REPO_ROOT / rel).read_text(encoding="utf-8").splitlines()[:GENERATED_HEADER_LINES])
            assert GENERATED_MARKERS.search(head), f"非生成产物被错误排除: {rel}"


class TestNoStaleAgentsNumberedRefs:
    """钉扎②：scripts/ 与 src/ 源文件零失效 AGENTS.md §编号引用。"""

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked 存量债两处（generate_front_door.py:137/no_delete_manifest.py:10 仍用 AGENTS.md §编号引用）归其所有者清偿中，本尺对全仓状态断言，转XPASS=债清偿落地须改判",
    )
    def test_scripts_and_src_have_no_stale_numbered_refs(self, scan_result):
        _, _, findings = scan_result
        assert not findings, "失效 AGENTS.md §编号引用（应改为规则名 RULE-XXX / 真源路径锚点）:\n" + "\n".join(findings)


class TestDetectorShape:
    """钉扎③：检测器本身语义正确——既抓得住病灶，也不误伤稳定锚与历史写法。"""

    @pytest.mark.parametrize(
        "stale",
        [
            "AGENTS.md §6.1 蓝图-代码同步强制约定",
            "对标 AGENTS.md§6.14 漂移免疫",
            "真源：AGENTS.md  §11.1.1 时间戳约定",
            "见 AGENTS.md §7「代码规范」",
        ],
    )
    def test_detects_stale_numbered_refs(self, stale):
        assert STALE_AGENTS_NUMBERED_REF.search(stale), f"病灶未命中: {stale}"

    @pytest.mark.parametrize(
        "clean",
        [
            "稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA",
            "真源 docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml（TRAE-080）",
            "旧宪法 §6.5（全文归档 agent_constitution_legacy_v1.md）",
            "AGENTS.md 人机门位 + risk_tier_registry.yaml",
            "ITIL SACM §4.5（外部框架对标）",
            "蓝图 §2 路径索引",
        ],
    )
    def test_accepts_stable_anchors_and_history_forms(self, clean):
        assert not STALE_AGENTS_NUMBERED_REF.search(clean), f"合法锚点被误判: {clean}"

    def test_three_part_a_files_reanchored_to_their_own_sources(self):
        """(A) 三处同源不同义病灶已各自回到自己真源——防回退成同一句话敷衍。"""
        expectations = {
            "scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_code_sync.py": (
                "TRAE-014",
                "RULE-DEPGRAPH",
            ),
            "scripts/governance/d1_structure/validate_config_integrity.py": (
                "risk_tier_registry.yaml",
                "ai_autonomy_authority_registry.yaml",
            ),
            "scripts/governance/d3_metadata/generate_derived_files.py": (
                "trae_062_ssot_classification.yaml",
                "GATE-VOCAB",
            ),
        }
        for rel, anchors in expectations.items():
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            for anchor in anchors:
                assert anchor in text, f"{rel} 丢失真源锚点 {anchor}"

    def test_all_cited_anchor_paths_exist(self):
        """新写下的真源指针必须可解析——否则只是把死链换了个写法。"""
        anchor_paths = [
            "docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml",
            "docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml",
            "docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml",
            "docs/01_policies_and_standards/rules/trae_004_parallel_atomic_transaction.yaml",
            "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
            "docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml",
            "docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml",
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
            "docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md",
            "docs/01_policies_and_standards/sop/governance_sop/agent_constitution_legacy_v1.md",
            "scripts/governance/quality_standard.md",
        ]
        missing = [p for p in anchor_paths if not (REPO_ROOT / p).exists()]
        assert not missing, f"锚点路径已失效: {missing}"
