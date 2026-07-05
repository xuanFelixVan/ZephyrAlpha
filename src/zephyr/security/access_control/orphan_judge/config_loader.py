# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §5.1
# [MODULE] zephyr.security.access_control.orphan_judge.config_loader
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.models
# [CONSUMERS] orphan-judge.judge.OrphanJudge; 各checker初始化
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] OrphanJudgeConfig是配置SSoT; 不修改任何源文件
# [MODIFY-GUARD] 修改默认值必须同步blueprint.md §5.1; 修改YAML schema必须同步此处
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAMLError on bad config file; 返回默认配置
# [TESTS] tests/orphan-judge/test_config_loader.py
# [A_module] module_id=MOD-SEC_config_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from zephyr.security.access_control.orphan_judge.models import OrphanJudgeConfig

logger = logging.getLogger(__name__)

__all__ = ["ConfigLoader"]

_DEFAULT_CONFIG_PATH = "data/asset_index/orphan_judge_config.yaml"


class ConfigLoader:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self._path = Path(config_path) if config_path else Path(_DEFAULT_CONFIG_PATH)
        self._config: OrphanJudgeConfig | None = None

    def load(self) -> OrphanJudgeConfig:
        if self._config is not None:
            return self._config

        if self._path.exists():
            try:
                data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self._config = OrphanJudgeConfig(**data)
                    logger.info("Config loaded from %s", self._path)
                    return self._config
            except Exception as exc:
                logger.warning("Failed to load config from %s: %s — using defaults", self._path, exc)

        self._config = OrphanJudgeConfig()
        logger.info("Using default config")
        return self._config

    def save(self, config: OrphanJudgeConfig | None = None) -> None:
        cfg = config or self._config or OrphanJudgeConfig()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            yaml.safe_dump(cfg.model_dump(), default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    @property
    def config(self) -> OrphanJudgeConfig:
        return self.load()

    def reload(self) -> OrphanJudgeConfig:
        self._config = None
        return self.load()
