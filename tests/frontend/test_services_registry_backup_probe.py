# [MODULE] tests.frontend.test_services_registry_backup_probe
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""处方 P-13 回归网：仪表盘"备份在位性"两行探针（cold_archive / code_backup）。

三查：①fail-visible 语义不许被治绿——缺目录/缺清单/缺关键件必须判 red（灾备事故），
36h/8d 红黄绿线原样；②版本化快照仓判据只吃「最新日期目录 + 少量关键件」，绝不 os.walk
（G 盘 USB-HDD 单日子目录实测 816,873 件/373s，轮询不可接受）；③判据对象路径跟随
backup_config.yaml 真源（旧缺陷=本文件另抄一份盘符，备份侧迁盘后探针恒红成"狼来了"）。
用例全在 tmp_path 造假目录树，禁扫真 G 盘、禁写 data/ 生产目录。
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.frontend.dashboard import services_registry as sr  # noqa: E402

_KEY_FILES = ("AGENTS.md", "pyproject.toml", "config/.env.postgres")


@pytest.fixture(autouse=True)
def _no_cross_test_cache(monkeypatch):
    """模块级 60s/300s 缓存会串用例——每例换新 dict。"""
    monkeypatch.setattr(sr, "_DIRFRESH_CACHE", {})
    monkeypatch.setattr(sr, "_COLD_CACHE", {})
    monkeypatch.setattr(sr, "_BACKUP_PATH_CACHE", {})


# ── cold_archive：清单在位性 ────────────────────────────────────────────────
def _mk_archive(root: Path, rows: list[dict], *, bom: bool = False) -> Path:
    """造归档根目录 + archive_manifest.jsonl（parquet_path 指向真存在的假件）。"""
    root.mkdir(parents=True, exist_ok=True)
    lines = []
    for r in rows:
        p = root / r["rel"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x" * r["parquet_size_bytes"])
        rec = {k: v for k, v in r.items() if k != "rel"}
        rec["parquet_path"] = str(p)
        lines.append(json.dumps(rec, ensure_ascii=False))
    m = root / "archive_manifest.jsonl"
    m.write_text(("﻿" if bom else "") + "\n".join(lines) + "\n", encoding="utf-8")  # BOM 由生成器实证
    return m


def test_cold_archive_green_all_in_place(tmp_path):
    """清单 2 件全部在位且尺寸相符 → green，detail 报件数与体量。"""
    m = _mk_archive(
        tmp_path / "arch",
        [
            {"rel": "c1/a.parquet", "parquet_size_bytes": 10, "archived_at": "2026-09-20T02:00:00+00:00"},
            {"rel": "c1/b.parquet", "parquet_size_bytes": 20, "archived_at": "2026-09-24T02:00:00+00:00"},
        ],
    )
    light, detail = sr._cold_archive(str(m.parent), "archive_manifest.jsonl")
    assert light == "green", detail
    assert "2 件在位" in detail and "最新归档" in detail  # 停滞天数只展示不判灯


def test_cold_archive_first_bom_line_not_dropped(tmp_path):
    """生成器落盘带 BOM：utf-8-sig 读法须把首行也算进清单（旧 utf-8 读法白丢一条）。"""
    m = _mk_archive(
        tmp_path / "arch",
        [
            {"rel": "a.parquet", "parquet_size_bytes": 5, "archived_at": "2026-09-24T02:00:00+00:00"},
            {"rel": "b.parquet", "parquet_size_bytes": 5, "archived_at": "2026-09-24T02:00:00+00:00"},
        ],
        bom=True,
    )
    light, detail = sr._cold_archive(str(m.parent), "archive_manifest.jsonl")
    assert light == "green" and "2 件在位" in detail, detail


def test_cold_archive_red_when_file_missing(tmp_path):
    """清单有 1 件不在位 → 判红（缺件=灾备事故，不许因为"目录还在"就绿）。"""
    m = _mk_archive(
        tmp_path / "arch",
        [
            {"rel": "a.parquet", "parquet_size_bytes": 5, "archived_at": "2026-09-24T02:00:00+00:00"},
        ],
    )
    (m.parent / "a.parquet").unlink()
    light, detail = sr._cold_archive(str(m.parent), "archive_manifest.jsonl")
    assert light == "red" and "1 件不在位" in detail, detail


def test_cold_archive_red_when_size_mismatch(tmp_path):
    """件在但字节数与清单不符（截断/覆写）→ 判红。"""
    m = _mk_archive(
        tmp_path / "arch",
        [
            {"rel": "a.parquet", "parquet_size_bytes": 5, "archived_at": "2026-09-24T02:00:00+00:00"},
        ],
    )
    (m.parent / "a.parquet").write_bytes(b"xxxxxxx")
    light, detail = sr._cold_archive(str(m.parent), "archive_manifest.jsonl")
    assert light == "red" and "1 件不在位" in detail, detail


def test_cold_archive_red_when_manifest_missing(tmp_path):
    """目录在、清单丢 → 判红（真盘 E:\\zephyr_cold_archive 整盘消失走的也是这条，恒红）。"""
    (tmp_path / "arch").mkdir()
    light, detail = sr._cold_archive(str(tmp_path / "arch"), "archive_manifest.jsonl")
    assert light == "red" and "归档清单丢失" in detail, detail


def test_cold_archive_red_when_dir_missing(tmp_path):
    """根目录不存在 → 判红（缺目录走"清单丢失"这条，正是旧 E:\\zephyr_cold_archive 恒红的
    输出——fail-visible 语义保留，只把判据对象搬到现行真源，不降级灰/绿）。"""
    light, detail = sr._cold_archive(str(tmp_path / "nowhere"), "archive_manifest.jsonl")
    assert light == "red" and "归档清单丢失" in detail, detail


def test_cold_archive_red_when_manifest_empty(tmp_path):
    """清单存在但零条有效记录 → 判红（空清单=归档链断，不许显示成"0 件在位"的绿）。"""
    root = tmp_path / "arch"
    root.mkdir()
    (root / "archive_manifest.jsonl").write_text("\nnot-json\n", encoding="utf-8")
    light, detail = sr._cold_archive(str(root), "archive_manifest.jsonl")
    assert light == "red" and "归档清单为空" in detail, detail


# ── daily_fresh：版本化快照仓廉价判据 ───────────────────────────────────────
def _mk_vault(vault: Path, day: str, *, key_files=_KEY_FILES, age_s: float = 60.0, deep_files: int = 0) -> Path:
    """造 <vault>/<yyyyMMdd>/ 快照：顶层关键件 + 少量顶层条目 + 可选深层文件（验证不递归）。"""
    d = vault / day
    for k in key_files:
        p = d / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    for i in range(5):
        (d / f"top_{i}.txt").write_text("x", encoding="utf-8")
    for i in range(deep_files):
        p = d / "src" / "deep"
        p.mkdir(parents=True, exist_ok=True)
        (p / f"f{i}.py").write_text("x", encoding="utf-8")
    ts = time.time() - age_s
    os.utime(d, (ts, ts))
    return d


def test_daily_fresh_legacy_red_when_dir_missing(tmp_path):
    """无 key_files（旧全盘扫口径）缺目录仍判红——治绿不是修法。"""
    light, detail = sr._daily_fresh(str(tmp_path / "nope"))
    assert light == "red" and "不存在" in detail, detail


def test_daily_fresh_legacy_red_when_empty(tmp_path):
    """旧口径零文件判红（语义未动）。"""
    (tmp_path / "v").mkdir()
    light, detail = sr._daily_fresh(str(tmp_path / "v"))
    assert light == "red" and "为空" in detail, detail


def test_daily_fresh_vault_red_when_dir_missing(tmp_path):
    light, detail = sr._daily_fresh(str(tmp_path / "nope"), _KEY_FILES)
    assert light == "red" and "不存在" in detail, detail


def test_daily_fresh_vault_red_when_no_dated_snapshot(tmp_path):
    """仓在但一个日期快照都没有 → 判红。"""
    (tmp_path / "v" / "not_a_date").mkdir(parents=True)
    light, detail = sr._daily_fresh(str(tmp_path / "v"), _KEY_FILES)
    assert light == "red" and "无日期快照" in detail, detail


def test_daily_fresh_vault_red_when_key_file_missing(tmp_path):
    """快照缺关键件（备份半途/漏阶段）→ 判红并点名缺哪个。"""
    _mk_vault(tmp_path / "v", "20260925", key_files=("AGENTS.md",))
    light, detail = sr._daily_fresh(str(tmp_path / "v"), _KEY_FILES)
    assert light == "red" and "缺关键件 2/3" in detail and "pyproject.toml" in detail, detail


def test_daily_fresh_vault_green_when_fresh(tmp_path):
    """最新快照在位+关键件齐+落盘钟 <36h → green，detail 报快照名与关键件数。"""
    _mk_vault(tmp_path / "v", "20260925", age_s=3600)
    light, detail = sr._daily_fresh(str(tmp_path / "v"), _KEY_FILES)
    assert light == "green", detail
    assert "20260925" in detail and "关键件 3/3 在位" in detail, detail


def test_daily_fresh_vault_uses_latest_complete_snapshot(tmp_path):
    """最新日期快照缺件时回看次新完整快照判灯（真断了旧快照会随年龄自然翻黄/翻红），
    且 detail 必须点名回看，不许偷偷换对象。"""
    v = tmp_path / "v"
    _mk_vault(v, "20260924", age_s=48 * 3600)  # 昨天：完整但已超 36h ⇒ 黄
    _mk_vault(v, "20260925", age_s=3600)  # 今天：完整且新鲜 ⇒ 绿
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "green" and "20260925" in detail, detail
    (v / "20260925" / "pyproject.toml").unlink()
    sr._DIRFRESH_CACHE.clear()
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "yellow" and "回看取 20260924" in detail and "20260925 未落齐" in detail, detail


def test_daily_fresh_vault_tolerates_empty_placeholder_snapshot(tmp_path):
    """跑批先建当日空壳目录（09-26 实测 20260926 长时间 0 条目）不得判红——拿空壳当对象=每天一次假红。"""
    v = tmp_path / "v"
    _mk_vault(v, "20260925", age_s=3600)
    (v / "20260926").mkdir()
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "green" and "20260926 未落齐" in detail, detail


def test_daily_fresh_vault_red_when_no_snapshot_has_key_files(tmp_path):
    """全部候选快照都缺关键件（含空壳）→ 仍判红，回看不等于护短。"""
    v = tmp_path / "v"
    _mk_vault(v, "20260925", key_files=("AGENTS.md",))
    (v / "20260926").mkdir()
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "red" and "缺关键件" in detail, detail


def test_daily_fresh_vault_yellow_and_red_thresholds_unchanged(tmp_path):
    """红黄绿线仍是 36h/8d（处方不许顺手改阈值）：2 天黄、9 天红。"""
    v = tmp_path / "v"
    _mk_vault(v, "20260924", age_s=2 * 86400)
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "yellow" and "超 1 天没备份" in detail, detail
    sr._DIRFRESH_CACHE.clear()
    os.utime(v / "20260924", (time.time() - 9 * 86400,) * 2)
    light, detail = sr._daily_fresh(str(v), _KEY_FILES)
    assert light == "red" and "超 1 周没备份" in detail, detail


def test_daily_fresh_vault_does_not_recurse(tmp_path):
    """探针不得递归：快照里塞 300 个深层文件，顶层条目计数仍只数顶层。"""
    d = _mk_vault(tmp_path / "v", "20260925", deep_files=300)
    light, detail = sr._daily_fresh(str(tmp_path / "v"), _KEY_FILES)
    assert light == "green", detail
    assert f"{len(list(d.iterdir()))} 个顶层条目" in detail, detail
    assert "300" not in detail


def test_daily_fresh_vault_freshness_not_fooled_by_preserved_mtime(tmp_path):
    """关键件 mtime 保留源时间戳（数月前的 .env）不得把钟拖老——落盘钟看快照目录。"""
    d = _mk_vault(tmp_path / "v", "20260925", age_s=3600)
    stale = time.time() - 100 * 86400
    os.utime(d / "config" / ".env.postgres", (stale, stale))
    light, detail = sr._daily_fresh(str(tmp_path / "v"), _KEY_FILES)
    assert light == "green", detail


# ── 备份落点真源跟随（P-13 病根）───────────────────────────────────────────
def test_backup_cfg_path_follows_config(tmp_path, monkeypatch):
    """cfg_key 命中时以 backup_config.yaml 为准（双反斜杠须折叠成单路径）。"""
    cfg = tmp_path / "backup_config.yaml"
    cfg.write_text(
        'working_vault:\n  base: "G:\\\\backup\\\\working_vault"\n'
        "offrepo_backup:\n  targets:\n    - id: cold_archive\n"
        '      source: "F:\\\\zephyr_cold\\\\50_archive"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(sr, "_BACKUP_CFG", cfg)
    assert sr._backup_cfg_path("working_vault", "X:\\fallback") == r"G:\backup\working_vault"
    assert sr._backup_cfg_path("cold_archive", "X:\\fallback") == r"F:\zephyr_cold\50_archive"


def test_backup_cfg_path_falls_back_when_unreadable(tmp_path, monkeypatch):
    """配置不可读/无该段 → 回落 catalog 字面量，且 unknown key 不参与解析。"""
    monkeypatch.setattr(sr, "_BACKUP_CFG", tmp_path / "missing.yaml")
    assert sr._backup_cfg_path("working_vault", r"Y:\literal") == r"Y:\literal"
    assert sr._det_dir({"dir": r"Y:\literal"}) == r"Y:\literal"  # 无 cfg_key ⇒ 原样


def test_catalog_paths_agree_with_backup_config():
    """防再犯：catalog 里两行判据的兜底字面量必须与备份配置真源同值（P-13 漂移的机检）。"""
    c = next(x for x in sr.SERVICE_CATALOG if x["id"] == "cold_archive")["detect"]
    b = next(x for x in sr.SERVICE_CATALOG if x["id"] == "code_backup")["detect"]
    assert c.get("cfg_key") == "cold_archive" and b.get("cfg_key") == "working_vault"
    assert sr._backup_cfg_path("cold_archive", "") == c["dir"]
    assert sr._backup_cfg_path("working_vault", "") == b["dir"]
