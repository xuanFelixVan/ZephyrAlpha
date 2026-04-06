---
module_id: IMPL_CONFIG_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕ­ﮔﮔ۰۲ﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 回测系统
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔ ﮒ
applicable_scope: ﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻛﺕﻠ۷ﻝﺛ?
compliance_level: ﮒﮒ۶ﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻠﻝﺛ؟ﻝ؟۰ﻝﻝﺏﭨﻝﭨ

> ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ? ﻠﻛﺕ­ﮒﺙﻠﻝﺛ؟ﻙﮒ۷ﮔﮔﺑﮔﺍﻙﻝﮔ؛ﮔ۶ﮒ?

---

## 1. ﻟ؟ﺝﻟ؟۰ﮔ۵ﻟﺟﺍ

ﻠﻝﺛ؟ﻝ؟۰ﻝﻝﺏﭨﻝﭨﮔﻛﺝﻠﻛﺕ­ﮒﺙﻠﻝﺛ؟ﮒ­ﮒ۷ﻙﮒ۷ﮔﮔﺑﮔﺍﮒﻝﮔ؛ﮔ۶ﮒﭘﮒﻟﺛﻙ?

```
ﻠﻝﺛ؟ﻝ؟۰ﻝﮔﭘﮔ
ﻗﻗﻗ ﻠﻝﺛ؟ﮒ­ﮒ۷ﮒﺎ?(Config Storage)
ﻗ?  ﻗﻗﻗ ﮔ؛ﮒﺍﮔﻛﭨﭘﮒ­ﮒ۷
ﻗ?  ﻗﻗﻗ ﻟﺟﻝ۷ﻠﻝﺛ؟ﻛﺕ­ﮒﺟ (etcd/consul)
ﻗ?  ﻗﻗﻗ ﻝﺁﮒ۱ﮒﻠ
ﻗﻗﻗ ﻠﻝﺛ؟ﮒ ﻟﺛﺛﮒﺎ?(Config Loader)
ﻗ?  ﻗﻗﻗ YAMLﮒ ﻟﺛﺛﮒ?
ﻗ?  ﻗﻗﻗ JSONﮒ ﻟﺛﺛﮒ?
ﻗ?  ﻗﻗﻗ ﻝﺁﮒ۱ﮒﻠﮒ ﻟﺛﺛﮒ?
ﻗﻗﻗ ﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺎ?(Config Validator)
ﻗ?  ﻗﻗﻗ ﻝﺎﭨﮒﻠ۹ﻟﺁ
ﻗ?  ﻗﻗﻗ ﻟﮒﺑﻠ۹ﻟﺁ
ﻗ?  ﻗﻗﻗ ﻛﺝﻟﭖﻠ۹ﻟﺁ
ﻗﻗﻗ ﮒ۷ﮔﮔﺑﮔﺍﮒﺎ (Config Updater)
ﻗ?  ﻗﻗﻗ ﻝ­ﮔﺑﮔﺍﮔﭦﮒ?
ﻗ?  ﻗﻗﻗ ﮒﮔﺑﻠﻝ۴
ﻗ?  ﻗﻗﻗ ﮒﮔﭨﮔﭦﮒﭘ
ﻗﻗﻗ ﻝﮔ؛ﮔ۶ﮒﭘﮒﺎ?(Config Versioning)
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﮔﺑﮒﮒﺎ
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﺟ،ﻝ۶
    ﻗﻗﻗ ﻠﻝﺛ؟ﮒﮔﭨ
```

---

## 2. ﮔ ﺕﮒﺟﮒ؟ﻝﺍ

### 2.1 ﻠﻝﺛ؟ﮔﺍﮔ؟ﻝﭨﮔ

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import yaml
import json
import os


class ConfigScope(Enum):
    """ﻠﻝﺛ؟ﻛﺛﻝ۷ﮒ?""
    SYSTEM = "system"
    MODULE = "module"
    STRATEGY = "strategy"
    USER = "user"


@dataclass
class ConfigItem:
    """ﻠﻝﺛ؟ﻠ۰?""
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
    """ﻠﻝﺛ؟ﮒﮔﺑﻟ؟ﺍﮒﺛ"""
    change_id: str
    key: str
    old_value: Any
    new_value: Any
    changed_at: datetime
    changed_by: str
    reason: str = ""


class ConfigManager:
    """ﻠﻝﺛ؟ﻝ؟۰ﻝﮒ?""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        self.configs: Dict[str, ConfigItem] = {}
        self.change_history: List[ConfigChange] = []
        self.subscribers: Dict[str, List[Callable]] = {}

        self._load_all_configs()

    def _load_all_configs(self):
        """ﮒ ﻟﺛﺛﮔﮔﻠﻝﺛ؟ﮔﻛﭨ?""
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
        """ﻛﭨﮒ­ﮒﺕﮒ ﻟﺛﺛﻠﻝﺛ?""
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
        """ﻟﺓﮒﻠﻝﺛ؟ﮒ?""
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
        """ﻟ؟ﺝﻝﺛ؟ﻠﻝﺛ؟ﮒ?""
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
        """ﻟ؟۱ﻠﻠﻝﺛ؟ﮒﮔﺑ"""
        if key not in self.subscribers:
            self.subscribers[key] = []

        self.subscribers[key].append(callback)

    def _notify_change(self, key: str, old_value: Any, new_value: Any):
        """ﻠﻝ۴ﻠﻝﺛ؟ﮒﮔﺑ"""
        callbacks = self.subscribers.get(key, [])

        for callback in callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                print(f"Callback error: {e}")

    def validate(self, key: str, value: Any) -> tuple:
        """ﻠ۹ﻟﺁﻠﻝﺛ؟ﮒ?""
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
        """ﻟﺓﮒﮔﮔﻠﻝﺛ?""
        if scope:
            return {
                k: v.value
                for k, v in self.configs.items()
                if v.scope == scope
            }

        return {k: v.value for k, v in self.configs.items()}

    def export(self, path: str):
        """ﮒﺁﺙﮒﭦﻠﻝﺛ؟ﮒﺍﮔﻛﭨ?""
        data = self.get_all()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def get_change_history(
        self,
        key: str = None,
        limit: int = 100
    ) -> List[ConfigChange]:
        """ﻟﺓﮒﮒﮔﺑﮒﮒﺎ"""
        history = self.change_history

        if key:
            history = [c for c in history if c.key == key]

        return history[-limit:]

    def rollback(self, key: str, version: int = None) -> bool:
        """ﮒﮔﭨﻠﻝﺛ؟"""
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

## 3. ﻠ۱ﮒ؟ﻛﺗﻠﻝﺛ؟ﮔ۷۰ﮔ?

```python
class ConfigTemplates:
    """ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""

    @staticmethod
    def get_system_config() -> Dict:
        """ﻝﺏﭨﻝﭨﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""
        return {
            "system": {
                "name": "ﮔﺕﻠ۲ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ",
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
        """ﮒ ﮒ­ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ"""
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
        """ﮔﺍﮔ؟ﮔﭦﻠﻝﺛ؟ﮔ۷۰ﮔ?""
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

## 4. ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ

```python
def example_config_manager():
    """ﻠﻝﺛ؟ﻝ؟۰ﻝﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ"""

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

**ﻝﮔ؛**: 1.0
**ﮔﺑﮔﺍ**: 2026-03-28
**Layer**: ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(ﮔ۷۹ﮒﮒﺏﮔﺏ۷ﻝ?
**ﻝﺑ۱ﮒﺙ**: BLUEPRINTS.md ﻗ?ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﻟﮒﺝ
**ﻛﺕﮔﺕﺕﮔ۴ﮒ۲**: ﻝﺏﭨﻝﭨﮒﺁﮒ۷
**ﻛﺕﮔﺕﺕﮔ۴ﮒ۲**: ﮔﮔﮔ۷۰ﮒ?(M01-M15)
