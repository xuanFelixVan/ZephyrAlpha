---
created: 2026-10-01
ttl: task_bound
title: 提交链灾难四死因治本终报（st-commitfix-20261001 总包）
session: st-commitfix-20261001
---

# 提交链灾难定案+治本终报（2026-10-01 夜班总包）

## 一、定案：真灾难现场，非正常损耗

datasop 会话提交三件 SOP 的漫长逐袋死亡过程（用户原始问题）= 四种结构性死因叠加，
另叠加两波**工作面整面抹除事故**。数据：今日死信 145 封（累计 962），Popen 批量死
26 袋（00:50-01:59），CLAIM_REQUIRED 10 袋，debt-ratchet 连坐 16 起/7 会话。

### 四死因与治本（全部已落 HEAD）

| # | 死因 | 治本 commit | 语义 |
|---|------|------------|------|
| 1 | Popen 形态透传 run() 独参（timeout/capture_output/meta_out），26 袋批量死 | C1=6fc89459 | g2 遗产保全（盘面热修原样落地）+非 mock 回归三钉（C7=217c8ee7 轮询加固） |
| 2 | claim TTL×队列等待结构性矛盾（失败保留 300s vs 排队 45min+，过期+静默被第三方回收，在途零续命） | C3=8533f645+C2=fb357faa | ①_claim_expired_and_idle 队列在途保护（C355 同构）②renew_claim 原语+入队挂钩（2h，ZEPHYR_ENQUEUE_CLAIM_TTL_S） |
| 3 | debt-ratchet 无 own/foreign 键级区分，外来全仓债键连坐无辜提交人（16 起/7 会话） | C5=5a48e1ba | 净增键二分：own anchor 阻断/外来 warn+审计永不入册；棘轮记账出册语义零变化 |
| 4 | status 命令默认自举排空整条队列，可观测性丧失 | C4=a0c0299e | 默认只读，--bootstrap 显式 opt-in |

### 附带抢救（两人已消亡车道的在飞面保全）

- C2 内含 a3 遗产（热册并发阻断自动改道扩面，FOREIGN/HELD-OVERLAP→队列）
- C6=b7acad9b：a1 遗产六件套（env 死因分类 84 封死信可安全 requeue+幽灵闸 pool
  延伸），自 stash@{0}+死袋 blob 双源哈希验证恢复

## 二、工作面抹除事故（两波，P0 移交日班）

- 波1 03:41：本会话为验 ruff 基线误跑 `git stash`（共享工作树全局快照=违禁操作，
  元凶=本会话，已记配方"共享树禁全局 stash"）。
- 波2 05:34:10：~455 文件被复位至 HEAD（g1 披露四独立佐证"整面 stash 事件"）。
  实证关联：05:31 有 pytest 进程（pytest_23644）在跑 tests/git/test_git_commit_gateway.py
  的 stash 族测试 + debt_ratchet_lever 审计同一分钟写入。该套件 103 测试名义 tmp
  隔离，但**疑有测试默认构造真仓 gateway 驱动真仓 stash/复位机器**——P0 待审计。
- 双源恢复法：stash@{0}（03:41 快照）按文件 checkout + 死袋 blob 哈希验证回植。
- stash@{0} 遗留处置：内容已全部入 HEAD（本报告七笔+各车道自查恢复），日班可
  `git stash drop stash@{0}` 清库（drop 前抽查 `git stash show -p` 一眼）。

## 三、验证

- 循环检查连续两轮全绿：lock_files 族 46+ratchet 15+gateway 103+queue 119+
  landing 90+belt_daemon 31+Popen 三钉（第二轮合跑 404 passed）。
- 队列战后健康：pending 22→11，兄弟车道（a2 复活/g1/W3-HARVEST/matrix-final）
  恢复正常落地节奏。

## 四、移交清单（等 Owner/日班）

1. **C0 容量治理半成品**：scripts/ 平铺 121-123 反复超限（幻影复活+活跃车道持续
   投放）。已备好：两枚归档迁移件（run_ollama_exam.py/grep_coverage.ps1→
   _archive/，token+翻译条目登记过，被工作面抹除波反复打回）+ manifest/inventory
   再生成流程。**卡点**：capability/module_translation 两册正被 st-matrix-final
   活持（CREATE-GUARD 要求 token 册同批提交）。处方：等 matrix-final 落地释放后
   按本报告 recipe 十分钟内原子落地；或 Owner 裁定 gate 注册表给
   FOLDER-CAPACITY 加"仅新增文件触发"豁免（现修改也拦=打地鼠结构性死结）。
2. **pytest 隔离审计（P0）**：test_git_commit_gateway.py 全套 103 测试逐一验
   tmp_path 隔离，禁任何默认真仓构造（05:34 波主嫌）。
3. **存量红**：tests/resource/test_process_pool.py::TestProcessPoolZombie::
   test_dead_process_detected 稳定红（is_alive 探针，与本役改动零交集，HEAD 既有
   /环境态），归维护班。
4. **今日 145 封死信**：a1 的 env 分类已落地（C6），84 封瞬态假失败可批量
   `commit_queue.py requeue`；其余按 dead_reason 分诊（root_cause 票据在
   .runtime/commit_queue/dead/_root_cause/）。
5. **claim 双平面漂移**（.ailocks vs SessionRegistry held_files）：本役多次被
   两平面不同步咬（CLI acquire 不写 SR、claim_files 不写 .ailocks 的错位面），
   建议日班给 lock_files.acquire 加 SR 同步或 claim gate 双平面合并读。
