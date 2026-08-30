# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_cognitive_preservation
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Cognitive Preservation
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 认知保留 —— 跨 Session/跨 Agent 的 Skill 学习状态持久化.
保存 Skill 执行后的认知决策链，供后续 Agent 做暖启动(warm-resume).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: skill_id 参数
#   fields: 参数 skill_id（无注解）
#   code: skill_cognitive_preservation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: state 参数
#   fields: 参数 state（无注解）
#   code: skill_cognitive_preservation.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: timestamp 参数
#   fields: 参数 timestamp（无注解）
#   code: skill_cognitive_preservation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CognitiveSnapshot
#   name_en: CognitiveSnapshot
#   intro: class CognitiveSnapshot 源码 L80-L93
#   desc: 公共方法（定义序）: to_dict；源码 L80-L93
#   inputs: skill_id state timestamp
#   outputs: 返回值
# - id: A2
#   name_zh: ② SkillCognitivePreservation
#   name_en: SkillCognitivePreservation
#   intro: Skill 认知保留 —— 跨 Session 记忆持久化与暖启动.
#   desc: Skill 认知保留 —— 跨 Session 记忆持久化与暖启动.；公共方法（定义序）: memory, save, restore, merge, list_skills, warm_resume_context,…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CognitiveSnapshot, SkillCognitivePreservation
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class CognitiveSnapshot:
    def __init__(self, skill_id: str, state: dict[str, Any], timestamp: float | None = None):
        self.skill_id = skill_id
        self.state = state
        self.timestamp = timestamp or time.time()
        self.version = state.get("_version", 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "state": self.state,
            "timestamp": self.timestamp,
            "version": self.version,
        }


class SkillCognitivePreservation:
    """Skill 认知保留 —— 跨 Session 记忆持久化与暖启动."""

    _SNAPSHOT_DIR = Path("_journals/cognitive_snapshots")
    MAX_SNAPSHOTS_PER_SKILL: int = 20
    _MAX_SNAPSHOTS_PER_SKILL = MAX_SNAPSHOTS_PER_SKILL  # backward-compat alias
    _MERGE_STRATEGY = "latest_wins"

    def __init__(self):
        self._memory: dict[str, CognitiveSnapshot] = {}
        self.load_all()

    @property
    def memory(self) -> dict[str, CognitiveSnapshot]:
        """Public accessor for the in-memory snapshot store (Stage 4 publicization)."""
        return self._memory

    def save(self, skill_id: str, state: dict[str, Any]) -> dict[str, Any]:
        state["_version"] = state.get("_version", 0) + 1
        state["_saved_at"] = time.time()
        snapshot = CognitiveSnapshot(skill_id, state)
        self._memory[skill_id] = snapshot
        self.persist_snapshot(snapshot)
        self.prune_old_snapshots(skill_id)
        return {"skill_id": skill_id, "version": state["_version"], "persisted": True}

    def restore(self, skill_id: str) -> dict[str, Any]:
        snapshot = self._memory.get(skill_id)
        if snapshot:
            return {
                "skill_id": skill_id,
                "found": True,
                "version": snapshot.version,
                "age_s": round(time.time() - snapshot.timestamp, 1),
                "state": snapshot.state,
            }
        return {"skill_id": skill_id, "found": False, "state": {}}

    def merge(self, skill_id: str, delta: dict[str, Any]) -> dict[str, Any]:
        existing = self._memory.get(skill_id)
        if existing:
            merged = dict(existing.state)
            merged.update(delta)
            return self.save(skill_id, merged)
        return self.save(skill_id, delta)

    def list_skills(self) -> list[dict[str, Any]]:
        return [
            {"skill_id": sid, "version": s.version, "age_s": round(time.time() - s.timestamp, 1)}
            for sid, s in sorted(self._memory.items())
        ]

    def warm_resume_context(self, skill_ids: list[str], max_tokens: int = 800) -> str:
        parts = []
        token_estimate = 0
        for sid in skill_ids:
            snapshot = self._memory.get(sid)
            if not snapshot:
                continue
            entry = f"[Warm Resume: {sid} v{snapshot.version}]\n"
            for k, v in snapshot.state.items():
                if k.startswith("_"):
                    continue
                line = f"  {k}: {str(v)[:120]}\n"
                if token_estimate + len(entry + line) > max_tokens * 4:
                    break
                entry += line
                token_estimate += len(line)
            parts.append(entry)
        return "\n".join(parts) if parts else ""

    def forget(self, skill_id: str):
        self._memory.pop(skill_id, None)
        self.delete_snapshots(skill_id)

    # ---- Internal persistence ----

    def persist_snapshot(self, snapshot: CognitiveSnapshot):
        """Public method: persist a snapshot to disk (Stage 4 publicization)."""
        try:
            self._SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
            fname = f"{snapshot.skill_id}_{int(snapshot.timestamp)}.json"
            path = self._SNAPSHOT_DIR / fname
            path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    def _persist_snapshot(self, snapshot: CognitiveSnapshot):
        """Backward-compat thin wrapper."""
        return self.persist_snapshot(snapshot)

    def prune_old_snapshots(self, skill_id: str):
        """Public method: prune old snapshots beyond the retention limit (Stage 4 publicization)."""
        try:
            pattern = f"{skill_id}_*.json"
            files = sorted(self._SNAPSHOT_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
            for f in files[self.MAX_SNAPSHOTS_PER_SKILL :]:
                f.unlink(missing_ok=True)
        except OSError:
            pass

    def _prune_old_snapshots(self, skill_id: str):
        """Backward-compat thin wrapper."""
        return self.prune_old_snapshots(skill_id)

    def load_all(self):
        """Public method: load all snapshots from disk into memory (Stage 4 publicization)."""
        try:
            if not self._SNAPSHOT_DIR.exists():
                return
            for f in sorted(self._SNAPSHOT_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    sid = data["skill_id"]
                    snap = CognitiveSnapshot(skill_id=sid, state=data["state"], timestamp=data["timestamp"])
                    existing = self._memory.get(sid)
                    if not existing or snap.timestamp > existing.timestamp:
                        self._memory[sid] = snap
                except (json.JSONDecodeError, KeyError, OSError):
                    pass
        except OSError:
            pass

    def _load_all(self):
        """Backward-compat thin wrapper."""
        return self.load_all()

    def delete_snapshots(self, skill_id: str):
        """Public method: delete all on-disk snapshots for a skill (Stage 4 publicization)."""
        try:
            for f in self._SNAPSHOT_DIR.glob(f"{skill_id}_*.json"):
                f.unlink(missing_ok=True)
        except OSError:
            pass

    def _delete_snapshots(self, skill_id: str):
        """Backward-compat thin wrapper."""
        return self.delete_snapshots(skill_id)


__all__ = ["CognitiveSnapshot", "SkillCognitivePreservation"]
