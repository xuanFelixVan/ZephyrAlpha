---
module_id: KE-082
status: active
title: 1.2 为什么要做成"正交视图"而不是 14 层业务之外再加一层
category: documentation
---

# 1.2 为什么要做成"正交视图"而不是 14 层业务之外再加一层

1.2 为什么要做成"正交视图"而不是 14 层业务之外再加一层

**核心判断**：业务分层（What）和运行平面（How/When）是**两把正交的尺子**，用哪把尺子切代码取决于你想回答什么问题。强行把"延迟特征"塞进"业务本体"会造成双重漂移：

| 混为一层的后果（反例）| 正交切分的收益（本视图采纳）|
|---|---|
| 例如把 `l14_hot_path/` 建成独立业务层 → L06 `trade_execution/` 订单管理和 L14 Hot Path 下单**同一业务概念被两层承担** → ACL 失效 / OCP 契约断裂 / 因子注册表跨层 | L06 仍完整承担"交易执行"业务本体，其中 `oms/` 子模块被打 `@RuntimePlane.WARM_PATH` 标签、`sor/` 打 `@RuntimePlane.HOT_PATH` 标签 → 业务语义保持 + 运行特征独立标注 |
| 未来新增"Cold Path Backfill 专用层"时必须再加一层 → 层数无上限膨胀 | 新增平面仅在本视图 §5 技术选型 + §3 映射矩阵打补丁，14 层业务不动 |
| AI 协作者找代码时必须同时记住"业务归属 + 延迟归属"两个维度在同一路径里 → 目录歧义 | AI 协作者按业务找代码（`src/zephyr/ex_core/sor/`）+ 按装饰器 / frontmatter 查运行平面，两把尺子各自清晰 |

**业界证据**：

| 机构 | 业务切分 | 运行平面切分 | 是否混合成一层 |
|---|---|---|---|
| **Citadel Securities** | 按 Asset Class + Strategy Family | Hot Path（FPGA / C++）/ Warm Path（Python research）分库 | ❌ 不混 |
| **Jane Street** | 按 Desk + Market | OCaml Hot Path / OCaml + Python Research 分 runtime | ❌ 不混 |
| **Two Sigma** | 按 Capability（Alpha / Risk / Execution）| C++ Hot / Python Warm / Spark Cold 分集群 | ❌ 不混 |
| **Jump Trading** | 按 Market + Instrument | Hardware-accelerated Hot / Software Warm 分机架 | ❌ 不混 |
| **Renaissance Medallion** | 按 Signal Family | Research（Warm）vs Production（Hot）分**组织** | ❌ 不混 |

**五家机构的一致做法**：业务分层和运行平面是**两个独立的架构维度**，通过**标签 / 装饰器 / frontmatter / 独立 deployment manifest** 做正交映射。**ZephyrAlpha 本视图采纳同一做法**。
