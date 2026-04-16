---
charter_id: 08_HUMAN_AI_INTERFACE_CHARTER
version: 1.0.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
review_cycle: quarterly
owner: HCI负责人
---

# 08_HUMAN_AI_INTERFACE 文件夹宪章

> **定位**: 人机交互层（L08）全模块蓝图与设计文档
> **当前规模**: ~156个文件，模块众多
> **负责人**: HCI负责人
> **对应层级**: L08 Human-AI Interface（系统架构Layer 8）

---

## 1. 核心职责

本目录是 **L08 人机交互层**的完整设计文档库，覆盖：

- **交易终端**: 40_TRADING_TERMINAL/（交易界面设计）
- **订单管理**: 61_ORDER_MANAGEMENT_SYSTEM/（OMS UI/UX）
- **风控监控**: 64_REALTIME_RISK_MONITORING/（风险仪表盘）
- **组合管理**: 80_PORTFOLIO_MANAGEMENT/（持仓界面）
- **API网关**: 28_API_GATEWAY/（接口设计）
- **AI助手**: 54_AI_ASSISTANT_INTEGRATION/（AI交互）
- **性能监控**: 43_PERFORMANCE_MONITORING/（系统状态展示）
- **权限管理**: 42_USER_PERMISSION_MANAGEMENT/（访问控制界面）

---

## 2. 内容边界

### 允许存放的文件类型

| 类型 | 模式 | 示例 | 存放子目录 |
|------|------|------|------------|
| UI设计文档 | `ui_*.md` | `ui_design.md` | `05_DESIGN_DOCS/ui_design/` |
| API文档 | `api_*.md` | `api_documentation.md` | `58_API_DOCUMENTATION_GENERATION/` |
| 交互规格 | `*_interaction.md` | `user_interaction_spec.md` | 各模块目录 |
| 原型说明 | `prototype_*.md` | `trading_terminal_prototype.md` | `40_TRADING_TERMINAL/` |
| 用户培训 | `training_*.md` | `user_training.md` | `36_USER_TRAINING/` |
| 可访问性 | `a11y_*.md` | `accessibility_guide.md` | `37_ACCESSIBILITY/` |
| i18n文档 | `i18n_*.md` | `i18n_support.md` | `33_I18N_SUPPORT/` |

### 禁止存放的文件类型

| 类型 | 原因 | 应放置位置 |
|------|------|------------|
| 前端实现代码 | 非文档 | `src/ui/` |
| 后端API实现 | 非文档 | `src/api/` |
| 测试报告 | 属于审计 | `09_AUDIT/STATE/` |
| 用户反馈原始数据 | 原始数据 | `data/feedback/` |
| 界面截图（大批量）| 占用空间大 | `assets/screenshots/` |

---

## 3. 二级目录结构（按功能模块组织）

```
docs/08_HUMAN_AI_INTERFACE/
├── 05_DESIGN_DOCS/               # 设计文档
│   └── ui_design/
├── 10_DASHBOARD/                 # 仪表盘设计
├── 15_ALERT_NOTIFICATION/        # 告警通知
├── 20_DATA_VISUALIZATION/        # 数据可视化
├── 25_REPORTING_INTERFACE/         # 报告界面
├── 28_API_GATEWAY/               # API网关
├── 33_I18N_SUPPORT/              # 国际化
├── 36_USER_TRAINING/             # 用户培训
├── 37_ACCESSIBILITY/             # 可访问性
├── 40_TRADING_TERMINAL/          # 交易终端
├── 42_USER_PERMISSION_MANAGEMENT/ # 权限管理
├── 43_PERFORMANCE_MONITORING/      # 性能监控
├── 54_AI_ASSISTANT_INTEGRATION/    # AI助手
├── 56_SECURITY_AUDIT/            # 安全审计界面
├── 58_API_DOCUMENTATION_GENERATION/ # API文档生成
├── 59_PERF_BENCHMARK_VALIDATION/   # 性能基准
├── 61_ORDER_MANAGEMENT_SYSTEM/     # 订单管理
├── 63_ALGORITHMIC_TRADING_CONSOLE/ # 算法交易控制台
├── 64_REALTIME_RISK_MONITORING/    # 实时风控
├── 65_RISK_REPORTING_SYSTEM/       # 风险报告
├── 66_DATA_MANAGEMENT_PLATFORM/      # 数据管理平台
├── 80_PORTFOLIO_MANAGEMENT/        # 组合管理
└── INDEX.md                      # 本目录索引
```

---

## 4. 容量限制

| 指标 | 当前值 | 上限 | 状态 |
|------|--------|------|------|
| 总文件数 | ~156 | 250 | 🟢 充足 |
| 子目录数 | 22 | 30 | 🟡 接近上限 |
| 最大深度 | 3 | 3 | 🟢 达标 |
| 单文件大小 | <5MB | 5MB | 🟢 正常 |

**注意**: 子目录数已达22个，接近30上限。新增模块需审查必要性。

---

## 5. 保留策略

| 内容类型 | TTL | 备注 |
|----------|-----|------|
| UI设计文档 | 永久 | 随产品迭代更新版本 |
| 原型说明 | 永久 | 历史原型归档至 `99_ARCHIVE/` |
| 用户培训材料 | 永久 | 持续更新 |
| 临时设计稿 | 30天 | 确认后正式化或删除 |
| 界面截图 | 30天 | 归档至 `assets/` |

---

## 6. 自动化检查

```bash
# UI文档frontmatter检查
python scripts/hooks/validate_blueprint_frontmatter.py \
  docs/08_HUMAN_AI_INTERFACE/*/

# 子目录数量监控（接近上限告警）
python scripts/governance/scan_subsystem_duplicates.py \
  --alert-threshold 25 docs/08_HUMAN_AI_INTERFACE/

# 目录深度检查
python scripts/hooks/check_directory_naming.py docs/08_HUMAN_AI_INTERFACE/
```

---

## 7. 与其他目录的关系

- **上游需求**: `07_AI_REPORTING/`（AI报告层提供展示内容）
- **上游策略**: `03_TRADING_TACTICS/`（策略层定义交易逻辑）
- **上游执行**: `04_EXECUTION/`（执行层提供订单状态）
- **上游风控**: `02_FACTOR_LIBRARY/`（风控因子信号）
- **下游实现**: `05_IMPLEMENTATION/`（前端开发实施）

**数据流向**:
```
03_TRADING_TACTICS/  04_EXECUTION/
        ↓                ↓
   07_AI_REPORTING/  02_FACTOR_LIBRARY/
              ↓      ↓
         08_HUMAN_AI_INTERFACE/ (界面展示)
                  ↓
         05_IMPLEMENTATION/ (前端实现)
```

---

## 8. 已知问题与改进计划

| 问题 | 优先级 | 计划解决时间 | 解决方案 |
|------|--------|--------------|----------|
| 子目录数接近上限（22/30）| P2 | 持续监控 | 新增模块需审批，考虑合并小模块 |
| 部分子目录内容稀疏 | P3 | 按需 | 模块成熟后补充内容 |
| 与 01_FRAMEWORK/LAYER8_HCI/ 边界模糊 | P2 | Phase D | 明确分层：设计在01，详细规格在08 |
| 多个集成来源目录（integrated_from_*）| P1 | Phase D | 按编号体系重构后整合 |

---

## 9. 变更历史

| 版本 | 日期 | 变更 | 变更人 |
|------|------|------|--------|
| v1.0.0 | 2026-04-16 | 初始创建 | AI Assistant |

---

**相关链接**:
- [08_HUMAN_AI_INTERFACE 索引](../../08_HUMAN_AI_INTERFACE/INDEX.md)
- [L08_HCI 架构蓝图](../../01_FRAMEWORK/LAYER8_HCI/INDEX.md)
- [03_BLUEPRINTS 目标结构](../../03_BLUEPRINTS/INDEX.md)
