#!/usr/bin/env python3
"""
Layer 9文档治理自动化检查脚本 v2.0
功能：
1. 检查YAML头部数量（只检查文档开头）
2. 检查module_id唯一性
3. 检查必要字段完整性
4. 检查文档链接有效性
5. 生成检查报告
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class DocumentGovernanceChecker:
    """文档治理检查器"""
    
    def __init__(self, layer_path: str):
        self.layer_path = Path(layer_path)
        self.issues = []
        self.stats = {
            'total_docs': 0,
            'docs_with_issues': 0,
            'total_issues': 0,
            'p0_issues': 0,
            'p1_issues': 0,
            'p2_issues': 0
        }
    
    def check_all(self):
        """执行所有检查"""
        print("=" * 80)
        print("Layer 9文档治理自动化检查 v2.0")
        print("=" * 80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"检查路径: {self.layer_path}")
        print()
        
        # 1. 检查所有markdown文件
        md_files = list(self.layer_path.rglob("*.md"))
        self.stats['total_docs'] = len(md_files)
        
        print(f"📄 找到 {len(md_files)} 个文档文件")
        print()
        
        # 2. 检查每个文件
        for md_file in md_files:
            if '_archive' in str(md_file):
                continue  # 跳过归档文件
            
            self.check_document(md_file)
        
        # 3. 检查module_id唯一性
        self.check_module_id_uniqueness(md_files)
        
        # 4. 生成报告
        self.generate_report()
    
    def check_document(self, file_path: Path):
        """检查单个文档"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查YAML头部（只检查文档开头）
        yaml_headers = self.extract_yaml_headers(content)
        yaml_count = len(yaml_headers)
        
        if yaml_count > 1:
            self.add_issue(
                file_path=str(file_path.relative_to(self.layer_path.parent)),
                issue_type='YAML头部重复',
                description=f'发现{yaml_count}个YAML头部，应该只有1个',
                severity='P0',
                suggestion='删除多余的YAML头部，只保留一个'
            )
        elif yaml_count == 0:
            self.add_issue(
                file_path=str(file_path.relative_to(self.layer_path.parent)),
                issue_type='YAML头部缺失',
                description='文档缺少YAML头部',
                severity='P1',
                suggestion='添加标准YAML头部'
            )
        
        # 检查必要字段
        if yaml_count >= 1:
            yaml_content = yaml_headers[0]
            self.check_yaml_fields(file_path, yaml_content)
    
    def extract_yaml_headers(self, content: str) -> List[str]:
        """
        提取YAML头部（只检查文档开头）
        改进：只检查文档开头的第一个YAML头部，忽略文档中间的---
        """
        yaml_headers = []
        
        # 检查文档是否以---开头
        if not content.strip().startswith('---'):
            return yaml_headers
        
        # 分割文档为行
        lines = content.split('\n')
        
        # 查找第一个YAML头部
        in_yaml = False
        yaml_lines = []
        found_first_yaml = False
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml and not found_first_yaml:
                    # 开始第一个YAML头部
                    in_yaml = True
                    yaml_lines = []
                elif in_yaml:
                    # 结束第一个YAML头部
                    yaml_content = '\n'.join(yaml_lines)
                    yaml_headers.append(yaml_content)
                    found_first_yaml = True
                    in_yaml = False
                    break  # 找到第一个YAML头部后立即退出
            elif in_yaml:
                yaml_lines.append(line)
        
        return yaml_headers
    
    def check_yaml_fields(self, file_path: Path, yaml_content: str):
        """检查YAML字段完整性"""
        required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
        
        for field in required_fields:
            if field not in yaml_content:
                self.add_issue(
                    file_path=str(file_path.relative_to(self.layer_path.parent)),
                    issue_type=f'字段缺失',
                    description=f'YAML头部缺少必要字段: {field}',
                    severity='P1',
                    suggestion=f'添加字段: {field}'
                )
    
    def check_module_id_uniqueness(self, md_files: List[Path]):
        """检查module_id唯一性"""
        module_ids = {}
        
        for md_file in md_files:
            if '_archive' in str(md_file):
                continue
            
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            yaml_headers = self.extract_yaml_headers(content)
            if yaml_headers:
                match = re.search(r'module_id:\s*(.+)', yaml_headers[0])
                if match:
                    module_id = match.group(1).strip()
                    if module_id in module_ids:
                        self.add_issue(
                            file_path=str(md_file.relative_to(self.layer_path.parent)),
                            issue_type='module_id重复',
                            description=f'module_id "{module_id}" 与 {module_ids[module_id]} 重复',
                            severity='P0',
                            suggestion='修改module_id，确保唯一'
                        )
                    else:
                        module_ids[module_id] = str(md_file.relative_to(self.layer_path.parent))
    
    def add_issue(self, file_path: str, issue_type: str, description: str, 
                  severity: str, suggestion: str):
        """添加问题"""
        issue = {
            'file_path': file_path,
            'issue_type': issue_type,
            'description': description,
            'severity': severity,
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat()
        }
        self.issues.append(issue)
        self.stats['total_issues'] += 1
        
        if severity == 'P0':
            self.stats['p0_issues'] += 1
        elif severity == 'P1':
            self.stats['p1_issues'] += 1
        else:
            self.stats['p2_issues'] += 1
    
    def generate_report(self):
        """生成检查报告"""
        print("=" * 80)
        print("检查结果汇总")
        print("=" * 80)
        print()
        
        # 统计信息
        print("📊 统计信息:")
        print(f"  - 检查文档数: {self.stats['total_docs']}")
        print(f"  - 发现问题数: {self.stats['total_issues']}")
        print(f"  - P0级问题: {self.stats['p0_issues']}")
        print(f"  - P1级问题: {self.stats['p1_issues']}")
        print(f"  - P2级问题: {self.stats['p2_issues']}")
        print()
        
        # 合规率计算
        if self.stats['total_docs'] > 0:
            compliance_rate = (self.stats['total_docs'] - len(set(issue['file_path'] for issue in self.issues))) / self.stats['total_docs'] * 100
        else:
            compliance_rate = 100
        
        print(f"✅ 文档治理合规率: {compliance_rate:.1f}%")
        print()
        
        # 问题列表
        if self.issues:
            print("=" * 80)
            print("问题列表")
            print("=" * 80)
            print()
            
            for i, issue in enumerate(self.issues, 1):
                print(f"问题 #{i} [{issue['severity']}]")
                print(f"  文件: {issue['file_path']}")
                print(f"  类型: {issue['issue_type']}")
                print(f"  描述: {issue['description']}")
                print(f"  建议: {issue['suggestion']}")
                print()
        else:
            print("✅ 未发现问题，文档治理状态良好！")
        
        # 保存报告
        self.save_report(compliance_rate)
    
    def save_report(self, compliance_rate: float):
        """保存报告到文件"""
        report_dir = self.layer_path / "maintenance_records"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'check_time': datetime.now().isoformat(),
            'layer_path': str(self.layer_path),
            'stats': self.stats,
            'compliance_rate': compliance_rate,
            'issues': self.issues
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 检查报告已保存: {report_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 9文档治理自动化检查')
    parser.add_argument('--layer', type=str, default='9', help='Layer编号')
    parser.add_argument('--path', type=str, default=None, help='自定义检查路径')
    
    args = parser.parse_args()
    
    # 确定检查路径
    if args.path:
        layer_path = args.path
    else:
        layer_path = Path(__file__).parent.parent / "docs" / f"09_RESEARCH_INNOVATION"
    
    # 执行检查
    checker = DocumentGovernanceChecker(layer_path)
    checker.check_all()


if __name__ == '__main__':
    main()
