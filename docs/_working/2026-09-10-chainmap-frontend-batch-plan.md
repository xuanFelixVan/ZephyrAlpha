---
ttl: task_bound
---

# 产业链前端（chainmap 页）施工批次计划

- **task_bound**：临时工作文档，批次全部销项后归档；会话 st-igfe-20260910 单写手
- **创建**：2026-09-10；creation_token=`chainmap-fe-batch-plan-20260910`（capability_canonical_file_registry.yaml creation_tokens 段，**插 di_seam_exemptions 行之前**——EOF 落错段实证坑）
- **Owner 已裁定（2026-09-10 对话）**：
  1. 3D 星云立项，三期推进：一期=族级 3D 星云 → 二期=链群小星云 → 三期=单链甬道（参照 TDM 视觉语言）；技术路线=引 Three.js 进 vendor/（dockview 先例）；嵌套口径三层（族星云→链群小星云→甬道），每期独立验收，Owner 看一期效果再定后续节奏
  2. 3D 属纯视觉层：`/api/chainmap-galaxy` 数据契约、cm:* 总线事件、搜索/导航联动、断线空态+15s 重试、零演示数据纪律全部不变
  3. 原待办 ④③②⑤ 照排；⑥浅色主题挂起等排期
  4. ①作战池：chainmap 侧动作端归本会话；warroom/筛选器侧领地未明示——**开工前需 Owner 一句扩权（wr-pool.js + app1.js scrPool 函数划入）或明示拆给他会话**；默认方案 B（localStorage `zk-warroom-pool` 键，sq-fav-list 先例）
  5. ②S21 需求卡已交 Owner 转后端会话（st-igbe-20260910）：cluster 响应 per-node 增 `s21_gap`/`gap_note`

## 批次表（完成一批销一批：状态→DONE+commit hash）

| # | 批次 | 内容 | 依赖 | 状态 |
|---|------|------|------|------|
| B1 | ④galaxy 加载体验 | 首算 3-6s 期间骨架屏+进度提示（已等待时长诚实计数），断线空态+15s 重试保留；零假数据 | 无 | DONE(2026-09-10) |
| B2 | 3D 一期：族级星云 | Three.js vendor 引入+loader 挂接；47 簇球面撒点（簇越大星越亮）；拖拽旋转/滚轮缩放/键盘方向；hover 邻居高亮；点击飞入进簇（cm:open-cluster 不变）；星云成形等待动画吸收 B1 骨架 | B1 | PENDING |
| B3 | 3D 二期：链群小星云 | 点族飞入链群小星云（同引擎复用，链=小星，公司数=亮度），点链进甬道 | B2 | PENDING |
| B4 | 3D 三期：单链甬道 | 参照 TDM 视觉语言：单链上下游横向甬道+关联连线+tier/职能徽章/公司面板平移（改造 chainmap-cluster L2 渲染，数据接口不动） | B3 | PENDING |
| B5 | ③chain_path 层级路径 | L1→L2→L3 下钻树 UI 骨架+空态（"层级路径未入库"诚实标注）；等后端 child_chain_id 数据到位零改动点亮 | 无（骨架可先行） | PENDING |
| B6 | ⑤缩放场景打磨 | 股权浮层/催化角标在深度缩放下的可用性（fixed 防裁剪已就位，余 hover 命中/角标避让） | 无 | PENDING |
| B7 | ②S21 弱化标注 | cluster 视图断链环节弱化+悬浮说明；等后端字段，字段一到半天接入 | 后端 s21_gap | BLOCKED(等后端) |
| B8 | ①作战池 chainmap 侧 | 受益清单个股真实入池（写入端+断线降级+诚实提示改造）；warroom 承接 UI 领地待裁定 | Owner 扩权/拆分 | BLOCKED(等领地) |
| — | ⑥浅色主题 | 全局项，非本页职权 | Owner 排期 | 挂起 |

## 纪律清单（每批必过）

1. TRAE-086 四件套同 commit：manifest/frontend_map 条目（语义变才动）+ACC 走 revision+踩坑入手册（两次以上才解决的坑）
2. 编辑后进程外核实：`node --check` + python 读文件断言关键串
3. 验收三件：`python -m pytest tests/frontend/test_dashboard_smoke.py -x -q -o cache_dir=.runtime/tmp/pytest_cache_fe` 全绿 + `check_frontend_map.py` fail=0 + 8890 实景截图（Playwright）
4. 提交：先 `RuleDiscoveryServer().discover_applicable_rules` 写 lookup_audit → `python scripts/git_commit.py --session st-igfe-20260910 --files "<逗号单参数>" --message-file <utf8> --allow-promote --allow-non-worktree --allow-multi-domain --adopt-prior-work` → `git show --name-only` 核实零搭车；禁裸 commit/禁 --no-verify/禁 push
5. loader.js ZK_BUILD 每批触前端必递增
6. 新建 yaml/md 先登记 creation_token（插 di_seam_exemptions 行之前！）
7. 验收截图只留本地不入库（docs/03_modules DCR-005 只许 .md/.yaml；存量 PNG 均 untracked 先例）——ACC 里记 evidence 路径即可；截图法=8899 http.server 静态壳（web/ 目录）+8890 API 真源（api.js BASE 绝对地址）+Playwright page.route 模拟延迟/断线，异步 API 用 async 版避免同步版路由阻塞

## 已交后端/Owner 的外部依赖

- 《接口需求卡：chainmap S21 骨架缺口标记》→ Owner 转后端会话（B7 前置）
- warroom 池领地裁定（B8 前置）
