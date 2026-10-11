# [BLUEPRINT] MOD-GOV-CSHARD-001 | docs/_working/t12_import_sharding/collection_shard_manifest.yaml | §manifest
# [MODULE] scripts.governance.generators.generate_collection_shard_manifest
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(argparse/json/os/re/sys/time/pathlib)；yaml；
#   无 zephyr 运行时耦合（纯子进程调 pytest + 解析文本，import 面零扩大）
# [CONSUMERS] 夜班错峰采集窗口（人工/AI 调 --shard 每目录一片自成一窗）；
#   机生册 docs/_working/t12_import_sharding/collection_shard_manifest.yaml 唯一写者；
#   反向钉桩 tests/gov/governance/generators/test_collection_shard_manifest_redpin.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只诊断不赦免——本工具【绝不跳过/降格任何 collection error】，真断链永远报红；
#   归因 fail-toward-red：缺省判 real_broken_link，仅当缺失模块属已知可选第三方（torch/cudf 等
#   非仓内命名空间）才标 environmental，二者均保留在 error 面（environmental 只是标签非 skip）；
#   仓内命名空间(zephyr/scripts/data/governance/tools/config)缺失一律 real_broken_link（防把断链
#   判成环境跳过凑绿=在册假绿主形态，唯一授权源=本班任务书）；机生册派生自 tests/ 一级目录
#   (testpaths)，非手工维护清单(根宪法§9.5)；禁 wall-clock——用 time.perf_counter() 相对耗时，
#   生成数据零 datetime.now()/time.time() 绝对时戳(根宪法 RULE-SCHEMA-TZ)；分片纯只读采集
#   (--collect-only --continue-on-collection-errors)，零执行零写生产路径；--shard 仅切窗口不缩语义
# [MODIFY-GUARD] 2026-10-11 st-maint2-20261011 新建（T12 import 面测试夜班降敏/错峰，裁定⑥）：
#   首落只诊断+切片，未接排产入口（排班/心跳/commit_queue 皆在册禁动面）；后续接排产须经总包
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺 pytest 子进程/解析失败→该分片记 unparsed_error 不静默清零；tests/ 缺失→
#   enumerate_shards 返回空且 --emit 拒绝写空册（exit 2）；YAML 不可写→OSError 上抛
# [TESTS] tests/gov/governance/generators/test_collection_shard_manifest_redpin.py
# [A_module] module_id=MOD-GOV-CSHARD-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 夜班错峰采集按需调用的 CLI（--emit/--shard/--list），非 cron/非 daemon/非常驻服务
# [PROVISIONAL] 暂编号 MOD-GOV-CSHARD-001：docs/03_modules 解冻后按注册表重编
"""generate_collection_shard_manifest — tests/ 采集面按目录分片机生册 + 错峰命令入口。

大白话（做什么/解决什么/怎么做）：
  病：`pytest tests/ -k "<kw>"` 夜班一跑约 20 分钟，时间几乎全花在"收集期"——要 import 全库模块面
      才能按关键词筛选；一被打断只剩"19 errors"这种无归因噪声，还和别的班抢资源。
  做：把"整棵 tests/ 的一次性 import 采集"按 tests/ 一级目录切成一片一片（每片=一个目录，
      自成一个可独立重跑的窗口）。产出机生册：每个目录的 collected / error_count / 每条错误的
      首行根因 + real_broken_link|environmental 归因 + 最近一次采集相对耗时。命令入口
      `--shard <目录名|序号>` 让夜班每次只切一片窗口跑（`--dry-run` 只打印命令不跑）。
  红线：本工具是【切片 + 归因 + 只读诊断】，不跳过、不赦免任何 collection error。真断链永远报红；
        environmental 只是给人看的标签（在册 env 缺席当前=0），绝不因贴了 env 标签就从红面消失。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import yaml

from zephyr.shared.infra.process_pool import (
    run_subprocess_hidden,  # noqa: E402 — BARE-SUBPROCESS 正门（trae_067 铁律2 CREATE_NO_WINDOW）
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS_DIR = _REPO_ROOT / "tests"

#: 默认机生册落点（docs/_working=AI 工作交付区，非永久配置册；.json 在此被禁故用 .yaml）。
_DEFAULT_MANIFEST = _REPO_ROOT / "docs" / "_working" / "t12_import_sharding" / "collection_shard_manifest.yaml"

#: 仓内可导入命名空间（缺失=真断链，禁止判环境跳过）。
_REPO_TOP_NAMESPACES = frozenset(
    {
        "zephyr",
        "scripts",
        "data",
        "governance",
        "tools",
        "config",
        "schemas",
        "src",
    }
)

#: 已知"可选第三方/硬件依赖"顶层包（缺席多为环境性，如 GPU/torch）。命中才允许标 environmental；
#: 名单外一律 fail-toward-red 归 real_broken_link。此表是唯一放宽面，扩表须经总包。
_OPTIONAL_THIRD_PARTY = frozenset(
    {
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow",
        "tf_keras",
        "keras",
        "cudf",
        "cuml",
        "cupy",
        "numba",
        "nvidia",
        "pynvml",
        "GPUtil",
        "pycuda",
        "xgboost",
        "lightgbm",
        "catboost",
        "talib",
        "ta",
        "TA_Lib",
        "psutil",
        "pyarrow",
        "tables",
        "h5py",
        "nvidia_ml",
    }
)

_MODULE_NAMED_RE = re.compile(r"No module named '([^']+)'")
_CANNOT_IMPORT_RE = re.compile(r"cannot import name '([^']+)' from '?([^' ]+)")
_BLOCK_RE = re.compile(r"^_+ ERROR collecting (\S+\.py) _+$", re.MULTILINE)
_ELINE_RE = re.compile(r"^E(\s+)(\w+Error|\w+Exception):\s*(.*)$", re.MULTILINE)
_SUMMARY_RE = re.compile(
    r"=+\s*(?P<collected>\d+) tests? collected.*?(?:,\s*(?P<errors>\d+) error.*)?\s+in\s+(?P<secs>[\d.]+)s"
)
_HEADER_RE = re.compile(r"^collected.*?items?(?:.*?/\s*\d+ error)?(?:.*?/\s*(?P<skipped>\d+) skipped)?", re.MULTILINE)


def _missing_module_top(exc_line: str) -> str | None:
    """从一条 'E ...Error: ...' 里取缺失顶层包名（仅 ModuleNotFoundError/ImportError 有意义）。"""
    m = _MODULE_NAMED_RE.search(exc_line)
    if m:
        return m.group(1).split(".")[0]
    m = _CANNOT_IMPORT_RE.search(exc_line)
    if m:
        # "cannot import name X from 'pkg.mod'" → 取 from 侧顶层
        return m.group(2).split(".")[0] or None
    return None


def classify_error(block: str) -> dict:
    """把一段 pytest 'ERROR collecting' 文本块归因。

    返回 {"category": "real_broken_link"|"environmental"|"unparsed_error",
          "first_line": <E 行首行原文>, "missing_module": <顶层包名或空>}。
    fail-toward-red：任何歧义/其它异常(KeyError/SyntaxError/fixture 缺失) 都归 real_broken_link，
    只有 ModuleNotFoundError/ImportError 且缺失顶层∈可选第三方 才归 environmental（且仍留红面）。
    """
    m = _ELINE_RE.search(block)
    if not m:
        first = ""
        for ln in block.splitlines():
            if ln.startswith("E "):
                first = ln.strip()
                break
        return {"category": "unparsed_error", "first_line": first, "missing_module": ""}
    first_line = m.group(0).strip()
    exc_type = m.group(2)
    top = _missing_module_top(first_line) or ""
    if exc_type in ("ModuleNotFoundError", "ImportError") and top:
        if top in _REPO_TOP_NAMESPACES:
            return {"category": "real_broken_link", "first_line": first_line, "missing_module": top}
        if top in _OPTIONAL_THIRD_PARTY:
            return {"category": "environmental", "first_line": first_line, "missing_module": top}
        # 未知顶层：不猜环境，fail-toward-red
        return {"category": "real_broken_link", "first_line": first_line, "missing_module": top}
    # SyntaxError / KeyError(注册表完整性) / fixture 缺失 / 其它 → 真断链候件，禁跳过
    return {"category": "real_broken_link", "first_line": first_line, "missing_module": ""}


def parse_collect_output(out: str) -> dict:
    """从 pytest --collect-only 文本解析 collected / skipped / errors 逐条归因 / 报告耗时。"""
    m = _SUMMARY_RE.search(out)
    collected = int(m.group("collected")) if m else None
    secs = float(m.group("secs")) if m else None
    errors: list[dict] = []
    # 逐块解析：每块以 "_ ERROR collecting <file> _" 起，截到下一个同类或结尾
    for fm in re.finditer(r"_+ ERROR collecting (\S+\.py) _+", out):
        fpath = fm.group(1)
        start = fm.end()
        nxt = re.search(r"_+ ERROR collecting \S+\.py _+", out[start:])
        block = out[start : start + nxt.start()] if nxt else out[start:]
        rec = classify_error(block)
        rec["file"] = fpath.replace("\\", "/")
        errors.append(rec)
    # 去重（同一文件在 ERRORS 区与 summary 区可能重复，按 file 保首个带 E 行的）
    seen: dict[str, dict] = {}
    for e in errors:
        cur = seen.get(e["file"])
        if cur is None or (cur["category"] == "unparsed_error" and e["category"] != "unparsed_error"):
            seen[e["file"]] = e
    hm = _HEADER_RE.search(out)
    skipped = int(hm.group("skipped")) if (hm and hm.group("skipped")) else 0
    return {
        "collected": collected,
        "skipped": skipped,
        "error_count": len(seen),
        "collect_seconds": secs,
        "errors": sorted(seen.values(), key=lambda d: d["file"]),
    }


def enumerate_shards() -> list[str]:
    """按 tests/ 一级目录列出分片（确定性排序）；根级散落 test_*.py 归 '_rootfiles'。"""
    if not _TESTS_DIR.is_dir():
        return []
    shards: list[str] = []
    if any(True for _ in _TESTS_DIR.glob("test_*.py")):
        shards.append("_rootfiles")
    for p in sorted(_TESTS_DIR.iterdir(), key=lambda x: x.name):
        if not p.is_dir() or p.name.startswith((".", "__")):
            continue
        shards.append(p.name)
    return shards


def _run_pytest(args: list[str]) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONPATH"] = str(_REPO_ROOT / "src")
    env["PYTHONUNBUFFERED"] = "1"
    proc = run_subprocess_hidden(
        [sys.executable, "-m", "pytest", *args],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or "")


def collect_shard(shard: str) -> dict:
    """对单个分片跑一次只读采集，返回解析结果（含 wall_ms 与 rc，供错峰窗口耗时参考）。"""
    target = "tests/" if shard == "_rootfiles" else f"tests/{shard}"
    if shard == "_rootfiles":
        root_files = sorted(str(p.relative_to(_REPO_ROOT)).replace("\\", "/") for p in _TESTS_DIR.glob("test_*.py"))
        target_args = root_files if root_files else ["tests/"]
    else:
        target_args = [target]
    t0 = time.perf_counter()
    rc, out = _run_pytest([*target_args, "--collect-only", "-q", "--continue-on-collection-errors"])
    wall_ms = int((time.perf_counter() - t0) * 1000)
    parsed = parse_collect_output(out)
    parsed["shard"] = shard
    parsed["wall_ms"] = wall_ms
    parsed["rc"] = rc
    return parsed


def emit_manifest(out_path: Path, shards: list[str] | None = None) -> dict:
    """逐片采集并写机生册（派生自 tests/ 树，非手工清单）。"""
    shard_names = shards or enumerate_shards()
    if not shard_names:
        raise SystemExit("enumerate_shards() 空——tests/ 缺失，拒绝写空册")
    records = []
    for name in shard_names:
        rec = collect_shard(name)
        records.append(rec)
        real = sum(1 for e in rec["errors"] if e["category"] == "real_broken_link")
        env = sum(1 for e in rec["errors"] if e["category"] == "environmental")
        other = rec["error_count"] - real - env
        print(
            f"[emit] {name:<18} collected={rec['collected']} "
            f"errors={rec['error_count']} (real={real} env={env} other={other}) "
            f"wall_ms={rec['wall_ms']}",
            file=sys.stderr,
        )
    total_errors = sum(r["error_count"] for r in records)
    total_real = sum(1 for r in records for e in r["errors"] if e["category"] == "real_broken_link")
    total_env = sum(1 for r in records for e in r["errors"] if e["category"] == "environmental")
    manifest = {
        # FILE-PLACEMENT-TTL：docs/_working 下 .yaml 须 task_bound（生成器机生，无 wall-clock 时戳）。
        "ttl": "task_bound",
        "title": "T12 tests/ 采集面按目录分片机生册（夜班错峰/降敏诊断）",
        "sid": "st-maint2-20261011",
        # 机生册说明：派生真源=tests/ 一级目录(testpaths)；本册只诊断，不跳过任何 error。
        "derived_from": "tests/ first-level directories (pytest testpaths)",
        "policy": "shard + attribution + read-only diagnose; NEVER skips or absolves a collection error (fail-toward-red)",
        "caveat": "目录分片按 tests/ 一级目录隔离采集，无法复现跨目录 import 污染型收集错误"
        "（如 governance 遮蔽链），此类错误只在整库单进程采集时现形；机生册为诊断面非"
        "'零错误'真源，权威计数仍以整库单进程 --collect-only 为准",
        "totals": {
            "shards": len(records),
            "collected": sum(int(r["collected"] or 0) for r in records),
            "errors": total_errors,
            "real_broken_link": total_real,
            "environmental": total_env,
        },
        "shards": records,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return manifest


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def shard_cmd(shard: str, kw: str | None, do_run: bool) -> int:
    """错峰窗口入口：把采集面切到单个目录一片（do_run=True 真跑，False 只打印命令）。"""
    if shard == "_rootfiles":
        target_args = [
            str(p.relative_to(_REPO_ROOT)).replace("\\", "/") for p in sorted(_TESTS_DIR.glob("test_*.py"))
        ] or ["tests/"]
    else:
        target_args = [f"tests/{shard}"]
    base = [*target_args, "-q", "--continue-on-collection-errors"]
    if kw:
        base += ["-k", kw]
    printable = "python -m pytest " + " ".join(base)
    print(printable)
    if not do_run:
        return 0
    rc, out = _run_pytest(base)
    print(out[-2000:])
    return rc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="tests/ 采集面按目录分片机生册 + 错峰窗口入口（T12）")
    p.add_argument("--emit", action="store_true", help="逐片采集并写机生册（较慢，约数分钟）")
    p.add_argument("--out", default=str(_DEFAULT_MANIFEST), help="机生册 .yaml 路径")
    p.add_argument("--list", action="store_true", help="打印分片清单与机生册摘要")
    p.add_argument("--shard", default="", help="分片名（tests/ 一级目录）或 0 起的序号")
    p.add_argument("--kw", default="", help="可选 -k 关键词（透传给该窗口）")
    p.add_argument("--dry-run", action="store_true", help="--shard 只打印命令不执行")
    p.add_argument("--classify-file", default="", help="调试：对给定 tests/ 路径跑单片采集并打印归因")
    ns = p.parse_args(argv)

    if ns.emit:
        emit_manifest(Path(ns.out))
        return 0
    if ns.classify_file:
        # 允许传相对路径 tests/xxx 或目录名
        shard = ns.classify_file
        if shard.startswith("tests/"):
            shard = shard[len("tests/") :]
        top = shard.split("/")[0]
        rec = collect_shard(top if top != "test" else "_rootfiles")
        print(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False))
        return 0
    if ns.list:
        man = load_manifest(Path(ns.out))
        shards = enumerate_shards()
        for i, s in enumerate(shards):
            print(f"{i:>2}  {s}")
        if man:
            print(f"[manifest totals] {man.get('totals')}")
        else:
            print("[manifest] 未生成，先 --emit")
        return 0
    if ns.shard:
        shard = ns.shard
        if shard.isdigit():
            shards = enumerate_shards()
            idx = int(shard)
            if not (0 <= idx < len(shards)):
                print(f"shard 序号越界: {idx} (0..{len(shards) - 1})", file=sys.stderr)
                return 2
            shard = shards[idx]
        return shard_cmd(shard, ns.kw or None, do_run=not ns.dry_run)
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
