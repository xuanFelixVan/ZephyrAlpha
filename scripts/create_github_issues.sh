#!/bin/bash
# create_github_issues.sh
# 批量创建GitHub Issue - 清风量化系统TODO转换
# 创建日期: 2026-04-06
# 使用方法: bash scripts/create_github_issues.sh

set -e

echo "🚀 开始创建GitHub Issue..."
echo "================================"

# 检查GitHub CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ 错误: GitHub CLI未安装"
    echo "请先安装GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  Windows: choco install gh"
    echo "  Linux: sudo apt install gh"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 错误: 未登录GitHub"
    echo "请先运行: gh auth login"
    exit 1
fi

# 创建Issue模板目录
mkdir -p issue_templates

# Issue #1: P0 - 实现自定义风险预算功能
cat > issue_templates/issue_01.md << 'EOF'
## 功能描述
在战略配置引擎中实现自定义风险预算功能，允许用户指定各资产的风险贡献度。

## 背景
当前使用默认的风险平价模型，需要支持用户自定义风险预算配置。

## 相关文档
- [STRATEGIC_ALLOCATION_ENGINE_BLUEPRINT.md](../docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGIC_ALLOCATION_ENGINE_BLUEPRINT.md#L328)

## 技术方案
1. 扩展HRPOpt类，支持自定义风险预算参数
2. 添加风险预算验证逻辑
3. 实现风险预算优化算法

## 验收标准
- [ ] 支持自定义风险预算参数输入
- [ ] 风险预算验证通过
- [ ] 优化结果符合预期
- [ ] 单元测试覆盖率≥80%
- [ ] 文档更新完成

## 预计时间
2天
EOF

# Issue #2: P0 - QMT执行器获取上次交易日期
cat > issue_templates/issue_02.md << 'EOF'
## 功能描述
从交易记录中获取上次交易日期，用于交易频率控制。

## 背景
QMT执行器需要根据上次交易日期判断是否满足交易频率限制。

## 相关文档
- [QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md](../docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md#L1431)

## 技术方案
1. 查询交易记录表
2. 过滤指定标的的交易记录
3. 返回最近交易日期

## 验收标准
- [ ] 正确查询交易记录
- [ ] 返回正确的上次交易日期
- [ ] 处理无交易记录的情况
- [ ] 单元测试覆盖率≥80%
- [ ] 文档更新完成

## 预计时间
0.5天
EOF

# Issue #3: P0 - QMT执行器发送告警通知
cat > issue_templates/issue_03.md << 'EOF'
## 功能描述
当交易执行出现异常时，发送告警通知。

## 背景
QMT执行器需要在异常情况下及时通知用户，确保风险可控。

## 相关文档
- [QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md](../docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md#L1503)

## 技术方案
1. 集成告警系统（邮件/钉钉/企业微信）
2. 定义告警触发条件
3. 格式化告警消息

## 验收标准
- [ ] 支持多种告警渠道
- [ ] 告警消息格式正确
- [ ] 告警触发及时
- [ ] 单元测试覆盖率≥80%
- [ ] 文档更新完成

## 预计时间
1天
EOF

# Issue #4: P0 - QMT执行器触发风控措施
cat > issue_templates/issue_04.md << 'EOF'
## 功能描述
当风险指标超过阈值时，自动触发风控措施。

## 背景
QMT执行器需要在风险超标时自动采取风控措施，保护投资组合。

## 相关文档
- [QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md](../docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md#L1509)

## 技术方案
1. 定义风控触发条件
2. 实现风控措施（暂停交易/减仓/清仓）
3. 记录风控日志

## 验收标准
- [ ] 风控触发条件准确
- [ ] 风控措施执行正确
- [ ] 风控日志完整
- [ ] 单元测试覆盖率≥80%
- [ ] 文档更新完成

## 预计时间
1天
EOF

# Issue #5: P0 - QMT执行器集成告警系统
cat > issue_templates/issue_05.md << 'EOF'
## 功能描述
集成完整的告警系统，支持邮件、钉钉、企业微信等多种告警渠道。

## 背景
QMT执行器需要一个统一的告警系统，方便扩展和维护。

## 相关文档
- [QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md](../docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md#L1699)

## 技术方案
1. 设计告警系统架构
2. 实现告警渠道接口
3. 添加告警配置管理

## 验收标准
- [ ] 支持多种告警渠道
- [ ] 告警配置灵活
- [ ] 告警发送可靠
- [ ] 单元测试覆盖率≥80%
- [ ] 文档更新完成

## 预计时间
1.5天
EOF

echo "✅ Issue模板创建完成"
echo ""

# 创建P0 Issues
echo "📝 创建P0高优先级Issue..."
echo "--------------------------------"

gh issue create --title "[P0] 实现自定义风险预算功能 - 战略配置引擎" --label "P0,enhancement,strategic-allocation" --body-file issue_templates/issue_01.md
echo "✅ Issue #1 创建成功"

gh issue create --title "[P0] QMT执行器 - 获取上次交易日期" --label "P0,enhancement,qmt-executor" --body-file issue_templates/issue_02.md
echo "✅ Issue #2 创建成功"

gh issue create --title "[P0] QMT执行器 - 发送告警通知" --label "P0,enhancement,qmt-executor,alert" --body-file issue_templates/issue_03.md
echo "✅ Issue #3 创建成功"

gh issue create --title "[P0] QMT执行器 - 触发风控措施" --label "P0,enhancement,qmt-executor,risk-control" --body-file issue_templates/issue_04.md
echo "✅ Issue #4 创建成功"

gh issue create --title "[P0] QMT执行器 - 集成告警系统" --label "P0,enhancement,qmt-executor,alert" --body-file issue_templates/issue_05.md
echo "✅ Issue #5 创建成功"

echo ""
echo "✅ P0 Issues创建完成 (5个)"
echo ""

# 创建P1 Issues
echo "📝 创建P1中优先级Issue..."
echo "--------------------------------"

gh issue create --title "[P1] 实现回测阶段功能 - 代码示例占位符" --label "P1,enhancement,backtest" --body "实现回测阶段的核心功能，包括回测引擎、数据加载、结果分析等。相关文档: CODE_QUALITY.md#L29"
echo "✅ Issue #6 创建成功"

gh issue create --title "[P1] 添加缓存机制 - 回测阶段优化" --label "P1,enhancement,backtest,performance" --body "为回测阶段添加缓存机制，提升回测性能。相关文档: CODE_QUALITY.md#L41"
echo "✅ Issue #7 创建成功"

gh issue create --title "[P1] 实现回测阶段功能 - 代码示例2" --label "P1,enhancement,backtest" --body "实现回测阶段的另一个功能点。相关文档: CODE_QUALITY.md#L48"
echo "✅ Issue #8 创建成功"

gh issue create --title "[P1] 添加缓存机制 - 通用缓存模块" --label "P1,enhancement,performance" --body "实现通用的缓存机制，支持多种缓存后端。相关文档: CODE_QUALITY.md#L156"
echo "✅ Issue #9 创建成功"

gh issue create --title "[P1] 实现订单Saga创建逻辑 - 订单管理" --label "P1,enhancement,database,order-management" --body "实现订单Saga模式，确保订单创建的原子性和一致性。相关文档: P0-07_Order_Management_Detailed_Design.md#L695"
echo "✅ Issue #10 创建成功"

gh issue create --title "[P1] 反序列化缓存数据 - 账户管理" --label "P1,enhancement,database,account-management" --body "实现缓存数据的反序列化逻辑。相关文档: P0-06_Account_Management_Detailed_Design.md#L861"
echo "✅ Issue #11 创建成功"

gh issue create --title "[P1] 实现重试逻辑 - 多引擎协调器" --label "P1,enhancement,database,multi-engine" --body "实现多引擎协调器的重试逻辑，提高系统容错能力。相关文档: P0-05_Multi_Engine_Coordinator_Design.md#L678"
echo "✅ Issue #12 创建成功"

gh issue create --title "[P1] 实现继续补偿逻辑 - 多引擎协调器" --label "P1,enhancement,database,multi-engine" --body "实现多引擎协调器的继续补偿逻辑。相关文档: P0-05_Multi_Engine_Coordinator_Design.md#L683"
echo "✅ Issue #13 创建成功"

gh issue create --title "[P1] 实现手动恢复逻辑 - 多引擎协调器" --label "P1,enhancement,database,multi-engine" --body "实现多引擎协调器的手动恢复逻辑。相关文档: P0-05_Multi_Engine_Coordinator_Design.md#L688"
echo "✅ Issue #14 创建成功"

gh issue create --title "[P1] 查询历史验证结果 - 数据监控" --label "P1,enhancement,data-monitoring" --body "从数据库查询历史验证结果，用于趋势分析。相关文档: DATA_MONITORING_ENHANCED/BLUEPRINT.md#L994"
echo "✅ Issue #15 创建成功"

gh issue create --title "[P1] 查询历史异常数据 - 数据监控" --label "P1,enhancement,data-monitoring" --body "从数据库查询历史异常数据，用于异常模式分析。相关文档: DATA_MONITORING_ENHANCED/BLUEPRINT.md#L1002"
echo "✅ Issue #16 创建成功"

gh issue create --title "[P1] 生成HTML报告 - 数据监控" --label "P1,enhancement,data-monitoring,report" --body "生成HTML格式的数据监控报告，便于查看和分享。相关文档: DATA_MONITORING_ENHANCED/BLUEPRINT.md#L1010"
echo "✅ Issue #17 创建成功"

echo ""
echo "✅ P1 Issues创建完成 (12个)"
echo ""

# 创建P2 Issues
echo "📝 创建P2低优先级Issue..."
echo "--------------------------------"

gh issue create --title "[P2] 集成告警系统 - 数据血缘追踪" --label "P2,enhancement,data-lineage,alert" --body "为数据血缘追踪系统集成告警系统，支持邮件、钉钉等告警渠道。相关文档: DATA_LINEAGE_TRACKING/BLUEPRINT.md#L700"
echo "✅ Issue #18 创建成功"

echo ""
echo "✅ P2 Issues创建完成 (1个)"
echo ""

# 清理临时文件
rm -rf issue_templates

echo "================================"
echo "🎉 所有Issue创建完成！"
echo ""
echo "📊 统计信息:"
echo "  - P0高优先级: 5个"
echo "  - P1中优先级: 12个"
echo "  - P2低优先级: 1个"
echo "  - 总计: 18个"
echo ""
echo "📋 下一步:"
echo "  1. 查看Issue列表: gh issue list"
echo "  2. 分配负责人: gh issue edit <number> --assignee <username>"
echo "  3. 添加到项目看板"
echo ""
