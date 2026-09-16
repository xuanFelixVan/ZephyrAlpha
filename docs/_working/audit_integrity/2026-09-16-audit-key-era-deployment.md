---
ttl: task_bound
completes_when: 裁定#267 落地+终验 mismatch=0+提交入库+Owner 验收（密钥分期与新钥部署收口）
---

# 审计链 HMAC 密钥分期与新真钥部署报告（st-auditkey-20260916）

- 会话: `st-auditkey-20260916` 日期: 2026-09-16
- 授权: Owner「开工」令（密钥政策裁定+施工方案三批 A/B/C 的执行批）
- 前序: GW-A 欠账清偿（st-auditfix-20260916，裁定#266）+ 本会话高级模型复核与密钥考古（旧钥判死终态移交 Owner 汇报）
- 边界遵守: 未触碰 flash 会话在途文件面（其 writer.py 收尾 75 分钟静默后接手并如实归属）

---

## 1. 复核结论（flash 班工作）

**PASS**。11 用例独立复跑全绿（8.4s）；三维普查数字独立复现精确吻合（26,909/#26810-#53718、5,343、5,595 重算口径）；红蓝攻击用例（era 外钥重签必拒）在我方新套件中延续钉死。发现并处置一处已提交回归（见 §2.3）。

## 2. 施工内容

### 2.1 批次 A：密钥分期验证基建

- **`config/audit_key_eras.yaml`（新建，creation_token=audit-key-eras-registry-20260916）**：
  五分期注册表——era-default-public（公开默认钥期，weak）/ era-lost-may2026（遗失钥期
  26,909 条）/ era-lost-may2026-finding-import（占位时间戳嵌套微分期，17 条 finding 导入批，
  见 §4.3）/ era-primary（真钥期）；transition_overlap_seconds=14 天（长驻写方滚动重启过渡窗）。
- **`src/zephyr/gov_audit/integrity.py`**：IntegrityVerifier 分期模式——
  仅 hmac_key=None（自动解析）且注册表存在时启用；显式传钥=单钥语义（既有 60 处调用面零变化）。
  四类判定 strong/weak/known_loss/mismatch；**禁 try-all**（era 范围外的钥验过=失配）；
  强分期 env 缺失 fail-loud；lost 分期 known_loss 不判 compromised；HMAC 口径补第三约定
  （2026-05 代 canonical 含 entry_hash——旧钥若寻回即恢复可验）。
- **`tests/governance/audit/test_key_era_verification.py`（新建 9 用例）**：三分期分类/
  weak 定性/强分期 fail-loud/**era 外钥重签攻击必拒**/过渡窗有界（窗内 weak 窗外 mismatch）/
  显式钥旁路/注册表缺失回退/畸形注册表 ValueError/May 约定兼容。
- **`tests/conftest.py`**：autouse `_isolate_audit_key_eras`——pytest 全域隔离仓内分期注册表
  （防真钥部署后测试事件误入强分期 fail-loud）。⚠️ 该 hunk 被他会话 commit 2e38f36c9c
  （conftest basetemp 自愈）吸收入库——内容与本次设计一致，归属如实交底，本提交不再含此文件。

### 2.2 批次 B：新钥部署（2026-09-16T07:05:02Z）

- 256-bit urlsafe 随机钥生成（secrets.token_urlsafe(32)，指纹 sha256[:12]=0fc77a652196，
  全值不落任何 git 资产）→ `.env` 追加（已 gitignore:262；备份 .runtime/tmp/env_backup_precert_20260916）。
- era 边界同窗回填：era-default-public.valid_to = era-primary.valid_from = 部署时刻。
- **终验（生产 events.jsonl 115,034 条全量，只读）**：
  `hmac_era_summary = {strong: 0, weak: 88,125, known_loss: 26,909, mismatch: 0}`
  ——HMAC 维度意外失配**清零**；known_loss 与取证数字分毫不差；新钥端到端冒烟 strong=1 valid。
  余 10,938 issues 全部为裁定#266 已载的另两维历史伤（prev 断链 5,595 重算口径+内容哈希 5,343），
  非本批范围。部署后新进程以真钥签名；存量长驻进程经 14 天过渡窗按 weak 接纳。

### 2.3 GW-A 收尾回归修复（writer.py，归属 st-auditfix 治本的延续）

已提交的 GW-A 锁引入一处回归（`tests/audit/.../test_audit_integration_fracture.py`
I8 失败保护实证红）：锁的 `lock_path.parent.mkdir` 副作用把「event_log_path 指向不存在
目录」这一写入失败前置消灭（目录被建出后 append 反而成功），readonly 永不触发。修复：
① 删锁内预建目录（正常路径由 __init__ data_dir.mkdir 保证）；② 失败计数临界区覆盖
锁获取+尾读+落盘全链。修复后审计域全量回归 **3,364 passed / 0 failed**（修复前 1 failed）。

## 3. 测试与验证总账

- 新套件 9/9 绿；审计域全量（tests/audit + tests/governance/audit）3,364 passed / 6 skipped / 0 failed。
- era-aware 生产全量 census：mismatch=0（§2.2）。
- 端到端冒烟：真钥签名+分期验证 strong 通过。

## 4. 诚实条款（未决/限制）

1. **旧钥判死不可逆**：26,909 条 HMAC 永久不可验证（非篡改，entry_hash 全自洽已三班互证）。
   若他日寻回 2026-05-26~06-01 期密钥，改 era-lost-may2026.key_source 为 env:VAR 即收窄定性。
2. **过渡窗攻击面 trade-off**：14 天窗内公开默认钥可在 era-primary 边界后伪造 weak 通过——
   这是滚动重启期的显式取舍（注册表头注已载）；维护班完成长驻写方重启清场后应收窄
   transition_overlap_seconds 至 0（移交项 C-3）。
3. **finding 导入批 17 条**：占位时间戳 2026-05-26T12:00:00Z（真实写入 05-27 20:10 前后），
   以嵌套微分期归入 known_loss——era 定性按记录时间戳的边界局限由此显式建模，非通融。
4. flash 班报告 §7.1 prose 写裁定改号 #265，注册表现值 #266（#265 空号）——prose 一步滞后，
   未代修（他会话在途件不代修纪律）；本会话裁定取 #267 避开 stale 引用。
5. strong=0 是部署时刻的必然（真钥只对部署后新写入生效）；部署后 census 的 strong 计数将随
   新进程写入自然增长，存量长驻进程重启前按 weak 计。

## 5. 移交清单（批次 C 剩余，维护班）

| # | 项 | 锚点 |
|---|---|---|
| C-1 | gate_chain.jsonl 同型锁改造 | 裁定#266 §8.2 观察项 |
| C-2 | log_rotation.rotate() 接 append 锁 | 解冻轮转前置 |
| C-3 | 长驻写方滚动重启 + overlap 收窄至 0 | 本报告 §4.2 |
| C-4 | secret_registry 周期核对（required=true 项失守告警） | config/secret_registry.yaml |
