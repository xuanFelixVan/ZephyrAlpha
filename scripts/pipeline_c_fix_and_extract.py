#!/usr/bin/env python3
"""
Pipeline C 修复和提取脚本
功能：
1. 修复编码损坏（UTF-8被误判为GBK）
2. 从git历史中提取被删除文件的知识
3. 生成标准化的KE文件

使用：
    python scripts/pipeline_c_fix_and_extract.py --input-list docs/09_AUDIT/STATE/gh-wave3-priority-files.txt --start 100 --count 50
"""

import argparse
import subprocess
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

REPO_ROOT = Path("D:/ZephyrAlpha")
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "08_KNOWLEDGE" / "FACTOR_LIBRARY"
TRACKER_FILE = REPO_ROOT / "docs" / "09_AUDIT" / "STATE" / "elimination-pipeline-tracker.yaml"

# 编码修复映射表（常见UTF-8被误读为GBK的模式）
# 注意：这是部分常见字符的映射，完整修复需要更复杂的处理
ENCODING_FIX_PATTERNS = {
    # 中文标点
    '銆': '【',
    '戓': '】',
    '锛': '（',
    '欤': '）',
    '垎': '析',
    '鏋': '架',
    '勬': '构',
    '枃': '档',
    '妯': '模',
    '鍧': '块',
    '潡': '块',
    '缂': '编',
    '紡': '式',
    '鏍': '格',
    '囨': '图',
    '枅': '档',
    '鏄': '是',
    '暟': '数',
    '鎹': '据',
    '噺': '量',
    '鎺': '接',
    '埗': '制',
    '鍜': '和',
    '绠': '管',
    '悊': '理',
    '鏍': '格',
    '噯': '准',
    '搴': '度',
    '鐩': '目',
    '爣': '标',
    '鎶': '报',
    '憡': '告',
    '鐢': '用',
    '搴旇': '应用',
    '寔': '持',
    '缁': '续',
    '缁翠': '继续',
    '鏇': '更',
    '柊': '新',
    '鏃': '时',
    '棩': '日',
    '鏈熸湡': '日期',
    '鍒': '创',
    '垱': '创',
    '寤': '建',
    '鍒涘缓': '创建',
    '鏈': '有',
    '晥': '效',
    '鏈夋晥': '有效',
    '鎬': '性',
    '鑳': '能',
    '鎬ц兘': '性能',
    '浼樺寲': '优化',
    '绠楁硶': '算法',
    '妯″瀷': '模型',
    '鍥犲瓙': '因子',
    '椋庨櫓': '风险',
    '鎶曡祫': '投资',
    '缁勫悎': '组合',
    '鏀剁泭': '收益',
    '鐜囧垯': '准则',
    '鐩戞帶': '监控',
    '鎺у埗': '控制',
    '绯荤粺': '系统',
    '鏁版嵁': '数据',
    '澶勭悊': '处理',
    '鑾峰彇': '获取',
    '瀛樺偍': '存储',
    '鍒嗘瀽': '分析',
    '璁＄畻': '计算',
    '鍙傛暟': '参数',
    '閰嶇疆': '配置',
    '绠＄悊': '管理',
    '瑙勮寖': '规范',
    '鏍囧噯': '标准',
    '娴佺▼': '流程',
    '鏂规硶': '方法',
    '宸ュ叿': '工具',
    '妯℃澘': '模板',
    '绀轰緥': '示例',
    '璇存槑': '说明',
    '鎻忚堪': '描述',
    '鍔熻兘': '功能',
    '鐗圭偣': '特点',
    '浼樺娍': '优势',
    '鍔＄害': '劣势',
    '椋庨櫓': '风险',
    '闄愬埗': '限制',
    '瑕佹眰': '要求',
    '鏉′欢': '条件',
    '鍓嶆彁': '前提',
    '鍋囫硶': '假设',
    '渚濊禆': '依赖',
    '鍏崇郴': '关系',
    '缁撴瀯': '结构',
    '缁勬垚': '组成',
    '鍒嗙被': '分类',
    '绫诲瀷': '类型',
    '灞炴€': '属性',
    '鐗规€': '特性',
    '琛ㄧ幇': '表现',
    '褰卞搷': '影响',
    '鏁堟灉': '效果',
    '缁撴灉': '结果',
    '杈撳嚭': '输出',
    '杈撳叆': '输入',
    '婧愪簬': '源于',
    '鏉ユ簮': '来源',
    '鐩爣': '目标',
    '鐩殑': '目的',
    '鎰忎箟': '意义',
    '浠峰€': '价值',
    '浣滅敤': '作用',
    '鐢ㄩ€': '用途',
    '搴旂敤': '应用',
    '鍦烘櫙': '场景',
    '鎯呭喌': '情况',
    '鐘舵€佹枃妗ｆ槸': '状态文档是',
    '鏁版嵁璐ㄩ噺': '数据质量',
    '鎺у埗绯荤粺': '控制系统',
    '妯″潡缂栧彿': '模块编号',
    '鐗堟湰': '版本',
    '鍒涘缓鏃ユ湡': '创建日期',
    '浼樺厛绾': '优先级',
    '绯荤粺姒傝堪': '系统概述',
    '鐩爣': '目标',
    '纭繚': '确保',
    '杩涘叆': '进入',
    '婊¤冻': '满足',
    '閲忓寲': '量化',
    '鍒嗘瀽': '分析',
    '璐ㄩ噺': '质量',
    '瑕佹眰': '要求',
    '闃叉': '防止',
    '鍨冨溇': '垃圾',
    '杩涜': '进行',
    '涓枃': '中文',
    '鏂囨。': '文档',
    '鏋舵瀯': '架构',
    '甯屾湜': '希望',
    '鑳藉': '能够',
    '甯姪': '帮助',
    '鎮ㄧ殑': '您的',
    '宸ヤ綔': '工作',
}


def fix_encoding(text: str) -> str:
    """修复UTF-8被误判为GBK导致的乱码"""
    # 尝试将错误解码的文本重新编码为bytes，然后用正确编码解码
    try:
        # 第一步：尝试修复常见的UTF-8被当作Latin-1/GBK解码的问题
        # 将字符串编码为latin-1（逐字节保留），然后用utf-8解码
        bytes_data = text.encode('latin-1', errors='ignore')
        fixed_text = bytes_data.decode('utf-8', errors='ignore')
        return fixed_text
    except Exception as e:
        print(f"编码修复失败: {e}")
        return text


def get_file_from_git_history(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """从git历史中获取被删除文件的内容和commit hash"""
    try:
        # 获取删除该文件的commit hash
        result = subprocess.run(
            ['git', 'log', '--all', '--diff-filter=D', '--name-only', '--pretty=format:%H', '--', file_path],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )
        
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        if not commits:
            return None, None
        
        commit_hash = commits[0]
        
        # 获取父commit中的文件内容
        parent_commit = f"{commit_hash}^"
        result = subprocess.run(
            ['git', 'show', f'{parent_commit}:{file_path}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=REPO_ROOT
        )
        
        if result.returncode == 0:
            return result.stdout, commit_hash
        else:
            return None, commit_hash
            
    except Exception as e:
        print(f"获取git历史失败 {file_path}: {e}")
        return None, None


def extract_core_knowledge(content: str, file_path: str) -> dict:
    """从文件内容中提取核心知识"""
    knowledge = {
        'title': '',
        'summary': '',
        'key_points': [],
        'applicable_scenarios': '',
        'category': 'best_practice',
    }
    
    # 提取标题（第一个#开头的行）
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        knowledge['title'] = title_match.group(1).strip()
    else:
        # 从文件名生成标题
        knowledge['title'] = Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
    
    # 提取摘要（查找"核心内容摘要"或"概述"部分）
    summary_patterns = [
        r'##\s*核心内容摘要\s*\n\n(.+?)(?=\n##|\Z)',
        r'##\s*概述\s*\n\n(.+?)(?=\n##|\Z)',
        r'##\s*1\.\s*.*?\n\n(.+?)(?=\n##|\Z)',
    ]
    
    for pattern in summary_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # 限制长度
            if len(summary) > 500:
                summary = summary[:497] + '...'
            knowledge['summary'] = summary
            break
    
    # 提取关键要点（查找列表项）
    key_points_section = re.search(r'##\s*(?:关键|核心|主要).*?\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if key_points_section:
        points_text = key_points_section.group(1)
        # 提取列表项
        list_items = re.findall(r'[-*]\s*(.+?)(?=\n[-*]|\n\n|\Z)', points_text, re.DOTALL)
        knowledge['key_points'] = [p.strip().replace('\n', ' ') for p in list_items[:5]]
    
    # 确定类别
    if 'factor' in file_path.lower() or '因子' in content:
        knowledge['category'] = 'factor'
    elif 'blueprint' in file_path.lower() or '蓝图' in content:
        knowledge['category'] = 'blueprint_decision'
    elif 'strategy' in file_path.lower() or '策略' in content:
        knowledge['category'] = 'strategy'
    
    return knowledge


def generate_ke_file(ke_number: int, file_path: str, content: str, commit_hash: str) -> str:
    """生成KE文件内容"""
    knowledge = extract_core_knowledge(content, file_path)
    
    # 确定layer
    layer = 'L01'  # 默认数据层
    if 'L03' in file_path or 'FACTOR' in file_path.upper() or 'factor' in file_path.lower():
        layer = 'L03'
    elif 'L02' in file_path:
        layer = 'L02'
    elif 'L04' in file_path:
        layer = 'L04'
    
    ke_content = f"""---
module_id: KE-{ke_number:03d}
title: "{knowledge['title']}"
category: {knowledge['category']}
source_file: "{file_path}"
source_git_deleted: true
original_path: "{file_path}"
deleted_in_commit: "{commit_hash}"
recovery_date: "{datetime.now().strftime('%Y-%m-%d')}"
extracted_date: "{datetime.now().strftime('%Y-%m-%d')}"
version: "1.0.0"
status: Active
layer: {layer}
owner: ZephyrAlpha-Owner
---

# {knowledge['title']}

## 核心内容摘要
{knowledge['summary'] or '（从git历史恢复的文件中提取的核心知识）'}

## 关键设计要点
"""
    
    if knowledge['key_points']:
        for i, point in enumerate(knowledge['key_points'], 1):
            ke_content += f"{i}. {point}\n"
    else:
        ke_content += "1. 该文件包含重要的技术规格和设计决策\n"
        ke_content += "2. 适用于Phase 2施工阶段参考\n"
        ke_content += "3. 具体内容请查看原始文件恢复命令\n"
    
    ke_content += f"""
## 适用场景
- Phase 2 施工中{layer}层的实现参考
- 相关模块的设计决策依据

## 原始文件
- 恢复命令：`git show {commit_hash}^:{file_path}`
"""
    
    return ke_content


def main():
    parser = argparse.ArgumentParser(description='Pipeline C 修复和提取脚本')
    parser.add_argument('--input-list', required=True, help='输入文件列表路径')
    parser.add_argument('--start', type=int, default=0, help='起始索引')
    parser.add_argument('--count', type=int, default=50, help='处理数量')
    parser.add_argument('--ke-start', type=int, default=44, help='KE起始编号')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际写入文件')
    
    args = parser.parse_args()
    
    # 读取文件列表
    with open(args.input_list, 'r', encoding='utf-8') as f:
        all_files = [line.strip() for line in f if line.strip()]
    
    # 选择要处理的文件
    files_to_process = all_files[args.start:args.start + args.count]
    
    print(f"将处理 {len(files_to_process)} 个文件（从索引 {args.start} 开始）")
    
    processed = 0
    extracted = 0
    failed = []
    
    for i, file_path in enumerate(files_to_process):
        print(f"\n[{i+1}/{len(files_to_process)}] 处理: {file_path}")
        
        # 从git历史获取内容
        content, commit_hash = get_file_from_git_history(file_path)
        
        if content is None:
            print(f"  ⚠️ 无法获取文件内容（可能不在git历史中）")
            failed.append(file_path)
            continue
        
        # 修复编码
        fixed_content = fix_encoding(content)
        
        # 检查内容质量
        if len(fixed_content.strip()) < 100:
            print(f"  ⚠️ 内容过少，跳过")
            continue
        
        # 生成KE文件
        ke_number = args.ke_start + extracted
        ke_content = generate_ke_file(ke_number, file_path, fixed_content, commit_hash)
        
        # 生成文件名
        file_name = Path(file_path).stem
        ke_file_name = f"KE-{ke_number:03d}-{file_name.lower()[:50]}.md"
        ke_file_path = KNOWLEDGE_DIR / ke_file_name
        
        if not args.dry_run:
            # 确保目录存在
            KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            
            # 写入KE文件
            with open(ke_file_path, 'w', encoding='utf-8') as f:
                f.write(ke_content)
            print(f"  ✅ 已创建: {ke_file_path}")
        else:
            print(f"  [试运行] 将创建: {ke_file_path}")
        
        extracted += 1
        processed += 1
    
    print(f"\n{'='*60}")
    print(f"处理完成:")
    print(f"  - 处理文件数: {processed}")
    print(f"  - 提取KE数: {extracted}")
    print(f"  - 失败数: {len(failed)}")
    if failed:
        print(f"  - 失败文件: {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
    print(f"  - 下一个KE编号: {args.ke_start + extracted}")
    
    return extracted


if __name__ == '__main__':
    extracted_count = main()
    sys.exit(0)
