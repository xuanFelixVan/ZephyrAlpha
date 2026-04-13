#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 职责边界检查工具

功能: 检查模块职责边界清晰度、职责重叠、接口定义、依赖关系
版本: v1.0
创建日期: 2026-04-01
维护者: 蓝图架构师智能体

使用方法:
    python scripts/boundary_checker.py [--verbose] [--report] [--module MODULE_ID]

参数:
    --verbose    : 显示详细检查过程
    --report     : 生成边界检查报告
    --module MODULE_ID : 只检查指定模块
    --all        : 检查所有模块
    --help       : 显示帮助信息
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class Responsibility:
    """职责定义"""
    id: str
    description: str
    module_id: str
    category: str  # 核心职责/边界接口/非职责
    priority: str  # P0/P1/P2
    
@dataclass
class Interface:
    """接口定义"""
    name: str
    source_module: str
    target_module: str
    data_type: str
    format: str
    frequency: str
    description: str
    
@dataclass
class ModuleBoundary:
    """模块边界定义"""
    module_id: str
    name: str
    layer_id: int
    core_responsibilities: List[Responsibility] = field(default_factory=list)
    non_responsibilities: List[Responsibility] = field(default_factory=list)
    interfaces: List[Interface] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

class BoundaryChecker:
    """职责边界检查器"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.modules: Dict[str, ModuleBoundary] = {}
        self.responsibility_map: Dict[str, List[str]] = defaultdict(list)  # 职责->模块列表
        self.issues: List[Dict[str, Any]] = []
        
    def load_boundary_document(self) -> bool:
        """加载职责边界文档"""
        boundaries_path = self.project_root / "docs" / "01_FRAMEWORK" / "MODULE_RESPONSIBILITY_BOUNDARIES.md"
        
        if not boundaries_path.exists():
            self._add_issue("P0", "职责边界文档缺失", f"找不到职责边界文档: {boundaries_path}")
            return False
        
        try:
            with open(boundaries_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割模块章节
            module_sections = self._extract_module_sections(content)
            
            if self.verbose:
                print(f"   找到 {len(module_sections)} 个模块章节")
            
            for i, section in enumerate(module_sections):
                if self.verbose:
                    print(f"   解析第 {i+1} 个模块章节...")
                module_boundary = self._parse_module_section(section)
                if module_boundary:
                    self.modules[module_boundary.module_id] = module_boundary
                    if self.verbose:
                        print(f"     -> 成功解析模块: {module_boundary.module_id}")
            
            # 建立职责映射
            self._build_responsibility_map()
            
            if self.verbose:
                print(f"✅ 职责边界文档加载完成")
                print(f"   加载了 {len(self.modules)} 个模块的边界定义")
                for module_id, module_boundary in self.modules.items():
                    print(f"     - {module_id}: {len(module_boundary.core_responsibilities)} 项核心职责")
            
            return True
            
        except Exception as e:
            self._add_issue("P0", "职责边界文档解析错误", f"解析职责边界文档时出错: {e}")
            return False
    
    def check_responsibility_clarity(self) -> bool:
        """检查职责清晰度"""
        if self.verbose:
            print("🔍 检查职责清晰度...")
        
        issues_found = False
        
        for module_id, module_boundary in self.modules.items():
            # 检查是否有核心职责
            if not module_boundary.core_responsibilities:
                self._add_issue("P1", f"模块 {module_id} 无核心职责", 
                               f"模块 {module_id} 没有定义任何核心职责，职责边界不清晰")
                issues_found = True
            
            # 检查职责描述是否明确
            vague_responsibilities = []
            for resp in module_boundary.core_responsibilities:
                if self._is_vague_description(resp.description):
                    vague_responsibilities.append(resp.description)
            
            if vague_responsibilities:
                self._add_issue("P2", f"模块 {module_id} 职责描述模糊",
                               f"以下职责描述不够明确: {', '.join(vague_responsibilities[:3])}")
                issues_found = True
        
        return not issues_found
    
    def check_responsibility_overlap(self) -> bool:
        """检查职责重叠"""
        if self.verbose:
            print("🔍 检查职责重叠...")
        
        issues_found = False
        
        for responsibility, modules in self.responsibility_map.items():
            if len(modules) > 1:
                # 检查是否是合理的共享职责
                if not self._is_shared_responsibility_allowed(responsibility):
                    self._add_issue("P1", "职责重叠", 
                                   f"职责 '{self._truncate_text(responsibility, 50)}' 在多个模块中定义: {', '.join(modules)}")
                    issues_found = True
        
        return not issues_found
    
    def check_interface_completeness(self) -> bool:
        """检查接口完整性"""
        if self.verbose:
            print("🔍 检查接口完整性...")
        
        issues_found = False
        
        for module_id, module_boundary in self.modules.items():
            # 检查是否有接口定义
            if not module_boundary.interfaces:
                self._add_issue("P2", f"模块 {module_id} 无接口定义",
                               f"模块 {module_id} 没有定义任何接口，难以与其他模块集成")
                issues_found = True
            else:
                # 检查接口定义是否完整
                incomplete_interfaces = []
                for interface in module_boundary.interfaces:
                    if not all([interface.name, interface.source_module, interface.target_module, interface.data_type]):
                        incomplete_interfaces.append(interface.name)
                
                if incomplete_interfaces:
                    self._add_issue("P1", f"模块 {module_id} 接口定义不完整",
                                   f"以下接口定义不完整: {', '.join(incomplete_interfaces)}")
                    issues_found = True
        
        return not issues_found
    
    def check_dependency_circularity(self) -> bool:
        """检查依赖循环"""
        if self.verbose:
            print("🔍 检查依赖循环...")
        
        # 构建依赖图
        dependency_graph = {module_id: set() for module_id in self.modules}
        for module_id, module_boundary in self.modules.items():
            for dep in module_boundary.dependencies:
                if dep in self.modules:
                    dependency_graph[module_id].add(dep)
        
        # 检查循环依赖
        cycles = self._find_cycles(dependency_graph)
        
        if cycles:
            for cycle in cycles:
                self._add_issue("P0", "循环依赖", 
                               f"发现循环依赖: {' -> '.join(cycle)}")
            return False
        
        return True
    
    def check_module_isolation(self) -> bool:
        """检查模块隔离性"""
        if self.verbose:
            print("🔍 检查模块隔离性...")
        
        issues_found = False
        
        for module_id, module_boundary in self.modules.items():
            # 检查模块是否过于耦合
            coupling_score = self._calculate_coupling_score(module_boundary)
            
            if coupling_score > 0.7:  # 耦合度过高
                self._add_issue("P1", f"模块 {module_id} 耦合度过高",
                               f"模块 {module_id} 的耦合度评分为 {coupling_score:.2f} (高于0.7)，建议重构")
                issues_found = True
            
            # 检查模块职责是否单一
            responsibility_categories = set()
            for resp in module_boundary.core_responsibilities:
                category = self._categorize_responsibility(resp.description)
                responsibility_categories.add(category)
            
            if len(responsibility_categories) > 3:  # 职责类别过多
                self._add_issue("P2", f"模块 {module_id} 职责不够单一",
                               f"模块 {module_id} 涉及 {len(responsibility_categories)} 个职责类别: {', '.join(sorted(responsibility_categories)[:3])}")
                issues_found = True
        
        return not issues_found
    
    def check_boundary_alignment(self) -> bool:
        """检查边界对齐"""
        if self.verbose:
            print("🔍 检查边界对齐...")
        
        issues_found = False
        
        # 检查模块之间的边界是否清晰
        module_pairs = []
        for i, module_id1 in enumerate(self.modules.keys()):
            for module_id2 in list(self.modules.keys())[i+1:]:
                module_pairs.append((module_id1, module_id2))
        
        for module_id1, module_id2 in module_pairs:
            overlap_score = self._calculate_boundary_overlap(module_id1, module_id2)
            
            if overlap_score > 0.3:  # 边界重叠度过高
                self._add_issue("P1", f"模块边界重叠",
                               f"模块 {module_id1} 和 {module_id2} 的边界重叠度为 {overlap_score:.2f} (高于0.3)，建议重新划分职责")
                issues_found = True
        
        return not issues_found
    
    def _extract_module_sections(self, content: str) -> List[str]:
        """提取模块章节"""
        # 查找所有###开头的模块定义章节，匹配格式: ### 1. 因子库蓝图 (FACTOR_BACKTEST_001)
        pattern = r"(### \d+\. [^\n]+蓝图[^\n]*.*?)(?=### \d+\. |## |\Z)"
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches if match.strip()]
    
    def _parse_module_section(self, section: str) -> Optional[ModuleBoundary]:
        """解析模块章节"""
        try:
            # 提取模块ID - 首先尝试从标题括号中提取
            module_id = None
            module_id_match = re.search(r"### \d+\. [^(\n]+蓝图\s*\(([A-Z_][A-Z0-9_]*)\)", section)
            if module_id_match:
                module_id = module_id_match.group(1)
            else:
                # 如果标题中没有，尝试从表格中提取
                table_id_match = re.search(r"模块ID\s*[|:]\s*([A-Z_][A-Z0-9_]*)", section)
                if table_id_match:
                    module_id = table_id_match.group(1)
                else:
                    # 如果还是找不到，尝试搜索模块ID模式
                    id_search = re.search(r"([A-Z_][A-Z0-9_]{3,})", section)
                    if id_search:
                        module_id = id_search.group(1)
            
            if not module_id:
                return None  # 没有模块ID，跳过这个章节
            
            # 提取模块名称
            module_name_match = re.search(r"### \d+\. ([^(\n]+)", section)
            module_name = module_name_match.group(1).strip() if module_name_match else "未知模块"
            
            # 提取Layer定位
            layer_id = -1
            # 尝试从表格中提取
            layer_match = re.search(r"所属Layer\s*[|:]\s*Layer\s*(\d+)", section)
            if layer_match:
                layer_id = int(layer_match.group(1))
            else:
                # 尝试从文本中提取
                layer_text_match = re.search(r"Layer\s*(\d+)", section)
                if layer_text_match:
                    layer_id = int(layer_text_match.group(1))
            
            module_boundary = ModuleBoundary(
                module_id=module_id,
                name=module_name,
                layer_id=layer_id
            )
            
            # 提取核心职责
            core_section = self._extract_subsection(section, "核心职责")
            if core_section:
                responsibilities = self._parse_responsibilities(core_section, module_id, "核心职责")
                module_boundary.core_responsibilities.extend(responsibilities)
            
            # 提取非职责
            non_section = self._extract_subsection(section, "非职责")
            if non_section:
                non_responsibilities = self._parse_responsibilities(non_section, module_id, "非职责")
                module_boundary.non_responsibilities.extend(non_responsibilities)
            
            # 提取边界接口
            interface_section = self._extract_subsection(section, "边界接口")
            if interface_section:
                interfaces = self._parse_interfaces(interface_section, module_id)
                module_boundary.interfaces.extend(interfaces)
            
            # 提取依赖关系
            dependency_section = self._extract_subsection(section, "依赖关系")
            if dependency_section:
                dependencies = self._parse_dependencies(dependency_section)
                module_boundary.dependencies.extend(dependencies)
            
            return module_boundary
            
        except Exception as e:
            self._add_issue("P2", f"模块解析错误", f"解析模块章节时出错: {e}")
            return None
    
    def _parse_responsibilities(self, section: str, module_id: str, category: str) -> List[Responsibility]:
        """解析职责列表"""
        responsibilities = []
        
        # 查找表格格式的职责
        table_rows = self._extract_table_from_section(section)
        if table_rows and len(table_rows) > 1:
            headers = table_rows[0]
            
            # 确定职责描述列的位置
            description_col_idx = 0
            if "具体任务" in headers:
                description_col_idx = headers.index("具体任务")
            elif "职责领域" in headers:
                description_col_idx = headers.index("职责领域")
            
            for row in table_rows[1:]:  # 跳过表头
                if len(row) > description_col_idx:
                    resp_id = f"{module_id}_{category}_{len(responsibilities)}"
                    description = row[description_col_idx].strip()
                    
                    # 确定优先级
                    priority = "P1"
                    if "必须" in description or "核心" in description or "核心职责" in category:
                        priority = "P0"
                    elif "建议" in description or "可选" in description:
                        priority = "P2"
                    
                    responsibilities.append(Responsibility(
                        id=resp_id,
                        description=description,
                        module_id=module_id,
                        category=category,
                        priority=priority
                    ))
        
        # 查找列表格式的职责
        list_items = re.findall(r"[-*]\s*(.*?)(?=\n[-*]|\n\n|\Z)", section, re.DOTALL)
        for item in list_items:
            if item.strip() and not item.strip().startswith("|"):
                resp_id = f"{module_id}_{category}_{len(responsibilities)}"
                
                # 确定优先级
                priority = "P1"
                if "必须" in item or "核心" in item:
                    priority = "P0"
                elif "建议" in item or "可选" in item:
                    priority = "P2"
                
                responsibilities.append(Responsibility(
                    id=resp_id,
                    description=item.strip(),
                    module_id=module_id,
                    category=category,
                    priority=priority
                ))
        
        return responsibilities
    
    def _parse_interfaces(self, section: str, module_id: str) -> List[Interface]:
        """解析接口定义"""
        interfaces = []
        
        # 查找表格格式的接口
        table_rows = self._extract_table_from_section(section)
        if table_rows and len(table_rows) > 1:
            headers = table_rows[0]
            
            # 确定列索引
            col_mapping = {}
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if "接口" in header and "类型" in header:
                    col_mapping["type"] = i
                elif "接口" in header and "内容" in header:
                    col_mapping["content"] = i
                elif "对接" in header or "模块" in header:
                    col_mapping["target"] = i
                elif "数据" in header or "格式" in header:
                    col_mapping["format"] = i
                elif "频率" in header or "频次" in header:
                    col_mapping["frequency"] = i
                elif "说明" in header or "描述" in header:
                    col_mapping["description"] = i
            
            for row in table_rows[1:]:
                interface_name = ""
                target_module = "未知"
                data_type = "未知"
                data_format = "未知"
                frequency = "未知"
                description = ""
                
                # 根据列映射提取数据
                if "content" in col_mapping and col_mapping["content"] < len(row):
                    interface_name = row[col_mapping["content"]].strip()
                
                if "target" in col_mapping and col_mapping["target"] < len(row):
                    target_module = row[col_mapping["target"]].strip()
                
                if "format" in col_mapping and col_mapping["format"] < len(row):
                    data_format = row[col_mapping["format"]].strip()
                
                if "frequency" in col_mapping and col_mapping["frequency"] < len(row):
                    frequency = row[col_mapping["frequency"]].strip()
                
                if "description" in col_mapping and col_mapping["description"] < len(row):
                    description = row[col_mapping["description"]].strip()
                
                # 如果接口名称为空，使用内容列
                if not interface_name and "content" in col_mapping and col_mapping["content"] < len(row):
                    interface_name = row[col_mapping["content"]].strip()
                
                interfaces.append(Interface(
                    name=interface_name or f"接口_{len(interfaces)}",
                    source_module=module_id,
                    target_module=target_module,
                    data_type=data_type,
                    format=data_format,
                    frequency=frequency,
                    description=description
                ))
        
        return interfaces
    
    def _parse_dependencies(self, section: str) -> List[str]:
        """解析依赖关系"""
        dependencies = []
        
        # 查找依赖列表
        list_items = re.findall(r"[-*]\s*([A-Z_]+[A-Z0-9_]*)", section)
        dependencies.extend(list_items)
        
        # 查找文本中的模块ID
        module_id_pattern = r"[A-Z_]+[A-Z0-9_]*"
        text_matches = re.findall(module_id_pattern, section)
        dependencies.extend([m for m in text_matches if m not in dependencies])
        
        return list(set(dependencies))
    
    def _extract_subsection(self, section: str, subsection_title: str) -> Optional[str]:
        """提取子章节内容"""
        # 匹配格式: #### ✅ 核心职责 (必须负责) 或 #### 核心职责
        # 先尝试匹配带符号的标题
        patterns = [
            rf"####\s*[✅❌⚠️⚡]*\s*{re.escape(subsection_title)}[^\n]*\n+([\s\S]*?)(?=####\s+|\Z)",
            rf"####\s*{re.escape(subsection_title)}[^\n]*\n+([\s\S]*?)(?=####\s+|\Z)",
            rf"####\s*[✅❌⚠️⚡]*\s*{re.escape(subsection_title)}[^\n]*\n+([\s\S]*?)(?=###\s+|\Z)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, section, re.MULTILINE)
            if match:
                content = match.group(1).strip()
                if content:
                    return content
        
        return None
    
    def _extract_table_from_section(self, section: str) -> Optional[List[List[str]]]:
        """从章节中提取表格"""
        # 查找表格 - 匹配以|开头和结尾的行
        table_pattern = r"(\|.*?\|(?:\n|$))+"
        table_match = re.search(table_pattern, section, re.MULTILINE)
        if not table_match:
            return None
        
        table_content = table_match.group(0)
        rows = []
        
        for line in table_content.split('\n'):
            line = line.strip()
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
        
        return rows if len(rows) > 1 else None
    
    def _build_responsibility_map(self):
        """建立职责映射表"""
        for module_id, module_boundary in self.modules.items():
            for resp in module_boundary.core_responsibilities:
                # 标准化职责描述用于比较
                normalized_desc = self._normalize_responsibility(resp.description)
                self.responsibility_map[normalized_desc].append(module_id)
    
    def _is_vague_description(self, description: str) -> bool:
        """检查描述是否模糊"""
        vague_keywords = ["相关", "协助", "配合", "支持", "涉及", "参与", "帮助"]
        return any(keyword in description for keyword in vague_keywords)
    
    def _is_shared_responsibility_allowed(self, responsibility: str) -> bool:
        """检查是否是允许共享的职责"""
        # 某些职责允许共享，如"数据验证"、"错误处理"
        shared_allowed = ["验证", "检查", "审计", "监控", "日志", "错误", "异常", "测试"]
        return any(keyword in responsibility for keyword in shared_allowed)
    
    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """查找循环依赖"""
        def dfs(node, path, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        visited = set()
        cycles = []
        
        for node in graph:
            if node not in visited:
                dfs(node, [node], visited, set())
        
        return cycles
    
    def _calculate_coupling_score(self, module_boundary: ModuleBoundary) -> float:
        """计算模块耦合度评分"""
        total_dependencies = len(module_boundary.dependencies)
        total_interfaces = len(module_boundary.interfaces)
        
        # 简单的耦合度计算公式
        coupling_score = (total_dependencies * 0.6 + total_interfaces * 0.4) / 10
        return min(coupling_score, 1.0)  # 限制在0-1之间
    
    def _calculate_boundary_overlap(self, module_id1: str, module_id2: str) -> float:
        """计算两个模块的边界重叠度"""
        module1 = self.modules.get(module_id1)
        module2 = self.modules.get(module_id2)
        
        if not module1 or not module2:
            return 0.0
        
        # 比较职责相似度
        resp1 = {self._normalize_responsibility(r.description) for r in module1.core_responsibilities}
        resp2 = {self._normalize_responsibility(r.description) for r in module2.core_responsibilities}
        
        if not resp1 or not resp2:
            return 0.0
        
        intersection = resp1.intersection(resp2)
        union = resp1.union(resp2)
        
        return len(intersection) / len(union)
    
    def _categorize_responsibility(self, description: str) -> str:
        """对职责进行分类"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ["计算", "生成", "创建", "构建"]):
            return "计算类"
        elif any(keyword in description_lower for keyword in ["存储", "保存", "管理", "维护"]):
            return "存储类"
        elif any(keyword in description_lower for keyword in ["验证", "检查", "审计", "测试"]):
            return "验证类"
        elif any(keyword in description_lower for keyword in ["分析", "评估", "统计", "报告"]):
            return "分析类"
        elif any(keyword in description_lower for keyword in ["执行", "运行", "操作", "处理"]):
            return "执行类"
        elif any(keyword in description_lower for keyword in ["接口", "通信", "传输", "交换"]):
            return "接口类"
        else:
            return "其他类"
    
    def _normalize_responsibility(self, description: str) -> str:
        """标准化职责描述"""
        # 移除优先级标记和特殊字符
        normalized = re.sub(r'[P0-9]+\s*:', '', description)
        normalized = re.sub(r'[【】（）()「」《》]', '', normalized)
        normalized = normalized.strip().lower()
        return normalized
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _add_issue(self, priority: str, title: str, description: str):
        """添加问题"""
        self.issues.append({
            "priority": priority,
            "title": title,
            "description": description
        })
        
        if self.verbose:
            print(f"  {priority}: {title}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """生成边界检查报告"""
        report = []
        
        # 报告头
        report.append("# 职责边界检查报告")
        report.append(f"> 生成时间: 2026-04-01")
        report.append(f"> 系统版本: v5.2")
        report.append(f"> 检查工具: boundary_checker.py v1.0")
        report.append("")
        
        # 概要统计
        total_modules = len(self.modules)
        total_responsibilities = sum(len(m.core_responsibilities) for m in self.modules.values())
        total_interfaces = sum(len(m.interfaces) for m in self.modules.values())
        
        report.append("## 📊 概要统计")
        report.append("")
        report.append("| 指标 | 数量 |")
        report.append("|------|------|")
        report.append(f"| 检查模块数 | {total_modules} |")
        report.append(f"| 核心职责总数 | {total_responsibilities} |")
        report.append(f"| 接口总数 | {total_interfaces} |")
        report.append(f"| 发现的问题数 | {len(self.issues)} |")
        report.append("")
        
        # 模块边界概览
        report.append("## 🏗️ 模块边界概览")
        report.append("")
        for module_id, module_boundary in self.modules.items():
            report.append(f"### {module_id}: {module_boundary.name}")
            report.append(f"- **Layer**: {module_boundary.layer_id}")
            report.append(f"- **核心职责**: {len(module_boundary.core_responsibilities)} 项")
            report.append(f"- **接口**: {len(module_boundary.interfaces)} 个")
            report.append(f"- **依赖**: {len(module_boundary.dependencies)} 个模块")
            report.append("")
        
        # 职责重叠分析
        overlapping_responsibilities = {}
        for responsibility, modules in self.responsibility_map.items():
            if len(modules) > 1:
                overlapping_responsibilities[responsibility] = modules
        
        if overlapping_responsibilities:
            report.append("## ⚠️ 职责重叠分析")
            report.append("")
            report.append("以下职责在多个模块中定义:")
            report.append("")
            for responsibility, modules in list(overlapping_responsibilities.items())[:10]:  # 只显示前10个
                report.append(f"- **{self._truncate_text(responsibility, 60)}**")
                report.append(f"  在模块: {', '.join(modules)}")
                report.append("")
        
        # 问题分析
        if self.issues:
            report.append("## 🔍 发现的问题")
            report.append("")
            
            # 按优先级分组
            priorities = {"P0": [], "P1": [], "P2": []}
            for issue in self.issues:
                priorities[issue["priority"]].append(issue)
            
            for priority in ["P0", "P1", "P2"]:
                if priorities[priority]:
                    report.append(f"### {priority} 优先级问题 ({len(priorities[priority])}个)")
                    report.append("")
                    for issue in priorities[priority]:
                        report.append(f"#### {issue['title']}")
                        report.append(f"- **描述**: {issue['description']}")
                        report.append("")
        
        # 改进建议
        report.append("## 💡 改进建议")
        report.append("")
        
        if any(issue["priority"] == "P0" for issue in self.issues):
            report.append("1. **立即修复P0问题** - 特别是循环依赖和关键职责缺失")
        
        if any(issue["priority"] == "P1" for issue in self.issues):
            report.append("2. **本周内修复P1问题** - 特别是职责重叠和接口不完整问题")
        
        if overlapping_responsibilities:
            report.append("3. **重新划分重叠职责** - 明确每个职责的唯一负责模块")
        
        # 检查是否存在无接口模块
        modules_without_interfaces = [m.module_id for m in self.modules.values() if not m.interfaces]
        if modules_without_interfaces:
            report.append(f"4. **为无接口模块定义接口** - 以下模块需要定义接口: {', '.join(modules_without_interfaces)}")
        
        # 将报告写入文件或返回
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"报告已保存到: {output_path}")
        
        return report_text
    
    def run_checks(self, module_id: Optional[str] = None) -> bool:
        """运行边界检查"""
        print("🔍 开始职责边界检查...")
        print(f"项目根目录: {self.project_root}")
        print("-" * 60)
        
        # 加载边界文档
        if not self.load_boundary_document():
            print("❌ 无法加载职责边界文档")
            return False
        
        # 执行各项检查
        results = []
        
        results.append(self.check_responsibility_clarity())
        results.append(self.check_responsibility_overlap())
        results.append(self.check_interface_completeness())
        results.append(self.check_dependency_circularity())
        results.append(self.check_module_isolation())
        results.append(self.check_boundary_alignment())
        
        # 汇总结果
        success = all(results)
        
        print("-" * 60)
        if success:
            print("✅ 职责边界检查完成，所有检查通过")
        else:
            print(f"⚠️ 职责边界检查完成，发现 {len(self.issues)} 个问题")
            print("   使用 --verbose 查看详细问题")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清风量化系统 - 职责边界检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    # 完整检查
    python scripts/boundary_checker.py
    
    # 详细输出
    python scripts/boundary_checker.py --verbose
    
    # 生成报告
    python scripts/boundary_checker.py --report
    
    # 只检查指定模块
    python scripts/boundary_checker.py --module FACTOR_BACKTEST_001
    
    # 所有检查
    python scripts/boundary_checker.py --all
        """
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细检查过程"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成边界检查报告"
    )
    
    parser.add_argument(
        "--module",
        type=str,
        help="只检查指定模块"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="检查所有模块"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建检查器
    checker = BoundaryChecker(
        project_root=project_root,
        verbose=args.verbose
    )
    
    # 运行检查
    try:
        success = checker.run_checks(module_id=args.module)
        
        # 生成报告
        if args.report:
            report_path = project_root / "docs" / "09_AUDIT" / "BOUNDARY_CHECK_REPORT.md"
            checker.generate_report(report_path)
        
        # 显示问题概要
        if checker.issues:
            print("\n📋 问题概要:")
            for issue in checker.issues[:10]:  # 只显示前10个
                print(f"  {issue['priority']}: {issue['title']}")
            
            if len(checker.issues) > 10:
                print(f"  ... 和其他 {len(checker.issues) - 10} 个问题")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断检查操作")
        return 1
    except Exception as e:
        print(f"检查过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())