#!/usr/bin/env python3
"""
七维深度压力测试与逻辑穿透审计脚本 v1.0
审计维度:
1. L0-L5越权检查
2. 真源唯一性冲突(module_id重复)
3. YAML元数据血统(Frontmatter完整性)
4. 孤儿与影子探测(未注册路径)
5. 索引断链审计(INDEX.md死链)
6. 双YAML逻辑炸弹
7. SOP执行闭环
"""

import io
import os
import re
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_FILE = PROJECT_ROOT / "seven_dimensional_audit_report.md"

LAYER_MAP = {
    "00_OVERVIEW": "L0", "00_RESOURCES": "L0",
    "01_FRAMEWORK": "L1",
    "02_FACTOR_LIBRARY": "L2",
    "03_TRADING_TACTICS": "L3",
    "04_EXECUTION": "L4",
    "05_IMPLEMENTATION": "L5",
    "06_ARCHIVE": "L5", "06_CONSTRUCTION_DOCS": "L5",
    "07_AI_INTEGRATION": "L6",
    "08_HUMAN_AI_INTERFACE": "L8",
    "09_AUDIT": "L9", "09_RESEARCH_INNOVATION": "L9",
    "10_GOVERNANCE_COMPLIANCE": "L10", "10_AI_WORKFLOW": "L10",
    "11_STRATEGIC_DECISION": "L11",
}

REQUIRED_FRONTMATTER = {"module_id", "version", "status", "owner"}
RECOMMENDED_FRONTMATTER = {"last_updated", "layer"}

HARDCODE_PATTERNS = [
    (r'(?:max_position_size|stop_loss_pct|take_profit_pct|risk_limit)\s*[:=]\s*[\d.]+', "硬编码风控参数"),
    (r'(?:threshold|limit|max|min)\s*[:=]\s*[\d.]+', "硬编码阈值"),
    (r'(?:RISK_FREE_RATE|BENCHMARK_RETURN|DEFAULT_LEVERAGE)\s*[:=]\s*[\d.]+', "硬编码金融常量"),
    (r'(?:SLIPPAGE|COMMISSION|IMPACT_COST)\s*[:=]\s*[\d.]+', "硬编码交易成本"),
]

class AuditResult:
    def __init__(self):
        self.critical = []
        self.high = []
        self.medium = []
        self.info = []
        self.stats = defaultdict(int)

    def add_critical(self, dim, file, desc):
        self.critical.append({"dim": dim, "file": file, "desc": desc})
        self.stats[f"dim{dim}_critical"] += 1

    def add_high(self, dim, file, desc):
        self.high.append({"dim": dim, "file": file, "desc": desc})
        self.stats[f"dim{dim}_high"] += 1

    def add_medium(self, dim, file, desc):
        self.medium.append({"dim": dim, "file": file, "desc": desc})
        self.stats[f"dim{dim}_medium"] += 1

    def add_info(self, dim, file, desc):
        self.info.append({"dim": dim, "file": file, "desc": desc})
        self.stats[f"dim{dim}_info"] += 1

result = AuditResult()

def get_layer(path: Path) -> str:
    rel = str(path.relative_to(DOCS_DIR))
    parts = rel.replace('\\', '/').split('/')
    if parts:
        top = parts[0]
        return LAYER_MAP.get(top, f"UNKNOWN({top})")
    return "UNKNOWN"

def parse_frontmatter_safe(content: str) -> Tuple[Optional[Dict], str]:
    if not content.startswith('---'):
        return None, content
    pattern = r'^---\s*\n(.*?)\n---\s*[\n]?'
    m = re.match(pattern, content, re.MULTILINE | re.DOTALL)
    if not m:
        return None, content
    yaml_text = m.group(1)
    body = content[m.end():]
    try:
        data = yaml.safe_load(yaml_text)
        if isinstance(data, dict):
            return data, body
        return None, body
    except Exception:
        return None, body

def read_file_safe(path: Path) -> Optional[str]:
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return None

def rel_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace('\\', '/')

print("=" * 80)
print("七维深度压力测试与逻辑穿透审计")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

md_files = list(DOCS_DIR.rglob("*.md"))
print(f"扫描文件总数: {len(md_files)}")

print("\n[维度1] L0-L5越权检查 - 扫描L5硬编码逻辑...")
for f in md_files:
    layer = get_layer(f)
    if layer not in ("L5",):
        continue
    content = read_file_safe(f)
    if not content:
        continue
    body = content
    fm, body_text = parse_frontmatter_safe(content)
    if fm:
        body = body_text
    for pattern, desc in HARDCODE_PATTERNS:
        matches = re.findall(pattern, body, re.IGNORECASE)
        if matches:
            for match in matches[:3]:
                result.add_critical(1, rel_path(f), f"{desc}: `{match}` (L5实现层包含应由L0定义的业务规则)")

print("[维度2] 真源唯一性冲突 - 全局扫描module_id重复...")
module_id_map = defaultdict(list)
for f in md_files:
    content = read_file_safe(f)
    if not content:
        continue
    fm, _ = parse_frontmatter_safe(content)
    if fm and isinstance(fm, dict) and 'module_id' in fm:
        mid = str(fm['module_id']).strip()
        if mid:
            module_id_map[mid].append(rel_path(f))

for mid, files in module_id_map.items():
    if len(files) > 1:
        layers = set()
        for fp in files:
            p = Path(PROJECT_ROOT) / fp
            layers.add(get_layer(p))
        if len(layers) > 1:
            result.add_critical(2, "MULTIPLE", f"module_id `{mid}` 跨层级重复: {files} (层级: {layers})")
        else:
            result.add_high(2, "MULTIPLE", f"module_id `{mid}` 同层级重复: {files}")

placeholder_ids = []
for mid in module_id_map:
    if '[' in mid or 'PLACEHOLDER' in mid.upper() or mid.startswith('YOUR_'):
        placeholder_ids.append(mid)
if placeholder_ids:
    for pid in placeholder_ids:
        result.add_high(2, "MULTIPLE", f"占位符module_id: `{pid}` (文件: {module_id_map[pid]})")

print("[维度3] YAML元数据血统 - Frontmatter完整性检查...")
for f in md_files:
    content = read_file_safe(f)
    if not content:
        continue
    fm, _ = parse_frontmatter_safe(content)
    if fm is None:
        if content.startswith('---'):
            result.add_critical(3, rel_path(f), "YAML Frontmatter存在但无法解析(解析错误)")
        else:
            result.add_medium(3, rel_path(f), "缺少YAML Frontmatter")
        continue
    if not isinstance(fm, dict):
        result.add_critical(3, rel_path(f), f"Frontmatter解析为{type(fm).__name__}而非dict")
        continue
    missing_required = REQUIRED_FRONTMATTER - set(fm.keys())
    missing_recommended = RECOMMENDED_FRONTMATTER - set(fm.keys())
    if missing_required:
        result.add_high(3, rel_path(f), f"缺少必需字段: {missing_required}")
    if missing_recommended:
        result.add_medium(3, rel_path(f), f"缺少推荐字段: {missing_recommended}")
    if 'version' in fm:
        v = str(fm['version'])
        if v.startswith('0.') or 'draft' in v.lower():
            result.add_medium(3, rel_path(f), f"版本号非正式: {v}")
    if 'owner' in fm:
        owner = str(fm['owner'])
        if owner in ('待指定', 'TBD', 'TODO', ''):
            result.add_medium(3, rel_path(f), f"owner为占位符: `{owner}`")
    if 'last_audit' not in fm:
        result.add_info(3, rel_path(f), "缺少last_audit字段(审计追溯缺失)")

print("[维度4] 孤儿与影子探测 - 未注册路径检测...")
path_standard_file = DOCS_DIR / "05_IMPLEMENTATION" / "02_DEVELOPMENT" / "path-standard.md"
registered_dirs = set()
if path_standard_file.exists():
    ps_content = read_file_safe(path_standard_file)
    if ps_content:
        for line in ps_content.split('\n'):
            m = re.match(r'\|\s*`?(\d{2}_[A-Z_]+)`?\s*\|', line)
            if m:
                registered_dirs.add(m.group(1))

top_level_dirs = set()
for d in DOCS_DIR.iterdir():
    if d.is_dir():
        top_level_dirs.add(d.name)

non_standard_dirs = []
for d in top_level_dirs:
    if d.startswith('.') or d.startswith('-') or d.startswith('['):
        non_standard_dirs.append(d)
        result.add_critical(4, d, f"非标准目录名(含特殊字符): `{d}`")
    elif not any(d.startswith(prefix) for prefix in ['00_', '01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_']):
        if d not in registered_dirs:
            result.add_high(4, d, f"未在PATH_STANDARD中注册的影子目录: `{d}`")

for d in DOCS_DIR.rglob("*"):
    if not d.is_dir():
        continue
    name = d.name
    if re.search(r'[\x00-\x1f\u4e00-\u9fff]', name):
        result.add_critical(4, rel_path(d), f"目录名含中文或控制字符: `{name}`")

print("[维度5] 索引断链审计 - INDEX.md死链检查...")
index_files = list(DOCS_DIR.rglob("INDEX.md"))
for idx_file in index_files:
    content = read_file_safe(idx_file)
    if not content:
        continue
    idx_dir = idx_file.parent
    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    for text, href in links:
        if href.startswith('http') or href.startswith('#') or href.startswith('mailto'):
            continue
        clean_href = href.split('#')[0].split('|')[0].strip()
        if not clean_href:
            continue
        target = (idx_dir / clean_href).resolve()
        if not target.exists():
            result.add_high(5, rel_path(idx_file), f"死链: `[{text}]({href})` -> 目标不存在")

    md_in_dir = set()
    for f in idx_dir.rglob("*.md"):
        if f.name != "INDEX.md":
            md_in_dir.add(f.name)
    mentioned_files = set()
    for f in idx_dir.iterdir():
        if f.is_file() and f.suffix == '.md' and f.name != 'INDEX.md':
            fname = f.name
            if fname not in content and fname.replace('.md', '') not in content:
                result.add_medium(5, rel_path(idx_file), f"未挂载文件: `{fname}` (存在于目录但未在索引中引用)")

print("[维度6] 双YAML逻辑炸弹 - 重复YAML块排查...")
for f in md_files:
    content = read_file_safe(f)
    if not content:
        continue
    yaml_block_count = len(re.findall(r'^---\s*$', content, re.MULTILINE))
    if yaml_block_count > 2:
        result.add_critical(6, rel_path(f), f"检测到{yaml_block_count}个YAML分隔符(应为2个), 存在双YAML逻辑炸弹")
    elif yaml_block_count == 2 and not content.strip().startswith('---'):
        result.add_high(6, rel_path(f), "YAML分隔符位置异常(不在文件开头)")

    if content.startswith('---'):
        fm, _ = parse_frontmatter_safe(content)
        if fm is None:
            result.add_critical(6, rel_path(f), "YAML Frontmatter存在但解析失败(逻辑炸弹)")

    module_ids_in_file = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)
    if len(module_ids_in_file) > 1:
        result.add_critical(6, rel_path(f), f"双module_id定义: {module_ids_in_file}")

print("[维度7] SOP执行闭环 - 空洞流程检测...")
sop_dirs = [
    DOCS_DIR / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS",
    DOCS_DIR / "05_IMPLEMENTATION" / "02_DEVELOPMENT",
    DOCS_DIR / "09_AUDIT" / "WORKFLOWS",
    DOCS_DIR / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "00_MANAGEMENT",
]
for sop_dir in sop_dirs:
    if not sop_dir.exists():
        continue
    for f in sop_dir.rglob("*.md"):
        content = read_file_safe(f)
        if not content:
            continue
        has_steps = bool(re.search(r'(?:步骤|Step|STEP)\s*\d', content) or re.search(r'^\d+\.\s', content, re.MULTILINE))
        has_check = bool(re.search(r'(?:自检|验证|检查|验收|Verify|Check|Validate|Test)', content, re.IGNORECASE))
        has_acceptance = bool(re.search(r'(?:验收标准|接受标准|完成标准|Acceptance|Done|Definition of Done)', content, re.IGNORECASE))
        if has_steps and not has_check and not has_acceptance:
            result.add_high(7, rel_path(f), "SOP有步骤但无自检/验收标准(空洞流程)")
        elif has_steps and has_check and not has_acceptance:
            result.add_medium(7, rel_path(f), "SOP有自检但无正式验收标准")

print("\n" + "=" * 80)
print("审计完成，生成报告...")
print("=" * 80)

with open(REPORT_FILE, 'w', encoding='utf-8') as out:
    out.write("# 七维深度压力测试与逻辑穿透审计报告\n\n")
    out.write(f"> **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    out.write(f"> **扫描文件数**: {len(md_files)}\n")
    out.write(f"> **审计范围**: L0-L5 治理体系全量扫描\n\n")

    out.write("---\n\n")
    out.write("## 审计摘要\n\n")
    out.write(f"| 风险等级 | 数量 |\n")
    out.write(f"|----------|------|\n")
    out.write(f"| 🔴 致命风险 (Critical) | {len(result.critical)} |\n")
    out.write(f"| 🟠 逻辑缺陷 (High) | {len(result.high)} |\n")
    out.write(f"| 🟡 合规建议 (Medium) | {len(result.medium)} |\n")
    out.write(f"| ℹ️ 信息 (Info) | {len(result.info)} |\n\n")

    dim_names = {
        1: "L0-L5越权检查",
        2: "真源唯一性冲突",
        3: "YAML元数据血统",
        4: "孤儿与影子探测",
        5: "索引断链审计",
        6: "双YAML逻辑炸弹",
        7: "SOP执行闭环",
    }

    out.write("### 各维度统计\n\n")
    out.write("| 维度 | Critical | High | Medium | Info |\n")
    out.write("|------|----------|------|--------|------|\n")
    for d in range(1, 8):
        c = result.stats.get(f"dim{d}_critical", 0)
        h = result.stats.get(f"dim{d}_high", 0)
        m = result.stats.get(f"dim{d}_medium", 0)
        i = result.stats.get(f"dim{d}_info", 0)
        out.write(f"| {d}. {dim_names[d]} | {c} | {h} | {m} | {i} |\n")
    out.write("\n---\n\n")

    for level_name, level_icon, items in [
        ("致命风险 (Critical)", "🔴", result.critical),
        ("逻辑缺陷 (High)", "🟠", result.high),
        ("合规建议 (Medium)", "🟡", result.medium),
        ("信息 (Info)", "ℹ️", result.info),
    ]:
        if not items:
            continue
        out.write(f"## {level_icon} {level_name}\n\n")
        dim_items = defaultdict(list)
        for item in items:
            dim_items[item["dim"]].append(item)
        for d in sorted(dim_items.keys()):
            out.write(f"### 维度{d}: {dim_names[d]}\n\n")
            for item in dim_items[d]:
                out.write(f"- **文件**: `{item['file']}`\n  **问题**: {item['desc']}\n\n")
        out.write("---\n\n")

    out.write("## 审计结论与建议\n\n")
    out.write("### 致命风险处置优先级\n\n")
    if result.critical:
        critical_dims = defaultdict(int)
        for item in result.critical:
            critical_dims[item["dim"]] += 1
        for d in sorted(critical_dims.keys()):
            out.write(f"1. **维度{d} ({dim_names[d]})**: {critical_dims[d]}个致命问题需立即修复\n")
    else:
        out.write("无致命风险。\n")

    out.write("\n### 治理体系健康度评估\n\n")
    total_issues = len(result.critical) + len(result.high) + len(result.medium)
    if total_issues == 0:
        health = "🟢 优秀"
    elif len(result.critical) > 10:
        health = "🔴 危险"
    elif len(result.critical) > 0:
        health = "🟠 需关注"
    elif len(result.high) > 20:
        health = "🟠 需关注"
    else:
        health = "🟡 一般"
    out.write(f"**综合健康度**: {health}\n")
    out.write(f"- 致命风险: {len(result.critical)}\n")
    out.write(f"- 逻辑缺陷: {len(result.high)}\n")
    out.write(f"- 合规建议: {len(result.medium)}\n")

print(f"\n报告已保存至: {REPORT_FILE}")
print(f"\n审计摘要:")
print(f"  🔴 致命风险 (Critical): {len(result.critical)}")
print(f"  🟠 逻辑缺陷 (High): {len(result.high)}")
print(f"  🟡 合规建议 (Medium): {len(result.medium)}")
print(f"  ℹ️ 信息 (Info): {len(result.info)}")
