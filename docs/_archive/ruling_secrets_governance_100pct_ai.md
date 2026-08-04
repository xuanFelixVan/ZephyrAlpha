---
ttl: permanent
rule_id: ARCH-SECRETS-GOV-001
related:
  - ARCH-GUC-TRIGGER-FIX-001
  - ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001
  - TRAE-031 (SEC-001~SEC-006 / SIR-001~004)
date: 2026-08-04
status: open (分析完成,治本施工方案待批准)
author: ZephyrAlpha AI Architect (客观第三方架构师视角)
---

# 架构裁定：100% AI 开发场景下的密钥治理加固

> **触发场景**：用户购买 Tushare 2000 积分后询问"项目里专门安全存放密钥和账户密码的地方是哪里"，暴露出密钥管理体系的可知性问题。
> **调研方法**：secrets.py 接口审计 + .env 文件普查 + bare_getenv_gate 检测盲区分析 + 73 处裸 getenv 调用分类 + TRAE-031 规则对照 + 第一性原理推导。

---

## 0. 摘要 (TL;DR)

**核心诊断**：项目密钥管理基础设施**已具备 80% 能力**（secrets.py 接口 + bare_getenv_gate + scan_secret_leak + TRAE-031 规则 + 7 个分服务 .env 文件），但在 100% AI 开发场景下存在**三个系统性缺口**：

1. **可知性缺口**（最严重）：无显性密钥管理文档，无结构化密钥注册表。AI 每次会话冷启动，无法知道"项目有哪些密钥、放哪里、怎么读"。SECURITY.md 仅一句话"使用 .env 和 .env.example"，形同虚设。
2. **可达性缺口**：secrets.py 缺少 config/.env.{service} 的便捷读取函数，导致 ch_config.py/redis_config.py 不得不写 `os.environ.get(...) or get_secret_from_file_or_default(..., path, ...)` 冗长模式，增加了违规诱因。
3. **可审计性缺口**：bare_getenv_gate 只检测**新增文件**（diff-filter=A）+ **字符串字面量参数**，存量 9 处真正的密钥类违规（含 IFIND_PASSWORD/DEEPSEEK_API_KEY/CLICKHOUSE_PASSWORD/*_DB_CONN 等）长期逍遥法外。

**核心裁定**：4 个子裁定，分 3 个 Phase 实施
- **裁定 S-1** (Phase 1, 本周)：显性化 —— 新增 SECRETS.md + secret_registry.yaml + 补全 .env.example
- **裁定 S-2** (Phase 2, 本月)：便捷化 —— secrets.py 新增 get_service_secret() + 整改 9 处密钥类违规
- **裁定 S-3** (Phase 2, 本月)：硬化检测 —— bare_getenv_gate 支持修改文件 + 新增 secret_registry 一致性 gate
- **裁定 S-4** (Phase 3, 长期)：pre-commit 密钥泄漏扫描 —— scan_secret_leak 轻量版前移

**现实证据**：用户购买的 TUSHARE_TOKEN 虽已写入 `.env` 并被 tushare_provider.py 正确用 `get_required_secret()` 读取，但**未在 .env.example 中文档化**——这正是"可知性缺口"的实时实例化。下一个 AI 会话不知道这个密钥存在，可能重复购买或遗漏配置。

---

## 1. 第一性原理分析

### 1.1 密钥管理的本质：可知性 + 可达性 + 可审计性

从第一性原理出发，密钥管理体系的本质是解决三个问题：

| 维度 | 本质问题 | 人类工程师场景 | 100% AI 场景 |
|---|---|---|---|
| **可知性** | AI 怎么知道项目有哪些密钥、放哪里？ | 工程师能记住"6 个 .env 文件 + 48 个 KEY" | AI 每次会话冷启动，只能靠文档/gate/代码约定 |
| **可达性** | AI 怎么合规地读取密钥？ | 工程师能判断"这个变量像密钥，该用 secrets.py" | AI 只能靠 SECRET_INDICATOR_PATTERNS 模式匹配，容易写裸 getenv |
| **可审计性** | 违规怎么被发现和阻断？ | code review 人工把关 | AI 高频操作，必须靠 gate 自动化检测 |

### 1.2 核心矛盾：基础设施为人类设计 vs 100% AI 开发现实

ZephyrAlpha 的密钥管理体系最初隐含假设人类工程师会：
- **主动文档化**新密钥（更新 .env.example）
- **主动判断**哪些变量是密钥（用 secrets.py 而非裸 getenv）
- **主动审查**代码中的违规（code review）

在 100% AI 开发场景下，这三个假设全部失效：
- AI 不会主动做"元工作"（meta-work）——完成任务即可，不会自发更新文档
- AI 的密钥判断靠模式匹配——SECRET_INDICATOR_PATTERNS 只覆盖 7 个模式（KEY/TOKEN/SECRET/PASSWORD/PASSWD/PWD/CREDENTIAL），漏判风险高
- AI 高频操作——人工 review 不可行，必须靠 gate

### 1.3 三层因果链

```
┌─────────────────────────────────────────────────────────────────┐
│ L1 最深层: 可知性缺口——无显性密钥文档/注册表                    │
│   根因: SECURITY.md 仅一句话, .env.example 是模板非注册表        │
│   症状: AI 冷启动不知道项目有哪些密钥, 新增密钥不文档化          │
│   实例: TUSHARE_TOKEN 已用但未进 .env.example                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓ 派生
┌─────────────────────────────────────────────────────────────────┐
│ L2 中间层: 可达性缺口——secrets.py 缺 config/.env.{service} 便捷 │
│   根因: 只有 get_secret_from_file(key, path) 需手动传路径        │
│   症状: ch_config.py 写 os.environ.get() or get_secret_from_    │
│         file_or_default(..., _CH_ENV_PATH, ...) 冗长模式         │
│   派生: 冗长模式增加违规诱因, AI 倾向直接裸 getenv              │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓ 派生
┌─────────────────────────────────────────────────────────────────┐
│ L3 表层: 可审计性缺口——bare_getenv_gate 检测盲区                │
│   根因: 只检测新增文件(diff-filter=A) + 字符串字面量参数         │
│   症状: 9 处密钥类存量违规长期存在(见 §3.2 清单)                 │
│   派生: 违规积累形成"破窗效应", 新 AI 模仿存量写法              │
└─────────────────────────────────────────────────────────────────┘
```

**关键洞察**：L1 是 L2/L3 的根因。不修 L1（显性化），AI 永远不知道正确做法是什么；不修 L2（便捷化），即使 AI 知道正确做法也倾向于走捷径；不修 L3（硬化检测），违规积累形成破窗效应。三者必须协同推进。

---

## 2. 调研结论汇总

### 2.1 基础设施现状（已有能力）

| 组件 | 路径 | 能力 | 成熟度 |
|---|---|---|---|
| **secrets.py** | src/zephyr/shared/security/secrets.py | SecretProvider 接口 + 5 个同步便捷函数 + SECRET_INDICATOR_PATTERNS + secret_rotation 集成 | ✅ production |
| **bare_getenv_gate** | src/zephyr/gov_enforcement/commit_gates/bare_getenv_gate.py | pre-commit 检测新增 .py 文件裸 getenv 读密钥 | ⚠️ 有盲区 |
| **zephyr_env_direct_access_gate** | src/zephyr/gov_enforcement/commit_gates/zephyr_env_direct_access_gate.py | 专检 ZEPHYR_ENV 直接访问 | ✅ production |
| **scan_secret_leak.py** | scripts/governance/d6_security/scan_secret_leak.py | 周扫描硬编码密钥正则匹配 | ⚠️ 非pre-commit |
| **secret_rotation.py** | src/zephyr/feedback_loop/security/secret_rotation.py | 密钥轮换调度 + configure_secret_rotation() 注入 | ✅ production |
| **TRAE-031 规则** | docs/01_policies_and_standards/rules/trae_031_security_key_access.yaml | SEC-001~006 + SIR-001~004 完整规则 | ✅ stable |
| **.env.example** | .env.example | 137 行模板，覆盖 AI/数据源/告警/审计/MCP | ⚠️ 缺 TUSHARE_TOKEN |
| **SECURITY.md** | SECURITY.md | 漏洞报告流程 + 一句话密钥约定 | ❌ 过于简略 |

### 2.2 密钥文件分布（7 个文件，约 30 个 KEY）

| 文件 | 用途 | KEY 数 | 加载方式 | .gitignore |
|---|---|---|---|---|
| `.env` (根目录) | 第三方 API token | 12 | zephyr/__init__.py 自动加载到 os.environ | ✅ 已忽略 |
| `config/.env.postgres` | PostgreSQL 凭证 | 5 | 手动 get_secret_from_file() | ✅ 已忽略 |
| `config/.env.clickhouse` | ClickHouse 凭证 | 4 | 手动 get_secret_from_file() | ✅ 已忽略 |
| `config/.env.redis` | Redis 凭证 | 3 | 手动 get_secret_from_file() | ✅ 已忽略 |
| `config/.env.qmt` | QMT 交易终端 | 3 | 手动 get_secret_from_file() | ✅ 已忽略 |
| `config/.env.ch_backup` | S3 备份凭证 | 3 | 手动 get_secret_from_file() | ✅ 已忽略 |
| `config/.env.restic` | Restic 备份 | 2 | 手动 get_secret_from_file() | ✅ 已忽略 |

**根目录 .env 当前 KEY 清单**（12 个）：DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, BDPAN_APP_ID, BDPAN_APP_KEY, BDPAN_SECRET_KEY, BDPAN_SIGN_KEY, BDPAN_ACCESS_TOKEN, BDPAN_REFRESH_TOKEN, IFIND_USERNAME, IFIND_PASSWORD, TUSHARE_TOKEN

### 2.3 TRAE-031 规则对照（已有规则 vs 现状差距）

| 规则 | 要求 | 现状 | 差距 |
|---|---|---|---|
| SEC-001 | 禁止明文存储密钥 | .env 已 gitignore，无硬编码 | ✅ 合规 |
| SEC-002 | 密钥通过环境变量/密钥服务注入 | .env + secrets.py | ✅ 合规 |
| SEC-003 | .env 在 .gitignore | ✅ 已配置 | ✅ 合规 |
| SEC-004 | 密钥轮换周期（生产90天/DB180天/开发365天） | secret_rotation.py 已实现 | ⚠️ 无生产环境，未实际轮换 |
| SEC-005 | 密钥撤销流程 | 无离职场景 | ✅ N/A |
| SEC-006 | 密钥强度标准 | 未强制校验 | ❌ 缺失 |
| **（隐含）可知性** | AI 能知道有哪些密钥 | 无显性文档/注册表 | ❌ **缺口** |
| **（隐含）可达性** | AI 能便捷合规读取 | 缺 config/.env.{service} 便捷函数 | ❌ **缺口** |
| enforcement.paired_gate_id | NO-BARE-GETENV | 已配对 | ⚠️ gate 有盲区 |

### 2.4 bare_getenv_gate 检测盲区分析

**当前检测逻辑**（bare_getenv_gate.py:233-260）：
1. `git diff --cached --diff-filter=A` → 只取**新增**文件
2. AST 解析，遍历 Call/Subscript 节点
3. `_extract_string_arg()` → 只提取**字符串字面量**参数
4. `_is_secret_key()` → 匹配 SECRET_INDICATOR_PATTERNS

**三个盲区**：
- **盲区1**：只检测新增文件，修改文件中的新增违规不检测 → 存量违规永远逍遥法外
- **盲区2**：只检测字符串字面量参数，`os.environ.get(key)` 变量参数不检测 → （设计权衡：secrets.py 自身用变量参数，无法区分）
- **盲区3**：SECRET_INDICATOR_PATTERNS 只 7 个模式，`IFIND_USERNAME`/`*_DB_CONN` 等不匹配 → 部分密钥类变量漏判

**设计权衡的合理性**：
- 盲区2 是合理权衡（无法区分 SSoT 实现和违规调用），不可消除
- 盲区1 和盲区3 可通过技术手段缓解（见 §4 裁定 S-3）

---

## 3. 裸 getenv 调用存量审计（精确分类）

### 3.1 审计方法

执行 `rg -n "os\.getenv\(|os\.environ\.get\(|os\.environ\[" --type py -g "!tests/**" -g "!**/secrets.py" -g "!**/bare_getenv_gate.py" -g "!**/zephyr_env_direct_access_gate.py"`，排除测试和 SSoT 实现，得到约 120 处调用。按**是否真正涉及密钥**分类：

### 3.2 真正的密钥类违规（9 处，P0 优先整改）

| # | 文件:行 | KEY | 风险 | 整改方案 |
|---|---|---|---|---|
| 1 | ifind_provider.py:227 | IFIND_USERNAME | 密钥裸读 | → get_required_secret() |
| 2 | ifind_provider.py:228 | IFIND_PASSWORD | 密钥裸读 | → get_required_secret() |
| 3 | deepseek_v4_chat.py:32 | DEEPSEEK_API_KEY | 密钥裸读 | → get_required_secret() |
| 4 | ch_writer.py:74-75 | CLICKHOUSE_WRITER_USER/PASSWORD | DB凭证裸读 | → get_service_secret() |
| 5 | environment_manager.py:50-83 | *_DB_CONN/*_BROKER_CONN | 连接串含密码 | → get_secret_or_default() |
| 6 | gov_audit/writer.py:388 | ZEPHYR_AUDIT_HMAC_SECRET | HMAC密钥裸读 | → get_required_secret() |
| 7 | tamper_evident_log.py:37 | ZEPHYR_TAMPER_HMAC_SECRET | HMAC密钥裸读 | → get_required_secret() |
| 8 | redis_config.py:113-141 | REDIS_HOST/PASSWORD 等 | 有fallback但先裸读 | → get_service_secret() |
| 9 | ch_config.py:113-171 | CLICKHOUSE_* 全部 | 有fallback但先裸读 | → get_service_secret() |

**补充**：test_deepseek_api.py:38 的 `DEEPSEEK_API_KEY` 在 scripts/construction/ 下，属于一次性测试脚本，优先级 P2。

### 3.3 配置类裸 getenv（约 100 处，非密钥，P2 规范化）

这些是 ZEPHYR_ENV/ZEPHYR_PROJECT_ROOT/ZEPHYR_SESSION_ID/OLLAMA_BASE_URL/DEEPSEEK_MODEL 等配置变量，**不是密钥**，但裸 getenv 不利于配置集中管理。包括：
- foundation/env.py（SSoT 实现，合理）
- pipeline/llm_gateway.py（模型配置，非密钥）
- gov_enforcement/*（运行时配置，非密钥）
- scripts/*（脚本配置，非密钥）

**裁定**：配置类裸 getenv 不属于密钥治理范围，不在本裁定整改 scope 内。但建议未来用 app_config.py 统一管理（已有 infrastructure/config/app_config.py 雏形）。

### 3.4 已合规的密钥读取（标杆案例）

- **tushare_provider.py:80** → `get_required_secret("TUSHARE_TOKEN")` ✅
- **secrets.py 自身** → 用变量参数 `os.environ.get(key)` ✅（SSoT 合理）

---

## 4. 裁定结果

基于第一性原理分析和调研，本裁定给出 4 个子裁定，分 3 个 Phase 实施：

### 裁定 S-1：显性化（Phase 1, 本周）—— 可知性治本

**问题**：AI 冷启动无法知道项目有哪些密钥、放哪里、怎么读。SECURITY.md 仅一句话，.env.example 是模板非注册表，无结构化密钥声明。

**治本方案**：

1. **新增 `config/SECRETS.md`**（显性密钥管理文档）：
   - 7 个密钥文件清单（路径/用途/KEY数/加载方式）
   - 密钥读取规范（MUST 用 secrets.py 接口，禁止裸 getenv）
   - 新增密钥流程（3 步：加 KEY 到 .env → 更新 .env.example → 更新 secret_registry.yaml）
   - 密钥文件分布图（根目录 .env vs config/.env.{service} 的分工逻辑）
   - 轮换流程（引用 TRAE-031 SEC-004）

2. **新增 `config/secret_registry.yaml`**（结构化密钥声明注册表）：
   ```yaml
   # 密钥声明注册表——项目所有密钥的结构化真源
   # 与 .env.example 双源对齐（gate 校验一致性）
   secrets:
     - key: TUSHARE_TOKEN
       service: tushare
       env_file: .env  # 根目录
       category: api_token
       required: true
       description: Tushare 数据源 API token（2000积分，¥200/年）
       obtain: https://tushare.pro/register → 个人主页 → API Token
       rotation_days: 365  # 开发环境
       since: 2026-08-04
     - key: DEEPSEEK_API_KEY
       service: deepseek
       env_file: .env
       # ...
     - key: POSTGRES_PASSWORD
       service: postgres
       env_file: config/.env.postgres
       category: db_credential
       required: true
       # ...
   ```

3. **补全 `.env.example`**：添加 TUSHARE_TOKEN 及其他缺失密钥

**预期效果**：
- AI 冷启动读 SECRETS.md 即可知道密钥全景
- secret_registry.yaml 提供结构化数据，可供 gate 校验、审计脚本消费
- 新增密钥有标准流程，不再遗漏文档化

### 裁定 S-2：便捷化（Phase 2, 本月）—— 可达性治本

**问题**：secrets.py 缺少 config/.env.{service} 便捷函数，导致 ch_config.py/redis_config.py 写冗长模式，增加违规诱因。

**治本方案**：

1. **secrets.py 新增 `get_service_secret(key, service, required=True)`**：
   ```python
   _SERVICE_ENV_FILES = {
       "postgres": "config/.env.postgres",
       "clickhouse": "config/.env.clickhouse",
       "redis": "config/.env.redis",
       "qmt": "config/.env.qmt",
       "ch_backup": "config/.env.ch_backup",
       "restic": "config/.env.restic",
   }

   def get_service_secret(key: str, service: str, required: bool = True) -> str:
       """从 config/.env.{service} 读取密钥（便捷函数）。

       优先级：os.environ > config/.env.{service} > default/异常
       """
       env_file = _SERVICE_ENV_FILES.get(service)
       if env_file is None:
           raise SecretsError(f"unknown service: {service}")
       if required:
           return get_secret_from_file(key, env_file)
       return get_secret_from_file_or_default(key, env_file, "")
   ```

2. **整改 9 处密钥类违规**（按 §3.2 清单）：
   - ifind_provider.py → `get_required_secret("IFIND_USERNAME")` / `get_required_secret("IFIND_PASSWORD")`
   - deepseek_v4_chat.py → `get_required_secret("DEEPSEEK_API_KEY")`
   - ch_writer.py → `get_service_secret("CLICKHOUSE_WRITER_USER", "clickhouse")` 等
   - ch_config.py → `get_service_secret("CLICKHOUSE_HOST", "clickhouse")` 等（消除冗长模式）
   - redis_config.py → `get_service_secret("REDIS_HOST", "redis")` 等
   - environment_manager.py → `get_secret_or_default("DEV_DB_CONN")` 等
   - gov_audit/writer.py → `get_required_secret("ZEPHYR_AUDIT_HMAC_SECRET")`
   - tamper_evident_log.py → `get_required_secret("ZEPHYR_TAMPER_HMAC_SECRET")`

**预期效果**：
- 密钥读取代码从 `os.environ.get() or get_secret_from_file_or_default(..., path, ...)` 简化为 `get_service_secret(key, service)`
- 消除违规诱因，AI 自然倾向用便捷函数
- 9 处存量违规清零

### 裁定 S-3：硬化检测（Phase 2, 本月）—— 可审计性治本

**问题**：bare_getenv_gate 只检测新增文件，存量违规逍遥法外；无 secret_registry 一致性校验。

**治本方案**：

1. **增强 bare_getenv_gate：支持修改文件的 diff-aware 检测**：
   - 当前：`git diff --cached --diff-filter=A`（只新增）
   - 增强：`git diff --cached --diff-filter=AM`（新增+修改），但只检测**修改文件中新增的行**（`git diff --cached -U0` 取 added lines），避免全文件扫描误报
   - 理由：修改文件中的新增违规应被检测，但已有违规（历史代码）不追溯

2. **新增 `secret_registry_consistency_gate`**（pre-commit）：
   - 检测 .env.example 与 secret_registry.yaml 的 KEY 一致性
   - .env.example 有但 registry 无 → 违规（未注册）
   - registry 有但 .env.example 无 → 违规（未文档化）
   - 强制 AI 新增密钥时同步更新两个文件

3. **扩展 SECRET_INDICATOR_PATTERNS**（可选，谨慎）：
   - 新增 `USERNAME`（覆盖 IFIND_USERNAME）、`CONN`（覆盖 *_DB_CONN）
   - 权衡：扩展模式可能增加误报，需评估

**预期效果**：
- 修改文件中的新增密钥类违规被阻断
- .env.example 与 secret_registry.yaml 保持一致
- 防止未来新增密钥未文档化

### 裁定 S-4：pre-commit 密钥泄漏扫描（Phase 3, 长期）—— 纵深防御

**问题**：scan_secret_leak.py 是周扫描脚本，AI 硬编码密钥提交后要等到周扫描才发现，已造成泄漏。

**治本方案**：

1. **新增 `detect_secrets_precommit.py`**（pre-commit 轻量版）：
   - 复用 scan_secret_leak.py 的 SECRET_PATTERNS_DEEP 正则
   - 只扫描 staged 文件（增量），不扫全库
   - P0 级发现（sk-/AKIA/ghp_ 等）硬阻断，P1 级 warn
   - 与 bare_getenv_gate 互补：bare_getenv 检测"读密钥方式违规"，detect_secrets 检测"密钥值硬编码"

2. **集成到 GitCommitGateway**：
   - 注册为 in-process gate（priority 待定，建议 82，在 NO-BARE-GETENV(81) 之后）
   - gate_id: `NO-SECRET-HARDCODE`

**预期效果**：
- 硬编码密钥在提交时被阻断，不等周扫描
- 与 bare_getenv_gate 形成双层防御：读密钥违规 + 密钥值硬编码

---

## 5. 实施路线图

| Phase | 裁定 | 工作量 | 优先级 | 依赖 |
|---|---|---|---|---|
| **Phase 1 (本周)** | S-1 显性化 | 1-2h（文档+注册表） | P0 | 无 |
| **Phase 2 (本月)** | S-2 便捷化 | 2-3h（接口+9处整改） | P1 | S-1 完成（registry 作为整改参照） |
| **Phase 2 (本月)** | S-3 硬化检测 | 2-3h（gate 增强+新gate） | P1 | S-1 完成（registry 一致性校验依赖 registry） |
| **Phase 3 (长期)** | S-4 密钥扫描前移 | 2h（pre-commit 脚本） | P2 | S-3 完成（gate 注册机制成熟） |

**关键路径**：S-1 → S-2/S-3（并行）→ S-4

---

## 6. 与现有治理体系的对齐

### 6.1 与 TRAE-031 的关系

本裁定**不替代** TRAE-031，而是**补强其执行层**：
- TRAE-031 定义"密钥管理应该怎么做"（规则层）
- 本裁定定义"AI 如何知道并遵守这些规则"（执行层 + 可知性层）
- TRAE-031 的 enforcement.paired_gate_id=NO-BARE-GETENV 已配对，本裁定增强该 gate 的检测能力

### 6.2 与 6 层闭环模型的对齐

| 层 | 现状 | 本裁定贡献 |
|---|---|---|
| ① 可知性 | ⚠️ 缺显性文档 | S-1 新增 SECRETS.md + registry |
| ② 可达性 | ⚠️ 缺便捷函数 | S-2 新增 get_service_secret() |
| ③ 可观察性 | ✅ scan_secret_leak 周扫描 | S-4 前移为 pre-commit |
| ④ 可逃生性 | ✅ get_secret_or_default 有默认值 | 无需改动 |
| ⑤ 可追溯性 | ✅ .env 在 .gitignore，secret_rotation 有日志 | 无需改动 |
| ⑥ 可预防性 | ⚠️ bare_getenv_gate 有盲区 | S-3 增强检测 + 新增一致性 gate |

### 6.3 与 100% AI 治理加固裁定（ruling_100pct_ai_governance_hardening.md）的关系

本裁定是 ruling_100pct_ai_governance_hardening.md 的**垂直深化**：
- 该裁定诊断 100% AI 场景下的**横向**治理失效（session/gate/阈值）
- 本裁定诊断 100% AI 场景下的**纵向**密钥治理失效（可知/可达/可审计）
- 两者共享同一第一性原理：**为人类设计的体系在 100% AI 场景下需要加固**

---

## 7. 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| secret_registry.yaml 与 .env.example 漂移 | 中 | 中 | S-3 一致性 gate 强制对齐 |
| get_service_secret() 误用 service 名 | 低 | 低 | _SERVICE_ENV_FILES 字典 fail-fast |
| bare_getenv_gate 增强（修改文件检测）误报 | 中 | 中 | 只检测 added lines，不追溯历史 |
| 9 处整改引入回归 | 低 | 中 | 逐处整改 + 单测验证 |
| SECRETS.md 过时（密钥增减未同步） | 中 | 中 | gate 强制 registry 更新 + 定期审计 |

---

## 8. 验收标准

### Phase 1 验收
- [ ] config/SECRETS.md 存在且包含 7 个文件清单 + 读取规范 + 新增流程
- [ ] config/secret_registry.yaml 存在且覆盖全部 ~30 个 KEY
- [ ] .env.example 包含 TUSHARE_TOKEN
- [ ] AI 冷启动读 SECRETS.md 能回答"项目有哪些密钥、放哪里、怎么读"

### Phase 2 验收
- [ ] secrets.py 新增 get_service_secret() + 单测
- [ ] 9 处密钥类违规全部整改（rg 搜索确认清零）
- [ ] bare_getenv_gate 支持 --diff-filter=AM + added lines 检测
- [ ] secret_registry_consistency_gate 注册并通过 smoke test
- [ ] .env.example 与 secret_registry.yaml 一致性 gate 通过

### Phase 3 验收
- [ ] detect_secrets_precommit.py 集成到 GitCommitGateway
- [ ] 硬编码密钥（sk-/AKIA/ghp_）提交被阻断
- [ ] smoke test 覆盖 P0 模式

---

## 9. 附录

### A. 密钥文件分布图

```
ZephyrAlpha/
├── .env                          ← 第三方 API token（12 KEY，自动加载）
├── .env.example                  ← 模板（待补全）
├── SECURITY.md                   ← 漏洞报告（待补强密钥章节）
└── config/
    ├── .env.postgres             ← PostgreSQL（5 KEY，手动加载）
    ├── .env.clickhouse           ← ClickHouse（4 KEY，手动加载）
    ├── .env.redis                ← Redis（3 KEY，手动加载）
    ├── .env.qmt                  ← QMT 交易终端（3 KEY，手动加载）
    ├── .env.ch_backup            ← S3 备份（3 KEY，手动加载）
    ├── .env.restic               ← Restic 备份（2 KEY，手动加载）
    ├── SECRETS.md                ← 【新增】密钥管理文档
    └── secret_registry.yaml      ← 【新增】密钥声明注册表
```

### B. 密钥读取规范决策树

```
读取密钥 →
├── 是 API token（DEEPSEEK_API_KEY/TUSHARE_TOKEN 等）？
│   └── get_required_secret("KEY")  ← 从 .env（自动加载到 os.environ）
├── 是基础设施凭证（POSTGRES_PASSWORD/CLICKHOUSE_PASSWORD 等）？
│   └── get_service_secret("KEY", "postgres"/"clickhouse"/...)  ← 从 config/.env.{service}
├── 可选密钥（有默认值）？
│   └── get_secret_or_default("KEY", "default")
└── 禁止：os.getenv("KEY") / os.environ.get("KEY") / os.environ["KEY"]
```

### C. 新增密钥流程（3 步）

1. **加 KEY 到对应 .env 文件**（根目录 .env 或 config/.env.{service}）
2. **更新 .env.example**（加 `KEY=` 占位 + 注释说明用途）
3. **更新 secret_registry.yaml**（加结构化条目：key/service/env_file/category/required/description）

> gate 会校验 .env.example 与 secret_registry.yaml 的一致性，遗漏任一步会被阻断。

---

**本裁定状态**：open（分析完成，治本施工方案待 Owner 批准）
**下一步**：等待 Owner 批准后，按 Phase 1 → Phase 2 → Phase 3 顺序实施
