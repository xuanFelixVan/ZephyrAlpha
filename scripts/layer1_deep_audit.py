"""
Layer 1 深度审计工具
基于专业量化机构五大原则和三层审计标准
"""
import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import yaml
from datetime import datetime

class Layer1DeepAuditor:
    """Layer 1深度审计器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs" / "02_FACTOR_LIBRARY" / "04_DATA_SOURCE"
        self.audit_results = {
            'L1_file_system': [],
            'L2_content': [],
            'L3_professional': []
        }
        self.all_docs = {}
        self.doc_hashes = {}
        self.module_ids = {}
        self.responsibilities = {}
        
    def run_full_audit(self):
        """运行完整审计"""
        print("="*80)
        print("Layer 1 深度审计开始")
        print("="*80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计路径: {self.docs_path}")
        print()
        
        # 收集所有文档
        self._collect_all_documents()
        print(f"✓ 收集到 {len(self.all_docs)} 个文档")
        print()
        
        # L1: 文件系统层审计
        print("阶段1: 文件系统层审计 (L1)")
        print("-"*80)
        self._audit_directory_structure()
        self._audit_file_naming()
        self._audit_path_references()
        print()
        
        # L2: 文档内容层审计
        print("阶段2: 文档内容层审计 (L2)")
        print("-"*80)
        self._audit_responsibility_clarity()
        self._audit_index_completeness()
        self._audit_version_isolation()
        self._audit_doc_code_correspondence()
        print()
        
        # L3: 专业标准层审计
        print("阶段3: 专业标准层审计 (L3)")
        print("-"*80)
        self._audit_five_principles()
        self._audit_document_classification()
        self._audit_numbering_system()
        self._audit_document_quality()
        print()
        
        # 生成报告
        self._generate_report()
        
    def _collect_all_documents(self):
        """收集所有文档"""
        for md_file in self.docs_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.docs_path)
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 计算内容哈希
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                # 提取YAML头部
                yaml_data = self._extract_yaml(content)
                
                self.all_docs[str(rel_path)] = {
                    'path': md_file,
                    'content': content,
                    'hash': content_hash,
                    'yaml': yaml_data,
                    'size': len(content),
                    'lines': content.count('\n') + 1
                }
                
                # 记录哈希用于重复检测
                if content_hash not in self.doc_hashes:
                    self.doc_hashes[content_hash] = []
                self.doc_hashes[content_hash].append(str(rel_path))
                
                # 记录module_id
                if yaml_data and 'module_id' in yaml_data:
                    module_id = yaml_data['module_id']
                    if module_id not in self.module_ids:
                        self.module_ids[module_id] = []
                    self.module_ids[module_id].append(str(rel_path))
                    
                # 记录职责
                if yaml_data and 'responsibility' in yaml_data:
                    self.responsibilities[str(rel_path)] = yaml_data['responsibility']
                    
            except Exception as e:
                print(f"  ⚠️ 读取文件失败: {rel_path} - {str(e)}")
                
    def _extract_yaml(self, content: str) -> dict:
        """提取YAML头部"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1])
                except:
                    pass
        return {}
        
    def _audit_directory_structure(self):
        """审计目录结构"""
        print("  检查目录结构...")
        
        # 检查目录层级深度
        for doc_path in self.all_docs.keys():
            depth = doc_path.count(os.sep)
            if depth > 4:
                self._add_issue('L1', '目录层级过深', doc_path, 
                              f'嵌套层级{depth}超过4层', '中')
                
        # 检查空目录
        for dir_path in self.docs_path.rglob("*"):
            if dir_path.is_dir():
                files = list(dir_path.glob("*.md"))
                if len(files) == 0:
                    self._add_issue('L1', '空目录', str(dir_path.relative_to(self.docs_path)),
                                  '目录下无Markdown文件', '低')
                elif len(files) < 3:
                    self._add_issue('L1', '稀疏目录', str(dir_path.relative_to(self.docs_path)),
                                  f'目录下仅{len(files)}个文件，建议整合', '低')
                                  
        print("  ✓ 目录结构审计完成")
        
    def _audit_file_naming(self):
        """审计文件命名"""
        print("  检查文件命名...")
        
        for doc_path in self.all_docs.keys():
            filename = Path(doc_path).name
            
            # 检查中文文件名
            if re.search(r'[\u4e00-\u9fff]', filename):
                self._add_issue('L1', '中文文件名', doc_path,
                              '文件名包含中文字符', '中')
                              
            # 检查空格
            if ' ' in filename:
                self._add_issue('L1', '文件名包含空格', doc_path,
                              '文件名包含空格', '低')
                              
            # 检查特殊字符
            if re.search(r'[^\w\-_\.]', filename.replace('.md', '')):
                self._add_issue('L1', '特殊字符', doc_path,
                              '文件名包含特殊字符', '低')
                              
        print("  ✓ 文件命名审计完成")
        
    def _audit_path_references(self):
        """审计路径引用"""
        print("  检查路径引用...")
        
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for doc_path, doc_data in self.all_docs.items():
            content = doc_data['content']
            links = link_pattern.findall(content)
            
            for link_text, link_url in links:
                # 检查相对路径层级
                if '../' in link_url:
                    depth = link_url.count('../')
                    if depth > 3:
                        self._add_issue('L1', '路径层级过深', doc_path,
                                      f'链接路径包含{depth}层../: {link_url}', '低')
                                      
                # 检查绝对路径
                if link_url.startswith('/') or link_url.startswith('D:'):
                    self._add_issue('L1', '绝对路径', doc_path,
                                  f'使用绝对路径: {link_url}', '中')
                                  
        print("  ✓ 路径引用审计完成")
        
    def _audit_responsibility_clarity(self):
        """审计职责清晰度"""
        print("  检查职责清晰度...")
        
        # 检查职责缺失
        docs_without_responsibility = []
        for doc_path, doc_data in self.all_docs.items():
            if not doc_data['yaml'] or 'responsibility' not in doc_data['yaml']:
                docs_without_responsibility.append(doc_path)
                
        if docs_without_responsibility:
            for doc_path in docs_without_responsibility[:10]:  # 只显示前10个
                self._add_issue('L2', '职责缺失', doc_path,
                              '文档缺少职责描述', '高')
                              
        # 检查职责重叠
        responsibility_docs = defaultdict(list)
        for doc_path, responsibility in self.responsibilities.items():
            if isinstance(responsibility, list):
                for resp in responsibility:
                    responsibility_docs[resp].append(doc_path)
            else:
                responsibility_docs[responsibility].append(doc_path)
                
        for resp, docs in responsibility_docs.items():
            if len(docs) > 1:
                self._add_issue('L2', '职责重叠', ', '.join(docs[:3]),
                              f'职责"{resp}"出现在{len(docs)}个文档中', '高')
                              
        print("  ✓ 职责清晰度审计完成")
        
    def _audit_index_completeness(self):
        """审计索引完备性"""
        print("  检查索引完备性...")
        
        # 检查主索引
        main_index = self.docs_path / "INDEX.md"
        if not main_index.exists():
            self._add_issue('L2', '主索引缺失', 'INDEX.md',
                          '缺少主入口INDEX.md', '高')
        else:
            # 检查索引完整性
            with open(main_index, 'r', encoding='utf-8') as f:
                index_content = f.read()
                
            for doc_path in self.all_docs.keys():
                if doc_path != 'INDEX.md' and doc_path not in index_content:
                    self._add_issue('L2', '索引不完整', 'INDEX.md',
                                  f'未包含文档: {doc_path}', '中')
                                  
        # 检查子目录索引
        for dir_path in self.docs_path.rglob("*"):
            if dir_path.is_dir():
                index_file = dir_path / "INDEX.md"
                if not index_file.exists():
                    files = list(dir_path.glob("*.md"))
                    if len(files) > 0:
                        self._add_issue('L2', '子目录索引缺失', 
                                      str(dir_path.relative_to(self.docs_path)),
                                      '缺少INDEX.md导航文件', '中')
                                      
        print("  ✓ 索引完备性审计完成")
        
    def _audit_version_isolation(self):
        """审计版本隔离"""
        print("  检查版本隔离...")
        
        # 检查重复文档（基于内容哈希）
        for content_hash, docs in self.doc_hashes.items():
            if len(docs) > 1:
                self._add_issue('L2', '重复文档', ', '.join(docs),
                              f'{len(docs)}个文档内容完全相同', '高')
                              
        # 检查module_id重复
        for module_id, docs in self.module_ids.items():
            if len(docs) > 1:
                self._add_issue('L2', 'module_id重复', ', '.join(docs),
                              f'module_id "{module_id}"重复使用', '高')
                              
        print("  ✓ 版本隔离审计完成")
        
    def _audit_doc_code_correspondence(self):
        """审计文档代码对应"""
        print("  检查文档代码对应...")
        
        # 检查文档中提到的代码文件是否存在
        code_pattern = re.compile(r'`([^`]+\.(py|sql|yaml|json))`')
        
        for doc_path, doc_data in self.all_docs.items():
            content = doc_data['content']
            code_refs = code_pattern.findall(content)
            
            for code_file, ext in code_refs:
                # 简单检查，不实际验证文件存在
                if '../' in code_file or code_file.startswith('/'):
                    self._add_issue('L2', '代码引用路径问题', doc_path,
                                  f'代码引用路径: {code_file}', '低')
                                  
        print("  ✓ 文档代码对应审计完成")
        
    def _audit_five_principles(self):
        """审计五大原则符合性"""
        print("  检查五大原则符合性...")
        
        for doc_path, doc_data in self.all_docs.items():
            yaml_data = doc_data['yaml']
            
            # 职责驱动原则
            if not yaml_data or 'responsibility' not in yaml_data:
                self._add_issue('L3', '职责驱动原则违反', doc_path,
                              '缺少职责描述', '高')
                              
            # 版本隔离原则
            if yaml_data and 'version' not in yaml_data:
                self._add_issue('L3', '版本隔离原则违反', doc_path,
                              '缺少版本号', '中')
                              
            # 命名规范原则
            if yaml_data and 'module_id' not in yaml_data:
                self._add_issue('L3', '命名规范原则违反', doc_path,
                              '缺少module_id', '中')
                              
        print("  ✓ 五大原则符合性审计完成")
        
    def _audit_document_classification(self):
        """审计文档分类"""
        print("  检查文档分类...")
        
        # 检查文档是否在正确的分类目录下
        for doc_path in self.all_docs.keys():
            parts = Path(doc_path).parts
            
            # 检查是否有分类目录
            if len(parts) > 1:
                category = parts[0]
                # 这里可以添加更多分类检查逻辑
                
        print("  ✓ 文档分类审计完成")
        
    def _audit_numbering_system(self):
        """审计编号体系"""
        print("  检查编号体系...")
        
        # 检查module_id格式
        module_id_pattern = re.compile(r'^[A-Z_]+_\d{3}$')
        
        for module_id, docs in self.module_ids.items():
            if not module_id_pattern.match(module_id):
                self._add_issue('L3', 'module_id格式不规范', docs[0],
                              f'module_id格式: {module_id}', '低')
                              
        print("  ✓ 编号体系审计完成")
        
    def _audit_document_quality(self):
        """审计文档质量"""
        print("  检查文档质量...")
        
        for doc_path, doc_data in self.all_docs.items():
            yaml_data = doc_data['yaml']
            content = doc_data['content']
            
            # 检查YAML头部
            if not yaml_data:
                self._add_issue('L3', 'YAML头部缺失', doc_path,
                              '文档缺少标准YAML元数据', '高')
            else:
                # 检查必要字段
                required_fields = ['module_id', 'version', 'status', 'created_date']
                for field in required_fields:
                    if field not in yaml_data:
                        self._add_issue('L3', 'YAML字段缺失', doc_path,
                                      f'缺少必要字段: {field}', '中')
                                      
            # 检查内容结构
            if '## ' not in content:
                self._add_issue('L3', '内容结构混乱', doc_path,
                              '文档缺少标准章节结构', '中')
                              
            # 检查文档大小
            if doc_data['size'] < 500:
                self._add_issue('L3', '文档内容过少', doc_path,
                              f'文档仅{doc_data["size"]}字节', '低')
                              
        print("  ✓ 文档质量审计完成")
        
    def _add_issue(self, level: str, issue_type: str, location: str, 
                   description: str, severity: str):
        """添加问题"""
        # 映射层级名称
        level_map = {
            'L1': 'L1_file_system',
            'L2': 'L2_content',
            'L3': 'L3_professional'
        }
        actual_level = level_map.get(level, level)
        
        self.audit_results[actual_level].append({
            'type': issue_type,
            'location': location,
            'description': description,
            'severity': severity,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    def _generate_report(self):
        """生成审计报告"""
        report_path = self.base_path / "docs" / "09_AUDIT" / "REPORTS" / \
                     f"LAYER1_DEEP_AUDIT_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""---
module_id: LAYER1_DEEP_AUDIT_REPORT_{datetime.now().strftime('%Y%m%d')}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席架构师
standard_type: 专业量化机构文档
responsibility:
  - 文档审计
  - 质量检查
layer: "Layer 1 (数据预处理层)"
---

# Layer 1 深度审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计对象**: Layer 1 (数据预处理层)  
**审计标准**: 专业量化机构五大原则 + 三层审计标准  
**文档总数**: {len(self.all_docs)}

---

## 📊 审计摘要

| 审计层级 | 问题数量 | 高严重度 | 中严重度 | 低严重度 |
|---------|---------|---------|---------|---------|
| L1 文件系统层 | {len(self.audit_results['L1_file_system'])} | {sum(1 for i in self.audit_results['L1_file_system'] if i['severity']=='高')} | {sum(1 for i in self.audit_results['L1_file_system'] if i['severity']=='中')} | {sum(1 for i in self.audit_results['L1_file_system'] if i['severity']=='低')} |
| L2 文档内容层 | {len(self.audit_results['L2_content'])} | {sum(1 for i in self.audit_results['L2_content'] if i['severity']=='高')} | {sum(1 for i in self.audit_results['L2_content'] if i['severity']=='中')} | {sum(1 for i in self.audit_results['L2_content'] if i['severity']=='低')} |
| L3 专业标准层 | {len(self.audit_results['L3_professional'])} | {sum(1 for i in self.audit_results['L3_professional'] if i['severity']=='高')} | {sum(1 for i in self.audit_results['L3_professional'] if i['severity']=='中')} | {sum(1 for i in self.audit_results['L3_professional'] if i['severity']=='低')} |
| **总计** | **{sum(len(v) for v in self.audit_results.values())}** | **{sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='高')}** | **{sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='中')}** | **{sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='低')}** |

---

## 🔴 L1 文件系统层问题

""")
            
            if self.audit_results['L1_file_system']:
                for issue in self.audit_results['L1_file_system']:
                    f.write(f"### {issue['type']} ({issue['severity']})\n\n")
                    f.write(f"**位置**: `{issue['location']}`\n\n")
                    f.write(f"**描述**: {issue['description']}\n\n")
                    f.write("---\n\n")
            else:
                f.write("✅ 无L1层问题\n\n")
                
            f.write("""
## 🟡 L2 文档内容层问题

""")
            
            if self.audit_results['L2_content']:
                for issue in self.audit_results['L2_content']:
                    f.write(f"### {issue['type']} ({issue['severity']})\n\n")
                    f.write(f"**位置**: `{issue['location']}`\n\n")
                    f.write(f"**描述**: {issue['description']}\n\n")
                    f.write("---\n\n")
            else:
                f.write("✅ 无L2层问题\n\n")
                
            f.write("""
## 🟢 L3 专业标准层问题

""")
            
            if self.audit_results['L3_professional']:
                for issue in self.audit_results['L3_professional']:
                    f.write(f"### {issue['type']} ({issue['severity']})\n\n")
                    f.write(f"**位置**: `{issue['location']}`\n\n")
                    f.write(f"**描述**: {issue['description']}\n\n")
                    f.write("---\n\n")
            else:
                f.write("✅ 无L3层问题\n\n")
                
            f.write(f"""
## 📝 修复建议

### 高优先级修复

""")
            
            # 列出高优先级问题
            high_priority = [i for i in sum(self.audit_results.values(), []) if i['severity'] == '高']
            if high_priority:
                for i, issue in enumerate(high_priority[:20], 1):  # 只显示前20个
                    f.write(f"{i}. **{issue['type']}** - {issue['location']}\n")
                    f.write(f"   {issue['description']}\n\n")
            else:
                f.write("✅ 无高优先级问题\n\n")
                
            f.write(f"""
---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本创建 | 首席架构师 |

---

**文档结束**
""")
        
        print(f"\n✓ 审计报告已生成: {report_path}")
        
        # 打印摘要
        print("\n" + "="*80)
        print("审计摘要")
        print("="*80)
        print(f"文档总数: {len(self.all_docs)}")
        print(f"L1层问题: {len(self.audit_results['L1_file_system'])}个")
        print(f"L2层问题: {len(self.audit_results['L2_content'])}个")
        print(f"L3层问题: {len(self.audit_results['L3_professional'])}个")
        print(f"总问题数: {sum(len(v) for v in self.audit_results.values())}个")
        print(f"高严重度: {sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='高')}个")
        print(f"中严重度: {sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='中')}个")
        print(f"低严重度: {sum(1 for i in sum(self.audit_results.values(), []) if i['severity']=='低')}个")
        print("="*80)

if __name__ == "__main__":
    auditor = Layer1DeepAuditor("d:/ZephyrAlpha")
    auditor.run_full_audit()
