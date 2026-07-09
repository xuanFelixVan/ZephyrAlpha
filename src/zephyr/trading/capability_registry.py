# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_registry
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
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
# [A_module] module_id=MOD-ORC_capability_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CapabilityRegistry — 能力注册中心
==================================
蓝图: ARC-0001 §6.1
对标: Google A2A AgentCard + Anthropic MCP Tools + Cursor Rules
"""

import threading
from pathlib import Path
from typing import Any
import yaml

from zephyr.trading.capability_card import CapabilityCard
from zephyr.shared.io.serialization import filter_dataclass_fields


class CapabilityRegistry:
    """能力注册中心——解决'AI 不知道有这个功能'的问题。

    对标:
      - Google A2A Agent Card: JSON 格式的能力自描述
      - Anthropic MCP: tools/list -> 列出所有可用工具
      - Cursor Rules: .cursor/rules/ 持久化上下文
    """

    def __init__(self, card_dir: Path | None = None) -> None:
        self._cards: dict[str, CapabilityCard] = {}
        self._lock = threading.Lock()
        self._card_dir = card_dir

    def register(self, card: CapabilityCard) -> None:
        with self._lock:
            if card.capability_id in self._cards:
                return
            self._cards[card.capability_id] = card
        if self._card_dir is not None:
            self._persist_card(card)

    def unregister(self, capability_id: str) -> None:
        with self._lock:
            self._cards.pop(capability_id, None)

    def discover(self, query: str) -> list[CapabilityCard]:
        q = query.lower()
        results: list[CapabilityCard] = []
        with self._lock:
            for card in self._cards.values():
                if q in card.name.lower() or q in card.description.lower():
                    results.append(card)
        return results

    def list_all(self) -> list[CapabilityCard]:
        with self._lock:
            return list(self._cards.values())

    def find_by_tags(self, tags: list[str]) -> list[CapabilityCard]:
        tag_set = set(t.lower() for t in tags)
        results: list[CapabilityCard] = []
        with self._lock:
            for card in self._cards.values():
                card_tags = set(t.lower() for t in card.tags)
                if tag_set & card_tags:
                    results.append(card)
        return results

    def get(self, capability_id: str) -> CapabilityCard | None:
        with self._lock:
            return self._cards.get(capability_id)

    def health_check_all(self) -> dict[str, bool]:
        with self._lock:
            return {cid: card.status == "ACTIVE" for cid, card in self._cards.items()}

    def dump_snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {cid: card.model_dump() for cid, card in self._cards.items()}

    def count(self) -> int:
        with self._lock:
            return len(self._cards)

    def _persist_card(self, card: CapabilityCard) -> None:
        if self._card_dir is None:
            return
        self._card_dir.mkdir(parents=True, exist_ok=True)
        path = self._card_dir / f"{card.capability_id}.yaml"
        data = card.model_dump(mode="json")
        path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")

    def load_from_dir(self) -> int:
        if self._card_dir is None or not self._card_dir.exists():
            return 0
        count = 0
        for path in self._card_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                card = CapabilityCard(**filter_dataclass_fields(CapabilityCard, data))
                with self._lock:
                    if card.capability_id not in self._cards:
                        self._cards[card.capability_id] = card
                count += 1
            except Exception:
                continue
        return count
