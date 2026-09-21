---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# ⚠️ ZCode 静默上传事件——本机查证结论（R2 实测版）2026-09-20

> R1 为剪报转述版；R2=Owner 授权"全部都要查"后的本机实测取证。**结论：本仓在事发窗口处于"仓库快照索引=开启"状态，暴露面按已泄露对待。**

## 1. 本机取证事实（全部亲测，时间 2026-09-20 深夜）

1. **体积**：`C:\Users\fanzi\.zcode` 共 **2.7 GB**（cli/db 1.2G=会话史、cli/log 564M、v2/logs 439M）。爆料者线索量级（700MB+）成立。
2. **实锤——快照索引对本仓开启过**：`v2/logs/2026-09-18.log` 00:01 的设置写入快照明文含 **`"repoSnapshotIndexingEnabled": true`** 且 **`"repoSnapshotIndexingUserConfigured": true`**，同一快照里 `recentProjects: ["D:\ZephyrAlpha"]`；repo-wiki 的 RPC 订阅在 09-18/09-19 全天活跃。
3. **开关一直开到今天**：`2026-09-19.log` 含该键为 true 共 435 处、`2026-09-20.log` 含 236 处——即事发窗口与之后，本机索引开关持续为 true；直到 v3.14.1（2026-09-20 发布，自动更新已开）后，当前 `v2/setting.json` 中**该键已消失**——与官方"已修复"口径吻合（修复以移除/改键方式落地）。
4. **未找到直接上传日志**：本地日志未见 aliyun/OSS 上传行（厂商云端加密上传未必落本地日志）——故定性为"**高度可能已上传**"而非"已证实上传"；在第三方审计出来前，按已泄露处理。
5. **暴露面清单（若上传发生）**：整仓快照**不理会 .gitignore**——`.env`（55 键名可见/registry 记 62 键：OKX 交易所 key、iFind 账号密码、百度网盘 OAuth token、TUSHARE_TOKEN、DeepSeek/Qwen/GLM/混元/千帆/Google/Groq/Mistral/Cohere 等 LLM key、QWEATHER/FRED/EIA）+ `config/.env.{postgres,clickhouse,redis,qmt,ch_backup,cryptoquant,glassnode}`（registry 合计 **100 键**）+ 完整 .git 历史。
6. **LFS**：规则 2026-08-03 已治本移除（死代码），`.git/lfs` 仅 21K——可忽略。
7. **附带发现**：`webRemoteControlExternalRelayDevice`（远程控制中继，deviceSid 在案）曾对本工作区启用——另一个云端触点，不用建议关。

## 2. 处置建议（P0，按优先级）

1. **轮换高价值密钥**（Owner 在各厂商控制台操作，AI 无法代办）：第一优先 **OKX**（能交易的！建议改成只读权限+IP 白名单+禁提币）、**iFind 账号密码**、**百度网盘 OAuth token**；第二优先各付费 LLM key 与 TUSHARE_TOKEN。轮换后只需改 `.env`/`config/.env.*` 一处（secrets.py 单点读取，零代码改动）。
2. **等待官方开源+第三方审计**再信任"云端即焚"口径；自动更新保持开启（本次修复就是靠它到的）。
3. **关掉不用的远程控制中继**（设置里 webRemoteControl 相关项）。
4. **每月两分钟巡检**：`du -sh ~/.zcode`（体积突增=警报）+ 在最新日志里 `grep repoSnapshot`（键复活=警报）。已写入口径，可挂月度任务。
5. **战略结论（防偷讨论，大白话）**：代码层面防不住——能读你代码的 AI 工具就传得走，这是权限本质决定的；真正要防的是**钥匙和数据**：钥匙最小权限+快轮换（泄露了也开不了门），出网大流量监控（防不住但抓得住），真·核弹级机密放离线机。本仓现状恰好抗泄露：alpha 主要在本地 CH 数据与 DB 参数里，不在代码文本里——代码摆烂，钥匙不摆烂。
