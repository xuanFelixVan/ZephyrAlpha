# [BLUEPRINT] MOD-GOV-REPAIR
# [MODULE] scripts.governance.repair.audit_design_completeness
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.repair.backup_depgraph
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
r"""
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/repair/audit_design_completeness.py | §5.2.4 MIG-4
[MODULE] 无（独立脚本）
[INVARIANTS] 按path精确匹配+按功能名模糊匹配; 输出差距报告; 提取所有ID格式
[MODIFY-GUARD] 本脚本由autopilot执行
[CONSUMERS] autopilot session-20260618-001
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 生成报告→exit 0; 无源文件→exit 1
[TESTS] 无

MIG-4: 完整性审计（v2.0 全面提取版）
- 扫描48个源MD文件
- 提取所有ID格式的模块/功能声明：
  * D-XXX-NN      模块ID（如 D-DATA-01）
  * C-XXX         能力卡片ID（如 C-001）
  * GATE-XX-NN    门禁ID（如 GATE-POS-05）
  * HB-XXX-NN     硬边界ID（如 HB-SEC-01）
  * E-XXX-NN      事件ID（如 E-POS-01）
  * AGG-XXX       聚合根ID（如 AGG-001）
  * CTR-XXX       契约ID（如 CTR-SELL-001）
  * VO-XXX        值对象ID（如 VO-001）
  * DD-XXX-NN     决策ID（如 DD-P2-01）
  * B-XXX         行为边界ID（如 B-001）
  * L-XXX         法规映射ID（如 L-001）
- 按path精确匹配 + 按功能名模糊匹配对照depgraph设计态节点
- 输出差距报告到 data/reports/design_migration_gap_report.md（可经 DESIGN_MIGRATION_REPORT_PATH 覆盖）
"""

__manifest__ = """
args: []
description: 'MIG-4: 完整性审计（v2.0 全面提取版）'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── _shared 模块 import bootstrap（P2迁移：复用 get_depgraph_pg_connection）──
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402

DST_DB = "depgraph (PostgreSQL)"
REPORT_PATH = os.getenv(
    "DESIGN_MIGRATION_REPORT_PATH",
    str(REPO_ROOT / "data" / "reports" / "design_migration_gap_report.md"),
)

# 源MD文件目录/文件
_default_source_dirs = [
    str(REPO_ROOT / "data" / "design_migration" / "依赖图"),
    str(REPO_ROOT / "data" / "design_migration" / "架构图"),
]
_env_source_dirs = os.getenv("DESIGN_MIGRATION_SOURCE_DIRS")
SOURCE_DIRS = _env_source_dirs.split(os.pathsep) if _env_source_dirs else _default_source_dirs
SOURCE_FILES = [
    str(REPO_ROOT / "data" / "design_migration" / "ZephyrAlpha全系统模块清单.md"),
    str(REPO_ROOT / "data" / "design_migration" / "能力定位书.md"),
]

# === 所有ID格式的正则表达式 ===
# 每个元组：(格式名, 正则, ID类型)
# ID类型用于匹配depgraph中的node_type
ID_PATTERNS = [
    # 模块ID：D-XXX-NN 或 D-XXX-NN-XXX 格式
    ("D-XXX-NN", re.compile(r"\b(D-[A-Z][A-Z_]+-\d+(?:-[A-Z]+)?)\b"), "module"),
    # 能力卡片ID：C-001 ~ C-047
    ("C-XXX", re.compile(r"\b(C-\d{3})\b"), "contract"),
    # 门禁ID：GATE-POS-05
    ("GATE-XX-NN", re.compile(r"\b(GATE-[A-Z]+-\d+)\b"), "gate"),
    # 硬边界ID：HB-SEC-01（boundary 已废弃，迁移到 domain，见 node_type_vocabulary.yaml）
    ("HB-XXX-NN", re.compile(r"\b(HB-[A-Z]+-\d+)\b"), "domain"),
    # 事件ID：E-POS-01（event 已废弃，迁移到 module）
    ("E-XXX-NN", re.compile(r"\b(E-[A-Z]+-\d+)\b"), "module"),
    # 聚合根ID：AGG-001
    ("AGG-XXX", re.compile(r"\b(AGG-\d+)\b"), "aggregate"),
    # 契约ID：CTR-SELL-001, CTR-ERR-001, CTR-TRACE-001
    ("CTR-XXX", re.compile(r"\b(CTR-[A-Z]+-\d+)\b"), "contract"),
    # 值对象ID：VO-001（value_object 已废弃，迁移到 module）
    ("VO-XXX", re.compile(r"\b(VO-\d+)\b"), "module"),
    # 决策ID：DD-P2-01, DD-P3-01（decision 已废弃，迁移到 doc）
    ("DD-XXX-NN", re.compile(r"\b(DD-[A-Z]+\d+-\d+)\b"), "doc"),
    # 行为边界ID：B-001, B-013.5（boundary 已废弃，迁移到 domain）
    ("B-XXX", re.compile(r"\b(B-\d{3}(?:\.\d+)?)\b"), "domain"),
    # 法规映射ID：L-001（decision 已废弃，迁移到 doc）
    ("L-XXX", re.compile(r"\b(L-\d{3})\b"), "doc"),
]

# 域ID正则：D-XXX（不带数字），用于提取域名称
DOMAIN_PATTERN = re.compile(r"^###\s+(D-[A-Z][A-Z_]+)\s+(.+)$")


def scan_md_files():
    """扫描所有源MD文件"""
    files = []
    for d in SOURCE_DIRS:
        if os.path.exists(d):
            for name in sorted(os.listdir(d)):
                if name.endswith(".md"):
                    files.append(os.path.join(d, name))
    for f in SOURCE_FILES:
        if os.path.exists(f):
            files.append(f)
    return files


def extract_name_from_line(line, mod_id):
    """从行中提取模块名称（ID后面的文本）"""
    idx = line.find(mod_id)
    if idx < 0:
        return ""
    after = line[idx + len(mod_id) :].strip()
    # 去除表格分隔符和多余字符
    name = re.sub(r"^[|\s\-—:]+", "", after).split("|")[0].strip()
    # 去除冒号（如 C-001：数据接入与管理）
    name = re.sub(r"^[：:]+", "", name).strip()
    # 截取前50字符
    return name[:50]


def extract_declarations(md_path):
    """从MD文件提取所有ID格式的声明（ID + 名称 + 上下文）"""
    declarations = []
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()

        src_name = os.path.basename(md_path)

        # 按行扫描
        for line in content.split("\n"):
            # 对每种ID格式进行匹配
            for fmt_name, pattern, node_type in ID_PATTERNS:
                matches = pattern.findall(line)
                for mod_id in matches:
                    name = extract_name_from_line(line, mod_id)
                    declarations.append(
                        {
                            "source_md": src_name,
                            "module_id": mod_id,
                            "module_name": name,
                            "id_format": fmt_name,
                            "node_type": node_type,
                            "raw_line": line.strip()[:100],
                        }
                    )

            # 提取域名称（### D-XXX 域名称）
            m = DOMAIN_PATTERN.match(line)
            if m:
                domain_id = m.group(1)
                domain_name = m.group(2).strip()
                declarations.append(
                    {
                        "source_md": src_name,
                        "module_id": domain_id,
                        "module_name": domain_name,
                        "id_format": "DOMAIN",
                        "node_type": "domain_root",
                        "raw_line": line.strip()[:100],
                    }
                )

    except Exception as e:
        print(f"  [WARNING] 读取{md_path}失败: {e}")
    return declarations


def match_in_db(conn, declaration):
    """在depgraph中匹配设计态节点（针对不同ID格式使用不同匹配策略）"""
    cur = conn.cursor()
    mod_id = declaration["module_id"]
    mod_name = declaration["module_name"]
    node_type = declaration["node_type"]

    # 1. 精确匹配：path包含module_id
    cur.execute(
        "SELECT node_id FROM nodes WHERE design_maturity='design' AND path LIKE %s LIMIT 1", (f"%{mod_id}%",)
    )
    row = cur.fetchone()
    if row:
        return "path_exact"

    # 2. 精确匹配：node_name = module_id
    cur.execute(
        "SELECT node_id FROM nodes WHERE design_maturity='design' AND node_name = %s LIMIT 1", (mod_id,)
    )
    row = cur.fetchone()
    if row:
        return "name_exact"

    # 3. 模糊匹配：node_name包含module_id
    cur.execute(
        "SELECT node_id FROM nodes WHERE design_maturity='design' AND node_name LIKE %s LIMIT 1", (f"%{mod_id}%",)
    )
    row = cur.fetchone()
    if row:
        return "name_fuzzy"

    # 4. 按node_type过滤后匹配（提高准确性）
    if node_type:
        # 4a. 在对应node_type中精确匹配node_name
        cur.execute(
            "SELECT node_id FROM nodes WHERE design_maturity='design' AND node_type=%s AND node_name = %s LIMIT 1",
            (node_type, mod_id),
        )
        row = cur.fetchone()
        if row:
            return "type_name_exact"

        # 4b. 在对应node_type中模糊匹配node_name
        cur.execute(
            "SELECT node_id FROM nodes WHERE design_maturity='design' AND node_type=%s AND node_name LIKE %s LIMIT 1",
            (node_type, f"%{mod_id}%"),
        )
        row = cur.fetchone()
        if row:
            return "type_name_fuzzy"

    # 5. 模糊匹配：path包含module_name（如果name非空且足够长）
    if mod_name and len(mod_name) >= 3:
        # 跳过纯中文的名称（避免误匹配）
        if re.search(r"[A-Za-z]{3,}", mod_name):
            cur.execute(
                "SELECT node_id FROM nodes WHERE design_maturity='design' AND path LIKE %s LIMIT 1", (f"%{mod_name}%",)
            )
            row = cur.fetchone()
            if row:
                return "path_name_fuzzy"

            # 6. 模糊匹配：node_name包含module_name
            cur.execute(
                "SELECT node_id FROM nodes WHERE design_maturity='design' AND node_name LIKE %s LIMIT 1",
                (f"%{mod_name}%",),
            )
            row = cur.fetchone()
            if row:
                return "name_name_fuzzy"

    return None


def check_duplicates(conn):
    """检查depgraph中是否有重复path的设计态节点"""
    cur = conn.cursor()
    cur.execute("""
        SELECT path, COUNT(*) as cnt, STRING_AGG(node_id, ',') as ids
        FROM nodes WHERE design_maturity='design' AND path IS NOT NULL AND path != ''
        GROUP BY path HAVING cnt > 1
    """)
    rows = cur.fetchall()
    return [{"path": r["path"], "count": r["cnt"], "ids": r["ids"]} for r in rows]


def main():
    # 扫描MD文件
    md_files = scan_md_files()
    print(f"[INFO] 扫描到 {len(md_files)} 个MD文件")

    # 提取所有声明
    all_declarations = []
    format_stats = {}  # 各格式提取统计
    for md_path in md_files:
        decls = extract_declarations(md_path)
        all_declarations.extend(decls)
        if decls:
            print(f"  {os.path.basename(md_path)}: {len(decls)} 个声明")

    print(f"\n[INFO] 共提取 {len(all_declarations)} 个声明（含重复）")

    # 按格式统计
    for d in all_declarations:
        fmt = d["id_format"]
        format_stats[fmt] = format_stats.get(fmt, 0) + 1
    print("[INFO] 各格式提取统计:")
    for fmt, cnt in sorted(format_stats.items(), key=lambda x: -x[1]):
        print(f"  {fmt:15s}: {cnt}")

    # 去重（按module_id + id_format）
    seen_keys = set()
    unique_declarations = []
    for d in all_declarations:
        key = (d["module_id"], d["id_format"])
        if key not in seen_keys:
            seen_keys.add(key)
            unique_declarations.append(d)
    print(f"[INFO] 去重后 {len(unique_declarations)} 个唯一声明")

    # 按格式统计唯一声明
    unique_format_stats = {}
    for d in unique_declarations:
        fmt = d["id_format"]
        unique_format_stats[fmt] = unique_format_stats.get(fmt, 0) + 1
    print("[INFO] 各格式唯一声明统计:")
    for fmt, cnt in sorted(unique_format_stats.items(), key=lambda x: -x[1]):
        print(f"  {fmt:15s}: {cnt}")

    # 连接DB匹配
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        matched = 0
        missing = []
        match_methods = {}

        for i, decl in enumerate(unique_declarations):
            method = match_in_db(conn, decl)
            if method:
                matched += 1
                match_methods[method] = match_methods.get(method, 0) + 1
            else:
                missing.append(decl)

            if (i + 1) % 500 == 0:
                print(f"  [进度] {i + 1}/{len(unique_declarations)} (匹配={matched}, 缺失={len(missing)})")

        # 检查重复
        duplicates = check_duplicates(conn)

        # 生成差距报告
        print(f"\n[结果] 匹配={matched}, 缺失={len(missing)}, 重复={len(duplicates)}")
        print(f"  匹配方式分布: {match_methods}")

        # 按格式统计缺失项
        missing_format_stats = {}
        for m in missing:
            fmt = m["id_format"]
            missing_format_stats[fmt] = missing_format_stats.get(fmt, 0) + 1
        print("  缺失项格式分布:")
        for fmt, cnt in sorted(missing_format_stats.items(), key=lambda x: -x[1]):
            print(f"  {fmt:15s}: {cnt}")

        report = []
        report.append("=== 设计态迁移差距报告（v2.0 全面提取版）===")
        report.append(f"生成时间: {datetime.now().isoformat()}")
        report.append(f"源MD文件数: {len(md_files)}")
        report.append(f"提取的声明总数（含重复）: {len(all_declarations)}")
        report.append(f"去重后唯一声明数: {len(unique_declarations)}")
        report.append("")
        report.append("【各格式提取统计】")
        report.append("| ID格式 | 唯一声明数 | 缺失数 | 匹配数 | 匹配率 |")
        report.append("|--------|-----------|--------|--------|--------|")
        for fmt in sorted(unique_format_stats.keys()):
            total = unique_format_stats[fmt]
            miss = missing_format_stats.get(fmt, 0)
            mat = total - miss
            rate = f"{mat * 100 / total:.1f}%" if total > 0 else "0%"
            report.append(f"| {fmt} | {total} | {miss} | {mat} | {rate} |")
        report.append("")
        report.append(f"匹配方式分布: {match_methods}")
        report.append("")

        # 缺失项
        report.append(f"【缺失项】（源MD有声明，depgraph无记录）共{len(missing)}项")
        report.append("| # | 源MD文件 | ID格式 | 模块ID | 模块名称 | 缺失原因 |")
        report.append("|---|---|---|---|---|---|")
        for i, m in enumerate(missing, 1):
            report.append(
                f"| {i} | {m['source_md']} | {m['id_format']} | {m['module_id']} | {m['module_name']} | path和功能名均未命中 |"
            )
        report.append("")

        # 重复项
        report.append(f"【重复项】（depgraph有多个同path节点）共{len(duplicates)}项")
        report.append("| # | path | 节点数 | 节点ID列表 | 处置建议 |")
        report.append("|---|---|---|---|---|")
        for i, d in enumerate(duplicates, 1):
            report.append(f"| {i} | {d['path']} | {d['count']} | {d['ids']} | 保留ID最小的，记录其余到待删除清单 |")
        report.append("")

        # 信息不足项（无法自动补入的）
        info_insufficient = [m for m in missing if not m["module_name"] or len(m["module_name"]) < 3]
        report.append(f"【信息不足项】（缺模块名称，无法用--add-design-node补入）共{len(info_insufficient)}项")
        report.append("| # | 源MD文件 | ID格式 | 模块ID | 缺失字段 | 处置 |")
        report.append("|---|---|---|---|---|---|")
        for i, m in enumerate(info_insufficient, 1):
            report.append(
                f"| {i} | {m['source_md']} | {m['id_format']} | {m['module_id']} | module_name | 记录到待人工补全清单 |"
            )
        report.append("")

        # 汇总
        report.append("=== 汇总 ===")
        report.append(f"缺失项: {len(missing)}")
        report.append(f"重复项: {len(duplicates)}")
        report.append(f"信息不足项: {len(info_insufficient)}")
        if len(unique_declarations) > 0:
            report.append(
                f"匹配率: {matched}/{len(unique_declarations)} = {matched * 100 / len(unique_declarations):.1f}%"
            )

        # 写入报告
        report_text = "\n".join(report)
        tmp_path = REPORT_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        os.replace(tmp_path, REPORT_PATH)

        print(f"\n[OK] 差距报告已生成: {REPORT_PATH}")
        print(f"  缺失项: {len(missing)}")
        print(f"  重复项: {len(duplicates)}")
        print(f"  信息不足项: {len(info_insufficient)}")
        if len(unique_declarations) > 0:
            print(f"  匹配率: {matched * 100 / len(unique_declarations):.1f}%")

        # MIG-4验收：差距报告生成，且缺失项=0或仅剩信息不足项
        non_insufficient_missing = len(missing) - len(info_insufficient)
        if non_insufficient_missing <= 0:
            print(f"\n[PASS] MIG-4 验收通过: 差距报告已生成，缺失项=0（信息不足项{len(info_insufficient)}个已豁免）")
            sys.exit(0)
        else:
            print(
                f"\n[FAIL] MIG-4 验收失败: 缺失项={len(missing)}，信息不足项={len(info_insufficient)}，非信息不足缺失={non_insufficient_missing}>0"
            )
            print(f"       需执行MIG-5 M5-2补缺步骤补入{non_insufficient_missing}个缺失项")
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
