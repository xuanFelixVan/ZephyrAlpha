# [A_module] module_id=MOD-ORC_skill_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] src.zephyr.orchestration.agent_lifecycle.skill_router

# [INVARIANTS]

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import re
import logging
import yaml
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from zephyr.integration.local_model.embedding_router import EmbeddingRouter


_logger = logging.getLogger(__name__)

_REGISTRY_PATH = Path(__file__).resolve().parent / "skill-registry.yaml"

_SEMANTIC_SIMILARITY_THRESHOLD = 0.7


class ConstructionStage(str, Enum):
    IDEA = "idea"
    PRE_AUDIT = "pre_audit"
    BLUEPRINT = "blueprint"
    CONSTRUCTION = "construction"
    VERIFICATION = "verification"
    POST_AUDIT = "post_audit"

    @classmethod
    def from_label(cls, label: str) -> Optional["ConstructionStage"]:
        mapping = {
            "想法": cls.IDEA, "草稿": cls.IDEA,
            "审计（施工前）": cls.PRE_AUDIT, "审计(施工前)": cls.PRE_AUDIT,
            "蓝图": cls.BLUEPRINT, "设计": cls.BLUEPRINT,
            "施工": cls.CONSTRUCTION, "实现": cls.CONSTRUCTION,
            "验收": cls.VERIFICATION, "验证": cls.VERIFICATION,
            "审计（施工后）": cls.POST_AUDIT, "审计(施工后)": cls.POST_AUDIT,
        }
        return mapping.get(label)


class SkillRouter:
    STAGE_ROUTING = {
        ConstructionStage.IDEA: {
            "role": "architect",
            "domain_default": "master-blueprint",
        },
        ConstructionStage.PRE_AUDIT: {
            "role": "governor",
            "domain_default": "gate-engine",
        },
        ConstructionStage.BLUEPRINT: {
            "role": "architect",
            "domain_match_mode": "topic",
        },
        ConstructionStage.CONSTRUCTION: {
            "role": "implementer",
            "domain_match_mode": "module",
        },
        ConstructionStage.VERIFICATION: {
            "role": "governor",
            "domain_match_mode": "module",
        },
        ConstructionStage.POST_AUDIT: {
            "role": "governor",
            "domain_default": "drift-detector",
        },
    }

    FALLBACK_TASK_ROUTING: List[Tuple[str, str, str]] = [
        (r"database|migration|sql|atm", "database-specialist", "implementer"),
        (r"mcp\s*(?:server|tool|protocol)?", "mcp-specialist", "implementer"),
        (r"context|pipeline", "context-specialist", "implementer"),
        (r"feedback|loop", "feedback-specialist", "implementer"),
        (r"gate|rule|policy", "gate-specialist", "governor"),
        (r"permission|rbac|acl", "agent-specialist", "governor"),
        (r"blueprint", "master-blueprint", "architect"),
        (r"audit|compliance|governance|drift", "drift-detector", "governor"),
        (r"knowledge|k[ea]\b|kb", "knowledge-specialist", "implementer"),
    ]

    DEFAULT = {"role": "implementer", "domain_default": None}

    def __init__(self, registry_path: Optional[Path] = None):
        self._registry_path = registry_path or _REGISTRY_PATH
        self._yaml_routing: Optional[List[Tuple[str, str, str]]] = None
        self._semantic_index: Optional[Dict[str, Any]] = None
        self._embedding_router: EmbeddingRouter | None = None

    def _init_semantic_index(self) -> None:
        if self._semantic_index is not None:
            return
        try:
            from zephyr.integration.local_model.embedding_router import EmbeddingRouter
            self._embedding_router = EmbeddingRouter()
            self._embedding_router.warmup()
            if not self._embedding_router.bge_m3_available and not self._embedding_router.bge_small_available:
                _logger.warning("Semantic index: no embedding model available, semantic routing disabled")
                self._semantic_index = {}
                return
            skill_descriptions: Dict[str, Tuple[str, str]] = {}
            domain_to_role: Dict[str, str] = {}
            try:
                with open(self._registry_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except (FileNotFoundError, yaml.YAMLError):
                self._semantic_index = {}
                return
            for category in ("domain", "role"):
                for _sid, sdata in data.get("skills", {}).get(category, {}).items():
                    name = sdata.get("name", "")
                    desc = sdata.get("description", name)
                    skill_descriptions[name] = (desc, name)
                    domain_to_role[name] = "governor" if category == "role" and name == "governor" else "implementer"
            domain_to_role.setdefault("master-blueprint", "architect")
            domain_to_role.setdefault("drift-detector", "governor")
            domain_to_role.setdefault("gate-specialist", "governor")
            domain_to_role.setdefault("agent-specialist", "governor")
            if not skill_descriptions:
                self._semantic_index = {}
                return
            names = list(skill_descriptions.keys())
            descs = [skill_descriptions[n][0] for n in names]
            vectors = self._embedding_router.embed_batch(descs, "decisions")
            if vectors is None or len(vectors) != len(names):
                self._semantic_index = {}
                return
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            normalized = vectors / norms
            self._semantic_index = {
                "names": names,
                "vectors": normalized,
                "domain_to_role": domain_to_role,
            }
            _logger.info("Semantic index built: %d skills", len(names))
        except Exception as exc:
            _logger.warning("Semantic index init failed: %s", exc)
            self._semantic_index = {}

    def _semantic_route(self, task_description: str) -> Optional[Tuple[str, str]]:
        self._init_semantic_index()
        if not self._semantic_index or "vectors" not in self._semantic_index:
            return None
        try:
            query_vec = self._embedding_router.embed(task_description, "decisions")
            if query_vec is None:
                return None
            query_norm = query_vec / max(np.linalg.norm(query_vec), 1e-9)
            similarities = self._semantic_index["vectors"] @ query_norm
            best_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_idx])
            if best_score < _SEMANTIC_SIMILARITY_THRESHOLD:
                _logger.debug("Semantic route below threshold: %.3f < %.3f", best_score, _SEMANTIC_SIMILARITY_THRESHOLD)
                return None
            best_name = self._semantic_index["names"][best_idx]
            best_role = self._semantic_index["domain_to_role"].get(best_name, "implementer")
            _logger.info("Semantic route: '%s' -> %s (%.3f)", task_description, best_name, best_score)
            return (best_name, best_role)
        except Exception as exc:
            _logger.warning("Semantic route failed: %s", exc)
            return None

    def _load_yaml_routing(self) -> List[Tuple[str, str, str]]:
        if self._yaml_routing is not None:
            return self._yaml_routing

        try:
            with open(self._registry_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError):
            return self.FALLBACK_TASK_ROUTING

        task_keywords: Dict[str, str] = data.get("trigger_routing", {}).get("task_keywords", {})
        if not task_keywords:
            return self.FALLBACK_TASK_ROUTING

        domain_to_role: Dict[str, str] = {}
        for category in ("domain", "role"):
            for sid, sdata in data.get("skills", {}).get(category, {}).items():
                name = sdata.get("name", "")
                domain_to_role[name] = "governor" if category == "role" and name == "governor" else "implementer"
        domain_to_role.setdefault("master-blueprint", "architect")
        domain_to_role.setdefault("drift-detector", "governor")
        domain_to_role.setdefault("gate-specialist", "governor")
        domain_to_role.setdefault("agent-specialist", "governor")

        keyword_groups: Dict[str, List[str]] = {}
        for keyword, domain in task_keywords.items():
            keyword_groups.setdefault(domain, []).append(re.escape(keyword))

        routing: List[Tuple[str, str, str]] = []
        for domain, keywords in keyword_groups.items():
            keywords_sorted = sorted(keywords, key=len, reverse=True)
            pattern = "|".join(keywords_sorted)
            role = domain_to_role.get(domain, "implementer")
            routing.append((pattern, domain, role))

        routing.sort(key=lambda x: -len(x[0]))

        self._yaml_routing = routing
        return self._yaml_routing

    def route(
        self,
        stage: Optional[ConstructionStage],
        task_description: str,
    ) -> Tuple[str, Optional[str]]:
        role: Optional[str] = None
        domain: Optional[str] = None

        domain_override = self._match_task_routing(task_description)
        if domain_override:
            domain, role = domain_override
        else:
            semantic_result = self._semantic_route(task_description)
            if semantic_result:
                domain, role = semantic_result

        if stage is not None and stage in self.STAGE_ROUTING:
            stage_config = self.STAGE_ROUTING[stage]
            if role is None:
                role = stage_config.get("role")
            if domain is None:
                domain = stage_config.get("domain_default")
                if domain is None and "domain_match_mode" in stage_config:
                    domain = self._match_domain(task_description)

        if role is None:
            role = self.DEFAULT["role"]
        if domain is None:
            domain = self.DEFAULT["domain_default"]

        return (role, domain)

    def _match_task_routing(self, task_description: str) -> Optional[Tuple[str, str]]:
        description_lower = task_description.lower()
        routing = self._load_yaml_routing()
        best_match_len = 0
        best_result: Optional[Tuple[str, str]] = None
        for pattern, domain, role in routing:
            m = re.search(pattern, description_lower, re.IGNORECASE)
            if m and len(m.group(0)) > best_match_len:
                best_match_len = len(m.group(0))
                best_result = (domain, role)
        return best_result

    def _match_domain(self, task_description: str) -> Optional[str]:
        match = self._match_task_routing(task_description)
        return match[0] if match else None

    def list_registered_skills(self) -> Dict[str, Dict[str, str]]:
        try:
            with open(self._registry_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError):
            return {}
        result: Dict[str, Dict[str, str]] = {}
        for category in ("domain", "role"):
            for sid, sdata in data.get("skills", {}).get(category, {}).items():
                result[sid] = {
                    "name": sdata.get("name", sid),
                    "category": category,
                    "description": sdata.get("description", ""),
                    "version": sdata.get("version", "0.1.0"),
                    "spec_hash": sdata.get("spec_hash", ""),
                }
        return result


TriggerRouter = SkillRouter

__all__ = ["SkillRouter", "TriggerRouter", "ConstructionStage"]
