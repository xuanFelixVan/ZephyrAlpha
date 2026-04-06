"""
组合优化层深度审计脚本 V2
用途：全面审计组合优化层所有文档，重点检查重复和职责不清
创建时间：2026-04-07
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
OUTPUT_DIR = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")


class Layer6DeepAuditorV2:
    """组合优化层深度审计器 V2"""
    
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
        
        # 定义职责关键词映射
        self.responsibility_keywords = {
            "组合优化": ["PORTFOLIO_OPTIMIZATION", "MEAN_VARIANCE", "BLACK_LITTERMAN", "MULTI_OBJECTIVE"],
            "再平衡": ["REBALANCING", "TURNOVER_CONTROL", "TAX_LOSS_HARVESTING"],
            "风险管理": ["RISK_PARITY", "RISK_BUDGET", "VAR_ES", "STRESS_TESTING"],
            "约束管理": ["CONSTRAINT_MANAGEMENT", "PORTFOLIO_CONSTRAINT"],
            "绩效评估": ["PERFORMANCE_EVALUATION", "ATTRIBUTION", "SCENARIO_ANALYSIS"]
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
    
    def extract_content_sections(self, content: str) -> dict:
        """提取文档内容章节"""
        sections = {}
        
        # 提取主标题
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if title_match:
            sections['title'] = title_match.group(1).strip()
        
        # 提取核心职责
        responsibility_match = re.search(r'(?:核心职责|核心定位|职责描述)[:：]\s*(.+?)(?:\n|$)', content)
        if responsibility_match:
            sections['responsibility'] = responsibility_match.group(1).strip()
        
        # 提取概述内容
        overview_match = re.search(r'##\s*概述\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if overview_match:
            sections['overview'] = overview_match.group(1).strip()[:500]  # 限制长度
        
        # 提取设计目标
        goals_match = re.search(r'(?:设计目标|核心目标)[:：]\s*(.+?)(?:\n\n|\n##|\Z)', content, re.DOTALL)
        if goals_match:
            sections['goals'] = goals_match.group(1).strip()[:300]
        
        return sections
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        if not text1 or not text2:
            return 0.0
        
        # 提取关键词
        words1 = set(re.findall(r'\b\w{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b\w{3,}\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def check_l1_filesystem(self):
        """L1文件系统层审计"""
        print("L1 文件系统层审计...")
        
        # 1.1 目录结构问题
        print("  1.1 检查目录结构...")
        
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
        if len(md_files) < 10:
            self.l1_issues.append({
                "type": "目录稀疏",
                "severity": "P2",
                "description": f"组合优化层文件数量过少: {len(md_files)}个",
                "path": str(BLUEPRINTS_DIR)
            })
        
        # 1.2 文件命名问题
        print("  1.2 检查文件命名...")
        
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
        
        # 1.3 路径引用问题
        print("  1.3 检查路径引用...")
        
        for filepath in md_files:
            content = self.read_document(filepath)
            
            # 检查死链接
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            for link_text, link_path in links:
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                # 检查相对路径
                if link_path.startswith('../'):
                    # 计算实际路径
                    depth = link_path.count('../')
                    actual_path = filepath.parents[depth] / link_path.replace('../', '')
                    
                    if not actual_path.exists():
                        self.l1_issues.append({
                            "type": "死链接",
                            "severity": "P1",
                            "description": f"链接不存在: [{link_text}]({link_path})",
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
            sections = self.extract_content_sections(content)
            
            self.documents[filepath.name] = {
                "path": str(filepath),
                "yaml": yaml_data,
                "sections": sections,
                "content": content
            }
        
        # 2.1 职责驱动原则检查
        print("  2.1 检查职责驱动原则...")
        
        for filename, doc_info in self.documents.items():
            sections = doc_info['sections']
            
            # 检查是否有明确的职责描述
            if 'responsibility' not in sections and 'overview' not in sections:
                self.l2_issues.append({
                    "type": "职责不清",
                    "severity": "P1",
                    "description": f"文档缺少明确的职责描述",
                    "path": doc_info['path']
                })
            
            # 检查职责是否过于宽泛
            if 'responsibility' in sections:
                resp_text = sections['responsibility']
                if len(resp_text) < 20:
                    self.l2_issues.append({
                        "type": "职责描述过于简略",
                        "severity": "P2",
                        "description": f"职责描述过短: {resp_text}",
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
        
        # 2.3 版本隔离检查
        print("  2.3 检查版本隔离...")
        
        # 检查重复文档
        filenames = list(self.documents.keys())
        for i in range(len(filenames)):
            for j in range(i + 1, len(filenames)):
                file1 = filenames[i]
                file2 = filenames[j]
                
                content1 = self.documents[file1]['content']
                content2 = self.documents[file2]['content']
                
                similarity = self.calculate_similarity(content1, content2)
                
                if similarity > 0.7:  # 高相似度
                    self.duplicates.append({
                        "file1": file1,
                        "file2": file2,
                        "similarity": similarity,
                        "severity": "P0" if similarity > 0.9 else "P1"
                    })
        
        # 2.4 文档代码对应检查
        print("  2.4 检查文档代码对应...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            # 检查module_id是否存在
            if 'module_id' not in yaml_data:
                self.l2_issues.append({
                    "type": "module_id缺失",
                    "severity": "P1",
                    "description": f"文档缺少module_id字段",
                    "path": doc_info['path']
                })
    
    def check_l3_standards(self):
        """L3专业标准层审计"""
        print("L3 专业标准层审计...")
        
        # 3.1 五大原则符合性检查
        print("  3.1 检查五大原则符合性...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            sections = doc_info['sections']
            
            # 职责驱动原则
            if 'responsibility' not in sections:
                self.l3_issues.append({
                    "type": "职责驱动原则违反",
                    "severity": "P1",
                    "description": f"文档缺少核心职责描述",
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
            # 检查是否属于Layer 6
            is_layer6 = any(keyword in filename.upper() for keyword in self.layer6_keywords)
            
            if not is_layer6:
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
                
                # 检查编号格式
                if not re.match(r'^[A-Z_0-9]+_\d{3}$', module_id):
                    self.l3_issues.append({
                        "type": "编号不规范",
                        "severity": "P2",
                        "description": f"module_id格式不符合规范: {module_id}",
                        "path": doc_info['path']
                    })
                
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
            
            # 检查内容结构
            if '## 概述' not in content:
                self.l3_issues.append({
                    "type": "内容结构缺失",
                    "severity": "P2",
                    "description": f"文档缺少'概述'章节",
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
    
    def analyze_responsibility_clarity(self):
        """分析职责清晰度"""
        print("分析职责清晰度...")
        
        # 按职责关键词分组
        responsibility_groups = defaultdict(list)
        
        for filename, doc_info in self.documents.items():
            sections = doc_info['sections']
            content_upper = doc_info['content'].upper()
            
            # 检查每个职责关键词
            matched_responsibilities = []
            for resp_name, keywords in self.responsibility_keywords.items():
                for keyword in keywords:
                    if keyword in filename.upper() or keyword in content_upper:
                        matched_responsibilities.append(resp_name)
                        break
            
            # 如果匹配多个职责，可能存在职责不清
            if len(matched_responsibilities) > 1:
                self.responsibility_issues.append({
                    "type": "职责重叠",
                    "severity": "P1",
                    "description": f"文档涉及多个职责: {', '.join(set(matched_responsibilities))}",
                    "path": doc_info['path'],
                    "filename": filename
                })
            elif len(matched_responsibilities) == 0:
                self.responsibility_issues.append({
                    "type": "职责不明",
                    "severity": "P1",
                    "description": f"无法确定文档的核心职责",
                    "path": doc_info['path'],
                    "filename": filename
                })
            
            # 记录到分组
            for resp in matched_responsibilities:
                responsibility_groups[resp].append(filename)
        
        # 检查职责分散
        for resp_name, files in responsibility_groups.items():
            if len(files) > 5:  # 同一职责分散在超过5个文档
                self.responsibility_issues.append({
                    "type": "职责分散",
                    "severity": "P2",
                    "description": f"职责'{resp_name}'分散在{len(files)}个文档中",
                    "files": files
                })
    
    def generate_report(self) -> str:
        """生成审计报告"""
        print("生成审计报告...")
        
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        
        # 统计严重程度
        p0_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P0')
        p1_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P1')
        p2_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P2')
        
        report = f"""# 组合优化层深度审计报告 V2

**审计日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS  
**审计文档数**: {len(self.documents)}  
**Git备份分支**: backup/layer6-deep-audit-round2-20260407

---

## 📊 审计统计

- **总文档数**: {len(self.documents)}
- **总问题数**: {total_issues}
- **P0级问题**: {p0_count}个
- **P1级问题**: {p1_count}个
- **P2级问题**: {p2_count}个
- **重复文档**: {len(self.duplicates)}组
- **职责不清**: {len(self.responsibility_issues)}个

---

## 🔴 L1 文件系统层问题

"""
        
        # L1问题详情
        if self.l1_issues:
            for issue in self.l1_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n"
                report += f"- **路径**: {issue['path']}\n\n"
        else:
            report += "✅ 无L1文件系统层问题\n\n"
        
        report += "---\n\n## 🟡 L2 文档内容层问题\n\n"
        
        # L2问题详情
        if self.l2_issues:
            for issue in self.l2_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n"
                report += f"- **路径**: {issue['path']}\n\n"
        else:
            report += "✅ 无L2文档内容层问题\n\n"
        
        report += "---\n\n## 🟢 L3 专业标准层问题\n\n"
        
        # L3问题详情
        if self.l3_issues:
            for issue in self.l3_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n"
                report += f"- **路径**: {issue['path']}\n\n"
        else:
            report += "✅ 无L3专业标准层问题\n\n"
        
        report += "---\n\n## 🔄 重复文档分析\n\n"
        
        if self.duplicates:
            for dup in self.duplicates:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(dup['severity'], "⚪")
                report += f"### {severity_icon} 高相似度文档 ({dup['severity']})\n\n"
                report += f"- **文档1**: {dup['file1']}\n"
                report += f"- **文档2**: {dup['file2']}\n"
                report += f"- **相似度**: {dup['similarity']:.2%}\n\n"
        else:
            report += "✅ 无重复文档\n\n"
        
        report += "---\n\n## 📋 职责清晰度分析\n\n"
        
        if self.responsibility_issues:
            for issue in self.responsibility_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report += f"### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                report += f"- **描述**: {issue['description']}\n"
                if 'filename' in issue:
                    report += f"- **文档**: {issue['filename']}\n"
                if 'files' in issue:
                    report += f"- **相关文档**: {', '.join(issue['files'][:5])}"
                    if len(issue['files']) > 5:
                        report += f" (共{len(issue['files'])}个)"
                    report += "\n"
                report += "\n"
        else:
            report += "✅ 职责清晰\n\n"
        
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
            for i, issue in enumerate(p1_issues[:10], 1):  # 只显示前10个
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
            if len(p1_issues) > 10:
                report += f"... 还有{len(p1_issues) - 10}个P1级问题\n"
        else:
            report += "✅ 无P1级问题\n"
        
        report += "\n### 长期优化 (P2级)\n\n"
        
        p2_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P2']
        if p2_issues:
            for i, issue in enumerate(p2_issues[:5], 1):  # 只显示前5个
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
            if len(p2_issues) > 5:
                report += f"... 还有{len(p2_issues) - 5}个P2级问题\n"
        else:
            report += "✅ 无P2级问题\n"
        
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
        print("组合优化层深度审计 V2")
        print("="*80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {BLUEPRINTS_DIR}")
        print("="*80)
        
        # 执行三层审计
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        # 分析职责清晰度
        self.analyze_responsibility_clarity()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_file = OUTPUT_DIR / f"LAYER6_DEEP_AUDIT_V2_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8-sig') as f:
            f.write(report)
        
        print("\n" + "="*80)
        print("审计完成")
        print("="*80)
        print(f"总问题数: {len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)}")
        print(f"重复文档: {len(self.duplicates)}组")
        print(f"职责不清: {len(self.responsibility_issues)}个")
        print(f"报告已保存至: {report_file}")
        
        return {
            "l1_issues": len(self.l1_issues),
            "l2_issues": len(self.l2_issues),
            "l3_issues": len(self.l3_issues),
            "duplicates": len(self.duplicates),
            "responsibility_issues": len(self.responsibility_issues),
            "report_file": str(report_file)
        }


if __name__ == "__main__":
    auditor = Layer6DeepAuditorV2()
    result = auditor.run_audit()
    
    # 保存JSON结果
    json_file = OUTPUT_DIR / f"layer6_deep_audit_v2_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON结果已保存至: {json_file}")
