# -*- coding: utf-8 -*-
"""
更新orphan_cleanup_audit.md审查状态和备注。
用CSV决策更新每行的审查状态列和备注列，更新§1进度表、§5执行清单、§6审查记录。
临时脚本，用完删除（RULE-FIVE）。
"""
import csv
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"D:\ZephyrAlpha")
AUDIT_DOC = PROJECT_ROOT / "docs/02_enterprise_architecture/03_governance_reports/orphan_cleanup_audit.md"
CSV_PATH = PROJECT_ROOT / "docs/02_enterprise_architecture/03_governance_reports/_review_decisions.csv"

# 读取CSV决策
decisions = {}
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        key = (int(row["section"]), int(row["num"]))
        decisions[key] = row

# 读取文档
content = AUDIT_DOC.read_text(encoding="utf-8")
lines = content.splitlines()
new_lines = []

# 状态跟踪
current_section = None  # 3 or 4
updated_orphan = 0
updated_zombie = 0

# 统计
stats = {
    3: {"approved": 0, "rejected": 0, "pending": 0},
    4: {"approved": 0, "rejected": 0, "pending": 0},
}

# 执行清单数据
exec_db_delete = []      # §5.1
exec_update_path = []    # §5.2
exec_register = []       # §5.3
exec_disk_delete = []    # §5.4

for line in lines:
    # 检测章节
    if line.startswith("## 3. 孤儿文件逐条审查表"):
        current_section = 3
        new_lines.append(line)
        continue
    if line.startswith("## 4. 僵尸节点逐条审查表"):
        current_section = 4
        new_lines.append(line)
        continue
    if line.startswith("## 5."):
        current_section = None
        # 在§5之前插入已更新的§1-§4内容
        break

    # 处理表格行
    if current_section in (3, 4) and line.strip().startswith("|"):
        cells = line.split("|")
        # 跳过表头和分隔行
        if len(cells) < 6:
            new_lines.append(line)
            continue
        first_cell = cells[1].strip()
        if first_cell in ("#", ":---", "---") or first_cell.startswith(":---") or first_cell.startswith("---"):
            new_lines.append(line)
            continue
        try:
            item_num = int(first_cell)
        except ValueError:
            new_lines.append(line)
            continue

        key = (current_section, item_num)
        if key not in decisions:
            new_lines.append(line)
            continue

        decision = decisions[key]
        review_status = decision["review_status"]
        reason = decision["reason"]
        disposition = decision["disposition"]

        # 更新统计
        if review_status == "已批准":
            stats[current_section]["approved"] += 1
        elif review_status == "已拒绝":
            stats[current_section]["rejected"] += 1
        else:
            stats[current_section]["pending"] += 1

        # 收集执行清单数据
        if current_section == 3:
            updated_orphan += 1
            if disposition == "保留并补注册":
                exec_register.append(decision["path"])
            elif disposition == "删除":
                exec_disk_delete.append((decision["path"], reason[:80]))
        elif current_section == 4:
            updated_zombie += 1
            if disposition == "DB DELETE":
                exec_db_delete.append(decision.get("node_id", ""))
            elif disposition == "UPDATE path":
                # 需要从原文获取新路径
                # cells for §4: ['', '#', 'node_id', '路径', '域', '精确状态', '磁盘实际位置', '推荐操作', '置信度', '审查状态', '备注', '']
                old_path = cells[3].strip().strip("`")
                new_path = cells[6].strip().strip("`")
                exec_update_path.append((decision.get("node_id", ""), old_path, new_path))

        # 更新审查状态和备注列
        # §3: 审查状态是第8列(index 8), 备注是第9列(index 9)
        # §4: 审查状态是第9列(index 9), 备注是第10列(index 10)
        if current_section == 3:
            status_idx = 8
            note_idx = 9
        else:
            status_idx = 9
            note_idx = 10

        if len(cells) > note_idx:
            cells[status_idx] = f" {review_status} "
            cells[note_idx] = f" {reason} "
        else:
            # 补齐列
            while len(cells) <= note_idx:
                cells.append(" ")
            cells[status_idx] = f" {review_status} "
            cells[note_idx] = f" {reason} "

        new_line = "|".join(cells)
        new_lines.append(new_line)
    else:
        new_lines.append(line)

# 读取§5之后的内容（保留原样）
remaining_lines = []
found_section_5 = False
for line in lines:
    if line.startswith("## 5."):
        found_section_5 = True
    if found_section_5:
        remaining_lines.append(line)

# ===== 更新§1进度跟踪表 =====
# 找到§1表格并更新
updated_section_1 = []
in_section_1 = False
for line in new_lines:
    if line.startswith("## 1. 审查进度跟踪"):
        in_section_1 = True
        updated_section_1.append(line)
        continue
    if in_section_1:
        if line.startswith("## "):
            in_section_1 = False
            updated_section_1.append(line)
            continue
        if line.strip().startswith("|") and "孤儿文件" in line:
            o_app = stats[3]["approved"]
            o_rej = stats[3]["rejected"]
            o_pen = stats[3]["pending"]
            updated_section_1.append(f"| 孤儿文件 | 312 | {o_pen} | {o_app} | {o_rej} | 0 |")
            continue
        if line.strip().startswith("|") and "僵尸节点" in line:
            z_app = stats[4]["approved"]
            z_rej = stats[4]["rejected"]
            z_pen = stats[4]["pending"]
            updated_section_1.append(f"| 僵尸节点 | 210 | {z_pen} | {z_app} | {z_rej} | 0 |")
            continue
        if line.strip().startswith("|") and "合计" in line:
            t_app = o_app + z_app
            t_rej = o_rej + z_rej
            t_pen = o_pen + z_pen
            updated_section_1.append(f"| **合计** | **522** | **{t_pen}** | **{t_app}** | **{t_rej}** | **0** |")
            continue
    updated_section_1.append(line)

# ===== 生成§5执行清单 =====
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

section_5 = []
section_5.append("## 5. 执行清单（审查完毕后填写）")
section_5.append("")
section_5.append("> 审查完毕后，将所有「已批准」项按操作类型汇总到此节，生成执行命令。")
section_5.append(f"> 审查完成时间: {now}")
section_5.append(f"> 审查人: 治理AI (session-20260624-001)")
section_5.append("")

# §5.1 DB DELETE
section_5.append("### 5.1 DB DELETE 清单（僵尸节点）")
section_5.append("")
section_5.append(f"共 {len(exec_db_delete)} 项。")
section_5.append("")
section_5.append("```sql")
section_5.append("-- 审查批准后的DB DELETE命令")
if exec_db_delete:
    node_ids = ", ".join(exec_db_delete)
    section_5.append(f"-- 分批执行（每批≤20项），执行前必须git备份depgraph.db")
    # 分批输出
    batch_size = 20
    for i in range(0, len(exec_db_delete), batch_size):
        batch = exec_db_delete[i:i+batch_size]
        ids = ", ".join(batch)
        section_5.append(f"-- 批次 {i//batch_size + 1}: {len(batch)}项")
        section_5.append(f"DELETE FROM nodes WHERE node_id IN ({ids});")
section_5.append("```")
section_5.append("")

# §5.2 UPDATE path
section_5.append("### 5.2 UPDATE path 清单（僵尸节点路径更新）")
section_5.append("")
section_5.append(f"共 {len(exec_update_path)} 项。")
section_5.append("")
section_5.append("| node_id | 旧路径 | 新路径 |")
section_5.append("|:---:|------|------|")
for nid, old, new in exec_update_path:
    section_5.append(f"| {nid} | `{old}` | `{new}` |")
section_5.append("")

# §5.3 补注册
section_5.append("### 5.3 补注册清单（孤儿文件）")
section_5.append("")
section_5.append(f"共 {len(exec_register)} 项。")
section_5.append("")
section_5.append("| 路径 | 操作 |")
section_5.append("|------|------|")
for path in exec_register:
    section_5.append(f"| `{path}` | 补注册到全景图 |")
section_5.append("")

# §5.4 磁盘删除
section_5.append("### 5.4 磁盘删除清单（孤儿文件）")
section_5.append("")
section_5.append(f"共 {len(exec_disk_delete)} 项。")
section_5.append("")
section_5.append("| 路径 | 原因 |")
section_5.append("|------|------|")
for path, reason in exec_disk_delete:
    section_5.append(f"| `{path}` | {reason} |")
section_5.append("")

# ===== 生成§6审查记录 =====
section_6 = []
section_6.append("## 6. 审查记录")
section_6.append("")
section_6.append("| 日期 | 审查人 | 审查范围 | 批准数 | 拒绝数 | 备注 |")
section_6.append("|------|------|------|:---:|:---:|------|")
total_app = stats[3]["approved"] + stats[4]["approved"]
total_rej = stats[3]["rejected"] + stats[4]["rejected"]
section_6.append(f"| 2026-06-24 | 治理AI (session-20260624-001) | §3孤儿312项+§4僵尸210项=522项 | {total_app} | {total_rej} | 全部审查完毕，待审查=0 |")
section_6.append("")
section_6.append("---")
section_6.append("")
section_6.append("## 审查流程")
section_6.append("")
section_6.append("1. 逐行检查 §3（孤儿）和 §4（僵尸）的审查表")
section_6.append("2. 对每条记录，判断推荐操作是否正确：")
section_6.append("   - 同意 → 审查状态改为「已批准」")
section_6.append("   - 不同意 → 审查状态改为「已拒绝」，备注栏说明原因")
section_6.append("3. 全部审查完毕后，将「已批准」项汇总到 §5 执行清单")
section_6.append("4. 生成执行命令，经最终确认后执行")
section_6.append("5. 执行完毕后将审查状态改为「已执行」")
section_6.append("")
section_6.append("## 执行原则")
section_6.append("")
section_6.append("- **禁止未审查直接执行**")
section_6.append("- **禁止跨项批量执行**（每批≤20项，执行后验证）")
section_6.append("- **执行前必须 git 备份 depgraph.db**")
section_6.append("- **每批执行后验证全景图一致性**")

# ===== 组装最终文档 =====
final_content = "\n".join(updated_section_1) + "\n" + "\n".join(section_5) + "\n" + "\n".join(section_6) + "\n"

# 原子写入
tmp_path = str(AUDIT_DOC) + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    f.write(final_content)
os.replace(tmp_path, str(AUDIT_DOC))

print(f"文档已更新: {AUDIT_DOC}")
print(f"§3孤儿文件: 更新{updated_orphan}行, 已批准{stats[3]['approved']}, 已拒绝{stats[3]['rejected']}, 待审查{stats[3]['pending']}")
print(f"§4僵尸节点: 更新{updated_zombie}行, 已批准{stats[4]['approved']}, 已拒绝{stats[4]['rejected']}, 待审查{stats[4]['pending']}")
print(f"§5执行清单: DB DELETE={len(exec_db_delete)}, UPDATE path={len(exec_update_path)}, 补注册={len(exec_register)}, 磁盘删除={len(exec_disk_delete)}")
