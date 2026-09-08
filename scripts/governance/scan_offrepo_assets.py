# -*- coding: utf-8 -*-
"""仓外资产扫描器（Off-repo Asset Scanner）
[BLUEPRINT] MOD-INF-026 §32+附录K 扩展 | config/asset_inventory.yaml offrepo_assets 节
用途:
  scan   扫描 C/E/D 盘项目相关目录，与 offrepo_assets 清单 diff:
         - 新增候选（盘上有、清单无）→ 提示 Owner 确认后 --adopt
         - 消失警告（清单有、盘上无）→ 提示更新清单
         - junction 健康检查（登记为 junction 的路径穿透校验）
  --adopt <path> [--type T] [--criticality L] [--regenerable]
         将候选路径写入 asset_inventory.yaml offrepo_assets（须 Owner 确认后执行）
设计约定:
  - 半自动治理: 机器只发现不登记，收录必须 Owner 裁定（防个人文件/游戏误入清单）
  - 关键词规则命中才报，排除名单过滤个人文件（游戏/微信/影音等）
  - 只读扫描，不修改任何被扫描目录
用法:
  python scripts/governance/scan_offrepo_assets.py scan
  python scripts/governance/scan_offrepo_assets.py --adopt "E:\\新目录" --type raw_corpus
报告: data/asset_index/offrepo_scan_report.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_FILE = PROJECT_ROOT / "config" / "asset_inventory.yaml"
REPORT_FILE = PROJECT_ROOT / "data" / "asset_index" / "offrepo_scan_report.json"

# 扫描根：D/E 盘扫根目录一级；C 盘只扫预定义监控点（避免全盘扫）
SCAN_ROOTS = [
    Path("D:/"),
    Path("E:/"),
]
C_WATCHPOINTS = [
    Path("C:/Temp"),
    Path("C:/Users/fanzi/.cache"),
    Path("C:/Users/fanzi/.trae-cn"),
    Path("C:/Users/fanzi/AppData/Local/Programs"),
    Path("C:/Users/fanzi/AppData/Roaming"),
]

# 项目关键词（目录名含任一即视为候选）
KEYWORDS = [
    "zephyr", "qmt", "ai_cache", "ollama", "ifind", "cold_archive",
    "同花顺", "数据下载", "tushare", "akshare", "wind", "quant",
    "trade", "bridge", "backtest", "factor", "memory",
]
# 排除名单（个人文件/游戏/已知非项目，命中也不报）
EXCLUDE_PATTERNS = [
    r"三角洲", r"微信", r"腾讯", r"爱奇艺", r"网易", r"CloudMusic", r"QQ",
    r"游戏", r"短剧", r"手游", r"Quark", r"百度", r"qycache", r"Loradota",
    r"运动会", r"作业", r"PDF", r"OCR", r"tesseract", r"lightroom", r"adobe",
    r"\\$RECYCLE", r"System Volume", r"\\tmp$", r"HyperV", r"个人文件",
    r"Program Files", r"WindowsApps", r"Temp$", r"__pycache__",
    r"v2rayN",  # 代理工具（"windows" 子串误命中 wind 关键词）
]
# Owner 已裁决排除的明确路径（2026-09-08，见 asset_inventory.yaml "已裁决不登记项" 注释）
EXCLUDE_PATHS = {
    Path("D:/ZephyrAlpha"),                      # 仓库本体，由 scanner 节覆盖
    Path("E:/iFinD"),                            # 已退役 #ARCH-DATA-IFIND-RETIRE-001
    Path("E:/国金证券QMT交易端"),                 # 终端可重装
    Path("E:/国金QMT交易端模拟"),                 # 终端可重装
    Path("D:/国金QMT交易端"),                     # 同上（D 盘副本）
    Path("E:/同花顺行情数据的API工具包"),
    Path("E:/同花顺行情数据的 API 工具包"),
    Path("E:/同花顺软件"),
    Path("E:/同花顺远航版"),
    Path("E:/wind"),                             # Owner 2026-09-08 裁定非项目
    Path("C:/Users/fanzi/.cache/wind-allskill"),  # Wind 插件缓存，非项目
}


def load_inventory_assets() -> list[dict]:
    """从 asset_inventory.yaml 解析 offrepo_assets（轻量行解析，与 scanner 节解耦）"""
    if not INVENTORY_FILE.exists():
        print(f"[ERR] 清单不存在: {INVENTORY_FILE}")
        sys.exit(1)
    text = INVENTORY_FILE.read_text(encoding="utf-8")
    m = re.search(r"^offrepo_assets:\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not m:
        return []
    assets, cur = [], None
    for line in m.group(1).splitlines():
        idm = re.match(r"\s*-\s*id:\s*(\S+)", line)
        if idm:
            cur = {"id": idm.group(1)}
            assets.append(cur)
            continue
        if cur is None:
            continue
        for key in ("path", "type", "criticality", "backup"):
            km = re.match(rf"\s*{key}:\s*\"?([^\"\n]+?)\"?\s*$", line)
            if km:
                cur[key] = km.group(1).replace("\\\\", "\\")
        rm = re.match(r"\s*regenerable:\s*(true|false)", line)
        if rm:
            cur["regenerable"] = rm.group(1) == "true"
    return [a for a in assets if "path" in a]


def iter_candidate_dirs() -> list[Path]:
    """收集扫描根下的候选目录（关键词命中且不在排除名单）"""
    candidates = []

    def hit(name: str) -> bool:
        low = name.lower()
        if any(re.search(p, name, re.I) for p in EXCLUDE_PATTERNS):
            return False
        return any(k in low for k in KEYWORDS)

    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for d in root.iterdir():
            if d.is_dir() and hit(d.name):
                candidates.append(d)
    for root in C_WATCHPOINTS:
        if not root.exists():
            continue
        for d in root.iterdir():
            if d.is_dir() and hit(d.name):
                candidates.append(d)
    return candidates


def dir_size_gb(p: Path) -> float:
    total = 0
    try:
        for f in p.rglob("*"):
            if f.is_file():
                try:
                    total += f.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total / 1024**3


def cmd_scan() -> int:
    assets = load_inventory_assets()
    known_paths = {Path(a["path"]).resolve() for a in assets}
    report = {"timestamp": datetime.now().isoformat(), "candidates": [], "missing": [], "junction_issues": []}

    # 1) 新增候选（排除：主仓库/已裁决路径/已登记路径的祖先与后代）
    for d in iter_candidate_dirs():
        try:
            rp = d.resolve()
        except OSError:
            rp = d
        if d in EXCLUDE_PATHS or rp in {Path(x).resolve() for x in map(str, EXCLUDE_PATHS) if Path(x).exists()}:
            continue
        if any(rp == k or k in rp.parents or rp in k.parents for k in known_paths):
            continue
        report["candidates"].append({"path": str(d), "size_gb": round(dir_size_gb(d), 2)})

    # 2) 消失警告 + 3) junction 健康
    for a in assets:
        p = Path(a["path"])
        if not p.exists():
            report["missing"].append({"id": a["id"], "path": str(p)})
        elif (not p.is_symlink() and p.parent.joinpath(p.name).is_symlink()) or p.is_symlink():
            pass
        try:
            real = p.resolve()
            if str(real).lower() != str(p).lower() and not real.exists():
                report["junction_issues"].append({"path": str(p), "resolves_to": str(real)})
        except OSError:
            pass

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== 仓外资产扫描 {report['timestamp']} ===")
    print(f"清单登记: {len(assets)} 项 | 报告: {REPORT_FILE}")
    if report["candidates"]:
        print(f"\n[新增候选 {len(report['candidates'])} 项 —— 确认后执行 --adopt 登记]")
        for c in report["candidates"]:
            print(f"  {c['path']}  ({c['size_gb']} GB)")
    else:
        print("\n[新增候选] 无")
    if report["missing"]:
        print(f"\n[消失警告 {len(report['missing'])} 项 —— 清单需更新]")
        for c in report["missing"]:
            print(f"  {c['id']}: {c['path']}")
    if report["junction_issues"]:
        print(f"\n[junction 异常 {len(report['junction_issues'])} 项]")
        for c in report["junction_issues"]:
            print(f"  {c['path']} -> {c['resolves_to']}")
    return 0


def cmd_adopt(path: str, type_: str, criticality: str, regenerable: bool, backup: str, notes: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"[ERR] 路径不存在: {p}")
        return 1
    rp = str(p.resolve())
    if any(Path(a["path"]).resolve() == Path(rp) for a in load_inventory_assets()):
        print(f"[SKIP] 已在清单中: {rp}")
        return 0
    size = dir_size_gb(Path(rp))
    entry = (
        f"\n  - id: OFFREPO-ADOPTED-{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4]}\n"
        f"    path: \"{rp.replace(chr(92), chr(92)*2)}\"\n"
        f"    type: {type_}\n"
        f"    regenerable: {str(regenerable).lower()}\n"
        f"    criticality: {criticality}\n"
        f"    backup: {backup}\n"
        f"    notes: \"--adopt 登记 {datetime.now().date()}；{size:.2f}GB；{notes}\"\n"
    )
    text = INVENTORY_FILE.read_text(encoding="utf-8")
    m = re.search(r"(^offrepo_assets:\n)", text, re.M)
    if not m:
        print("[ERR] 清单中未找到 offrepo_assets 节")
        return 1
    # 新条目插到 offrepo_assets: 行之后（列表首项），保持 YAML 列表语法合法
    INVENTORY_FILE.write_text(text[: m.end()] + entry + text[m.end():], encoding="utf-8")
    print(f"[OK] 已登记: {rp} ({size:.2f}GB, type={type_}, criticality={criticality}, backup={backup})")
    if backup == "mirror":
        print("[HINT] backup=mirror —— 请同步在 scripts/backup/backup_config.yaml offrepo_backup.targets 补一条")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="仓外资产扫描器（MOD-INF-026 扩展）")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("scan", help="扫描并 diff 清单")
    adopt = sub.add_parser("adopt", help="登记候选路径（Owner 确认后）")
    adopt.add_argument("path")
    adopt.add_argument("--type", default="raw_corpus", help="资产类型")
    adopt.add_argument("--criticality", default="important", choices=["critical", "important", "low"])
    adopt.add_argument("--regenerable", action="store_true", help="可重建")
    adopt.add_argument("--backup", default="none", choices=["mirror", "none"])
    adopt.add_argument("--notes", default="")
    args = ap.parse_args()

    if args.cmd == "scan":
        return cmd_scan()
    if args.cmd == "adopt":
        return cmd_adopt(args.path, args.type, args.criticality, args.regenerable, args.backup, args.notes)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
