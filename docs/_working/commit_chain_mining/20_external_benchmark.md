---
ttl: task_bound
---

# 环节10：业界对标——提交队列/门禁分层/租约调度（全网向）

> 挖矿：子代理 2026-09-22（真实检索/直取官方文档，全部 URL 在案；429 受阻矿脉如实记录）。全文存档于挖矿批次产出，本文存决策精华。

## A 对标矩阵（13 案）

GitHub Merge Queue（失败即踢+批上限+等待超时兜底）｜bors-ng（失败批二分定位）｜pre-commit（声明序=执行序+fail_fast+stages）｜lint-staged（变更面喂参+改写自动回暂存+超长分块）｜etcd Lease（TTL+KeepAlive+**过期删除产生 delete 事件**）｜ZooKeeper 锁配方（临时节点+只 watch 前驱零惊群）｜Fencing Token（Kleppmann 2016，单调令牌拒旧写）｜PG Advisory Lock+SingleFlight（连接活性=隐式心跳/同 key 合并）｜Nx affected（变更面→依赖图只跑受影响）｜Google 小 CL（目标 100 行/1000 过大）+SmartBear/Cisco（200-400 行 60 分钟）｜CI 队列可观测（queued+created_at/started_at 惯例）｜Buildkite priority（待验证）｜Claude 并行会话（每 agent 独立 worktree 开 PR）。

## B 五病对标结论（病号对应本战役实测）

| 病 | 业界成熟对应 | 本战役吸收 |
|----|------------|-----------|
| ①失败磨到终点才暴露 | pre-commit fail-fast 车道/GH MQ 失败即踢 | R1 入队预检车道+D3 两段式（**不用全局 fail_fast**：own/foreign 归因语义需要全量输出，两段式=等价收益零语义险） |
| ②大批无上限 | Google 小 CL/GH MQ merge limits/lint-staged 分块 | R2 批上限 40+逃生旗（业界带宽数据：40 居 GH limits 与 SmartBear 心智带内） |
| ③门禁不分贵贱 | pre-commit 声明序/lint-staged 重写门后置 | 两段式通道（重写型 ruff-format 留全段；确定性 7 hooks 前置） |
| ④无兜底唤醒 | etcd「租约过期删除=delete 事件」/ZK watch 前驱 | R4 watchdog 观察 serializer.lease，删除即 poke（单机文件 watch=etcd 事件语义等效实现） |
| ⑤盲轮询 | GH queued+时长呈现/ZK 单点唤醒 | R5 status 位置+已等时长+租约持有者（比 GitHub 更进一步给位置号） |

## C 不移植清单（跨域不同对象，留痕防重复挖）

etcd/ZK/PG 共识组件本体（单机文件语义已等效）｜staging 分支重测工作流（serializer 暂存语义已覆盖）｜Buildkite agent 池（单 serializer）｜100 行目标值（AI 生成批过严，取上限不取目标）｜/batch 5-30 代理预算（无此成本模型）。挂起观察：bors 二分定位（若 R1/R2 后大批失败已罕见则永久挂起）｜fencing 序号（租约 mtime+ref 双查近似已够）｜depgraph 变更面门禁裁剪（own-scope 化改造，工程最大最后做）。

## D 挖矿日志表

13 矿脉 15 轮：signal 12/受阻 1（homu，bors-ng 覆盖同类语义无缺口）/noise 1（OpenAI 多代理专项无增量）/待验证 2（Buildkite priority、GH API 字段细节——单来源只登记不入图）。
