---
ttl: task_bound
---

# SEC_realkey_scan — LANE-SEC 真键回溯扫描案卷（只读补偿控制）

- 车道：LANE-SEC（安全补偿控制）｜总筹：st-qmine-20260925｜日期：2026-09-25（夜）
- 任务性质：`REAL-KEY-REFERENCE-SCAN` gate 禁用窗口期的事后补偿控制。**只读，未改任何业务文件，未动 in_process_gate_registry.yaml，未做任何 git 写操作。**

## 1. 扫描规则真源（未自造判据）

直接 import gate 本体函数跑，零复制规则文本：

- 判据常量：`src/zephyr/ai_layer/redline/negative_list.py` → `REAL_KEY_MARKER = "QMT" "_REAL"`（即字面子串 `QMT_REAL`，大小写敏感，源码中刻意拆分书写避免 gate 源文件自触发）。
- 判定函数：`src/zephyr/ai_layer/redline/negative_list_gates.py::scan_real_key_hits`（gate check 内部调用的同一纯函数）＋ `_is_real_key_whitelisted`（白名单＝basename `secret_registry.yaml` / `SECRETS.md`，任意目录深度）。
- 口径要点：该 gate **无 noqa/逃生标记**（SAFETY 注记"白名单外零逃生"），故本报告"疑似但被豁免"一类只可能是白名单命中——实测为空。
- 登记册位置：`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` 约 707 行，`enabled: false`（09-26 总指挥暂禁用批注），同段另有 `TASK-ORDER-DOCS-LOCK`（约 718 行）/`CONSTITUTION-LINE-LIMIT`（约 724 行）两台同批禁用，本车道不处置。

## 2. 扫描范围与件数

窗口定义（任务书口径）：`git log --since="2026-09-25 20:40" --name-only` 的 `src/zephyr/**` ＋ 未落 HEAD 的 staged（`--diff-filter=AM`）＋ 未跟踪 `src/zephyr/**`。

| 池 | 件数 | 读取面 |
|---|---|---|
| 窗口 commit 池（`git log --since 20:40`，仅 4a977608d7 含 src/zephyr 件） | 3 | 磁盘（与 HEAD 一致，无后续改动时等价） |
| staged 未落地 AM 池（staged 总盘 549 条中 src/zephyr 部分；staged 走 `git show :path` index blob，与 gate `_read_staged_file` 同源） | 87 | index blob |
| 未跟踪池 | 22 | 磁盘 |
| 去重合计 | **109** | 不可读件=0 |

## 3. 结果：零命中（附红证，非"扫不出"）

- `scan_real_key_hits` 输出：**hits=[]**；白名单豁免（含 marker 但被 exempt）=0；unreadable=0；全 miss 109。
- 扩展观察（超 gate 口径，仅供复核，不改变结论）：
  - 宽松近失正则 `(?i)qmt[_-]?real`：0 件；
  - 全池 `QMT` 字样人工抽看：均为规则定义文本（拆分书写的 marker 本体）、注释/文档叙述、`miniQMT` 数据源名——无实盘键名字样裸露；
  - 用**在册活 gate** `NO-SECRET-HARDCODE` 的 `_SECRET_PATTERNS_DEEP`（`src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py`）对同池全文件跑一遍：2 处命中均在 `src/zephyr/gov_enforcement/commit_gates/create_guard.py` 127/711 行——CREATE-GUARD creation_token 治理字样（非服务凭证、非窗口新增行；当前 staged diff 无匹配 added 行，活 gate 口径不会拦），定性误报。
- **红证（证"扫得出"）**：物理样例 `.runtime/tmp/lane_sec_redcheck/fake_key_probe_demo.py`（合成假键 `QMT_REAL_DEMO_ONLY_NOT_A_SECRET_zzz9`，非真凭据）与对照白名单件 `secret_registry.yaml` 同喂 gate 本体函数 → 输出恰好只报样例件命中、白名单件放行（`passed: true`），证毕即删（目录已确认不存在）。脚本=`.runtime/tmp/lane_sec_redproof.py`。
- 件清单落盘：`.runtime/tmp/lane_sec_win_{committed,staged,untracked}.txt`；扫描器=`.runtime/tmp/lane_sec_realkey_scan.py`；结果=`.runtime/tmp/lane_sec_scan_result.json`（均 .runtime/tmp，24h TTL 自然回收，不入袋）。

## 4. 三道防线核对（SECRETS.md 口径）与本次真空分析

真键若已入仓，各面本会拦谁/为何现在拦不住：

1. **取值面 `secrets.py`**（`src/zephyr/shared/security/secrets.py`）：QMT 实盘键唯一正门＝`get_service_secret("QMT_REAL_PATH"/"QMT_REAL_ACCOUNT", "qmt")` 读 `config/.env.qmt`（gitignore，注册=`config/secret_registry.yaml` 799-831 行）。它管"怎么取值"，**不管键名字样散落**——散落引用不经此面即无声。
2. **gate 面**：在册活闸三台 `NO-BARE-GETENV(81)`/`SECRET-REGISTRY-CONSISTENCY(127)`/`NO-SECRET-HARDCODE(128)` 全部盯"值/格式/读法"（sk-/AKIA/`KEY="value"` 等，且只扫 added 行）；盯"**实盘键名字样出现在 own-diff 文本面**"的恰是禁用的 `REAL-KEY-REFERENCE-SCAN(149)`——窗口期该字面=**真空**，此即本补偿控制的必要性。
3. **运行时面 `session_env_guard`（S1）**（`src/zephyr/ai_layer/redline/session_env_guard.py`）：`screen_session_env` 按 `DENY_ENV_PATTERNS`（`QMT_REAL_*`/`ZEPHYR_AUDIT_HMAC_SECRET`/`*_LIVE_*`）拒发 env＋审计（只落键名+值长）＋KillSwitch `permission_boundary_probe`。**实测 src/ 与 scripts/ 无任何生产调用方**（仅 `redline/__init__` import 占位）——即使本批落地，此面仍悬空，属"实现已在、接线未做"。且它守 env 注入，救不了已 commit 入仓的硬编码。

结论：零命中＝窗口期真键未漏，但窗口期防线仅剩 1/2 两台半（NO-SECRET-HARDCODE 管值不管名、运行时面无调用方、名册 gate 关闭）。

## 5. 处置与袋划分建议（交总筹/落地车道，本车道不执行）

- 命中件清单：**空**——窗口袋无需建密钥清洗子袋。
- 建议袋 A（随 Z-C7 落地批）：三 gate 与 `negative_list*.py`+`tests/ai_layer/redline/test_negative_list_gates.py` **同 commit 翻回**，本扫描证据支持翻回安全（现存 109 件零命中，不会误伤后续 landing；gate 只扫 own-diff，存量永不回溯）。
- 建议袋 B（独立，非本车道权限）：`screen_session_env` 生产接线（AI 会话 spawn 路径），否则 S1 运行时面永远纸面。
- 建议袋 C（低优先）：`create_guard.py` 两处 deep-pattern 字样若被未来 own-diff 重加行会触发 NO-SECRET-HARDCODE 误伤，届时按豁免纪律处置即可，勿现在改。

## 6. 三条 gate 现在该不该翻

**不该先翻名册**（总筹裁 Z-C7：module＋测试同 commit 一起翻；且实测 module 未落 HEAD，名册先行＝同源断裂复发路径）——但本卷证明**同批翻回无存量冲突风险**，落地车道可放心随 AI 层批执行。
