# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
优化版组合优化层深度审计脚本 V3
用途：优化职责检查逻辑，同时检查YAML头部和文档内容
创建时间：2026-04-07
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
OUTPUT_DIR = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")


class Layer6DeepAuditorV3:
    """组合优化层深度审计器 V3 - 优化职责检查"""
    
    def __init__(self):
        self.l1_issues = []  # 文件系统层问题
        self.l2_issues = []  # 文档内容层问题
        self.l3_issues = []  # 专业标准层问题
        self.documents = {}  # 文档信息存储
        self.duplicates = []  # 重复文档
        self.responsibility_issues = []  # 职责不清问题
        
        # 定义Layer 6关键词
        self.layer6_keywords = [
            "PORTFOLIO", "OPTIMIZATION", "REBALANCING", "RISK_PARITY",
            "BLACK_LITTERMAN", "MEAN_VARIANCE", "CONSTRAINT", "ATTRIBUTION",
            "PERFORMANCE", "TURNOVER", "TAX_LOSS", "SCENARIO"
        ]
    
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
    
    def extract_yaml(self, content: str) -> dict:
        """提取YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            yaml_data = {}
            
            # 提取各个字段
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_data[key.strip()] = value.strip().strip('"\'')
            
            return yaml_data
        return {}
    
    def has_responsibility_in_yaml(self, yaml_data: dict) -> bool:
        """检查YAML头部是否有responsibility字段"""
        return 'responsibility' in yaml_data and yaml_data['responsibility']
    
    def has_responsibility_in_content(self, content: str) -> bool:
        """检查文档内容是否有职责描述"""
        # 检查是否有"核心职责"、"核心定位"、"职责描述"等关键词
        patterns = [
            r'核心职责[:：]\s*(.+?)(?:\n|$)',
            r'核心定位[:：]\s*(.+?)(?:\n|$)',
            r'职责描述[:：]\s*(.+?)(?:\n|$)',
            r'##\s*核心职责',
            r'##\s*职责'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def check_l1_filesystem(self):
        """L1文件系统层审计"""
        print("L1 文件系统层审计...")
        
        # 检查目录是否存在
        if not BLUEPRINTS_DIR.exists():
            self.l1_issues.append({
                "type": "目录缺失",
                "severity": "P0",
                "description": f"组合优化层目录不存在: {BLUEPRINTS_DIR}",
                "path": str(BLUEPRINTS_DIR)
            })
            return
        
        # 统计文件数量
        md_files = list(BLUEPRINTS_DIR.glob("*.md"))
        
        # 检查文件命名
        for filepath in md_files:
            filename = filepath.name
            
            # 检查是否包含旧架构命名
            if re.search(r'Layer\s*[0-9]', filename):
                self.l1_issues.append({
                    "type": "旧架构命名残留",
                    "severity": "P1",
                    "description": f"文件名包含旧架构关键词: {filename}",
                    "path": str(filepath)
                })
            
            # 检查命名规范
            if not re.match(r'^[A-Z_0-9]+_BLUEPRINT\.md$', filename) and filename != "INDEX.md":
                self.l1_issues.append({
                    "type": "命名不规范",
                    "severity": "P2",
                    "description": f"文件名不符合蓝图命名规范: {filename}",
                    "path": str(filepath)
                })
    
    def check_l2_content(self):
        """L2文档内容层审计"""
        print("L2 文档内容层审计...")
        
        # 收集所有文档信息
        print("  收集文档信息...")
        
        md_files = list(BLUEPRINTS_DIR.glob("*.md"))
        
        for filepath in md_files:
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            yaml_data = self.extract_yaml(content)
            
            self.documents[filepath.name] = {
                "path": str(filepath),
                "yaml": yaml_data,
                "content": content,
                "has_yaml_responsibility": self.has_responsibility_in_yaml(yaml_data),
                "has_content_responsibility": self.has_responsibility_in_content(content)
            }
        
        # 2.1 职责驱动原则检查（优化版）
        print("  2.1 检查职责驱动原则（优化版）...")
        
        for filename, doc_info in self.documents.items():
            # 同时检查YAML头部和文档内容
            has_yaml_resp = doc_info['has_yaml_responsibility']
            has_content_resp = doc_info['has_content_responsibility']
            
            if not has_yaml_resp and not has_content_resp:
                self.l2_issues.append({
                    "type": "职责不清",
                    "severity": "P1",
                    "description": f"文档缺少职责描述（YAML和内容均无）",
                    "path": doc_info['path']
                })
            elif not has_yaml_resp:
                self.l2_issues.append({
                    "type": "YAML职责缺失",
                    "severity": "P2",
                    "description": f"YAML头部缺少responsibility字段",
                    "path": doc_info['path']
                })
            elif not has_content_resp:
                self.l2_issues.append({
                    "type": "内容职责缺失",
                    "severity": "P2",
                    "description": f"文档内容缺少职责描述章节",
                    "path": doc_info['path']
                })
        
        # 2.2 索引完备性检查
        print("  2.2 检查索引完备性...")
        
        index_file = BLUEPRINTS_DIR / "INDEX.md"
        if not index_file.exists():
            self.l2_issues.append({
                "type": "索引缺失",
                "severity": "P1",
                "description": "组合优化层缺少INDEX.md索引文件",
                "path": str(BLUEPRINTS_DIR)
            })
        else:
            index_content = self.read_document(index_file)
            
            # 检查索引是否包含所有文档
            for filename in self.documents.keys():
                if filename not in index_content:
                    self.l2_issues.append({
                        "type": "索引不完整",
                        "severity": "P2",
                        "description": f"索引未包含文档: {filename}",
                        "path": str(index_file)
                    })
    
    def check_l3_standards(self):
        """L3专业标准层审计"""
        print("L3 专业标准层审计...")
        
        # 3.1 五大原则符合性检查
        print("  3.1 检查五大原则符合性...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            # 职责驱动原则（优化版）
            if not doc_info['has_yaml_responsibility'] and not doc_info['has_content_responsibility']:
                self.l3_issues.append({
                    "type": "职责驱动原则违反",
                    "severity": "P1",
                    "description": f"文档缺少职责描述",
                    "path": doc_info['path']
                })
            
            # 版本隔离原则
            if 'version' not in yaml_data:
                self.l3_issues.append({
                    "type": "版本隔离原则违反",
                    "severity": "P2",
                    "description": f"文档缺少版本号",
                    "path": doc_info['path']
                })
            
            # 命名规范原则
            if 'module_id' not in yaml_data:
                self.l3_issues.append({
                    "type": "命名规范原则违反",
                    "severity": "P1",
                    "description": f"文档缺少module_id",
                    "path": doc_info['path']
                })
        
        # 3.2 文档分类检查
        print("  3.2 检查文档分类...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            # 检查layer字段
            if 'layer' in yaml_data:
                layer = yaml_data['layer']
                # 检查是否属于Layer 6
                is_layer6 = any(keyword in filename.upper() for keyword in self.layer6_keywords)
                
                if not is_layer6 and "Layer 6" in layer:
                    self.l3_issues.append({
                        "type": "分类错误",
                        "severity": "P2",
                        "description": f"文档可能不属于组合优化层",
                        "path": doc_info['path']
                    })
        
        # 3.3 编号体系检查
        print("  3.3 检查编号体系...")
        
        module_ids = []
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            if 'module_id' in yaml_data:
                module_id = yaml_data['module_id']
                
                # 检查编号重复
                if module_id in module_ids:
                    self.l3_issues.append({
                        "type": "编号重复",
                        "severity": "P0",
                        "description": f"module_id重复: {module_id}",
                        "path": doc_info['path']
                    })
                else:
                    module_ids.append(module_id)
        
        # 3.4 文档质量检查
        print("  3.4 检查文档质量...")
        
        for filename, doc_info in self.documents.items():
            content = doc_info['content']
            yaml_data = doc_info['yaml']
            
            # 检查YAML字段完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
            for field in required_fields:
                if field not in yaml_data:
                    self.l3_issues.append({
                        "type": "YAML字段缺失",
                        "severity": "P1",
                        "description": f"YAML缺少必要字段: {field}",
                        "path": doc_info['path']
                    })
            
            # 检查变更记录
            if '变更历史' not in content and '变更记录' not in content:
                self.l3_issues.append({
                    "type": "变更记录缺失",
                    "severity": "P2",
                    "description": f"文档缺少变更历史记录",
                    "path": doc_info['path']
                })
    
    def generate_report(self) -> str:
        """生成审计报告"""
        print("生成审计报告...")
        
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        
        # 统计严重程度
        p0_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P0')
        p1_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P1')
        p2_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P2')
        
        # 统计职责清晰度
        yaml_resp_count = sum(1 for doc in self.documents.values() if doc['has_yaml_responsibility'])
        content_resp_count = sum(1 for doc in self.documents.values() if doc['has_content_responsibility'])
        both_resp_count = sum(1 for doc in self.documents.values() 
                             if doc['has_yaml_responsibility'] and doc['has_content_responsibility'])
        
        report = f"""# 组合优化层深度审计报告 V3（优化版）

**审计日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS  
**审计文档数**: {len(self.documents)}  
**Git备份分支**: backup/responsibility-clarity-optimization-20260407

---

## 📊 审计统计

- **总文档数**: {len(self.documents)}
- **总问题数**: {total_issues}
- **P0级问题**: {p0_count}个
- **P1级问题**: {p1_count}个
- **P2级问题**: {p2_count}个

---

## 📋 职责清晰度统计（优化版）

- **YAML头部有职责**: {yaml_resp_count}个文档 ({yaml_resp_count/len(self.documents)*100:.1f}%)
- **内容有职责描述**: {content_resp_count}个文档 ({content_resp_count/len(self.documents)*100:.1f}%)
- **两者都有**: {both_resp_count}个文档 ({both_resp_count/len(self.documents)*100:.1f}%)

---

## 🔴 L1 文件系统层问题

"""
        
        # L1问题详情
        if self.l1_issues:
            for issue in self.l1_issues[:10]:  # 只显示前10个
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n"
                report += f"- **路径**: {issue['path']}\n\n"
            
            if len(self.l1_issues) > 10:
                report += f"... 还有{len(self.l1_issues) - 10}个L1问题\n\n"
        else:
            report += "✅ 无L1文件系统层问题\n\n"
        
        report += "---\n\n## 🟡 L2 文档内容层问题\n\n"
        
        # L2问题详情（重点显示职责问题）
        responsibility_issues = [issue for issue in self.l2_issues if '职责' in issue['type']]
        other_l2_issues = [issue for issue in self.l2_issues if '职责' not in issue['type']]
        
        if responsibility_issues:
            report += "### 职责相关问题\n\n"
            for issue in responsibility_issues[:10]:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"#### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n\n"
            
            if len(responsibility_issues) > 10:
                report += f"... 还有{len(responsibility_issues) - 10}个职责相关问题\n\n"
        
        if other_l2_issues:
            report += "### 其他L2问题\n\n"
            for issue in other_l2_issues[:5]:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"#### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n\n"
        
        if not self.l2_issues:
            report += "✅ 无L2文档内容层问题\n\n"
        
        report += "---\n\n## 🟢 L3 专业标准层问题\n\n"
        
        # L3问题详情
        if self.l3_issues:
            for issue in self.l3_issues[:10]:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n\n"
            
            if len(self.l3_issues) > 10:
                report += f"... 还有{len(self.l3_issues) - 10}个L3问题\n\n"
        else:
            report += "✅ 无L3专业标准层问题\n\n"
        
        report += f"""---

## 📈 改进建议

### 立即修复 (P0级)

"""
        
        p0_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P0']
        if p0_issues:
            for i, issue in enumerate(p0_issues, 1):
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
        else:
            report += "✅ 无P0级问题\n"
        
        report += "\n### 短期改进 (P1级)\n\n"
        
        p1_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P1']
        if p1_issues:
            for i, issue in enumerate(p1_issues[:10], 1):
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
            if len(p1_issues) > 10:
                report += f"... 还有{len(p1_issues) - 10}个P1级问题\n"
        else:
            report += "✅ 无P1级问题\n"
        
        report += f"""

---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计执行人**: Audit Sentinel  
**审计状态**: ✅ 完成
"""
        
        return report
    
    def run_audit(self):
        """执行完整审计"""
        print("="*80)
        print("组合优化层深度审计 V3（优化版）")
        print("="*80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {BLUEPRINTS_DIR}")
        print("="*80)
        
        # 执行三层审计
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_file = OUTPUT_DIR / f"LAYER6_DEEP_AUDIT_V3_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8-sig') as f:
            f.write(report)
        
        print("\n" + "="*80)
        print("审计完成")
        print("="*80)
        print(f"总问题数: {len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)}")
        print(f"报告已保存至: {report_file}")
        
        return {
            "l1_issues": len(self.l1_issues),
            "l2_issues": len(self.l2_issues),
            "l3_issues": len(self.l3_issues),
            "report_file": str(report_file)
        }


if __name__ == "__main__":
    auditor = Layer6DeepAuditorV3()
    result = auditor.run_audit()
    
    # 保存JSON结果
    json_file = OUTPUT_DIR / f"layer6_deep_audit_v3_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON结果已保存至: {json_file}")
