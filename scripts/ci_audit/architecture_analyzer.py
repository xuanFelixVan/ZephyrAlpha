#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 架构分析工具

功能: 分析三级时间框架融合架构的完整性、模块定位、数据流、接口定义
版本: v1.1
创建日期: 2026-04-01
维护者: 蓝图架构师智能体

使用方法:
    python scripts/architecture_analyzer.py [--verbose] [--report] [--check-layer N]

参数:
    --verbose    : 显示详细分析过程
    --report     : 生成HTML分析报告
    --check-layer N : 只检查指定Layer (0-8，技术层参考)
    --all        : 检查所有方面
    --help       : 显示帮助信息

架构说明:
    - 业务架构: 三级时间框架融合架构 (宏观配置层/中观策略层/微观执行层)
    - 技术架构: Layer 0-8技术流水线 (技术实现参考)
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
import yaml

@dataclass
class LayerDefinition:
    """Layer定义"""
    layer_id: int
    name: str
    description: str
    modules: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    
@dataclass
class ModuleDefinition:
    """模块定义"""
    module_id: str
    name: str
    layer_id: int
    responsibilities: List[str] = field(default_factory=list)
    interfaces: Dict[str, List[str]] = field(default_factory=dict)  # 输入/输出接口
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他模块
    
@dataclass
class DataFlow:
    """数据流定义"""
    source_layer: int
    source_module: Optional[str]
    target_layer: int
    target_module: Optional[str]
    data_type: str
    format: str
    frequency: str
    quality_requirements: str

class ArchitectureAnalyzer:
    """架构分析器"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.layers: Dict[int, LayerDefinition] = {}
        self.modules: Dict[str, ModuleDefinition] = {}
        self.data_flows: List[DataFlow] = []
        self.issues: List[Dict[str, Any]] = []
        
        # Layer 0-8标准定义
        self._initialize_standard_layers()
        
    def _initialize_standard_layers(self):
        """初始化Layer 0-8标准定义"""
        standard_layers = {
            0: LayerDefinition(0, "数据源层", "原始数据获取层，包括QMT、iFind、SuperCommand等数据源"),
            1: LayerDefinition(1, "数据预处理层", "数据清洗、标准化、对齐、验证"),
            2: LayerDefinition(2, "Alpha因子层", "5700+因子计算、存储、IC分析"),
            3: LayerDefinition(3, "舆情分析层", "新闻情感分析、事件驱动、舆情信号生成"),
            4: LayerDefinition(4, "机器学习层", "AI因子挖掘、时序预测、特征工程"),
            5: LayerDefinition(5, "策略执行层", "策略逻辑开发、回测执行、交易执行"),
            6: LayerDefinition(6, "组合优化层", "组合权重优化、风险模型、约束求解"),
            7: LayerDefinition(7, "AI报告层", "绩效归因、自动报告生成、市场分析"),
            8: LayerDefinition(8, "人机交互层", "可视化仪表板、授权确认、监控告警、人机辩论")
        }
        self.layers = standard_layers
        
    def analyze_architecture_document(self):
        """分析ARCHITECTURE.md文档"""
        arch_path = self.project_root / "docs" / "01_FRAMEWORK" / "ARCHITECTURE.md"
        
        if not arch_path.exists():
            self._add_issue("P0", "架构文档缺失", f"找不到架构文档: {arch_path}")
            return False
        
        try:
            with open(arch_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查Layer 0-8是否完整定义
            layer_patterns = {}
            for layer_id in range(9):
                pattern = rf"Layer {layer_id}: ([^(\n]+)"
                match = re.search(pattern, content)
                if match:
                    layer_name = match.group(1).strip()
                    layer_patterns[layer_id] = layer_name
                else:
                    self._add_issue("P1", f"Layer {layer_id}未定义", f"架构文档中缺少Layer {layer_id}的定义")
            
            # 检查数据流图
            dataflow_section = self._extract_section(content, "4. 跨层级数据流")
            if not dataflow_section:
                self._add_issue("P1", "数据流图缺失", "架构文档中缺少跨层级数据流定义")
            
            # 检查数据接口表
            interface_table = self._extract_table(content, "关键数据接口")
            if not interface_table or len(interface_table) < 5:
                self._add_issue("P1", "数据接口定义不完整", "关键数据接口表缺失或内容不足")
            
            # 检查模块定义
            module_sections = self._extract_all_sections_with_pattern(content, r"Layer \d+: [^(\n]+")
            
            if self.verbose:
                print(f"✅ 架构文档分析完成")
                print(f"   发现 {len(layer_patterns)} 个Layer定义")
                print(f"   发现 {len(module_sections)} 个模块定义部分")
            
            return True
            
        except Exception as e:
            self._add_issue("P0", "架构文档解析错误", f"解析架构文档时出错: {e}")
            return False
    
    def analyze_module_boundaries(self):
        """分析模块职责边界文档"""
        boundaries_path = self.project_root / "docs" / "01_FRAMEWORK" / "MODULE_RESPONSIBILITY_BOUNDARIES.md"
        
        if not boundaries_path.exists():
            self._add_issue("P0", "职责边界文档缺失", f"找不到职责边界文档: {boundaries_path}")
            return False
        
        try:
            with open(boundaries_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取模块定义 - 匹配格式: ### 1. 因子库蓝图 (FACTOR_BACKTEST_001)
            module_sections = self._extract_all_sections_with_pattern(content, r"### \d+\. ([^(\n]+)蓝图")
            
            for section in module_sections:
                # 提取模块ID - 从标题括号中或从表格中提取
                module_id = None
                
                # 尝试从标题括号中提取: (FACTOR_BACKTEST_001)
                title_match = re.search(r"### \d+\. [^(\n]+蓝图\s*\(([A-Z_][A-Z0-9_]*)\)", section)
                if title_match:
                    module_id = title_match.group(1)
                else:
                    # 尝试从表格中提取模块ID
                    module_id_match = re.search(r"模块\s*\|\s*模块ID\s*\|\s*所属Layer", section)
                    if module_id_match:
                        # 查找表格中的模块ID
                        table_match = re.search(r"\*\*因子库模块\*\*\s*\|\s*([A-Z_][A-Z0-9_]*)\s*\|\s*Layer", section)
                        if table_match:
                            module_id = table_match.group(1)
                
                if not module_id:
                    # 如果还是找不到，尝试从章节内容中搜索模块ID模式
                    id_match = re.search(r"([A-Z_][A-Z0-9_]{3,})", section)
                    if id_match:
                        module_id = id_match.group(1)
                    else:
                        continue  # 跳过没有模块ID的章节
                
                # 提取Layer定位
                layer_id = -1
                # 尝试从表格中提取
                layer_match = re.search(r"所属Layer\s*\|\s*Layer\s*(\d+)", section)
                if layer_match:
                    layer_id = int(layer_match.group(1))
                else:
                    # 尝试从文本中提取
                    layer_text_match = re.search(r"Layer\s*(\d+)", section)
                    if layer_text_match:
                        layer_id = int(layer_text_match.group(1))
                
                # 提取核心职责 - 从表格中提取
                responsibilities = []
                # 查找核心职责表格
                core_section = self._extract_subsection(section, "核心职责")
                if core_section:
                    # 从表格中提取职责
                    table_rows = self._extract_table_from_section(core_section)
                    if table_rows and len(table_rows) > 1:
                        for row in table_rows[1:]:  # 跳过表头
                            if len(row) >= 2:
                                responsibility = f"{row[0]}: {row[1]}"
                                responsibilities.append(responsibility)
                
                # 创建模块定义
                if module_id not in self.modules:
                    module_name = self._extract_module_name(section)
                    self.modules[module_id] = ModuleDefinition(
                        module_id=module_id,
                        name=module_name,
                        layer_id=layer_id,
                        responsibilities=responsibilities
                    )
                    
                    # 添加到对应的Layer
                    if 0 <= layer_id <= 8:
                        self.layers[layer_id].modules.append(module_id)
            
            # 检查职责重叠
            self._check_responsibility_overlap()
            
            if self.verbose:
                print(f"✅ 职责边界分析完成")
                print(f"   发现 {len(self.modules)} 个模块定义")
                for module_id, module_def in self.modules.items():
                    print(f"     - {module_id}: Layer {module_def.layer_id}, {len(module_def.responsibilities)} 项职责")
            
            return True
            
        except Exception as e:
            self._add_issue("P0", "职责边界文档解析错误", f"解析职责边界文档时出错: {e}")
            return False
    
    def analyze_system_manifest(self):
        """分析System_Manifest.md系统总索引"""
        manifest_path = self.project_root / "docs" / "System_Manifest.md"
        
        if not manifest_path.exists():
            self._add_issue("P0", "系统总索引缺失", f"找不到系统总索引: {manifest_path}")
            return False
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查蓝图索引
            blueprint_section = self._extract_section(content, "模块蓝图索引")
            if not blueprint_section:
                # 也尝试查找"蓝图索引"作为备选
                blueprint_section = self._extract_section(content, "蓝图索引")
                if not blueprint_section:
                    self._add_issue("P1", "蓝图索引缺失", "系统总索引中缺少模块蓝图索引部分")
            
            # 检查模块映射表
            module_table = self._extract_table(content, "模块映射表")
            if not module_table or len(module_table) < 5:
                self._add_issue("P1", "模块映射表不完整", "系统总索引中模块映射表缺失或内容不足")
            
            # 验证所有蓝图文档都存在
            blueprint_matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", blueprint_section or "")
            for match in blueprint_matches:
                blueprint_name, blueprint_path = match
                full_path = self.project_root / blueprint_path
                if not full_path.exists():
                    self._add_issue("P1", "蓝图文档不存在", f"索引中引用的蓝图文档不存在: {blueprint_path}")
            
            if self.verbose:
                print(f"✅ 系统总索引分析完成")
                print(f"   发现 {len(blueprint_matches)} 个蓝图文档引用")
            
            return True
            
        except Exception as e:
            self._add_issue("P0", "系统总索引解析错误", f"解析系统总索引时出错: {e}")
            return False
    
    def analyze_directory_structure(self):
        """分析目录结构是否符合架构"""
        docs_path = self.project_root / "docs"
        
        if not docs_path.exists():
            self._add_issue("P0", "docs目录缺失", "项目缺少docs目录")
            return False
        
        # 检查目录结构
        expected_dirs = [
            "01_FRAMEWORK",
            "02_FACTOR_LIBRARY", 
            "03_TRADING_TACTICS",
            "04_EXECUTION",
            "05_RISK_MANAGEMENT",
            "06_ARCHIVE",
            "07_QUALITY",
            "08_AI_REPORTING",
            "09_AUDIT",
            "00_RESOURCES"
        ]
        
        existing_dirs = [d.name for d in docs_path.iterdir() if d.is_dir()]
        missing_dirs = [d for d in expected_dirs if d not in existing_dirs]
        
        if missing_dirs:
            self._add_issue("P2", "目录结构不完整", f"缺少以下目录: {', '.join(missing_dirs)}")
        
        # 检查中文目录名
        chinese_dirs = [d for d in existing_dirs if self._contains_chinese(d)]
        if chinese_dirs:
            self._add_issue("P1", "中文目录名", f"发现中文目录名: {', '.join(chinese_dirs[:5])}")
        
        if self.verbose:
            print(f"✅ 目录结构分析完成")
            print(f"   发现 {len(existing_dirs)} 个目录，{len(missing_dirs)} 个缺失")
        
        return len(missing_dirs) == 0
    
    def check_layer_integrity(self, layer_id: Optional[int] = None):
        """检查Layer完整性"""
        if layer_id is not None:
            return self._check_single_layer(layer_id)
        
        results = []
        for layer_id in range(9):
            results.append(self._check_single_layer(layer_id))
        
        return all(results)
    
    def _check_single_layer(self, layer_id: int) -> bool:
        """检查单个Layer的完整性"""
        layer = self.layers.get(layer_id)
        if not layer:
            self._add_issue("P0", f"Layer {layer_id}未定义", "标准Layer定义中缺少该Layer")
            return False
        
        # 检查是否有模块
        if not layer.modules:
            self._add_issue("P2", f"Layer {layer_id}无模块", f"Layer {layer_id} ({layer.name}) 没有分配任何模块")
            return False
        
        # 检查模块职责
        for module_id in layer.modules:
            module = self.modules.get(module_id)
            if not module:
                self._add_issue("P1", f"模块未定义", f"Layer {layer_id}中的模块 {module_id} 未在职责边界文档中定义")
            elif module.layer_id != layer_id:
                self._add_issue("P1", f"模块定位错误", f"模块 {module_id} 应属于Layer {layer_id}，实际定位为Layer {module.layer_id}")
        
        return True
    
    def _check_responsibility_overlap(self):
        """检查职责重叠"""
        responsibility_map: Dict[str, List[str]] = {}
        
        for module_id, module_def in self.modules.items():
            for responsibility in module_def.responsibilities:
                if responsibility not in responsibility_map:
                    responsibility_map[responsibility] = []
                responsibility_map[responsibility].append(module_id)
        
        # 找出重叠的职责
        for responsibility, modules in responsibility_map.items():
            if len(modules) > 1:
                self._add_issue("P1", "职责重叠", 
                               f"职责 '{responsibility}' 在多个模块中定义: {', '.join(modules)}")
    
    def _extract_section(self, content: str, section_title: str) -> Optional[str]:
        """提取指定章节内容"""
        pattern = rf"## {re.escape(section_title)}(.*?)(?=## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_all_sections_with_pattern(self, content: str, pattern: str) -> List[str]:
        """提取所有匹配模式的内容块"""
        matches = re.findall(rf"{pattern}(.*?)(?=### |## |\Z)", content, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _extract_table(self, content: str, table_title: str) -> Optional[List[List[str]]]:
        """提取表格内容"""
        # 查找表格标题后的表格
        table_pattern = rf"{re.escape(table_title)}.*?\n(\|.*?\n)+\n"
        match = re.search(table_pattern, content, re.DOTALL)
        
        if not match:
            return None
        
        table_content = match.group(0)
        rows = []
        
        for line in table_content.split('\n'):
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
        
        return rows if len(rows) > 1 else None
    
    def _extract_subsection(self, content: str, subsection_title: str) -> Optional[str]:
        """提取子章节内容"""
        # 查找子章节标题后的内容，直到下一个标题
        pattern = rf"{re.escape(subsection_title)}.*?\n(.*?)(?=\n#### |\n### |\n## |\n# |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_table_from_section(self, section: str) -> Optional[List[List[str]]]:
        """从章节中提取表格内容"""
        # 查找表格模式
        table_pattern = r"(\|.*?\n)+\n"
        match = re.search(table_pattern, section, re.DOTALL)
        
        if not match:
            return None
        
        table_content = match.group(0)
        rows = []
        
        for line in table_content.split('\n'):
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
        
        return rows if len(rows) > 1 else None
    
    def _extract_module_name(self, section: str) -> str:
        """从章节中提取模块名称"""
        # 查找###后面的模块名称
        match = re.search(r"### \d+\. ([^(\n]+)", section)
        return match.group(1).strip() if match else "未知模块"
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def _add_issue(self, priority: str, title: str, description: str):
        """添加问题"""
        self.issues.append({
            "priority": priority,
            "title": title,
            "description": description,
            "layer": None  # 稍后可以根据上下文添加
        })
        
        if self.verbose:
            print(f"  {priority}: {title}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """生成分析报告"""
        report = []
        
        # 报告头
        report.append("# 架构分析报告")
        report.append(f"> 生成时间: 2026-04-01")
        report.append(f"> 系统版本: v5.2")
        report.append(f"> 分析工具: architecture_analyzer.py v1.0")
        report.append("")
        
        # 概要统计
        total_modules = len(self.modules)
        layers_with_modules = sum(1 for layer in self.layers.values() if layer.modules)
        
        report.append("## 📊 概要统计")
        report.append("")
        report.append("| 指标 | 数量 |")
        report.append("|------|------|")
        report.append(f"| 总Layer数 | 9 |")
        report.append(f"| 有模块的Layer数 | {layers_with_modules} |")
        report.append(f"| 总模块数 | {total_modules} |")
        report.append(f"| 发现的问题数 | {len(self.issues)} |")
        report.append("")
        
        # Layer完整性分析
        report.append("## 🏗️ Layer完整性分析")
        report.append("")
        for layer_id in range(9):
            layer = self.layers[layer_id]
            module_count = len(layer.modules)
            status = "✅" if module_count > 0 else "⚠️"
            report.append(f"### Layer {layer_id}: {layer.name}")
            report.append(f"- **状态**: {status} ({module_count} 个模块)")
            report.append(f"- **描述**: {layer.description}")
            if layer.modules:
                report.append(f"- **模块**: {', '.join(layer.modules)}")
            report.append("")
        
        # 问题分析
        if self.issues:
            report.append("## ⚠️ 发现的问题")
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
        
        # 建议
        report.append("## 💡 改进建议")
        report.append("")
        
        if any(issue["priority"] == "P0" for issue in self.issues):
            report.append("1. **立即修复P0问题** - 这些是高风险问题，可能影响系统稳定性")
        
        if any(issue["priority"] == "P1" for issue in self.issues):
            report.append("2. **本周内修复P1问题** - 这些是中风险问题，影响架构完整性")
        
        if not all(layer.modules for layer in self.layers.values()):
            empty_layers = [layer_id for layer_id, layer in self.layers.items() if not layer.modules]
            report.append(f"3. **为空的Layer分配模块** - 以下Layer没有模块: {', '.join(map(str, empty_layers))}")
        
        # 将报告写入文件或返回
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"报告已保存到: {output_path}")
        
        return report_text
    
    def run_analysis(self, check_layer: Optional[int] = None) -> bool:
        """运行完整分析"""
        print("🔍 开始架构分析...")
        print(f"项目根目录: {self.project_root}")
        print("-" * 60)
        
        # 执行各项分析
        results = []
        
        results.append(self.analyze_architecture_document())
        results.append(self.analyze_module_boundaries())
        results.append(self.analyze_system_manifest())
        results.append(self.analyze_directory_structure())
        
        if check_layer is not None:
            results.append(self.check_layer_integrity(check_layer))
        else:
            results.append(self.check_layer_integrity())
        
        # 汇总结果
        success = all(results)
        
        print("-" * 60)
        if success:
            print("✅ 架构分析完成，所有检查通过")
        else:
            print(f"⚠️ 架构分析完成，发现 {len(self.issues)} 个问题")
            print("   使用 --verbose 查看详细问题")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清风量化系统 - 架构分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    # 完整分析
    python scripts/architecture_analyzer.py
    
    # 详细输出
    python scripts/architecture_analyzer.py --verbose
    
    # 生成HTML报告
    python scripts/architecture_analyzer.py --report
    
    # 只检查Layer 5
    python scripts/architecture_analyzer.py --check-layer 5
    
    # 所有检查
    python scripts/architecture_analyzer.py --all
        """
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细分析过程"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成HTML分析报告"
    )
    
    parser.add_argument(
        "--check-layer",
        type=int,
        choices=range(0, 9),
        help="只检查指定Layer (0-8)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="检查所有方面"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).resolve().parents[2]
    
    # 创建分析器
    analyzer = ArchitectureAnalyzer(
        project_root=project_root,
        verbose=args.verbose
    )
    
    # 运行分析
    try:
        success = analyzer.run_analysis(check_layer=args.check_layer)
        
        # 生成报告
        if args.report:
            report_path = project_root / "docs" / "09_AUDIT" / "ARCHITECTURE_ANALYSIS_REPORT.md"
            analyzer.generate_report(report_path)
        
        # 显示问题概要
        if analyzer.issues:
            print("\n📋 问题概要:")
            for issue in analyzer.issues[:10]:  # 只显示前10个
                print(f"  {issue['priority']}: {issue['title']}")
            
            if len(analyzer.issues) > 10:
                print(f"  ... 和其他 {len(analyzer.issues) - 10} 个问题")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断分析操作")
        return 1
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())