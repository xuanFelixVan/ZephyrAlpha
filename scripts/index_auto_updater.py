"""
Layer 1 索引自动更新机制
自动检测新文档并更新INDEX.md
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Set
import yaml
from datetime import datetime
from collections import defaultdict

class IndexAutoUpdater:
    """索引自动更新器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs" / "02_FACTOR_LIBRARY" / "04_DATA_SOURCE"
        self.index_file = self.docs_path / "INDEX.md"
        
        self.update_log = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updates': [],
            'statistics': {
                'total_docs': 0,
                'indexed_docs': 0,
                'new_docs': 0,
                'removed_docs': 0
            }
        }
        
    def run_auto_update(self):
        """运行自动更新"""
        print("="*80)
        print("Layer 1 索引自动更新")
        print("="*80)
        print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 收集所有文档
        all_docs = self._collect_all_documents()
        self.update_log['statistics']['total_docs'] = len(all_docs)
        print(f"发现 {len(all_docs)} 个文档")
        
        # 读取现有索引
        indexed_docs = self._read_current_index()
        self.update_log['statistics']['indexed_docs'] = len(indexed_docs)
        print(f"已索引 {len(indexed_docs)} 个文档")
        
        # 找出新文档
        new_docs = all_docs - indexed_docs
        self.update_log['statistics']['new_docs'] = len(new_docs)
        print(f"新增 {len(new_docs)} 个文档")
        
        # 找出已删除文档
        removed_docs = indexed_docs - all_docs
        self.update_log['statistics']['removed_docs'] = len(removed_docs)
        print(f"已删除 {len(removed_docs)} 个文档")
        print()
        
        if new_docs:
            print("新增文档列表:")
            for doc in sorted(new_docs):
                print(f"  + {doc}")
            print()
            
        if removed_docs:
            print("已删除文档列表:")
            for doc in sorted(removed_docs):
                print(f"  - {doc}")
            print()
            
        # 更新索引
        if new_docs or removed_docs:
            self._update_index(new_docs, removed_docs, all_docs)
        else:
            print("✅ 索引已是最新，无需更新")
            
        print()
        
        # 保存更新日志
        self._save_update_log()
        
        print("="*80)
        print("索引更新完成")
        print("="*80)
        
    def _collect_all_documents(self) -> Set[str]:
        """收集所有文档"""
        all_docs = set()
        
        for md_file in self.docs_path.rglob("*.md"):
            if md_file.name == "INDEX.md":
                continue
                
            rel_path = md_file.relative_to(self.docs_path)
            all_docs.add(str(rel_path).replace('\\', '/'))
            
        return all_docs
        
    def _read_current_index(self) -> Set[str]:
        """读取当前索引"""
        if not self.index_file.exists():
            return set()
            
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取所有链接
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = link_pattern.findall(content)
        
        indexed_docs = set()
        for link_text, link_url in links:
            # 只处理相对路径的.md文件
            if link_url.endswith('.md') and not link_url.startswith('http'):
                indexed_docs.add(link_url)
                
        return indexed_docs
        
    def _update_index(self, new_docs: Set[str], removed_docs: Set[str], all_docs: Set[str]):
        """更新索引"""
        print("开始更新索引...")
        print("-"*80)
        
        # 读取现有索引内容
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 按目录分组新文档
        grouped_docs = defaultdict(list)
        for doc in new_docs:
            parts = Path(doc).parts
            if len(parts) > 1:
                group = parts[0]
                grouped_docs[group].append(doc)
            else:
                grouped_docs['root'].append(doc)
                
        # 生成新索引内容
        new_content = "\n\n## 📁 自动索引更新\n\n"
        new_content += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if new_docs:
            new_content += "### 新增文档\n\n"
            
            for group, docs in sorted(grouped_docs.items()):
                if group != 'root':
                    new_content += f"#### {group}\n\n"
                    
                for doc in sorted(docs):
                    doc_name = Path(doc).stem
                    doc_title = self._get_document_title(doc)
                    new_content += f"- [{doc_title}]({doc})\n"
                    
                new_content += "\n"
                
        if removed_docs:
            new_content += "### 已删除文档\n\n"
            for doc in sorted(removed_docs):
                new_content += f"- ~~{doc}~~\n"
            new_content += "\n"
            
        # 追加到索引文件
        with open(self.index_file, 'a', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ 已添加 {len(new_docs)} 个新文档到索引")
        
        self.update_log['updates'].append({
            'type': 'index_update',
            'new_docs': list(new_docs),
            'removed_docs': list(removed_docs)
        })
        
    def _get_document_title(self, doc_path: str) -> str:
        """获取文档标题"""
        full_path = self.docs_path / doc_path
        
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 提取YAML中的title
                yaml_data = self._extract_yaml(content)
                if yaml_data and 'title' in yaml_data:
                    return yaml_data['title']
                    
                # 提取第一个标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    return title_match.group(1)
                    
            except:
                pass
                
        # 使用文件名作为标题
        return Path(doc_path).stem.replace('_', ' ')
        
    def _extract_yaml(self, content: str) -> dict:
        """提取YAML头部"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1]) or {}
                except:
                    pass
        return {}
        
    def _save_update_log(self):
        """保存更新日志"""
        log_path = self.base_path / "docs" / "09_AUDIT" / "STATE" / \
                  f"index_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.update_log, f, ensure_ascii=False, indent=2)
            
        print(f"✓ 更新日志已保存: {log_path}")

if __name__ == "__main__":
    updater = IndexAutoUpdater("d:/ZephyrAlpha")
    updater.run_auto_update()
