"""Layer 3: 协调+仲裁 — Coordinator, Living Spec 同步, 死锁防护, 全量 25 模块落地"""

from .supervisor import Supervisor
from .construction_verifier import ConstructionVerifier, StubAnalysis, VerifierResult
from .deadlock_guard import DeadlockGuard
from .livelock_detector import LivelockDetector
from .cascade_guard import CascadeGuard
from .a2a_economics import A2AEconomics
from .a2a_forgetting import A2AForgetting
from .a2a_delegation_chain import A2ADelegationChain
from .a2a_idempotency import A2AIdempotency
from .a2a_temporal_admission import A2ATemporalAdmission
from .a2a_idle_guard import A2AIdleGuard
from .a2a_red_team import A2ARedTeam, AttackVector, AttackSeverity, AttackCategory

from .conflict_detector import ConflictDetector, Conflict, ConflictType, ConflictSeverity, ChangeRange, ChangeSet
from .arbitrator import Arbitrator, AgentRole, FileOwnership, AgentMeta, ArbitrationResult
from .semantic_diff import SemanticDiffEngine, SemanticDiffType, SemanticDiffEntry, SemanticDiffReport, SemanticRegion
from .a2a_security import A2ASecurityScanner, SecurityFinding, ThreatCategory, SecurityVerdict, A2ASecurityReport
from .a2a_anomaly_detector import A2AAnomalyDetector, AnomalyRecord, AnomalyLevel, MetricBaseline, MetricKey

from .a2a_debate import A2ADebate, DebateRound, DebateResult, DebatePhase
from .a2a_voting import A2AVoting, VoteAction, VotingResult
from .a2a_negotiation import A2ANegotiation, NegotiationOffer, NegotiationResult, NegotiationStatus
from .a2a_saga import A2ASaga, SagaStep, SagaResult, SagaStatus
from .a2a_work_steal import A2AWorkSteal, TaskQueue

from .a2a_collusion_detector import A2ACollusionDetector, CollusionFinding, CollusionReport
from .a2a_blame_attribution import A2ABlameAttribution, BlameItem, BlameReport
from .a2a_causal_trace import A2ACausalTrace, CausalNode, CausalEdge, CausalGraph
from .a2a_behavior_fingerprint import A2ABehaviorFingerprint, BehaviorFingerprint
from .a2a_knowledge_distill import A2AKnowledgeDistill, DistilledKnowledge
from .a2a_latent_comm import A2ALatentComm, LatentCommSignal
from .a2a_cross_agent_semantic_flow import CrossAgentSemanticFlow, SemanticFlowNode, SemanticFlow
from .session_smuggling_defense import SessionSmugglingDefense, SmugglingAttempt

from .a2a_dashboard import A2ADashboard, DashboardPanel
from .a2a_governance_adapter import A2AGovernanceAdapter, GovernanceCheckResult
from .a2a_tracing import A2ATracing, Span
from .a2a_protocol_gateway import A2AProtocolGateway, GatewayResult
from .a2a_frame_negotiation import A2AFrameNegotiation, FrameOffer, NegotiatedFrame
from .spec_sync import SpecSync, SpecSyncEntry
from .a2a_formal_verification import A2AFormalVerification, VerificationStatus, PropertyCheck, VerificationReport

__all__ = [
    'Supervisor', 'ConstructionVerifier', 'StubAnalysis', 'VerifierResult',
    'DeadlockGuard', 'LivelockDetector', 'CascadeGuard',
    'A2AEconomics', 'A2AForgetting',
    'A2ADelegationChain', 'A2AIdempotency',
    'A2ATemporalAdmission', 'A2AIdleGuard',
    'A2ARedTeam', 'AttackVector', 'AttackSeverity', 'AttackCategory',

    'ConflictDetector', 'Conflict', 'ConflictType', 'ConflictSeverity', 'ChangeRange', 'ChangeSet',
    'Arbitrator', 'AgentRole', 'FileOwnership', 'AgentMeta', 'ArbitrationResult',
    'SemanticDiffEngine', 'SemanticDiffType', 'SemanticDiffEntry', 'SemanticDiffReport', 'SemanticRegion',
    'A2ASecurityScanner', 'SecurityFinding', 'ThreatCategory', 'SecurityVerdict', 'A2ASecurityReport',
    'A2AAnomalyDetector', 'AnomalyRecord', 'AnomalyLevel', 'MetricBaseline', 'MetricKey',

    'A2ADebate', 'DebateRound', 'DebateResult', 'DebatePhase',
    'A2AVoting', 'VoteAction', 'VotingResult',
    'A2ANegotiation', 'NegotiationOffer', 'NegotiationResult', 'NegotiationStatus',
    'A2ASaga', 'SagaStep', 'SagaResult', 'SagaStatus',
    'A2AWorkSteal', 'TaskQueue',

    'A2ACollusionDetector', 'CollusionFinding', 'CollusionReport',
    'A2ABlameAttribution', 'BlameItem', 'BlameReport',
    'A2ACausalTrace', 'CausalNode', 'CausalEdge', 'CausalGraph',
    'A2ABehaviorFingerprint', 'BehaviorFingerprint',
    'A2AKnowledgeDistill', 'DistilledKnowledge',
    'A2ALatentComm', 'LatentCommSignal',
    'CrossAgentSemanticFlow', 'SemanticFlowNode', 'SemanticFlow',
    'SessionSmugglingDefense', 'SmugglingAttempt',

    'A2ADashboard', 'DashboardPanel',
    'A2AGovernanceAdapter', 'GovernanceCheckResult',
    'A2ATracing', 'Span',
    'A2AProtocolGateway', 'GatewayResult',
    'A2AFrameNegotiation', 'FrameOffer', 'NegotiatedFrame',
    'SpecSync', 'SpecSyncEntry',
    'A2AFormalVerification', 'VerificationStatus', 'PropertyCheck', 'VerificationReport',
    'a2a_anomaly_detector', 'a2a_behavior_fingerprint', 'a2a_blame_attribution',
    'a2a_carbon', 'a2a_causal_trace', 'a2a_checkpoint', 'a2a_collusion_detector',
    'a2a_consent', 'a2a_constitutional', 'a2a_context_rot', 'a2a_cross_agent_semantic_flow',
    'a2a_dashboard', 'a2a_debate', 'a2a_delegation_chain', 'a2a_economics',
    'a2a_forgetting', 'a2a_formal_verification', 'a2a_frame_negotiation',
    'a2a_governance_adapter', 'a2a_hardware_router', 'a2a_hibernate',
    'a2a_idempotency', 'a2a_idle_guard', 'a2a_immune', 'a2a_knowledge_distill',
    'a2a_latent_comm', 'a2a_metrics', 'a2a_negotiation', 'a2a_protocol_gateway',
    'a2a_protocol_security', 'a2a_red_team', 'a2a_saga', 'a2a_security',
    'a2a_temporal_admission', 'a2a_tracing', 'a2a_vector_reputation',
    'a2a_voting', 'a2a_work_steal', 'semantic_diff',
]

__version__ = "0.10.0"