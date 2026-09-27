---
ttl: task_bound
---

# W-152 提交队列载荷 HMAC 归属载体立项提案

- **编号**: W-152（波 9.4 排产，`docs/_working/total_command_closeout/10_wave_plan.md` §9.4）
- **状态**: 立项提案（未批准开工）——本文件只是工程方案+量级评估，不含任何代码改动
- **落点**: `docs/_working/commit_speedup_campaign/80_hmac_proposal/proposal.md`
- **性质**: 非实施（review_ext_verdict 已将本件降级为附带产物：写文档不消灭人工环节）
- **立案依据**: 终局令曾把"归属级 HMAC 载体立项"列为 Owner 已批直接执行，但 dossier_H
  H-105/S-07 实测"`80_hmac_proposal` 盘面与 HEAD 皆无、册上查无"⇒ 转 W-152 补立项

## 一、背景与威胁模型

### 1.1 现状：归属判定的两道既有防线

1. **`[GW:]` 明文标记**：提交必经 GitCommitGateway（`scripts/git_commit.py`），gateway 在
   commit message 写入 `[GW:]` 归属标记；POST-COMMIT-GUARD 判手写标记为 forged 并 reset
   回滚（宪法 §9.8 提交工具红线）。
2. **提交队列载荷自述**：`scripts/commit_queue.py` 队列项 payload §6.1 已结构化
   （qid / session_id / created_at / branch / base_head / files[{path, blob_sha256, …}]），
   A 段零 git 依赖，逐路径基底 blob sha 可复算。

### 1.2 红队实证：两道防线皆可冒充穿透

- **总决算红蓝补测（W-101）**：`docs/_working/total_command_closeout/96_final_delivery.md`
  首次拿到能红的读数——governance 22 绿 **1 真红：冒充在活 sid 的伪造 `[GW:]` 零分支零审计**。
  即攻击面＝持有一个在活 session id 的会话（或能写 message 的恶意通道），伪造成该 sid 的
  `[GW:]` 标记直连提交，**当前没有任何分支逻辑与审计事件**能识别这是冒名。
- 99_FINAL_REPORT §三.6 已登记为待办："归属级 HMAC 载体（红蓝④发现，登记待办）"。
- f08 leaf book 结论一致："归属级治本＝每笔提交带凭据载体（HMAC），需改 git_commit_gateway.py"。

### 1.3 威胁模型界定

| 要素 | 判定 |
|------|------|
| 攻击者能力 | 能发起 git 写路径、能写 commit message、知道某个在活 sid（可从 stash_notice/队列 status 等旁路观测） |
| 攻击者不掌握 | gateway/serializer 进程内存中的 HMAC 密钥（密钥永不进会话 env） |
| 防护目标 | 伪造/冒名的队列载荷与直连提交**可被机械识别**并留审计，而非依赖"标记长什么样" |
| 非目标 | 不防 Owner 本人操作、不防已拿到进程内存的完全攻陷场景、不替代审计链（gov_audit） |

### 1.4 事实挖掘留痕（本提案证据链）

- `docs/_working/total_command_closeout/dossier_A_commit_chain.md`：grep HMAC = **0 命中**
  （提交链案卷本身未涉及 HMAC，佐证"查无立项"结论）。
- `docs/_working/commit_speedup_campaign/` 全目录 grep -ri hmac：仅 99_FINAL_REPORT.md:44
  与 90_verification/CAMPAIGN_STATE_SNAPSHOT.md:123 两处"待办"提及，无方案正文。
- 裁定 #10/#266/#267/#287（dossier_H 汇总）均为**审计链** HMAC 双契约/分期验证他题，
  非提交归属命题——本提案不与之冲突，且复用其密钥纪律先例。

## 二、方案（HMAC-SHA256，密钥走 secrets.py）

### 2.1 载体与覆盖面

- **签名对象（canonical payload）**：`payload = files + base_head + session`，即
  队列项 §6.1 结构化字段的规范序列化（逐路径 path+blob_sha256 列表、base_head、session_id；
  序列化采用与 payload 现行写盘一致的确定性编码，禁 datetime.now()/time.time() 混入
  签名体——RULE-SCHEMA-TZ）。
- **算法**：HMAC-SHA256（stdlib `hmac` + `hashlib`，与
  `src/zephyr/shared/security/secrets.py::derive_key_hkdf` 现行实现同族）。
- **签名位置**：git_commit_gateway 入队（enqueue）前计算，写入队列项
  `meta.payload_hmac`（十六进制）；`--no-auto-enqueue` 直连路径在 gateway 落盘前同法签名。
- **校验位置**：serializer/drain 真实落地前复算；不匹配 ⇒ 拒落地 + 登记审计事件
  （复用 governance.db 审计通道），缺失签名按 flag 分期（见迁移）。

### 2.2 密钥纪律（RULE-SECRETS 三道 gate 全适配）

- 密钥取用一律 `src/zephyr/shared/security/secrets.py::get_required_secret("ZEPHYR_COMMIT_HMAC_SECRET")`
  （禁裸 getenv/硬编码）；可选用 `derive_key_hkdf(master, info="commit/hmac")` 派生子密钥，
  与审计链 `info="audit/hmac"` 域分离。
- 先例：`src/zephyr/gov_audit/writer.py::resolve_audit_hmac_secret` +
  `IntegrityVerifier(hmac_key=…)` 已是同型"密钥+验签器"组合，方案即向提交链复刻该模式。
- 密钥**禁入会话 env**：`ZEPHYR_COMMIT_HMAC_SECRET` 须追加进
  `src/zephyr/ai_layer/redline/negative_list.py` NL-2 deny 模式（与
  `ZEPHYR_AUDIT_HMAC_SECRET` 同列），由 session_env_guard 机检兜底。

## 三、与现有 [GW:] 标记的关系

| 维度 | `[GW:]` 明文标记（现有） | payload HMAC（本提案） |
|------|--------------------------|------------------------|
| 归属依据 | message 里的会话名（人读+门判读） | 只有持密钥进程能产生的凭据（机强校验） |
| 伪造成本 | 红队已证：冒充在活 sid 零分支零审计 | 不知道密钥则不可伪造（SHA256 抗碰+密钥隔离） |
| 判伪机制 | POST-COMMIT-GUARD 判手写=forged | drain 侧复算不符=拒落地+审计 |
| 去留 | **保留不退役**（宪法 §9.8 红线继续有效） | 叠加新增，二者互补 |

结论：HMAC 是 `[GW:]` 的密码学底座，不是替代品；`[GW:]` 继续供人读与现有门判读，
HMAC 补上"标记可被冒写"这一被红队证实的缺口。

## 四、迁移步骤（三步）

1. **生成与注入（观察期）**：git_commit_gateway 对 canonical payload 计算
   HMAC-SHA256 写入 `meta.payload_hmac`；commit_queue payload 增加可选字段（无 schema
   迁移）；旧无签名项照常落地；新增 flag `commit_payload_hmac_enforce`（出厂 off）。
2. **校验与审计**：drain 侧复算；不匹配 ⇒ 拒落地+审计事件；缺失 ⇒ 只记审计不阻断
   （观察期口径）；同时把 `ZEPHYR_COMMIT_HMAC_SECRET` 加进 NL-2 deny 名单。
3. **翻转与收口**：Owner 门位批准后翻转 flag（flag 出厂翻转属 high 域人机门位），
   缺签名即阻断；红蓝回归补测 W-101 场景（伪造 `[GW:]`+冒充在活 sid）转绿后结案。

## 五、验收判据

1. 红队复测 W-101 场景：冒充在活 sid 的伪造提交从"零分支零审计"变为"拒落地+审计留痕"。
2. 队列兼容：观察期内旧无签名项可正常 enqueue/drain；翻转后无签名项被拒且留审计。
3. 密钥不外泄：session_env_guard 实测喂入 `ZEPHYR_COMMIT_HMAC_SECRET` ⇒
   `allowed=False、leak_suspected=True`（与 ZEPHYR_AUDIT_HMAC_SECRET 同判）。
4. 幂等与重放：同一载荷重放 HMAC 恒等（确定性序列化）；改 files/base_head/session
   任一字段 ⇒ 校验必不通过。
5. 回归不破：提交链七套合并回归全绿；`--adopt-prior-work`/`--enqueue` 重试路径
   签名语义不漂移。

## 六、量级评估（波 9.4 验收必备节）

- **改动面（预估）**：`git_commit_gateway.py`（签名注入）、`commit_queue.py`
  （meta 可选字段+drain 校验钩子）、`negative_list.py`（+1 deny 条目）、
  `config/flags.yaml`（+1 flag）、配套单测 ≈ **5 文件、150–300 行量级**（含测试）。
- **性能**：HMAC-SHA256 单次微秒级；每提交一次签名+一次复算，对 24h 提交量级
  （当前 ≤ 数百/日）开销可忽略；不新增任何 git plumbing 调用。
- **风险**：密钥缺失导致全网签不了（缓解：get_required_secret 启动期显式失败）；
  观察期长短由 Owner 裁定（建议一轮红蓝周期）。
- **不做**：本立项不实施；签名算法升级路径（如 Ed25519 非对称）留待 Owner 另裁。
