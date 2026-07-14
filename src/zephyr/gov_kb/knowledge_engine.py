# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_kb.knowledge_engine
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_knowledge_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from datetime import UTC, datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class KnowledgeEntry(BaseModel):
    entry_id: str
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    source_file: str = ""
    indexed_at: str = ""


class KnowledgeIndex(BaseModel):
    entries: dict[str, KnowledgeEntry] = Field(default_factory=dict)
    inverted_index: dict[str, list[str]] = Field(default_factory=dict)

    def index(self, entry: KnowledgeEntry) -> None:
        entry.indexed_at = datetime.now(UTC).isoformat()
        self.entries[entry.entry_id] = entry
        for tag in entry.tags:
            self.inverted_index.setdefault(tag, []).append(entry.entry_id)

    def search(self, query: str) -> list[KnowledgeEntry]:
        query_lower = query.lower()
        results: list[KnowledgeEntry] = []
        for entry in self.entries.values():
            if (
                query_lower in entry.title.lower()
                or query_lower in entry.content.lower()
                or any(query_lower in t.lower() for t in entry.tags)
            ):
                results.append(entry)
        return results

    def search_by_tag(self, tag: str) -> list[KnowledgeEntry]:
        ids = self.inverted_index.get(tag, [])
        return [self.entries[eid] for eid in ids if eid in self.entries]

    def associate(self, entry_id: str) -> list[KnowledgeEntry]:
        entry = self.entries.get(entry_id)
        if entry is None:
            return []
        related_ids: set[str] = set()
        for tag in entry.tags:
            for eid in self.inverted_index.get(tag, []):
                if eid != entry_id:
                    related_ids.add(eid)
        return [self.entries[eid] for eid in related_ids if eid in self.entries]


_knowledge_index: KnowledgeIndex | None = None


def get_index() -> KnowledgeIndex:
    global _knowledge_index
    if _knowledge_index is None:
        _knowledge_index = KnowledgeIndex()
    return _knowledge_index
