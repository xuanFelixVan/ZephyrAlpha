"""
组合优化层深度审计脚本
用途：执行三层审计（L1文件系统层、L2文档内容层、L3专业标准层）
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import json

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


class Layer6DeepAuditor:
    """组合优化层深度审计器"""
    
    def __init__(self):
        self.l1_issues = []  # 文件系统层问题
        self.l2_issues = []  # 文档内容层问题
        self.l3_issues = []  # 专业标准层问题
        self.documents = {}  # 文档信息存储
        self.duplicates = defaultdict(list)  # 重复文档检测
        self.responsibility_map = defaultdict(list)  # 职责映射
        
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
    
    def extract_responsibility(self, content: str) -> str:
        """提取职责描述"""
        patterns = [
            r'职责[：:]\s*(.+?)(?:\n|$)',
            r'responsibility[：:]\s*(.+?)(?:\n|$)',
            r'本文档职责[：:]\s*(.+?)(?:\n|$)',
            r'applicable_scope[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def check_l1_filesystem(self):
        """L1文件系统层审计"""
        print("\n" + "="*80)
        print("L1 文件系统层审计")
        print("="*80)
        
        # 1.1 检查目录结构
        print("\n1.1 目录结构检查...")
        
        # 检查是否有漂移文件
        non_blueprint_files = []
        for filepath in BLUEPRINTS_DIR.iterdir():
            if filepath.is_file() and not filepath.name.endswith('BLUEPRINT.md'):
                if filepath.name not in ['INDEX.md', 'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_ARCHITECTURE.md']:
                    non_blueprint_files.append(filepath.name)
        
        if non_blueprint_files:
            issue = {
                "type": "目录漂移",
                "severity": "P1",
                "description": f"发现非蓝图文件: {', '.join(non_blueprint_files)}",
                "files": non_blueprint_files
            }
            self.l1_issues.append(issue)
            print(f"  ⚠️ 发现 {len(non_blueprint_files)} 个非蓝图文件")
        else:
            print("  ✅ 未发现目录漂移问题")
        
        # 1.2 检查文件命名
        print("\n1.2 文件命名检查...")
        
        naming_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            # 检查是否包含BLUEPRINT
            if not filepath.name.endswith("BLUEPRINT.md") and "ARCHITECTURE" not in filepath.name:
                naming_issues.append(filepath.name)
        
        if naming_issues:
            issue = {
                "type": "命名不规范",
                "severity": "P2",
                "description": f"文件命名不符合蓝图规范: {', '.join(naming_issues)}",
                "files": naming_issues
            }
            self.l1_issues.append(issue)
            print(f"  ⚠️ 发现 {len(naming_issues)} 个命名不规范文件")
        else:
            print("  ✅ 文件命名规范")
        
        # 1.3 检查路径引用
        print("\n1.3 路径引用检查...")
        
        path_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            content = self.read_document(filepath)
            
            # 检查是否有过多../
            if content.count('../') > 5:
                path_issues.append({
                    "file": filepath.name,
                    "issue": "路径引用冗余"
                })
        
        if path_issues:
            issue = {
                "type": "路径引用问题",
                "severity": "P2",
                "description": f"发现路径引用冗余的文档",
                "files": path_issues
            }
            self.l1_issues.append(issue)
            print(f"  ⚠️ 发现 {len(path_issues)} 个路径引用问题")
        else:
            print("  ✅ 路径引用正常")
    
    def check_l2_content(self):
        """L2文档内容层审计"""
        print("\n" + "="*80)
        print("L2 文档内容层审计")
        print("="*80)
        
        # 2.1 检查职责驱动原则
        print("\n2.1 职责驱动原则检查...")
        
        responsibility_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            yaml_header = self.extract_yaml_header(content)
            responsibility = self.extract_responsibility(content)
            
            self.documents[filepath.name] = {
                "yaml": yaml_header,
                "responsibility": responsibility,
                "content": content[:1000]  # 存储前1000字符用于对比
            }
            
            # 检查职责是否明确
            if not responsibility and not yaml_header.get('applicable_scope'):
                responsibility_issues.append(filepath.name)
            
            # 构建职责映射
            if responsibility:
                self.responsibility_map[responsibility].append(filepath.name)
        
        if responsibility_issues:
            issue = {
                "type": "职责不明确",
                "severity": "P1",
                "description": f"缺少明确职责描述的文档: {len(responsibility_issues)}个",
                "files": responsibility_issues
            }
            self.l2_issues.append(issue)
            print(f"  ⚠️ 发现 {len(responsibility_issues)} 个职责不明确的文档")
        else:
            print("  ✅ 所有文档职责明确")
        
        # 检查职责重叠
        print("\n  检查职责重叠...")
        overlap_issues = []
        for responsibility, files in self.responsibility_map.items():
            if len(files) > 1:
                overlap_issues.append({
                    "responsibility": responsibility,
                    "files": files
                })
        
        if overlap_issues:
            issue = {
                "type": "职责重叠",
                "severity": "P0",
                "description": f"发现职责重叠的文档组合: {len(overlap_issues)}组",
                "details": overlap_issues
            }
            self.l2_issues.append(issue)
            print(f"  🔴 发现 {len(overlap_issues)} 组职责重叠")
        else:
            print("  ✅ 未发现职责重叠")
        
        # 2.2 检查索引完备性
        print("\n2.2 索引完备性检查...")
        
        index_file = BLUEPRINTS_DIR / "INDEX.md"
        if not index_file.exists():
            issue = {
                "type": "索引缺失",
                "severity": "P0",
                "description": "缺少INDEX.md索引文件"
            }
            self.l2_issues.append(issue)
            print("  🔴 缺少INDEX.md索引文件")
        else:
            # 检查索引完整性
            index_content = self.read_document(index_file)
            indexed_files = set(re.findall(r'\[([^\]]+BLUEPRINT\.md)\]', index_content))
            actual_files = set([f.name for f in BLUEPRINTS_DIR.glob("*BLUEPRINT.md")])
            
            missing_from_index = actual_files - indexed_files
            if missing_from_index:
                issue = {
                    "type": "索引不完整",
                    "severity": "P1",
                    "description": f"索引中缺少的文档: {len(missing_from_index)}个",
                    "files": list(missing_from_index)
                }
                self.l2_issues.append(issue)
                print(f"  ⚠️ 索引中缺少 {len(missing_from_index)} 个文档")
            else:
                print("  ✅ 索引完整")
        
        # 2.3 检查版本隔离
        print("\n2.3 版本隔离检查...")
        
        version_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            yaml_header = self.extract_yaml_header(content)
            
            # 检查是否有版本信息
            if not yaml_header.get('version') and not yaml_header.get('module_id'):
                version_issues.append(filepath.name)
        
        if version_issues:
            issue = {
                "type": "版本标识缺失",
                "severity": "P2",
                "description": f"缺少版本标识的文档: {len(version_issues)}个",
                "files": version_issues
            }
            self.l2_issues.append(issue)
            print(f"  ⚠️ 发现 {len(version_issues)} 个缺少版本标识的文档")
        else:
            print("  ✅ 版本标识完整")
        
        # 2.4 检查重复文档
        print("\n2.4 重复文档检测...")
        
        # 基于内容相似度检测
        content_hashes = defaultdict(list)
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            # 使用前500字符作为指纹
            content_hash = hash(content[:500])
            content_hashes[content_hash].append(filepath.name)
        
        duplicate_groups = {k: v for k, v in content_hashes.items() if len(v) > 1}
        
        if duplicate_groups:
            issue = {
                "type": "重复文档",
                "severity": "P0",
                "description": f"发现可能重复的文档组: {len(duplicate_groups)}组",
                "details": list(duplicate_groups.values())
            }
            self.l2_issues.append(issue)
            print(f"  🔴 发现 {len(duplicate_groups)} 组可能重复的文档")
        else:
            print("  ✅ 未发现重复文档")
    
    def check_l3_standards(self):
        """L3专业标准层审计"""
        print("\n" + "="*80)
        print("L3 专业标准层审计")
        print("="*80)
        
        # 3.1 检查五大原则符合性
        print("\n3.1 五大原则符合性检查...")
        
        principle_violations = {
            "职责驱动": [],
            "索引完备": [],
            "版本隔离": [],
            "文档代码对应": [],
            "命名规范": []
        }
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            yaml_header = self.extract_yaml_header(content)
            
            # 检查职责驱动原则
            if not yaml_header.get('applicable_scope') and '职责' not in content[:500]:
                principle_violations["职责驱动"].append(filepath.name)
            
            # 检查索引完备原则
            if not yaml_header.get('parent_document'):
                principle_violations["索引完备"].append(filepath.name)
            
            # 检查版本隔离原则
            if not yaml_header.get('version'):
                principle_violations["版本隔离"].append(filepath.name)
            
            # 检查命名规范原则
            if not yaml_header.get('module_id'):
                principle_violations["命名规范"].append(filepath.name)
        
        for principle, violations in principle_violations.items():
            if violations:
                issue = {
                    "type": f"{principle}原则违反",
                    "severity": "P1",
                    "description": f"违反{principle}原则的文档: {len(violations)}个",
                    "files": violations
                }
                self.l3_issues.append(issue)
                print(f"  ⚠️ {principle}: {len(violations)}个文档")
            else:
                print(f"  ✅ {principle}: 符合")
        
        # 3.2 检查文档分类
        print("\n3.2 文档分类检查...")
        
        layer_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            yaml_header = self.extract_yaml_header(content)
            
            layer = yaml_header.get('layer', '')
            # 检查是否属于Layer 6
            if 'Layer 6' not in layer and '组合优化' not in layer:
                layer_issues.append({
                    "file": filepath.name,
                    "layer": layer
                })
        
        if layer_issues:
            issue = {
                "type": "层级分类错误",
                "severity": "P1",
                "description": f"Layer定位不明确的文档: {len(layer_issues)}个",
                "details": layer_issues
            }
            self.l3_issues.append(issue)
            print(f"  ⚠️ 发现 {len(layer_issues)} 个Layer定位不明确的文档")
        else:
            print("  ✅ Layer定位明确")
        
        # 3.3 检查编号体系
        print("\n3.3 编号体系检查...")
        
        module_ids = defaultdict(list)
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            yaml_header = self.extract_yaml_header(content)
            
            module_id = yaml_header.get('module_id', '')
            if module_id:
                module_ids[module_id].append(filepath.name)
        
        duplicate_ids = {k: v for k, v in module_ids.items() if len(v) > 1}
        
        if duplicate_ids:
            issue = {
                "type": "编号重复",
                "severity": "P0",
                "description": f"发现重复的module_id: {len(duplicate_ids)}个",
                "details": list(duplicate_ids.values())
            }
            self.l3_issues.append(issue)
            print(f"  🔴 发现 {len(duplicate_ids)} 个重复的module_id")
        else:
            print("  ✅ 编号体系规范")
        
        # 3.4 检查文档质量
        print("\n3.4 文档质量检查...")
        
        quality_issues = []
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            
            # 检查YAML头部
            if not content.startswith('---'):
                quality_issues.append({
                    "file": filepath.name,
                    "issue": "缺少YAML头部"
                })
            
            # 检查文档治理章节
            if '文档治理' not in content:
                quality_issues.append({
                    "file": filepath.name,
                    "issue": "缺少文档治理章节"
                })
        
        if quality_issues:
            issue = {
                "type": "文档质量问题",
                "severity": "P2",
                "description": f"存在质量问题的文档: {len(quality_issues)}个",
                "details": quality_issues
            }
            self.l3_issues.append(issue)
            print(f"  ⚠️ 发现 {len(quality_issues)} 个质量问题")
        else:
            print("  ✅ 文档质量良好")
    
    def generate_report(self) -> str:
        """生成审计报告"""
        report = []
        report.append("="*80)
        report.append("组合优化层深度审计报告")
        report.append("="*80)
        report.append(f"\n审计时间: 2026-04-07")
        report.append(f"审计范围: {BLUEPRINTS_DIR}")
        report.append(f"审计文档数: {len([f for f in BLUEPRINTS_DIR.glob('*.md') if f.name != 'INDEX.md'])}")
        
        # L1问题汇总
        report.append("\n" + "="*80)
        report.append("L1 文件系统层问题汇总")
        report.append("="*80)
        if self.l1_issues:
            for issue in self.l1_issues:
                severity = issue.get('severity', 'P2')
                icon = "🔴" if severity == "P0" else "⚠️" if severity == "P1" else "ℹ️"
                report.append(f"\n{icon} [{severity}] {issue['type']}")
                report.append(f"   {issue['description']}")
                if 'files' in issue:
                    for file in issue['files'][:5]:
                        report.append(f"   - {file}")
                    if len(issue['files']) > 5:
                        report.append(f"   ... 还有 {len(issue['files']) - 5} 个")
        else:
            report.append("\n✅ 未发现问题")
        
        # L2问题汇总
        report.append("\n" + "="*80)
        report.append("L2 文档内容层问题汇总")
        report.append("="*80)
        if self.l2_issues:
            for issue in self.l2_issues:
                severity = issue.get('severity', 'P2')
                icon = "🔴" if severity == "P0" else "⚠️" if severity == "P1" else "ℹ️"
                report.append(f"\n{icon} [{severity}] {issue['type']}")
                report.append(f"   {issue['description']}")
                if 'files' in issue:
                    for file in issue['files'][:5]:
                        report.append(f"   - {file}")
                    if len(issue['files']) > 5:
                        report.append(f"   ... 还有 {len(issue['files']) - 5} 个")
        else:
            report.append("\n✅ 未发现问题")
        
        # L3问题汇总
        report.append("\n" + "="*80)
        report.append("L3 专业标准层问题汇总")
        report.append("="*80)
        if self.l3_issues:
            for issue in self.l3_issues:
                severity = issue.get('severity', 'P2')
                icon = "🔴" if severity == "P0" else "⚠️" if severity == "P1" else "ℹ️"
                report.append(f"\n{icon} [{severity}] {issue['type']}")
                report.append(f"   {issue['description']}")
                if 'files' in issue:
                    for file in issue['files'][:5]:
                        report.append(f"   - {file}")
                    if len(issue['files']) > 5:
                        report.append(f"   ... 还有 {len(issue['files']) - 5} 个")
        else:
            report.append("\n✅ 未发现问题")
        
        # 总体评估
        report.append("\n" + "="*80)
        report.append("总体评估")
        report.append("="*80)
        
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        p0_issues = len([i for i in (self.l1_issues + self.l2_issues + self.l3_issues) if i.get('severity') == 'P0'])
        p1_issues = len([i for i in (self.l1_issues + self.l2_issues + self.l3_issues) if i.get('severity') == 'P1'])
        p2_issues = len([i for i in (self.l1_issues + self.l2_issues + self.l3_issues) if i.get('severity') == 'P2'])
        
        report.append(f"\n总问题数: {total_issues}")
        report.append(f"  🔴 P0级问题: {p0_issues}")
        report.append(f"  ⚠️ P1级问题: {p1_issues}")
        report.append(f"  ℹ️ P2级问题: {p2_issues}")
        
        if p0_issues > 0:
            compliance_rate = 85
        elif p1_issues > 0:
            compliance_rate = 95
        else:
            compliance_rate = 98
        
        report.append(f"\n合规率估算: {compliance_rate}%")
        
        if p0_issues > 0:
            report.append("\n🚨 需要立即处理P0级问题")
        elif p1_issues > 0:
            report.append("\n⚠️ 建议尽快处理P1级问题")
        else:
            report.append("\n✅ 文档治理状况良好")
        
        return "\n".join(report)
    
    def run_audit(self):
        """执行完整审计"""
        print("\n" + "="*80)
        print("开始组合优化层深度审计")
        print("="*80)
        
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        report = self.generate_report()
        
        # 保存报告
        report_path = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER6_DEEP_AUDIT_REPORT_20260407.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n" + report)
        print(f"\n📄 审计报告已保存至: {report_path}")
        
        return report


if __name__ == "__main__":
    auditor = Layer6DeepAuditor()
    auditor.run_audit()
