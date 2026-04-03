#!/usr/bin/env python3
"""
清风量化系统 - 蓝图质量验证工具

功能: 验证蓝图文档质量，检查结构完整性、内容合规性、格式规范性
版本: v1.0
创建日期: 2026-04-01
维护者: 蓝图架构师智能体

使用方法:
    python scripts/blueprint_validator.py [--verbose] [--report] [--blueprint PATH]

参数:
    --verbose    : 显示详细验证过程
    --report     : 生成HTML验证报告
    --blueprint PATH : 只验证指定蓝图文档
    --all        : 验证所有蓝图文档
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
import yaml

@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    category: str  # 结构、内容、格式、合规性
    description: str
    severity: str  # P0/P1/P2
    check_function: str  # 检查函数名
    
@dataclass
class ValidationResult:
    """验证结果"""
    blueprint_path: Path
    rule_id: str
    passed: bool
    message: str
    severity: str
    details: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class BlueprintValidation:
    """蓝图验证结果"""
    blueprint_path: Path
    blueprint_name: str
    total_rules: int
    passed_rules: int
    failed_rules: int
    p0_issues: int
    p1_issues: int
    p2_issues: int
    validation_score: float  # 0-100
    results: List[ValidationResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class BlueprintValidator:
    """蓝图验证器"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.validations: Dict[Path, BlueprintValidation] = {}
        self.issues: List[Dict[str, Any]] = []
        self.rules: List[ValidationRule] = []
        
        # 初始化验证规则
        self._initialize_validation_rules()
        
    def _initialize_validation_rules(self):
        """初始化验证规则"""
        # 结构规则
        self.rules.append(ValidationRule(
            rule_id="STRUCT-001",
            category="structure",
            description="蓝图文档必须有标准章节结构",
            severity="P0",
            check_function="_check_standard_structure"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="STRUCT-002",
            category="structure",
            description="蓝图文档必须有版本标识",
            severity="P1",
            check_function="_check_version_identifier"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="STRUCT-003",
            category="structure",
            description="蓝图文档必须有模块ID",
            severity="P0",
            check_function="_check_module_id"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="STRUCT-004",
            category="structure",
            description="蓝图文档必须有Layer定位",
            severity="P1",
            check_function="_check_layer_positioning"
        ))
        
        # 内容规则
        self.rules.append(ValidationRule(
            rule_id="CONTENT-001",
            category="content",
            description="蓝图文档必须有清晰的职责定义",
            severity="P0",
            check_function="_check_responsibility_definition"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="CONTENT-002",
            category="content",
            description="蓝图文档必须有接口定义",
            severity="P1",
            check_function="_check_interface_definition"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="CONTENT-003",
            category="content",
            description="蓝图文档必须有数据流描述",
            severity="P1",
            check_function="_check_dataflow_description"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="CONTENT-004",
            category="content",
            description="蓝图文档必须有实施路径规划",
            severity="P2",
            check_function="_check_implementation_path"
        ))
        
        # 格式规则
        self.rules.append(ValidationRule(
            rule_id="FORMAT-001",
            category="format",
            description="蓝图文档必须使用标准命名规范",
            severity="P1",
            check_function="_check_naming_convention"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="FORMAT-002",
            category="format",
            description="蓝图文档必须有正确的标题层级",
            severity="P2",
            check_function="_check_heading_hierarchy"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="FORMAT-003",
            category="format",
            description="蓝图文档必须有表格格式化",
            severity="P2",
            check_function="_check_table_formatting"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="FORMAT-004",
            category="format",
            description="蓝图文档必须有代码块标记",
            severity="P2",
            check_function="_check_code_block_marking"
        ))
        
        # 合规性规则
        self.rules.append(ValidationRule(
            rule_id="COMPLY-001",
            category="compliance",
            description="蓝图文档必须被System_Manifest.md索引",
            severity="P0",
            check_function="_check_system_manifest_indexing"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="COMPLY-002",
            category="compliance",
            description="蓝图文档必须符合文档治理五大原则",
            severity="P1",
            check_function="_check_governance_principles"
        ))
        
        self.rules.append(ValidationRule(
            rule_id="COMPLY-003",
            category="compliance",
            description="蓝图文档必须没有职责重叠",
            severity="P0",
            check_function="_check_responsibility_overlap"
        ))
        
    def validate_blueprints(self, blueprint_path: Optional[Path] = None) -> bool:
        """验证蓝图文档"""
        if self.verbose:
            print("🔍 开始蓝图质量验证...")
        
        # 获取蓝图文档
        if blueprint_path:
            blueprint_files = [blueprint_path]
        else:
            blueprint_files = self._collect_blueprint_files()
        
        if not blueprint_files:
            self._add_issue("P0", "无蓝图文档", "未找到任何蓝图文档")
            return False
        
        if self.verbose:
            print(f"   找到 {len(blueprint_files)} 个蓝图文档")
        
        # 验证每个蓝图
        for bp_path in blueprint_files:
            if self.verbose:
                print(f"   验证蓝图: {bp_path.relative_to(self.project_root)}")
            
            validation = self._validate_single_blueprint(bp_path)
            if validation:
                self.validations[bp_path] = validation
        
        # 生成总体报告
        overall_score = self._calculate_overall_score()
        
        if self.verbose:
            print(f"✅ 蓝图质量验证完成")
            print(f"   验证了 {len(self.validations)} 个蓝图文档")
            print(f"   总体评分: {overall_score:.1f}/100")
        
        return True
    
    def _collect_blueprint_files(self) -> List[Path]:
        """收集蓝图文档文件"""
        blueprint_files = []
        
        # 在docs目录中查找蓝图文档
        docs_path = self.project_root / "docs"
        if not docs_path.exists():
            return []
        
        # 蓝图文档命名模式
        blueprint_patterns = ["*BLUEPRINT*", "*蓝图*", "BLUEPRINT.md"]
        
        for root, dirs, files in os.walk(docs_path):
            # 跳过某些目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() == '.md':
                    # 检查文件名是否包含蓝图关键词
                    file_lower = file.lower()
                    if any(pattern.lower() in file_lower for pattern in blueprint_patterns):
                        blueprint_files.append(file_path)
        
        return blueprint_files
    
    def _validate_single_blueprint(self, bp_path: Path) -> Optional[BlueprintValidation]:
        """验证单个蓝图文档"""
        try:
            if not bp_path.exists():
                return None
            
            with open(bp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取蓝图基本信息
            blueprint_name = self._extract_blueprint_name(content, bp_path)
            
            # 执行所有规则检查
            results = []
            for rule in self.rules:
                # 调用对应的检查函数
                check_func = getattr(self, rule.check_function, None)
                if check_func:
                    passed, message, details = check_func(content, bp_path)
                    
                    result = ValidationResult(
                        blueprint_path=bp_path,
                        rule_id=rule.rule_id,
                        passed=passed,
                        message=message,
                        severity=rule.severity,
                        details=details
                    )
                    results.append(result)
                else:
                    # 检查函数不存在
                    result = ValidationResult(
                        blueprint_path=bp_path,
                        rule_id=rule.rule_id,
                        passed=False,
                        message=f"检查函数 {rule.check_function} 不存在",
                        severity=rule.severity,
                        details={}
                    )
                    results.append(result)
            
            # 统计结果
            total_rules = len(results)
            passed_rules = len([r for r in results if r.passed])
            failed_rules = total_rules - passed_rules
            
            p0_issues = len([r for r in results if not r.passed and r.severity == "P0"])
            p1_issues = len([r for r in results if not r.passed and r.severity == "P1"])
            p2_issues = len([r for r in results if not r.passed and r.severity == "P2"])
            
            # 计算验证评分
            validation_score = self._calculate_validation_score(results)
            
            # 生成改进建议
            recommendations = self._generate_recommendations(results)
            
            return BlueprintValidation(
                blueprint_path=bp_path,
                blueprint_name=blueprint_name,
                total_rules=total_rules,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                p0_issues=p0_issues,
                p1_issues=p1_issues,
                p2_issues=p2_issues,
                validation_score=validation_score,
                results=results,
                recommendations=recommendations
            )
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 验证蓝图 {bp_path} 时出错: {e}")
            return None
    
    # ===== 验证规则检查函数 =====
    
    def _check_standard_structure(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查标准章节结构"""
        required_sections = [
            "概述",
            "架构设计",
            "技术实现",
            "数据模型",
            "实施路径",
            "文档治理",
            "风险评估"
        ]
        
        found_sections = []
        missing_sections = []
        
        for section in required_sections:
            pattern = rf"^#+\s+.*{re.escape(section)}.*$"
            if re.search(pattern, content, re.MULTILINE):
                found_sections.append(section)
            else:
                missing_sections.append(section)
        
        passed = len(missing_sections) == 0
        message = f"找到 {len(found_sections)}/{len(required_sections)} 个标准章节" if passed else f"缺少章节: {', '.join(missing_sections)}"
        
        return passed, message, {
            "required_sections": required_sections,
            "found_sections": found_sections,
            "missing_sections": missing_sections
        }
    
    def _check_version_identifier(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查版本标识"""
        # 查找版本号
        version_patterns = [
            r'版本\s*[:：]\s*([0-9.]+)',
            r'version\s*[:：]\s*([0-9.]+)',
            r'v([0-9.]+)',
            r'Version:\s*([0-9.]+)'
        ]
        
        versions_found = []
        for pattern in version_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            versions_found.extend(matches)
        
        passed = len(versions_found) > 0
        message = f"找到版本标识: {', '.join(versions_found)}" if passed else "未找到版本标识"
        
        return passed, message, {
            "versions_found": versions_found,
            "version_patterns": version_patterns
        }
    
    def _check_module_id(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查模块ID"""
        # 查找模块ID
        module_id_patterns = [
            r'模块ID\s*[:：]\s*([A-Z_][A-Z0-9_]*)',
            r'模块标识\s*[:：]\s*([A-Z_][A-Z0-9_]*)',
            r'MODULE_ID\s*[:：]\s*([A-Z_][A-Z0-9_]*)'
        ]
        
        module_ids = []
        for pattern in module_id_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            module_ids.extend(matches)
        
        # 也检查文件名中的模块ID
        filename = bp_path.name
        filename_match = re.search(r'([A-Z_][A-Z0-9_]{3,})', filename)
        if filename_match:
            module_ids.append(filename_match.group(1))
        
        passed = len(module_ids) > 0
        message = f"找到模块ID: {', '.join(set(module_ids))}" if passed else "未找到模块ID"
        
        return passed, message, {
            "module_ids": list(set(module_ids)),
            "module_id_patterns": module_id_patterns
        }
    
    def _check_layer_positioning(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查Layer定位"""
        # 查找Layer信息
        layer_patterns = [
            r'Layer\s*(\d+)',
            r'层级\s*(\d+)',
            r'所属Layer\s*[:：]\s*Layer\s*(\d+)',
            r'定位\s*[:：]\s*Layer\s*(\d+)'
        ]
        
        layers_found = []
        for pattern in layer_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            layers_found.extend(matches)
        
        passed = len(layers_found) > 0
        message = f"找到Layer定位: {', '.join(set(layers_found))}" if passed else "未找到Layer定位"
        
        return passed, message, {
            "layers_found": list(set(layers_found)),
            "layer_patterns": layer_patterns
        }
    
    def _check_responsibility_definition(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查职责定义"""
        # 查找职责相关关键词
        responsibility_keywords = [
            "职责", "责任", "负责", "功能", "职能", "responsibility", "duty"
        ]
        
        sections_with_responsibilities = []
        for keyword in responsibility_keywords:
            pattern = rf"^#+\s+.*{re.escape(keyword)}.*$"
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                sections_with_responsibilities.append(keyword)
        
        # 检查是否有表格格式的职责定义
        table_pattern = r"(\|.*?\n)+\n"
        table_matches = re.findall(table_pattern, content)
        
        passed = len(sections_with_responsibilities) > 0 or len(table_matches) > 0
        message = f"找到职责定义: {len(sections_with_responsibilities)} 个相关章节, {len(table_matches)} 个表格" if passed else "未找到清晰的职责定义"
        
        return passed, message, {
            "responsibility_keywords": responsibility_keywords,
            "sections_found": sections_with_responsibilities,
            "tables_found": len(table_matches)
        }
    
    def _check_interface_definition(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查接口定义"""
        # 查找接口相关关键词
        interface_keywords = [
            "接口", "接口定义", "边界接口", "API", "interface", "API定义"
        ]
        
        sections_with_interfaces = []
        for keyword in interface_keywords:
            pattern = rf"^#+\s+.*{re.escape(keyword)}.*$"
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                sections_with_interfaces.append(keyword)
        
        # 检查是否有接口表格
        interface_table_pattern = r"接口.*?\n(\|.*?\n)+\n"
        interface_tables = re.findall(interface_table_pattern, content, re.IGNORECASE)
        
        passed = len(sections_with_interfaces) > 0 or len(interface_tables) > 0
        message = f"找到接口定义: {len(sections_with_interfaces)} 个相关章节, {len(interface_tables)} 个接口表格" if passed else "未找到接口定义"
        
        return passed, message, {
            "interface_keywords": interface_keywords,
            "sections_found": sections_with_interfaces,
            "interface_tables_found": len(interface_tables)
        }
    
    def _check_dataflow_description(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查数据流描述"""
        # 查找数据流相关关键词
        dataflow_keywords = [
            "数据流", "数据流向", "数据流程", "数据传递", "data flow", "dataflow"
        ]
        
        sections_with_dataflow = []
        for keyword in dataflow_keywords:
            pattern = rf"^#+\s+.*{re.escape(keyword)}.*$"
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                sections_with_dataflow.append(keyword)
        
        # 检查是否有数据流图或描述
        diagram_patterns = [
            r"```.*?\n.*?数据.*?\n.*?```",
            r"流程图",
            r"flowchart",
            r"sequence diagram"
        ]
        
        diagrams_found = []
        for pattern in diagram_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                diagrams_found.append(pattern)
        
        passed = len(sections_with_dataflow) > 0 or len(diagrams_found) > 0
        message = f"找到数据流描述: {len(sections_with_dataflow)} 个相关章节, {len(diagrams_found)} 个图表" if passed else "未找到数据流描述"
        
        return passed, message, {
            "dataflow_keywords": dataflow_keywords,
            "sections_found": sections_with_dataflow,
            "diagrams_found": diagrams_found
        }
    
    def _check_implementation_path(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查实施路径规划"""
        # 查找实施路径相关关键词
        implementation_keywords = [
            "实施路径", "实施计划", "实施步骤", "实施阶段", "implementation", "roadmap"
        ]
        
        sections_with_implementation = []
        for keyword in implementation_keywords:
            pattern = rf"^#+\s+.*{re.escape(keyword)}.*$"
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                sections_with_implementation.append(keyword)
        
        # 检查是否有阶段划分
        phase_patterns = [
            r"Phase\s+[0-9]+",
            r"阶段\s*[0-9]+",
            r"第[一二三四五六七八九十]+阶段"
        ]
        
        phases_found = []
        for pattern in phase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            phases_found.extend(matches)
        
        passed = len(sections_with_implementation) > 0 or len(phases_found) > 0
        message = f"找到实施路径: {len(sections_with_implementation)} 个相关章节, {len(phases_found)} 个阶段划分" if passed else "未找到实施路径规划"
        
        return passed, message, {
            "implementation_keywords": implementation_keywords,
            "sections_found": sections_with_implementation,
            "phases_found": phases_found
        }
    
    def _check_naming_convention(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查命名规范"""
        # 检查文件名是否包含中文
        filename = bp_path.name
        contains_chinese = bool(re.search(r'[\u4e00-\u9fff]', filename))
        
        passed = not contains_chinese
        message = "文件名符合命名规范" if passed else "文件名包含中文，不符合命名规范"
        
        return passed, message, {
            "filename": filename,
            "contains_chinese": contains_chinese
        }
    
    def _check_heading_hierarchy(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查标题层级"""
        # 提取所有标题
        headings = re.findall(r'^(#+)\s+(.*)$', content, re.MULTILINE)
        
        if not headings:
            return False, "文档没有标题", {"headings": []}
        
        # 检查标题层级是否合理
        heading_levels = [len(h[0]) for h in headings]
        max_level = max(heading_levels) if heading_levels else 0
        min_level = min(heading_levels) if heading_levels else 0
        
        # 合理的标题层级应该是从#开始，层级连续
        passed = min_level == 1 and max_level <= 6
        message = f"标题层级合理: 从H{min_level}到H{max_level}" if passed else f"标题层级不合理: 从H{min_level}到H{max_level}，应该从H1开始且不超过H6"
        
        return passed, message, {
            "headings": headings,
            "heading_levels": heading_levels,
            "max_level": max_level,
            "min_level": min_level
        }
    
    def _check_table_formatting(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查表格格式化"""
        # 查找所有表格
        table_pattern = r"(\|.*?\n)+\n"
        tables = re.findall(table_pattern, content)
        
        if not tables:
            return True, "文档无表格，跳过检查", {"tables_found": 0, "well_formatted_tables": 0}
        
        # 检查表格是否格式正确（有表头分隔线）
        well_formatted_count = 0
        for table in tables:
            lines = table.strip().split('\n')
            if len(lines) >= 3:
                # 检查第二行是否包含分隔线
                second_line = lines[1]
                if re.search(r'\|[-:]+\|', second_line):
                    well_formatted_count += 1
        
        passed = well_formatted_count == len(tables)
        message = f"表格格式化正确: {well_formatted_count}/{len(tables)} 个表格格式正确" if passed else f"表格格式化问题: {well_formatted_count}/{len(tables)} 个表格格式正确"
        
        return passed, message, {
            "tables_found": len(tables),
            "well_formatted_tables": well_formatted_count
        }
    
    def _check_code_block_marking(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查代码块标记"""
        # 查找代码块
        code_block_pattern = r'```(\w*)\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        
        if not code_blocks:
            return True, "文档无代码块，跳过检查", {"code_blocks_found": 0, "language_specified_blocks": 0}
        
        # 检查代码块是否有语言标记
        language_specified_blocks = 0
        for lang, code in code_blocks:
            if lang.strip():
                language_specified_blocks += 1
        
        passed = language_specified_blocks == len(code_blocks)
        message = f"代码块标记正确: {language_specified_blocks}/{len(code_blocks)} 个代码块有语言标记" if passed else f"代码块标记问题: {language_specified_blocks}/{len(code_blocks)} 个代码块有语言标记"
        
        return passed, message, {
            "code_blocks_found": len(code_blocks),
            "language_specified_blocks": language_specified_blocks
        }
    
    def _check_system_manifest_indexing(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查System_Manifest.md索引"""
        # 检查蓝图是否在System_Manifest.md中被索引
        manifest_path = self.project_root / "docs" / "System_Manifest.md"
        
        if not manifest_path.exists():
            return False, "System_Manifest.md不存在", {"manifest_exists": False}
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # 计算蓝图在manifest中的相对路径
            relative_path = bp_path.relative_to(self.project_root)
            
            # 检查是否被引用
            escaped_path = re.escape(str(relative_path))
            pattern = rf'\[.*?\]\({escaped_path}\)'
            
            if re.search(pattern, manifest_content):
                return True, f"蓝图被System_Manifest.md索引", {
                    "manifest_exists": True,
                    "indexed": True,
                    "relative_path": str(relative_path)
                }
            else:
                return False, f"蓝图未被System_Manifest.md索引", {
                    "manifest_exists": True,
                    "indexed": False,
                    "relative_path": str(relative_path)
                }
                
        except Exception as e:
            return False, f"检查System_Manifest.md时出错: {e}", {
                "manifest_exists": True,
                "error": str(e)
            }
    
    def _check_governance_principles(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查文档治理五大原则"""
        # 检查文档治理原则的遵守情况
        principles = [
            "职责驱动原则",
            "索引完备原则", 
            "版本隔离原则",
            "文档代码对应原则",
            "命名规范原则"
        ]
        
        principles_mentioned = []
        for principle in principles:
            if principle in content:
                principles_mentioned.append(principle)
        
        passed = len(principles_mentioned) > 0
        message = f"提及 {len(principles_mentioned)}/{len(principles)} 个文档治理原则" if passed else "未提及文档治理原则"
        
        return passed, message, {
            "principles": principles,
            "principles_mentioned": principles_mentioned
        }
    
    def _check_responsibility_overlap(self, content: str, bp_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """检查职责重叠"""
        # 这是一个简化检查，实际应该对比所有蓝图
        # 这里只检查当前蓝图内部是否有重复的职责描述
        responsibility_keywords = ["负责", "职责", "功能", "任务"]
        
        responsibilities = []
        for keyword in responsibility_keywords:
            # 查找包含关键词的句子
            pattern = rf'[^。！？.!?]*{re.escape(keyword)}[^。！？.!?]*[。！？.!?]'
            matches = re.findall(pattern, content)
            responsibilities.extend(matches)
        
        # 简单的重复检查（基于文本相似度）
        unique_responsibilities = list(set(responsibilities))
        
        passed = len(unique_responsibilities) == len(responsibilities) or len(responsibilities) <= 1
        message = f"职责定义清晰，未发现明显重叠" if passed else f"发现 {len(responsibilities)-len(unique_responsibilities)} 个可能的职责重叠"
        
        return passed, message, {
            "responsibilities_found": len(responsibilities),
            "unique_responsibilities": len(unique_responsibilities),
            "responsibility_keywords": responsibility_keywords
        }
    
    # ===== 辅助函数 =====
    
    def _extract_blueprint_name(self, content: str, bp_path: Path) -> str:
        """提取蓝图名称"""
        # 从标题中提取
        title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # 从文件名中提取
        filename = bp_path.stem
        return filename
    
    def _calculate_validation_score(self, results: List[ValidationResult]) -> float:
        """计算验证评分"""
        if not results:
            return 0.0
        
        # 权重：P0规则权重更高
        weight_map = {"P0": 3.0, "P1": 2.0, "P2": 1.0}
        
        total_weight = 0
        weighted_score = 0
        
        for result in results:
            weight = weight_map.get(result.severity, 1.0)
            total_weight += weight
            if result.passed:
                weighted_score += weight * 100
            else:
                # 未通过的规则得0分
                weighted_score += 0
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_overall_score(self) -> float:
        """计算总体评分"""
        if not self.validations:
            return 0.0
        
        total_scores = [v.validation_score for v in self.validations.values()]
        return sum(total_scores) / len(total_scores)
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重程度排序
        failed_results = [r for r in results if not r.passed]
        failed_results.sort(key=lambda x: {"P0": 0, "P1": 1, "P2": 2}[x.severity])
        
        for result in failed_results[:5]:  # 最多5个建议
            recommendations.append(f"{result.rule_id}: {result.message}")
        
        return recommendations
    
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
        """生成蓝图验证报告"""
        report = []
        
        # 报告头
        report.append("# 蓝图质量验证报告")
        report.append(f"> 生成时间: 2026-04-01")
        report.append(f"> 系统版本: v5.2")
        report.append(f"> 验证工具: blueprint_validator.py v1.0")
        report.append("")
        
        # 概要统计
        total_blueprints = len(self.validations)
        overall_score = self._calculate_overall_score()
        
        # 按评分分类
        excellent_count = len([v for v in self.validations.values() if v.validation_score >= 90])
        good_count = len([v for v in self.validations.values() if 70 <= v.validation_score < 90])
        fair_count = len([v for v in self.validations.values() if 50 <= v.validation_score < 70])
        poor_count = len([v for v in self.validations.values() if v.validation_score < 50])
        
        report.append("## 📊 概要统计")
        report.append("")
        report.append("| 指标 | 数量 |")
        report.append("|------|------|")
        report.append(f"| 验证蓝图数 | {total_blueprints} |")
        report.append(f"| 总体评分 | {overall_score:.1f}/100 |")
        report.append(f"| 优秀蓝图 (≥90分) | {excellent_count} |")
        report.append(f"| 良好蓝图 (70-89分) | {good_count} |")
        report.append(f"| 一般蓝图 (50-69分) | {fair_count} |")
        report.append(f"| 需改进蓝图 (<50分) | {poor_count} |")
        report.append("")
        
        # 详细蓝图列表
        report.append("## 📄 蓝图验证详情")
        report.append("")
        report.append("| 蓝图文档 | 总体评分 | 通过规则 | 总规则 | P0问题 | P1问题 | P2问题 | 状态 |")
        report.append("|----------|----------|----------|--------|--------|--------|--------|------|")
        
        sorted_validations = sorted(self.validations.items(), key=lambda x: x[1].validation_score, reverse=True)
        
        for bp_path, validation in sorted_validations[:20]:  # 显示前20个蓝图
            relative_path = bp_path.relative_to(self.project_root)
            
            status = "✅ 优秀" if validation.validation_score >= 90 else \
                     "⚠️ 良好" if validation.validation_score >= 70 else \
                     "🔶 一般" if validation.validation_score >= 50 else "❌ 需改进"
            
            report.append(f"| [{relative_path}]({relative_path}) | {validation.validation_score:.1f} | {validation.passed_rules} | {validation.total_rules} | {validation.p0_issues} | {validation.p1_issues} | {validation.p2_issues} | {status} |")
        
        if len(sorted_validations) > 20:
            report.append(f"| ... 和其他 {len(sorted_validations) - 20} 个蓝图 | ... | ... | ... | ... | ... | ... | ... |")
        
        report.append("")
        
        # 规则通过率统计
        report.append("## 📈 规则通过率统计")
        report.append("")
        report.append("| 规则类别 | 总规则数 | 通过规则数 | 通过率 |")
        report.append("|----------|----------|------------|--------|")
        
        categories = ["structure", "content", "format", "compliance"]
        category_names = {"structure": "结构", "content": "内容", "format": "格式", "compliance": "合规性"}
        
        for category in categories:
            category_rules = [r for r in self.rules if r.category == category]
            if not category_rules:
                continue
            
            total_category_rules = len(category_rules) * total_blueprints
            passed_category_rules = 0
            
            for validation in self.validations.values():
                for result in validation.results:
                    rule = next((r for r in category_rules if r.rule_id == result.rule_id), None)
                    if rule and result.passed:
                        passed_category_rules += 1
            
            pass_rate = (passed_category_rules / total_category_rules * 100) if total_category_rules > 0 else 0
            
            report.append(f"| {category_names[category]} | {total_category_rules} | {passed_category_rules} | {pass_rate:.1f}% |")
        
        report.append("")
        
        # 改进建议
        report.append("## 💡 改进建议")
        report.append("")
        
        all_recommendations = []
        for validation in self.validations.values():
            all_recommendations.extend(validation.recommendations)
        
        if all_recommendations:
            unique_recommendations = list(set(all_recommendations))[:10]  # 去重后取前10个
            for i, rec in enumerate(unique_recommendations, 1):
                report.append(f"{i}. {rec}")
        else:
            report.append("所有蓝图都符合质量要求，无需特别改进。")
        
        report.append("")
        
        report_content = "\n".join(report)
        
        # 保存报告
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            if self.verbose:
                print(f"📄 报告已保存到: {output_path}")
        
        return report_content
    
    def run_validation(self, blueprint_path: Optional[Path] = None) -> bool:
        """运行验证"""
        if self.verbose:
            print(f"🔍 开始蓝图质量验证...")
            print(f"项目根目录: {self.project_root}")
            print("-" * 60)
        
        success = self.validate_blueprints(blueprint_path)
        
        print("-" * 60)
        if success:
            overall_score = self._calculate_overall_score()
            if overall_score >= 90:
                print(f"✅ 蓝图质量验证完成，总体评分: {overall_score:.1f}/100 (优秀)")
            elif overall_score >= 70:
                print(f"⚠️ 蓝图质量验证完成，总体评分: {overall_score:.1f}/100 (良好)")
            elif overall_score >= 50:
                print(f"🔶 蓝图质量验证完成，总体评分: {overall_score:.1f}/100 (一般)")
            else:
                print(f"❌ 蓝图质量验证完成，总体评分: {overall_score:.1f}/100 (需改进)")
        else:
            print("❌ 蓝图质量验证失败")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清风量化系统 - 蓝图质量验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    # 完整验证
    python scripts/blueprint_validator.py
    
    # 详细输出
    python scripts/blueprint_validator.py --verbose
    
    # 生成HTML报告
    python scripts/blueprint_validator.py --report
    
    # 只验证指定蓝图
    python scripts/blueprint_validator.py --blueprint docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md
    
    # 所有检查
    python scripts/blueprint_validator.py --all
        """
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细验证过程"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成HTML验证报告"
    )
    
    parser.add_argument(
        "--blueprint",
        type=Path,
        help="只验证指定蓝图文档"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="验证所有蓝图文档"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建验证器
    validator = BlueprintValidator(
        project_root=project_root,
        verbose=args.verbose
    )
    
    # 运行验证
    try:
        success = validator.run_validation(blueprint_path=args.blueprint)
        
        # 生成报告
        if args.report:
            report_path = project_root / "docs" / "09_AUDIT" / "BLUEPRINT_VALIDATION_REPORT.md"
            validator.generate_report(report_path)
        
        # 显示问题概要
        if validator.issues:
            print("\n📋 问题概要:")
            for issue in validator.issues[:10]:  # 只显示前10个
                print(f"  {issue['priority']}: {issue['title']}")
            
            if len(validator.issues) > 10:
                print(f"  ... 和其他 {len(validator.issues) - 10} 个问题")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断验证操作")
        return 1
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())