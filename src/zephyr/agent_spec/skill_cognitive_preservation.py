"""
MOD-INF-019: Agent Spec — Skill Cognitive Preservation
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 认知保留 —— 跨 Session/跨 Agent 的 Skill 学习状态持久化.
保存 Skill 执行后的认知决策链，供后续 Agent 做暖启动(warm-resume).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class CognitiveSnapshot:
    def __init__(self, skill_id: str, state: Dict[str, Any],
                 timestamp: Optional[float] = None):
        self.skill_id = skill_id
        self.state = state
        self.timestamp = timestamp or time.time()
        self.version = state.get("_version", 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "state": self.state,
            "timestamp": self.timestamp,
            "version": self.version,
        }


class SkillCognitivePreservation:
    """Skill 认知保留 —— 跨 Session 记忆持久化与暖启动."""

    _SNAPSHOT_DIR = Path("_journals/cognitive_snapshots")
    _MAX_SNAPSHOTS_PER_SKILL = 20
    _MERGE_STRATEGY = "latest_wins"

    def __init__(self):
        self._memory: Dict[str, CognitiveSnapshot] = {}
        self._load_all()

    def save(self, skill_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        state["_version"] = state.get("_version", 0) + 1
        state["_saved_at"] = time.time()
        snapshot = CognitiveSnapshot(skill_id, state)
        self._memory[skill_id] = snapshot
        self._persist_snapshot(snapshot)
        self._prune_old_snapshots(skill_id)
        return {"skill_id": skill_id, "version": state["_version"], "persisted": True}

    def restore(self, skill_id: str) -> Dict[str, Any]:
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

    def merge(self, skill_id: str, delta: Dict[str, Any]) -> Dict[str, Any]:
        existing = self._memory.get(skill_id)
        if existing:
            merged = dict(existing.state)
            merged.update(delta)
            return self.save(skill_id, merged)
        return self.save(skill_id, delta)

    def list_skills(self) -> List[Dict[str, Any]]:
        return [
            {"skill_id": sid, "version": s.version,
             "age_s": round(time.time() - s.timestamp, 1)}
            for sid, s in sorted(self._memory.items())
        ]

    def warm_resume_context(self, skill_ids: List[str],
                            max_tokens: int = 800) -> str:
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
        self._delete_snapshots(skill_id)

    # ---- Internal persistence ----

    def _persist_snapshot(self, snapshot: CognitiveSnapshot):
        try:
            self._SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
            fname = f"{snapshot.skill_id}_{int(snapshot.timestamp)}.json"
            path = self._SNAPSHOT_DIR / fname
            path.write_text(json.dumps(
                snapshot.to_dict(), ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    def _prune_old_snapshots(self, skill_id: str):
        try:
            pattern = f"{skill_id}_*.json"
            files = sorted(
                self._SNAPSHOT_DIR.glob(pattern),
                key=lambda p: p.stat().st_mtime, reverse=True)
            for f in files[self._MAX_SNAPSHOTS_PER_SKILL:]:
                f.unlink(missing_ok=True)
        except OSError:
            pass

    def _load_all(self):
        try:
            if not self._SNAPSHOT_DIR.exists():
                return
            for f in sorted(self._SNAPSHOT_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    sid = data["skill_id"]
                    snap = CognitiveSnapshot(
                        skill_id=sid, state=data["state"],
                        timestamp=data["timestamp"])
                    existing = self._memory.get(sid)
                    if not existing or snap.timestamp > existing.timestamp:
                        self._memory[sid] = snap
                except (json.JSONDecodeError, KeyError, OSError):
                    pass
        except OSError:
            pass

    def _delete_snapshots(self, skill_id: str):
        try:
            for f in self._SNAPSHOT_DIR.glob(f"{skill_id}_*.json"):
                f.unlink(missing_ok=True)
        except OSError:
            pass


__all__ = ["SkillCognitivePreservation", "CognitiveSnapshot"]
