#!/usr/bin/env python3
"""
职责描述自动生成器

功能:
- 分析文档内容，提取关键信息
- 根据模板自动生成职责描述
- 支持多种文档类型和领域
- 生成符合专业量化机构标准的职责描述
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    BLUEPRINT = "blueprint"
    TECHNICAL_SPEC = "technical_spec"
    IMPLEMENTATION_GUIDE = "implementation_guide"
    GOVERNANCE_DOC = "governance_doc"


class DomainType(Enum):
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_MANAGEMENT = "risk_management"
    TRADING_EXECUTION = "trading_execution"
    DATA_GOVERNANCE = "data_governance"
    AI_ML = "ai_ml"
    SYSTEM_ARCHITECTURE = "system_architecture"


@dataclass
class DocumentInfo:
    filepath: str
    filename: str
    title: str
    module_id: str
    domain: DomainType
    doc_type: DocumentType
    keywords: List[str]
    functions: List[str]
    technologies: List[str]
    features: List[str]


@dataclass
class ResponsibilityTemplate:
    template: str
    domain: DomainType
    keywords: List[str]
    example: str


class ResponsibilityGenerator:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.templates = self._load_templates()
        self.domain_keywords = self._load_domain_keywords()
        self.technology_patterns = self._load_technology_patterns()
        
    def _load_templates(self) -> Dict[DomainType, List[ResponsibilityTemplate]]:
        """加载职责描述模板"""
        return {
            DomainType.PORTFOLIO_OPTIMIZATION: [
                ResponsibilityTemplate(
                    template="{module_name}，负责基于{method}的投资组合优化，支持{feature1}、{feature2}、{feature3}等功能",
                    domain=DomainType.PORTFOLIO_OPTIMIZATION,
                    keywords=["优化", "投资组合", "权重", "配置"],
                    example="均值方差优化器，负责基于预期收益和风险协方差矩阵的投资组合优化，支持约束条件处理、边界优化、数值稳定性优化等功能"
                ),
                ResponsibilityTemplate(
                    template="{module_name}，负责构建{strategy}投资组合，实现{goal}，支持{feature1}、{feature2}、{feature3}等功能",
                    domain=DomainType.PORTFOLIO_OPTIMIZATION,
                    keywords=["策略", "配置", "风险"],
                    example="风险平价策略模块，负责构建风险平价投资组合，实现风险均衡配置，支持风险预算分配、相关性调整、杠杆优化等功能"
                ),
            ],
            DomainType.RISK_MANAGEMENT: [
                ResponsibilityTemplate(
                    template="{module_name}，负责实时监控投资组合的{metric}，支持{method1}、{method2}、{method3}等多种计算方法，提供{feature}功能",
                    domain=DomainType.RISK_MANAGEMENT,
                    keywords=["监控", "风险", "VaR", "ES"],
                    example="VaR/ES监控系统，负责实时监控投资组合的风险价值和预期损失，支持历史模拟法、蒙特卡洛模拟、参数法等多种计算方法，提供风险预警和报告生成功能"
                ),
                ResponsibilityTemplate(
                    template="{module_name}，负责分解投资组合{target}，识别{result}，支持{feature1}、{feature2}、{feature3}等功能",
                    domain=DomainType.RISK_MANAGEMENT,
                    keywords=["归因", "分解", "因子"],
                    example="风险归因系统，负责分解投资组合风险来源，识别主要风险因子，支持多因子风险模型、边际风险贡献计算、风险暴露分析等功能"
                ),
            ],
            DomainType.TRADING_EXECUTION: [
                ResponsibilityTemplate(
                    template="{module_name}，负责优化交易执行{target}，最小化{cost}，支持{algo1}、{algo2}、{algo3}等多种执行算法，提供{feature}功能",
                    domain=DomainType.TRADING_EXECUTION,
                    keywords=["执行", "交易", "算法", "TWAP", "VWAP"],
                    example="智能执行引擎，负责优化交易执行路径，最小化市场冲击和交易成本，支持TWAP、VWAP、POV等多种执行算法，提供实时执行监控和调整功能"
                ),
                ResponsibilityTemplate(
                    template="{module_name}，负责将{action}并路由至最优交易场所，支持{feature1}、{feature2}、{feature3}等功能，优化{goal}",
                    domain=DomainType.TRADING_EXECUTION,
                    keywords=["路由", "订单", "拆分"],
                    example="智能订单路由器，负责将大额订单拆分并路由至最优交易场所，支持多市场路由、流动性检测、暗池接入等功能，优化执行价格和成本"
                ),
            ],
            DomainType.DATA_GOVERNANCE: [
                ResponsibilityTemplate(
                    template="{module_name}，负责数据资产的{action1}、{action2}、{action3}和元数据管理，提升数据治理能力，支持{feature1}、{feature2}、{feature3}等功能",
                    domain=DomainType.DATA_GOVERNANCE,
                    keywords=["数据", "目录", "血缘", "元数据"],
                    example="数据目录系统，负责数据资产的注册、发现、血缘追踪和元数据管理，提升数据治理能力，支持数据资产目录化、数据血缘可视化、数据质量监控等功能"
                ),
                ResponsibilityTemplate(
                    template="{module_name}，负责实时检测数据{issue}，确保数据质量符合{requirement}，支持{feature1}、{feature2}、{feature3}等功能",
                    domain=DomainType.DATA_GOVERNANCE,
                    keywords=["质量", "监控", "异常"],
                    example="数据质量监控系统，负责实时检测数据异常、缺失、延迟等问题，确保数据质量符合交易要求，支持数据质量评分、异常告警、质量报告生成等功能"
                ),
            ],
            DomainType.AI_ML: [
                ResponsibilityTemplate(
                    template="{module_name}，负责利用{technology}识别{target}，包括{feature1}、{feature2}、{feature3}等功能，支持{model1}、{model2}等深度学习模型",
                    domain=DomainType.AI_ML,
                    keywords=["AI", "机器学习", "识别", "模式"],
                    example="AI模式识别引擎，负责利用机器学习技术识别市场交易模式，包括趋势识别、反转信号检测、异常波动预警等功能，支持LSTM、Transformer等深度学习模型"
                ),
                ResponsibilityTemplate(
                    template="{module_name}，负责利用{method}优化{target}，支持{feature1}、{feature2}、{feature3}等功能，实现{goal}",
                    domain=DomainType.AI_ML,
                    keywords=["强化学习", "优化", "决策"],
                    example="强化学习再平衡系统，负责利用强化学习算法优化再平衡决策，支持状态空间建模、奖励函数设计、策略网络训练等功能，实现自适应再平衡策略"
                ),
            ],
            DomainType.SYSTEM_ARCHITECTURE: [
                ResponsibilityTemplate(
                    template="{module_name}，负责{action}，支持{feature1}、{feature2}、{feature3}等功能，提供{benefit}",
                    domain=DomainType.SYSTEM_ARCHITECTURE,
                    keywords=["架构", "系统", "服务"],
                    example="事件驱动架构模块，负责处理系统事件的生产、检测和消费，支持异步通信、事件溯源、CQRS等功能，提供高可用性和可扩展性"
                ),
            ],
        }
    
    def _load_domain_keywords(self) -> Dict[DomainType, List[str]]:
        """加载领域关键词"""
        return {
            DomainType.PORTFOLIO_OPTIMIZATION: [
                "投资组合", "优化", "权重", "配置", "均值方差", "风险平价",
                "Black-Litterman", "有效前沿", "夏普比率", "约束", "优化器"
            ],
            DomainType.RISK_MANAGEMENT: [
                "风险", "VaR", "ES", "CVaR", "监控", "归因", "止损",
                "压力测试", "风险因子", "风险暴露", "风险预算"
            ],
            DomainType.TRADING_EXECUTION: [
                "交易", "执行", "订单", "路由", "TWAP", "VWAP", "POV",
                "市场冲击", "执行成本", "算法交易", "智能执行"
            ],
            DomainType.DATA_GOVERNANCE: [
                "数据", "目录", "血缘", "元数据", "质量", "生命周期",
                "数据湖", "数据编织", "数据资产", "数据治理"
            ],
            DomainType.AI_ML: [
                "AI", "机器学习", "深度学习", "LSTM", "Transformer",
                "强化学习", "因子挖掘", "特征工程", "模型集成", "模式识别"
            ],
            DomainType.SYSTEM_ARCHITECTURE: [
                "架构", "微服务", "事件驱动", "高可用", "可扩展",
                "API", "服务", "系统", "模块", "组件"
            ],
        }
    
    def _load_technology_patterns(self) -> Dict[str, List[str]]:
        """加载技术模式"""
        return {
            "optimization_methods": [
                "均值方差", "风险平价", "Black-Litterman", "鲁棒优化",
                "随机优化", "动态规划", "遗传算法"
            ],
            "risk_metrics": [
                "VaR", "ES", "CVaR", "夏普比率", "最大回撤",
                "波动率", "相关性", "贝塔"
            ],
            "execution_algorithms": [
                "TWAP", "VWAP", "POV", "IS", "自适应算法"
            ],
            "ml_models": [
                "LSTM", "Transformer", "CNN", "RNN", "随机森林",
                "XGBoost", "强化学习", "深度学习"
            ],
            "data_technologies": [
                "数据湖", "数据编织", "数据仓库", "ETL", "流处理",
                "批处理", "实时计算"
            ],
        }
    
    def analyze_document(self, filepath: str) -> DocumentInfo:
        """分析文档内容"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        
        title = self._extract_title(content)
        module_id = self._extract_module_id(content)
        domain = self._detect_domain(content, title)
        doc_type = self._detect_document_type(filepath, content)
        keywords = self._extract_keywords(content)
        functions = self._extract_functions(content)
        technologies = self._extract_technologies(content)
        features = self._extract_features(content)
        
        return DocumentInfo(
            filepath=filepath,
            filename=filename,
            title=title,
            module_id=module_id,
            domain=domain,
            doc_type=doc_type,
            keywords=keywords,
            functions=functions,
            technologies=technologies,
            features=features
        )
    
    def _extract_title(self, content: str) -> str:
        """提取文档标题"""
        title_pattern = r'^#\s+(.+?)$'
        match = re.search(title_pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_module_id(self, content: str) -> str:
        """提取模块ID"""
        module_id_pattern = r'module_id:\s*(.+)'
        match = re.search(module_id_pattern, content)
        if match:
            return match.group(1).strip()
        return ""
    
    def _detect_domain(self, content: str, title: str) -> DomainType:
        """检测文档领域"""
        combined_text = f"{title} {content}".lower()
        
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            domain_scores[domain] = score
        
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])
            if best_domain[1] > 0:
                return best_domain[0]
        
        return DomainType.SYSTEM_ARCHITECTURE
    
    def _detect_document_type(self, filepath: str, content: str) -> DocumentType:
        """检测文档类型"""
        if 'BLUEPRINT' in filepath.upper():
            return DocumentType.BLUEPRINT
        elif 'TECHNICAL_SPEC' in filepath.upper():
            return DocumentType.TECHNICAL_SPEC
        elif 'IMPLEMENTATION_GUIDE' in filepath.upper():
            return DocumentType.IMPLEMENTATION_GUIDE
        elif 'GOVERNANCE' in filepath.upper():
            return DocumentType.GOVERNANCE_DOC
        return DocumentType.BLUEPRINT
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        keyword_patterns = [
            r'关键词[：:]\s*(.+?)(?:\n|$)',
            r'关键字[：:]\s*(.+?)(?:\n|$)',
            r'Keywords[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                keyword_text = match.group(1).strip()
                keywords.extend([k.strip() for k in keyword_text.split(',')])
                break
        
        return keywords
    
    def _extract_functions(self, content: str) -> List[str]:
        """提取功能列表"""
        functions = []
        
        function_patterns = [
            r'功能[：:]\s*(.+?)(?:\n\n|\n#)',
            r'主要功能[：:]\s*(.+?)(?:\n\n|\n#)',
            r'核心功能[：:]\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in function_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                func_text = match.group(1).strip()
                func_items = re.findall(r'[-•]\s*(.+?)(?:\n|$)', func_text)
                functions.extend([f.strip() for f in func_items])
                break
        
        return functions
    
    def _extract_technologies(self, content: str) -> List[str]:
        """提取技术列表"""
        technologies = []
        
        for tech_category, tech_list in self.technology_patterns.items():
            for tech in tech_list:
                if tech.lower() in content.lower():
                    technologies.append(tech)
        
        return technologies
    
    def _extract_features(self, content: str) -> List[str]:
        """提取特性列表"""
        features = []
        
        feature_patterns = [
            r'支持(.+?)功能',
            r'提供(.+?)功能',
            r'实现(.+?)功能',
            r'包括(.+?)功能',
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                feature_items = [f.strip() for f in match.split('、')]
                features.extend(feature_items)
        
        return features
    
    def generate_responsibility(self, doc_info: DocumentInfo) -> str:
        """生成职责描述"""
        templates = self.templates.get(doc_info.domain, [])
        
        if not templates:
            return self._generate_generic_responsibility(doc_info)
        
        best_template = self._select_best_template(doc_info, templates)
        
        return self._fill_template(best_template, doc_info)
    
    def _select_best_template(self, doc_info: DocumentInfo, templates: List[ResponsibilityTemplate]) -> ResponsibilityTemplate:
        """选择最佳模板"""
        best_score = -1
        best_template = templates[0]
        
        for template in templates:
            score = sum(1 for keyword in template.keywords if keyword in doc_info.keywords)
            score += sum(1 for keyword in template.keywords if keyword in doc_info.title.lower())
            
            if score > best_score:
                best_score = score
                best_template = template
        
        return best_template
    
    def _fill_template(self, template: ResponsibilityTemplate, doc_info: DocumentInfo) -> str:
        """填充模板"""
        result = template.template
        
        module_name = self._extract_module_name(doc_info)
        
        result = result.replace("{module_name}", module_name)
        
        placeholders = re.findall(r'\{(\w+)\}', result)
        
        for i, placeholder in enumerate(placeholders):
            if placeholder == "module_name":
                continue
            
            value = self._get_placeholder_value(placeholder, doc_info, i)
            result = result.replace(f"{{{placeholder}}}", value, 1)
        
        return result
    
    def _extract_module_name(self, doc_info: DocumentInfo) -> str:
        """提取模块名称"""
        title = doc_info.title
        
        title = re.sub(r'蓝图$', '', title)
        title = re.sub(r'文档$', '', title)
        title = re.sub(r'系统$', '', title)
        title = re.sub(r'模块$', '', title)
        
        return title.strip()
    
    def _get_placeholder_value(self, placeholder: str, doc_info: DocumentInfo, index: int) -> str:
        """获取占位符值"""
        if "method" in placeholder:
            return self._get_method(doc_info, index)
        elif "feature" in placeholder:
            return self._get_feature(doc_info, index)
        elif "algo" in placeholder:
            return self._get_algorithm(doc_info, index)
        elif "model" in placeholder:
            return self._get_model(doc_info, index)
        elif "metric" in placeholder:
            return self._get_metric(doc_info, index)
        elif "target" in placeholder:
            return self._get_target(doc_info, index)
        elif "cost" in placeholder:
            return self._get_cost(doc_info, index)
        elif "action" in placeholder:
            return self._get_action(doc_info, index)
        elif "goal" in placeholder:
            return self._get_goal(doc_info, index)
        elif "strategy" in placeholder:
            return self._get_strategy(doc_info, index)
        elif "technology" in placeholder:
            return self._get_technology(doc_info, index)
        elif "issue" in placeholder:
            return self._get_issue(doc_info, index)
        elif "requirement" in placeholder:
            return self._get_requirement(doc_info, index)
        elif "benefit" in placeholder:
            return self._get_benefit(doc_info, index)
        elif "result" in placeholder:
            return self._get_result(doc_info, index)
        else:
            return self._get_feature(doc_info, index)
    
    def _get_method(self, doc_info: DocumentInfo, index: int) -> str:
        """获取方法"""
        methods = {
            DomainType.PORTFOLIO_OPTIMIZATION: ["预期收益和风险协方差矩阵", "风险预算模型", "Black-Litterman模型"],
            DomainType.RISK_MANAGEMENT: ["历史模拟法", "蒙特卡洛模拟", "参数法"],
            DomainType.TRADING_EXECUTION: ["TWAP算法", "VWAP算法", "POV算法"],
            DomainType.AI_ML: ["机器学习技术", "深度学习技术", "强化学习算法"],
        }
        
        domain_methods = methods.get(doc_info.domain, ["标准方法"])
        return domain_methods[index % len(domain_methods)]
    
    def _get_feature(self, doc_info: DocumentInfo, index: int) -> str:
        """获取功能"""
        if doc_info.features:
            return doc_info.features[index % len(doc_info.features)]
        
        default_features = {
            DomainType.PORTFOLIO_OPTIMIZATION: ["约束条件处理", "边界优化", "数值稳定性优化"],
            DomainType.RISK_MANAGEMENT: ["风险预警", "报告生成", "实时监控"],
            DomainType.TRADING_EXECUTION: ["实时监控", "动态调整", "成本优化"],
            DomainType.DATA_GOVERNANCE: ["数据资产目录化", "数据血缘可视化", "数据质量监控"],
            DomainType.AI_ML: ["趋势识别", "模式检测", "异常预警"],
            DomainType.SYSTEM_ARCHITECTURE: ["高可用性", "可扩展性", "性能优化"],
        }
        
        domain_features = default_features.get(doc_info.domain, ["核心功能"])
        return domain_features[index % len(domain_features)]
    
    def _get_algorithm(self, doc_info: DocumentInfo, index: int) -> str:
        """获取算法"""
        algorithms = ["TWAP", "VWAP", "POV", "IS", "自适应算法"]
        return algorithms[index % len(algorithms)]
    
    def _get_model(self, doc_info: DocumentInfo, index: int) -> str:
        """获取模型"""
        models = ["LSTM", "Transformer", "CNN", "RNN", "随机森林"]
        return models[index % len(models)]
    
    def _get_metric(self, doc_info: DocumentInfo, index: int) -> str:
        """获取指标"""
        metrics = ["风险价值", "预期损失", "波动率", "最大回撤"]
        return metrics[index % len(metrics)]
    
    def _get_target(self, doc_info: DocumentInfo, index: int) -> str:
        """获取目标"""
        targets = {
            DomainType.PORTFOLIO_OPTIMIZATION: "投资组合权重",
            DomainType.RISK_MANAGEMENT: "风险来源",
            DomainType.TRADING_EXECUTION: "执行路径",
            DomainType.AI_ML: "再平衡决策",
        }
        return targets.get(doc_info.domain, "核心目标")
    
    def _get_cost(self, doc_info: DocumentInfo, index: int) -> str:
        """获取成本"""
        costs = ["市场冲击", "交易成本", "执行成本"]
        return costs[index % len(costs)]
    
    def _get_action(self, doc_info: DocumentInfo, index: int) -> str:
        """获取动作"""
        actions = {
            DomainType.DATA_GOVERNANCE: ["注册", "发现", "追踪"],
            DomainType.TRADING_EXECUTION: ["大额订单拆分"],
        }
        
        domain_actions = actions.get(doc_info.domain, ["处理", "管理", "优化"])
        return domain_actions[index % len(domain_actions)]
    
    def _get_goal(self, doc_info: DocumentInfo, index: int) -> str:
        """获取目标"""
        goals = {
            DomainType.PORTFOLIO_OPTIMIZATION: "风险均衡配置",
            DomainType.TRADING_EXECUTION: "执行价格和成本",
            DomainType.AI_ML: "自适应策略",
        }
        return goals.get(doc_info.domain, "核心目标")
    
    def _get_strategy(self, doc_info: DocumentInfo, index: int) -> str:
        """获取策略"""
        strategies = ["风险平价", "均值方差", "Black-Litterman"]
        return strategies[index % len(strategies)]
    
    def _get_technology(self, doc_info: DocumentInfo, index: int) -> str:
        """获取技术"""
        technologies = ["机器学习技术", "深度学习技术", "强化学习算法", "神经网络"]
        return technologies[index % len(technologies)]
    
    def _get_issue(self, doc_info: DocumentInfo, index: int) -> str:
        """获取问题"""
        issues = ["异常", "缺失", "延迟"]
        return issues[index % len(issues)]
    
    def _get_requirement(self, doc_info: DocumentInfo, index: int) -> str:
        """获取要求"""
        requirements = ["交易要求", "业务需求", "质量标准"]
        return requirements[index % len(requirements)]
    
    def _get_benefit(self, doc_info: DocumentInfo, index: int) -> str:
        """获取收益"""
        benefits = ["高可用性和可扩展性", "性能优化", "成本降低"]
        return benefits[index % len(benefits)]
    
    def _get_result(self, doc_info: DocumentInfo, index: int) -> str:
        """获取结果"""
        results = ["主要风险因子", "风险暴露", "风险贡献"]
        return results[index % len(results)]
    
    def _generate_generic_responsibility(self, doc_info: DocumentInfo) -> str:
        """生成通用职责描述"""
        module_name = self._extract_module_name(doc_info)
        
        if doc_info.features:
            features_str = "、".join(doc_info.features[:3])
            return f"{module_name}，负责{module_name.lower()}相关功能，包括{features_str}等"
        
        return f"{module_name}，负责{module_name.lower()}的核心功能，提供关键业务支持"
    
    def run(self, filepath: Optional[str] = None, output_file: Optional[str] = None):
        """运行生成器"""
        print('=' * 80)
        print('职责描述自动生成器')
        print('=' * 80)
        print()
        
        if filepath:
            doc_info = self.analyze_document(filepath)
            responsibility = self.generate_responsibility(doc_info)
            
            print(f'文档: {doc_info.filename}')
            print(f'标题: {doc_info.title}')
            print(f'领域: {doc_info.domain.value}')
            print(f'模块ID: {doc_info.module_id}')
            print()
            print(f'生成的职责描述:')
            print(f'  {responsibility}')
            print()
            
            if output_file:
                result = {
                    'filepath': filepath,
                    'filename': doc_info.filename,
                    'title': doc_info.title,
                    'module_id': doc_info.module_id,
                    'domain': doc_info.domain.value,
                    'responsibility': responsibility
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f'✅ 结果已保存到: {output_file}')
        else:
            print('批量生成模式')
            print()
            
            blueprints_path = Path(self.blueprints_dir)
            if not blueprints_path.exists():
                print(f'❌ 蓝图目录不存在: {self.blueprints_dir}')
                return
            
            blueprint_files = list(blueprints_path.glob('**/*.md'))
            print(f'找到 {len(blueprint_files)} 个蓝图文件')
            print()
            
            results = []
            for i, blueprint_file in enumerate(blueprint_files[:10], 1):
                print(f'处理 [{i}/{min(10, len(blueprint_files))}]: {blueprint_file.name}')
                
                try:
                    doc_info = self.analyze_document(str(blueprint_file))
                    responsibility = self.generate_responsibility(doc_info)
                    
                    results.append({
                        'filepath': str(blueprint_file),
                        'filename': blueprint_file.name,
                        'title': doc_info.title,
                        'module_id': doc_info.module_id,
                        'domain': doc_info.domain.value,
                        'responsibility': responsibility
                    })
                    
                    print(f'  ✅ {responsibility[:80]}...')
                except Exception as e:
                    print(f'  ❌ 错误: {e}')
                
                print()
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f'✅ 结果已保存到: {output_file}')
        
        print('=' * 80)
        print('生成完成')
        print('=' * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='职责描述自动生成器')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    generator = ResponsibilityGenerator()
    generator.run(filepath=args.file, output_file=args.output)


if __name__ == '__main__':
    main()
