#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
深度审计脚本
功能: 每季度执行,执行三层审计（L1-L3）和五大原则符合性检查
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from document_auditor import DocumentAuditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deep_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_deep_audit():
    """执行深度审计"""
    try:
        logger.info("开始深度审计...")
        
        auditor = DocumentAuditor(project_root='.')
        
        # 执行完整审计
        results = auditor.run_full_audit()
        
        # 添加层级信息
        results['summary']['audit_type'] = 'deep_audit'
        results['summary']['l1_issues'] = len([i for i in auditor.issues if i.issue_type in ['non_standard_category', 'naming_violation']])
        results['summary']['l2_issues'] = len([i for i in auditor.issues if i.issue_type in ['missing_metadata', 'inconsistent_version']])
        results['summary']['l3_issues'] = len([i for i in auditor.issues if i.issue_type in ['broken_link']])
        
        # 重新组织结果
        results['l1_results'] = {'issues': [asdict(i) for i in auditor.issues if i.issue_type in ['non_standard_category', 'naming_violation']]}
        results['l2_results'] = {'issues': [asdict(i) for i in auditor.issues if i.issue_type in ['missing_metadata', 'inconsistent_version']]}
        results['l3_results'] = {'issues': [asdict(i) for i in auditor.issues if i.issue_type in ['broken_link']]}
        
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/quarterly_{timestamp}.json'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"深度审计完成，报告已保存到: {output_file}")
        
        generate_detailed_report(results, timestamp)
        
        return 0
        
    except Exception as e:
        logger.error(f"深度审计失败: {str(e)}")
        return 1

def generate_detailed_report(results, timestamp):
    """生成详细审计报告"""
    report_file = f'docs/09_AUDIT/REPORTS/QUARTERLY_AUDIT_REPORT_{timestamp}.md'
    
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 季度文档治理审计报告\n\n")
        f.write(f"**审计时间**: {results['summary']['scan_time']}\n")
        f.write(f"**审计类型**: 深度审计\n\n")
        
        f.write(f"## 审计概要\n\n")
        f.write(f"| 审计层级 | 问题数量 |\n")
        f.write(f"|---------|---------|\n")
        f.write(f"| L1文件系统层 | {results['summary']['l1_issues']} |\n")
        f.write(f"| L2文档内容层 | {results['summary']['l2_issues']} |\n")
        f.write(f"| L3专业标准层 | {results['summary']['l3_issues']} |\n")
        f.write(f"| **总计** | **{results['summary']['total_issues']}** |\n\n")
        
        if results['l1_results'].get('issues'):
            f.write(f"## L1文件系统层审计结果\n\n")
            for issue in results['l1_results']['issues']:
                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")
        
        if results['l2_results'].get('issues'):
            f.write(f"\n## L2文档内容层审计结果\n\n")
            for issue in results['l2_results']['issues']:
                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")
        
        if results['l3_results'].get('issues'):
            f.write(f"\n## L3专业标准层审计结果\n\n")
            for issue in results['l3_results']['issues']:
                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")

if __name__ == '__main__':
    sys.exit(run_deep_audit())
