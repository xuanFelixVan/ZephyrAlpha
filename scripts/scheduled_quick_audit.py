#!/usr/bin/env python3
"""
快速审计脚本
功能: 每周执行，检查链接有效性和元数据完整性
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from document_auditor import DocumentAuditor
from dataclasses import asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quick_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_quick_audit():
    """执行快速审计"""
    try:
        logger.info("开始快速审计...")
        
        auditor = DocumentAuditor(project_root='.')
        
        # 快速审计只检查链接和元数据
        files = auditor.scan_markdown_files()
        link_issues = auditor.check_links(files)
        
        # 生成简化报告
        results = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'scanned_files': len(files),
                'total_issues': len(auditor.issues),
                'issues_by_severity': {},
                'issues_by_type': {}
            },
            'details': {
                'link_issues': [asdict(issue) for issue in auditor.issues if issue.issue_type == 'broken_link']
            }
        }
        
        # 统计问题
        for issue in auditor.issues:
            results['summary']['issues_by_severity'][issue.severity] = \
                results['summary']['issues_by_severity'].get(issue.severity, 0) + 1
            results['summary']['issues_by_type'][issue.issue_type] = \
                results['summary']['issues_by_type'].get(issue.issue_type, 0) + 1
        
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/weekly_{timestamp}.json'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"快速审计完成，报告已保存到: {output_file}")
        
        if results['summary']['total_issues'] > 0:
            logger.warning(f"发现 {results['summary']['total_issues']} 个问题")
            send_notification(results)
        
        return 0
        
    except Exception as e:
        logger.error(f"快速审计失败: {str(e)}")
        return 1

def send_notification(results):
    """发送审计通知（可选）"""
    pass

if __name__ == '__main__':
    sys.exit(run_quick_audit())
