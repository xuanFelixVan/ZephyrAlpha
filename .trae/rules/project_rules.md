# ZephyrAlpha Project Rules（Trae IDE 自动加载）

> **本文件由 Trae IDE 自动注入每个 AI 对话的上下文。以下为硬规则——不可协商、不可绕过。**

---

## 🔴 RULE-ZERO：AI 对话文件锁协议（最高优先级）

**触发条件：你对任何文件执行任何写入操作（创建/修改/删除/重命名）之前。**

### 强制三步流程

```
BEFORE WRITE → CHECK  → python scripts/lock_files.py check <file>
               ↓
            FREE? → ACQUIRE → python scripts/lock_files.py acquire <file> <your_session_id> --task "<任务简述>"
               ↓
            LOCKED? → STOP. DO NOT TOUCH. 报告给用户：文件被 <owner> 锁定。
               ↓
AFTER WRITE  → RELEASE → python scripts/lock_files.py release <file> <your_session_id>
```

### 你的 session_id 格式

```
session-YYYYMMDD-NNN
```

从 `session-logs/` 目录中找到你对应的编号。如果不知道编号，使用当前日期 + 你在对话中看到的编号。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **跳过 check 直接写文件** | 编码损坏、修改丢失 |
| ❌ | **check 返回 LOCKED 后仍然写文件** | 覆盖其他对话的工作 |
| ❌ | **用 Write 工具绕过 lock_files.py** | 本协议的强制力完全失效 |
| ❌ | **写完后不执行 release** | 死锁——其他对话永远抢不到锁 |

### 读操作

**读操作不需要加锁。** 只有写入操作需要走三步流程。

### 批量操作

如果一次任务需要修改 N 个文件：
1. 先对 N 个文件逐个 `check`
2. 全部 FREE 后，逐个 `acquire`
3. 全部修改完成后，逐个 `release`

如果一个被锁住了 → 释放已抢到的，等全部可抢再开工。

### 紧急情况

如果发现 `.ailocks/registry.json` 损坏或出现大量死锁：
```
python scripts/lock_files.py cleanup    # 清理所有 TTL 过期的死锁
python scripts/lock_files.py status     # 确认清理结果
```

### 原理

锁通过**原子目录创建**（`os.makedirs(exist_ok=False)`）实现互斥：
- `.ailocks/{sanitized_path}.lock/owner.json` → 锁持有者信息
- `.ailocks/registry.json` → 全局锁注册表
- TTL = 30 分钟 → AI 对话结束前必须释放，TTL 只是防崩溃的最后防线

对标：K8s ResourceQuota + etcd 分布式锁 + Git pre-commit hooks

---

## 🔴 编码安全（从 AGENTS.md §4 继承）

| # | 规则 |
|---|------|
| 1 | Python `open(path, 'w')` 禁止省略 `encoding='utf-8'` |
| 2 | PowerShell 写文件：`[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)` |
| 3 | `files.autoGuessEncoding` = `false`, `files.encoding` = `utf8` |
| 4 | 禁止 Trae + Cursor 同时打开同一文件 |
| 5 | 扫描器大量报错 → 先检查扫描器本身的逻辑 |

---

## 🟡 施工纪律（继承 AGENTS.md §6）

- §6.2 原子事务：关联修改同一批完成
- §6.5 脚本入库：新建 .py 立即注册到 script_manifest.yaml
- §6.12 AI受众优先：输出格式优先让 AI 零歧义消费
- §7.2 根源分析：遇到问题 → 5 Whys → 治根不治标

---

## 🔴 修改原则：第一性原理，零历史债务（不可绕过）

| # | 规则 |
|---|------|
| 1 | **发现事实错误 → 直接修正数字/名称/路径/状态。禁止添加解释性段落说明"之前为什么是错的"。** |
| 2 | **文档中所有数字、字段数、版本号、计数必须是当前唯一真实值。不留"之前是X现在改为Y"的过渡文本。** |
| 3 | **历史版本差异通过变更日志（change log / 版本记录）追踪，不在正文中保留已过时数据。** |
| 4 | **单个 real number 原则：一个事实在所有蓝图中只能有一个数字。N 处出现 = 同一数字，不一致就是 bug，直接修。** |

违反此规则的典型反模式：
- "TaskCard 有 74+ 字段（旧版）→ 实际 62" → 应为 "TaskCard: 62 字段"
- "之前 belongs_to 均未声明，现已补全" → 应为 "belongs_to: 已声明"

---

## 会话结束清单

每个 AI 对话结束前 MUST：

### 锁协议
1. `python scripts/lock_files.py release-all <your_session_id>` ——释放所有锁
2. `python scripts/lock_files.py cleanup` ——清理残留死锁
3. `python scripts/lock_files.py status` ——确认 CLEAN

### Session Continuity 保存
4. `sc.generate_and_save(session_id=..., task_repo=...)` ——保存状态给下一次 session

### MANDATORY-ZR 零残留强制自净（IRN-011 · ZR-008）
5. 临时文件扫描：`_temp*` / `_check*` / `_phase_*` 前缀文件 → DeleteFile（物理删除）
6. 确认本次 session 产生的所有 `.py` 文件已在合法三目录（`scripts/governance/` / `src/zephyr/` / `tests/`）中——不存在根目录孤儿
7. 如果 session 中删除过文件或目录 → 检查废墟引用残留（其他文件仍引用已删除路径）

### 记录
8. 写 Session Log（`session-logs/YYYY/MM/session-YYYYMMDD-NNN.yaml`）

### 💡 关键原则
- 你今天留下的临时文件，**永远不会被下一个 AI session 自动发现和清理**——临时文件 = 磁盘噪音 = 下一个 AI session 的认知负担
- 对标 AGENTS.md §5.3.3 + §5.3.5，IRN-011 ZR-003/ZR-005/ZR-007/ZR-008
