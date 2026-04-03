#!/usr/bin/env python3
"""
智能链接修复脚本
功能: 根据审计报告自动修复损坏的链接，正确计算相对路径
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SmartLinkFixer:
    """智能链接修复器"""
    
    def __init__(self, project_root: str, audit_report: str):
        self.project_root = Path(project_root)
        self.audit_report = Path(audit_report)
        self.fixes: List[Dict] = []
        self.fixed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # 建立文件索引
        self.file_index = self._build_file_index()
        
    def _build_file_index(self) -> Dict[str, Path]:
        """建立文件名到路径的索引"""
        index = {}
        for md_file in self.project_root.rglob('*.md'):
            index[md_file.name] = md_file
        logger.info(f"已建立索引，共 {len(index)} 个Markdown文件")
        return index
    
    def load_audit_report(self) -> Dict:
        """加载审计报告"""
        with open(self.audit_report, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_target_file(self, target_name: str) -> Optional[Path]:
        """
        查找目标文件
        
        参数:
            target_name: 目标文件名
            
        返回:
            Path: 目标文件路径，如果找不到则返回None
        """
        return self.file_index.get(target_name)
    
    def calculate_relative_path(self, source_file: Path, target_file: Path) -> str:
        """
        计算从源文件到目标文件的相对路径
        
        参数:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        返回:
            str: 相对路径
        """
        try:
            # 计算相对路径
            relative_path = os.path.relpath(target_file, source_file.parent)
            # 统一使用正斜杠
            relative_path = relative_path.replace('\\', '/')
            return relative_path
        except Exception as e:
            logger.error(f"计算相对路径失败: {str(e)}")
            return None
    
    def fix_link_in_file(self, file_path: Path, old_link: str, new_link: str, line_number: int) -> bool:
        """
        在文件中修复链接
        
        参数:
            file_path: 文件路径
            old_link: 旧链接
            new_link: 新链接
            line_number: 行号
            
        返回:
            bool: 是否成功修复
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            if line_number > len(lines):
                logger.warning(f"行号超出范围: {file_path}:{line_number}")
                return False
            
            line = lines[line_number - 1]
            
            # 替换链接（支持Markdown链接格式）
            # 格式1: [text](link)
            pattern1 = rf'\[([^\]]+)\]\({re.escape(old_link)}\)'
            new_line = re.sub(pattern1, rf'[\1]({new_link})', line)
            
            # 格式2: 直接链接
            if new_line == line:
                new_line = line.replace(old_link, new_link)
            
            if new_line == line:
                logger.warning(f"未找到链接: {file_path}:{line_number} - {old_link}")
                return False
            
            lines[line_number - 1] = new_line
            
            # 写回文件
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.error(f"修复链接失败: {file_path} - {str(e)}")
            return False
    
    def analyze_and_fix_links(self):
        """分析并修复链接"""
        report = self.load_audit_report()
        issues = report['details']['link_issues']
        
        logger.info(f"开始分析 {len(issues)} 个损坏链接...")
        
        # 按文件分组
        issues_by_file = {}
        for issue in issues:
            file_path = issue['file_path']
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        logger.info(f"涉及 {len(issues_by_file)} 个文件")
        
        # 修复链接
        for file_path_str, file_issues in issues_by_file.items():
            file_path = self.project_root / file_path_str
            
            if not file_path.exists():
                logger.warning(f"文件不存在: {file_path}")
                self.skipped_count += len(file_issues)
                continue
            
            logger.info(f"\n处理文件: {file_path.name} ({len(file_issues)} 个问题)")
            
            for issue in file_issues:
                old_link = issue['message'].split(': ')[1]
                line_number = issue['line_number']
                
                # 提取目标文件名
                target_name = Path(old_link).name
                
                # 查找目标文件
                target_file = self.find_target_file(target_name)
                
                if target_file:
                    # 计算正确的相对路径
                    new_link = self.calculate_relative_path(file_path, target_file)
                    
                    if new_link:
                        # 修复链接
                        success = self.fix_link_in_file(file_path, old_link, new_link, line_number)
                        
                        if success:
                            self.fixed_count += 1
                            self.fixes.append({
                                'file': str(file_path),
                                'line': line_number,
                                'old_link': old_link,
                                'new_link': new_link,
                                'status': 'fixed'
                            })
                            logger.info(f"  ✓ 行{line_number}: {old_link} -> {new_link}")
                        else:
                            self.failed_count += 1
                            self.fixes.append({
                                'file': str(file_path),
                                'line': line_number,
                                'old_link': old_link,
                                'new_link': new_link,
                                'status': 'failed'
                            })
                    else:
                        self.failed_count += 1
                        self.fixes.append({
                            'file': str(file_path),
                            'line': line_number,
                            'old_link': old_link,
                            'new_link': None,
                            'status': 'path_error'
                        })
                else:
                    self.failed_count += 1
                    self.fixes.append({
                        'file': str(file_path),
                        'line': line_number,
                        'old_link': old_link,
                        'new_link': None,
                        'status': 'not_found'
                    })
                    logger.warning(f"  ✗ 行{line_number}: 未找到目标文件 - {target_name}")
    
    def generate_report(self, output_file: str):
        """生成修复报告"""
        report = {
            'summary': {
                'total_issues': len(self.fixes) + self.skipped_count,
                'fixed': self.fixed_count,
                'failed': self.failed_count,
                'skipped': self.skipped_count,
                'success_rate': f"{self.fixed_count / (len(self.fixes) + self.skipped_count) * 100:.1f}%" if (len(self.fixes) + self.skipped_count) > 0 else "0%"
            },
            'details': self.fixes
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"修复完成！")
        logger.info(f"{'='*60}")
        logger.info(f"总计: {report['summary']['total_issues']} 个问题")
        logger.info(f"成功: {report['summary']['fixed']} 个")
        logger.info(f"失败: {report['summary']['failed']} 个")
        logger.info(f"跳过: {report['summary']['skipped']} 个")
        logger.info(f"成功率: {report['summary']['success_rate']}")
        logger.info(f"\n修复报告已保存到: {output_file}")


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    audit_report = project_root / 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/weekly_20260402.json'
    output_report = project_root / 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/link_fix_report_20260402.json'
    
    fixer = SmartLinkFixer(str(project_root), str(audit_report))
    fixer.analyze_and_fix_links()
    fixer.generate_report(str(output_report))


if __name__ == '__main__':
    main()
