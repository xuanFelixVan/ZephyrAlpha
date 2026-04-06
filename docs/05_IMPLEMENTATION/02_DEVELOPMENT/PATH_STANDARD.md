---
module_id: IMPL_DEV_PATH_STD_001
version: 1.0.1
status: Stable
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构�?
responsibility:
  - 因子计算
  - 交易执行
  - 回测系统
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 已完�?---


# 路径处理规范 (PATH_STANDARD.md)
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> 本文档定义了清风量化交易系统4.0的路径处理标准，包括命名规范、路径格式、跨平台兼容性等�?
>
> **版本**：v1.0
> **更新日期**�?026-04-02

---

## 1. 命名规范

### 1.1 目录命名

| 规范 | 要求 | 示例 |
|------|------|------|
| 编号前缀 | 使用2位数�?| `00_`, `01_`, `02_` |
| 英文命名 | 小写字母+下划�?| `factor_library`, `trading_tactics` |
| 避免中文 | 跨平台兼容性问�?| �?避免使用中文目录�?|
| 禁止空格 | 路径中无空格 | �?避免 `my docs` |

### 1.2 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Markdown | 英文命名或中�?英文编号 | `factor_definition.md` �?`T.01.TR001.趋势跟踪.md` |
| 代码文件 | 英文命名 | `backtest_engine.py` |
| 配置文件 | `snake_case.yaml` | `system_config.yaml` |
| 数据文件 | 包含日期后缀 | `data_20260328.csv` |

### 1.3 命名转换规则

```python
# 中文文件名在跨平台时需要转�?
中文文件�?�?英文/拼音文件�?

示例�?
T.00.MR001.市场趋势识别.md
    �?T.00.MR001.Market_Trend_Recognition.md

量化策略框架_v3.1.md
    �?quantitative_strategy_framework_v3_1.md
```

---

## 2. 路径格式

### 2.1 相对路径 vs 绝对路径

| 场景 | 推荐格式 | 示例 |
|------|----------|------|
| 文档内部链接 | 相对路径 | `[README](./README.md)` |
| 配置文件 | 相对项目�?| `config/system.yaml` |
| 代码引用 | Python import路径 | `from src.core.base import Result` |
| 外部引用 | 绝对路径(慎用) | `D:\project\config\secrets.yaml` |

### 2.2 路径分隔�?

```python
# Windows
path = r"D:\清风量化交易系统4.0\docs"

# Linux/Mac
path = "/home/user/quant_system_v4/docs"

# Python (推荐跨平�?
from pathlib import Path
path = Path("docs") / "01_FRAMEWORK" / "README.md"
```

### 2.3 路径规范

```python
# �?正确：使�?pathlib
from pathlib import Path

# 项目根目�?
PROJECT_ROOT = Path(__file__).parent.parent

# 文档目录
DOCS_DIR = PROJECT_ROOT / "docs"

# 配置文件
CONFIG_DIR = PROJECT_ROOT / "ZephyrAlpha" / "config"

# 组合路径
config_path = CONFIG_DIR / "system.yaml"

# �?错误：硬编码路径
config_path = "D:\\清风量化交易系统4.0\\ZephyrAlpha\\config\\system.yaml"
```

---

## 3. 跨平台兼容�?

### 3.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 中文路径乱码 | Windows中文编码 | 避免中文路径 |
| 路径大小�?| Linux区分大小�?| 统一小写命名 |
| 分隔符差�?| `\` vs `/` | 使用 pathlib |
| 特殊字符 | 部分系统不支�?| 避免 `:*?"<>\|` |

### 3.2 编码处理

```python
# 处理中文路径
import os

# Windows
path_with_chinese = r"D:\清风量化\文档"

# 转为UTF-8
normalized_path = os.fsdecode(os.fsencode(path_with_chinese))

# 或使�?pathlib (Python 3.6+)
from pathlib import Path
path = Path(path_with_chinese)
```

### 3.3 Git路径配置

```bash
# .gitattributes 设置换行�?
* text=auto

# 强制UTF-8编码
*.md text encoding=utf-8
*.py text encoding=utf-8
```

---

## 4. 路径使用规范

### 4.1 文档内链�?

```markdown
<!-- �?正确：相对路�?-->
[回到首页](./README.md)
[策略池](../../03_TRADING_TACTICS/INDEX.md)

<!-- �?正确：目录层级引�?-->
[上级目录](../../03_TRADING_TACTICS/INDEX.md)

<!-- �?错误：绝对路径（不可移植�?-->
[D:\项目\docs\INDEX.md](../../03_TRADING_TACTICS/INDEX.md)
```

### 4.2 Python路径引用

```python
# �?正确：相对导�?
from src.core.base import Result
from src.modules.factor import FactorCalculator

# �?正确：路径拼�?
from pathlib import Path

def get_data_path(stock_code: str) -> Path:
    return Path("data") / "stocks" / f"{stock_code}.csv"

# �?错误：sys.path操作
import sys
sys.path.insert(0, "D:\\project\\src")
```

### 4.3 配置文件中路�?

```yaml
# �?config/system.yaml
paths:
  data_dir: "data"
  log_dir: "logs"
  config_dir: "config"

# �?错误：硬编码绝对路径
data_dir: "D:\\清风量化交易系统4.0\\data"
```

---

## 5. 临时文件与缓�?

### 5.1 临时文件目录

| 目录 | 用�?| 清理策略 |
|------|------|----------|
| `temp/` | 临时计算结果 | 每次运行前清�?|
| `cache/` | 缓存数据 | 定期清理(7�? |
| `__pycache__/` | Python字节�?| 不提交到版本控制 |

### 5.2 清理规范

```python
# temp 目录使用后清�?
import shutil
from pathlib import Path

def cleanup_temp():
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir()
```

---

## 6. 检查清�?

### 6.1 新建文件前检�?

- [ ] 文件名是否使用英文？
- [ ] 是否避免空格和特殊字符？
- [ ] 是否遵循命名规范�?
- [ ] 是否使用合适的文件扩展名？

### 6.2 路径引用检�?

- [ ] 是否使用相对路径而非绝对路径�?
- [ ] 是否使用 `pathlib` 而非字符串拼接？
- [ ] 是否避免硬编码路径？
- [ ] 文档内链接是否正确？

---

## 附录: 相关文档

| 文档 | 说明 |
|------|------|
| `CODE_QUALITY.md` | 代码质量标准 |
| `CONFIG_STANDARD.md` | 配置文件标准 |
| `SECURITY.md` | 安全规范 |

---

**版本**: v1.0
**最后更�?*: 2026-03-28
