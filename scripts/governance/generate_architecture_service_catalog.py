#!/usr/bin/env python3
"""
生成「架构/服务目录 + C4 类多视图摘要 + 可检索 JSON」—— 尽量从代码与元数据推导。

仓库根执行:
  python scripts/governance/generate_architecture_service_catalog.py

输出（默认）:
  docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_<date>.json
  docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_<date>.md

输入来源: git ls-files (src/)、pyproject.toml、src/api/main.py、src/api/routes/*.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path


def git_ls_files(repo_root: Path, prefix: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files", prefix],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def parse_pyproject_basic(repo_root: Path) -> dict[str, str]:
    raw = (repo_root / "pyproject.toml").read_text(encoding="utf-8", errors="replace")
    name_m = re.search(r'name\s*=\s*"([^"]+)"', raw)
    ver_m = re.search(r'version\s*=\s*"([^"]+)"', raw)
    py_m = re.search(r"requires-python\s*=\s*\"([^\"]+)\"", raw)
    lic_m = re.search(r"license\s*=\s*\{[^}]*text\s*=\s*\"([^\"]+)\"", raw, re.DOTALL)
    return {
        "name": name_m.group(1) if name_m else "unknown",
        "version": ver_m.group(1) if ver_m else "",
        "requires_python": py_m.group(1) if py_m else "",
        "license_spdx": lic_m.group(1) if lic_m else "",
    }


def parse_router_prefixes(main_py: Path) -> dict[str, str]:
    text = main_py.read_text(encoding="utf-8", errors="replace")
    prefixes: dict[str, str] = {}
    for m in re.finditer(
        r'app\.include_router\(\s*(\w+)\.router\s*(?:,\s*prefix\s*=\s*["\']([^"\']*)["\'])?',
        text,
    ):
        mod = m.group(1)
        pref = m.group(2) if m.lastindex and m.group(2) is not None else ""
        prefixes[mod] = pref or ""
    return prefixes


def extract_routes(route_file: Path) -> list[dict[str, str]]:
    text = route_file.read_text(encoding="utf-8", errors="replace")
    routes: list[dict[str, str]] = []
    for m in re.finditer(
        r"@router\.(get|post|put|delete|patch)\(\s*[\"']([^\"']+)[\"']",
        text,
        re.IGNORECASE,
    ):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


def src_directory_tree(paths: list[str]) -> dict:
    """按 src/ 下路径建树（仅目录 + .py 计数）。"""
    tree: dict = {}
    for p in paths:
        if not p.startswith("src/") or not p.endswith(".py"):
            continue
        parts = p.split("/")
        node = tree
        for seg in parts[:-1]:
            node = node.setdefault(seg, {})
        node.setdefault("_files", []).append(parts[-1])
    return tree


def flatten_modules(tree: dict, prefix: str = "") -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for k, v in sorted(tree.items()):
        if k == "_files":
            continue
        path = f"{prefix}/{k}" if prefix else k
        files = v.get("_files", []) if isinstance(v, dict) else []
        sub = {sk: sv for sk, sv in v.items() if sk != "_files"} if isinstance(v, dict) else {}
        py_count = len([f for f in files if f.endswith(".py")])
        rows.append({"path": path, "python_files": py_count})
        rows.extend(flatten_modules(sub, path))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    parser.add_argument(
        "--out-dir",
        default="docs/09_AUDIT/STATE",
        help="相对仓库根",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    proj = parse_pyproject_basic(repo_root)
    src_paths = git_ls_files(repo_root, "src")
    tree = src_directory_tree(src_paths)
    components = flatten_modules(tree.get("src", {}), "src")

    main_py = repo_root / "src" / "api" / "main.py"
    route_prefixes = parse_router_prefixes(main_py) if main_py.is_file() else {}

    http_services: list[dict[str, object]] = []
    routes_dir = repo_root / "src" / "api" / "routes"
    if routes_dir.is_dir():
        for rf in sorted(routes_dir.glob("*.py")):
            if rf.name.startswith("_") or rf.name == "__init__.py":
                continue
            mod = rf.stem
            prefix = route_prefixes.get(mod, "")
            rlist = extract_routes(rf)
            full_paths = []
            for r in rlist:
                p = r["path"]
                if not p.startswith("/"):
                    p = "/" + p
                base = prefix.rstrip("/") if prefix else ""
                full = (base + p).replace("//", "/") or p
                full_paths.append({"method": r["method"], "path": full})
            http_services.append(
                {
                    "route_module": mod,
                    "url_prefix": prefix or "(none)",
                    "endpoints": full_paths,
                    "source_file": str(rf.relative_to(repo_root)).replace("\\", "/"),
                }
            )

    contract_rel = "docs/03_TRADING_TACTICS/API_Contract.md"
    contract_abs = repo_root / contract_rel
    contract_ok = contract_abs.is_file()

    has_license = (repo_root / "LICENSE").is_file()
    has_contributing = (repo_root / "CONTRIBUTING.md").is_file()
    has_security_root = (repo_root / "SECURITY.md").is_file()

    root_gaps = [
        {
            "item": "LICENSE",
            "institutional_note": "根目录许可证文件（与 pyproject 声明一致，便于 GitHub/GitLab 识别）",
            "status": "已存在" if has_license else "缺失",
        },
        {
            "item": "CONTRIBUTING.md",
            "institutional_note": "贡献流程、PR、代码风格入口",
            "status": "已存在" if has_contributing else "缺失",
        },
        {
            "item": "SECURITY.md（根目录）",
            "institutional_note": "漏洞上报渠道（GitHub Security 推荐）；细则可在 docs 展开",
            "status": "已存在" if has_security_root else "缺失",
        },
        {
            "item": "Dockerfile / compose",
            "institutional_note": "可复现运行与 CI 镜像",
            "status": "当前仓库未检出",
        },
        {
            "item": "CODEOWNERS",
            "institutional_note": "按路径自动评审人",
            "status": "当前仓库未检出",
        },
        {
            "item": ".python-version / 工具链钉扎",
            "institutional_note": "与 pyproject requires-python 对齐的可选文件",
            "status": "可选",
        },
    ]

    payload = {
        "generated_date": args.date,
        "generator": "scripts/governance/generate_architecture_service_catalog.py",
        "sources": [
            "git ls-files src/",
            "pyproject.toml",
            "src/api/main.py",
            "src/api/routes/*.py",
        ],
        "project": proj,
        "contracts": {
            "api_contract_markdown": contract_rel,
            "exists": contract_ok,
        },
        "c4_views": {
            "context": {
                "system": "ZephyrAlpha / 清风量化",
                "summary": "量化交易与策略研究系统；用户含研究员/运营/自动化客户端；对外契约见 API_Contract 与 OpenAPI。",
                "external_docs": [
                    "docs/01_FRAMEWORK/ARCHITECTURE.md",
                    "docs/03_TRADING_TACTICS/API_Contract.md",
                ],
            },
            "containers": [
                {
                    "name": "python_application",
                    "technology": f"Python {proj.get('requires_python') or '3.10+'}",
                    "path": "src/",
                    "entry_cli": "python -m src.main",
                    "role": "领域逻辑、引擎、模块",
                },
                {
                    "name": "http_api",
                    "technology": "FastAPI (optional extra `api`)",
                    "path": "src/api/",
                    "entry": "src/api/main.py",
                    "role": "REST/OpenAPI 服务",
                },
            ],
            "components": {
                "src_tree_python_files": components,
                "http_route_modules": http_services,
            },
        },
        "service_catalog": [
            {
                "id": "rest-api",
                "type": "HTTP",
                "owner": "TBD",
                "description": "FastAPI 暴露的策略/回测/监控/健康检查",
                "route_modules": [s["route_module"] for s in http_services],
            },
            {
                "id": "batch-cli",
                "type": "CLI",
                "owner": "TBD",
                "description": "python -m src.main 及离线脚本工作流",
                "path": "src/main.py",
            },
        ],
        "root_gaps_vs_institutional": root_gaps,
    }

    json_path = out_dir / f"ARCHITECTURE_SERVICE_CATALOG_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Markdown（人类浏览 + 嵌入 C4 摘要）
    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 架构服务目录（生成物）",
        f"generated_date: '{args.date}'",
        "generated_by: scripts/governance/generate_architecture_service_catalog.py",
        "---",
        "",
        f"# 架构服务目录与 C4 摘要（自动生成）",
        "",
        (
            f"> **机器真源**：[`ARCHITECTURE_SERVICE_CATALOG_{args.date}.json`]"
            f"(./ARCHITECTURE_SERVICE_CATALOG_{args.date}.json)\n"
            "> **复跑**：仓库根 `python scripts/governance/generate_architecture_service_catalog.py`\n"
            "> **叙事与裁决**仍以 [`docs/01_FRAMEWORK/ARCHITECTURE.md`](../../01_FRAMEWORK/ARCHITECTURE.md)、"
            "[`docs/System_Manifest.md`](../../System_Manifest.md) 等为真源；本文仅**从代码/元数据推导**的索引视图。"
        ),
        "",
        "## 1. 项目元数据（pyproject）",
        "",
        f"| 键 | 值 |",
        f"|---|---|",
        f"| name | `{proj['name']}` |",
        f"| version | `{proj['version']}` |",
        f"| requires-python | `{proj['requires_python']}` |",
        f"| license | `{proj['license_spdx']}` |",
        "",
        "## 2. C4 — Context（上下文）",
        "",
        payload["c4_views"]["context"]["summary"],
        "",
        f"- **对外契约**： [`{contract_rel}`](../../03_TRADING_TACTICS/API_Contract.md)（存在：**{'是' if contract_ok else '否'}**）",
        "",
        "## 3. C4 — Containers（容器）",
        "",
    ]
    for c in payload["c4_views"]["containers"]:
        md_lines.append(f"### {c['name']}")
        md_lines.append("")
        for k, v in c.items():
            if k == "name":
                continue
            md_lines.append(f"- **{k}**：{v}")
        md_lines.append("")

    md_lines.extend(
        [
            "## 4. C4 — Components（组件 / HTTP 端点摘录）",
            "",
        ]
    )
    for svc in http_services:
        md_lines.append(f"### `{svc['route_module']}` ← `{svc['source_file']}`")
        md_lines.append("")
        md_lines.append(f"- **url_prefix**：`{svc['url_prefix']}`")
        md_lines.append("- **endpoints**：")
        for ep in svc["endpoints"][:30]:
            md_lines.append(f"  - `{ep['method']}` `{ep['path']}`")
        if len(svc["endpoints"]) > 30:
            md_lines.append(f"  - … 共 {len(svc['endpoints'])} 条，详见 JSON")
        md_lines.append("")

    md_lines.extend(
        [
            "## 5. `src/` 目录组件平面表（按文件夹 Python 文件数）",
            "",
            "| 路径前缀 | .py 文件数 |",
            "|---|---:|",
        ]
    )
    for row in components[:80]:
        md_lines.append(f"| `{row['path']}` | {row['python_files']} |")
    if len(components) > 80:
        md_lines.append(f"| … | 共 {len(components)} 行，见 JSON |")
    md_lines.append("")

    md_lines.extend(
        [
            "## 6. 根目录相对专业机构常见缺口（自检表）",
            "",
            "| 项 | 说明 |",
            "|---|---|",
        ]
    )
    for g in root_gaps:
        md_lines.append(f"| **{g['item']}** | {g['institutional_note']}；**状态**：{g['status']} |")
    md_lines.append("")
    md_lines.append(
        "> 说明：表中「已补」以**本仓库目标态**为准；若某文件尚未提交，以 `git ls-files` 根目录为准更新本生成物。"
    )
    md_lines.append("")

    md_path = out_dir / f"ARCHITECTURE_SERVICE_CATALOG_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(repo_root)}")
    print(f"Wrote: {md_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
