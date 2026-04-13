#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
处理剩余链接问题脚本
功能: 处理剩余的36个链接问题
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RemainingLinkFixer:
    """剩余链接修复器"""
    
    def __init__(self, project_root: str, audit_report: str):
        self.project_root = Path(project_root)
        self.audit_report = Path(audit_report)
        self.fixes: List[Dict] = []
        self.fixed_count = 0
        self.removed_count = 0
        self.failed_count = 0
        
    def load_audit_report(self) -> Dict:
        """加载审计报告"""
        with open(self.audit_report, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def fix_file_url_links(self, file_path: Path, line_number: int) -> bool:
        """
        修复file:///格式的链接
        
        参数:
            file_path: 文件路径
            line_number: 行号
            
        返回:
            bool: 是否成功修复
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            line = lines[line_number - 1]
            
            # 查找file:///格式的链接
            pattern = r'file:///[^)]+[/\\]([^/\\)]+\.md)'
            match = re.search(pattern, line)
            
            if match:
                target_name = match.group(1)
                # 查找目标文件
                target_file = None
                for md_file in self.project_root.rglob(target_name):
                    target_file = md_file
                    break
                
                if target_file:
                    # 计算相对路径
                    relative_path = os.path.relpath(target_file, file_path.parent)
                    relative_path = relative_path.replace('\\', '/')
                    
                    # 替换链接
                    old_link = match.group(0)
                    new_line = re.sub(pattern, relative_path, line)
                    
                    if new_line != line:
                        lines[line_number - 1] = new_line
                        new_content = '\n'.join(lines)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"修复file:///链接失败: {str(e)}")
            return False
    
    def remove_placeholder_links(self, file_path: Path, line_number: int) -> bool:
        """
        移除占位符链接
        
        参数:
            file_path: 文件路径
            line_number: 行号
            
        返回:
            bool: 是否成功移除
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            line = lines[line_number - 1]
            
            # 检查是否包含占位符
            if '{' in line and '}' in line:
                # 注释掉这一行
                new_line = f"<!-- 占位符链接已注释: {line.strip()} -->\n"
                lines[line_number - 1] = new_line
                
                new_content = '\n'.join(lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除占位符链接失败: {str(e)}")
            return False
    
    def comment_nonexistent_links(self, file_path: Path, line_number: int, target_link: str) -> bool:
        """
        注释掉不存在的链接
        
        参数:
            file_path: 文件路径
            line_number: 行号
            target_link: 目标链接
            
        返回:
            bool: 是否成功注释
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            line = lines[line_number - 1]
            
            # 注释掉包含目标链接的行
            if target_link in line:
                # 检查是否是Markdown链接
                pattern = rf'\[([^\]]+)\]\({re.escape(target_link)}\)'
                if re.search(pattern, line):
                    new_line = f"<!-- 链接目标不存在已注释: {line.strip()} -->\n"
                    lines[line_number - 1] = new_line
                    
                    new_content = '\n'.join(lines)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"注释链接失败: {str(e)}")
            return False
    
    def process_remaining_issues(self):
        """处理剩余问题"""
        report = self.load_audit_report()
        issues = report['details']['link_issues']
        
        logger.info(f"开始处理 {len(issues)} 个剩余链接问题...")
        
        for issue in issues:
            file_path = self.project_root / issue['file_path']
            line_number = issue['line_number']
            target_link = issue['message'].split(': ')[1]
            
            if not file_path.exists():
                logger.warning(f"文件不存在: {file_path}")
                self.failed_count += 1
                continue
            
            # 处理file:///格式的链接
            if target_link.startswith('file:///'):
                if self.fix_file_url_links(file_path, line_number):
                    self.fixed_count += 1
                    logger.info(f"✓ 修复file:///链接: {file_path.name}:{line_number}")
                    continue
            
            # 处理占位符链接
            if '{' in target_link and '}' in target_link:
                if self.remove_placeholder_links(file_path, line_number):
                    self.removed_count += 1
                    logger.info(f"✓ 移除占位符链接: {file_path.name}:{line_number}")
                    continue
            
            # 处理示例链接（如NEW_DOCUMENT.md）
            if 'NEW_DOCUMENT' in target_link or 'EXAMPLE' in target_link.upper():
                if self.comment_nonexistent_links(file_path, line_number, target_link):
                    self.removed_count += 1
                    logger.info(f"✓ 注释示例链接: {file_path.name}:{line_number}")
                    continue
            
            # 处理其他不存在的链接
            if self.comment_nonexistent_links(file_path, line_number, target_link):
                self.removed_count += 1
                logger.info(f"✓ 注释不存在链接: {file_path.name}:{line_number}")
            else:
                self.failed_count += 1
                logger.warning(f"✗ 处理失败: {file_path.name}:{line_number} - {target_link}")
    
    def generate_report(self, output_file: str):
        """生成修复报告"""
        report = {
            'summary': {
                'total_issues': len(self.fixes) + self.fixed_count + self.removed_count + self.failed_count,
                'fixed': self.fixed_count,
                'removed': self.removed_count,
                'failed': self.failed_count
            },
            'details': self.fixes
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"处理完成！")
        logger.info(f"{'='*60}")
        logger.info(f"修复: {report['summary']['fixed']} 个")
        logger.info(f"移除: {report['summary']['removed']} 个")
        logger.info(f"失败: {report['summary']['failed']} 个")
        logger.info(f"\n报告已保存到: {output_file}")


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    audit_report = project_root / 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/weekly_20260402.json'
    output_report = project_root / 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/remaining_link_fix_report_20260402.json'
    
    fixer = RemainingLinkFixer(str(project_root), str(audit_report))
    fixer.process_remaining_issues()
    fixer.generate_report(str(output_report))


if __name__ == '__main__':
    main()
