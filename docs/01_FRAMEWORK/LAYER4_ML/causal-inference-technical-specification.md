---
module_id: CAUSAL_INFERENCE_TECHNICAL_SPECIFICATION
version: 1.0.0
status: Active
priority: P2
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - CAUSAL_INFERENCE_TECHNICAL技术规范
layer: layer_01
spec_version: 1.0
index: CI-001
estimated_hours: 80
review_status: Pending
reviewer: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
applicable_scope: ﮒﮔﮔ۷ﮔﻝﺏﭨﻝﭨ
compliance_level: ﻠ۰ﭘﻝﭦ۶ﻛﺕﻛﺕﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﮔﮔﺁﻟ۶ﮔﺙﻟ؟ﺝﻟ؟۰ﮒ؟ﮔ?
---
```
```---
```







# ﮒﮔﮔ۷ﮔﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ v1.0



> **核心职责**: 定义causal inference technical specification的技术规格、接口标准和实现细节



> **职责边界**:



> - ✅ 本文档负责：文档内容说明相关内容



> - ❌ 本文档不负责：其他模块内容











> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - ﮒﮔﮔ۷ﮔﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝﻟ؟?> **ﻝﺑ۱ﮒﺙ**: `CI-001`



> **ﮒﺙﮒﮔﭘﻠ?*: 80h



> **ﮔﺕﮒﺟﮒ؟ﻛﺛ**: ﮒﭦﮒﮒﮔﻛﺕﻝﺕﮒﺏﻙﮒﮔﮒﻝﺍﻙﮒﮔﮔﮒﭦﻛﺙﺍﻟ؟۰ﻙﮒﻛﭦﮒ؟ﮒﮔ



```
```---
```



## 1. ﮔ۵ﻟﺟﺍ







### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟ﻝ?



**ﻛﺕﮒ۰ﻠﮔﺎ?*:



- ﮒﭦﮒﮒﮔﮔ۶ﻛﺕﻝﺕﮒﺏﮔ۶ﮔﺁﻠﮒﮔﺕﮒﺟﻟﺛﮒ



- ﻠﺟﮒﻟﮒﻛﺟ۰ﮒﺓﮒﻟﺟﮔﮒ



- ﮔﮒﻝﻝ۴ﻝ۷ﺏﮒ۴ﮔ۶ﮒﮒﺁﻟ۶۲ﻠﮔ?- ﮔﺁﮔﻝﻝ۴ﮒﺛﮒﮒﮔ







**ﮔﮔﺁﻝﻝ?*:



- ﻛﺙﻝﭨMLﮒ۹ﮒ۵ﻛﺗﻝﺕﮒﺏﮔ۶ﺅﺙﮔﮔﺏﻟﺁﮒ،ﮒﮔ



- ﮒﮔﮒﺝﮔﮒﭨﭦﻛﺝﻟﭖﻛﺕﮒ؟ﭘﻝ۴ﻟﺁ?- ﮔﺓﺓﮔﮒﻝﺑﮒ۳ﻝﮒﺍﻠﺝ



- ﮒﻛﭦﮒ؟ﮔ۷ﮔﻟ؟۰ﻝ؟ﮒ۳ﮔ?



**ﻠ۱ﮔﻛﭨﺓﮒ?*:



- ﻝﻝ۴ﻝ۷ﺏﮒ۴ﮔ۶ﮔﮒ?0%



- ﻟﮒﻛﺟ۰ﮒﺓﻟﺁﮒ،ﻝﮔﮒ?0%



- ﻝﻝ۴ﮒﺛﮒﮒﻝ۰؟ﮔ۶ﮔﮒ?0%



- ﻟﺟﮔﮒﻠ۲ﻠ۸ﻠﻛﺛ?0%







### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛﮒﺎ?



- **Layerﮒ؟ﻛﺛ**: Layer 4 - ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎﺅﺙAIﮔ۷۰ﮒﮔﮒ۰ﺅﺙ?- **ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔﺕﮒﺟﮔﺁﮔﮔ۷۰ﮒ



- **ﮔﭘﮔﻟ۶ﻟﺎ**: ﮔﻛﺝﮒﮔﮒﻝﺍﻙﮒﮔﮔﮒﭦﻛﺙﺍﻟ؟۰ﻙﮒﻛﭦﮒ؟ﮒﮔ







### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁﻛﺕﮒﮔﺑﻟ؟ﺍﮒﺛ?



| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛﻟ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝﭘﮔ?|



|------|------|------|----------|------|



| v1.0 | 2026-04-03 | ﻠﮒﻝﻝ۸ﭘﮒ?| ﮒﮒ۶ﻝﮔ؛ | Active |







```
```---
```







## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰







### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔﮒ?



```







### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ







- **Layerﮒﺛﮒﺎ**: Layer 4 - ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎ?- **ﻟﻟﺑ۲ﻟﮒﺑ**: ﮒﮔﮒﻝﺍﻙﮒﮔﮔﮒﭦﻛﺙﺍﻟ؟۰ﻙﮒﻛﭦﮒ؟ﮔ۷ﮔﻙﮒﺗﺎﻠ۱ﮔ۷۰ﮔ?- **ﻛﺕﻛﺕﮒﺎﮔ۴ﮒ?*:



- ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 5 (ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎ? - ﻝﻝ۴ﮒﺛﮒﻟﺁﺓﮔﺎ



  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 4 (MLﮔ۷۰ﮒ) - ﻝﺗﮒﺝﮔﺍﮔ؟







### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟ﻛﺗ?



- **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﮒﮔﮔ۷ﮔﮒﮔ



- **ﻟﻟﺑ۲ﻟﺝﺗﻝ**:



- ﻗ?ﮔ؛ﮔ۷۰ﮒﻟﺑﻟﺑ? ﮒﮔﮒﻝﺍﻙﮔﮒﭦﻛﺙﺍﻟ؟۰ﻙﮒﻛﭦﮒ؟ﮔ۷ﮔ



- ﻗ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲: ﮔ۷۰ﮒﻟ؟ﻝﭨﻙﻝﺗﮒﺝﮒﺓ۴ﻝ۷ﻙﻝﻝ۴ﮔ۶ﻟ۰?- **ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﮔﮒﮒﻝﮒﮔﮔ۷ﮔAPI







### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨﻛﺕﻠﮔﻝﺗ







| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |



|----------|----------|----------|----------|------|



| DoWhy | ﮒﺙﭦﻛﺝﻟﭖ?| Pythonﮒﭦ?| >=0.8.0 | ﮒﮔﮔ۷ﮔﮔ۰ﮔﭘ |



| CausalNex | ﮒﺙﭦﻛﺝﻟﭖ?| Pythonﮒﭦ?| >=0.12.0 | ﻟﺑﮒﭘﮔﺁﻝﺛﻝﭨ?|



| EconML | ﮒﺙﭦﻛﺝﻟﭖ?| Pythonﮒﭦ?| >=0.14.0 | ﮒﺙﻟﺑ۷ﮔﮒﭦﻛﺙﺍﻟ؟۰ |



| CDT | ﮒﺙﭦﻛﺝﻟﭖ?| Pythonﮒﭦ?| >=0.6.0 | ﮒﮔﮒﻝﺍﮒﺓ۴ﮒﺓ |







```---







## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ







### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ







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



"""ﮒﮔﮒﺏﻝﺏﭨﻝﺎﭨﮒ"""



    DIRECT = "direct"



    INDIRECT = "indirect"



    CONFOUNDED = "confounded"



    SPURIOUS = "spurious"











class TreatmentType(Enum):



    """ﮒ۳ﻝﻝﺎﭨﮒ"""



    BINARY = "binary"



    CONTINUOUS = "continuous"



    MULTIVALUE = "multivalue"











@dataclass



class CausalEdge:



"""ﮒﮔﻟﺝ?""



    source: str



    target: str



    edge_type: CausalRelationType



    confidence: float



    effect_size: Optional[float] = None











@dataclass



class CausalGraph:



"""ﮒﮔﮒ?""



    nodes: Set[str]



    edges: List[CausalEdge]



    adjacency_matrix: np.ndarray



    graph: nx.DiGraph







    def get_parents(self, node: str) -> List[str]:



        """ﻟﺓﮒﻝﭘﻟﻝ?""



        return list(self.graph.predecessors(node))







    def get_children(self, node: str) -> List[str]:



"""ﻟﺓﮒﮒﻟﻝ?""



        return list(self.graph.successors(node))







    def get_ancestors(self, node: str) -> Set[str]:



        """ﻟﺓﮒﻝ۴ﮒﻟﻝﺗ"""



        return nx.ancestors(self.graph, node)







    def get_descendants(self, node: str) -> Set[str]:



        """ﻟﺓﮒﮒﻛﭨ۲ﻟﻝﺗ"""



        return nx.descendants(self.graph, node)







    def find_confounders(self, treatment: str, outcome: str) -> Set[str]:



"""ﮒﺁﭨﮔﺝﮔﺓﺓﮔﮒﻝﺑ"""



        treatment_ancestors = self.get_ancestors(treatment)



        outcome_ancestors = self.get_ancestors(outcome)



        return treatment_ancestors & outcome_ancestors







    def find_backdoor_paths(self, treatment: str, outcome: str) -> List[List[str]]:



        """ﮒﺁﭨﮔﺝﮒﻠ۷ﻟﺓﺁﮒﺝ"""



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



"""ﮒﮔﮔﮒﭦ"""



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



    """ﮒﻛﭦﮒ؟ﻝﭨﮔ?""



    sample_id: str



    factual_outcome: float



    counterfactual_outcome: float



    treatment_change: Dict[str, Any]



    individual_effect: float



    confidence: float











class CausalDiscovery:



"""ﮒﮔﮒﻝﺍ







ﻛﭨﻟ۶ﮔﭖﮔﺍﮔ؟ﻛﺕﮒﻝﺍﮒﮔﻝﭨﮔ



    """







    def __init__(self, config: Dict[str, Any]):



        self.config = config







    def discover_with_pc(



        self,



        data: pd.DataFrame,



        alpha: float = 0.05,



        indep_test: str = "fisherz"



    ) -> CausalGraph:



"""PCﻝ؟ﮔﺏﮒﮔﮒﻝﺍ







        Args:



            data: ﻟ۶ﮔﭖﮔﺍﮔ؟



            alpha: ﮔﺝﻟﮔ۶ﮔﺍﺑﮒﺗ?            indep_test: ﻝ؛ﻝ،ﮔ۶ﮔ۲ﻠ۹ﮔﺗﮔﺏ?



        Returns:



CausalGraph: ﮒﮔﮒ?        """



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



"""NOTEARSﻝ؟ﮔﺏﮒﮔﮒﻝﺍ







ﮒﭦﻛﭦﻟﺟﻝﭨﻛﺙﮒﻝﮒﮔﮒﻝﺍﮔﺗﮔﺏ?



        Args:



            data: ﻟ۶ﮔﭖﮔﺍﮔ؟



lambda1: L1ﮔ۲ﮒﮒﮒﮔ?            loss_type: ﮔﮒ۳ﺎﮒﺛﮔﺍﻝﺎﭨﮒ







        Returns:



CausalGraph: ﮒﮔﮒ?        """



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



"""ﻠ۹ﻟﺁﮒﮔﮒ?



        Args:



graph: ﮒﮔﮒ?            data: ﻟ۶ﮔﭖﮔﺍﮔ؟



            domain_knowledge: ﻠ۱ﮒﻝ۴ﻟﺁﻝﭦ۵ﮔ







        Returns:



            Dict: ﻠ۹ﻟﺁﻝﭨﮔ



        """



        validation_result = {



            "is_valid": True,



            "violations": [],



            "suggestions": [],



            "score": 0.0



        }







        if not nx.is_directed_acyclic_graph(graph.graph):



            validation_result["is_valid"] = False



validation_result["violations"].append("ﮒﮒ۷ﻝ?)







        if domain_knowledge:



            for constraint_type, constraints in domain_knowledge.items():



                if constraint_type == "forbidden_edges":



                    for source, target in constraints:



                        if graph.graph.has_edge(source, target):



                            validation_result["violations"].append(



f"ﻝ۵ﮔ۱ﻟﺝﺗﮒﮒ? {source} -> {target}"



                            )







        validation_result["score"] = self._calculate_graph_score(graph, data)







        return validation_result







    def _calculate_graph_score(self, graph: CausalGraph, data: pd.DataFrame) -> float:



        """ﻟ؟۰ﻝ؟ﮒﺝﻟﺁﮒ?""



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



"""ﮒﮔﮔﮒﭦﻛﺙﺍﻟ؟۰ﮒ?



ﻛﺙﺍﻟ؟۰ﮒ۳ﻝﮒﺁﺗﻝﭨﮔﻝﮒﮔﮔﮒﭦ



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



        """ﮒﺝﮒﮒﺝﮒﮒﺗﻠﻛﺙﺍﻟ؟۰







        Args:



            data: ﮔﺍﮔ؟



            treatment: ﮒ۳ﻝﮒﻠ



            outcome: ﻝﭨﮔﮒﻠ



confounders: ﮔﺓﺓﮔﮒﻝﺑ



            caliper: ﮒﺗﻠﮒ؟ﺗﮒﺓ؟







        Returns:



CausalEffect: ﮒﮔﮔﮒﭦ



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



"""ﻠﮔ۵ﻝﮒﮔﻛﺙﺍﻟ؟?



        Args:



            data: ﮔﺍﮔ؟



            treatment: ﮒ۳ﻝﮒﻠ



            outcome: ﻝﭨﮔﮒﻠ



confounders: ﮔﺓﺓﮔﮒﻝﺑ







        Returns:



CausalEffect: ﮒﮔﮔﮒﭦ



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



        """ﮒﻠﻝ۷ﺏﮒ۴ﻛﺙﺍﻟ؟۰







        Args:



            data: ﮔﺍﮔ؟



            treatment: ﮒ۳ﻝﮒﻠ



            outcome: ﻝﭨﮔﮒﻠ



confounders: ﮔﺓﺓﮔﮒﻝﺑ







        Returns:



CausalEffect: ﮒﮔﮔﮒﭦ



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



    """ﮒﻛﭦﮒ؟ﮒﮔﮒ۷







    ﻟﺟﻟ۰ﮒﻛﭦﮒ؟ﮔ۷ﮔ?    """







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



        """ﻛﺙﺍﻟ؟۰ﻛﺕ۹ﻛﺛﮒ۳ﻝﮔﮒﭦ (ITE)







        Args:



model: ﮒﮔﮔ۷۰ﮒ



            X: ﻝﺗﮒﺝﮔﺍﮔ؟



            treatment: ﮒ۳ﻝﮒﻠ



            outcome: ﻝﭨﮔﮒﻠ



sample_indices: ﮔﺓﮔ؛ﻝﺑ۱ﮒﺙ







        Returns:



            List[CounterfactualResult]: ﮒﻛﭦﮒ؟ﻝﭨﮔﮒﻟ۰?        """



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



        """ﻛﺙﺍﻟ؟۰ﮔ۰ﻛﭨﭘﮒﺗﺏﮒﮒ۳ﻝﮔﮒﭦ (CATE)







        Args:



model: ﮒﮔﮔ۷۰ﮒ



            X: ﻝﺗﮒﺝﮔﺍﮔ؟



            treatment: ﮒ۳ﻝﮒﻠ



            outcome: ﻝﭨﮔﮒﻠ



subgroups: ﮒﻝﺝ۳ﻛﺛﮒ؟ﻛﺗ?



        Returns:



Dict[str, float]: ﮒﮒﻝﺝ۳ﻛﺛﻝCATE



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



        """ﮔ۷۰ﮔﮒﺗﺎﻠ۱ﮔﮔ







        Args:



causal_graph: ﮒﮔﮒ?            data: ﻟ۶ﮔﭖﮔﺍﮔ؟



            intervention: ﮒﺗﺎﻠ۱ﮒ؟ﻛﺗ {ﮒﻠ: ﮒﺙ}



outcome: ﻝ؟ﮔﻝﭨﮔﮒﻠ







        Returns:



            Dict: ﮒﺗﺎﻠ۱ﮔ۷۰ﮔﻝﭨﮔ



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



"""ﮒﮒﮒﮔﮒﮔﮒ?



ﻛﺕﻠ۷ﻝ۷ﻛﭦﻠﮒﮒﮒﮒﮔﮒﮔ



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



"""ﮒﮔﮒﮒﮒﮔﮔ?



        Args:



factor_data: ﮒﮒﮔﺍﮔ؟



returns: ﮔﭘﻝﻝﮒﭦﮒ?            factor_names: ﮒﮒﮒﻝ۶ﺍﮒﻟ۰۷







        Returns:



Dict: ﮒﮔﮒﮔﻝﭨﮔ



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



        """ﻟﺁﮒ،ﻟﮒﻛﺟ۰ﮒﺓ







        Args:



factor_data: ﮒﮒﮔﺍﮔ؟



returns: ﮔﭘﻝﻝﮒﭦﮒ?            factor_names: ﮒﮒﮒﻝ۶ﺍﮒﻟ۰۷



            threshold: ﮔﮒﭦﻠﮒ?



        Returns:



List[str]: ﻟﮒﻛﺟ۰ﮒﺓﮒﮒﮒﻟ۰۷



        """



        analysis = self.analyze_factor_causality(factor_data, returns, factor_names)







        spurious = []



        for factor, effect in analysis["causal_effects"].items():



            if abs(effect.point_estimate) < threshold:



                spurious.append(factor)







        return spurious



```







```---







## 4. ﮔﭖﻟﺁﻝﻝ۴







### 4.1 ﮒﮒﮔﭖﻟﺁ







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



        """ﮔﭖﻟﺁPCﻝ؟ﮔﺏ"""



        discovery = CausalDiscovery({})



        graph = discovery.discover_with_pc(sample_data)







        assert 'X' in graph.nodes



        assert 'Y' in graph.nodes



        assert 'Z' in graph.nodes







    def test_notears_algorithm(self, sample_data):



        """ﮔﭖﻟﺁNOTEARSﻝ؟ﮔﺏ"""



        discovery = CausalDiscovery({})



        graph = discovery.discover_with_notears(sample_data)







        assert nx.is_directed_acyclic_graph(graph.graph)











class TestCausalEffectEstimator:







    def test_psm_estimation(self):



        """ﮔﭖﻟﺁﮒﺝﮒﮒﺝﮒﮒﺗﻠ"""



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







```---







## 5. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵ﮔ?



### 5.1 ﮔﮔﺁﻠ۲ﻠ?



| ﻠ۲ﻠ۸ﻠ۰?| ﻠ۲ﻠ۸ﻝﻝﭦ۶ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |



|--------|----------|----------|



| ﮒﮔﮒﺝﻠﻟﺁ?| P1 | ﻠ۱ﮒﻝ۴ﻟﺁﻠ۹ﻟﺁﻙﮒ۳ﻝ؟ﮔﺏﻛﭦ۳ﮒﻠ۹ﻟﺁ |



| ﮔ۹ﻟ۶ﮔﭖﮔﺓﺓﮔ?| P1 | ﮔﮔﮔ۶ﮒﮔﻙﮒﺓ۴ﮒﺓﮒﻠ?|



| ﻟ؟۰ﻝ؟ﮒ۳ﮔﮒﭦ۵ﻠ، | P2 | ﻠﮔﺓﻙﮒﺗﭘﻟ۰ﻟ؟۰ﻝ؟?|







```---







## 6. ﻠ۹ﮔﭘﮔﮒ







### 6.1 ﮒﻟﺛﻠ۹ﮔﭘ







| ﻠ۹ﮔﭘﻠ۰?| ﻠ۹ﮔﭘﮔﮒ |



|--------|----------|



| ﮒﮔﮒﻝﺍ | ﮔﺁﮔPCﻙNOTEARSﻝ؟ﮔﺏ |



| ﮔﮒﭦﻛﺙﺍﻟ؟۰ | ﮔﺁﮔPSMﻙIPWﻙﮒﻠﻝ۷ﺏﮒ?|



| ﮒﻛﭦﮒ؟ﮔ۷ﮔ?| ﮔﺁﮔITEﻙCATEﻛﺙﺍﻟ؟۰ |



| ﮒﮒﮒﮔ | ﮔﺁﮔﻟﮒﻛﺟ۰ﮒﺓﻟﺁﮒ، |







### 6.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘ







| ﮔﮔ | ﻝ؟ﮔﮒ?|



|------|--------|



| ﮒﮔﮒﻝﺍﺅﺙ?000ﮔﺓﮔ؛ﺅﺙ?| < 60ﻝ۶?|



| ﮔﮒﭦﻛﺙﺍﻟ؟۰ | < 5ﻝ۶?|



| ﮒﻛﭦﮒ؟ﮔ۷ﮔﺅﺙ100ﮔﺓﮔ؛ﺅﺙ?| < 10ﻝ۶?|







```---







## 7. ﻝﮔ؛ﮒﮒﺎ







| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛﻟ?| ﮒﮔﺑﻟﺁﺑﮔ |



|------|------|------|----------|



| v1.0 | 2026-04-03 | ﻠﮒﻝﻝ۸ﭘﮒ?| ﮒﮒ۶ﻝﮔ؛ |







```---







**ﮔﮔ۰۲ﻝﮔ؛**: v1.0.0



**ﮔﮒﮔﺑﮔ?*: 2026-04-03



**ﻝﭨﺑﮔ۳ﻟ?*: ﻠﮒﻝﻝ۸ﭘﮒ?



```
