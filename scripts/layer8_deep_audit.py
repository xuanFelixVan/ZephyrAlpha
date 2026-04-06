"""
Layer 8 人机交互层全面深度审计脚本
用途：按照专业量化机构五大原则和三层审计标准进行全面审计
创建时间：2026-04-07
"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

LAYER8_DIR = Path("docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")


class Layer8DeepAuditor:
    """Layer 8 人机交互层全面深度审计器"""
    
    def __init__(self):
        # L1 文件系统层问题
        self.l1_issues = {
            "目录结构问题": [],
            "文件命名问题": [],
            "路径引用问题": []
        }
        
        # L2 文档内容层问题
        self.l2_issues = {
            "职责驱动原则问题": [],
            "索引完备性问题": [],
            "版本隔离问题": [],
            "文档代码对应问题": []
        }
        
        # L3 专业标准层问题
        self.l3_issues = {
            "五大原则符合性问题": [],
            "文档分类问题": [],
            "编号体系问题": [],
            "文档质量问题": []
        }
        
        # 文档信息存储
        self.documents = {}
        self.duplicates = []
        self.content_hashes = {}
        
        # Layer 8 关键词
        self.layer8_keywords = [
            "MONITORING", "ALERTING", "AUTH", "API", "BACKTEST", "REPORTING",
            "AUDIT", "MOBILE", "TRADING", "CONFIG", "USER", "SYSTEM", "DATA",
            "STRATEGY", "PERMISSION", "RATE_LIMITING", "DOCUMENTATION", "KNOWLEDGE",
            "CI_CD", "BACKUP", "RESEARCH", "PARAMETER", "LIVE_TRADING", "INTERFACE"
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
            
            current_key = None
            current_value = []
            
            for line in yaml_content.split('\n'):
                if ':' in line and not line.startswith(' '):
                    if current_key:
                        yaml_data[current_key] = '\n'.join(current_value).strip()
                    current_key, value = line.split(':', 1)
                    current_value = [value.strip().strip('"\'')]
                elif line.startswith(' ') and current_key:
                    current_value.append(line.strip())
            
            if current_key:
                yaml_data[current_key] = '\n'.join(current_value).strip()
            
            return yaml_data
        return {}
    
    def compute_content_hash(self, content: str) -> str:
        """计算内容哈希，用于检测重复"""
        # 移除YAML头部和空白字符
        clean_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        clean_content = re.sub(r'\s+', ' ', clean_content)
        return hashlib.md5(clean_content.encode()).hexdigest()
    
    def check_l1_filesystem(self):
        """L1 文件系统层审计"""
        print("L1 文件系统层审计...")
        
        # 1.1 目录结构问题
        print("  1.1 检查目录结构问题...")
        
        # 检查目录是否存在
        if not LAYER8_DIR.exists():
            self.l1_issues["目录结构问题"].append({
                "type": "目录缺失",
                "severity": "P0",
                "description": f"Layer 8 人机交互层目录不存在: {LAYER8_DIR}",
                "path": str(LAYER8_DIR)
            })
            return
        
        # 检查子目录
        subdirs = [item for item in LAYER8_DIR.iterdir() if item.is_dir()]
        
        for subdir in subdirs:
            # 检查目录稀疏（文件数<3）
            files_in_dir = list(subdir.glob("*.md"))
            if len(files_in_dir) < 2:
                self.l1_issues["目录结构问题"].append({
                    "type": "目录稀疏",
                    "severity": "P2",
                    "description": f"目录文件过少（{len(files_in_dir)}个），应整合",
                    "path": str(subdir)
                })
            
            # 检查目录层级过深
            depth = len(subdir.relative_to(LAYER8_DIR).parts)
            if depth > 2:
                self.l1_issues["目录结构问题"].append({
                    "type": "目录层级过深",
                    "severity": "P2",
                    "description": f"嵌套超过2层，难以导航",
                    "path": str(subdir)
                })
            
            # 检查目录命名规范
            if not re.match(r'^\d{2}_[A-Z_]+$', subdir.name):
                self.l1_issues["目录结构问题"].append({
                    "type": "目录命名不规范",
                    "severity": "P2",
                    "description": f"目录命名不符合专业命名标准",
                    "path": str(subdir)
                })
        
        # 1.2 文件命名问题
        print("  1.2 检查文件命名问题...")
        
        md_files = list(LAYER8_DIR.glob("**/*.md"))
        
        for filepath in md_files:
            filename = filepath.name
            
            # 检查旧架构命名残留
            if re.search(r'Layer\s*[0-9]', filename):
                self.l1_issues["文件命名问题"].append({
                    "type": "旧架构命名残留",
                    "severity": "P1",
                    "description": f"文件名包含旧架构关键词: {filename}",
                    "path": str(filepath)
                })
            
            # 检查命名规范
            if filename != "INDEX.md" and filename != "index.md":
                if not re.match(r'^[A-Z_0-9]+_BLUEPRINT\.md$', filename):
                    self.l1_issues["文件命名问题"].append({
                        "type": "命名不规范",
                        "severity": "P2",
                        "description": f"文件名不符合蓝图命名规范: {filename}",
                        "path": str(filepath)
                    })
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', filename):
                self.l1_issues["文件命名问题"].append({
                    "type": "特殊字符问题",
                    "severity": "P2",
                    "description": f"文件名包含空格或中文: {filename}",
                    "path": str(filepath)
                })
        
        # 1.3 路径引用问题
        print("  1.3 检查路径引用问题...")
        
        for filepath in md_files:
            content = self.read_document(filepath)
            if not content:
                continue
            
            # 检查路径冗余（过多../）
            redundant_paths = re.findall(r'\.\./\.\./\.\./', content)
            if redundant_paths:
                self.l1_issues["路径引用问题"].append({
                    "type": "路径冗余",
                    "severity": "P2",
                    "description": f"使用过多 ../ 相对路径",
                    "path": str(filepath)
                })
            
            # 检查绝对路径硬编码
            absolute_paths = re.findall(r'[A-Z]:\\[A-Za-z_0-9\\]+', content)
            if absolute_paths:
                self.l1_issues["路径引用问题"].append({
                    "type": "绝对路径硬编码",
                    "severity": "P2",
                    "description": f"使用绝对路径而非相对路径",
                    "path": str(filepath)
                })
    
    def check_l2_content(self):
        """L2 文档内容层审计"""
        print("L2 文档内容层审计...")
        
        # 收集所有文档信息
        print("  收集文档信息...")
        
        md_files = list(LAYER8_DIR.glob("**/*.md"))
        
        for filepath in md_files:
            content = self.read_document(filepath)
            if not content:
                continue
            
            yaml_data = self.extract_yaml(content)
            content_hash = self.compute_content_hash(content)
            
            self.documents[filepath.name] = {
                "path": str(filepath),
                "yaml": yaml_data,
                "content": content,
                "content_hash": content_hash
            }
            
            # 检测重复文档
            if content_hash in self.content_hashes:
                self.duplicates.append({
                    "file1": self.content_hashes[content_hash],
                    "file2": filepath.name,
                    "hash": content_hash
                })
            else:
                self.content_hashes[content_hash] = filepath.name
        
        # 2.1 职责驱动原则问题
        print("  2.1 检查职责驱动原则问题...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            content = doc_info['content']
            
            # 检查职责描述
            has_responsibility = 'responsibility' in yaml_data and yaml_data['responsibility']
            has_core_duty = bool(re.search(r'核心职责|核心定位|职责描述', content))
            
            if not has_responsibility and not has_core_duty:
                self.l2_issues["职责驱动原则问题"].append({
                    "type": "职责不清",
                    "severity": "P1",
                    "description": f"文档缺少职责描述（YAML和内容均无）",
                    "path": doc_info['path']
                })
            elif not has_responsibility:
                self.l2_issues["职责驱动原则问题"].append({
                    "type": "YAML职责缺失",
                    "severity": "P2",
                    "description": f"YAML头部缺少responsibility字段",
                    "path": doc_info['path']
                })
        
        # 检查职责重叠
        responsibility_map = defaultdict(list)
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            if 'responsibility' in yaml_data:
                responsibility_map[yaml_data['responsibility']].append(filename)
        
        for responsibility, files in responsibility_map.items():
            if len(files) > 1:
                self.l2_issues["职责驱动原则问题"].append({
                    "type": "职责重叠",
                    "severity": "P1",
                    "description": f"多个文档承担相同职责: {', '.join(files)}",
                    "path": "多个文件"
                })
        
        # 检查重复文档
        for dup in self.duplicates:
            self.l2_issues["职责驱动原则问题"].append({
                "type": "重复文档",
                "severity": "P1",
                "description": f"文档内容重复: {dup['file1']} 与 {dup['file2']}",
                "path": dup['file1']
            })
        
        # 2.2 索引完备性问题
        print("  2.2 检查索引完备性问题...")
        
        # 检查主索引
        main_index = LAYER8_DIR / "index.md"
        if not main_index.exists():
            self.l2_issues["索引完备性问题"].append({
                "type": "入口混乱",
                "severity": "P1",
                "description": "Layer 8 人机交互层缺少INDEX.md主入口",
                "path": str(LAYER8_DIR)
            })
        else:
            index_content = self.read_document(main_index)
            
            # 检查索引是否包含所有文档
            for filename in self.documents.keys():
                if filename not in index_content and filename != "index.md":
                    self.l2_issues["索引完备性问题"].append({
                        "type": "索引不完整",
                        "severity": "P2",
                        "description": f"主索引未包含文档: {filename}",
                        "path": str(main_index)
                    })
        
        # 检查子目录索引
        for subdir in LAYER8_DIR.iterdir():
            if subdir.is_dir():
                subdir_index = subdir / "INDEX.md"
                if not subdir_index.exists():
                    self.l2_issues["索引完备性问题"].append({
                        "type": "子目录缺索引",
                        "severity": "P2",
                        "description": f"子目录缺少INDEX.md导航文件",
                        "path": str(subdir)
                    })
        
        # 2.3 版本隔离问题
        print("  2.3 检查版本隔离问题...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            content = doc_info['content']
            
            # 检查版本标识
            if 'version' not in yaml_data:
                self.l2_issues["版本隔离问题"].append({
                    "type": "版本标识缺失",
                    "severity": "P2",
                    "description": f"文档缺少版本号",
                    "path": doc_info['path']
                })
            
            # 检查变更记录
            if '变更历史' not in content and '变更记录' not in content:
                self.l2_issues["版本隔离问题"].append({
                    "type": "变更记录缺失",
                    "severity": "P2",
                    "description": f"文档缺少变更历史记录",
                    "path": doc_info['path']
                })
        
        # 2.4 文档代码对应问题
        print("  2.4 检查文档代码对应问题...")
        
        # 检查文档是否描述了不存在的模块
        for filename, doc_info in self.documents.items():
            content = doc_info['content']
            
            # 检查是否有明确的模块路径引用
            module_refs = re.findall(r'src/([a-z_/]+)', content)
            for module_ref in module_refs:
                module_path = Path("src") / module_ref
                if not module_path.exists():
                    self.l2_issues["文档代码对应问题"].append({
                        "type": "文档描述代码不存在",
                        "severity": "P2",
                        "description": f"文档描述的代码模块不存在: {module_ref}",
                        "path": doc_info['path']
                    })
    
    def check_l3_standards(self):
        """L3 专业标准层审计"""
        print("L3 专业标准层审计...")
        
        # 3.1 五大原则符合性问题
        print("  3.1 检查五大原则符合性问题...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            content = doc_info['content']
            
            # 职责驱动原则
            has_responsibility = 'responsibility' in yaml_data and yaml_data['responsibility']
            has_core_duty = bool(re.search(r'核心职责|核心定位|职责描述', content))
            if not has_responsibility and not has_core_duty:
                self.l3_issues["五大原则符合性问题"].append({
                    "type": "职责驱动原则违反",
                    "severity": "P1",
                    "description": f"文档缺少职责描述",
                    "path": doc_info['path']
                })
            
            # 版本隔离原则
            if 'version' not in yaml_data:
                self.l3_issues["五大原则符合性问题"].append({
                    "type": "版本隔离原则违反",
                    "severity": "P2",
                    "description": f"文档缺少版本号",
                    "path": doc_info['path']
                })
            
            # 命名规范原则
            if 'module_id' not in yaml_data:
                self.l3_issues["五大原则符合性问题"].append({
                    "type": "命名规范原则违反",
                    "severity": "P1",
                    "description": f"文档缺少module_id",
                    "path": doc_info['path']
                })
        
        # 3.2 文档分类问题
        print("  3.2 检查文档分类问题...")
        
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            # 检查layer字段
            if 'layer' in yaml_data:
                layer = yaml_data['layer']
                # 检查是否属于Layer 8
                is_layer8 = any(keyword in filename.upper() for keyword in self.layer8_keywords)
                
                if not is_layer8 and "Layer 8" not in layer:
                    self.l3_issues["文档分类问题"].append({
                        "type": "分类错误",
                        "severity": "P2",
                        "description": f"文档可能不属于人机交互层",
                        "path": doc_info['path']
                    })
        
        # 3.3 编号体系问题
        print("  3.3 检查编号体系问题...")
        
        module_ids = []
        for filename, doc_info in self.documents.items():
            yaml_data = doc_info['yaml']
            
            if 'module_id' in yaml_data:
                module_id = yaml_data['module_id']
                
                # 检查编号重复
                if module_id in module_ids:
                    self.l3_issues["编号体系问题"].append({
                        "type": "编号重复",
                        "severity": "P0",
                        "description": f"module_id重复: {module_id}",
                        "path": doc_info['path']
                    })
                else:
                    module_ids.append(module_id)
                
                # 检查编号规范
                if not re.match(r'^[A-Z_0-9]+_\d{3}$', module_id):
                    self.l3_issues["编号体系问题"].append({
                        "type": "编号不规范",
                        "severity": "P2",
                        "description": f"module_id不符合命名标准: {module_id}",
                        "path": doc_info['path']
                    })
        
        # 3.4 文档质量问题
        print("  3.4 检查文档质量问题...")
        
        for filename, doc_info in self.documents.items():
            content = doc_info['content']
            yaml_data = doc_info['yaml']
            
            # 检查YAML字段完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
            for field in required_fields:
                if field not in yaml_data:
                    self.l3_issues["文档质量问题"].append({
                        "type": "YAML字段缺失",
                        "severity": "P1",
                        "description": f"YAML缺少必要字段: {field}",
                        "path": doc_info['path']
                    })
            
            # 检查内容结构
            if '## 概述' not in content and '## 📋 概述' not in content:
                self.l3_issues["文档质量问题"].append({
                    "type": "内容结构混乱",
                    "severity": "P2",
                    "description": f"文档缺少标准章节结构",
                    "path": doc_info['path']
                })
            
            # 检查链接引用
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in links:
                if link_path.startswith('http'):
                    continue
                # 检查相对路径链接
                if link_path.startswith('./') or link_path.startswith('../'):
                    link_file = Path(doc_info['path']).parent / link_path
                    if not link_file.exists():
                        self.l3_issues["文档质量问题"].append({
                            "type": "链接引用错误",
                            "severity": "P2",
                            "description": f"文档内链接无法访问: {link_path}",
                            "path": doc_info['path']
                        })
    
    def generate_report(self) -> str:
        """生成审计报告"""
        print("生成审计报告...")
        
        # 统计问题数量
        l1_count = sum(len(issues) for issues in self.l1_issues.values())
        l2_count = sum(len(issues) for issues in self.l2_issues.values())
        l3_count = sum(len(issues) for issues in self.l3_issues.values())
        total_issues = l1_count + l2_count + l3_count
        
        # 统计严重程度
        all_issues = []
        for issues in self.l1_issues.values():
            all_issues.extend(issues)
        for issues in self.l2_issues.values():
            all_issues.extend(issues)
        for issues in self.l3_issues.values():
            all_issues.extend(issues)
        
        p0_count = sum(1 for issue in all_issues if issue.get('severity') == 'P0')
        p1_count = sum(1 for issue in all_issues if issue.get('severity') == 'P1')
        p2_count = sum(1 for issue in all_issues if issue.get('severity') == 'P2')
        
        report = f"""---
module_id: LAYER8DEEPAUDITREPORT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
responsibility:
  - 人机交互
  - 文档治理
  - 审计
standard_type: 专业量化机构报告
applicable_scope: Layer 8 人机交互层
compliance_level: 专业标准
---

# Layer 8 人机交互层全面深度审计报告

**审计日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: docs/08_HUMAN_AI_INTERFACE  
**审计文档数**: {len(self.documents)}  
**Git备份分支**: backup/layer8-deep-audit-20260407

---

## 📊 审计统计

- **总文档数**: {len(self.documents)}
- **总问题数**: {total_issues}
- **P0级问题**: {p0_count}个
- **P1级问题**: {p1_count}个
- **P2级问题**: {p2_count}个

---

## 🔴 L1 文件系统层问题

"""
        
        # L1问题详情
        for category, issues in self.l1_issues.items():
            if issues:
                report += f"### {category}\n\n"
                for issue in issues[:10]:  # 只显示前10个
                    severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                    report += f"#### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                    report += f"- **描述**: {issue['description']}\n"
                    report += f"- **路径**: {issue['path']}\n\n"
                
                if len(issues) > 10:
                    report += f"... 还有{len(issues) - 10}个{category}\n\n"
            else:
                report += f"### {category}\n\n✅ 无问题\n\n"
        
        report += "---\n\n## 🟡 L2 文档内容层问题\n\n"
        
        # L2问题详情
        for category, issues in self.l2_issues.items():
            if issues:
                report += f"### {category}\n\n"
                for issue in issues[:10]:
                    severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                    report += f"#### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                    report += f"- **描述**: {issue['description']}\n\n"
                
                if len(issues) > 10:
                    report += f"... 还有{len(issues) - 10}个{category}\n\n"
            else:
                report += f"### {category}\n\n✅ 无问题\n\n"
        
        report += "---\n\n## 🟢 L3 专业标准层问题\n\n"
        
        # L3问题详情
        for category, issues in self.l3_issues.items():
            if issues:
                report += f"### {category}\n\n"
                for issue in issues[:10]:
                    severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                    report += f"#### {severity_icon} {issue['type']} ({issue['severity']})\n\n"
                    report += f"- **描述**: {issue['description']}\n\n"
                
                if len(issues) > 10:
                    report += f"... 还有{len(issues) - 10}个{category}\n\n"
            else:
                report += f"### {category}\n\n✅ 无问题\n\n"
        
        report += f"""---

## 📈 改进建议

### 立即修复 (P0级)

"""
        
        p0_issues = [issue for issue in all_issues if issue.get('severity') == 'P0']
        if p0_issues:
            for i, issue in enumerate(p0_issues, 1):
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
        else:
            report += "✅ 无P0级问题\n"
        
        report += "\n### 短期改进 (P1级)\n\n"
        
        p1_issues = [issue for issue in all_issues if issue.get('severity') == 'P1']
        if p1_issues:
            for i, issue in enumerate(p1_issues[:20], 1):
                report += f"{i}. **{issue['type']}**: {issue['description']}\n"
            if len(p1_issues) > 20:
                report += f"... 还有{len(p1_issues) - 20}个P1级问题\n"
        else:
            report += "✅ 无P1级问题\n"
        
        report += f"""

---

## 📊 问题分布统计

| 层级 | 问题类型 | 问题数量 |
|------|----------|----------|
"""
        
        for category, issues in self.l1_issues.items():
            report += f"| L1 | {category} | {len(issues)} |\n"
        
        for category, issues in self.l2_issues.items():
            report += f"| L2 | {category} | {len(issues)} |\n"
        
        for category, issues in self.l3_issues.items():
            report += f"| L3 | {category} | {len(issues)} |\n"
        
        report += f"""

---

## 🔄 重复文档检测

"""
        
        if self.duplicates:
            report += "发现以下重复文档：\n\n"
            for dup in self.duplicates:
                report += f"- **{dup['file1']}** 与 **{dup['file2']}** (内容哈希: {dup['hash'][:8]}...)\n"
        else:
            report += "✅ 未发现重复文档\n"
        
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
        print("Layer 8 人机交互层全面深度审计")
        print("="*80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {LAYER8_DIR}")
        print("="*80)
        
        # 执行三层审计
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_file = OUTPUT_DIR / f"LAYER8_DEEP_AUDIT_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8-sig') as f:
            f.write(report)
        
        # 统计问题数量
        l1_count = sum(len(issues) for issues in self.l1_issues.values())
        l2_count = sum(len(issues) for issues in self.l2_issues.values())
        l3_count = sum(len(issues) for issues in self.l3_issues.values())
        total_issues = l1_count + l2_count + l3_count
        
        print("\n" + "="*80)
        print("审计完成")
        print("="*80)
        print(f"L1文件系统层问题: {l1_count}")
        print(f"L2文档内容层问题: {l2_count}")
        print(f"L3专业标准层问题: {l3_count}")
        print(f"总问题数: {total_issues}")
        print(f"报告已保存至: {report_file}")
        
        return {
            "l1_issues": l1_count,
            "l2_issues": l2_count,
            "l3_issues": l3_count,
            "total_issues": total_issues,
            "report_file": str(report_file)
        }


if __name__ == "__main__":
    auditor = Layer8DeepAuditor()
    result = auditor.run_audit()
    
    # 保存JSON结果
    json_file = OUTPUT_DIR / f"layer8_deep_audit_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON结果已保存至: {json_file}")
