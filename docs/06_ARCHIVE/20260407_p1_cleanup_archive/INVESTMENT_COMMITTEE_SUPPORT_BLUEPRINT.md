---
module_id: INVESTMENT_COMMITTEE_SUPPORT_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - INVESTMENT_COMMITTEE_SUPPORT蓝图设计
---

﻿---
module_id: INVESTMENT_COMMITTEE_SUPPORT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 系统架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11 - 战略决策层
compliance_level: 顶级专业标准
reference_models: ["Bridgewater Investment Committee", "Two Sigma Decision Process", "Citadel Investment Committee"]
parent_document: ./BLUEPRINT.md
implementation_status: 蓝图阶段
responsibility:
  - 投资委员会决策支持系统设计
  - 决策流程管理

---

# 投资委员会决策支持系统蓝图

> **核心职责**: 投资委员会决策支持系统蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：投资委员会决策支持系统蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

> **版本**: v1.0
> **优先级**: 🔴 P0 - 核心战略模块
> **开源方案**: OpenProject, Taiga, 自定义决策流程
> **目标**: 构建专业级投资委员会决策支持系统，适合个人开发、AI维护、个人使用

---

## 📋 执行摘要

### 核心定位

投资委员会决策支持系统是战略决策层的**决策流程管理核心**，负责：
- 决策提案管理与评审
- 决策投票与审批流程
- 决策记录存档与追溯
- 决策知识积累与学习

### 个人使用价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **决策系统化** | 投资委员会决策流程 | AI提案生成 + 人工确认 | ⭐⭐⭐⭐⭐ |
| **决策追溯** | 完整决策记录存档 | Git版本控制 + 数据库 | ⭐⭐⭐⭐⭐ |
| **决策学习** | 决策复盘与改进 | AI决策分析 + 知识库 | ⭐⭐⭐⭐⭐ |
| **决策效率** | 会议决策流程 | 异步决策流程 | ⭐⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**

---

## 一、系统架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│              投资委员会决策支持系统架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │           决策提案管理模块 (Proposal Management)          │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 提案创建引擎                                       │  │  │
│ │ │ ├── AI提案生成（基于市场分析自动生成提案）        │  │  │
│ │ │ ├── 手动提案创建（人工创建决策提案）              │  │  │
│ │ │ ├── 提案模板库（标准化提案模板）                  │  │  │
│ │ │ └── 提案验证（提案完整性和合理性检查）            │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 提案评审引擎                                       │  │  │
│ │ │ ├── 自动评审（AI基于规则自动评审）                │  │  │
│ │ │ ├── 风险评估（提案风险影响评估）                  │  │  │
│ │ │ ├── 合规检查（提案合规性检查）                    │  │  │
│ │ │ └── 评审报告（生成评审报告）                      │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │           决策投票管理模块 (Voting Management)            │  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 投票流程引擎                                       │  │  │
│ │ │ ├── 投票发起（创建投票任务）                      │  │  │
│ │ │ ├── 投票提醒（投票截止提醒）                      │  │  │
│ │ │ ├── 投票统计（投票结果统计）                      │  │  │
│ │ │ └── 投票通知（投票结果通知）                      │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 投票规则引擎                                       │  │  │
│ │ │ ├── 简单多数（>50%同意即通过）                    │  │  │
│ │ │ ├── 绝对多数（>66%同意即通过）                    │  │  │
│ │ │ ├── 一致同意（100%同意即通过）                    │  │  │
│ │ │ └── 加权投票（按权重投票）                        │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │           决策记录管理模块 (Decision Archive)             │  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 决策存档引擎                                       │  │  │
│ │ │ ├── 决策记录存储（数据库存储）                    │  │  │
│ │ │ ├── 决策版本控制（Git版本管理）                   │  │  │
│ │ │ ├── 决策附件管理（支持文档附件）                  │  │  │
│ │ │ └── 决策加密存储（敏感信息加密）                  │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 决策追溯引擎                                       │  │  │
│ │ │ ├── 决策查询（多维度查询）                        │  │  │
│ │ │ ├── 决策历史（决策变更历史）                      │  │  │
│ │ │ ├── 决策影响分析（决策结果影响）                  │  │  │
│ │ │ └── 决策复盘（决策效果复盘）                      │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │           决策知识库模块 (Decision Knowledge Base)        │  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 知识积累引擎                                       │  │  │
│ │ │ ├── 决策经验提取（从历史决策提取经验）            │  │  │
│ │ │ ├── 决策模式识别（识别决策模式）                  │  │  │
│ │ │ ├── 决策教训总结（失败决策教训）                  │  │  │
│ │ │ └── 决策最佳实践（成功决策实践）                  │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 知识检索引擎                                       │  │  │
│ │ │ ├── 相似决策检索（检索相似历史决策）              │  │  │
│ │ │ ├── 决策建议生成（基于知识库生成建议）            │  │  │
│ │ │ ├── 决策风险预警（基于历史风险预警）              │  │  │
│ │ │ └── 决策参考推荐（推荐相关决策参考）              │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心数据模型

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class DecisionType(Enum):
    STRATEGIC_ALLOCATION = "strategic_allocation"      # 战略资产配置
    TACTICAL_ALLOCATION = "tactical_allocation"        # 战术资产配置
    RISK_BUDGET = "risk_budget"                        # 风险预算分配
    STRATEGY_SELECTION = "strategy_selection"          # 策略选择
    STRATEGIC_ADJUSTMENT = "strategic_adjustment"      # 战略调整
    EMERGENCY_DECISION = "emergency_decision"          # 紧急决策

class DecisionStatus(Enum):
    DRAFT = "draft"                  # 草稿
    PENDING_REVIEW = "pending_review" # 待评审
    IN_VOTING = "in_voting"          # 投票中
    APPROVED = "approved"            # 已批准
    REJECTED = "rejected"            # 已拒绝
    EXECUTED = "executed"            # 已执行
    ARCHIVED = "archived"            # 已归档

class VoteResult(Enum):
    AGREE = "agree"                  # 同意
    DISAGREE = "disagree"            # 不同意
    ABSTAIN = "abstain"              # 弃权

@dataclass
class DecisionProposal:
    """决策提案"""
    proposal_id: str                           # 提案ID
    title: str                                 # 提案标题
    description: str                           # 提案描述
    decision_type: DecisionType                # 决策类型
    proposer: str                              # 提案人
    proposal_date: datetime                    # 提案日期
    rationale: str                             # 提案理由
    expected_impact: dict                      # 预期影响
    risk_assessment: dict                      # 风险评估
    attachments: List[str]                     # 附件列表
    status: DecisionStatus                     # 提案状态
    tags: List[str]                            # 标签

@dataclass
class Vote:
    """投票记录"""
    vote_id: str                               # 投票ID
    proposal_id: str                           # 提案ID
    voter: str                                 # 投票人
    vote_result: VoteResult                    # 投票结果
    vote_reason: Optional[str]                 # 投票理由
    vote_time: datetime                        # 投票时间

@dataclass
class DecisionRecord:
    """决策记录"""
    decision_id: str                           # 决策ID
    proposal_id: str                           # 提案ID
    decision_type: DecisionType                # 决策类型
    decision_result: str                       # 决策结果
    decision_date: datetime                    # 决策日期
    execution_date: Optional[datetime]         # 执行日期
    execution_result: Optional[str]            # 执行结果
    impact_analysis: Optional[dict]            # 影响分析
    lessons_learned: Optional[str]             # 经验教训
    related_decisions: List[str]               # 相关决策
```

---

## 二、核心功能设计

### 2.1 决策提案管理

#### 2.1.1 AI提案生成

**功能描述**: 基于市场分析和系统状态，AI自动生成决策提案

**实现方案**:
```python
from langchain import LLMChain, PromptTemplate
from typing import Dict, List

class AIProposalGenerator:
    """AI提案生成器"""
    
    def __init__(self, llm):
        self.llm = llm
        self.proposal_template = PromptTemplate(
            template="""
            基于以下市场分析和系统状态，生成投资决策提案：
            
            市场分析：
            {market_analysis}
            
            系统状态：
            {system_status}
            
            请生成一个包含以下内容的决策提案：
            1. 提案标题
            2. 提案描述
            3. 提案理由
            4. 预期影响
            5. 风险评估
            
            输出格式：
            {output_format}
            """,
            input_variables=["market_analysis", "system_status", "output_format"]
        )
    
    async def generate_proposal(
        self, 
        market_analysis: Dict,
        system_status: Dict
    ) -> DecisionProposal:
        """生成决策提案"""
        # 准备输入数据
        chain = LLMChain(llm=self.llm, prompt=self.proposal_template)
        
        # 生成提案内容
        result = await chain.arun(
            market_analysis=market_analysis,
            system_status=system_status,
            output_format="JSON"
        )
        
        # 解析结果并创建提案对象
        proposal_data = json.loads(result)
        proposal = DecisionProposal(
            proposal_id=self._generate_proposal_id(),
            title=proposal_data['title'],
            description=proposal_data['description'],
            decision_type=DecisionType(proposal_data['type']),
            proposer="AI决策助手",
            proposal_date=datetime.now(),
            rationale=proposal_data['rationale'],
            expected_impact=proposal_data['expected_impact'],
            risk_assessment=proposal_data['risk_assessment'],
            attachments=[],
            status=DecisionStatus.DRAFT,
            tags=proposal_data['tags']
        )
        
        return proposal
    
    def _generate_proposal_id(self) -> str:
        """生成提案ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PROP_{timestamp}"
```

#### 2.1.2 提案评审

**功能描述**: 对提案进行自动评审和风险评估

**实现方案**:
```python
class ProposalReviewer:
    """提案评审器"""
    
    def __init__(self, risk_engine, compliance_checker):
        self.risk_engine = risk_engine
        self.compliance_checker = compliance_checker
    
    async def review_proposal(self, proposal: DecisionProposal) -> Dict:
        """评审提案"""
        review_result = {
            'proposal_id': proposal.proposal_id,
            'review_time': datetime.now(),
            'auto_review': await self._auto_review(proposal),
            'risk_assessment': await self._assess_risk(proposal),
            'compliance_check': await self._check_compliance(proposal),
            'recommendation': None
        }
        
        # 生成评审建议
        review_result['recommendation'] = self._generate_recommendation(review_result)
        
        return review_result
    
    async def _auto_review(self, proposal: DecisionProposal) -> Dict:
        """自动评审"""
        # 检查提案完整性
        completeness = self._check_completeness(proposal)
        
        # 检查提案合理性
        reasonability = self._check_reasonability(proposal)
        
        # 检查提案可行性
        feasibility = self._check_feasibility(proposal)
        
        return {
            'completeness': completeness,
            'reasonability': reasonability,
            'feasibility': feasibility,
            'overall_score': (completeness + reasonability + feasibility) / 3
        }
    
    async def _assess_risk(self, proposal: DecisionProposal) -> Dict:
        """风险评估"""
        return await self.risk_engine.assess_decision_risk(
            proposal.decision_type,
            proposal.expected_impact
        )
    
    async def _check_compliance(self, proposal: DecisionProposal) -> Dict:
        """合规检查"""
        return await self.compliance_checker.check_decision_compliance(
            proposal
        )
    
    def _generate_recommendation(self, review_result: Dict) -> str:
        """生成评审建议"""
        auto_review = review_result['auto_review']
        risk_assessment = review_result['risk_assessment']
        compliance_check = review_result['compliance_check']
        
        if auto_review['overall_score'] < 0.6:
            return "reject"
        elif risk_assessment['risk_level'] == 'high':
            return "review_required"
        elif not compliance_check['compliant']:
            return "compliance_issue"
        else:
            return "approve"
```

### 2.2 决策投票管理

#### 2.2.1 投票流程

**功能描述**: 管理决策投票流程

**实现方案**:
```python
from datetime import timedelta

class VotingManager:
    """投票管理器"""
    
    def __init__(self, db, notification_service):
        self.db = db
        self.notification_service = notification_service
    
    async def create_voting(
        self, 
        proposal: DecisionProposal,
        voting_rule: str = "simple_majority",
        duration_hours: int = 24
    ) -> str:
        """创建投票任务"""
        voting_id = self._generate_voting_id()
        
        voting = {
            'voting_id': voting_id,
            'proposal_id': proposal.proposal_id,
            'voting_rule': voting_rule,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=duration_hours),
            'votes': [],
            'status': 'active'
        }
        
        # 保存投票任务
        await self.db.save_voting(voting)
        
        # 发送投票通知
        await self.notification_service.send_voting_notification(voting)
        
        return voting_id
    
    async def cast_vote(
        self, 
        voting_id: str,
        voter: str,
        vote_result: VoteResult,
        vote_reason: Optional[str] = None
    ) -> bool:
        """投票"""
        # 检查投票是否有效
        voting = await self.db.get_voting(voting_id)
        if not self._is_voting_valid(voting):
            return False
        
        # 记录投票
        vote = Vote(
            vote_id=self._generate_vote_id(),
            proposal_id=voting['proposal_id'],
            voter=voter,
            vote_result=vote_result,
            vote_reason=vote_reason,
            vote_time=datetime.now()
        )
        
        await self.db.save_vote(vote)
        
        # 检查是否可以提前结束投票
        if await self._can_early_close(voting, vote):
            await self._close_voting(voting_id)
        
        return True
    
    async def get_voting_result(self, voting_id: str) -> Dict:
        """获取投票结果"""
        voting = await self.db.get_voting(voting_id)
        votes = voting['votes']
        
        # 统计投票结果
        agree_count = sum(1 for v in votes if v.vote_result == VoteResult.AGREE)
        disagree_count = sum(1 for v in votes if v.vote_result == VoteResult.DISAGREE)
        abstain_count = sum(1 for v in votes if v.vote_result == VoteResult.ABSTAIN)
        total_count = len(votes)
        
        # 根据投票规则判断结果
        passed = self._evaluate_voting_rule(
            voting['voting_rule'],
            agree_count,
            disagree_count,
            abstain_count,
            total_count
        )
        
        return {
            'voting_id': voting_id,
            'total_votes': total_count,
            'agree_count': agree_count,
            'disagree_count': disagree_count,
            'abstain_count': abstain_count,
            'passed': passed,
            'voting_rule': voting['voting_rule']
        }
    
    def _evaluate_voting_rule(
        self,
        rule: str,
        agree: int,
        disagree: int,
        abstain: int,
        total: int
    ) -> bool:
        """评估投票规则"""
        if rule == "simple_majority":
            return agree > (total / 2)
        elif rule == "absolute_majority":
            return agree > (total * 2 / 3)
        elif rule == "unanimous":
            return agree == total
        else:
            return False
```

### 2.3 决策记录管理

#### 2.3.1 决策存档

**功能描述**: 存档决策记录并支持版本控制

**实现方案**:
```python
import git
import json
from pathlib import Path

class DecisionArchiver:
    """决策存档器"""
    
    def __init__(self, db, git_repo_path: str):
        self.db = db
        self.repo = git.Repo(git_repo_path)
        self.archive_path = Path(git_repo_path) / "decisions"
    
    async def archive_decision(
        self, 
        decision: DecisionRecord,
        attachments: List[str] = None
    ) -> str:
        """存档决策"""
        # 保存到数据库
        decision_id = await self.db.save_decision(decision)
        
        # 保存到文件系统
        decision_file = self.archive_path / f"{decision.decision_id}.json"
        with open(decision_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(decision), f, ensure_ascii=False, indent=2)
        
        # 保存附件
        if attachments:
            attachment_dir = self.archive_path / decision.decision_id / "attachments"
            attachment_dir.mkdir(parents=True, exist_ok=True)
            for attachment in attachments:
                # 复制附件文件
                pass
        
        # Git提交
        self.repo.index.add([str(decision_file)])
        self.repo.index.commit(f"Archive decision: {decision.decision_id}")
        
        return decision_id
    
    async def query_decisions(
        self,
        decision_type: Optional[DecisionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        keyword: Optional[str] = None
    ) -> List[DecisionRecord]:
        """查询决策记录"""
        return await self.db.query_decisions(
            decision_type=decision_type,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            keyword=keyword
        )
    
    async def get_decision_history(self, decision_id: str) -> List[Dict]:
        """获取决策历史"""
        # 从Git历史中获取决策变更记录
        decision_file = self.archive_path / f"{decision_id}.json"
        commits = list(self.repo.iter_commits(paths=str(decision_file)))
        
        history = []
        for commit in commits:
            history.append({
                'commit_hash': commit.hexsha,
                'commit_time': datetime.fromtimestamp(commit.committed_date),
                'author': commit.author.name,
                'message': commit.message
            })
        
        return history
```

### 2.4 决策知识库

#### 2.4.1 知识积累

**功能描述**: 从历史决策中提取知识和经验

**实现方案**:
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

class DecisionKnowledgeBase:
    """决策知识库"""
    
    def __init__(self, embedding_model, vector_store_path: str):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=vector_store_path,
            embedding_function=self.embeddings
        )
    
    async def extract_knowledge(self, decision: DecisionRecord) -> Dict:
        """从决策中提取知识"""
        knowledge = {
            'decision_id': decision.decision_id,
            'decision_type': decision.decision_type.value,
            'decision_result': decision.decision_result,
            'success_factors': [],
            'risk_factors': [],
            'lessons_learned': decision.lessons_learned,
            'best_practices': []
        }
        
        # 提取成功因素
        if decision.execution_result and 'success' in decision.execution_result.lower():
            knowledge['success_factors'] = await self._extract_success_factors(decision)
        
        # 提取风险因素
        if decision.impact_analysis:
            knowledge['risk_factors'] = await self._extract_risk_factors(decision)
        
        # 提取最佳实践
        knowledge['best_practices'] = await self._extract_best_practices(decision)
        
        # 存储到向量数据库
        await self._store_knowledge(knowledge)
        
        return knowledge
    
    async def retrieve_similar_decisions(
        self, 
        query: str,
        k: int = 5
    ) -> List[Dict]:
        """检索相似决策"""
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.metadata for doc in results]
    
    async def generate_decision_suggestion(
        self, 
        context: Dict
    ) -> str:
        """生成决策建议"""
        # 检索相关决策
        similar_decisions = await self.retrieve_similar_decisions(
            json.dumps(context)
        )
        
        # 基于历史决策生成建议
        suggestion = await self._generate_suggestion_from_history(
            context,
            similar_decisions
        )
        
        return suggestion
```

---

## 三、开源集成方案

### 3.1 OpenProject集成

**集成目标**: 使用OpenProject作为决策流程管理平台

**集成方案**:
```python
from openproject import OpenProjectClient

class OpenProjectIntegration:
    """OpenProject集成"""
    
    def __init__(self, base_url: str, api_key: str):
        self.client = OpenProjectClient(base_url, api_key)
    
    async def create_decision_project(self, decision: DecisionProposal):
        """创建决策项目"""
        project = await self.client.create_project({
            'name': f"决策: {decision.title}",
            'identifier': decision.proposal_id.lower(),
            'description': decision.description
        })
        
        # 创建工作包（任务）
        work_package = await self.client.create_work_package({
            'project': project['id'],
            'subject': decision.title,
            'description': decision.rationale,
            'type': 'Decision',
            'status': 'New'
        })
        
        return project, work_package
    
    async def track_decision_progress(self, proposal_id: str):
        """跟踪决策进度"""
        project = await self.client.get_project(proposal_id.lower())
        work_packages = await self.client.get_work_packages(project['id'])
        
        return {
            'project': project,
            'work_packages': work_packages,
            'status': self._map_status(work_packages[0]['status'])
        }
```

### 3.2 自定义决策流程

**实现方案**: 基于Python Flask/FastAPI构建轻量级决策流程系统

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="Investment Committee Decision Support")

class ProposalCreate(BaseModel):
    title: str
    description: str
    decision_type: str
    rationale: str

@app.post("/api/v1/proposals")
async def create_proposal(
    proposal: ProposalCreate,
    background_tasks: BackgroundTasks
):
    """创建决策提案"""
    # 创建提案
    new_proposal = await proposal_manager.create_proposal(proposal)
    
    # 触发AI评审（后台任务）
    background_tasks.add_task(
        proposal_reviewer.review_proposal,
        new_proposal
    )
    
    return {"proposal_id": new_proposal.proposal_id}

@app.post("/api/v1/votes")
async def cast_vote(vote: VoteCreate):
    """投票"""
    result = await voting_manager.cast_vote(
        vote.voting_id,
        vote.voter,
        vote.vote_result,
        vote.vote_reason
    )
    
    return {"success": result}

@app.get("/api/v1/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """获取决策记录"""
    decision = await decision_archiver.get_decision(decision_id)
    return decision
```

---

## 四、数据库设计

### 4.1 PostgreSQL表结构

```sql
-- 决策提案表
CREATE TABLE decision_proposals (
    proposal_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    decision_type VARCHAR(50) NOT NULL,
    proposer VARCHAR(100) NOT NULL,
    proposal_date TIMESTAMP NOT NULL,
    rationale TEXT,
    expected_impact JSONB,
    risk_assessment JSONB,
    status VARCHAR(20) NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 投票记录表
CREATE TABLE votes (
    vote_id VARCHAR(50) PRIMARY KEY,
    proposal_id VARCHAR(50) REFERENCES decision_proposals(proposal_id),
    voter VARCHAR(100) NOT NULL,
    vote_result VARCHAR(20) NOT NULL,
    vote_reason TEXT,
    vote_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 决策记录表
CREATE TABLE decision_records (
    decision_id VARCHAR(50) PRIMARY KEY,
    proposal_id VARCHAR(50) REFERENCES decision_proposals(proposal_id),
    decision_type VARCHAR(50) NOT NULL,
    decision_result TEXT,
    decision_date TIMESTAMP NOT NULL,
    execution_date TIMESTAMP,
    execution_result TEXT,
    impact_analysis JSONB,
    lessons_learned TEXT,
    related_decisions TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_proposals_status ON decision_proposals(status);
CREATE INDEX idx_proposals_type ON decision_proposals(decision_type);
CREATE INDEX idx_proposals_date ON decision_proposals(proposal_date);
CREATE INDEX idx_votes_proposal ON votes(proposal_id);
CREATE INDEX idx_decisions_type ON decision_records(decision_type);
CREATE INDEX idx_decisions_date ON decision_records(decision_date);
```

---

## 五、实施路径

### 5.1 Phase 1: 核心功能（Week 1）

**任务清单**:
- [ ] 实现决策提案管理模块
- [ ] 实现AI提案生成功能
- [ ] 实现提案评审功能
- [ ] 实现决策投票管理模块

**预期成果**:
- 完整的提案管理功能
- AI辅助提案生成
- 自动提案评审

### 5.2 Phase 2: 存档与知识库（Week 2）

**任务清单**:
- [ ] 实现决策记录存档模块
- [ ] 实现Git版本控制集成
- [ ] 实现决策知识库模块
- [ ] 实现知识检索功能

**预期成果**:
- 完整的决策存档系统
- Git版本控制集成
- 决策知识库

### 5.3 Phase 3: 集成与优化（Week 3）

**任务清单**:
- [ ] 集成OpenProject
- [ ] 实现Web界面
- [ ] 编写API文档
- [ ] 性能优化

**预期成果**:
- OpenProject集成
- Web管理界面
- 完整API文档

---

## 六、成功指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **提案生成准确率** | ≥80% | AI生成提案的准确性 |
| **提案评审效率** | ≤5分钟 | 自动评审时间 |
| **投票完成率** | ≥95% | 投票任务的完成率 |
| **决策追溯完整性** | 100% | 决策记录的完整性 |
| **知识库覆盖率** | ≥80% | 历史决策的知识提取率 |

---

## 七、风险与应对

### 7.1 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| AI提案质量不稳定 | 中 | 人工审核 + 规则约束 |
| 系统性能瓶颈 | 低 | 异步处理 + 缓存优化 |
| 数据丢失风险 | 高 | Git备份 + 数据库备份 |

### 7.2 业务风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 决策流程过于复杂 | 中 | 简化流程 + 可配置规则 |
| 用户接受度低 | 中 | 培训 + 文档支持 |
| 维护成本高 | 低 | 开源方案 + AI辅助维护 |

---

## 八、相关文档

- [战略决策层蓝图](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md)
- [架构补充方案](./STRATEGIC_DECISION_ARCHITECTURE_COMPLETION_PLAN_20260407.md)
- [决策知识库蓝图](08_HUMAN_AI_INTERFACE/18_KNOWLEDGE_BASE/KNOWLEDGE_BASE_BLUEPRINT.md)
- [开源集成蓝图](./OPEN_SOURCE_INTEGRATION_BLUEPRINT.md)

---

**文档版本**: v1.0
**创建时间**: 2026-04-07
**预计完成时间**: 2026-04-10
**维护者**: 系统架构师
