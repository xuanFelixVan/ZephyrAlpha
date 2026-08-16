# ZephyrAlpha 密钥管理文档（SECRETS.md）

> **文档类型**：治理文档（密钥管理显性化）
> **裁定来源**：[#ARCH-SECRETS-GOV-001](docs/_archive/ruling_secrets_governance_100pct_ai.md) 裁定 S-1
> **规则依据**：[TRAE-031](docs/01_policies_and_standards/rules/trae_031_security_key_access.yaml) SEC-001~SEC-006
> **配套注册表**：[secret_registry.yaml](config/secret_registry.yaml)（结构化密钥声明真源）
> **创建日期**：2026-08-04
> **维护者**：AI Architect（100% AI 开发场景下的显性化治理）

---

## 0. 为什么有这个文档？

ZephyrAlpha 是 **100% AI 开发** 项目。AI 每次会话都是"冷启动"，无法像人类工程师那样记住"项目有哪些密钥、放哪里、怎么读"。本文档解决这个**可知性问题**——AI 读完此文档即可知道密钥管理的全貌。

**一句话总结**：密钥放 `.env` 文件（已 gitignore），用 `secrets.py` 接口读取，禁止裸 `os.getenv`。新增密钥三步走（加 KEY → 更新 .env.example → 更新 registry）。

---

## 1. 密钥文件分布（6 个文件，74 个 KEY）

```
ZephyrAlpha/
├── .env                          ← 第三方 API token + 运行时密钥（自动加载）
├── .env.example                  ← .env 的模板（不含实际值）
├── SECURITY.md                   ← 漏洞报告流程
├── SECRETS.md                    ← 本文档（密钥管理显性入口）
└── config/
    ├── .env.postgres             ← PostgreSQL 凭证（depgraph 数据库）
    ├── .env.clickhouse           ← ClickHouse 凭证（行情数据库）
    ├── .env.redis                ← Redis 凭证（因子缓存）
    ├── .env.qmt                  ← QMT 量化交易终端
    ├── .env.ch_backup            ← ClickHouse 备份凭证（Hyper-V VM）
    └── secret_registry.yaml      ← 结构化密钥声明注册表
```

### 文件分工逻辑

| 文件 | 用途 | KEY 数 | 加载方式 | 读取接口 |
|---|---|---|---|---|
| `.env` | 第三方 API token、运行时密钥 | 38 | `zephyr/__init__.py` **自动加载**到 `os.environ` | `get_required_secret("KEY")` |
| `config/.env.postgres` | PostgreSQL 凭证 | 9 | **手动加载** | `get_service_secret("KEY", "postgres")` |
| `config/.env.clickhouse` | ClickHouse 凭证 | 10 | **手动加载** | `get_service_secret("KEY", "clickhouse")` |
| `config/.env.redis` | Redis 凭证 | 7 | **手动加载** | `get_service_secret("KEY", "redis")` |
| `config/.env.qmt` | QMT 交易终端 | 4 | **手动加载** | `get_service_secret("KEY", "qmt")` |
| `config/.env.ch_backup` | CH 备份凭证 | 6 | **手动加载** | `get_service_secret("KEY", "ch_backup")` |

> **注**：`get_service_secret()`（裁定 S-2，Phase 2-S2 已落地）按服务名便捷读取基础设施凭证，底层等价 `get_secret_from_file("KEY", "config/.env.{service}")`。

### 为什么分两个位置？

- **根目录 `.env`**：第三方 API token（DeepSeek/Tushare/百度网盘等），由 `zephyr/__init__.py` 在包导入时**自动加载**到 `os.environ`，全项目可直接 `get_required_secret()` 读取。
- **`config/.env.{service}`**：基础设施服务凭证（PostgreSQL/ClickHouse/Redis 等），**不自动加载**（避免基础设施凭证全量注入环境变量），需手动 `get_secret_from_file()` 或 `get_service_secret()` 读取。

### 已废弃文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `config/.env.restic` | 已废弃 | restic 替换为 robocopy /MIR，无 restic 依赖。此文件已删除；`F:\restic-zephyr` 目录待清理 |

---

## 2. 密钥读取规范（MUST 遵守）

### 2.1 读取接口决策树

```
读取密钥 →
├── 是第三方 API token（在 .env 中，自动加载）？
│   ├── 必需密钥  → get_required_secret("KEY")          # 缺失抛 SecretsError
│   └── 可选密钥  → get_secret_or_default("KEY", "默认值")  # 缺失返回默认值
│
├── 是基础设施凭证（在 config/.env.{service} 中）？
│   ├── 必需密钥  → get_service_secret("KEY", "postgres")     # 按服务名便捷读取
│   └── 可选密钥  → get_secret_from_file_or_default("KEY", "config/.env.postgres", "默认值")
│
└── 禁止 ⛔：
    ├── os.getenv("KEY")
    ├── os.environ.get("KEY")
    └── os.environ["KEY"]
```

### 2.2 接口清单（secrets.py）

| 函数 | 用途 | 示例 |
|---|---|---|
| `get_required_secret(key)` | 必需密钥，缺失抛异常 | `token = get_required_secret("TUSHARE_TOKEN")` |
| `get_secret_or_default(key, default)` | 可选密钥，缺失返回默认值 | `url = get_secret_or_default("DEEPSEEK_BASE_URL", "https://...")` |
| `get_secret_from_file(key, env_file)` | 从指定文件读（必需） | `pwd = get_secret_from_file("POSTGRES_PASSWORD", "config/.env.postgres")` |
| `get_secret_from_file_or_default(key, env_file, default)` | 从指定文件读（可选） | `host = get_secret_from_file_or_default("REDIS_HOST", "config/.env.redis", "localhost")` |
| `get_service_secret(key, service)` | 按服务名读基础设施凭证（必需） | `pwd = get_service_secret("POSTGRES_PASSWORD", "postgres")` |

### 2.3 禁止行为（三道 gate 阻断，#ARCH-SECRETS-GOV-001）

密钥治理有三道 commit-time in-process gate 硬阻断（`--no-verify` 无法绕过），覆盖"读密钥方式违规 / 新增密钥遗漏登记 / 密钥值硬编码"三个维度：

| gate_id（priority） | 检测内容 | 阻断场景 |
|---|---|---|
| `NO-BARE-GETENV`（81） | 裸 `os.getenv`/`os.environ.get`/`os.environ["KEY"]` 读密钥类 KEY | 读密钥**方式**违规（diff-aware：检测**新增+修改** .py 文件的 added 行，修改文件只检测 git diff 新增行，不触碰存量基线） |
| `SECRET-REGISTRY-CONSISTENCY`（127） | `.env.example` 与 `secret_registry.yaml` 的 KEY 不一致 | 新增密钥遗漏文档化（.env.example）或注册登记（registry） |
| `NO-SECRET-HARDCODE`（128） | 硬编码密钥值（`sk-`/`AKIA`/`ghp_`/`KEY="value"` 等），扫 .py/.yaml/.yml/.json/.toml | 密钥**值**硬编码到代码/配置 |

```python
# ✅ 正确
from zephyr.shared.security.secrets import get_required_secret
token = get_required_secret("TUSHARE_TOKEN")

# ⛔ 错误（NO-BARE-GETENV 阻断）——读密钥方式违规
import os
token = os.getenv("TUSHARE_TOKEN")        # 裸 getenv 读密钥
token = os.environ.get("TUSHARE_TOKEN")   # 裸 environ.get 读密钥
token = os.environ["TUSHARE_TOKEN"]       # 裸下标访问读密钥

# ⛔ 错误（NO-SECRET-HARDCODE 阻断）——密钥值硬编码
API_KEY = "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"   # OpenAI key 明文
password = "s3cret_pass"                          # password 明文赋值
```

> 三道 gate 豁免：`tests/`（测试）、`.env.example`（模板）、密钥扫描脚本自身、docstring/注释/import 行（.py）。误报通过豁免处理，gate 全部 fail-closed 硬阻断（100% AI 场景不用 warn-only）。

---

## 3. 新增密钥流程（3 步）

新增密钥时**必须**同步完成以下 3 步，否则 `secret_registry_consistency_gate`（裁定 S-3，Phase 2）会阻断提交：

### Step 1：加 KEY 到对应 .env 文件

```bash
# 第三方 API token → 根目录 .env
echo "NEW_API_KEY=你的实际密钥值" >> .env

# 基础设施凭证 → config/.env.{service}
echo "NEW_DB_PASSWORD=你的实际密码" >> config/.env.postgres
```

### Step 2：更新 .env.example（加占位 + 注释）

```bash
# .env.example 中添加（不含实际值）
echo "" >> .env.example
echo "# --- 新数据源 ---" >> .env.example
echo "NEW_API_KEY=" >> .env.example
```

### Step 3：更新 secret_registry.yaml（加结构化条目）

```yaml
# config/secret_registry.yaml 的 secrets 列表中添加
  - key: NEW_API_KEY
    service: new_service
    env_file: .env
    category: secret
    required: true
    description: "新数据源 API 密钥"
    obtain: "https://new-service.example.com/api-keys"
    rotation_days: 90
    since: "2026-08-04"
```

---

## 4. 密钥安全规范（TRAE-031 SEC-001~006 摘要）

| 规则 | 要求 | 现状 |
|---|---|---|
| SEC-001 | 禁止明文存储密钥（代码/配置/文档/日志/git） | ✅ .env 已 gitignore |
| SEC-002 | 密钥通过环境变量(.env)或密钥服务注入 | ✅ secrets.py 接口 |
| SEC-003 | .env 在 .gitignore | ✅ 已配置 |
| SEC-004 | 轮换周期：生产API 90天/DB 180天/开发 365天 | ⚠️ secret_rotation.py 已实现，未实际轮换 |
| SEC-005 | 密钥撤销（离职24h/下线7天/泄露立即） | ✅ N/A（无离职场景） |
| SEC-006 | 密钥强度：API≥256bit/DB≥16字符/JWT≥2048bit | ❌ 未强制校验（Phase 3） |

### 密钥泄露响应（SEC-LEAK-RESPONSE）

1. 立即撤销泄露的密钥
2. 生成新密钥并注入环境
3. 搜索泄露密钥出现过的所有文件，确认无残留
4. 通知所有使用该密钥的服务更新配置
5. 记录泄露事件（时间、范围、原因）
6. 7天内提交改进方案

---

## 5. 密钥分类说明

| category | 含义 | 保护级别 | 示例 |
|---|---|---|---|
| `secret` | 真正的密钥，不可日志输出 | 最高 | API_KEY, PASSWORD, TOKEN, HMAC_SECRET |
| `credential` | 凭证类（账号名），非纯密钥 | 中 | USERNAME, USER, ACCOUNT |
| `config` | 非密钥配置（host/port/url） | 最低 | HOST, PORT, BASE_URL, MODEL |

> `secret` 和 `credential` 类 KEY 必须通过 `secrets.py` 接口读取；`config` 类 KEY 虽非密钥，但建议也走 `secrets.py` 统一管理。

---

## 6. 存量违规整改记录（裁定 S-2，Phase 2-S2 已完成）

以下 9 处密钥类裸 `os.getenv` 调用已于 Phase 2-S2（2026-08-04）全部整改为 `secrets.py` 接口，密钥类裸 getenv 已清零。保留此表供历史追溯：

| 文件 | KEY | 整改方案 | 状态 |
|---|---|---|---|
| ifind_provider.py:227-228 | IFIND_USERNAME/PASSWORD | → `get_required_secret()` | ✅ 已整改 |
| deepseek_v4_chat.py:32 | DEEPSEEK_API_KEY | → `get_required_secret()` | ✅ 已整改 |
| ch_writer.py:74-75 | CLICKHOUSE_WRITER_USER/PASSWORD | → `get_service_secret()` | ✅ 已整改 |
| ch_config.py:113-171 | CLICKHOUSE_* | → `get_service_secret()` | ✅ 已整改 |
| redis_config.py:113-141 | REDIS_* | → `get_service_secret()` | ✅ 已整改 |
| environment_manager.py:50-83 | *_DB_CONN/*_BROKER_CONN | → `get_secret_or_default()` | ✅ 已整改 |
| gov_audit/writer.py:388 | ZEPHYR_AUDIT_HMAC_SECRET | → `get_required_secret()` | ✅ 已整改 |
| tamper_evident_log.py:37 | ZEPHYR_TAMPER_HMAC_SECRET | → `get_required_secret()` | ✅ 已整改 |

> 新增违规由 `NO-BARE-GETENV` gate（diff-aware，检测新增+修改文件 added 行）在 commit 阶段硬阻断，防止存量复发。

---

## 7. FAQ

### Q: 为什么不把所有密钥合并到一个文件？

**A**: 物理合并成本高、风险大、收益低。分文件的设计逻辑是：
- 根目录 `.env` 自动加载 → 第三方 API token 全项目可用
- `config/.env.{service}` 手动加载 → 基础设施凭证按需加载，不全量注入环境变量
- 合并后所有凭证全量注入 `os.environ`，增加泄露面

### Q: AI 如何快速知道某个 KEY 放哪里？

**A**: 查 `config/secret_registry.yaml`，按 `key` 搜索即可找到 `env_file` 字段。

### Q: 配置类变量（ZEPHYR_ENV/ZEPHYR_PROJECT_ROOT 等）为什么不在本 registry 中？

**A**: 本 registry 聚焦**密钥与凭证**。纯配置变量（非密钥）由 `infrastructure/config/app_config.py` 管理。`ZEPHYR_PROJECT_ROOT` 等运行时配置已登记在 registry 中（category=config），因为它们在 `.env` 文件中。

### Q: `os.environ.get("ZEPHYR_ENV")` 为什么不被 gate 阻断？

**A**: `ZEPHYR_ENV` 不匹配 `SECRET_INDICATOR_PATTERNS`（KEY/TOKEN/SECRET/PASSWORD/PASSWD/PWD/CREDENTIAL），且有专用 gate `zephyr_env_direct_access_gate` 检测应改用 `is_dev()`/`is_prod()` canonical 入口。

---

## 8. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-08-04 | 1.0.0 | 初始版本（裁定 S-1 Phase 1 施工）|
| 2026-08-04 | 1.1.0 | 同步 Phase 2-S2/S3/Phase 3 落地状态：§2.1 决策树清理 Phase 临时表述；§2.3 补全三道 gate（NO-BARE-GETENV diff-aware + SECRET-REGISTRY-CONSISTENCY + NO-SECRET-HARDCODE）；§6 标注 9 处存量违规已整改完成 |
