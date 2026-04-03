---
module_id: TECH_SPEC_BLUEPRINT_SUPP_001
version: 1.1.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席技术评审官
standard_type: 蓝图补充文档
applicable_scope: 市场参与者行为模拟系统
compliance_level: 专业标准
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: 设计阶段
---

# 市场参与者行为模拟系统 - 蓝图补充文档

> **版本**: v1.1
> **创建日期**: 2026-04-03
> **技术评审官**: Spec-Approver (审批智能体)
> **目的**: 补充技术评审中发现的缺失设计（IMP-005至IMP-008）

---

## 📋 一、Layer间职责边界定义 ⭐ **IMP-005补充**

### 1.1 Layer 2.5 与 Layer 2 (Alpha因子层) 的职责边界

#### 1.1.1 职责划分

| 维度 | Layer 2.5 (市场参与者模拟层) | Layer 2 (Alpha因子层) |
|------|---------------------------|---------------------|
| **核心职责** | 模拟市场参与者行为，生成智能体决策 | 计算传统Alpha因子，提供因子信号 |
| **数据来源** | iFind + 智能体内部状态 | iFind + Layer 2.5输出 |
| **输出类型** | 因子、信号、决策三种形式 | 因子一种形式 |
| **时间框架** | 日度/日内 | 日度 |
| **计算方法** | RL + LLM + 行为金融学 | 统计模型 + 机器学习 |

#### 1.1.2 接口协议

```python
class Layer2_5_to_Layer2_Interface:
    """Layer 2.5 → Layer 2 接口协议
    
    索引: INTERFACE.LAYER.2_5_TO_2.001
    职责: 定义Layer 2.5向Layer 2输出因子的接口
    """
    
    def output_factor_to_layer2(self, 
                                factor_output: FactorOutput) -> FactorRegistration:
        """输出因子到Layer 2
        
        流程:
        1. Layer 2.5生成因子
        2. 格式化为FactorOutput
        3. 调用Layer 2因子注册接口
        4. Layer 2验证因子质量
        5. Layer 2存储因子
        
        约束:
        - Layer 2.5仅负责生成因子，不负责因子存储
        - Layer 2负责因子质量检查和存储
        - 因子格式必须符合Layer 2标准
        
        返回:
            FactorRegistration: 因子注册结果
        """
        pass
```

#### 1.1.