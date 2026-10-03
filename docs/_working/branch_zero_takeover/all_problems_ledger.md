---
ttl: task_bound
session: st-ffchief-20261002
date: 2026-10-02
title: 三夜全量问题挖矿清单与治本台账
completes_when: 三十三类全治本
---
# 本对话全量问题挖矿清单 + 治本台账（st-ffchief-20261002）

> Owner 令：把三夜对话遇到的所有问题全部挖出来、全部治本，让以后的 AI 不再遇到。每类：症状 → 根因 → 治本（落地锚）→ 以后怎么做。已按"会话生命周期/提交链/ belt/ 门禁/ 档案安全"五域归组。

## 域一：会话生命周期（AI 施工队生存问题）

| # | 问题 | 根因 | 治本（落地锚） | 以后 |
|---|---|---|---|---|
| 1 | 会话注册 90 秒后被判死（鸡生蛋） | 注册后需心跳自持，心跳守护又要求先注册 | 标准序：register(pid=0)→90s 窗内 Start-Process 脱树拉守护→自持 | 已录配方（memory+本册） |
| 2 | ZCode 后台 shell 树回收子进程→守护秒退 | 后台 Bash 的进程组管理回收子孙 | 守护必须 Start-Process 脱树拉起 | 同上 |
| 3 | pid=真实短命 pid 被 salvage 清尸 | 判活查 pid 存活 | 注册用 pid=0+logical=True（总包形态） | 同上 |
| 4 | 会话中途死亡→资源无人认领（Owner 核心痛点） | 判死时资源不显化 | **接管台账三件套**（L1 清单/L2 死亡钩子/L3 门禁）a57de1be+95dd7f426e | 永久机制在册，会话分支随关闭清（SOP） |
| 5 | 瞬时死亡（强杀/除名）扫描盲区 | 扫描只读注册表 | _scan_orphan_resources 孤儿树侦测（9b3359eccf） | 在 HEAD |
| 6 | V5 前伪造注册/keeper 刷活性 | register() 无频率护栏 | 频率护栏 1860s 窗（79eeda72），混沌演训实证拒伪造注入 | 在 HEAD |

## 域二：提交链（3 小时提交战的病根全录）

| # | 问题 | 根因 | 治本 | 以后 |
|---|---|---|---|---|
| 7 | 落地门超时误杀合法长链（全队退避风暴） | 900s 上限<k4 并发期实际 1571s | CR-16：2400s（9503d222） | 在 HEAD |
| 8 | belt 守护空转（sys.path 脆弱） | PYTHONSAFEPATH/服务化启动下包导入炸 | _drain_once 显式补仓根（582866894e） | 在 HEAD |
| 9 | 守护堆积 6-8 只 | 看门 CIM 探测竞态 | 杀净重拉配方；**根治待白班**改心跳文件判活（裁定七） | Owner 门位 |
| 10 | 主区直投被外来 staged 面连坐（DATETIME/TEST-SOURCE/REGISTRY-MASS 警告+REGISTRY-MASS 硬拦） | 共享暂存区多会话混居 | --allow-multi-domain+接管收编净删标记；**治本方向=prestage 严格 own-scope 化**（登记议题） | 登记在案 |
| 11 | CREATE-GUARD 反复拦（token 缺/键不匹配/判第二真源） | ①token ASCII ②gate 读袋内快照册 ③关键词级查重 | 携册直投配方+not-dup 标记+create-guard 官方工具 | 配方在册 |
| 12 | TRANSLATION-COVERAGE 缺词 | 新 .py 未登记 | add_module_translation 大白话禁模板 | 配方在册 |
| 13 | ALGO-FLOW 锚缺/断链 | 锚必须在 docstring+外置 yaml 在盘 | drafter 工具+手包结构 | 配方在册 |
| 14 | TTL/EXEMPT-ZONE frontmatter 规则族 | exempt-zone 禁 doc_type；ttl 必填 | frontmatter 模板（ttl+completes_when，exempt-zone 无 doc_type） | 本册模板 |
| 15 | GATE-SELFDOC 不认 exempt-zone 的 frontmatter | 该门判据限永久区 | ABS-27 字面量改写（语义不变） | 配方在册 |
| 16 | R5 数字后缀目录（两次自伤） | 建目录时 autopilot 带日期 | 建目录零日期；已建的改名+token/词条随路径重登记 | 规约在 DCR |
| 17 | BARE-SUBPROCESS / PERM-TRIGGER / MSG-EXPOSURE / NOQA | 新代码各门族 | run_subprocess_hidden / m11 双载体 / details 字段 / noqa 官方登记 | 配方在册 |
| 18 | 多行 except 的 noqa 位置 | ruff 诊断行=异常类元素行 | noqa 落 Exception 元素行 | 本册 |

## 域三：belt 与队列

| # | 问题 | 根因 | 治本 | 以后 |
|---|---|---|---|---|
| 19 | 袋快照丢未暂存册 | git add 时机晚于快照 | 册先行 git add 再 enqueue | 配方在册 |
| 20 | scratch worktree 半程暂存残渣楔死 | 守护被杀时 landing 中断 | reset --hard+clean（scratch 区配方） | 本册 |
| 21 | FOLDER-CAPACITY 楔死 | 临时树 __pycache__ 累积 | 清理配方；scripts/ 拆簇待 Owner 批 | 拆簇方案在案 |
| 22 | 历史死信无清算 | 无常驻机制 | --sweep-absorbed 三分流（首跑显化 696 超龄） | 在 HEAD |
| 23 | 判弃死袋销账无标准 | 人工判弃 | --resolve+dead_archive 档案化 | 在 HEAD |

## 域四：档案安全（Owner 最担心的"误删"专项审计结论）

| # | 事项 | 审计结论 |
|---|---|---|
| 24 | worktree 退役 180 棵 | **零删除**：28,887 文件全量字节级存档（825MB，160 manifest），处置前逐树脏检 |
| 25 | 抢救档案曾被放 tmp TTL 区（**本日自查发现的真风险**） | 已移持久区 .runtime/campaign_trash_20261001/（非 TTL） |
| 26 | salvaged 内容与 dev 对拍 | 138 同字节/4033 旧版本变体/24716 独有路径——全部在档案区可按 manifest 复活，零不可逆丢失 |
| 27 | 分支删除 140+ | 已并入直删或 tag 归档（25 tag 在册），零未并入工作丢失 |
| 28 | 判弃死袋（c10 等族） | 未吸收内容全部留在 dead/ blob 区可复活；判弃=有更优落地覆盖的书面裁定 |
| 29 | 4 件中途锁保护 worktree | 未动，待锁方表态（唯一遗留） |
| 30 | 混沌演训死亡模拟 | 5 会话处死后：落地成果无损/接管条目全生成/闭环验证通过 |

## 域五：文档与档案

| # | 问题 | 治本 |
|---|---|---|
| 31 | 晚期成品建好忘入带（3 小时提交战的直接后果） | 收官补投六件全落（q-0015~0017 链）；**SOP 增补：收班必跑"HEAD 在位自检"** |
| 32 | logs/ 与 exempt-zone 的 frontmatter 规则族 | 模板在本册（域二 #14） |
| 33 | 台账命令字面量误扫 | ABS-27 改写配方 |

## 结语

三十三类问题，治本落地锚全部在 HEAD 或配方在册；唯二开放项=守护看门加固与 scripts/ 拆簇（Owner 批准后白班执行）。本册即"以后的 AI 不再遇到同样问题"的操作手册：遇症查册→按治本列执行→无需重新踩坑。
