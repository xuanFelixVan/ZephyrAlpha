"""
清风量化交易系统 v5.1
主入口

使用方式:
    1. 模块方式 (推荐): python -m src.main
    2. 直接运行: python src/main.py (需设置 PYTHONPATH)
    3. 安装后运行: pip install -e . && python -m src.main
"""
import sys
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.base import Result, Signal, Order, Position
from src.core.exceptions import SystemException


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    配置系统日志

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger("QingFengQuant")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载系统配置

    Args:
        config_path: 配置文件路径，默认为 config/system.yaml

    Returns:
        Dict[str, Any]: 配置字典

    Raises:
        SystemException: 配置文件不存在或格式错误
    """
    logger = logging.getLogger("QingFengQuant")

    if config_path is None:
        config_path = project_root / "config" / "system.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        logger.warning(f"配置文件不存在: {config_path}")
        logger.info("使用默认配置")
        return {
            "version": "5.1.0",
            "log_level": "INFO",
            "modules": {
                "factor_calculator": {"enabled": True},
                "risk_manager": {"enabled": True},
                "alert_manager": {"enabled": True}
            }
        }

    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info(f"成功加载配置文件: {config_path}")
        return config

    except Exception as e:
        logger.error(f"配置文件加载失败: {e}")
        raise SystemException(f"配置文件加载失败: {e}")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置有效性

    Args:
        config: 配置字典

    Returns:
        bool: 配置是否有效

    Raises:
        SystemException: 配置验证失败
    """
    logger = logging.getLogger("QingFengQuant")

    required_fields = ["version"]
    for field in required_fields:
        if field not in config:
            logger.error(f"配置缺少必需字段: {field}")
            raise SystemException(f"配置缺少必需字段: {field}")

    if "modules" in config:
        enabled_modules = [name for name, settings in config["modules"].items()
                          if settings.get("enabled", False)]
        logger.info(f"已启用模块: {', '.join(enabled_modules)}")

    logger.info("配置验证通过")
    return True


def initialize_system(config: Dict[str, Any]) -> Result:
    """
    初始化系统

    Args:
        config: 系统配置

    Returns:
        Result: 初始化结果
    """
    logger = logging.getLogger("QingFengQuant")
    logger.info("开始初始化系统...")

    try:
        version = config.get("version", "unknown")
        logger.info(f"系统版本: {version}")

        modules_status = {
            "factor_calculator": "✅ 已实现",
            "risk_manager": "✅ 已实现",
            "alert_manager": "✅ 已实现",
            "data_collector": "🔄 规划中",
            "strategy_engine": "🔄 规划中",
            "trade_executor": "🔄 规划中"
        }

        logger.info("系统模块状态:")
        for module, status in modules_status.items():
            logger.info(f"  {status} {module}")

        logger.info("系统初始化完成")
        return Result(success=True, data={"version": version, "modules": modules_status})

    except Exception as e:
        logger.error(f"系统初始化失败: {e}")
        logger.error(traceback.format_exc())
        return Result(success=False, error=str(e))


def main(config_path: Optional[str] = None) -> Result:
    """
    主入口

    Args:
        config_path: 配置文件路径，可选

    Returns:
        Result: 执行结果
    """
    logger = None

    try:
        logger = setup_logging()
        logger.info("=" * 60)
        logger.info("清风量化交易系统 v5.1")
        logger.info("=" * 60)

        config = load_config(config_path)
        validate_config(config)

        log_level = config.get("log_level", "INFO")
        logger = setup_logging(log_level)

        result = initialize_system(config)

        logger.info("系统启动完成")
        logger.info("详见: docs/System_Manifest.md")

        return result

    except SystemException as e:
        if logger:
            logger.error(f"系统异常: {e}")
        return Result(success=False, error=str(e))

    except KeyboardInterrupt:
        if logger:
            logger.info("用户中断，系统退出")
        return Result(success=True, data={"message": "用户中断"})

    except Exception as e:
        if logger:
            logger.error(f"未预期的错误: {e}")
            logger.error(traceback.format_exc())
        return Result(success=False, error=f"未预期的错误: {e}")


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.success else 1)
