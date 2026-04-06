"""
文档质量监控机制
用途：建立持续监控机制，定期检查文档质量
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
AUDIT_STATE_DIR = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")


class DocumentQualityMonitor:
    """文档质量监控器"""
    
    def __init__(self):
        self.issues = []
        self.stats = {
            "total_documents": 0,
            "documents_with_issues": 0,
            "total_issues": 0,
            "compliance_rate": 0.0
        }
    
    def read_document(self, filepath: Path) -> str:
        """读取文档内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return ""
    
    def extract_yaml_header(self, content: str) -> dict:
        """提取YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            return {}
        
        yaml_content = yaml_match.group(1)
        yaml_dict = {}
        
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                yaml_dict[key.strip()] = value.strip().strip('"\'')
        
        return yaml_dict
    
    def check_document_quality(self, filepath: Path) -> List[Dict]:
        """检查单个文档质量"""
        issues = []
        content = self.read_document(filepath)
        
        if not content:
            return [{"type": "无法读取", "severity": "P0", "description": "文档无法读取"}]
        
        # 1. 检查YAML头部
        if not content.startswith('---'):
            issues.append({
                "type": "YAML头部缺失",
                "severity": "P1",
                "description": "文档缺少YAML头部"
            })
        else:
            yaml_header = self.extract_yaml_header(content)
            
            # 检查必要字段
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
            missing_fields = [f for f in required_fields if f not in yaml_header]
            if missing_fields:
                issues.append({
                    "type": "YAML字段缺失",
                    "severity": "P2",
                    "description": f"缺少字段: {', '.join(missing_fields)}"
                })
            
            # 检查Layer定位
            if not yaml_header.get('layer'):
                issues.append({
                    "type": "Layer定位缺失",
                    "severity": "P1",
                    "description": "文档缺少Layer定位"
                })
        
        # 2. 检查文档结构
        if not re.search(r'^#\s+', content, re.MULTILINE):
            issues.append({
                "type": "主标题缺失",
                "severity": "P2",
                "description": "文档缺少主标题"
            })
        
        # 3. 检查文档治理章节
        if '文档治理' not in content:
            issues.append({
                "type": "文档治理章节缺失",
                "severity": "P2",
                "description": "文档缺少文档治理章节"
            })
        
        # 4. 检查变更历史
        if '变更历史' not in content and '版本历史' not in content:
            issues.append({
                "type": "变更记录缺失",
                "severity": "P2",
                "description": "文档缺少变更历史记录"
            })
        
        # 5. 检查死链接
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        dead_links = []
        for text, link in links:
            if link.startswith('http') or link.startswith('#'):
                continue
            
            if link.startswith('../'):
                target_path = filepath.parent.parent / link.replace('../', '')
            else:
                target_path = filepath.parent / link
            
            if not target_path.exists():
                dead_links.append(link)
        
        if dead_links:
            issues.append({
                "type": "死链接",
                "severity": "P1",
                "description": f"发现 {len(dead_links)} 个死链接"
            })
        
        return issues
    
    def run_quality_check(self):
        """执行质量检查"""
        print("="*80)
        print("文档质量监控检查")
        print("="*80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 检查所有文档
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            self.stats["total_documents"] += 1
            
            issues = self.check_document_quality(filepath)
            
            if issues:
                self.stats["documents_with_issues"] += 1
                self.stats["total_issues"] += len(issues)
                
                for issue in issues:
                    self.issues.append({
                        "filename": filepath.name,
                        **issue
                    })
        
        # 计算合规率
        if self.stats["total_documents"] > 0:
            self.stats["compliance_rate"] = (
                (self.stats["total_documents"] - self.stats["documents_with_issues"]) 
                / self.stats["total_documents"] * 100
            )
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成监控报告"""
        report = []
        report.append("# 文档质量监控报告")
        report.append("")
        report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**检查范围**: {BLUEPRINTS_DIR}")
        report.append("")
        report.append("---")
        report.append("")
        report.append("## 📊 质量统计")
        report.append("")
        report.append(f"- **总文档数**: {self.stats['total_documents']}")
        report.append(f"- **有问题文档数**: {self.stats['documents_with_issues']}")
        report.append(f"- **总问题数**: {self.stats['total_issues']}")
        report.append(f"- **合规率**: {self.stats['compliance_rate']:.1f}%")
        report.append("")
        report.append("---")
        report.append("")
        
        # 按严重程度分组
        p0_issues = [i for i in self.issues if i['severity'] == 'P0']
        p1_issues = [i for i in self.issues if i['severity'] == 'P1']
        p2_issues = [i for i in self.issues if i['severity'] == 'P2']
        
        if p0_issues:
            report.append("## 🔴 P0级问题")
            report.append("")
            for issue in p0_issues:
                report.append(f"- **{issue['filename']}**: {issue['description']}")
            report.append("")
        
        if p1_issues:
            report.append("## 🟡 P1级问题")
            report.append("")
            for issue in p1_issues:
                report.append(f"- **{issue['filename']}**: {issue['type']} - {issue['description']}")
            report.append("")
        
        if p2_issues:
            report.append("## 🟢 P2级问题")
            report.append("")
            for issue in p2_issues:
                report.append(f"- **{issue['filename']}**: {issue['type']} - {issue['description']}")
            report.append("")
        
        # 保存报告
        report_path = AUDIT_STATE_DIR / f"quality_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(report))
        
        print(f"\n质量统计:")
        print(f"  总文档数: {self.stats['total_documents']}")
        print(f"  有问题文档数: {self.stats['documents_with_issues']}")
        print(f"  总问题数: {self.stats['total_issues']}")
        print(f"  合规率: {self.stats['compliance_rate']:.1f}%")
        print(f"\n报告已保存至: {report_path}")


def main():
    """主函数"""
    monitor = DocumentQualityMonitor()
    monitor.run_quality_check()


if __name__ == "__main__":
    main()
