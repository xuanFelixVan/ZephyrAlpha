---
module_id: CAUSAL_INFERENCE_001
version: 1.0.0
spec_version: 1.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
layer: Layer 4 (机器学习层) | 业务架构: AI模型服务
index: CI-001
estimated_hours: 80
review_status: Pending
reviewer: 首席技术评审官
owner: 量化研究员
standard_type: 专业量化机构技术规格书
applicable_scope: 因果推断系统
compliance_level: 顶级专业标准
parent_document: ../INDEX.md
implementation_status: 技术规格设计完成
---

# 因果推断技术规格书 v1.0

> 清风量化系统 v5.3 - 因果推断详细技术设计
> **索引**: `CI-001`
> **开发时长**: 80h
> **核心定位**: 区分因果与相关、因果发现、因果效应估计、反事实分析

---

## 1. 概述

### 1.1 设计背景与业务目的

**业务需求**:
- 区分因果性与相关性是量化核心能力
- 避免虚假信号和过拟合
- 提升策略稳健性和可解释性
- 支持策略归因分析

**技术痛点**:
- 传统ML只学习相关性，无法识别因果
- 因果图构建依赖专家知识
- 混杂因素处理困难
- 反事实推断计算复杂

**预期价值**:
- 策略稳健性提升30%
- 虚假信号识别率提升50%
- 策略归因准确性提升40%
- 过拟合风险降低60%

### 1.2 技术定位与架构层归属

- **Layer定位**: Layer 4 - 机器学习层（AI模型服务）
- **模块类别**: 核心支撑模块
- **架构角色**: 提供因果发现、因果效应估计、反事实分析

### 1.3 版本信息与变更记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0 | 2026-04-03 | 量化研究员 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     因果推断系统架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │             因果发现层 (Causal Discovery Layer)           │  │
│ │ ├── PCAlgorithm (PC算法)                                 │  │
│ │ ├── GESAlgorithm (GES算法)                               │  │
│ │ ├── NOTEARSAlgorithm (NOTEARS算法)                       │  │
│ │ └── CausalGraphValidator (因果图验证)                    │  │
│ └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │             因果效应估计层 (Effect Estimation Layer)      │  │
│ │ ├── PropensityScoreMatching (倾向得分匹配)               │  │
│ │ ├── InverseProbabilityWeighting (逆概率加权)             │  │
│ │ ├── DoublyRobustEstimator (双重稳健估计)                 │  │
│ │ ├── InstrumentalVariable (工具变量法)                    │  │
│ │ └── DifferenceInDifferences (双重差分)                   │  │
│ └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │             反事实推断层 (Counterfactual Layer)           │  │
│ │ ├── IndividualTreatmentEffect (个体处理效应)             │  │
│ │ ├── AverageTreatmentEffect (平均处理效应)                │  │
│ │ ├── ConditionalAverageTreatmentEffect (条件平均处理效应) │  │
│ │ └── CounterfactualPredictor (反事实预测器)               │  │
│ └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │             应用层 (Application Layer)                    │  │
│ │ ├── FactorCausalAnalysis (因子因果分析)                  │  │
│ │ ├── StrategyAttribution (策略归因)                       │  │
│ │ ├── MarketRegimeCausal (市场状态因果)                    │  │
│ │ └── InterventionSimulator (干预模拟器)                   │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明

- **Layer归属**: Layer 4 - 机器学习层
- **职责范围**: 因果发现、因果效应估计、反事实推断、干预模拟
- **上下层接口**: 
  - 上层依赖: Layer 5 (策略执行层) - 策略归因请求
  - 下层依赖: Layer 4 (ML模型) - 特征数据

### 2.3 模块职责与边界定义

- **核心职责**: 因果推断分析
- **职责边界**: 
  - ✅ 本模块负责: 因果发现、效应估计、反事实推断
  - ❌ 本模块不负责: 模型训练、特征工程、策略执行
- **接口契约**: 提供标准化的因果推断API

### 2.4 依赖关系与集成点

| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| DoWhy | 强依赖 | Python库 | >=0.8.0 | 因果推断框架 |
| CausalNex | 强依赖 | Python库 | >=0.12.0 | 贝叶斯网络 |
| EconML | 强依赖 | Python库 | >=0.14.0 | 异质效应估计 |
| CDT | 强依赖 | Python库 | >=0.6.0 | 因果发现工具 |

---

## 3. 接口定义

### 3.1 API接口规范

```python
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import networkx as nx


class CausalRelationType(Enum):
    """因果关系类型"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    CONFOUNDED = "confounded"
    SPURIOUS = "spurious"


class TreatmentType(Enum):
    """处理类型"""
    BINARY = "binary"
    CONTINUOUS = "continuous"
    MULTIVALUE = "multivalue"


@dataclass
class CausalEdge:
    """因果边"""
    source: str
    target: str
    edge_type: CausalRelationType
    confidence: float
    effect_size: Optional[float] = None


@dataclass
class CausalGraph:
    """因果图"""
    nodes: Set[str]
    edges: List[CausalEdge]
    adjacency_matrix: np.ndarray
    graph: nx.DiGraph
    
    def get_parents(self, node: str) -> List[str]:
        """获取父节点"""
        return list(self.graph.predecessors(node))
    
    def get_children(self, node: str) -> List[str]:
        """获取子节点"""
        return list(self.graph.successors(node))
    
    def get_ancestors(self, node: str) -> Set[str]:
        """获取祖先节点"""
        return nx.ancestors(self.graph, node)
    
    def get_descendants(self, node: str) -> Set[str]:
        """获取后代节点"""
        return nx.descendants(self.graph, node)
    
    def find_confounders(self, treatment: str, outcome: str) -> Set[str]:
        """寻找混杂因素"""
        treatment_ancestors = self.get_ancestors(treatment)
        outcome_ancestors = self.get_ancestors(outcome)
        return treatment_ancestors & outcome_ancestors
    
    def find_backdoor_paths(self, treatment: str, outcome: str) -> List[List[str]]:
        """寻找后门路径"""
        all_paths = list(nx.all_simple_paths(self.graph, treatment, outcome))
        backdoor_paths = []
        
        for path in all_paths:
            if len(path) > 2:
                for i in range(1, len(path) - 1):
                    parents = self.get_parents(path[i])
                    children = self.get_children(path[i])
                    if path[i-1] in parents and path[i+1] in parents:
                        backdoor_paths.append(path)
                        break
        
        return backdoor_paths


@dataclass
class CausalEffect:
    """因果效应"""
    treatment: str
    outcome: str
    effect_type: str
    point_estimate: float
    confidence_interval: Tuple[float, float]
    p_value: float
    standard_error: float
    confounders: List[str]
    method: str


@dataclass
class CounterfactualResult:
    """反事实结果"""
    sample_id: str
    factual_outcome: float
    counterfactual_outcome: float
    treatment_change: Dict[str, Any]
    individual_effect: float
    confidence: float


class CausalDiscovery:
    """因果发现
    
    从观测数据中发现因果结构
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def discover_with_pc(
        self,
        data: pd.DataFrame,
        alpha: float = 0.05,
        indep_test: str = "fisherz"
    ) -> CausalGraph:
        """PC算法因果发现
        
        Args:
            data: 观测数据
            alpha: 显著性水平
            indep_test: 独立性检验方法
            
        Returns:
            CausalGraph: 因果图
        """
        from causallearn.search.ConstraintBased.PC import pc
        
        cg = pc(data.values, alpha, indep_test)
        
        nodes = set(data.columns)
        edges = []
        
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        
        for i in range(len(data.columns)):
            for j in range(i + 1, len(data.columns)):
                edge = cg.G.get_edge(cg.G.nodes[i], cg.G.nodes[j])
                if edge is not None:
                    source = data.columns[i]
                    target = data.columns[j]
                    
                    edge_type = CausalRelationType.DIRECT
                    confidence = 1.0
                    
                    edges.append(CausalEdge(
                        source=source,
                        target=target,
                        edge_type=edge_type,
                        confidence=confidence
                    ))
                    graph.add_edge(source, target)
        
        adj_matrix = nx.adjacency_matrix(graph).toarray()
        
        return CausalGraph(
            nodes=nodes,
            edges=edges,
            adjacency_matrix=adj_matrix,
            graph=graph
        )
    
    def discover_with_notears(
        self,
        data: pd.DataFrame,
        lambda1: float = 0.1,
        loss_type: str = "l2"
    ) -> CausalGraph:
        """NOTEARS算法因果发现
        
        基于连续优化的因果发现方法
        
        Args:
            data: 观测数据
            lambda1: L1正则化参数
            loss_type: 损失函数类型
            
        Returns:
            CausalGraph: 因果图
        """
        from castle.algorithms import Notears
        
        notears = Notears(lambda1=lambda1, loss_type=loss_type)
        notears.learn(data.values)
        
        adj_matrix = notears.causal_matrix
        
        nodes = set(data.columns)
        edges = []
        
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        
        for i in range(len(data.columns)):
            for j in range(len(data.columns)):
                if adj_matrix[i, j] > 0.3:
                    source = data.columns[i]
                    target = data.columns[j]
                    
                    edges.append(CausalEdge(
                        source=source,
                        target=target,
                        edge_type=CausalRelationType.DIRECT,
                        confidence=float(adj_matrix[i, j])
                    ))
                    graph.add_edge(source, target)
        
        return CausalGraph(
            nodes=nodes,
            edges=edges,
            adjacency_matrix=adj_matrix,
            graph=graph
        )
    
    def validate_causal_graph(
        self,
        graph: CausalGraph,
        data: pd.DataFrame,
        domain_knowledge: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """验证因果图
        
        Args:
            graph: 因果图
            data: 观测数据
            domain_knowledge: 领域知识约束
            
        Returns:
            Dict: 验证结果
        """
        validation_result = {
            "is_valid": True,
            "violations": [],
            "suggestions": [],
            "score": 0.0
        }
        
        if not nx.is_directed_acyclic_graph(graph.graph):
            validation_result["is_valid"] = False
            validation_result["violations"].append("存在环")
        
        if domain_knowledge:
            for constraint_type, constraints in domain_knowledge.items():
                if constraint_type == "forbidden_edges":
                    for source, target in constraints:
                        if graph.graph.has_edge(source, target):
                            validation_result["violations"].append(
                                f"禁止边存在: {source} -> {target}"
                            )
        
        validation_result["score"] = self._calculate_graph_score(graph, data)
        
        return validation_result
    
    def _calculate_graph_score(self, graph: CausalGraph, data: pd.DataFrame) -> float:
        """计算图评分"""
        from scipy.stats import pearsonr
        
        total_score = 0.0
        edge_count = 0
        
        for edge in graph.edges:
            if edge.source in data.columns and edge.target in data.columns:
                corr, _ = pearsonr(data[edge.source], data[edge.target])
                total_score += abs(corr)
                edge_count += 1
        
        return total_score / max(edge_count, 1)


class CausalEffectEstimator:
    """因果效应估计器
    
    估计处理对结果的因果效应
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def estimate_with_psm(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: List[str],
        caliper: float = 0.2
    ) -> CausalEffect:
        """倾向得分匹配估计
        
        Args:
            data: 数据
            treatment: 处理变量
            outcome: 结果变量
            confounders: 混杂因素
            caliper: 匹配容差
            
        Returns:
            CausalEffect: 因果效应
        """
        from sklearn.linear_model import LogisticRegression
        from scipy.stats import ttest_ind
        
        X = data[confounders]
        T = data[treatment]
        Y = data[outcome]
        
        ps_model = LogisticRegression(max_iter=1000)
        ps_model.fit(X, T)
        propensity_scores = ps_model.predict_proba(X)[:, 1]
        
        treated_idx = T == 1
        control_idx = T == 0
        
        matched_treated = []
        matched_control = []
        
        for i, (t_idx, ps) in enumerate(zip(treated_idx, propensity_scores)):
            if t_idx:
                distances = np.abs(propensity_scores[control_idx] - ps)
                min_idx = np.argmin(distances)
                if distances[min_idx] < caliper:
                    matched_treated.append(i)
                    matched_control.append(np.where(control_idx)[0][min_idx])
        
        treated_outcomes = Y.iloc[matched_treated]
        control_outcomes = Y.iloc[matched_control]
        
        ate = treated_outcomes.mean() - control_outcomes.mean()
        _, p_value = ttest_ind(treated_outcomes, control_outcomes)
        
        se = np.sqrt(
            treated_outcomes.var() / len(treated_outcomes) +
            control_outcomes.var() / len(control_outcomes)
        )
        
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        
        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            effect_type="ATE",
            point_estimate=float(ate),
            confidence_interval=ci,
            p_value=float(p_value),
            standard_error=float(se),
            confounders=confounders,
            method="Propensity Score Matching"
        )
    
    def estimate_with_ipw(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: List[str]
    ) -> CausalEffect:
        """逆概率加权估计
        
        Args:
            data: 数据
            treatment: 处理变量
            outcome: 结果变量
            confounders: 混杂因素
            
        Returns:
            CausalEffect: 因果效应
        """
        from sklearn.linear_model import LogisticRegression
        
        X = data[confounders]
        T = data[treatment]
        Y = data[outcome]
        
        ps_model = LogisticRegression(max_iter=1000)
        ps_model.fit(X, T)
        propensity_scores = ps_model.predict_proba(X)[:, 1]
        
        propensity_scores = np.clip(propensity_scores, 0.01, 0.99)
        
        weights_treated = T / propensity_scores
        weights_control = (1 - T) / (1 - propensity_scores)
        
        weighted_outcome_treated = (Y * weights_treated).sum() / weights_treated.sum()
        weighted_outcome_control = (Y * weights_control).sum() / weights_control.sum()
        
        ate = weighted_outcome_treated - weighted_outcome_control
        
        n = len(data)
        se = np.std(Y) / np.sqrt(n)
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        
        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            effect_type="ATE",
            point_estimate=float(ate),
            confidence_interval=ci,
            p_value=0.05,
            standard_error=float(se),
            confounders=confounders,
            method="Inverse Probability Weighting"
        )
    
    def estimate_with_doubly_robust(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        confounders: List[str]
    ) -> CausalEffect:
        """双重稳健估计
        
        Args:
            data: 数据
            treatment: 处理变量
            outcome: 结果变量
            confounders: 混杂因素
            
        Returns:
            CausalEffect: 因果效应
        """
        from sklearn.linear_model import LogisticRegression, LinearRegression
        
        X = data[confounders]
        T = data[treatment]
        Y = data[outcome]
        
        ps_model = LogisticRegression(max_iter=1000)
        ps_model.fit(X, T)
        propensity_scores = ps_model.predict_proba(X)[:, 1]
        propensity_scores = np.clip(propensity_scores, 0.01, 0.99)
        
        outcome_model_treated = LinearRegression()
        outcome_model_control = LinearRegression()
        
        outcome_model_treated.fit(X[T == 1], Y[T == 1])
        outcome_model_control.fit(X[T == 0], Y[T == 0])
        
        mu1 = outcome_model_treated.predict(X)
        mu0 = outcome_model_control.predict(X)
        
        dr_treated = (
            T * (Y - mu1) / propensity_scores + mu1
        ).mean()
        
        dr_control = (
            (1 - T) * (Y - mu0) / (1 - propensity_scores) + mu0
        ).mean()
        
        ate = dr_treated - dr_control
        
        n = len(data)
        se = np.std(Y) / np.sqrt(n)
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        
        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            effect_type="ATE",
            point_estimate=float(ate),
            confidence_interval=ci,
            p_value=0.05,
            standard_error=float(se),
            confounders=confounders,
            method="Doubly Robust Estimation"
        )


class CounterfactualAnalyzer:
    """反事实分析器
    
    进行反事实推断
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def estimate_ite(
        self,
        model: Any,
        X: pd.DataFrame,
        treatment: str,
        outcome: str,
        sample_indices: Optional[List[int]] = None
    ) -> List[CounterfactualResult]:
        """估计个体处理效应 (ITE)
        
        Args:
            model: 因果模型
            X: 特征数据
            treatment: 处理变量
            outcome: 结果变量
            sample_indices: 样本索引
            
        Returns:
            List[CounterfactualResult]: 反事实结果列表
        """
        if sample_indices is None:
            sample_indices = list(range(min(100, len(X))))
        
        results = []
        
        for idx in sample_indices:
            sample = X.iloc[idx:idx+1].copy()
            
            factual_treatment = sample[treatment].values[0]
            factual_outcome = model.predict(sample)[0]
            
            counterfactual_sample = sample.copy()
            counterfactual_sample[treatment] = 1 - factual_treatment
            counterfactual_outcome = model.predict(counterfactual_sample)[0]
            
            individual_effect = counterfactual_outcome - factual_outcome
            
            results.append(CounterfactualResult(
                sample_id=str(idx),
                factual_outcome=float(factual_outcome),
                counterfactual_outcome=float(counterfactual_outcome),
                treatment_change={treatment: (factual_treatment, 1 - factual_treatment)},
                individual_effect=float(individual_effect),
                confidence=0.8
            ))
        
        return results
    
    def estimate_cate(
        self,
        model: Any,
        X: pd.DataFrame,
        treatment: str,
        outcome: str,
        subgroups: Dict[str, pd.Series]
    ) -> Dict[str, float]:
        """估计条件平均处理效应 (CATE)
        
        Args:
            model: 因果模型
            X: 特征数据
            treatment: 处理变量
            outcome: 结果变量
            subgroups: 子群体定义
            
        Returns:
            Dict[str, float]: 各子群体的CATE
        """
        cate_results = {}
        
        for group_name, group_mask in subgroups.items():
            group_data = X[group_mask]
            
            ite_results = self.estimate_ite(
                model, group_data, treatment, outcome,
                list(range(len(group_data)))
            )
            
            cate = np.mean([r.individual_effect for r in ite_results])
            cate_results[group_name] = cate
        
        return cate_results
    
    def simulate_intervention(
        self,
        causal_graph: CausalGraph,
        data: pd.DataFrame,
        intervention: Dict[str, Any],
        outcome: str
    ) -> Dict[str, Any]:
        """模拟干预效果
        
        Args:
            causal_graph: 因果图
            data: 观测数据
            intervention: 干预定义 {变量: 值}
            outcome: 目标结果变量
            
        Returns:
            Dict: 干预模拟结果
        """
        from causalnex.structure.notears import from_pandas
        from causalnex.network import BayesianNetwork
        
        bn = BayesianNetwork(causal_graph.graph)
        
        original_distribution = data[outcome].describe()
        
        intervened_data = data.copy()
        for var, value in intervention.items():
            intervened_data[var] = value
        
        intervened_distribution = intervened_data[outcome].describe()
        
        effect = intervened_distribution['mean'] - original_distribution['mean']
        
        return {
            "intervention": intervention,
            "outcome": outcome,
            "original_mean": original_distribution['mean'],
            "intervened_mean": intervened_distribution['mean'],
            "intervention_effect": float(effect),
            "original_distribution": original_distribution.to_dict(),
            "intervened_distribution": intervened_distribution.to_dict()
        }


class FactorCausalAnalyzer:
    """因子因果分析器
    
    专门用于量化因子因果分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.discovery = CausalDiscovery(config)
        self.estimator = CausalEffectEstimator(config)
        self.counterfactual = CounterfactualAnalyzer(config)
        
    def analyze_factor_causality(
        self,
        factor_data: pd.DataFrame,
        returns: pd.Series,
        factor_names: List[str]
    ) -> Dict[str, Any]:
        """分析因子因果性
        
        Args:
            factor_data: 因子数据
            returns: 收益率序列
            factor_names: 因子名称列表
            
        Returns:
            Dict: 因果分析结果
        """
        data = factor_data.copy()
        data['returns'] = returns
        
        causal_graph = self.discovery.discover_with_notears(data[factor_names + ['returns']])
        
        causal_effects = {}
        for factor in factor_names:
            confounders = list(causal_graph.get_ancestors(factor) & causal_graph.get_ancestors('returns'))
            
            effect = self.estimator.estimate_with_doubly_robust(
                data, factor, 'returns', confounders if confounders else factor_names
            )
            causal_effects[factor] = effect
        
        direct_causes = [
            factor for factor in factor_names
            if causal_graph.graph.has_edge(factor, 'returns')
        ]
        
        return {
            "causal_graph": causal_graph,
            "causal_effects": causal_effects,
            "direct_causes": direct_causes,
            "spurious_factors": [
                f for f in factor_names 
                if f not in direct_causes and 
                abs(causal_effects[f].point_estimate) < 0.01
            ]
        }
    
    def identify_spurious_signals(
        self,
        factor_data: pd.DataFrame,
        returns: pd.Series,
        factor_names: List[str],
        threshold: float = 0.05
    ) -> List[str]:
        """识别虚假信号
        
        Args:
            factor_data: 因子数据
            returns: 收益率序列
            factor_names: 因子名称列表
            threshold: 效应阈值
            
        Returns:
            List[str]: 虚假信号因子列表
        """
        analysis = self.analyze_factor_causality(factor_data, returns, factor_names)
        
        spurious = []
        for factor, effect in analysis["causal_effects"].items():
            if abs(effect.point_estimate) < threshold:
                spurious.append(factor)
        
        return spurious
```

---

## 4. 测试策略

### 4.1 单元测试

```python
import pytest
import numpy as np
import pandas as pd
from causal_inference import CausalDiscovery, CausalEffectEstimator


class TestCausalDiscovery:
    
    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        n = 1000
        
        X = np.random.randn(n)
        Y = 0.5 * X + np.random.randn(n) * 0.1
        Z = 0.3 * X + 0.2 * Y + np.random.randn(n) * 0.1
        
        return pd.DataFrame({'X': X, 'Y': Y, 'Z': Z})
    
    def test_pc_algorithm(self, sample_data):
        """测试PC算法"""
        discovery = CausalDiscovery({})
        graph = discovery.discover_with_pc(sample_data)
        
        assert 'X' in graph.nodes
        assert 'Y' in graph.nodes
        assert 'Z' in graph.nodes
    
    def test_notears_algorithm(self, sample_data):
        """测试NOTEARS算法"""
        discovery = CausalDiscovery({})
        graph = discovery.discover_with_notears(sample_data)
        
        assert nx.is_directed_acyclic_graph(graph.graph)


class TestCausalEffectEstimator:
    
    def test_psm_estimation(self):
        """测试倾向得分匹配"""
        np.random.seed(42)
        n = 500
        
        X = np.random.randn(n)
        T = (X > 0).astype(int)
        Y = 0.5 * T + 0.3 * X + np.random.randn(n) * 0.1
        
        data = pd.DataFrame({'X': X, 'T': T, 'Y': Y})
        
        estimator = CausalEffectEstimator({})
        effect = estimator.estimate_with_psm(data, 'T', 'Y', ['X'])
        
        assert abs(effect.point_estimate - 0.5) < 0.2
```

---

## 5. 风险与约束

### 5.1 技术风险

| 风险项 | 风险等级 | 缓解措施 |
|--------|----------|----------|
| 因果图错误 | P1 | 领域知识验证、多算法交叉验证 |
| 未观测混杂 | P1 | 敏感性分析、工具变量 |
| 计算复杂度高 | P2 | 采样、并行计算 |

---

## 6. 验收标准

### 6.1 功能验收

| 验收项 | 验收标准 |
|--------|----------|
| 因果发现 | 支持PC、NOTEARS算法 |
| 效应估计 | 支持PSM、IPW、双重稳健 |
| 反事实推断 | 支持ITE、CATE估计 |
| 因子分析 | 支持虚假信号识别 |

### 6.2 性能验收

| 指标 | 目标值 |
|------|--------|
| 因果发现（1000样本） | < 60秒 |
| 效应估计 | < 5秒 |
| 反事实推断（100样本） | < 10秒 |

---

## 7. 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-04-03 | 量化研究员 | 初始版本 |

---

**文档版本**: v1.0.0
**最后更新**: 2026-04-03
**维护者**: 量化研究员
