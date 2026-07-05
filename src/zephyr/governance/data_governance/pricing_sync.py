# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.data_governance.pricing_sync
# [DOMAIN] D_GOVERNANCE
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
# [A_module] module_id=MOD-RES_pricing_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


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
            with open(self._pricing_path, encoding="utf-8") as f:
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
        tmp_path = f"{self._pricing_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            os.replace(tmp_path, str(self._pricing_path))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

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

    def sync_from_litellm(self, litellm_json_path: str = "") -> int:
        if not litellm_json_path:
            _candidates = [
                Path.home() / ".cache" / "litellm" / "model_prices_and_context_window.json",
                REPO_ROOT / "data" / "litellm_prices.json",
            ]
            for c in _candidates:
                if c.exists():
                    litellm_json_path = str(c)
                    break
        if not litellm_json_path or not Path(litellm_json_path).exists():
            logger.warning("PricingSync: LiteLLM price file not found, skip sync")
            return 0
        try:
            with open(litellm_json_path, encoding="utf-8") as f:
                litellm_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("PricingSync: failed to load LiteLLM prices: %s", e)
            return 0
        updated = 0
        for model_key, info in litellm_data.items():
            if not isinstance(info, dict):
                continue
            input_price = info.get("input_cost_per_token", 0.0)
            output_price = info.get("output_cost_per_token", 0.0)
            # 5.50.1 修复：原 == 0.0 浮点精确比较，与同文件 L134 的 abs()>1e-8 风格不一致。
            # 改用容差比较，避免浮点残差导致哨兵值检测失败。
            if abs(input_price) < 1e-12 and abs(output_price) < 1e-12:
                continue
            input_per_1k = input_price * 1000
            output_per_1k = output_price * 1000
            provider = info.get("litellm_provider", "unknown")
            existing = self._prices.get(model_key)
            if (
                existing is None
                or abs(existing.input_per_1k - input_per_1k) > 1e-8
                or abs(existing.output_per_1k - output_per_1k) > 1e-8
            ):
                self._prices[model_key] = PriceEntry(
                    model=model_key,
                    input_per_1k=input_per_1k,
                    output_per_1k=output_per_1k,
                    provider=provider,
                )
                updated += 1
        if updated > 0:
            self._save()
            logger.info("PricingSync: synced %d model prices from LiteLLM", updated)
        return updated
