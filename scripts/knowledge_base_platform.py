#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库平台搭建脚本
功能：
1. 知识库目录结构创建
2. 知识条目导入
3. 知识索引生成
4. 知识检索接口
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import shutil

@dataclass
class KnowledgeEntry:
    id: str
    title: str
    category: str
    subcategory: str
    content: str
    tags: List[str]
    created_date: str
    updated_date: str
    author: str
    status: str

class KnowledgeBasePlatform:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.kb_dir = self.base_dir / "docs/08_KNOWLEDGE_BASE"
        self.config_file = self.kb_dir / "knowledge_base_config.yaml"
        self.config = self._load_config()
        self.entries: List[KnowledgeEntry] = []
    
    def _load_config(self) -> Dict:
        if not self.config_file.exists():
            return self._create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> Dict:
        default_config = {
            'knowledge_base': {
                'name': 'ZephyrAlpha知识库',
                'version': '1.0.0',
                'description': '专业量化机构知识库平台',
                'categories': {
                    '01_TECHNICAL_KNOWLEDGE': {
                        'name': '技术知识',
                        'description': '系统架构、技术方案、最佳实践',
                        'subcategories': {
                            'ARCHITECTURE': '架构设计',
                            'ALGORITHMS': '算法实现',
                            'BEST_PRACTICES': '最佳实践',
                            'TECHNICAL_SPECS': '技术规范'
                        }
                    },
                    '02_BUSINESS_KNOWLEDGE': {
                        'name': '业务知识',
                        'description': '业务流程、业务规则、业务场景',
                        'subcategories': {
                            'TRADING_STRATEGIES': '交易策略',
                            'RISK_MANAGEMENT': '风险管理',
                            'PORTFOLIO_MANAGEMENT': '组合管理',
                            'MARKET_ANALYSIS': '市场分析'
                        }
                    },
                    '03_OPERATIONS_KNOWLEDGE': {
                        'name': '运维知识',
                        'description': '部署流程、监控配置、故障处理',
                        'subcategories': {
                            'DEPLOYMENT': '部署运维',
                            'MONITORING': '监控告警',
                            'TROUBLESHOOTING': '故障处理',
                            'PERFORMANCE': '性能优化'
                        }
                    },
                    '04_MANAGEMENT_KNOWLEDGE': {
                        'name': '管理知识',
                        'description': '项目管理、团队协作、流程规范',
                        'subcategories': {
                            'PROJECT_MANAGEMENT': '项目管理',
                            'TEAM_COLLABORATION': '团队协作',
                            'PROCESS_STANDARDS': '流程规范',
                            'DOCUMENTATION': '文档管理'
                        }
                    }
                }
            },
            'settings': {
                'auto_index': True,
                'search_enabled': True,
                'version_control': True,
                'backup_enabled': True
            }
        }
        
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        
        return default_config
    
    def create_directory_structure(self):
        print("\n=== 创建知识库目录结构 ===\n")
        
        categories = self.config['knowledge_base']['categories']
        
        for category_id, category_info in categories.items():
            category_dir = self.kb_dir / category_id
            category_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建分类目录: {category_info['name']}")
            
            index_file = category_dir / "INDEX.md"
            if not index_file.exists():
                self._create_category_index(category_id, category_info, index_file)
            
            for subcategory_id, subcategory_name in category_info['subcategories'].items():
                subcategory_dir = category_dir / subcategory_id
                subcategory_dir.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ 创建子分类目录: {subcategory_name}")
        
        print(f"\n目录结构创建完成")
    
    def _create_category_index(self, category_id: str, category_info: Dict, index_file: Path):
        index_content = f"""---
module_id: {category_id}_INDEX_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 知识管理团队
standard_type: 专业量化机构索引
applicable_scope: {category_info['name']}
---

# {category_info['name']}索引

## 📋 目录概要

**目录路径**: `docs/08_KNOWLEDGE_BASE/{category_id}/`
**目录职责**: {category_info['description']}
**知识条目**: 0个

---

## 📁 知识分类

"""
        
        for subcategory_id, subcategory_name in category_info['subcategories'].items():
            index_content += f"### {subcategory_name}\n\n"
            index_content += f"| 知识ID | 知识名称 | 描述 | 状态 |\n"
            index_content += f"|--------|---------|------|------|\n"
            index_content += f"| **{category_id[:2]}_{subcategory_id[:4]}_001** | [知识条目示例]({subcategory_id}/EXAMPLE_KNOWLEDGE.md) | 示例知识条目 | 📝 待创建 |\n\n"
        
        index_content += f"""---

## 📊 知识统计

### 总体统计

| 指标 | 数值 |
|------|------|
| **总知识条目** | 0 |
| **活跃条目** | 0 |
| **归档条目** | 0 |

---

## 🔗 相关文档

- [知识库总索引](../INDEX.md)
- [知识库架构设计](../KNOWLEDGE_BASE_ARCHITECTURE.md)

---

## 📝 维护记录

| 日期 | 操作 | 操作人 | 备注 |
|------|------|--------|------|
| {datetime.now().strftime('%Y-%m-%d')} | 创建索引 | Knowledge Platform | 初始创建{category_info['name']}索引 |

---

**知识库状态**: ✅ 已创建
**知识条目**: 0个
**知识覆盖率**: 0%
"""
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
    
    def import_knowledge_entries(self, entries: List[Dict]):
        print(f"\n=== 导入知识条目 ===\n")
        print(f"导入条目数: {len(entries)}")
        
        for entry_data in entries:
            entry = KnowledgeEntry(
                id=entry_data['id'],
                title=entry_data['title'],
                category=entry_data['category'],
                subcategory=entry_data['subcategory'],
                content=entry_data['content'],
                tags=entry_data.get('tags', []),
                created_date=datetime.now().strftime('%Y-%m-%d'),
                updated_date=datetime.now().strftime('%Y-%m-%d'),
                author=entry_data.get('author', 'Knowledge Platform'),
                status=entry_data.get('status', 'Active')
            )
            
            self._save_knowledge_entry(entry)
            self.entries.append(entry)
            print(f"✅ 导入条目: {entry.title}")
        
        print(f"\n导入完成: {len(self.entries)}个条目")
    
    def _save_knowledge_entry(self, entry: KnowledgeEntry):
        category_dir = self.kb_dir / entry.category / entry.subcategory
        category_dir.mkdir(parents=True, exist_ok=True)
        
        entry_file = category_dir / f"{entry.id}.md"
        
        entry_content = f"""---
module_id: {entry.id}
version: 1.0.0
status: {entry.status}
created_date: {entry.created_date}
last_updated: {entry.updated_date}
owner: {entry.author}
standard_type: 专业量化机构知识
applicable_scope: {entry.category}
---

# {entry.title}

## 📋 知识概要

**知识分类**: {entry.category}
**知识子类**: {entry.subcategory}
**知识标签**: {', '.join(entry.tags)}

---

## 📝 知识内容

{entry.content}

---

## 🔗 相关知识

- [相关知识1](../RELATED_KNOWLEDGE_001.md)
- [相关知识2](../RELATED_KNOWLEDGE_002.md)

---

## 📝 维护记录

| 日期 | 操作 | 操作人 | 备注 |
|------|------|--------|------|
| {entry.created_date} | 创建条目 | {entry.author} | 初始创建知识条目 |

---

**知识状态**: ✅ {entry.status}
**知识版本**: v1.0.0
**最后更新**: {entry.updated_date}
"""
        
        with open(entry_file, 'w', encoding='utf-8') as f:
            f.write(entry_content)
    
    def generate_search_index(self):
        print(f"\n=== 生成搜索索引 ===\n")
        
        search_index = {
            'version': '1.0.0',
            'generated_at': datetime.now().isoformat(),
            'total_entries': len(self.entries),
            'entries': []
        }
        
        for entry in self.entries:
            search_index['entries'].append({
                'id': entry.id,
                'title': entry.title,
                'category': entry.category,
                'subcategory': entry.subcategory,
                'tags': entry.tags,
                'content_preview': entry.content[:200]
            })
        
        index_file = self.kb_dir / "search_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 搜索索引已生成: {index_file}")
        print(f"  总条目数: {len(self.entries)}")
    
    def get_platform_stats(self) -> Dict:
        stats = {
            'total_categories': len(self.config['knowledge_base']['categories']),
            'total_entries': len(self.entries),
            'entries_by_category': {},
            'entries_by_status': {}
        }
        
        for entry in self.entries:
            stats['entries_by_category'][entry.category] = \
                stats['entries_by_category'].get(entry.category, 0) + 1
            
            stats['entries_by_status'][entry.status] = \
                stats['entries_by_status'].get(entry.status, 0) + 1
        
        return stats

def main():
    base_dir = Path("D:/ZephyrAlpha")
    platform = KnowledgeBasePlatform(base_dir)
    
    platform.create_directory_structure()
    
    sample_entries = [
        {
            'id': 'TK_ARCH_001',
            'title': '系统架构设计原则',
            'category': '01_TECHNICAL_KNOWLEDGE',
            'subcategory': 'ARCHITECTURE',
            'content': '系统架构设计的基本原则包括：模块化设计、高内聚低耦合、可扩展性、可维护性等。',
            'tags': ['架构', '设计原则', '系统设计'],
            'author': '架构团队'
        },
        {
            'id': 'TK_ALGO_001',
            'title': '因子计算算法',
            'category': '01_TECHNICAL_KNOWLEDGE',
            'subcategory': 'ALGORITHMS',
            'content': '因子计算是量化投资的核心算法，包括动量因子、价值因子、质量因子等。',
            'tags': ['算法', '因子计算', '量化投资'],
            'author': '算法团队'
        }
    ]
    
    platform.import_knowledge_entries(sample_entries)
    platform.generate_search_index()
    
    stats = platform.get_platform_stats()
    print(f"\n=== 知识库平台统计 ===")
    print(f"总分类数: {stats['total_categories']}")
    print(f"总条目数: {stats['total_entries']}")
    print(f"按分类统计: {stats['entries_by_category']}")

if __name__ == "__main__":
    main()
