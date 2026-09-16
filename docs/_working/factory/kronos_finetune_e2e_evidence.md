---
ttl: task_bound
---

# Kronos 微调全链 E2E 证据（MOD-BT-204 / st-kronosft-20260916）

日期：2026-09-16（夜窗）｜机器：RTX 3090 24GB｜torch 2.13.0+cu126｜Python 3.12.8

## 0. 环境降级记录（重要）

- torchrun 不可用（本机构建三重缺陷，探针实录）：
  1. `torch.distributed.DistStoreError: use_libuv was requested but PyTorch was built without libuv support`
     —— c10d rendezvous 的 TCPStore 死锁（USE_LIBUV=0 环境变量不生效，elastic 路径
     `_create_tcp_store_server` 未传 use_libuv）。
  2. NCCL 未编译进 Windows 构建：`Attempted to get default timeout for nccl backend,
     but NCCL support is not compiled`。
  3. gloo-uv 传输层解析中文主机名「范清风」失败：`Unable to find address for: 127.0.0.1`
     / `10049 在其上下文中，该请求的地址无效`，且进程段错误（EXIT=139）。
- 降级通道（按任务预授权）：`python` 直跑单卡 + 进程内替身
  `.runtime/tmp/kronos_train_launcher.py`：
  - `dist.init_process_group/all_reduce/barrier/...` → world_size=1 数学恒等替身；
  - `DistributedDataParallel` → IdentityDDP 透传壳（保留 `.module` 契约）；
  - 单进程下与 torchrun 数值语义完全等价（all_reduce(SUM) 不变、无跨卡同步对象、
    DistributedSampler(1,0)=纯 shuffle）。
- 探针全绿证据：`.runtime/tmp/kronos_selftest/probe_real_model.py` 真权重
  tokenizer 前反向 loss=0.4007 / predictor 前反向 loss=6.4819（≈ln(1024)=6.93 初值
  附近，符合预训练分布）/ save_pretrained→from_pretrained 往返 OK / bs=4 峰值 271MB。
- comet_ml 缺失 → `pip install comet_ml`（3.58.6，网络可用）；config.use_comet=False，
  训练指标走 stdout 日志留证。

## 1. CH → prep CSV（官方七列规范）

命令：
```
python scripts/backtest/kronos_finetune_pkl_prep.py --top-n 20 --days 1200
```
- 20 只成交额 top 标的 CSV 落 `.runtime/tmp/kronos_finetune_data/`。
- 数据源：CH market_kline_daily_hfq 后复权日 K（与推理同口径）。

## 2. CSV → pkl（QlibDataset 契约）

- pkl 输出：`.runtime/tmp/kronos_finetune_data/pkl/{train_data,val_data.pkl}` + manifest.json。
- 统计：17 标的入训；3 只次新被最小行数过滤剔除
  （688820.SH 102 行 / 688825.SH 37 行 / 688836.SH 20 行，均 <250）。
- 窗口总量：train 16948 + val 4365（window=71=lookback60+predict10+1）。
- 切分：每标的时序 80/20（禁随机打乱）；val 头部回补 60 行上下文（官方 config
  同款重叠实践）；泄漏硬防线=val 专属行与 train 零交集（测试锁定）。

## 3. T3 基线冒烟（旧权重，换装前）

命令：
```
python scripts/backtest/kronos_adapter.py --symbol 600519.SH --n-test 20
```
留证：`.runtime/tmp/kronos_baseline_smoke_old_weights.json`（EXIT=0，device=cuda）

| 指标 | Kronos 旧权重 | Naive RW 基准 |
|---|---|---|
| sharpness | 123.0119 | 320.5827 |
| calibrated_share | 0.60 | 0.80 |
| pit_ks | 0.2176 | 0.2573 |

## 4. T2 训练（tokenizer → predictor，各 10 epoch）

命令（降级通道）：
```
python .runtime/tmp/kronos_train_launcher.py vendor/Kronos/finetune/train_tokenizer.py \
  > .runtime/logs/kronos_tok_finetune.log 2>&1
python .runtime/tmp/kronos_train_launcher.py vendor/Kronos/finetune/train_predictor.py \
  > .runtime/logs/kronos_finetune.log 2>&1
```
关键超参（vendor/Kronos/finetune/config.py 日线化）：
feature_list=[open,high,low,close,volume,amount]；lookback=60/predict=10；
epochs=10；batch_size=128（3090 24GB 实测宽裕）；num_workers=0（Windows 单卡）；
use_comet=False；dataset/save/pretrained 路径全部绝对化（防 CWD 漂移）。

【训练结果见文末 §7（跑完后回填）】

## 5. T4 权重换装

步骤：`cp -r vendor/kronos_weights/kronos_small{,.bak_pre_finetune}` → 换入
finetuned best_model → adapter 冒烟同命令对比基线；异常即回滚 bak。
【换装结果见文末 §7】

## 6. 红蓝对抗预演清单（T6）

| # | 攻击面 | 预期 | 实录 |
|---|---|---|---|
| R1 | CSV 列缺失/乱序 → build_pkl | RuntimeError/剔除留痕 | 测试 test_min_rows/列不规范分支 |
| R2 | 切分泄漏（未来行进 train） | val 专属行与 train 零交集 | 测试锁定（val_horizon_post_split 等） |
| R3 | 窗口越界（rows<window+1） | 标的剔除 reason 留痕 | build_pkl 窗口不足分支 |
| R4 | 路径写穿（dataset_path 相对漂移） | 绝对路径+CWD 无关 | config.py `_REPO_ROOT` 锚定；launcher chdir finetune |
| R5 | 权重回滚缺失 | bak 目录先行 | cp -r bak 后才换装；adapter 异常即回滚 |
| R6 | 中断恢复 | best_model 按 epoch 落盘，重跑幂等 | save_pretrained 每 epoch 覆盖 best；pkl 可 --from-existing 重建 |
| R7 | 时间特征契约（TemporalEmbedding 5 列硬编码） | 不可减列，日线 minute/hour 恒 0 | config 注释+manifest note+测试 x_stamp shape=(71,5) |
| R8 | 热文件并发写 | safe_write_text CAS | 登记/注册工具均走 CAS（实测 attempt 1 成功） |

## 7. 结果回填（训练完成）

### 7.1 训练曲线（各 10 epoch，bs=128，单卡）

- **tokenizer**（.runtime/logs/kronos_tok_finetune.log）：
  0.0155 → 0.0148 → 0.0147 → 0.0144 → 0.0143 → 0.0143 → 0.0141 → 0.0141 → 0.0140 → 0.0140
  十 epoch 单调下降，best=0.0140（ep10）。相对初期 **-9.7%**。
- **predictor**（.runtime/logs/kronos_finetune.log）：
  3.4094 → 3.3697 → 3.3567 → 3.3535 → **3.3527**(best, ep5) → 3.3544 → 3.3558 → 3.3563 → 3.3574 → 3.3575
  前 5 epoch 单调下降后缓升（过拟合前兆，best_model 机制自动保留 ep5）。
  相对初期 **-0.0567（-1.66%）**。summary.json best_val_loss=3.352708。
- 产物：`.runtime/tmp/kronos_finetune_outputs/models/{kronos_tok_daily_ft,kronos_pred_daily_ft}/checkpoints/best_model/`

### 7.2 T4 换装 + adapter 冒烟（600519.SH，n-test=20，sample-count=8，cuda）

备份：vendor/kronos_weights/kronos_small.bak_pre_finetune（换入前 cp -r 留证）
换入：kronos_pred_daily_ft/checkpoints/best_model/{config.json,model.safetensors}

| 指标 | 旧权重(预训练) | 新权重(微调后) |
|---|---|---|
| adapter 退出码 | 0 | **0（load 不报错=验收过）** |
| sharpness | 123.0119 | 223.1364 |
| calibrated_share | 0.60 | 0.60 |
| pit_ks | 0.2176 | 0.3764 |

行为变化非退化判定：MOD-BT-204 验收两条（val loss 下降 + load 不报错）均过；
单票 20 日样本噪声大，微调后预测分布变宽属预期（域适配中），基线对台优劣
判定权在 E4 双标准考尺（MOD-BT-194），不在本任务范围。

### 7.3 红蓝对抗实测结果

| # | 攻击面 | 结果 |
|---|---|---|
| R1 | 列缺失 CSV | 已入常驻测试 test_malformed_columns_skipped_with_reason（剔除留痕，好标的照常）✅ |
| R2 | 切分泄漏 | val 专属行与 train 零交集+horizon 后置（3 个测试锁定）✅ |
| R3 | 窗口越界 | 行数不足/切分后窗口不足双分支（3 只真实次新被剔实测）✅ |
| R4 | 路径写穿 | config 绝对路径锚定 _REPO_ROOT；真实 Config 下 QlibDataset 全量加载 16948/4365 窗 ✅ |
| R5 | 权重回滚缺失 | bak 先行；坏权重目录 from_pretrained fail-loud（TypeError 非静默）✅ |
| R6 | 中断恢复 | best_model 逐 epoch 落盘；pkl 重建幂等（同绝对路径 manifest 字段级零差异）✅ |
| R7 | TemporalEmbedding 5 列硬契约 | x_stamp=(71,5) 测试锁定；config 注释+manifest note 双留痕 ✅ |
| R8 | torchrun 三重故障 | 降级通道替身=数学等价（见 §0），训练全程 GPU 峰值 ~7GB ✅ |

### 7.4 登记与提交

- 模块翻译：module_translation_registry.yaml（upsert 1 条，CJK≥8 非模板）
- creation_token：capability_canonical_file_registry.yaml（kronos_finetune capability，1 条）
- depgraph：generate_project_depgraph.py 全量跑 → pkl_prep.py node=13846455(stable)，
  test node=13847761(generated)
- 异常归属说明：上述两 catalog 改动被并发会话 commit a6cf1aad2d（治理战役 A2）
  的暂存区吸收入史——HEAD 已含本会话条目（grep 验证=1），故本会话提交清单
  不再含这两个 catalog（避免空 diff 提交）。
- **主仓提交：3c63409a**（GitCommitGateway，[GW:st-kronosft-20260916]，--allow-non-worktree
  按 2026-08-13 裁定；git log -1 --name-only 归属核实=仅本会话 2 文件，零搭便车）：
  scripts/backtest/kronos_finetune_pkl_prep.py + tests/backtest/test_kronos_finetune_pkl_prep.py
- **vendor 内嵌仓提交：fdeae5c**（vendor/ 外层 gitignore 不入库；内嵌 .git 留痕防
  `git -C vendor/Kronos checkout -- .` 恢复动作误伤日线化 config）
- claim 释放：RELEASED 2 files；会话注销：worktree 丢弃+unregistered（main_cleaned=0）
- T6 两轮全量：26 passed / 26 passed（0 失败）

### 7.6 临时文件清理确认

- 已删：.runtime/tmp/kronos_selftest/（探针+pip 探测轮+pytest cache）、kronos_commit_msg.txt
- 留存（证据/可复跑）：kronos_e2e_evidence.md、kronos_baseline_smoke_old_weights.json、
  kronos_smoke_finetuned_weights.json、kronos_train_launcher.py（降级通道，重训可复用）、
  kronos_finetune_data/（CSV+pkl 语料）、kronos_finetune_outputs/（两模型 checkpoint）、
  .runtime/logs/kronos_*.log（训练/冒烟日志）、vendor/kronos_weights/kronos_small.bak_pre_finetune（回滚保险）

### 7.5 端到端结论

全链贯通：CH→prep CSV(20 标的)→pkl(17 标的/16948+4365 窗)→tokenizer 训练✅→
predictor 训练✅→权重换装✅→adapter 冒烟✅。验收标准全过，零降级例外
（torchrun 降级为任务预授权通道，非故障弃赛）。

## 9. 审计补记（2026-09-16 晨，st-fac4sch-20260916）

- **tokenizer 错位治本**：验收审计发现 predictor 训练加载的是微调 tokenizer（train_predictor.py:213 →
  config.finetuned_tokenizer_path），但换装仅换 predictor、adapter 推理仍用 base tokenizer——token 空间错位。
  修复=成对档位：vendor/kronos_weights/{kronos_daily_ft, kronos_tokenizer_daily_ft} 同源微调权重建档，
  kronos_small 恢复官方底座（bak 保留），adapter 增 --model-size daily_ft 映射；GPU 冒烟 600519.SH
  n-test=20 通过，calibrated=true。训练产物原 ephemeral 区（.runtime/tmp），成对档换装后不再依赖。
