# [BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.governance.generators.test_regen_clean_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generators.regen_clean_check
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红蓝自测（S7 簿 §4.5）：红=单字段手改必检出（专杀计数级弱校验盲区）+时间戳-only 差异必判 clean；蓝=净盘面必过；全部夹具走 tmp_path，禁写生产路径
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_REGEN_CLEAN_CHECK | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_regen_clean_check.py — regen-clean 生成闭环检查器 单元测试（B4/st-fms-chief-20260927）

覆盖（S7 簿 §4.2/§4.3 规格逐条）：
- 归一化：时间戳-only 差异判 clean（volatile_lines）；键序/行序漂移判 clean（yaml_canonical）；
  CRLF/BOM 判 clean（MD 行比对）；单字段手改判 drift（专杀 generate_gate_registry --check
  弱校验盲区——计数同但字段被改必报）
- 触发判定：staged ∩ (input∪output∪生成器自身)
- 执行序：红级/enabled:false → skip 留痕且绝不执行；生成器崩/超时 → error（fail-open exit 2）
- 棘轮基线：baseline 外 drift → exit 1 硬拦；baseline 内 → warn exit 0
- structural mode：index 表行 ∩ 盘面 双向覆盖（missing/ghost）
- 红线：门模式零盘面副作用（正本字节不变）；--auto-fix 才回写；--update-baseline 走 CAS
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.governance.generators import regen_clean_check as rcc  # noqa: E402

# 夹具生成器：读 --src 真源渲染到 --output；--mode 注入故障
GEN_SCRIPT = """\
import sys, time
from pathlib import Path
args = sys.argv[1:]
out = Path(args[args.index("--output") + 1])
src = Path(args[args.index("--src") + 1])
mode = args[args.index("--mode") + 1] if "--mode" in args else "ok"
if mode == "crash":
    raise RuntimeError("boom")
if mode == "hang":
    time.sleep(60)
out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
"""


def _abs(p: Path) -> str:
    return p.as_posix()


def _write_registry(tmp_path: Path, pairs: list[dict]) -> Path:
    reg = tmp_path / "generator_registry.yaml"
    reg.write_text(yaml.dump({"generators": pairs}, allow_unicode=True), encoding="utf-8")
    return reg


@pytest.fixture()
def gen_script(tmp_path: Path) -> Path:
    p = tmp_path / "fixture_generator.py"
    p.write_text(GEN_SCRIPT, encoding="utf-8")
    return p


@pytest.fixture()
def sandbox(tmp_path: Path, monkeypatch):
    """把检查器的 REPO_ROOT / iso 区 / jsonl 区全部重定向到 tmp_path。"""
    monkeypatch.setattr(rcc, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(rcc, "ISO_TMP_ROOT", tmp_path / ".runtime" / "tmp" / "regen_clean")
    monkeypatch.setattr(rcc, "DEFAULT_JSONL_DIR", tmp_path / ".runtime" / "gate_audit" / "regen_clean")
    return tmp_path


def _make_pair(
    tmp_path: Path,
    gen_script: Path,
    canonical_body: str,
    *,
    tier: str = "green",
    enabled: bool = True,
    name: str = "fixture_pair",
    **extra,
) -> tuple[Path, Path]:
    src = tmp_path / f"{name}_truth.yaml"
    src.write_text(canonical_body, encoding="utf-8")
    canonical = tmp_path / f"{name}_canonical.yaml"
    canonical.write_text(canonical_body, encoding="utf-8")
    regen = {
        "tier": tier,
        "invoke": f'"{_abs(gen_script)}" --output {{iso_out}} --src "{_abs(src)}"',
        "canonical": _abs(canonical),
        "normalize": ["volatile_lines", "yaml_canonical"],
        "timeout_seconds": 10,
        "enabled": enabled,
    }
    regen.update(extra)
    registry = _write_registry(
        tmp_path,
        [
            {
                "name": name,
                "module_path": _abs(gen_script),
                "input_sources": [_abs(src)],
                "output_globs": [_abs(canonical)],
                "regen": regen,
            }
        ],
    )
    return registry, canonical


# ════════════════════════════════════════════════════════════════════════
# 归一化（§4.3）
# ════════════════════════════════════════════════════════════════════════


class TestNormalization:
    def test_timestamp_only_diff_is_clean(self, sandbox, gen_script):
        """时间戳-only 差异必须判 clean（volatile_lines + yaml_canonical）。"""
        body = "generated_at: 2026-01-01T00:00:00Z\nvalue: a\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        # 生成器产出与真源一致；正本仅 generated_at 不同 → 应判净
        canonical.write_text("generated_at: 2020-01-01T00:00:00Z\nvalue: a\n", encoding="utf-8")
        rc = rcc.main(
            ["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no_baseline.yaml")]
        )
        assert rc == rcc.EXIT_CLEAN

    def test_key_order_diff_is_clean(self, sandbox, gen_script):
        """键序漂移在 yaml_canonical 下必须判净（§4.3.2 比行 diff 严）。"""
        reg, canonical = _make_pair(sandbox, gen_script, "a: 1\nb: 2\n")
        canonical.write_text("b: 2\na: 1\n", encoding="utf-8")
        rc = rcc.main(
            ["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no_baseline.yaml")]
        )
        assert rc == rcc.EXIT_CLEAN

    def test_single_field_change_is_drift(self, sandbox, gen_script):
        """红测：total 计数不变但单字段被手改 → 必报 drift（专杀 2.1.2 弱校验盲区）。"""
        body = "total: 2\nitems:\n  - name: x\n    enabled: true\n  - name: y\n    enabled: true\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        # 手改单字段，条目数不变——计数级 --check 探不到，全量 diff 必须探到
        canonical.write_text(body.replace("name: y", "name: y-hand-edited"), encoding="utf-8")
        rc = rcc.main(
            ["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no_baseline.yaml")]
        )
        assert rc == rcc.EXIT_DRIFT

    def test_md_crlf_bom_is_clean(self, sandbox):
        """MD 行比对：CRLF→LF、BOM 剥离后逐行比（§4.3.3）。"""
        canonical = sandbox / "doc.md"
        canonical.write_text("# 标题\n正文\n", encoding="utf-8")
        iso = sandbox / "iso.md"
        iso.write_bytes(b"\xef\xbb\xbf# \xe6\xa0\x87\xe9\xa2\x98\r\n\xe6\xad\xa3\xe6\x96\x87\r\n")
        pair = rcc.RegenPair(name="p", canonical=_abs(canonical), normalize=["volatile_lines"])
        a, _ = rcc.normalize_text(rcc.read_text_normalized(canonical), pair)
        b, _ = rcc.normalize_text(rcc.read_text_normalized(iso), pair)
        assert a == b
        assert rcc.unified_diff(a, b, pair) == []


# ════════════════════════════════════════════════════════════════════════
# 触发判定与执行序（§4.2 执行序①②）
# ════════════════════════════════════════════════════════════════════════


class TestTriggerAndSkip:
    def test_staged_filter_selects_matching_pair(self, sandbox, gen_script):
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n", name="pair_hit")
        pairs = rcc.load_pairs(reg)
        assert rcc.pair_triggered(pairs["pair_hit"], [str(sandbox / "pair_hit_truth.yaml")], sandbox)
        assert not rcc.pair_triggered(pairs["pair_hit"], ["docs/unrelated.md"], sandbox)

    def test_generator_self_path_triggers(self, sandbox, gen_script):
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n")
        pairs = rcc.load_pairs(reg)
        # 生成器自身路径在触发面内（module_path → 脚本路径）
        assert rcc.pair_triggered(pairs["fixture_pair"], [_abs(gen_script)], sandbox)

    def test_red_pair_skipped_and_never_executed(self, sandbox, gen_script):
        """红级 → skip 留痕且绝不执行（金丝雀不被写）。"""
        canary = sandbox / "canary.txt"
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n", tier="red", skip_reason="pg-depgraph")
        rc = rcc.main(["--registry", str(reg), "--pairs", "*", "--baseline", str(sandbox / "no_baseline.yaml")])
        assert rc == rcc.EXIT_CLEAN  # 全跳过=exit 0
        assert not canary.exists()
        jsonl = next((sandbox / ".runtime" / "gate_audit" / "regen_clean").glob("*.jsonl"))
        rec = json.loads(jsonl.read_text(encoding="utf-8").strip())
        assert rec["verdict"] == "skip" and rec["detail"] == "pg-depgraph"

    def test_disabled_pair_skipped(self, sandbox, gen_script):
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n", enabled=False)
        rc = rcc.main(["--registry", str(reg), "--pairs", "*", "--baseline", str(sandbox / "no_baseline.yaml")])
        assert rc == rcc.EXIT_CLEAN
        jsonl = next((sandbox / ".runtime" / "gate_audit" / "regen_clean").glob("*.jsonl"))
        assert json.loads(jsonl.read_text(encoding="utf-8").strip())["verdict"] == "skip"

    def test_unknown_pair_is_infra_error(self, sandbox, gen_script):
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n")
        assert rcc.main(["--registry", str(reg), "--pairs", "no_such_pair"]) == rcc.EXIT_INFRA

    def test_missing_registry_is_infra_error(self, sandbox):
        assert rcc.main(["--registry", str(sandbox / "absent.yaml")]) == rcc.EXIT_INFRA


# ════════════════════════════════════════════════════════════════════════
# 故障语义（ERROR_CONTRACT：崩/超时 → error + exit 2 fail-open）
# ════════════════════════════════════════════════════════════════════════


class TestInfraFailures:
    def test_generator_crash_is_error_exit2(self, sandbox, gen_script):
        src = sandbox / "truth.yaml"
        src.write_text("v: 1\n", encoding="utf-8")
        canonical = sandbox / "canonical.yaml"
        canonical.write_text("v: 1\n", encoding="utf-8")
        reg = _write_registry(
            sandbox,
            [
                {
                    "name": "boom",
                    "module_path": "x",
                    "input_sources": [],
                    "output_globs": [_abs(canonical)],
                    "regen": {
                        "tier": "green",
                        "invoke": f'"{_abs(gen_script)}" --output {{iso_out}} --src "{_abs(src)}" --mode crash',
                        "canonical": _abs(canonical),
                        "normalize": ["yaml_canonical"],
                        "timeout_seconds": 10,
                        "enabled": True,
                    },
                }
            ],
        )
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "boom", "--baseline", str(sandbox / "no.yaml")])
            == rcc.EXIT_INFRA
        )

    def test_generator_timeout_is_error(self, sandbox, gen_script):
        src = sandbox / "truth2.yaml"
        src.write_text("v: 1\n", encoding="utf-8")
        canonical = sandbox / "canonical2.yaml"
        canonical.write_text("v: 1\n", encoding="utf-8")
        reg = _write_registry(
            sandbox,
            [
                {
                    "name": "hang",
                    "module_path": "x",
                    "input_sources": [],
                    "output_globs": [_abs(canonical)],
                    "regen": {
                        "tier": "green",
                        "invoke": f'"{_abs(gen_script)}" --output {{iso_out}} --src "{_abs(src)}" --mode hang',
                        "canonical": _abs(canonical),
                        "normalize": ["yaml_canonical"],
                        "timeout_seconds": 10,
                        "enabled": True,
                    },
                }
            ],
        )
        assert (
            rcc.main(
                [
                    "--registry",
                    str(reg),
                    "--pairs",
                    "hang",
                    "--budget-ms",
                    "1500",
                    "--baseline",
                    str(sandbox / "no.yaml"),
                ]
            )
            == rcc.EXIT_INFRA
        )


# ════════════════════════════════════════════════════════════════════════
# 棘轮基线（§4.3.5：baseline 外硬拦、baseline 内 warn）
# ════════════════════════════════════════════════════════════════════════


class TestRatchetBaseline:
    def _drift_setup(self, sandbox, gen_script):
        body = "v: 1\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        canonical.write_text("v: 2\n", encoding="utf-8")  # 手改 → 与生成器产出漂移
        return reg, canonical

    def test_drift_outside_baseline_hard_fails(self, sandbox, gen_script):
        reg, _ = self._drift_setup(sandbox, gen_script)
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no.yaml")])
            == rcc.EXIT_DRIFT
        )

    def test_drift_inside_baseline_warns_exit0(self, sandbox, gen_script):
        reg, _ = self._drift_setup(sandbox, gen_script)
        baseline = sandbox / "baseline.yaml"
        # 先跑一次拿指纹 → --update-baseline 入册 → 再跑必须 exit 0（baseline 内 warn）
        rcc.main(["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(baseline), "--update-baseline"])
        data = yaml.safe_load(baseline.read_text(encoding="utf-8"))
        assert data["baseline"]["fixture_pair"], "指纹必须入册"
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(baseline)]) == rcc.EXIT_CLEAN
        )

    def test_fingerprint_is_line_number_stable(self):
        """无关区域行号平移不换指纹（棘轮指纹 = 变更行集合，与 diff 头/行号无关）。"""
        d1 = rcc.drift_fingerprint(["---", "+++", "@@ -1,3 +1,3 @@", "-a", "+b", " ctx"])
        d2 = rcc.drift_fingerprint(["---", "+++", "@@ -9,3 +9,3 @@", "-a", "+b", " ctx"])
        assert d1 == d2 and d1 != ""
        assert rcc.drift_fingerprint([]) == ""

    def test_load_baseline_tolerates_missing_file(self, sandbox):
        assert rcc.load_baseline(sandbox / "absent.yaml") == {}


# ════════════════════════════════════════════════════════════════════════
# 结构性对账（§4.3.4 mode: structural）
# ════════════════════════════════════════════════════════════════════════


class TestStructuralMode:
    def _setup_scope(self, sandbox: Path, disk: list[str]) -> Path:
        scope = sandbox / "docs"
        scope.mkdir(exist_ok=True)
        for f in disk:
            (scope / f).write_text("x: 1\n", encoding="utf-8")
        return scope

    def _index(self, sandbox: Path, rows: list[str]) -> Path:
        index = sandbox / "idx.md"
        table = "\n".join(f"| [{r}]({r}) | YAML | |" for r in rows)
        index.write_text(
            '---\ncreated: "2026-01-01"\nupdated: "2026-01-01"\n---\n\n# idx\n\n## 目录内容\n\n'
            "| 文件/目录 | 类型 | 说明 |\n|-----------|------|------|\n"
            + table
            + "\n\n## 导航\n\n- [上级目录](../index.md)\n",
            encoding="utf-8",
        )
        return index

    def _pair(self, sandbox: Path, index: Path) -> rcc.RegenPair:
        return rcc.RegenPair(
            name="idx_pair",
            canonical=_abs(index),
            mode="structural",
            structural={
                "index_file": _abs(index),
                "scope_dir": _abs(sandbox / "docs"),
                "include": ["*.yaml"],
                "ref_section": "## 目录内容",
                "ref_pattern": r"\[[^\]]*\]\(([^)]+)\)",
                "ref_strip": ["/index.md"],
            },
        )

    def test_bidirectional_coverage_clean(self, sandbox):
        self._setup_scope(sandbox, ["a.yaml", "b.yaml"])
        pair = self._pair(sandbox, self._index(sandbox, ["a.yaml", "b.yaml"]))
        violations, _ = rcc.run_structural(pair)
        assert violations == []

    def test_missing_from_index_detected(self, sandbox):
        """盘面有条目而索引缺行 → drift（docs/index.md 漏 library/ 的同类形态）。"""
        self._setup_scope(sandbox, ["a.yaml", "hidden.yaml"])
        pair = self._pair(sandbox, self._index(sandbox, ["a.yaml"]))
        violations, _ = rcc.run_structural(pair)
        assert violations == ["missing-from-index: " + _abs(sandbox / "docs" / "hidden.yaml")]

    def test_ghost_ref_detected(self, sandbox):
        """索引表行引用盘面不存在条目 → 幽灵引用 drift。"""
        self._setup_scope(sandbox, ["a.yaml"])
        pair = self._pair(sandbox, self._index(sandbox, ["a.yaml", "ghost.yaml"]))
        violations, _ = rcc.run_structural(pair)
        assert violations == ["ghost-ref: " + _abs(sandbox / "docs" / "ghost.yaml")]

    def test_structural_drift_exits_1(self, sandbox):
        self._setup_scope(sandbox, ["a.yaml", "orphan.yaml"])
        index = self._index(sandbox, ["a.yaml"])
        reg = _write_registry(
            sandbox,
            [
                {
                    "name": "idx_pair",
                    "module_path": "x",
                    "input_sources": [],
                    "output_globs": [_abs(index)],
                    "regen": {
                        "mode": "structural",
                        "tier": "green",
                        "enabled": True,
                        "canonical": _abs(index),
                        "structural": {
                            "index_file": _abs(index),
                            "scope_dir": _abs(sandbox / "docs"),
                            "include": ["*.yaml"],
                            "ref_section": "## 目录内容",
                            "ref_pattern": r"\[[^\]]*\]\(([^)]+)\)",
                        },
                    },
                }
            ],
        )
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "idx_pair", "--baseline", str(sandbox / "no.yaml")])
            == rcc.EXIT_DRIFT
        )

    def test_volatile_frontmatter_not_needed_for_structural(self, sandbox):
        """structural 不重生成正本——只读 index.md 与盘面对账（§4.3.4 语义）。"""
        self._setup_scope(sandbox, ["a.yaml"])
        index = self._index(sandbox, ["a.yaml"])
        before = index.read_bytes()
        rcc.run_structural(self._pair(sandbox, index))
        assert index.read_bytes() == before


# ════════════════════════════════════════════════════════════════════════
# 红线：门模式零盘面副作用；--auto-fix / seed_iso 语义
# ════════════════════════════════════════════════════════════════════════


class TestPurityAndAutoFix:
    def test_gate_mode_never_touches_canonical(self, sandbox, gen_script):
        """检出 drift 的同时正本字节必须原样（绝不改盘面/工作树）。"""
        body = "v: 1\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        canonical.write_text("v: hand-edited\n", encoding="utf-8")
        before = canonical.read_bytes()
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no.yaml")])
            == rcc.EXIT_DRIFT
        )
        assert canonical.read_bytes() == before

    def test_auto_fix_copies_iso_to_canonical(self, sandbox, gen_script):
        body = "v: 1\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        canonical.write_text("v: stale\n", encoding="utf-8")
        rc = rcc.main(
            ["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no.yaml"), "--auto-fix"]
        )
        assert rc == rcc.EXIT_DRIFT
        assert canonical.read_text(encoding="utf-8") == body  # 隔离产出已拷回

    def test_seed_iso_preseeds_merge_style_generators(self, sandbox):
        """seed_iso: true → 先把正本拷到 iso 位再跑（保育语义对 rule_catalog 类合并生成器）。"""
        gen = sandbox / "merge_gen.py"
        gen.write_text(
            "import sys\nfrom pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "out = Path(args[args.index('--output') + 1])\n"
            "out.write_text('seeded' if out.exists() else 'empty', encoding='utf-8')\n",
            encoding="utf-8",
        )
        canonical = sandbox / "merge_canonical.yaml"
        canonical.write_text("seeded", encoding="utf-8")
        reg = _write_registry(
            sandbox,
            [
                {
                    "name": "merge_pair",
                    "module_path": "x",
                    "input_sources": [],
                    "output_globs": [_abs(canonical)],
                    "regen": {
                        "tier": "green",
                        "invoke": f'"{_abs(gen)}" --output {{iso_out}}',
                        "canonical": _abs(canonical),
                        "seed_iso": True,
                        "normalize": ["volatile_lines"],
                        "timeout_seconds": 10,
                        "enabled": True,
                    },
                }
            ],
        )
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "merge_pair", "--baseline", str(sandbox / "no.yaml")])
            == rcc.EXIT_CLEAN
        )


# ════════════════════════════════════════════════════════════════════════
# CLI 契约
# ════════════════════════════════════════════════════════════════════════


class TestCli:
    def test_help_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as ei:
            rcc.main(["--help"])
        assert ei.value.code == 0
        out = capsys.readouterr().out
        for flag in ("--check", "--staged", "--pairs", "--baseline", "--jsonl", "--budget-ms", "--auto-fix"):
            assert flag in out

    def test_clean_run_exit0_and_jsonl_records(self, sandbox, gen_script):
        reg, _ = _make_pair(sandbox, gen_script, "v: 1\n")
        assert (
            rcc.main(["--registry", str(reg), "--pairs", "*", "--baseline", str(sandbox / "no.yaml")]) == rcc.EXIT_CLEAN
        )
        jsonl = next((sandbox / ".runtime" / "gate_audit" / "regen_clean").glob("*.jsonl"))
        rec = json.loads(jsonl.read_text(encoding="utf-8").strip())
        for key in ("run_id", "pair", "tier", "verdict", "diff_hash", "diff_excerpt", "elapsed_ms"):
            assert key in rec
        assert rec["verdict"] == "clean"

    def test_diff_excerpt_capped_at_20(self, sandbox, gen_script):
        """diff_excerpt ≤ 20 行（§4.2 输出契约）。"""
        body = "\n".join(f"k{i}: {i}" for i in range(50)) + "\n"
        reg, canonical = _make_pair(sandbox, gen_script, body)
        canonical.write_text("\n".join(f"k{i}: {i}-changed" for i in range(50)) + "\n", encoding="utf-8")
        rcc.main(["--registry", str(reg), "--pairs", "fixture_pair", "--baseline", str(sandbox / "no.yaml")])
        jsonl = next((sandbox / ".runtime" / "gate_audit" / "regen_clean").glob("*.jsonl"))
        rec = json.loads(jsonl.read_text(encoding="utf-8").strip())
        assert len(rec["diff_excerpt"]) <= 20


# ════════════════════════════════════════════════════════════════════════
# 集成：generate_manifest.py --output 旗标（S7 簿缺口②消解验证）
# ════════════════════════════════════════════════════════════════════════


class TestGenerateManifestOutputFlag:
    def _run(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(_PROJECT_ROOT / "scripts" / "generate_manifest.py"), *extra],
            cwd=str(_PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

    def test_output_flag_writes_isolated_copy(self, tmp_path):
        out = tmp_path / "iso_manifest.yaml"
        proc = self._run("--output", str(out))
        assert proc.returncode == 0, proc.stderr
        assert out.exists()
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert data["total_scripts"] > 0

    def test_no_arg_default_contract(self):
        """既有 subprocess 消费方（reconciliation_registry/audit_registration）无参调用契约：
        缺省输出位=登记真源 scripts/script-manifest.yaml。真机跑无参会写生产路径正本
        （宪法 9.6 测试禁写生产路径），故此处只验缺省值契约，不真跑。"""
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib.util;"
                "spec = importlib.util.spec_from_file_location('gm', r'"
                + str(_PROJECT_ROOT / "scripts" / "generate_manifest.py")
                + "');"
                "gm = importlib.util.module_from_spec(spec); spec.loader.exec_module(gm);"
                "print(gm.OUTPUT_PATH)",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.strip() == "scripts/script-manifest.yaml"

    def test_idempotent_skip(self, tmp_path):
        out = tmp_path / "iso2.yaml"
        assert self._run("--output", str(out)).returncode == 0
        proc = self._run("--output", str(out))
        assert proc.returncode == 0
        assert "unchanged, skipped" in proc.stdout


class TestPairTimeoutAuthority:
    """--budget-ms 只兜底未声明对；登记册声明值必须赢（治 09-27 首轮实测 3 对恒 timeout）。"""

    def test_declared_timeout_beats_global_budget(self) -> None:
        pair = rcc.RegenPair(name="rule_catalog_registry", timeout_seconds=60)
        assert rcc._pair_seconds(pair, 8000) == 60.0

    def test_undeclared_pair_falls_back_to_budget(self) -> None:
        pair = rcc.RegenPair(name="p", timeout_seconds=None)
        assert rcc._pair_seconds(pair, 8000) == 8.0

    def test_zero_declared_means_undeclared(self) -> None:
        """registry 里 docs_index_structural 写 timeout_seconds: 0=不用声明值。"""
        pair = rcc.RegenPair(name="docs_index_structural", timeout_seconds=0)
        assert rcc._pair_seconds(pair, 12000) == 12.0

    def test_declared_capped_by_hard_ceiling(self) -> None:
        """声明写错（如 99999）也不得让一次检查挂死。"""
        pair = rcc.RegenPair(name="p", timeout_seconds=99999)
        assert rcc._pair_seconds(pair, 8000) == rcc._MAX_PAIR_SECONDS

    def test_registry_pairs_actually_get_their_seconds(self) -> None:
        """活体口径：真册里声明 60s 的对，压到 8s 预算后仍须是 60s（旧实现此处即红）。"""
        reg = yaml.safe_load(rcc.DEFAULT_REGISTRY.read_text(encoding="utf-8"))
        declared = [
            (g.get("name"), (g.get("regen") or {}).get("timeout_seconds"))
            for g in (reg.get("generators") or [])
            if (g.get("regen") or {}).get("timeout_seconds")
        ]
        assert declared, "登记册里无任何 timeout_seconds 声明，本尺失去判别对象"
        for name, secs in declared:
            got = rcc._pair_seconds(rcc.RegenPair(name=str(name), timeout_seconds=float(secs)), 8000)
            assert got == min(float(secs), rcc._MAX_PAIR_SECONDS), (name, secs, got)
