#!/usr/bin/env python3
"""
合并三个蓝图文档，生成融合后的 complete-blueprint-overview.md。
"""
import re
from pathlib import Path

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_before_section(content, section_title):
    """返回 content 中在 section_title 之前的部分（包括标题行）"""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == section_title:
            # 返回直到该行的内容
            return '\n'.join(lines[:i])
    return content

def extract_section(content, section_title):
    """提取从 section_title 开始到下一个同级标题之前的部分"""
    lines = content.split('\n')
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == section_title:
            start = i
            break
    if start == -1:
        return ''
    # 查找下一个以 '## ' 开头的行（同级标题）
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith('## '):
            end = i
            break
    return '\n'.join(lines[start:end])

def main():
    # 读取原始权威文档
    canonical = read_file('docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md')
    # 读取实施计划详情
    impl_details = read_file('implementation_details.md')
    # 读取进度表格
    progress_table = read_file('progress_table.md')
    
    # 提取实施策略部分（从 remaining-blueprints-implementation-plan.md）
    remaining = read_file('docs/11_STRATEGIC_DECISION/remaining-blueprints-implementation-plan.md')
    # 找到 "### 实施策略" 部分（注意前面可能有空行）
    impl_strategy = ''
    lines = remaining.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '### 实施策略':
            # 提取直到下一个 '---' 分隔符或 '## ' 标题
            end = len(lines)
            for j in range(i, len(lines)):
                if j > i and (lines[j].startswith('---') or lines[j].startswith('## ')):
                    end = j
                    break
            impl_strategy = '\n'.join(lines[i:end])
            break
    
    # 构建新内容
    # 我们保留 canonical 的 frontmatter 和前面的部分，直到“## 一、完整模块清单”
    # 在“## 一、完整模块清单”之后插入新章节
    # 首先，找到“## 一、完整模块清单”的位置
    lines_canonical = canonical.split('\n')
    idx_module_list = -1
    for i, line in enumerate(lines_canonical):
        if line.strip() == '## 一、完整模块清单':
            idx_module_list = i
            break
    if idx_module_list == -1:
        print("未找到模块清单章节")
        return
    
    # 找到“## 二、缺失模块详细清单”的位置（可能不存在）
    idx_missing_list = -1
    for i in range(idx_module_list, len(lines_canonical)):
        if lines_canonical[i].strip() == '## 二、缺失模块详细清单':
            idx_missing_list = i
            break
    
    # 构建新行的列表
    new_lines = []
    # 添加 frontmatter 和前面的内容，直到 idx_module_list（包括该行）
    new_lines.extend(lines_canonical[:idx_module_list])
    
    # 添加“## 一、完整模块清单”及其内容，直到下一个章节
    # 确定模块清单章节的结束位置（下一个 '## ' 或文件结尾）
    module_end = len(lines_canonical)
    for i in range(idx_module_list + 1, len(lines_canonical)):
        if lines_canonical[i].startswith('## '):
            module_end = i
            break
    new_lines.extend(lines_canonical[idx_module_list:module_end])
    
    # 插入新章节：实施策略
    if impl_strategy:
        new_lines.append('')
        new_lines.append('## 二、实施策略')
        new_lines.append('')
        new_lines.append(impl_strategy)
    
    # 插入新章节：实施计划详情
    if impl_details:
        new_lines.append('')
        new_lines.append('## 三、实施计划详情')
        new_lines.append('')
        new_lines.append('以下为每个缺失蓝图的详细实施计划：')
        new_lines.append('')
        new_lines.append(impl_details)
    
    # 插入新章节：进度跟踪表
    if progress_table:
        new_lines.append('')
        new_lines.append('## 四、进度跟踪表')
        new_lines.append('')
        new_lines.append(progress_table)
    
    # 添加原有的“缺失模块详细清单”和后续章节（如果存在）
    if idx_missing_list != -1:
        # 找到“缺失模块详细清单”章节的结束位置（下一个 '## ' 或文件结尾）
        missing_end = len(lines_canonical)
        for i in range(idx_missing_list + 1, len(lines_canonical)):
            if lines_canonical[i].startswith('## '):
                missing_end = i
                break
        # 调整标题编号（因为我们在前面插入了新章节）
        # 将“二、缺失模块详细清单”改为“五、缺失模块详细清单”
        # 简单起见，我们保留原样，但需要调整编号
        # 这里我们直接插入原内容，但需要重编号？暂时保持原样。
        new_lines.append('')
        new_lines.extend(lines_canonical[idx_missing_list:missing_end])
        # 添加剩余部分
        if missing_end < len(lines_canonical):
            new_lines.extend(lines_canonical[missing_end:])
    else:
        # 如果没有缺失清单章节，则添加剩余部分（从 module_end 开始）
        if module_end < len(lines_canonical):
            new_lines.extend(lines_canonical[module_end:])
    
    # 写入新文件
    new_content = '\n'.join(new_lines)
    write_file('docs/11_STRATEGIC_DECISION/complete-blueprint-overview-merged.md', new_content)
    print("融合后的文档已保存到 complete-blueprint-overview-merged.md")
    
    # 可选：备份原文件并替换
    # import shutil
    # shutil.copy2('docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md', 'docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md.backup')
    # write_file('docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md', new_content)
    # print("原文件已备份并替换")

if __name__ == '__main__':
    main()