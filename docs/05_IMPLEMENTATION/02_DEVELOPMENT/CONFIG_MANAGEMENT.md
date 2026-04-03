---
module_id: IMPL_CONFIG_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 配置管理系统

> 基础设施�? 集中式配置、动态更新、版本控�?

---

## 1. 设计概述

配置管理系统提供集中式配置存储、动态更新和版本控制功能�?

```
配置管理架构
├── 配置存储�?(Config Storage)
�?  ├── 本地文件存储
�?  ├── 远程配置中心 (etcd/consul)
�?  └── 环境变量
├── 配置加载�?(Config Loader)
�?  ├── YAML加载�?
�?  ├── JSON加载�?
�?  └── 环境变量加载�?
├── 配置验证�?(Config Validator)
�?  ├── 类型验证
�?  ├── 范围验证
�?  └── 依赖验证
├── 动态更新层 (Config Updater)
�?  ├── 热更新机�?
�?  ├── 变更通知
�?  └── 回滚机制
└── 版本控制�?(Config Versioning)
    ├── 配置变更历史
    ├── 配置快照
    └── 配置回滚
```

---

## 2. 核心实现

### 2.1 配置数据结构

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import yaml
import json
import os


class ConfigScope(Enum):
    """配置作用�?""
    SYSTEM = "system"
    MODULE = "module"
    STRATEGY = "strategy"
    USER = "user"


@dataclass
class ConfigItem:
    """配置�?""
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
    """配置变更记录"""
    change_id: str
    key: str
    old_value: Any
    new_value: Any
    changed_at: datetime
    changed_by: str
    reason: str = ""


class ConfigManager:
    """配置管理�?""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        self.configs: Dict[str, ConfigItem] = {}
        self.change_history: List[ConfigChange] = []
        self.subscribers: Dict[str, List[Callable]] = {}

        self._load_all_configs()

    def _load_all_configs(self):
        """加载所有配置文�?""
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
        """从字典加载配�?""
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
        """获取配置�?""
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
        """设置配置�?""
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
        """订阅配置变更"""
        if key not in self.subscribers:
            self.subscribers[key] = []

        self.subscribers[key].append(callback)

    def _notify_change(self, key: str, old_value: Any, new_value: Any):
        """通知配置变更"""
        callbacks = self.subscribers.get(key, [])

        for callback in callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                print(f"Callback error: {e}")

    def validate(self, key: str, value: Any) -> tuple:
        """验证配置�?""
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
        """获取所有配�?""
        if scope:
            return {
                k: v.value
                for k, v in self.configs.items()
                if v.scope == scope
            }

        return {k: v.value for k, v in self.configs.items()}

    def export(self, path: str):
        """导出配置到文�?""
        data = self.get_all()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def get_change_history(
        self,
        key: str = None,
        limit: int = 100
    ) -> List[ConfigChange]:
        """获取变更历史"""
        history = self.change_history

        if key:
            history = [c for c in history if c.key == key]

        return history[-limit:]

    def rollback(self, key: str, version: int = None) -> bool:
        """回滚配置"""
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

## 3. 预定义配置模�?

```python
class ConfigTemplates:
    """配置模板"""

    @staticmethod
    def get_system_config() -> Dict:
        """系统配置模板"""
        return {
            "system": {
                "name": "清风量化交易系统",
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
        """因子配置模板"""
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
        """数据源配置模�?""
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

## 4. 使用示例

```python
def example_config_manager():
    """配置管理使用示例"""

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

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: 基础设施�?(横切关注�?
**索引**: BLUEPRINTS.md �?基础设施蓝图
**上游接口**: 系统启动
**下游接口**: 所有模�?(M01-M15)
