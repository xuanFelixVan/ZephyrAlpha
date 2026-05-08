from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class PriceEntry:
    model: str
    input_per_1k: float
    output_per_1k: float
    provider: str
    updated_at: float = field(default_factory=time.time)


class PricingSync:
    def __init__(self, pricing_path: str = "config/model_pricing.yaml"):
        self._pricing_path = Path(pricing_path)
        self._prices: dict[str, PriceEntry] = {}
        self._load()

    def _load(self) -> None:
        if self._pricing_path.exists():
            with open(self._pricing_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                for model_name, cfg in data.items():
                    self._prices[model_name] = PriceEntry(
                        model=model_name,
                        input_per_1k=cfg.get("input_price", 0.0),
                        output_per_1k=cfg.get("output_price", 0.0),
                        provider=cfg.get("provider", "unknown"),
                    )

    def _save(self) -> None:
        data = {
            m: {
                "input_price": p.input_per_1k,
                "output_price": p.output_per_1k,
                "provider": p.provider,
                "updated_at": p.updated_at,
            }
            for m, p in self._prices.items()
        }
        with open(self._pricing_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def update_price(self, model: str, input_price: float, output_price: float, provider: str) -> PriceEntry:
        entry = PriceEntry(model=model, input_per_1k=input_price, output_per_1k=output_price, provider=provider)
        self._prices[model] = entry
        self._save()
        return entry

    def get_price(self, model: str) -> PriceEntry | None:
        return self._prices.get(model)

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        entry = self._prices.get(model)
        if entry is None:
            return 0.0
        return (input_tokens / 1000) * entry.input_per_1k + (output_tokens / 1000) * entry.output_per_1k

    def all_models(self) -> list[str]:
        return list(self._prices.keys())

    def providers(self) -> list[str]:
        return list({p.provider for p in self._prices.values()})
