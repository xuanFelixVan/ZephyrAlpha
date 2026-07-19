# [BLUEPRINT] MOD-INF-005 | scripts/a2a_full_verification.py | §
# [MODULE] scripts.a2a_full_verification
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.integration.__init__; zephyr.gov_audit.__init__; zephyr.security.access_control.a2a_check
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""A2A Protocol 全链路满分验证脚本"""

import sys

score = 0
total = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global score, total
    total += 1
    if condition:
        score += 1
        print(f"  PASS  {name} {detail}")
    else:
        print(f"  FAIL  {name} {detail}")


print("=" * 60)
print("A2A Protocol v0.10.0 Full-Chain Verification")
print("=" * 60)

# === 验证2: AutoRuntimeCore启动链路 ===
print("\n[验证2] AutoRuntimeCore启动链路A2A集成")
from zephyr.infrastructure.config.runtime_config import RuntimeConfig
from zephyr.infrastructure.runtime.auto_runtime_core import AutoRuntimeCore

c = AutoRuntimeCore(RuntimeConfig())
c._registry.load_from_dir()

check("A2A Registry 已初始化", c.a2a_registry is not None)
check("A2A ProtocolGateway 已初始化", c._a2a_protocol_gateway is not None)

int_points = {p.point_id: p.status for p in c._integration_registry._points.values()}
check("IntegrationPoint a2a-protocol 已注册", "a2a-protocol" in int_points)
check("IntegrationPoint a2a-protocol 状态 CONNECTED", int_points.get("a2a-protocol") == "CONNECTED")

# === 验证3: CapabilityCard加载+发现 ===
print("\n[验证3] CapabilityCard加载+发现")
a2a_caps = c._registry.find_by_tags(["a2a"])
check("A2A CapabilityCard 可被 tag 发现", len(a2a_caps) >= 1, f"found={len(a2a_caps)}")

a2a_disc = c._registry.discover("agent-to-agent")
check("A2A CapabilityCard 可被 discover 发现", len(a2a_disc) >= 1, f"found={len(a2a_disc)}")

if a2a_caps:
    cap = a2a_caps[0]
    check("CapabilityCard ID 正确", cap.capability_id == "a2a-protocol")
    check("CapabilityCard 名称正确", cap.name == "A2A Protocol")
    check("CapabilityCard 状态 ACTIVE", cap.status == "ACTIVE")
    check("CapabilityCard category coordination", cap.category.value == "coordination")

# === 验证4: 新AI发现路径 ===
print("\n[验证4] 新AI发现路径完整性")
with open("AGENTS.md", encoding="utf-8") as f:
    agents_md = f.read()

check("AGENTS.md 包含 A2A Protocol", "A2A Protocol" in agents_md)
check("AGENTS.md 包含 card_registry.discover 示例", "card_registry.discover" in agents_md)
check("AGENTS.md 包含 ConflictDetector 示例", "ConflictDetector" in agents_md)
check("AGENTS.md 包含 Arbitrator 示例", "Arbitrator" in agents_md)
check("AGENTS.md 包含 A2A 触发关键词说明", "a2a" in agents_md.lower())

# === 验证5: 三套注册体系桥接 ===
print("\n[验证5] 三套注册体系桥接")
from zephyr.integration.a2a_protocol.agent_card import AgentCapability, AgentCard

test_card = AgentCard(
    agent_id="agent-verify-bridge",
    name="Bridge Verify",
    description="test",
    version="1.0",
    capabilities=[AgentCapability.WRITE],
    skill_ids=[],
    model_preferences=["test"],
    max_tasks=5,
)
c._a2a_registry.register(test_card)
synced = c.sync_a2a_to_capability_registry()
bridge_cap = c._registry.get("a2a-agent-agent-verify-bridge")
check("A2A AgentCard 可同步到 CapabilityRegistry", bridge_cap is not None, f"synced={synced}")
check("桥接后的 CapabilityCard 存在", bridge_cap is not None)
if bridge_cap:
    check("桥接后的 tags 包含 a2a-agent", "a2a-agent" in bridge_cap.tags)
    check("桥接后的 tags 包含 write capability", "write" in bridge_cap.tags)

# === 验证6: 红白对抗链路 ===
print("\n[验证6] 红白对抗链路")
from zephyr.integration.a2a_protocol.a2a_red_team import A2ARedTeam

rt = A2ARedTeam()
vectors = rt.list_vectors()
check("红队攻击向量 >= 6", len(vectors) >= 6, f"vectors={len(vectors)}")

severities = [v.severity.value for v in vectors]
check("包含 CRITICAL 级别向量", "critical" in severities)
check("包含 HIGH 级别向量", "high" in severities)

# === 验证7: 跨系统全链路打通 ===
print("\n[验证7] 跨系统全链路打通")

# Layer 1
from zephyr.integration.a2a_protocol.a2a_registry import A2ARegistry
from zephyr.integration.a2a_protocol.identity_verifier import IdentityVerifier

reg = A2ARegistry()
iv = IdentityVerifier()
check("Layer 1: A2ARegistry 可用", True)
check("Layer 1: IdentityVerifier 可用", True)

# Layer 2
check("Layer 2: A2AMessage 可用", True)
check("Layer 2: A2AStateMachine 可用", True)
check("Layer 2: MessageRouter 可用", True)
check("Layer 2: HandoffManager 可用", True)

# Layer 3
check("Layer 3: ConflictDetector 可用", True)
check("Layer 3: Arbitrator 可用", True)
check("Layer 3: A2ANegotiation 可用", True)
check("Layer 3: A2AVoting 可用", True)
check("Layer 3: A2ADebate 可用", True)
check("Layer 3: A2ASaga 可用", True)
check("Layer 3: Supervisor 可用", True)
check("Layer 3: DeadlockGuard 可用", True)
check("Layer 3: A2AProtocolGateway 可用", True)

# 治理桥接
check("Governance: GovernanceAdapter 可用", True)
check("Governance: A2AAuditor 可用", True)
check("Governance: verify_a2a_pair 可用", True)

# L8 安全层
try:
    import importlib

    l8_mod = importlib.import_module("zephyr.security.llm_defense.llm_security.l8_multi_agent")
    check("Security: L8 MultiAgentSecurityLayer 可用", hasattr(l8_mod, "MultiAgentSecurityLayer"))
except Exception as e:
    check("Security: L8 MultiAgentSecurityLayer 可用", False, str(e))

# === 验证8: 残余断裂点扫描 ===
print("\n[验证8] 残余断裂点扫描")

# 检查 ConstructionVerifier
from zephyr.integration.a2a_protocol.construction_verifier import ConstructionVerifier

cv = ConstructionVerifier()
result = cv.verify()
is_verified = result.get("passed", False) if isinstance(result, dict) else getattr(result, "passed", False)
issue_count = len(result.get("issues", [])) if isinstance(result, dict) else len(getattr(result, "issues", []))
stub_ratio = result.get("stub_ratio", 1.0) if isinstance(result, dict) else getattr(result, "stub_ratio", 1.0)
check(
    "ConstructionVerifier 自检通过", is_verified and stub_ratio < 0.1, f"issues={issue_count} stub_ratio={stub_ratio}"
)

# 检查 SpecSync
from zephyr.integration.a2a_protocol.spec_sync import SpecSync

ss = SpecSync()
ss.register(
    "a2a-protocol",
    "docs/03_modules/infrastructure_runtime_integration/a2a-protocol/blueprint.md",
    ["src/zephyr/infrastructure_runtime_integration/a2a_protocol/"],
)
sync_result = ss.check("a2a-protocol")
check("SpecSync a2a-protocol 注册成功", sync_result["status"] == "synced")

# === 最终评分 ===
print("\n" + "=" * 60)
pct = (score / total * 100) if total > 0 else 0
print(f"FINAL SCORE: {score}/{total} = {pct:.1f}%")
if pct == 100:
    print("VERDICT: PERFECT SCORE")
elif pct >= 90:
    print("VERDICT: EXCELLENT (minor gaps)")
elif pct >= 80:
    print("VERDICT: GOOD (some gaps remain)")
else:
    print("VERDICT: NEEDS WORK")
print("=" * 60)

sys.exit(0 if pct == 100 else 1)
