"""
Layer 1 深度审计问题修复脚本
"""
import os
import re
from pathlib import Path
from typing import Dict, List
import yaml
from datetime import datetime

class Layer1IssueFixer:
    """Layer 1问题修复器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs" / "02_FACTOR_LIBRARY" / "04_DATA_SOURCE"
        self.fix_log = {
            'fix_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fixes': []
        }
        
    def run_all_fixes(self):
        """运行所有修复"""
        print("="*80)
        print("Layer 1 深度审计问题修复")
        print("="*80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # P0: 修复职责重叠问题
        print("P0: 修复职责重叠问题")
        print("-"*80)
        self._fix_responsibility_overlap()
        print()
        
        # P1: 修复索引不完整问题
        print("P1: 修复索引不完整问题")
        print("-"*80)
        self._fix_index_incompleteness()
        print()
        
        # P2: 修复module_id格式问题
        print("P2: 修复module_id格式问题")
        print("-"*80)
        self._fix_module_id_format()
        print()
        
        # 保存修复日志
        self._save_fix_log()
        
        print("\n" + "="*80)
        print("修复完成")
        print("="*80)
        
    def _fix_responsibility_overlap(self):
        """修复职责重叠问题"""
        # 读取所有文档的职责
        doc_responsibilities = {}
        
        for md_file in self.docs_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.docs_path)
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                yaml_data = self._extract_yaml(content)
                if yaml_data and 'responsibility' in yaml_data:
                    doc_responsibilities[str(rel_path)] = {
                        'path': md_file,
                        'responsibility': yaml_data['responsibility'],
                        'yaml': yaml_data,
                        'content': content
                    }
            except Exception as e:
                print(f"  ⚠️ 读取文件失败: {rel_path}")
                
        # 分析职责重叠
        responsibility_count = {}
        for doc_path, data in doc_responsibilities.items():
            resp = data['responsibility']
            if isinstance(resp, list):
                for r in resp:
                    if r not in responsibility_count:
                        responsibility_count[r] = []
                    responsibility_count[r].append(doc_path)
            else:
                if resp not in responsibility_count:
                    responsibility_count[resp] = []
                responsibility_count[resp].append(doc_path)
                
        # 找出重叠的职责
        overlapping = {k: v for k, v in responsibility_count.items() if len(v) > 5}
        
        print(f"  发现 {len(overlapping)} 个重叠职责")
        
        # 对重叠职责进行细化
        for resp, docs in overlapping.items():
            print(f"\n  处理职责: {resp} ({len(docs)}个文档)")
            
            # 根据文档路径和内容细化职责
            for doc_path in docs[:5]:  # 只处理前5个
                data = doc_responsibilities[doc_path]
                new_resp = self._refine_responsibility(doc_path, resp, data['content'])
                
                if new_resp != resp:
                    self._update_document_responsibility(
                        data['path'],
                        data['content'],
                        data['yaml'],
                        resp,
                        new_resp
                    )
                    self.fix_log['fixes'].append({
                        'type': '职责细化',
                        'file': doc_path,
                        'old': resp,
                        'new': new_resp
                    })
                    
        print(f"\n  ✓ 职责重叠修复完成")
        
    def _refine_responsibility(self, doc_path: str, original_resp: str, content: str) -> str:
        """细化职责描述"""
        # 根据文档路径和内容生成更具体的职责
        path_parts = Path(doc_path).parts
        
        # 如果是蓝图文档
        if 'BLUEPRINT' in doc_path:
            module_name = Path(doc_path).parent.name
            return f"{module_name.replace('_', ' ')} - 蓝图设计"
            
        # 如果是索引文档
        if 'INDEX' in doc_path:
            module_name = Path(doc_path).parent.name
            return f"{module_name.replace('_', ' ')} - 模块导航"
            
        # 如果是特定功能文档
        if 'CONNECTOR' in doc_path:
            connector_name = Path(doc_path).stem.replace('_CONNECTOR', '')
            return f"{connector_name}数据源连接器"
            
        # 如果是配置管理
        if 'CONFIG' in doc_path:
            return "配置管理与环境变量"
            
        # 如果是数据质量
        if 'QUALITY' in doc_path:
            return "数据质量控制与监控"
            
        # 如果是数据清洗
        if 'CLEANING' in doc_path:
            return "数据清洗与预处理"
            
        # 如果是数据管道
        if 'PIPELINE' in doc_path:
            return "数据管道编排"
            
        # 默认返回原始职责
        return original_resp
        
    def _update_document_responsibility(self, doc_path: Path, content: str, 
                                       yaml_data: dict, old_resp: str, new_resp: str):
        """更新文档职责"""
        try:
            # 更新YAML中的职责
            if 'responsibility' in yaml_data:
                if isinstance(yaml_data['responsibility'], list):
                    # 替换列表中的职责
                    yaml_data['responsibility'] = [
                        new_resp if r == old_resp else r 
                        for r in yaml_data['responsibility']
                    ]
                else:
                    yaml_data['responsibility'] = new_resp
                    
                # 重新生成YAML头部
                yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False)
                
                # 替换内容
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        new_content = f"---\n{yaml_str}---{parts[2]}"
                        
                        with open(doc_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                        print(f"    ✓ 更新: {doc_path.name}")
                        
        except Exception as e:
            print(f"    ⚠️ 更新失败: {doc_path.name} - {str(e)}")
            
    def _fix_index_incompleteness(self):
        """修复索引不完整问题"""
        index_file = self.docs_path / "INDEX.md"
        
        if not index_file.exists():
            print("  ⚠️ INDEX.md不存在")
            return
            
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 收集所有文档
        all_docs = []
        for md_file in self.docs_path.rglob("*.md"):
            if md_file.name != "INDEX.md":
                rel_path = md_file.relative_to(self.docs_path)
                all_docs.append(str(rel_path).replace('\\', '/'))
                
        # 检查哪些文档未被索引
        missing_docs = []
        for doc in all_docs:
            if doc not in content:
                missing_docs.append(doc)
                
        print(f"  发现 {len(missing_docs)} 个未索引文档")
        
        # 添加缺失的文档到索引
        if missing_docs:
            # 按目录分组
            grouped = {}
            for doc in missing_docs:
                parts = Path(doc).parts
                if len(parts) > 1:
                    group = parts[0]
                    if group not in grouped:
                        grouped[group] = []
                    grouped[group].append(doc)
                else:
                    if 'root' not in grouped:
                        grouped['root'] = []
                    grouped['root'].append(doc)
                    
            # 生成索引内容
            index_additions = "\n\n## 新增文档索引\n\n"
            
            for group, docs in sorted(grouped.items()):
                if group != 'root':
                    index_additions += f"### {group}\n\n"
                for doc in docs:
                    doc_name = Path(doc).stem
                    index_additions += f"- [{doc_name}]({doc})\n"
                index_additions += "\n"
                
            # 追加到INDEX.md
            with open(index_file, 'a', encoding='utf-8') as f:
                f.write(index_additions)
                
            print(f"  ✓ 已添加 {len(missing_docs)} 个文档到索引")
            
            self.fix_log['fixes'].append({
                'type': '索引补充',
                'count': len(missing_docs),
                'docs': missing_docs[:10]  # 只记录前10个
            })
        else:
            print("  ✓ 索引完整")
            
    def _fix_module_id_format(self):
        """修复module_id格式问题"""
        issues = [
            {
                'file': 'DATA_SOURCE_LAYER_GAP_ANALYSIS_V2.md',
                'old': 'DATA_SOURCE_LAYER_GAP_ANALYSIS_V2_001',
                'new': 'DATA_SOURCE_GAP_ANALYSIS_001'
            },
            {
                'file': '07_DATA_PIPELINE/README.md',
                'old': 'FACTOR_001_L02_README',
                'new': 'DATA_PIPELINE_README_001'
            }
        ]
        
        for issue in issues:
            doc_path = self.docs_path / issue['file']
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 替换module_id
                new_content = content.replace(issue['old'], issue['new'])
                
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                print(f"  ✓ 修复: {issue['file']}")
                
                self.fix_log['fixes'].append({
                    'type': 'module_id格式修复',
                    'file': issue['file'],
                    'old': issue['old'],
                    'new': issue['new']
                })
            else:
                print(f"  ⚠️ 文件不存在: {issue['file']}")
                
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
        
    def _save_fix_log(self):
        """保存修复日志"""
        log_path = self.base_path / "docs" / "09_AUDIT" / "STATE" / \
                  f"layer1_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
            
        print(f"\n✓ 修复日志已保存: {log_path}")

if __name__ == "__main__":
    fixer = Layer1IssueFixer("d:/ZephyrAlpha")
    fixer.run_all_fixes()
