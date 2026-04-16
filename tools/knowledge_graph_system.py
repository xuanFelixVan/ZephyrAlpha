"""
知识图谱系统（简化版）

适用于个人开发、AI维护、个人使用场景
提供简单的知识关联和可视化功能

使用方法:
    python knowledge_graph_system.py --build
    python knowledge_graph_system.py --query "因子引擎"
    python knowledge_graph_system.py --visualize
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re


class SimpleKnowledgeGraph:
    """简化版知识图谱系统"""

    def __init__(self, project_root: str = "d:\\ZephyrAlpha"):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.graph_file = self.project_root / "docs" / "08_KNOWLEDGE" / "knowledge_graph.json"

        self.nodes = {}
        self.edges = defaultdict(list)
        self.tags_index = defaultdict(set)
        self.keywords_index = defaultdict(set)

    def build_graph(self):
        """构建知识图谱"""
        print("🔨 开始构建知识图谱...")

        self._scan_documents()
        self._extract_relationships()
        self._build_indices()
        self._save_graph()

        print(f"✅ 知识图谱构建完成！")
        print(f"   节点数: {len(self.nodes)}")
        print(f"   边数: {sum(len(v) for v in self.edges.values())}")

    def query(self, query_text: str, max_results: int = 10) -> List[Dict]:
        """查询知识图谱"""
        print(f"🔍 查询: {query_text}")

        keywords = self._extract_keywords(query_text)

        results = []
        for keyword in keywords:
            if keyword in self.keywords_index:
                for node_id in self.keywords_index[keyword]:
                    node = self.nodes[node_id]
                    results.append({
                        'node_id': node_id,
                        'title': node['title'],
                        'path': node['path'],
                        'relevance': self._calculate_relevance(node, keywords),
                        'related_nodes': self._get_related_nodes(node_id)
                    })

        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]

    def visualize(self, output_file: str = None):
        """生成可视化数据"""
        print("📊 生成可视化数据...")

        if output_file is None:
            output_file = self.project_root / "docs" / "08_KNOWLEDGE" / "knowledge_graph_visualization.json"

        vis_data = {
            'nodes': [],
            'edges': []
        }

        for node_id, node in self.nodes.items():
            vis_data['nodes'].append({
                'id': node_id,
                'label': node['title'],
                'type': node['type'],
                'tags': node.get('tags', [])
            })

        for source_id, targets in self.edges.items():
            for target_id, relation_type in targets:
                vis_data['edges'].append({
                    'source': source_id,
                    'target': target_id,
                    'type': relation_type
                })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(vis_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 可视化数据已保存: {output_file}")

        self._generate_mermaid_diagram(vis_data)

    def _scan_documents(self):
        """扫描文档"""
        print("  📄 扫描文档...")

        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue

            node_id = str(md_file.relative_to(self.project_root))

            metadata = self._extract_metadata(md_file)

            self.nodes[node_id] = {
                'id': node_id,
                'path': str(md_file),
                'title': metadata.get('title', md_file.stem),
                'type': self._determine_type(md_file),
                'tags': metadata.get('tags', []),
                'keywords': self._extract_keywords_from_file(md_file),
                'metadata': metadata
            }

    def _extract_metadata(self, file_path: Path) -> Dict:
        """提取文档元数据"""
        metadata = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    frontmatter = content[3:end]
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')

            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1)

        except Exception as e:
            print(f"    警告: 无法读取 {file_path}: {e}")

        return metadata

    def _determine_type(self, file_path: Path) -> str:
        """确定文档类型"""
        path_str = str(file_path)

        if 'FRAMEWORK' in path_str:
            return 'framework'
        elif 'KNOWLEDGE' in path_str:
            return 'knowledge'
        elif 'AUDIT' in path_str:
            return 'audit'
        elif 'ARCHITECTURE' in path_str:
            return 'architecture'
        else:
            return 'document'

    def _extract_keywords_from_file(self, file_path: Path) -> Set[str]:
        """从文件中提取关键词"""
        keywords = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            keywords.update(self._extract_keywords(content))

        except Exception as e:
            print(f"    警告: 无法提取关键词 {file_path}: {e}")

        return keywords

    def _extract_keywords(self, text: str) -> Set[str]:
        """提取关键词"""
        keywords = set()

        important_terms = [
            '因子', '策略', '风险', '组合', '投资', '研究',
            '因子引擎', '策略引擎', '风控引擎', '组合引擎',
            '动量', '价值', '质量', '规模', '波动',
            '回测', '优化', '监控', '审计', '合规',
            '知识库', '因子库', '策略库', '案例库',
            '架构', '模块', '数据流', '接口',
            'Python', 'API', 'REST', '数据库'
        ]

        for term in important_terms:
            if term in text:
                keywords.add(term)

        return keywords

    def _extract_relationships(self):
        """提取关系"""
        print("  🔗 提取关系...")

        for node_id, node in self.nodes.items():
            try:
                with open(node['path'], 'r', encoding='utf-8') as f:
                    content = f.read()

                link_pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
                matches = re.findall(link_pattern, content)

                for link_text, link_path in matches:
                    target_path = (Path(node['path']).parent / link_path).resolve()
                    target_id = str(target_path.relative_to(self.project_root))

                    if target_id in self.nodes:
                        self.edges[node_id].append((target_id, 'references'))

            except Exception as e:
                print(f"    警告: 无法提取关系 {node_id}: {e}")

    def _build_indices(self):
        """构建索引"""
        print("  🗂️ 构建索引...")

        for node_id, node in self.nodes.items():
            for tag in node.get('tags', []):
                self.tags_index[tag].add(node_id)

            for keyword in node.get('keywords', set()):
                self.keywords_index[keyword].add(node_id)

    def _calculate_relevance(self, node: Dict, query_keywords: Set[str]) -> float:
        """计算相关性"""
        node_keywords = node.get('keywords', set())
        intersection = query_keywords & node_keywords
        union = query_keywords | node_keywords

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _get_related_nodes(self, node_id: str, depth: int = 1) -> List[Dict]:
        """获取相关节点"""
        related = []

        for target_id, relation_type in self.edges.get(node_id, []):
            if target_id in self.nodes:
                related.append({
                    'node_id': target_id,
                    'title': self.nodes[target_id]['title'],
                    'relation': relation_type
                })

        return related

    def _save_graph(self):
        """保存知识图谱"""
        graph_data = {
            'nodes': self.nodes,
            'edges': dict(self.edges),
            'tags_index': {k: list(v) for k, v in self.tags_index.items()},
            'keywords_index': {k: list(v) for k, v in self.keywords_index.items()},
            'metadata': {
                'created_at': str(Path(__file__).stat().st_mtime),
                'node_count': len(self.nodes),
                'edge_count': sum(len(v) for v in self.edges.values())
            }
        }

        self.graph_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)

        print(f"  💾 知识图谱已保存: {self.graph_file}")

    def _generate_mermaid_diagram(self, vis_data: Dict):
        """生成Mermaid图表"""
        mermaid_file = self.project_root / "docs" / "08_KNOWLEDGE" / "knowledge_graph.md"

        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write("# 知识图谱可视化\n\n")
            f.write("```mermaid\n")
            f.write("graph TD\n")

            for node in vis_data['nodes'][:50]:
                node_label = node['label'].replace('"', "'")
                f.write(f'    {node["id"]}["{node_label}"]\n')

            for edge in vis_data['edges'][:100]:
                f.write(f'    {edge["source"]} --> {edge["target"]}\n')

            f.write("```\n")

        print(f"  📊 Mermaid图表已生成: {mermaid_file}")

    def load_graph(self):
        """加载知识图谱"""
        if not self.graph_file.exists():
            print("❌ 知识图谱文件不存在，请先构建")
            return False

        with open(self.graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)

        self.nodes = graph_data['nodes']
        self.edges = defaultdict(list, graph_data['edges'])
        self.tags_index = defaultdict(set, {k: set(v) for k, v in graph_data['tags_index'].items()})
        self.keywords_index = defaultdict(set, {k: set(v) for k, v in graph_data['keywords_index'].items()})

        print("✅ 知识图谱已加载")
        return True


def main():
    parser = argparse.ArgumentParser(description='知识图谱系统（简化版）')
    parser.add_argument('--build', action='store_true', help='构建知识图谱')
    parser.add_argument('--query', type=str, help='查询知识图谱')
    parser.add_argument('--visualize', action='store_true', help='生成可视化')
    parser.add_argument('--project-root', default='d:\\ZephyrAlpha',
                       help='项目根目录')

    args = parser.parse_args()

    kg = SimpleKnowledgeGraph(args.project_root)

    if args.build:
        kg.build_graph()
    elif args.query:
        if kg.load_graph():
            results = kg.query(args.query)
            print("\n查询结果:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   路径: {result['path']}")
                print(f"   相关性: {result['relevance']:.2f}")
                if result['related_nodes']:
                    print(f"   相关节点: {', '.join([n['title'] for n in result['related_nodes'][:3]])}")
    elif args.visualize:
        if kg.load_graph():
            kg.visualize()
    else:
        print("请指定操作: --build, --query, 或 --visualize")


if __name__ == '__main__':
    main()
