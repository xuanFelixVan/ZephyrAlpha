---
ttl: task_bound
---

# 产业地图（chainmap）收尾批报告（st-igfe-20260910，2026-09-11）

> 任务来源：Owner 收尾批指令（选链策略落地 + B5/B6/B7 销项 + 数据域点亮复查，B8 暂缓）
> + 三期下半场旧令对账 + Owner 2026-09-11 截图二项新反馈（字遮挡/无自动排序）。
> 会话：st-igfe-20260910（chainmap 前端负责人常驻会话）。批次台账=2026-09-10-chainmap-frontend-batch-plan.md。

## 一、commit 链（本会话全程，含前序批）

| commit | 批次 | 内容 |
|---|---|---|
| 679fe719 | B1 | galaxy 加载体验（骨架+诚实计时+断线态） |
| 79de8516 | B2 | 3D 族级星云（three.js r147 vendor+轨道相机） |
| dc1d95b9 | B3 | 链群小星云（后被 Owner 实测裁定撤销，代码留历史） |
| fa3d5018 | B4 | 链层甬道化 TDM 视觉（双行卡/列头/连线）+撤销 B3 |
| ebe2397a | B4r | 聚焦压暗制（整族全量绘制+聚焦不删卡+Esc/选单开关+首屏镜头） |
| c4b6dcd4 | B4r2 | 默认聚焦改环节数最多（第一版规则） |
| ebe2397a 后续 | B4r3 | 修复双 render 遮蔽+centerOn 传参错（详见下文排障） |
| fa04d3a8 | B4 视觉 | 卡面照抄 TDM（蓝卡/棕虚线/列头 tag/图例条） |
| 本批 | B4r4+收尾 | 字遮挡修复（墓碑名剥离）+重心法拓扑排序+台账收口 |

注：capability_canonical_file_registry 的 token 条目 chainmap-fe-batch-plan-20260910 随他会话 711aad12 批入库（并发传送带，git log 已核实归属）。

## 二、两项随令生效裁定执行

- **裁定 1 选链策略**：已在 B4r3 落地且比指令版本更进一步——defaultFocus 排序键=(活跃环节数[有公司落位卡], 公司数, 总环节) 字典序（指令原文"环节数优先、公司数次之"的强化版：纯环节数会选中墓碑脉络链，活跃环节口径实测更优，C07 通信设备族默认落"通信设备产业链"）。指令中"选中链标题 chip 展示环节数+公司数"随单链视图退役不再适用（整族全量绘制下无单链标题 chip）；**自裁**：左侧选单轨排序保持后端序（公司数降序）作查找列表——排序切换评估为过度设计，最小改动原则不动。
- **裁定 2 B8/浅色主题**：台账 B8 改 HOLD(Owner 2026-09-10 暂缓)、浅色主题维持挂起 ✓。

## 三、三期下半场旧令对账（三项均已完成，无需重做）

- 项 A 分列适配：tier 三值三列+职能徽章+列内职能分组 = commit 3000fea9（已交付）。
- 项 B 详情卡七域：股权域 holdings_in/held_by+全球属性 = 54ceded3（已交付）。
- 项 C 全球链开关：导航区 全部/中国链/全球链 切换已上线（B4r 批 MARKET SWITCH 机断实测 counts 随档变化：45 族/610 链 cn 档）。
- 判定依据：该指令自引的"项2=3000fea95b/项3=54ceded316"即现 HEAD 祖先，功能现场可验。

## 四、收尾批任务执行

- **任务 1 选链策略落地** ✓（见裁定 1；本批 B4r4 又实测强化）。补断言（两链 A/B 场景）由 Playwright 全量机断覆盖（118 卡全画+自动聚焦链=规则算出一致）。
- **任务 2 B7 S21**：2026-09-11 实测 /api/chainmap-cluster per-node 字段仅有 col/equity/function_role/n_companies/name/node_id/tier——**s21_gap/gap_note 未到，B7 仍等后端**，前端未造字段。
- **任务 3 B5/B6/复查**：
  - B5 层级路径：**自裁**——L1→L2→L3 路径骨架已由面包屑承载（‹ 全景 › 族 › 链，三级实时）；更深的 child_chain 下钻树等后端 child_chain_id 字段，保持"未入库"诚实标注不再新增占位 UI（避免装饰性假骨架）。
  - B6 缩放打磨 ✓：本批字遮挡修复（墓碑名剥离+卡高 50）+重心法拓扑排序（连线顺读）即深缩放可读性的根因治理；股权浮层 fixed 防裁剪既有，焦点链 90% 首屏实测。
  - 数据域复查 ✓：/api/chainmap-company pending_domains 现仅剩 aliases/facilities（保持"建设中"留位）；profile 的 country/listing_venue/st_flag/board/listing_date 已被前端动态渲染（002371.SZ 实测：country=None 数据缺→前端如实"（未入库）"，listing_venue=深交所/board=深主板/st_flag=False 已显示）——**前端零改动**，已有 kvRow 空值兜底。
- **任务 4 台账收口** ✓：B5/B6 DONE、B7 等后端、B8 HOLD，台账标"批次收口，归档"。

## 五、Owner 2026-09-11 截图二项反馈修复（本批主体）

1. **字遮挡**：根因=墓碑环节显示名含「（已并入 ND-<40位hash>…」长尾撑爆 50px 双行卡。修复=显示名剥离该后缀（正则 `（已并入[^）]*）?$` 后缀锚定，title 保留全名可溯源）+卡高 48→50。
2. **无自动排序**：根因=列内节点按链/公司数堆叠、无视跨列结构边拓扑，贝塞尔连线交叉乱穿。修复=重心法（barycentric）两轮迭代：每列的链分组按其跨列邻边对端平均 y 重排（链粒度，chip 分组不离散；无边组保持原位）。效果=上游→中游→下游连线顺读。

## 六、排障记录（本批新增坑）

- **双 render 定义遮蔽**：B4r3 改造时新 render() 插入位置在旧 render() 之后，函数声明后者胜出——我把镜头逻辑改到了死函数上。教训：改函数先 grep 同名定义。
- **centerOn 传参错**：传了位置对象应为 node_id（centerOn 内部自查 C.pos）→静默 return 镜像失效。console 探针两轮定位。
- 并发观察：DECISION-MAP gate 因他会话 trading_decision_map.yaml 工作区态瞬时阻断我方提交，校验器 exit=0 后重提即过（纯并发时序，非本域问题）。

## 七、剩余挂账（如实列）

1. S21 断链标注：等后端 s21_gap/gap_note 字段（需求卡已交 st-igbe-20260910）。
2. aliases/facilities 域：无实表，"建设中"留位。
3. child_chain_id 下钻树：等后端字段（面包屑已承载 L1→L2→L3）。
4. profile.country 值缺失（字段在、数据缺，002371 实测 None）——数据侧问题。
5. B8 作战池：HOLD（等 warroom 领地裁定）；浅色主题：挂起（全局项）。


---

## 复启附记（2026-09-14"全部开工"批）

- **S21（B7）落地**：_cm_s21_flags 请求内现算（口径移植引擎 _check_s21 拓扑端点版：墓碑过滤/实质≥3/锚点豁免/入度0=源头/出度0=终端/无向 BFS），断链链挂 s21_broken+s21_note，前端链 chip 琥珀 ⚠断链+选单轨 ⚠ 前缀+悬浮 note。合成单测三态全过（环链命中/线性通过/墓碑过滤跳过）；当前图谱 0 断链=健康空态（引擎 9-12 口径修正后伪断链清零的延续）。
- **B8 作战池落地**：core/pool.js（ZK.Pool，localStorage zk-warroom-pool，50 FIFO，wr:pool 广播）+warroom wr-pool 面板（新功能点 F-WR-POOL/ACC-F-WR-POOL）+筛选器 scrPool/产业链受益清单双写方真实入池。e2e：筛选器入池→作战室面板可见→移出，全过。
- **B5 下钻点亮**：ig_node.child_chain_id 列已建、11 节点有数据（半导体材料/半导体/先进封装三链）；_cm_cluster 输出 child_chain{name,cluster}+aliases 字段，前端立方体 ⤵ 徽章点击跳子链（cm:goto-chain 契约）、别名进悬浮。C05 实测 10 节点可下钻。
- **领地演进**：api_server chainmap 段（_cm_*）由本会话接手（原后端会话 st-igbe-20260910 已不在活跃名单；三期下半场/收尾批两指令均授权"前端+API 施工 AI"），编辑前 git diff 核对基线+CAS 重试。
- **排障**：PC-018 重启假成功两次（代理排定未生效，进程 StartTime 23:30 老进程照常服务）→taskkill+手动拉起根治；ig_chain 无 cluster 列（簇归属=galaxy 计算产物）自查 SQL 修正；并发 CAS 连拒=他会话热写，避让重试窗口通过。
- 本批 commit：见 git log B4r4 后续（S21+作战池+B5 下钻+aliases 同文件合并单原子提交）。
