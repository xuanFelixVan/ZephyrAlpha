#!/usr/bin/env python3
"""
清风量化系统 - 风险分析工具

功能: 分析技术方案中的各类风险，包括技术风险、安全风险、合规风险、实施风险等
版本: v1.0
创建日期: 2026-04-02
维护者: 审批智能体 (Spec-Approver)

使用方法:
    python scripts/risk_analyzer.py [--verbose] [--report] [--input PATH] [--risk-level {P0,P1,P2,P3}]

参数:
    --verbose    : 显示详细分析过程
    --report     : 生成详细的风险分析报告
    --input PATH : 指定输入文件（蓝图或技术规格书）
    --risk-level : 只显示指定风险等级的风险项
    --help       : 显示帮助信息

风险分类与等级:
P0 (极高风险): 可能导致系统完全失效、数据丢失、重大安全漏洞、严重合规违规
P1 (高风险): 可能导致系统部分功能失效、性能严重下降、中等安全风险
P2 (中风险): 可能导致系统功能受限、性能下降、需要额外维护工作
P3 (低风险): 可能产生轻微影响、可通过常规维护解决的潜在问题

风险维度:
1. 技术风险 (权重: 35%)
   - 技术选型风险
   - 技术债务风险
   - 技术兼容性风险
   - 技术过时风险
2. 安全风险 (权重: 25%)
   - 数据安全风险
   - 访问控制风险
   - 代码安全风险
   - 网络安全风险
3. 合规风险 (权重: 20%)
   - 监管合规风险
   - 数据隐私风险
   - 许可协议风险
   - 行业标准风险
4. 实施风险 (权重: 20%)
   - 项目进度风险
   - 资源分配风险
   - 团队能力风险
   - 沟通协作风险
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import yaml

@dataclass
class RiskItem:
    """单个风险项"""
    risk_id: str
    category: str  # 风险类别: technical, security, compliance, implementation
    level: str     # 风险等级: P0, P1, P2, P3
    title: str     # 风险标题
    description: str  # 风险描述
    probability: float  # 发生概率 (0.0-1.0)
    impact: float      # 影响程度 (0.0-1.0)
    risk_score: float = 0.0  # 风险评分 = 概率 × 影响 × 等级系数（在__post_init__中计算）
    mitigation: str = ""    # 缓解措施
    detection_method: str = ""  # 检测方法
    owner: str = ""   # 风险负责人
    status: str = "identified"  # 状态: identified, mitigated, closed
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 计算风险评分
        level_coefficient = {
            "P0": 1.0,  # 极高风险
            "P1": 0.8,  # 高风险
            "P2": 0.5,  # 中风险
            "P3": 0.2   # 低风险
        }.get(self.level, 0.5)
        
        self.risk_score = self.probability * self.impact * level_coefficient * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "category": self.category,
            "level": self.level,
            "title": self.title,
            "description": self.description,
            "probability": self.probability,
            "impact": self.impact,
            "risk_score": self.risk_score,
            "mitigation": self.mitigation,
            "detection_method": self.detection_method,
            "owner": self.owner,
            "status": self.status,
            "created_at": self.created_at
        }


@dataclass
class RiskCategorySummary:
    """风险类别汇总"""
    category: str
    total_risks: int = 0
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    p3_count: int = 0
    total_score: float = 0.0
    avg_score: float = 0.0
    
    def add_risk(self, risk: RiskItem):
        self.total_risks += 1
        self.total_score += risk.risk_score
        
        if risk.level == "P0":
            self.p0_count += 1
        elif risk.level == "P1":
            self.p1_count += 1
        elif risk.level == "P2":
            self.p2_count += 1
        elif risk.level == "P3":
            self.p3_count += 1
    
    def finalize(self):
        if self.total_risks > 0:
            self.avg_score = self.total_score / self.total_risks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "total_risks": self.total_risks,
            "p0_count": self.p0_count,
            "p1_count": self.p1_count,
            "p2_count": self.p2_count,
            "p3_count": self.p3_count,
            "total_score": self.total_score,
            "avg_score": self.avg_score
        }


@dataclass
class RiskAnalysisResult:
    """风险分析结果"""
    file_path: str
    total_risks: int = 0
    risks_by_category: Dict[str, RiskCategorySummary] = field(default_factory=dict)
    risks_by_level: Dict[str, List[RiskItem]] = field(default_factory=dict)
    all_risks: List[RiskItem] = field(default_factory=list)
    overall_risk_score: float = 0.0
    risk_level: str = "低风险"
    analysis_timestamp: str = ""
    
    def __post_init__(self):
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 初始化类别汇总
        categories = ["technical", "security", "compliance", "implementation"]
        for category in categories:
            if category not in self.risks_by_category:
                self.risks_by_category[category] = RiskCategorySummary(category=category)
        
        # 初始化等级分类
        levels = ["P0", "P1", "P2", "P3"]
        for level in levels:
            if level not in self.risks_by_level:
                self.risks_by_level[level] = []
    
    def add_risk(self, risk: RiskItem):
        self.all_risks.append(risk)
        self.total_risks += 1
        
        # 添加到类别汇总
        if risk.category not in self.risks_by_category:
            self.risks_by_category[risk.category] = RiskCategorySummary(category=risk.category)
        self.risks_by_category[risk.category].add_risk(risk)
        
        # 添加到等级分类
        self.risks_by_level[risk.level].append(risk)
    
    def finalize(self):
        # 完成类别汇总计算
        for category in self.risks_by_category.values():
            category.finalize()
        
        # 计算总体风险评分
        if self.total_risks > 0:
            total_score = sum(risk.risk_score for risk in self.all_risks)
            self.overall_risk_score = total_score / self.total_risks
        else:
            self.overall_risk_score = 0.0
        
        # 确定总体风险等级
        if self.overall_risk_score >= 80:
            self.risk_level = "极高风险"
        elif self.overall_risk_score >= 60:
            self.risk_level = "高风险"
        elif self.overall_risk_score >= 40:
            self.risk_level = "中风险"
        else:
            self.risk_level = "低风险"
    
    def get_top_risks(self, limit: int = 10) -> List[RiskItem]:
        """获取风险评分最高的风险项"""
        sorted_risks = sorted(self.all_risks, key=lambda x: x.risk_score, reverse=True)
        return sorted_risks[:limit]
    
    def get_risks_by_category(self, category: str) -> List[RiskItem]:
        """获取指定类别的风险项"""
        return [risk for risk in self.all_risks if risk.category == category]
    
    def get_risks_by_level(self, level: str) -> List[RiskItem]:
        """获取指定等级的风险项"""
        return self.risks_by_level.get(level, [])
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "total_risks": self.total_risks,
            "overall_risk_score": self.overall_risk_score,
            "risk_level": self.risk_level,
            "analysis_timestamp": self.analysis_timestamp,
            "categories": {cat: summ.to_dict() for cat, summ in self.risks_by_category.items()},
            "risks_by_level": {
                level: [risk.to_dict() for risk in risks]
                for level, risks in self.risks_by_level.items()
            },
            "all_risks": [risk.to_dict() for risk in self.all_risks]
        }


class RiskAnalyzer:
    """风险分析器"""
    
    # 风险关键词库
    RISK_KEYWORDS = {
        "technical": [
            # 技术选型风险
            "新技术", "未经验证", "实验性", "alpha", "beta", "测试版", "不稳定",
            "技术债务", "技术债", "遗留代码", "老旧技术", "过时", "淘汰",
            "兼容性", "版本冲突", "依赖问题", "环境配置", "部署复杂",
            "性能瓶颈", "扩展性", "并发能力", "响应时间",
            "单点故障", "高可用", "容错", "灾难恢复",
            "第三方依赖", "外部库", "开源组件", "许可证"
        ],
        "security": [
            # 安全风险
            "安全漏洞", "漏洞", "攻击", "注入", "XSS", "CSRF", "SQL注入",
            "认证", "授权", "权限", "访问控制", "越权", "身份验证",
            "数据泄露", "隐私", "敏感信息", "加密", "脱敏", "掩码",
            "代码安全", "恶意代码", "后门", "木马", "病毒",
            "网络安全", "防火墙", "入侵检测", "DDoS", "网络攻击",
            "日志安全", "审计日志", "操作日志", "安全日志"
        ],
        "compliance": [
            # 合规风险
            "合规", "监管", "法规", "法律", "政策", "条例",
            "数据隐私", "个人信息", "GDPR", "隐私保护", "数据保护",
            "许可协议", "许可证", "版权", "知识产权", "专利",
            "行业标准", "国家标准", "国际标准", "规范", "要求",
            "审计", "检查", "认证", "资质", "认证要求"
        ],
        "implementation": [
            # 实施风险
            "项目延期", "进度风险", "时间不足", "工期紧张",
            "资源不足", "人力不足", "预算不足", "资金短缺",
            "团队能力", "技能不足", "经验不足", "培训需求",
            "沟通问题", "协作困难", "信息不对称", "沟通不畅",
            "需求变更", "范围蔓延", "需求不明确", "需求模糊",
            "测试不足", "测试覆盖", "测试用例", "测试资源",
            "运维风险", "部署风险", "上线风险", "生产环境"
        ]
    }
    
    # 风险等级关键词
    LEVEL_KEYWORDS = {
        "P0": ["完全失效", "数据丢失", "系统崩溃", "安全漏洞", "严重违规", "重大事故", "灾难性"],
        "P1": ["部分失效", "功能缺失", "性能严重下降", "中等风险", "重要问题", "主要功能"],
        "P2": ["功能受限", "性能下降", "维护困难", "使用不便", "次要问题", "一般风险"],
        "P3": ["轻微影响", "界面问题", "提示不明确", "优化建议", "潜在问题", "低风险"]
    }
    
    # 风险缓解措施模板
    MITIGATION_TEMPLATES = {
        "technical": [
            "进行技术验证和原型开发，评估技术可行性",
            "建立技术债务管理机制，定期进行代码重构",
            "制定技术兼容性测试计划，确保系统兼容性",
            "建立技术升级路线图，避免技术过时",
            "设计高可用架构，避免单点故障",
            "制定第三方组件评估标准，选择稳定可靠的组件"
        ],
        "security": [
            "实施安全开发生命周期(SDL)，在开发各阶段考虑安全",
            "建立完善的访问控制机制，实施最小权限原则",
            "对敏感数据进行加密存储和传输",
            "定期进行安全代码审查和漏洞扫描",
            "实施网络安全防护措施，如防火墙、入侵检测",
            "建立安全审计日志机制，记录所有关键操作"
        ],
        "compliance": [
            "进行合规性评估，识别适用的法规和标准",
            "建立数据隐私保护机制，确保符合隐私法规",
            "审查所有第三方组件的许可证，确保合规使用",
            "遵循行业最佳实践和标准规范",
            "建立合规审计机制，定期进行合规检查",
            "制定合规培训计划，提高团队合规意识"
        ],
        "implementation": [
            "制定详细的项目计划，包括风险缓冲时间",
            "进行资源需求分析，确保资源充足",
            "评估团队技能缺口，制定培训计划",
            "建立有效的沟通机制，确保信息畅通",
            "制定需求变更管理流程，控制范围蔓延",
            "制定详细的测试计划和运维方案"
        ]
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        
    def analyze_file(self, file_path: str) -> RiskAnalysisResult:
        """分析蓝图或技术规格书文件中的风险"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if self.verbose:
            print(f"开始风险分析: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建分析结果对象
        result = RiskAnalysisResult(file_path=file_path)
        
        # 分析各类风险
        self._analyze_technical_risks(content, result)
        self._analyze_security_risks(content, result)
        self._analyze_compliance_risks(content, result)
        self._analyze_implementation_risks(content, result)
        
        # 完成分析
        result.finalize()
        self.results.append(result)
        
        if self.verbose:
            print(f"风险分析完成: 发现{result.total_risks}个风险项")
            print(f"总体风险评分: {result.overall_risk_score:.1f} ({result.risk_level})")
        
        return result
    
    def _analyze_technical_risks(self, content: str, result: RiskAnalysisResult):
        """分析技术风险"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 检查技术风险关键词
            for keyword in self.RISK_KEYWORDS["technical"]:
                if keyword in line_lower:
                    # 确定风险等级
                    risk_level = self._determine_risk_level(line)
                    
                    # 确定风险概率和影响
                    probability, impact = self._estimate_probability_impact(line, "technical")
                    
                    # 生成风险ID
                    risk_id = f"TECH-{len(result.all_risks)+1:03d}"
                    
                    # 生成风险项
                    risk = RiskItem(
                        risk_id=risk_id,
                        category="technical",
                        level=risk_level,
                        title=f"技术风险: {keyword}",
                        description=f"在文件中发现技术风险关键词 '{keyword}'。相关上下文: {self._get_context(lines, i, 2)}",
                        probability=probability,
                        impact=impact,
                        mitigation=self._get_mitigation("technical", keyword),
                        detection_method="关键词扫描",
                        owner="技术架构师"
                    )
                    
                    result.add_risk(risk)
                    break  # 每行只检测一个关键词，避免重复
    
    def _analyze_security_risks(self, content: str, result: RiskAnalysisResult):
        """分析安全风险"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 检查安全风险关键词
            for keyword in self.RISK_KEYWORDS["security"]:
                if keyword in line_lower:
                    # 确定风险等级
                    risk_level = self._determine_risk_level(line)
                    
                    # 确定风险概率和影响
                    probability, impact = self._estimate_probability_impact(line, "security")
                    
                    # 生成风险ID
                    risk_id = f"SEC-{len(result.all_risks)+1:03d}"
                    
                    # 生成风险项
                    risk = RiskItem(
                        risk_id=risk_id,
                        category="security",
                        level=risk_level,
                        title=f"安全风险: {keyword}",
                        description=f"在文件中发现安全风险关键词 '{keyword}'。相关上下文: {self._get_context(lines, i, 2)}",
                        probability=probability,
                        impact=impact,
                        mitigation=self._get_mitigation("security", keyword),
                        detection_method="关键词扫描",
                        owner="安全工程师"
                    )
                    
                    result.add_risk(risk)
                    break
    
    def _analyze_compliance_risks(self, content: str, result: RiskAnalysisResult):
        """分析合规风险"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 检查合规风险关键词
            for keyword in self.RISK_KEYWORDS["compliance"]:
                if keyword in line_lower:
                    # 确定风险等级
                    risk_level = self._determine_risk_level(line)
                    
                    # 确定风险概率和影响
                    probability, impact = self._estimate_probability_impact(line, "compliance")
                    
                    # 生成风险ID
                    risk_id = f"COMP-{len(result.all_risks)+1:03d}"
                    
                    # 生成风险项
                    risk = RiskItem(
                        risk_id=risk_id,
                        category="compliance",
                        level=risk_level,
                        title=f"合规风险: {keyword}",
                        description=f"在文件中发现合规风险关键词 '{keyword}'。相关上下文: {self._get_context(lines, i, 2)}",
                        probability=probability,
                        impact=impact,
                        mitigation=self._get_mitigation("compliance", keyword),
                        detection_method="关键词扫描",
                        owner="合规专员"
                    )
                    
                    result.add_risk(risk)
                    break
    
    def _analyze_implementation_risks(self, content: str, result: RiskAnalysisResult):
        """分析实施风险"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 检查实施风险关键词
            for keyword in self.RISK_KEYWORDS["implementation"]:
                if keyword in line_lower:
                    # 确定风险等级
                    risk_level = self._determine_risk_level(line)
                    
                    # 确定风险概率和影响
                    probability, impact = self._estimate_probability_impact(line, "implementation")
                    
                    # 生成风险ID
                    risk_id = f"IMPL-{len(result.all_risks)+1:03d}"
                    
                    # 生成风险项
                    risk = RiskItem(
                        risk_id=risk_id,
                        category="implementation",
                        level=risk_level,
                        title=f"实施风险: {keyword}",
                        description=f"在文件中发现实施风险关键词 '{keyword}'。相关上下文: {self._get_context(lines, i, 2)}",
                        probability=probability,
                        impact=impact,
                        mitigation=self._get_mitigation("implementation", keyword),
                        detection_method="关键词扫描",
                        owner="项目经理"
                    )
                    
                    result.add_risk(risk)
                    break
    
    def _determine_risk_level(self, line: str) -> str:
        """根据行内容确定风险等级"""
        line_lower = line.lower()
        
        # 检查P0关键词
        for keyword in self.LEVEL_KEYWORDS["P0"]:
            if keyword in line_lower:
                return "P0"
        
        # 检查P1关键词
        for keyword in self.LEVEL_KEYWORDS["P1"]:
            if keyword in line_lower:
                return "P1"
        
        # 检查P2关键词
        for keyword in self.LEVEL_KEYWORDS["P2"]:
            if keyword in line_lower:
                return "P2"
        
        # 默认P3
        return "P3"
    
    def _estimate_probability_impact(self, line: str, category: str) -> Tuple[float, float]:
        """估计风险发生概率和影响程度"""
        # 基于风险类别和内容长度进行简单估计
        line_length = len(line)
        
        # 概率估计：行越长，可能描述越详细，概率可能越高
        probability = min(1.0, line_length / 200.0)
        
        # 影响估计：基于风险类别
        impact_by_category = {
            "technical": 0.7,
            "security": 0.9,
            "compliance": 0.8,
            "implementation": 0.6
        }
        
        impact = impact_by_category.get(category, 0.5)
        
        return probability, impact
    
    def _get_context(self, lines: List[str], line_index: int, context_lines: int = 2) -> str:
        """获取上下文内容"""
        start = max(0, line_index - context_lines)
        end = min(len(lines), line_index + context_lines + 1)
        
        context = []
        for i in range(start, end):
            prefix = ">>> " if i == line_index else "    "
            context.append(f"{prefix}{lines[i]}")
        
        return "\n".join(context)
    
    def _get_mitigation(self, category: str, keyword: str) -> str:
        """获取风险缓解措施"""
        templates = self.MITIGATION_TEMPLATES.get(category, [])
        if templates:
            # 基于关键词简单选择模板
            keyword_hash = sum(ord(c) for c in keyword)
            template_index = keyword_hash % len(templates)
            return templates[template_index]
        else:
            return "制定具体的风险缓解计划，包括预防措施和应急方案"
    
    def generate_report(self, result: RiskAnalysisResult) -> str:
        """生成风险分析报告"""
        report = []
        report.append("=" * 80)
        report.append("风险分析报告")
        report.append("=" * 80)
        report.append(f"分析文件: {result.file_path}")
        report.append(f"分析时间: {result.analysis_timestamp}")
        report.append("")
        
        report.append("1. 总体风险概况")
        report.append("-" * 40)
        report.append(f"风险项总数: {result.total_risks}")
        report.append(f"总体风险评分: {result.overall_risk_score:.1f}/100")
        report.append(f"风险等级: {result.risk_level}")
        report.append("")
        
        report.append("2. 风险分类统计")
        report.append("-" * 40)
        for category, summary in result.risks_by_category.items():
            if summary.total_risks > 0:
                report.append(f"{category.upper()}风险:")
                report.append(f"  总数: {summary.total_risks} | P0: {summary.p0_count} | P1: {summary.p1_count} | P2: {summary.p2_count} | P3: {summary.p3_count}")
                report.append(f"  平均风险评分: {summary.avg_score:.1f}")
                report.append("")
        
        report.append("3. 高风险项 (Top 10)")
        report.append("-" * 40)
        top_risks = result.get_top_risks(limit=10)
        if top_risks:
            for i, risk in enumerate(top_risks, 1):
                report.append(f"{i}. [{risk.level}] {risk.title} (评分: {risk.risk_score:.1f})")
                report.append(f"   描述: {risk.description[:100]}...")
                report.append(f"   缓解措施: {risk.mitigation}")
                report.append(f"   负责人: {risk.owner}")
                report.append("")
        else:
            report.append("未发现高风险项")
            report.append("")
        
        report.append("4. 风险等级分布")
        report.append("-" * 40)
        for level in ["P0", "P1", "P2", "P3"]:
            risks = result.get_risks_by_level(level)
            if risks:
                report.append(f"{level}风险 ({len(risks)}项):")
                for risk in risks[:3]:  # 只显示前3项
                    report.append(f"  • {risk.title} (评分: {risk.risk_score:.1f})")
                if len(risks) > 3:
                    report.append(f"  ... 还有{len(risks)-3}项{level}风险")
                report.append("")
        
        report.append("5. 风险应对建议")
        report.append("-" * 40)
        
        # 根据风险等级给出建议
        p0_count = len(result.get_risks_by_level("P0"))
        p1_count = len(result.get_risks_by_level("P1"))
        
        if p0_count > 0:
            report.append("[FAIL] 发现P0极高风险项，建议:")
            report.append("  • 立即停止相关开发工作")
            report.append("  • 召开紧急风险评估会议")
            report.append("  • 制定详细的风险应对计划")
            report.append("  • 考虑重新设计技术方案")
        elif p1_count > 3:
            report.append("[WARNING] 发现较多P1高风险项，建议:")
            report.append("  • 优先处理高风险项")
            report.append("  • 制定详细的风险缓解计划")
            report.append("  • 增加风险缓冲时间和资源")
            report.append("  • 加强技术验证和测试")
        elif result.total_risks > 10:
            report.append("[WARNING] 风险项较多，建议:")
            report.append("  • 建立风险管理机制")
            report.append("  • 定期进行风险评估")
            report.append("  • 加强项目监控和控制")
            report.append("  • 完善项目文档和沟通")
        else:
            report.append("[OK] 风险可控，建议:")
            report.append("  • 继续按计划实施")
            report.append("  • 保持风险监控")
            report.append("  • 定期更新风险评估")
        
        report.append("")
        report.append("6. 后续行动")
        report.append("-" * 40)
        report.append("1. 召开风险评估会议，讨论所有风险项")
        report.append("2. 为每个风险项制定具体的缓解措施")
        report.append("3. 分配风险负责人，跟踪风险状态")
        report.append("4. 建立风险监控机制，定期更新风险评估")
        report.append("5. 将风险管理纳入项目日常管理")
        
        report.append("")
        report.append("=" * 80)
        report.append("报告生成完毕")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_to_json(self, result: RiskAnalysisResult, output_path: str = None) -> str:
        """导出风险分析结果为JSON格式"""
        if output_path is None:
            output_path = f"risk_analysis_{Path(result.file_path).stem}.json"
        
        data = result.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def export_to_csv(self, result: RiskAnalysisResult, output_path: str = None) -> str:
        """导出风险分析结果为CSV格式"""
        if output_path is None:
            output_path = f"risk_analysis_{Path(result.file_path).stem}.csv"
        
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                "风险ID", "类别", "等级", "标题", "描述", 
                "概率", "影响", "风险评分", "缓解措施", 
                "检测方法", "负责人", "状态", "创建时间"
            ])
            
            # 写入数据行
            for risk in result.all_risks:
                writer.writerow([
                    risk.risk_id,
                    risk.category,
                    risk.level,
                    risk.title,
                    risk.description[:200],  # 限制描述长度
                    f"{risk.probability:.2f}",
                    f"{risk.impact:.2f}",
                    f"{risk.risk_score:.1f}",
                    risk.mitigation,
                    risk.detection_method,
                    risk.owner,
                    risk.status,
                    risk.created_at
                ])
        
        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="风险分析工具")
    parser.add_argument("--verbose", action="store_true", help="显示详细分析过程")
    parser.add_argument("--report", action="store_true", help="生成详细的风险分析报告")
    parser.add_argument("--input", type=str, help="指定输入文件（蓝图或技术规格书）")
    parser.add_argument("--risk-level", type=str, choices=["P0", "P1", "P2", "P3"], help="只显示指定风险等级的风险项")
    parser.add_argument("--export-json", type=str, help="导出JSON结果到指定文件")
    parser.add_argument("--export-csv", type=str, help="导出CSV结果到指定文件")
    
    args = parser.parse_args()
    
    # 如果没有指定输入文件，尝试使用默认测试文件
    if args.input is None:
        # 检查是否存在测试蓝图文件
        default_files = [
            "docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md",
            "docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/TECHNICAL_SPECIFICATION_TEMPLATE.md"
        ]
        
        for file in default_files:
            if os.path.exists(file):
                args.input = file
                break
        
        if args.input is None:
            print("错误: 请使用 --input 参数指定要分析的文件")
            print("或确保以下文件之一存在:")
            for file in default_files:
                print(f"  - {file}")
            sys.exit(1)
    
    try:
        # 创建分析器
        analyzer = RiskAnalyzer(verbose=args.verbose)
        
        # 分析文件
        result = analyzer.analyze_file(args.input)
        
        # 输出结果
        if args.risk_level:
            risks = result.get_risks_by_level(args.risk_level)
            print(f"{args.risk_level}风险项 ({len(risks)}项):")
            print("-" * 60)
            for risk in risks:
                print(f"[{risk.risk_id}] {risk.title} (评分: {risk.risk_score:.1f})")
                print(f"  描述: {risk.description[:100]}...")
                print(f"  缓解措施: {risk.mitigation}")
                print()
        elif args.report:
            report = analyzer.generate_report(result)
            print(report)
        else:
            print(f"风险分析完成:")
            print(f"  文件: {result.file_path}")
            print(f"  风险项总数: {result.total_risks}")
            print(f"  总体风险评分: {result.overall_risk_score:.1f}/100")
            print(f"  风险等级: {result.risk_level}")
            print("")
            print("风险分类统计:")
            for category, summary in result.risks_by_category.items():
                if summary.total_risks > 0:
                    print(f"  {category.upper()}: {summary.total_risks}项 (P0:{summary.p0_count} P1:{summary.p1_count} P2:{summary.p2_count} P3:{summary.p3_count})")
            
            # 显示前3个高风险项
            top_risks = result.get_top_risks(limit=3)
            if top_risks:
                print("")
                print("高风险项 (Top 3):")
                for i, risk in enumerate(top_risks, 1):
                    print(f"  {i}. [{risk.level}] {risk.title} (评分: {risk.risk_score:.1f})")
        
        # 导出结果
        if args.export_json:
            output_file = analyzer.export_to_json(result, args.export_json)
            print(f"JSON结果已导出到: {output_file}")
        elif args.export_csv:
            output_file = analyzer.export_to_csv(result, args.export_csv)
            print(f"CSV结果已导出到: {output_file}")
        elif args.report and not args.risk_level:
            # 自动生成JSON文件
            output_file = analyzer.export_to_json(result)
            print(f"JSON结果已导出到: {output_file}")
            
    except Exception as e:
        print(f"风险分析过程中发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()