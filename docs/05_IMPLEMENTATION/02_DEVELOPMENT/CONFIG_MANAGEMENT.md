﻿---
module_id: IMPL_CONFIG_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕ­ﮔﮔ۰۲ﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔ ﮒ
applicable_scope: ﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻛﺕﻠ۷ﻝﺛ?
compliance_level: ﮒﮒ۶ﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---
---


# ﻠﻝﺛ؟ﻝ؟۰ﻝﻝﺏﭨﻝﭨ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ? ﻠﻛﺕ­ﮒﺙﻠﻝﺛ؟ﻙﮒ۷ﮔﮔﺑﮔﺍﻙﻝﮔ؛ﮔ۶ﮒ?

---

## 1. ﻟ؟ﺝﻟ؟۰ﮔ۵ﻟﺟﺍ

ﻠﻝﺛ؟ﻝ؟۰ﻝﻝﺏﭨﻝﭨﮔﻛﺝﻠﻛﺕ­ﮒﺙﻠﻝﺛ؟ﮒ­ﮒ۷ﻙﮒ۷ﮔﮔﺑﮔﺍﮒﻝﮔ؛ﮔ۶ﮒﭘﮒﻟﺛﻙ?

```
ﻠﻝﺛ؟ﻝ؟۰ﻝﮔﭘﮔ
ﻗﻗﻗ ﻠﻝﺛ؟ﮒ­ﮒ۷ﮒﺎ?(Config Storage)
ﻗ?  ﻗﻗﻗ ﮔ؛ﮒﺍﮔﻛﭨﭘﮒ­ﮒ۷
ﻗ?  ﻗﻗﻗ ﻟﺟﻝ۷ﻠﻝﺛ؟ﻛﺕ­ﮒﺟ (etcd/consul)
ﻗ?  ﻗﻗﻗ ﻝﺁﮒ۱ﮒﻠ
ﻗﻗﻗ ﻠﻝﺛ؟ﮒ ﻟﺛﺛﮒﺎ?(Config Loader)
ﻗ?  ﻗﻗﻗ YAMLﮒ ﻟﺛﺛﮒ?
ﻗ?  ﻗﻗﻗ JSONﮒ ﻟﺛﺛﮒ?
ﻗ?  ﻗﻗﻗ ﻝﺁﮒ۱ﮒﻠﮒ ﻟﺛﺛﮒ?
ﻗﻗﻗ ﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺎ?(Config Validator)
ﻗ?  ﻗﻗﻗ ﻝﺎﭨﮒﻠ۹ﻟﺁ
ﻗ?  ﻗﻗﻗ ﻟﮒﺑﻠ۹ﻟﺁ
ﻗ?  ﻗﻗﻗ ﻛﺝﻟﭖﻠ۹ﻟﺁ
ﻗﻗﻗ ﮒ۷ﮔﮔﺑﮔﺍﮒﺎ (Config Updater)
ﻗ?  ﻗﻗﻗ ﻝ­ﮔﺑﮔﺍﮔﭦﮒ?
ﻗ?  ﻗﻗﻗ ﮒﮔﺑﻠﻝ۴
ﻗ?  ﻗﻗﻗ ﮒﮔﭨﮔﭦﮒﭘ
ﻗﻗﻗ ﻝﮔ؛ﮔ۶ﮒﭘﮒﺎ?(Config Versioning)
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﮔﺑﮒﮒﺎ
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﺟ،ﻝ۶
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﮔﭨ
```

---

## 2. ﮔ ﺕﮒﺟﮒ؟ﻝﺍ

### 2.1 ﻠﻝﺛ؟ﮔﺍﮔ؟ﻝﭨﮔ

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import yaml
import json
import os


class ConfigScope(Enum):
    """ﻠﻝﺛ؟ﻛﺛﻝ۷ﮒ?""
    SYSTEM = "system"
    MODULE = "module"
    STRATEGY = "strategy"
    USER = "user"


@dataclass
class ConfigItem:
    """ﻠﻝﺛ؟ﻠ۰?""
    key: str
    value: Any
    scope: ConfigScope
    default_value: Any = None
    description: str = ""
    value_type: type = str
    validator: Optional[Callable] = None
    mutable: bool = True
    version: int = 1
    updated_at: datetime = field(default_factory=datetime.now)
    updated_by: str = "system"


@dataclass
class ConfigChange:
    """ﻠﻝﺛ؟ﮒﮔﺑﻟ؟ﺍﮒﺛ"""
    change_id: str
    key: str
    old_value: Any
    new_value: Any
    changed_at: datetime
    changed_by: str
    reason: str = ""


class ConfigManager:
    """ﻠﻝﺛ؟ﻝ؟۰ﻝﮒ?""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        self.configs: Dict[str, ConfigItem] = {}
        self.change_history: List[ConfigChange] = []
        self.subscribers: Dict[str, List[Callable]] = {}

        self._load_all_configs()

    def _load_all_configs(self):
        """ﮒ ﻟﺛﺛﮔﮔﻠﻝﺛ؟ﮔﻛﭨ?""
        system_config_path = os.path.join(self.config_dir, "system.yaml")

        if os.path.exists(system_config_path):
            with open(system_config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self._load_from_dict(data, ConfigScope.SYSTEM)

        data_source_path = os.path.join(self.config_dir, "data_sources.yaml")
        if os.path.exists(data_source_path):
            with open(data_source_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self._load_from_dict(data, ConfigScope.SYSTEM)

    def _load_from_dict(self, data: Dict, scope: ConfigScope):
        """ﻛﭨﮒ­ﮒﺕﮒ ﻟﺛﺛﻠﻝﺛ?""
        for key, value in data.items():
            if isinstance(value, dict):
                self._load_from_dict(value, scope)
            else:
                self.configs[key] = ConfigItem(
                    key=key,
                    value=value,
                    scope=scope
                )

    def get(self, key: str, default: Any = None) -> Any:
        """ﻟﺓﮒﻠﻝﺛ؟ﮒ?""
        item = self.configs.get(key)

        if item:
            return item.value

        return os.environ.get(key, default)

    def set(
        self,
        key: str,
        value: Any,
        scope: ConfigScope = ConfigScope.SYSTEM,
        reason: str = "",
        notify: bool = True
    ) -> bool:
        """ﻟ؟ﺝﻝﺛ؟ﻠﻝﺛ؟ﮒ?""
        old_item = self.configs.get(key)
        old_value = old_item.value if old_item else None

        new_item = ConfigItem(
            key=key,
            value=value,
            scope=scope,
            default_value=old_item.default_value if old_item else None,
            version=(old_item.version + 1) if old_item else 1,
            updated_at=datetime.now()
        )

        self.configs[key] = new_item

        self.change_history.append(ConfigChange(
            change_id=f"C{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            key=key,
            old_value=old_value,
            new_value=value,
            changed_at=datetime.now(),
            changed_by="system",
            reason=reason
        ))

        if notify:
            self._notify_change(key, old_value, value)

        return True

    def subscribe(self, key: str, callback: Callable):
        """ﻟ؟۱ﻠﻠﻝﺛ؟ﮒﮔﺑ"""
        if key not in self.subscribers:
            self.subscribers[key] = []

        self.subscribers[key].append(callback)

    def _notify_change(self, key: str, old_value: Any, new_value: Any):
        """ﻠﻝ۴ﻠﻝﺛ؟ﮒﮔﺑ"""
        callbacks = self.subscribers.get(key, [])

        for callback in callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                print(f"Callback error: {e}")

    def validate(self, key: str, value: Any) -> tuple:
        """ﻠ۹ﻟﺁﻠﻝﺛ؟ﮒ?""
        item = self.configs.get(key)

        if not item:
            return True, ""

        if item.validator:
            try:
                item.validator(value)
                return True, ""
            except Exception as e:
                return False, str(e)

        if item.value_type:
            if not isinstance(value, item.value_type):
                return False, f"Expected {item.value_type}, got {type(value)}"

        return True, ""

    def get_all(self, scope: ConfigScope = None) -> Dict[str, Any]:
        """ﻟﺓﮒﮔﮔﻠﻝﺛ?""
        if scope:
            return {
                k: v.value
                for k, v in self.configs.items()
                if v.scope == scope
            }

        return {k: v.value for k, v in self.configs.items()}

    def export(self, path: str):
        """ﮒﺁﺙﮒﭦﻠﻝﺛ؟ﮒﺍﮔﻛﭨ?""
        data = self.get_all()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def get_change_history(
        self,
        key: str = None,
        limit: int = 100
    ) -> List[ConfigChange]:
        """ﻟﺓﮒﮒﮔﺑﮒﮒﺎ"""
        history = self.change_history

        if key:
            history = [c for c in history if c.key == key]

        return history[-limit:]

    def rollback(self, key: str, version: int = None) -> bool:
        """ﮒﮔﭨﻠﻝﺛ؟"""
        if key not in self.configs:
            return False

        item = self.configs[key]

        if version and item.version == version:
            return False

        history = [c for c in self.change_history if c.key == key]

        if not history:
            return False

        target = history[-2] if len(history) > 1 else None

        if target:
            self.set(key, target.old_value, reason=f"Rollback to {target.change_id}")

        return True
```

---

## 3. ﻠ۱ﮒ؟ﻛﺗﻠﻝﺛ؟ﮔ۷۰ﮔ?

```python
class ConfigTemplates:
    """ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""

    @staticmethod
    def get_system_config() -> Dict:
        """ﻝﺏﭨﻝﭨﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""
        return {
            "system": {
                "name": "ﮔﺕﻠ۲ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ",
                "version": "4.0.0",
                "mode": "backtest",
                "log_level": "INFO"
            },
            "paths": {
                "data_dir": "./data",
                "log_dir": "./logs",
                "output_dir": "./output",
                "config_dir": "./config"
            },
            "defaults": {
                "initial_capital": 1000000,
                "commission_rate": 0.0003,
                "stamp_tax": 0.001
            }
        }

    @staticmethod
    def get_factor_config() -> Dict:
        """ﮒ ﮒ­ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""
        return {
            "factors": {
                "lookback_periods": [5, 10, 20, 60],
                "rebalance_frequency": "daily",
                "neutralization": ["industry", "size"]
            },
            "risk": {
                "max_position_pct": 0.15,
                "max_sector_pct": 0.30,
                "max_drawdown": 0.10
            }
        }

    @staticmethod
    def get_data_source_config() -> Dict:
        """ﮔﺍﮔ؟ﮔﭦﻠﻝﺛ؟ﮔ۷۰ﮔ?""
        return {
            "akshare": {
                "enabled": True,
                "priority": 1,
                "rate_limit": 10
            },
            "tushare": {
                "enabled": False,
                "token": "${TUSHARE_TOKEN}"
            },
            "ifind": {
                "enabled": False,
                "path": "${IFIND_PATH}"
            }
        }
```

---

## 4. ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ

```python
def example_config_manager():
    """ﻠﻝﺛ؟ﻝ؟۰ﻝﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ"""

    config = ConfigManager("./config")

    initial_capital = config.get("defaults.initial_capital", 1000000)
    print(f"Initial capital: {initial_capital}")

    def on_capital_change(key, old_value, new_value):
        print(f"Capital changed from {old_value} to {new_value}")

    config.subscribe("defaults.initial_capital", on_capital_change)

    config.set(
        "defaults.initial_capital",
        2000000,
        reason="Increase capital for more positions"
    )

    print(config.get_change_history("defaults.initial_capital"))
```

---

**ﻝﮔ؛**: 1.0
**ﮔﺑﮔﺍ**: 2026-03-28
**Layer**: ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(ﮔ۷۹ﮒﮒﺏﮔﺏ۷ﻝ?
**ﻝﺑ۱ﮒﺙ**: BLUEPRINTS.md ﻗ?ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﻟﮒﺝ
**ﻛﺕﮔﺕﺕﮔ۴ﮒ۲**: ﻝﺏﭨﻝﭨﮒﺁﮒ۷
**ﻛﺕﮔﺕﺕﮔ۴ﮒ۲**: ﮔﮔﮔ۷۰ﮒ?(M01-M15)
