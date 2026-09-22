---
ttl: task_bound
session: st-integrated-bt-20260922
issue: IBT-RUN-LOGS-001
---

# 跑批日志留痕（四窗 run/挖掘/敏感性全程，原 .log 不入 git 打包件）

## ibt_mining_matrix.log
```
ts\backtest\translated\c4_a4543012b464_trend5.py:91: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:87: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  cand = align & reg_ok.reindex(close.index).fillna(False) & not_over
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:91: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[B] CAND-a4543012b464 done: {"W_IS": true, "W_OOS": true, "W_HOLDOUT": true, "W_POSTD": true}
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:70: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  g_idx = golden.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:71: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  d_idx = death.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:70: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  g_idx = golden.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:71: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  d_idx = death.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:70: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  g_idx = golden.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:71: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  d_idx = death.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:70: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  g_idx = golden.shift(1).reindex(dates).fillna(False).iloc[:, 0]
D:\ZephyrAlpha\scripts\backtest\translated\c4_e2e7f033d97c_kd_cross.py:71: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  d_idx = death.shift(1).reindex(dates).fillna(False).iloc[:, 0]
[B] CAND-e2e7f033d97c done: {"W_IS": true, "W_OOS": true, "W_HOLDOUT": true, "W_POSTD": true}
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[B] CAND-bd42540f86e4 done: {"W_IS": true, "W_OOS": true, "W_HOLDOUT": true, "W_POSTD": true}
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
[B] CAND-6a6ec8869ddb done: {"W_IS": true, "W_OOS": true, "W_HOLDOUT": true, "W_POSTD": true}
saved -> D:\ZephyrAlpha\docs\_working\integrated_backtest\ibt_data_matrix.json (wall 279.3s)

```

## ibt_run_W_HOLDOUT.log
```
[03:12:22] === W_HOLDOUT [2025-09-09..2026-09-08] ===
[03:12:25]   panel FACT-4f749668: 242x40 (2.6s, start=2025-09-09)
[03:12:26]   panel FACT-4228020a: 242x40 (0.8s, start=2025-09-09)
[03:12:27]   panel FACT-e293e217: 242x40 (0.7s, start=2025-09-09)
[03:12:27]   panel FACT-e831084c: 242x40 (0.7s, start=2025-09-09)
[03:12:28]   panel FACT-4b200528: 242x40 (0.8s, start=2025-09-09)
[03:12:43]   panel CAND-8d000bf3ccc3: 242x5216 (14.5s, start=2025-09-09)
[03:12:43]   panel CAND-c4ec6332c07f: 242x1 (0.2s, start=2025-09-09)
[03:12:43]   panel CAND-e3da6fa71af1: 242x1 (0.0s, start=2025-09-09)
[03:12:47]   panel CAND-4440d07f973f: 242x3195 (3.6s, start=2025-09-09)
[03:12:47]   panel CAND-eaddc3f9db4e: 242x1 (0.2s, start=2025-09-09)
[03:12:47]   panel CAND-d06cab686cef: 242x1 (0.1s, start=2025-09-09)
[03:12:47]   panel CAND-29eb91dbaf60: 242x1 (0.1s, start=2025-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:87: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  cand = align & reg_ok.reindex(close.index).fillna(False) & not_over
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:91: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[03:12:50]   panel CAND-a4543012b464: 242x307 (3.2s, start=2025-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[03:12:54]   panel CAND-bd42540f86e4: 242x330 (4.2s, start=2025-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
[03:13:01]   panel CAND-6a6ec8869ddb: 242x5216 (7.1s, start=2025-09-09)
[03:13:02] composed: (242, 5217) participants=15 skipped=[]
[03:13:03] traded symbols: 515 (stocks 513 + index legs ['000300', '000852'])
[03:13:41]   IBT-A: ret=-0.1224 sharpe=-1.389 dd=0.1645 trades=7567 (35.3s)
[03:14:16]   IBT-B: ret=-0.1210 sharpe=-1.635 dd=0.1548 trades=6738 (34.8s)
[03:14:46]   member FACT-4f749668: sharpe=-0.331 ret=-0.0528 dd=0.1626
[03:15:11]   member FACT-4228020a: sharpe=0.095 ret=0.0242 dd=0.1478
[03:15:37]   member FACT-e293e217: sharpe=-0.705 ret=-0.1109 dd=0.2314
[03:16:01]   member FACT-e831084c: sharpe=-0.175 ret=-0.0309 dd=0.1764
[03:16:26]   member FACT-4b200528: sharpe=-0.147 ret=-0.0376 dd=0.1503
[03:16:48]   member CAND-8d000bf3ccc3: sharpe=-0.094 ret=-0.0776 dd=0.4096
[03:17:06]   member CAND-c4ec6332c07f: sharpe=-0.058 ret=0.0023 dd=0.0962
[03:17:16]   member CAND-e3da6fa71af1: sharpe=0.218 ret=0.0401 dd=0.0445
[03:17:30]   member CAND-4440d07f973f: sharpe=-0.814 ret=-0.3585 dd=0.5499
[03:17:48]   member CAND-eaddc3f9db4e: sharpe=0.076 ret=0.0236 dd=0.0944
[03:18:06]   member CAND-d06cab686cef: sharpe=0.076 ret=0.0236 dd=0.0944
[03:18:29]   member CAND-29eb91dbaf60: sharpe=-0.236 ret=-0.0201 dd=0.0982
[03:18:52]   member CAND-a4543012b464: sharpe=-0.316 ret=-0.2408 dd=0.5406
[03:19:16]   member CAND-bd42540f86e4: sharpe=-1.111 ret=-0.1493 dd=0.2279
[03:19:41]   member CAND-6a6ec8869ddb: sharpe=-0.883 ret=-0.2491 dd=0.4118
[03:19:41] saved D:\ZephyrAlpha\docs\_working\integrated_backtest\artifacts\W_HOLDOUT\run_summary.json

```

## ibt_run_W_IS.log
```
s<char>>&&) @ 0x000000001939e3bf
4. MemoryTracker::allocImpl(long, bool, MemoryTracker*, double) @ 0x000000001939a72e
5. MemoryTracker::allocImpl(long, bool, MemoryTracker*, double) @ 0x0000000019399a9f
6. MemoryTracker::allocImpl(long, bool, MemoryTracker*, double) @ 0x0000000019399a9f
7. MemoryTracker::allocImpl(long, bool, MemoryTracker*, double) @ 0x0000000019399a9f
8. DB::IMergeTreeReader::IMergeTreeReader(std::shared_ptr<DB::IMergeTreeDataPartInfoForReader>, DB::NamesAndTypesList const&, std::unordered_map<String, DB::Field, std::hash<String>, std::equal_to<String>, std::allocator<std::pair<String const, DB::Field>>> const&, std::shared_ptr<DB::StorageSnapshot> const&, std::shared_ptr<DB::MergeTreeSettings const> const&, DB::UncompressedCache*, DB::MarkCache*, DB::MarkRanges const&, DB::MergeTreeReaderSettings const&, std::map<String, double, std::less<String>, std::allocator<std::pair<String const, double>>> const&) @ 0x000000001f251c96
9. DB::MergeTreeReaderCompact::MergeTreeReaderCompact(std::shared_ptr<DB::IMergeTreeDataPartInfoForReader>, DB::NamesAndTypesList, std::unordered_map<String, DB::Field, std::hash<String>, std::equal_to<String>, std::allocator<std::pair<String const, DB::Field>>> const&, std::shared_ptr<DB::StorageSnapshot> const&, std::shared_ptr<DB::MergeTreeSettings const> const&, DB::UncompressedCache*, DB::MarkCache*, DB::DeserializationPrefixesCache*, DB::MarkRanges, DB::MergeTreeReaderSettings, std::map<String, double, std::less<String>, std::allocator<std::pair<String const, double>>>, std::function<void (DB::ReadBufferFromFileBase::ProfileInfo)> const&, int) @ 0x000000001f5da7c0
10. DB::MergeTreeReaderCompactSingleBuffer::MergeTreeReaderCompactSingleBuffer<std::shared_ptr<DB::IMergeTreeDataPartInfoForReader> const&, DB::NamesAndTypesList const&, std::unordered_map<String, DB::Field, std::hash<String>, std::equal_to<String>, std::allocator<std::pair<String const, DB::Field>>> const&, std::shared_ptr<DB::StorageSnapshot> const&, std::shared_ptr<DB::MergeTreeSettings const> const&, DB::UncompressedCache*&, DB::MarkCache*&, DB::DeserializationPrefixesCache*&, DB::MarkRanges const&, DB::MergeTreeReaderSettings const&, std::map<String, double, std::less<String>, std::allocator<std::pair<String const, double>>> const&, std::function<void (DB::ReadBufferFromFileBase::ProfileInfo)> const&, int>(std::shared_ptr<DB::IMergeTreeDataPartInfoForReader> const&, DB::NamesAndTypesList const&, std::unordered_map<String, DB::Field, std::hash<String>, std::equal_to<String>, std::allocator<std::pair<String const, DB::Field>>> const&, std::shared_ptr<DB::StorageSnapshot> const&, std::shared_ptr<DB::MergeTreeSettings const> const&, DB::UncompressedCache*&, DB::MarkCache*&, DB::DeserializationPrefixesCache*&, DB::MarkRanges const&, DB::MergeTreeReaderSettings const&, std::map<String, double, std::less<String>, std::allocator<std::pair<String const, double>>> const&, std::function<void (DB::ReadBufferFromFileBase::ProfileInfo)> const&, int&&) @ 0x000000001f475dc3
11. DB::createMergeTreeReader(std::shared_ptr<DB::IMergeTreeDataPartInfoForReader> const&, DB::NamesAndTypesList const&, std::shared_ptr<DB::StorageSnapshot> const&, std::shared_ptr<DB::MergeTreeSettings const> const&, DB::MarkRanges const&, std::unordered_map<String, DB::Field, std::hash<String>, std::equal_to<String>, std::allocator<std::pair<String const, DB::Field>>> const&, DB::UncompressedCache*, DB::MarkCache*, DB::DeserializationPrefixesCache*, DB::MergeTreeReaderSettings const&, std::map<String, double, std::less<String>, std::allocator<std::pair<String const, double>>> const&, std::function<void (DB::ReadBufferFromFileBase::ProfileInfo)> const&) @ 0x000000001f25921d
12. DB::MergeTreeReadTask::createReaders(std::shared_ptr<DB::MergeTreeReadTaskInfo const> const&, DB::MergeTreeReadTask::Extras const&, DB::MarkRanges const&, std::vector<DB::MarkRanges, std::allocator<DB::MarkRanges>> const&)::$_0::operator()(DB::NamesAndTypesList const&, bool) const @ 0x000000001f629bd4
13. DB::MergeTreeReadTask::createReaders(std::shared_ptr<DB::MergeTreeReadTaskInfo const> const&, DB::MergeTreeReadTask::Extras const&, DB::MarkRanges const&, std::vector<DB::MarkRanges, std::allocator<DB::MarkRanges>> const&) @ 0x000000001f627eb7
14. DB::MergeTreeReadPoolBase::createTask(std::shared_ptr<DB::MergeTreeReadTaskInfo const>, DB::MarkRanges, std::vector<DB::MarkRanges, std::allocator<DB::MarkRanges>>, DB::MergeTreeReadTask*, std::shared_ptr<DB::RuntimeDataflowStatisticsCacheUpdater>) const @ 0x000000001f652cf9
15. DB::MergeTreeReadPoolBase::createTask(std::shared_ptr<DB::MergeTreeReadTaskInfo const>, DB::MarkRanges, DB::MergeTreeReadTask*, std::shared_ptr<DB::RuntimeDataflowStatisticsCacheUpdater>) const @ 0x000000001f654087
16. DB::MergeTreeReadPoolInOrder::getTask(unsigned long, DB::MergeTreeReadTask*) @ 0x00000000205d167d
17. DB::MergeTreeSelectProcessor::read() @ 0x000000001f640ad1
18. DB::MergeTreeSource::tryGenerate() @ 0x00000000205d2bbc
19. DB::ISource::work() @ 0x000000001feb7ac1
20. DB::ExecutionThreadContext::executeTask() @ 0x000000001fed9f0d
21. DB::PipelineExecutor::executeStepImpl(unsigned long, DB::IAcquiredSlot*, std::atomic<bool>*) @ 0x000000001fec91c4
22. DB::PipelineExecutor::execute(unsigned long, bool) @ 0x000000001fec7330
23. void std::__function::__policy_func<void ()>::__call_func[abi:fqe220101]<ThreadFromGlobalPoolImpl<true, true>::ThreadFromGlobalPoolImpl<DB::PullingAsyncPipelineExecutor::pull(DB::Chunk&, unsigned long)::$_0>(DB::PullingAsyncPipelineExecutor::pull(DB::Chunk&, unsigned long)::$_0&&)::'lambda'()>(std::__function::__policy_storage const*) @ 0x000000001fee3d51
24. void std::__function::__policy_func<void ()>::__call_func[abi:fqe220101]<startThreadFromGlobalPool(std::shared_ptr<ThreadFromGlobalPoolState>, std::function<void ()>, unsigned long, unsigned long, bool, bool)::$_0>(std::__function::__policy_storage const*) @ 0x0000000019507c43
25. ThreadPoolImpl<std::thread>::ThreadFromThreadPool::worker() @ 0x00000000194fca1d
26. void* std::__thread_proxy[abi:fqe220101]<std::tuple<std::unique_ptr<std::__thread_struct, std::default_delete<std::__thread_struct>>, void (ThreadPoolImpl<std::thread>::ThreadFromThreadPool::*)(), ThreadPoolImpl<std::thread>::ThreadFromThreadPool*>>(void*) @ 0x0000000019504d5a
27. ? @ 0x000000000009cb84
28. ? @ 0x0000000000129ecc

HTTP query 失败: status=500
CH query 失败(TCP+HTTP 均失败): SELECT symbol FROM c1_market.st_stock_list FINAL WHERE trade_date = (SELECT max(trade_date) FROM c1_market.st_stock_list FINAL WHERE trade_date <= '2023-04-24')
st_stock_list 快照查询为空（2023-04-24），ST 兜底降级为非 ST 口径
HTTP query 失败: status=500
CH query 失败(TCP+HTTP 均失败): SELECT symbol, limit_up, limit_down, limit_pct, st_flag FROM c1_market.stk_limit FINAL WHERE trade_date = '2023-06-19' AND symbol IN ('000063','000066','000651','000858','000977','002049','002456','00
[01:48:33]   member FACT-4228020a: sharpe=-0.416 ret=-0.1874 dd=0.3453
[01:52:39]   member FACT-e293e217: sharpe=-0.586 ret=-0.2696 dd=0.3431
[01:57:07]   member FACT-e831084c: sharpe=-0.819 ret=-0.3957 dd=0.4334
[02:01:47]   member FACT-4b200528: sharpe=-0.530 ret=-0.2887 dd=0.3668
[02:06:53]   member CAND-8d000bf3ccc3: sharpe=0.053 ret=0.0167 dd=0.6471
[02:10:14]   member CAND-c4ec6332c07f: sharpe=-0.283 ret=-0.1337 dd=0.3742
[02:12:19]   member CAND-e3da6fa71af1: sharpe=0.168 ret=0.1911 dd=0.3433
[02:15:08]   member CAND-4440d07f973f: sharpe=-0.928 ret=-0.9127 dd=0.9175
[02:18:42]   member CAND-eaddc3f9db4e: sharpe=-0.250 ret=-0.1059 dd=0.3666
[02:22:26]   member CAND-d06cab686cef: sharpe=-0.274 ret=-0.1256 dd=0.3719
[02:26:41]   member CAND-29eb91dbaf60: sharpe=-0.309 ret=-0.1095 dd=0.3676
[02:30:58]   member CAND-a4543012b464: sharpe=0.051 ret=-0.1669 dd=0.7973
[02:35:41]   member CAND-bd42540f86e4: sharpe=-0.015 ret=-0.0269 dd=0.4088
[02:40:15]   member CAND-6a6ec8869ddb: sharpe=0.370 ret=0.5317 dd=0.3901
[02:40:15] saved D:\ZephyrAlpha\docs\_working\integrated_backtest\artifacts\W_IS\run_summary.json

```

## ibt_run_W_OOS.log
```
[02:40:16] === W_OOS [2024-01-01..2025-09-08] ===
[02:40:19]   panel FACT-4f749668: 409x40 (2.7s, start=2024-01-01)
[02:40:20]   panel FACT-4228020a: 409x40 (1.3s, start=2024-01-01)
[02:40:21]   panel FACT-e293e217: 409x40 (1.2s, start=2024-01-01)
[02:40:22]   panel FACT-e831084c: 409x40 (1.2s, start=2024-01-01)
[02:40:24]   panel FACT-4b200528: 409x40 (1.2s, start=2024-01-01)
[02:40:42]   panel CAND-8d000bf3ccc3: 409x5129 (18.3s, start=2024-01-01)
[02:40:42]   panel CAND-c4ec6332c07f: 409x1 (0.4s, start=2024-01-01)
[02:40:42]   panel CAND-e3da6fa71af1: 409x1 (0.0s, start=2024-01-01)
[02:40:47]   panel CAND-4440d07f973f: 409x3161 (4.9s, start=2024-01-01)
[02:40:47]   panel CAND-eaddc3f9db4e: 409x1 (0.2s, start=2024-01-01)
[02:40:47]   panel CAND-d06cab686cef: 409x1 (0.1s, start=2024-01-01)
[02:40:48]   panel CAND-29eb91dbaf60: 409x1 (0.1s, start=2024-01-01)
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:87: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  cand = align & reg_ok.reindex(close.index).fillna(False) & not_over
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:91: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[02:40:51]   panel CAND-a4543012b464: 409x311 (3.7s, start=2024-01-01)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[02:40:58]   panel CAND-bd42540f86e4: 409x334 (6.4s, start=2024-01-01)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
[02:41:07]   panel CAND-6a6ec8869ddb: 409x5129 (9.6s, start=2024-01-01)
[02:41:08] composed: (409, 5130) participants=15 skipped=[]
[02:41:09] traded symbols: 767 (stocks 765 + index legs ['000300', '000852'])
[02:42:51]   IBT-A: ret=0.1193 sharpe=0.336 dd=0.1595 trades=13935 (95.8s)
[02:43:52]   IBT-B: ret=0.0642 sharpe=0.163 dd=0.2157 trades=13113 (60.6s)
[02:44:40]   member FACT-4f749668: sharpe=0.394 ret=0.1600 dd=0.2072
[02:45:31]   member FACT-4228020a: sharpe=0.574 ret=0.2456 dd=0.2129
[02:46:20]   member FACT-e293e217: sharpe=0.918 ret=0.4335 dd=0.1928
[02:47:12]   member FACT-e831084c: sharpe=0.392 ret=0.1635 dd=0.2715
[02:48:06]   member FACT-4b200528: sharpe=0.306 ret=0.1232 dd=0.2534
[02:48:56]   member CAND-8d000bf3ccc3: sharpe=0.508 ret=0.2233 dd=0.3753
[02:49:41]   member CAND-c4ec6332c07f: sharpe=0.997 ret=0.3658 dd=0.1536
[02:50:07]   member CAND-e3da6fa71af1: sharpe=0.967 ret=0.5109 dd=0.2135
[02:50:44]   member CAND-4440d07f973f: sharpe=0.622 ret=0.4313 dd=0.3830
[02:51:29]   member CAND-eaddc3f9db4e: sharpe=0.684 ret=0.1844 dd=0.1167
[02:52:19]   member CAND-d06cab686cef: sharpe=0.684 ret=0.1844 dd=0.1167
[02:53:01]   member CAND-29eb91dbaf60: sharpe=0.418 ret=0.0971 dd=0.0870
[02:53:42]   member CAND-a4543012b464: sharpe=0.036 ret=-0.1392 dd=0.5997
[02:54:33]   member CAND-bd42540f86e4: sharpe=0.326 ret=0.1236 dd=0.2863
[02:55:22]   member CAND-6a6ec8869ddb: sharpe=0.058 ret=-0.0737 dd=0.3756
[02:55:22] saved D:\ZephyrAlpha\docs\_working\integrated_backtest\artifacts\W_OOS\run_summary.json
[02:56:21]   sens slip=0bp: sharpe=0.475
[02:57:19]   sens slip=5bp: sharpe=0.286
[02:58:24]   sens slip=10bp: sharpe=0.049
[02:59:24]   sens slip=20bp: sharpe=-0.393
[03:00:26]   sens slip=40bp: sharpe=-1.226
Traceback (most recent call last):
  File "D:\ZephyrAlpha\.runtime\tmp\ibt_runner.py", line 381, in <module>
    main()
  File "D:\ZephyrAlpha\.runtime\tmp\ibt_runner.py", line 374, in main
    result, _pf, _ex = run_engine(data, signals_a, variant="IBT-A-zerocost", schedule=None, zero_cost=True)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\ZephyrAlpha\.runtime\tmp\ibt_runner.py", line 232, in run_engine
    config = BacktestConfig(**cfg_kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BacktestConfig.__init__() got an unexpected keyword argument 'min_commission'

```

## ibt_run_W_POSTD.log
```
[03:29:15] === W_POSTD [2026-09-09..2026-09-18] ===
[03:29:17]   panel FACT-4f749668: 8x40 (1.6s, start=2026-09-09)
[03:29:17]   panel FACT-4228020a: 8x40 (0.2s, start=2026-09-09)
[03:29:17]   panel FACT-e293e217: 8x40 (0.2s, start=2026-09-09)
[03:29:17]   panel FACT-e831084c: 8x40 (0.2s, start=2026-09-09)
[03:29:17]   panel FACT-4b200528: 8x40 (0.2s, start=2026-09-09)
[03:29:23]   panel CAND-8d000bf3ccc3: 8x5221 (5.7s, start=2026-09-09)
[03:29:23]   panel CAND-c4ec6332c07f: 8x1 (0.1s, start=2026-09-09)
[03:29:23]   panel CAND-e3da6fa71af1: 8x1 (0.0s, start=2026-09-09)
[03:29:24]   panel CAND-4440d07f973f: 8x3196 (1.2s, start=2026-09-09)
[03:29:24]   panel CAND-eaddc3f9db4e: 8x1 (0.1s, start=2026-09-09)
[03:29:25]   panel CAND-d06cab686cef: 8x1 (0.1s, start=2026-09-09)
[03:29:25]   panel CAND-29eb91dbaf60: 8x1 (0.0s, start=2026-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:87: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  cand = align & reg_ok.reindex(close.index).fillna(False) & not_over
D:\ZephyrAlpha\scripts\backtest\translated\c4_a4543012b464_trend5.py:91: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[03:29:26]   panel CAND-a4543012b464: 8x280 (1.1s, start=2026-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_bd42540f86e4_pe_pb.py:60: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  c_idx = cand.shift(1).reindex(dates).fillna(False)
[03:29:26]   panel CAND-bd42540f86e4: 8x300 (0.3s, start=2026-09-09)
D:\ZephyrAlpha\scripts\backtest\translated\c4_6a6ec8869ddb_momentum62.py:74: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
  s_idx = sig.shift(1).reindex(dates).fillna(False)
[03:29:28]   panel CAND-6a6ec8869ddb: 8x5221 (2.2s, start=2026-09-09)
[03:29:28] composed: (8, 5222) participants=9 skipped=[('CAND-8d000bf3ccc3', 'all-zero weight rows'), ('CAND-e3da6fa71af1', 'all-zero weight rows'), ('CAND-eaddc3f9db4e', 'all-zero weight rows'), ('CAND-d06cab686cef', 'all-zero weight rows'), ('CAND-29eb91dbaf60', 'all-zero weight rows'), ('CAND-bd42540f86e4', 'all-zero weight rows')]
[03:29:29] traded symbols: 61 (stocks 60 + index legs ['000300'])
[03:29:30]   IBT-A: ret=-0.0214 sharpe=0.000 dd=0.0749 trades=194 (0.5s)
[03:29:30]   IBT-B: ret=-0.0214 sharpe=0.000 dd=0.0749 trades=194 (0.5s)
[03:29:31]   member FACT-4f749668: sharpe=0.000 ret=0.0138 dd=0.0188
[03:29:31]   member FACT-4228020a: sharpe=0.000 ret=0.0159 dd=0.0142
[03:29:31]   member FACT-e293e217: sharpe=0.000 ret=0.0165 dd=0.0154
[03:29:32]   member FACT-e831084c: sharpe=0.000 ret=0.0060 dd=0.0221
[03:29:32]   member FACT-4b200528: sharpe=0.000 ret=0.0205 dd=0.0218
[03:29:32]   member CAND-8d000bf3ccc3: 窗内零信号（短路，不入引擎）
[03:29:32]   member CAND-c4ec6332c07f: sharpe=0.000 ret=0.0027 dd=0.0000
[03:29:32]   member CAND-e3da6fa71af1: 窗内零信号（短路，不入引擎）
[03:29:33]   member CAND-4440d07f973f: sharpe=0.000 ret=-0.0897 dd=0.1655
[03:29:33]   member CAND-eaddc3f9db4e: 窗内零信号（短路，不入引擎）
[03:29:33]   member CAND-d06cab686cef: 窗内零信号（短路，不入引擎）
[03:29:33]   member CAND-29eb91dbaf60: 窗内零信号（短路，不入引擎）
[03:29:33]   member CAND-a4543012b464: sharpe=0.000 ret=0.0231 dd=0.0029
[03:29:33]   member CAND-bd42540f86e4: 窗内零信号（短路，不入引擎）
[03:29:33]   member CAND-6a6ec8869ddb: sharpe=0.000 ret=0.0038 dd=0.0226
[03:29:33] saved D:\ZephyrAlpha\docs\_working\integrated_backtest\artifacts\W_POSTD\run_summary.json

```

## ibt_sens_final.log
```
[03:22:12] traded symbols: 767 (stocks 765 + index legs ['000300', '000852'])
slip=0: sharpe=0.4748 ret=0.1658
slip=5: sharpe=0.2859 ret=0.1029
slip=10: sharpe=0.0492 ret=0.0294
slip=20: sharpe=-0.3935 ret=-0.0920
slip=40: sharpe=-1.2263 ret=-0.2810
zero_cost: sharpe=0.8373 ret=0.2995
FINAL sens saved (same-batch)

```

## ibt_sens_is.log
```
[04:10:38] traded symbols: 1667 (stocks 1664 + index legs ['000016', '000300', '000852'])
slip=0: sharpe=-0.1136 ret=-0.0153
slip=5: sharpe=-0.3168 ret=-0.1398
slip=10: sharpe=-0.5960 ret=-0.2790
slip=20: sharpe=-1.1606 ret=-0.4763
slip=40: sharpe=-2.3084 ret=-0.7152
zero_cost: sharpe=0.2477 ret=0.2649
IS sens saved

```
