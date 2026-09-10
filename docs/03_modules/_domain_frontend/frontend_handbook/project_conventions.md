---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·项目约定（PC）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.7.0"
date: 2026-08-31
topic: frontend_handbook_project_conventions
scope: frontend
---

# 前端技术手册·项目约定（PC）

> 本册收录 ZephyrAlpha 项目自有的前端约定（overlay 分组/commit 门禁/文件认领/验收纪律）。
> 条目四段式：触发词 → 想做什么 → 内置能否 → 坑 → 正确做法+代码锚点。编号永久稳定不回收。

---

### FEH-PC-001｜K 线标注层 overlay 分组管理

- **触发词**：overlay 分组 / marks / trades / cost / draw / 标注层
- **想做什么**：在 K 线图上同时管理多类标注（量化信号/真实成交/成本线/画线工具）且互不干扰
- **内置能否**：✅ 库支持 groupId，但分组方案是项目自定义
- **坑**：不分组会互相覆盖/误删（关一个开关全没了）；分组名乱起会无法对齐治理
- **正确做法**：固定四组——`marks`（量化买卖点灰框）/ `trades`（真实成交红B绿S）/ `cost`（黄色成本线）/ `draw`（画线工具）；开关按组控显隐
- **代码锚点**：开关逻辑 `src/zephyr/frontend/dashboard/web/core/app1.js#L6147`（klpRefreshMarks）；成本线组 `app1.js#L6229`
- **来源**：KLineChart 集成交接文档 · 2026-08-31

### FEH-PC-002｜前端 commit 必须走 GitCommitGateway

- **触发词**：commit / 提交 / 网关 / git_commit / 裸 commit
- **想做什么**：提交前端代码/文档改动
- **内置能否**：❌ 裸 `git commit` 被禁（pre-commit 全树 stash 会冲掉其他会话暂存）
- **坑**：禁裸 commit、禁 `--no-verify`；受保护路径（AGENTS.md/architecture_model/rules/）需 message 带 `[ARCH-APPROVAL:ISSUE_ID]`；新文件入永久区需 `--allow-promote`；先改后提触发 FOREIGN_CHANGE 需 `--adopt-prior-work`
- **正确做法**：`python scripts/git_commit.py --session <id> --files <逗号分隔> --message-file <utf8文件> --allow-non-worktree [--adopt-prior-work 跨session续作时] [--allow-promote 永久区新文件] [--allow-multi-domain 多域]`
- **代码锚点**：——（流程纪律）；网关 `scripts/git_commit.py`
- **来源**：项目硬约束（project_memory） · 2026-08-31

### FEH-PC-003｜编辑被追踪文档前先 claim_files

- **触发词**：claim / 文件锁 / 回滚 / watchdog / 认领文件
- **想做什么**：修改已被治理追踪的文档/文件
- **内置能否**：✅ 有机制但必须主动用
- **坑**：不 claim 直接改会被 watchdog 回滚或触发 FOREIGN_CHANGE 阻断（"改了被冲掉"）
- **正确做法**：编辑前先 claim（gateway 的 `--adopt-prior-work` 可认领前序未提交变更）；热文件（注册表/AGENTS.md/tracker）用 `safe_write_text`（base-hash CAS+回读校验）
- **代码锚点**：`src/zephyr/shared/io/file_utils.py`（safe_write_text）
- **来源**：项目系统性问题（topic 记忆 2026-08-31） · 2026-08-31

### FEH-PC-004｜前端验收纪律（验收单+截图目检）

- **触发词**：验收 / 截图目检 / 回归 / 图标消失
- **想做什么**：改完 UI 确认没改坏、没回归
- **内置能否**：❌ 前端无自动化测试（Playwright 冒烟待建=四件套第 5 步）
- **坑**：AI 改完 UI 只看代码不看效果——"图标消失"类回归全靠人眼事后发现
- **正确做法**：任何 UI 改动 commit 前：起本地服务 → 截图 → 逐条对验收单（`docs/03_modules/_domain_frontend/acceptance/`，待建）→ 全绿才提交；过渡期"机断"条款由人工/AI 在浏览器控制台手动执行等价断言
- **代码锚点**：验收单目录 `docs/03_modules/_domain_frontend/acceptance/`（待建）
- **来源**：四件套草案 v0.4 §二 · 2026-08-31

### FEH-PC-005｜Playwright 冒烟测试三实证坑

- **触发词**：冒烟测试 / Playwright / wait_for_selector 超时 / 测试导航不生效 / 改动被回拨
- **想做什么**：用 Playwright 给仪表盘写结构断言测试
- **内置能否**：✅（playwright 1.62+chromium 已装；chromium 下载走镜像 `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright`，官方源国内会卡死零字节）
- **坑**：①`wait_for_selector` 默认等"可见"，但页面 section 默认隐藏（导航才显示）——必须用 `state="attached"`；②测试里改 `location.hash` 不触发页面初始化（应用无 hashchange 监听）——必须调全局 `go('<page>')`；③Edit 工具改完文件可能被 IDE 脏缓冲区回拨（实证：test_dashboard_smoke.py 第一处改动被静默回退）——改后必须进程外核实（Select-String/git diff）
- **正确做法**：见坑①②③；冒烟网真源 `tests/frontend/test_dashboard_smoke.py`（自起 http.server，无需外部服务）
- **代码锚点**：`tests/frontend/test_dashboard_smoke.py`
- **来源**：冒烟网建设实证（3 次失败→3 修复→4/4 绿） · 2026-08-31

---

# FEH-PC-008｜组件拆分铁律（数据源边界 + 单一功能）
- 触发词：组件拆分 / 模块拆分 / 什么时候拆组件 / 自选和持仓 / 数据源边界 / 单一功能
- 想做什么：判断两个功能块该不该拆成独立组件
- 内置能否：无内置，项目自约定（Owner 2026-09-01 裁定铁律）
- 坑：①数据源不同的功能块糊在一起 = 改 A 数据源要测 B 功能，回滚互相牵连（自选列表 vs 持仓列表实证）②功能语义不同但数据源相同的功能块糊在一起 = 改标题样式要测五档挂单，回归爆炸
- 正确做法：
  - **数据源边界判据（最高优先）**：两个功能块数据源不同，必须拆成两个组件。即使视觉相邻、同页面、同模块组，数据源不同 = 独立组件。例：自选列表（localStorage）vs 持仓列表（QMT）必须拆；股票标题（daily_valuation）vs 五档挂单（l2_tick）必须拆
  - **单一功能判据**：一个视觉区块 + 一种交互行为 + 一个功能语义 = 一个组件。即使数据源相同，功能不同也必须拆。例：右栏"股票标题"和"关键数据表"都读 daily_valuation，但功能语义不同 = 独立组件
  - **积木思维**：组件拆到最细 = 任何页面直接引用 = 改 A 页面不影响 B 页面 = 未来加新功能只需在页面做入口
- 反例（禁止）：把"自选+持仓"写成一个"侧边栏组件"（数据源不同）；把"股票标题+关键数据+五档挂单+简介"糊成一个"资料面板组件"（功能语义不同）
- 关联：TRAE-086（前端拆件铁律）· DS-11（设计规范）· stockq 拆分清单 v2
- 来源：Owner 2026-09-01 裁定（数据源边界+单一功能双判据）

---

# FEH-PC-007｜depgraph 新增字段四步铁律（防重建丢值）
- 触发词：depgraph 加字段 / migration / nodes_metadata / 重建器 / generate_project_depgraph / PRODUCTION_PROTECTED_FIELDS
- 想做什么：给 depgraph 的 nodes 表新增业务字段（如前端覆盖三字段 has_frontend/no_frontend_reason/frontend_ref）
- 内置能否：无内置保护，必须人工走四步
- 坑：**generate_project_depgraph 重建运营态时会整表 DELETE+INSERT，新字段不在保护字段清单里 = 全部重置为默认值**。夜战实证：20 个模块的前端覆盖数据一次重建后全丢，回填工作白费
- 正确做法（四步缺一不可）：
  1. **nodes 表加列**：`ALTER TABLE nodes ADD COLUMN IF NOT EXISTS xxx`（migration SQL 脚本，如 `12_add_frontend_coverage_fields.sql`）
  2. **nodes_metadata 保险柜表同步加列**：同脚本里给 metadata 表也加同一列——metadata 是重建前的"保险柜"，存盘时把值暂存于此
  3. **重建器"重建前存档"（UPSERT）登记新列**：在 `generate_project_depgraph.py` 的 Stage 2 UPSERT 语句里，把新列加进 INSERT 字段清单和 ON CONFLICT DO UPDATE SET 清单——否则存档时漏存新列
  4. **重建器"重建后恢复"（UPDATE）登记新列**：在同一文件的 Stage 2 UPDATE 语句里，把新列加进恢复清单——COALESCE(NULLIF(nodes.xxx, ''), nm.xxx, nodes.xxx)。**注意空哨兵**：如果字段默认值是非空字符串（如 has_frontend 默认 'no'），不能直接用 COALESCE，必须用 `CASE WHEN nodes.xxx = 'no' AND nm.xxx <> 'no' THEN nm.xxx ELSE nodes.xxx END`，否则重建默认值会回灌覆盖真值
- 验证：四步做完后，必须完整跑一次 `generate_project_depgraph.py`，然后查 `SELECT count(*) FROM nodes WHERE xxx != 默认值` 确认值存活
- 代码锚点：migration `12_add_frontend_coverage_fields.sql` · `generate_project_depgraph.py` Stage 2 UPSERT (~3680) / UPDATE (~4210)
- 关联：depgraph_schema.py `_DDL_NODES_METADATA`
- 来源：2026-09-01 夜战实证（20 模块值重建丢值 → 四步根治 → 端到端重建验证存活）

---

# FEH-PC-006｜数据源状态灯四态约定（DS-12）
- 触发词：状态灯 / 真源角标 / 数据断线 / klpDataMode / ● 真源
- 想做什么：给数据功能标题行加数据源状态指示
- 内置能否：无内置，项目自约定（DS-12，2026-09-01 Owner 裁定四态不二元）
- 坑：①二元（绿/红）会误判"数据旧但接口通"（归绿=静默放行旧数据=交易大忌；归红=狼来了，真断线时脱敏）②"未启动"（从未取数）≠"断线"（取过但失败），必须分开——灰留给前者
- 正确做法：四态——绿 真源（取数成功+数据在新鲜窗口内）/ 黄 延迟（取到但过期）/ 红 断线（回退演示数据，诚实纪律红色明示不可信）/ 灰 未启动（服务从未响应）；新鲜窗口随 update_frequency（日级 4 天 / 分钟级 30 分钟）
- 代码锚点：app1.js klpDataMode + dataLoader finish 分支（~5980）· 样式 .klp-datamode.dm-*（main.css ~254）
- 关联：DS-12（design.html）· modlib #52 · ACC-F-STOCKQ-KLINE-DATA
- 来源：commit 53bdb4b6 打样 + 2026-09-01 Owner 四态裁定

---

# FEH-PC-009｜"改了不显示"版本戳排查法（浏览器缓存）
- 触发词：改了不显示 / 页面没更新 / 还是旧样式 / ⚑12 不见
- 想做什么：代码已改已提交，页面死活不变时定位是代码 bug 还是缓存
- 内置能否：无内置，项目自约定（loader.js 顶部 window.ZK_BUILD）
- 坑：①浏览器 HTTP 缓存可残留数小时前的旧 JS，F5 强刷有时也不彻底（2026-09-01 实证：⚑12 不显示=浏览器跑 2.5h 前旧代码，代码本身没问题）②组件一次性拉取失败会永久回退演示数据，与缓存症状相似但根因不同——事件行"无数据"实为 API 重启瞬间拉取失败后无重试
- 正确做法：①看页头品牌行有无 `b<ZK_BUILD>` 版本戳（每次前端改动 ZK_BUILD+1）②无戳=浏览器跑旧代码 → 开无痕窗口验证 ③无痕正常=缓存问题，根治=Electron 壳（app:// 直读 web/ 零 HTTP 缓存）④无痕也异常=真 bug，查组件有无拉取重试（新组件拉数据必须 15s 自动重试直至真源）
- 代码锚点：core/loader.js 顶部 window.ZK_BUILD + 品牌行戳注入；features/stockq/sq-event-row.js 15s 重试
- 关联：FEH-PC-010（Electron 壳根治）· SOP §四常见坑
- 来源：2026-09-01 事件行排障实证

---

# FEH-PC-010｜Electron 桌面壳与媒体素材纪律
- 触发词：桌面版 / Electron / 桌面快捷方式 / 图标不更新 / 视频自动播放 / 素材放哪
- 想做什么：前端封装为本地桌面应用、管理图片视频素材
- 内置能否：无内置，项目自约定（2026-09-01 Owner 裁定前端桌面化）
- 坑：①Windows 桌面图标缓存按路径索引——换 ico 文件不重建快捷方式永不更新（解法：ico 复制到 %LOCALAPPDATA%\ZephyrAlpha-app.ico 新路径+重建快捷方式）②PS5.1 下无 BOM UTF-8 的 PS1 脚本中文注释被 GBK 误读吞行（脚本注释一律英文）③Chromium 禁无手势有声 autoplay——Electron 壳加 autoplay-policy=no-user-gesture-required，浏览器端必须静音兜底+首次点击恢复声音④页面 display:none 不停视频解码——切页必须显式 pause()（挂 page:show 广播），否则后台持续占用资源
- 正确做法：壳居 tools/desktop/（src/zephyr 为 Python 包根禁 .json）；生产模式 app:// 协议直读 web/ 零 HTTP 缓存；标题栏黑底 #0A0D14；素材统一进 web/assets/media/{img/brand,img/pages,video}/，派生图（ico）与原图同目录成对存放，入库后外部原件可删
- 代码锚点：tools/desktop/main.js · core/home.js ovxVideo · pages/home.html home-pure-video
- 关联：FEH-PC-009 · SOP §七桌面壳/媒体素材段落
- 来源：2026-09-01 桌面化+首页纯视频实证

---

# FEH-PC-011｜QMT 文件桥真源组件三律（编码/列序/口径）
- 触发词：QMT 文件桥 / PositionStatics.csv / 持仓乱码 / 盈亏比例失真 / 十档
- 想做什么：组件接 QMT 文件桥（E:\qmt_bridge）实盘数据
- 内置能否：无内置，项目自约定（miniQMT 2026-09-18 关停后唯一实盘通道）
- 坑：①CSV 一律 GBK 编码，utf-8 读必乱码②持仓列序硬编码 row[7]=代码/row[9]=当前拥有/row[15]=可用/row[18]=最新价，错位即错数③QMT 导出"盈亏比例"列因送转/负成本严重失真（实测 -94.29%/-102.65%），直接展示=误导 Owner
- 正确做法：①encoding='gbk'②列序按硬编码常量，不猜表头③显示口径裁定（Owner 2026-09-01）：持仓列表价格旁百分比=股票**当天涨跌幅**（与自选列表同口径，走 kline_daily /api/quote），真实盈亏只放悬停提示④文件 mtime >1h=延迟（黄灯）不是断线——非交易时段终端不导出新文件属正常⑤quote.csv 档位数动态解析（bid1~bid10），前端自适应显示
- 代码锚点：api_server.py /api/position · /api/order-book（_QMT_BRIDGE_STOCK_DIR）；features/stockq/sq-position-list.js v3
- 关联：FEH-PC-006 四态灯 · SOP §三数据源变体
- 来源：2026-09-01 持仓列表口径修正+十档自适应实证

---

# FEH-PC-012｜registerFeature 只登记不初始化——组件自举三事必须文件顶层做
- 触发词：features 组件 / 样式没生效 / init 没人调 / registerFeature / 组件白板
- 想做什么：按拆件 SOP 写 features/<page>/<name>.js 功能模块
- 内置能否：ZK.registerFeature（core/event_bus.js）只做登记（ZK.features[id]=def），**绝不调用 init()**——app1.js 仅对 sq-* 系列显式调 init，其余页面组件无人调
- 坑：①把样式注入（injectStyles）放 init() 里 → 无人调 init → 样式永不注入 → 流程条/高亮全裸奔（DOM 数据全对但视觉无样式，ACC 验收才暴露）②首渲染依赖 init 或宿主 → 兜底路径漏样式必现白板
- 正确做法：组件文件 IIFE 顶层直接做三件事——injectStyles()（加载即注入）、竞态兜底渲染（检查宿主变量+容器存在则主动 render()）、宿主联动入口（window.<hostFn>=function(){ZK.features[id].render()}）；init() 只留 chart 挂载等真正需要宿主参数的逻辑
- 代码锚点：features/backtest/bt-battle-stage.js（实证修复）· core/event_bus.js ZK.registerFeature
- 关联：FEH-LOAD-002 加载链竞态 · frontend_component_split_sop §Step2 模板注释（"竞态兜底"行）
- 来源：2026-09-04 回测页策略所处环节模块 ACC 验收实证

---

# FEH-PC-013｜详情抽屉统一模板——分区+chip+导航行（禁各页各自发明）
- 触发词：详情抽屉 / 节点档案 / drawer / 右侧详情 / 点节点看详情
- 想做什么：全景图/树图页做「点节点开右侧抽屉看完整档案」
- 内置能否：❌ 无现成组件——但 tdm 页抽屉 v2（b20260908-10）已实证成模板
- 坑：①长文+键值+引用列表混排纯文字堆叠 → 信息全但不可读②引用列表顿号长串 → 一行爆宽③治理字段「激活=x ｜ 档位=y」拼接 → 空值塌行④真源文本不转义直拼 innerHTML → YAML 含 `<>&` 必断标签⑤轮询重绘不存 scrollTop → 用户阅读位置被冲掉
- 正确做法：照 `frontend_handbook/detail_drawer_template.md`——固定分区顺序（标题徽标→问→机制→治理键值网格→模块锚→挂载→八轴 chip→上下游导航行→设计备注）；三态徽标色与画布卡片同语义同色号；esc() 强制；空值 `—` 留位；新页施工时抽屉应按拆件三判据（单一功能+独立样式+跨页复用）直接拆为独立组件而非内联
- 代码锚点：pages/tdm.html style 块「右侧详情抽屉 v2」段 · features/tdm.js drawer()
- 关联：detail_drawer_template.md（模板真源）· FEH-PC-008 拆件铁律
- 来源：2026-09-08 tdm 抽屉重设计实证（commit 062975c7）· Owner 裁定模板化

---

# FEH-PC-014｜绝对定位容器尺寸不能量 offsetWidth——用布局常量直接算
- 触发词：连线消失 / SVG 不显示 / offsetWidth / 绝对定位 / 画布尺寸 / 视口塌了
- 想做什么：绝对定位画布页（世界层+树+SVG 连线）初始化 SVG 视口尺寸
- 内置能否：无内置，量 DOM 是第一直觉但在此布局必错
- 坑：绝对定位容器收缩包裹（shrink-to-fit）+ 树内卡片全绝对定位不撑宽 → host.offsetWidth 恒≈padding（tdm 实测 8px）→ SVG 视口塌成 8px → 全部连线画到可视区外视觉上"连线全消失"（tdm b20260908-02 事故，171 条边一条不见但 DOM 全在，极易误判为数据/边生成 bug）
- 正确做法：世界层/树/SVG 尺寸不用量 DOM——用布局常量直接算：contentW = 末列 X + 列宽、contentH = 末行 y + 余量，显式写 style.width/height；SVG 尺寸同源赋值（attr+style 双写）；容器尺寸变化走 ResizeObserver 整树重排不重量
- 代码锚点：features/tdm.js render() 尾部注释块（contentW/contentH 显式计算）· pages/tdm.html #tdm-world/#tdm-wire
- 关联：FEH-PC-012 自举三律 · ACC-F-TDM-MAP item 6（连线可见性回归点）
- 来源：2026-09-08 tdm 连线消失排障实证（b20260908-02）

---

# FEH-PC-015｜ID 容器内状态色类必须带 ID 前缀——防基础规则特异度碾压
- 触发词：状态色失效 / 颜色不生效 / 特异度 / CSS 选择器 / 样式被覆盖 / 卡片全一个色
- 想做什么：给 ID 容器（#tdm-tree）内的状态变体（.production/.design/.paper）写差异化配色
- 内置能否：无内置，CSS 特异度规则通用但在"ID 基础规则+状态类"组合必踩
- 坑：ID 基础规则 `#tdm-tree .tn` 特异度 (1-1-0) 压过状态类 `.tn.production` (0-2-0)——状态色全被基础边框色覆盖（tdm b20260908-05 事故：三态色全失效，卡片视觉全同色，验收时才暴露）
- 正确做法：状态色变体一律写带 ID 前缀的完整选择器：`#tdm-tree .tn.production`、`#tdm-tree .tn.design`、`#tdm-tree .tn.paper`（(1-2-0) > (1-1-0) 稳赢）；新画布页样式照此模式，禁裸状态类
- 代码锚点：pages/tdm.html style 块（#tdm-tree .tn.production 等，注释有事故记录）
- 关联：FEH-PC-013 抽屉徽标三态（同语义同色号）· ACC-F-TDM-MAP item 4（三态配色回归点）
- 来源：2026-09-08 tdm 状态色失效排障实证（b20260908-05）

---

---

# FEH-PC-016｜creation_tokens CAS 追加会落进文件尾最后一个键——先定位再插入
- 触发词：creation_tokens / safe_write_text / capability_canonical_file_registry / 落错键 / StaleWriteRefused
- 想做什么：新建 .yaml/.md 文件前在 capability_canonical_file_registry.yaml 的 creation_tokens 追加 token 条目
- 内置能否：无内置；registry 是多会话热文件，必须走 safe_write_text CAS（expected_base_sha256 必填，否则拒写）
- 坑1（本会话 2026-09-09 实证）：EOF 直接 append 的条目物理上落进文件尾**最后一个顶层键**（当前=di_seam_exemptions），不在 creation_tokens——yaml 也能解析通过，肉眼难察觉，消费方按键查不到=白登记
- 坑2：safe_write_text 不带 expected_base_sha256 → StaleWriteRefused 拒写（热文件 CAS 契约）；base=content_sha256(读到的原文)
- 正确做法：①`s.count("\n di_seam_exemptions:\n")` 式定位**下一个顶层键**锚点，把新条目插到它**前面**（=上一个键列表尾）②CAS 写后必须 yaml.safe_load 复核条目真的在目标键下（`[e.get("file") for e in data["creation_tokens"]]` 断言）③文件尾"最后一个顶层键"会随治理演进漂移（曾是 creation_tokens 自身），禁硬编码 EOF append
- 代码锚点：docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml（L4951 creation_tokens 键起；尾键=di_seam_exemptions）
- 关联：TRAE-086 四件套闭环 · git_commit.py --allow-promote 前置（token 未登记则晋升被阻断）
- 来源：2026-09-09 chainmap 二期 Commit A 实证（sess-chainmap-a2-20260909）

---

# FEH-PC-017｜commit message 声称"含后端"不等于真的提交了——交接前 git 实核
- 触发词：端点 404 / 后端丢失 / quarantine / message 与实物不符 / 接手一期成果
- 想做什么：接手前任 AI 的一期成果继续二期施工，以为端点/模块已入库
- 内置能否：git log --oneline 只能看 message，不能证实物
- 坑：一期 chainmap commit（3c314f7b85）message 声称"四模块+四端点"，实际只提交 16 个前端/文档文件，api_server.py 不在清单——后端四端点只活在 quarantine 副本里（drift 漂移隔离），dev 分支从未有过；前端对着 404 空转。同 commit 还有 loader 挂链缺失前科（f40afb8924 补救）。**message 与实物不符是事故族，不是孤例**
- 正确做法：接手即核三件：①`git show <commit> --stat` 文件清单与 message 逐项对 ②`git log --all -S '<关键符号>' -- <文件>` 验证代码真进过历史 ③live 文件 Select-String 关键符号。发现缺失→先从 quarantine/副本移植回 live 并 AST 验证，再开工新功能，且在新 commit 里明确写"移植"语义
- 代码锚点：src/zephyr/frontend/dashboard/api_server.py L1788 起（2026-09-09 从 quarantine drift_20260908T143802 移植的 chainmap 段）
- 关联：ACC 冻结前实景验收（execution.flow 起服务逐条对）· TRAE-079 漂移隔离
- 来源：2026-09-09 chainmap 二期调研发现 + Commit A 移植实证

# FEH-PC-018｜8890 面板服务重启权限墙——services-control restart 不是每次都真换进程
- 触发词：改了 api_server 看不到效果 / restart 返回 ok 但端点还是旧逻辑 / taskkill 拒绝访问 / StartTime 不变
- 想做什么：AI 会话改完 api_server.py 后重启 8890 让新代码生效（ACC execution.flow"起面板 API"）
- 内置能否：services-control restart 对 self 级开放（_do_restart_self 分离代理：psutil kill 旧进程→等端口空→Popen 重拉），表面看一键搞定
- 坑：①restart 返回 ok≠进程真换——旧实例可能是管理员提升权限进程（Get-CimInstance 的 ExecutablePath 查出来为空=权限不足信号），非提升 shell 的 taskkill/Stop-Process 一律"拒绝访问"，restarter 代理也会被权限挡住静默失败（连发三次排定三次 PID/StartTime 纹丝不动）。**判定服务版本唯一可信=进程 StartTime+端点行为探针（新字段/新参数返回），不是 restart 返回值**。②隔离验证别硬刚 8890：起临时实例（.runtime 下唯一文件名脚本+uvicorn 固定端口 8891）+ http.server 静态代理（/api 反代 8891）即可全链路实景验收，零权限需求；api.js BASE 硬编码 8890，浏览器侧用 playwright route 把 8890 请求改道 8891。③临时进程会被 ProcessReaper 当孤儿清理——cmdline 子串登记 data/runtime/process_reaper_keep.txt 保活
- 正确做法：能换进程（StartTime 变）才继续 8890 验证；换不动立即转 8891 隔离方案，并在汇报里如实写"8890 需 Owner/管理员壳重启"，禁拿 8890 旧代码响应当新代码验收证据
- 代码锚点：src/zephyr/frontend/dashboard/services_registry.py `_RESTARTER_SRC`/`_do_restart_self`（分离代理实现）；api_server.py `main()`（uvicorn 8890 单进程）
- 关联：PC-009 版本戳排查法（ZK_BUILD 判前端旧代码）· 前会话实录 2026-09-09-chainmap-fix.md 教训 2
- 来源：2026-09-10 chainmap 三项施工夜班实证（restart×3+taskkill+Stop-Process 五连败后 8891 方案全绿）

# FEH-PC-019｜3D 画布双坑——render 异常被 .catch 伪装成"API 断线" + 元素遮挡让 pointerdown 失效
- 触发词：meta 显示"API 断线（xxx is not defined）"但 curl 后端全绿 / E2E 点星没反应但 hover 高亮正常 / lastPick 探针为 null
- 想做什么：chainmap galaxy 3D 化（B2）后正常渲染+点星进簇；Playwright 全序列验收
- 坑：①取数 load() 的 `.then` 回调里调 render()，render 抛错（如裸 `scene.add` ReferenceError）会被同一 Promise 链的 `.catch` 捕获→fail(e.message)→meta 显示"API 断线（scene is not defined）"——**前端渲染异常伪装成后端断线**，且场景已建一半（stars/lines 计数正常）更具迷惑性。判定法：页内直接 fetch 后端对账（fetch ok=true + meta 断线 = 前端 .then 内异常被吞）；配套 debug() 只读探针暴露 lastPick/相机球坐标供机断。②交互监听器分家：pointermove 挂 window（任何目标都触发）、pointerdown 挂画布元素——当点击点被 pointer-events:auto 元素（顶栏 cm-meta 计数行等）遮挡时，hover 照常工作而 pointerdown 永远不达画布，表现为"hover 亮但点了没反应"。判定法：elementFromPoint(x,y) 看落点元素；E2E 侧在拖拽/缩放后先 dblclick 复位再选目标（旋转后标签可能漂进顶栏遮挡区）
- 正确做法：render 入口不依赖外层 .catch 兜错误——重渲染路径的异常要么在 render 内部自捕获转诚实空态，要么 fail() 文案区分"取数失败"与"渲染失败"；3D 交互 E2E 断言用 debug() 探针而不是只看 DOM 副作用
- 代码锚点：src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-galaxy.js（load().catch / clickPick 的 G.lastPick / debug() 探针）
- 关联：PC-009 版本戳排查法 · ACC-F-CHAINMAP-GALAXY rev4 item12（debug 探针机断）
- 来源：2026-09-10 chainmap B2 3D 星云一期施工实证（scene.add ReferenceError 三轮排查 + cm-meta 遮挡致 E2E 点选连败）

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 4 条（PC-001~004） | 四件套施工第 1 步；项目自有约定是弱模型最易踩的坑 |
| 2026-08-31 | 1.1.0 | +PC-005 Playwright 冒烟测试三实证坑 | 冒烟网建设 3 失败→3 修复实证 |
| 2026-09-01 | 1.2.0 | +PC-006 数据源状态灯四态约定（DS-12） | Owner 四态裁定（绿/黄/红/灰）成文 |
| 2026-09-01 | 1.3.0 | +PC-007 depgraph 新增字段四步铁律 | 夜战实证：重建器静默重置新字段（20 模块值全丢）→ 根治后重建验证存活 |
| 2026-09-01 | 1.4.0 | +PC-008 组件拆分铁律（数据源边界+单一功能） | Owner 2026-09-01 裁定：数据源不同必拆；功能语义不同必拆 |
| 2026-09-01 | 1.5.0 | +PC-009 版本戳排查法 / +PC-010 Electron 壳与素材纪律 / +PC-011 QMT 文件桥三律 | 当日三连实证：⚑12 缓存排障、桌面化落地、持仓口径修正 |
| 2026-09-08 | 1.6.0 | +PC-013 详情抽屉统一模板（指向 detail_drawer_template.md） | tdm 抽屉 v2 实证沉淀，Owner 裁定模板化供全景图页复用 |
| 2026-09-08 | 1.7.0 | +PC-014 绝对定位容器尺寸禁量 DOM / +PC-015 状态色类必须带 ID 前缀 | tdm 四件套补登记沉淀：b20260908-02 连线消失 + b20260908-05 状态色失效双事故成文 |
| 2026-09-09 | 1.8.0 | +PC-016 creation_tokens CAS 落错键 / +PC-017 commit message 与实物不符排查法 | chainmap 二期 Commit A 实证：di_seam_exemptions 落键事故 + 一期后端假提交移植 |
| 2026-09-10 | 1.9.0 | +PC-018 8890 面板服务重启权限墙 | chainmap 三项施工夜班实证：restart×3 假成功，8891 隔离实例+playwright route 改道方案全绿 |
