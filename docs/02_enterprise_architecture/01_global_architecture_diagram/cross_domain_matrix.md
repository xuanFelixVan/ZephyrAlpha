---
doc_type: register
title: 域间依赖矩阵
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 域间依赖矩阵

> **文档作用 / Purpose**: 以矩阵形式展示所有功能域之间的依赖关系，识别高耦合域和独立域，为架构解耦提供依据。

> 本文档由 generate_cross_domain_matrix.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) edges表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 50 |
| 跨域依赖对数 | 175 |
| 跨域依赖边总数 | 3468 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D_AUDITTEST | D_TRADING | 639 | test_depends |
| D_AUDITTEST | D_GOVERNANCE | 527 | contract,data,runtime,test_depends |
| D_AUDITTEST | D_GOV_ENFORCEMENT | 222 | runtime,test_depends |
| D_AUDITTEST | D_SHARED | 170 | test_depends |
| D_AUDITTEST | D_SECURITY | 169 | contract,test_depends |
| D_GOVERNANCE | D_SHARED | 164 | import_depends,runtime |
| D_AUDITTEST | D_AUTONOMY_CORE | 127 | test_depends |
| D_AUDITTEST | D_INFRA_RUNTIME | 125 | runtime,test_depends |
| D_TRADING | D_SHARED | 101 | import_depends |
| D_INFRA_RUNTIME | D_SHARED | 70 | import_depends |
| D_AUDITTEST | D_INTEGRATION | 63 | test_depends |
| D_AUDITTEST | D_INFRA_RECOVERY | 52 | test_depends |
| D_GOV_SCRIPTS | D_SHARED | 44 | import_depends |
| D_GOVERNANCE | D_TRADING | 43 | import_depends,runtime |
| D_INTEGRATION | D_SHARED | 41 | import_depends |
| D_AUDITTEST | D_SECURITY_LLM | 41 | runtime,test_depends |
| D_GOV_ENFORCEMENT | D_GOVERNANCE | 38 | contract,import_depends,runtime |
| D_AUDITTEST | D_INFRA_A2A | 35 | test_depends |
| D_AUDITTEST | D_INTELLIGENCE | 31 | test_depends |
| D_GOV_SCRIPTS | D_GOVERNANCE | 31 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D_AUDITTEST | D_TRADING | 639 | test_depends |
| 2 | D_AUDITTEST | D_GOVERNANCE | 527 | contract,data,runtime,test_depends |
| 3 | D_AUDITTEST | D_GOV_ENFORCEMENT | 222 | runtime,test_depends |
| 4 | D_AUDITTEST | D_SHARED | 170 | test_depends |
| 5 | D_AUDITTEST | D_SECURITY | 169 | contract,test_depends |
| 6 | D_GOVERNANCE | D_SHARED | 164 | import_depends,runtime |
| 7 | D_AUDITTEST | D_AUTONOMY_CORE | 127 | test_depends |
| 8 | D_AUDITTEST | D_INFRA_RUNTIME | 125 | runtime,test_depends |
| 9 | D_TRADING | D_SHARED | 101 | import_depends |
| 10 | D_INFRA_RUNTIME | D_SHARED | 70 | import_depends |
| 11 | D_AUDITTEST | D_INTEGRATION | 63 | test_depends |
| 12 | D_AUDITTEST | D_INFRA_RECOVERY | 52 | test_depends |
| 13 | D_GOV_SCRIPTS | D_SHARED | 44 | import_depends |
| 14 | D_GOVERNANCE | D_TRADING | 43 | import_depends,runtime |
| 15 | D_INTEGRATION | D_SHARED | 41 | import_depends |
| 16 | D_AUDITTEST | D_SECURITY_LLM | 41 | runtime,test_depends |
| 17 | D_GOV_ENFORCEMENT | D_GOVERNANCE | 38 | contract,import_depends,runtime |
| 18 | D_AUDITTEST | D_INFRA_A2A | 35 | test_depends |
| 19 | D_AUDITTEST | D_INTELLIGENCE | 31 | test_depends |
| 20 | D_GOV_SCRIPTS | D_GOVERNANCE | 31 | import_depends |
| 21 | D_TRADING | D_INTEGRATION | 26 | import_depends |
| 22 | D_TRADING | D_GOVERNANCE | 26 | import_depends |
| 23 | D_GOVERNANCE | D_GOV_ENFORCEMENT | 22 | contract,import_depends,runtime |
| 24 | D_GOVERNANCE | D_INTEGRATION | 20 | import_depends |
| 25 | D_GOV_ENFORCEMENT | D_SHARED | 19 | import_depends |
| 26 | D_INTEGRATION_GATEWAY | D_SHARED | 19 | import_depends |
| 27 | D_INFRA_RECOVERY | D_SHARED | 18 | import_depends |
| 28 | D_TRADING | D_INFRA_RUNTIME | 18 | import_depends |
| 29 | D_GOVERNANCE | D_INFRA_RUNTIME | 18 | config_depends,import_depends,runtime |
| 30 | D_SECURITY_LLM | D_SHARED | 17 | import_depends |
| 31 | D_GOVERNANCE | D_INTELLIGENCE | 17 | import_depends |
| 32 | D_INFRA_A2A | D_SHARED | 16 | import_depends |
| 33 | D_INTELLIGENCE | D_SHARED | 15 | import_depends |
| 34 | D_FUNDAMENTAL_SIGNAL | D_TRADING | 14 | import_depends |
| 35 | D_AUTONOMY_CORE | D_GOVERNANCE | 14 | contract,data,import_depends,runtime |
| 36 | D_AUTONOMY_CORE | D_SHARED | 14 | import_depends |
| 37 | D_AUDITTEST | D_BACKTEST | 13 | test_depends |
| 38 | D_INTEGRATION_GATEWAY | D_GOVERNANCE | 13 | import_depends |
| 39 | D_GOVERNANCE | D_SECURITY | 12 | contract,import_depends,runtime |
| 40 | D_AUTONOMY_PERM | D_SECURITY | 12 | import_depends |
| 41 | D_INTEGRATION | D_INFRA_RUNTIME | 11 | import_depends |
| 42 | D_EX_CORE | D_GOVERNANCE | 11 | import_depends |
| 43 | D_INFRA_TELEMETRY | D_SHARED | 10 | import_depends |
| 44 | D_SECURITY | D_SHARED | 9 | import_depends |
| 45 | D_INTEGRATION | D_GOVERNANCE | 9 | import_depends |
| 46 | D_AUDITTEST | D_FRONTEND | 8 | test_depends |
| 47 | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | 8 | import_depends |
| 48 | D_INFRA_RECOVERY | D_GOVERNANCE | 8 | import_depends |
| 49 | D_INFRA_RUNTIME | D_GOVERNANCE | 8 | import_depends,runtime |
| 50 | D_AUTONOMY_CORE | D_INFRA_RUNTIME | 7 | import_depends |
| 51 | D_GOVERNANCE | D_SECURITY_LLM | 7 | contract,import_depends |
| 52 | D_FRONTEND | D_GOVERNANCE | 7 | import_depends,runtime |
| 53 | D_SECURITY | D_GOVERNANCE | 6 | import_depends |
| 54 | D_EX_CORE | D_SHARED | 6 | import_depends |
| 55 | D_TRADING | D_SECURITY | 6 | import_depends |
| 56 | D_SECURITY | D_GOV_ENFORCEMENT | 6 | import_depends |
| 57 | D_GOV_SCRIPTS | D_INFRA_RUNTIME | 6 | import_depends |
| 58 | D_REPORTING | D_SHARED | 6 | import_depends |
| 59 | D_GOVERNANCE | D_AUDITTEST | 6 | runtime |
| 60 | D_AUDITTEST | D_RISK | 6 | test_depends |
| 61 | D_AUTONOMY_CORE | D_INTEGRATION | 6 | import_depends |
| 62 | D_GOV_ENFORCEMENT | D_INTEGRATION | 6 | import_depends |
| 63 | D_TRADING | D_GOV_ENFORCEMENT | 5 | import_depends |
| 64 | D_GOVERNANCE | D_FRONTEND | 5 | import_depends |
| 65 | D_TRADING | D_INTELLIGENCE | 5 | import_depends |
| 66 | D_PF_CORE | D_GOVERNANCE | 5 | import_depends |
| 67 | D_GOV_DRIFT | D_GOVERNANCE | 5 | runtime |
| 68 | D_TRADING | D_SECURITY_LLM | 4 | import_depends |
| 69 | D_INTELLIGENCE | D_ML_TRAIN | 4 | import_depends |
| 70 | D_INTELLIGENCE | D_GOVERNANCE | 4 | import_depends |
| 71 | D_INTEGRATION_GATEWAY | D_INTEGRATION | 4 | import_depends |
| 72 | D_AUDITTEST | D_OPS | 4 | test_depends |
| 73 | D_AUDITTEST | D_EX_CORE | 4 | test_depends |
| 74 | D_TRADING | D_AUTONOMY_CORE | 4 | import_depends |
| 75 | D_SHARED | D_INFRA_RUNTIME | 3 | import_depends |
| 76 | D_BACKTEST | D_GOVERNANCE | 3 | import_depends |
| 77 | D_EX_CORE | D_TRADING | 3 | import_depends |
| 78 | D_FRONTEND | D_SHARED | 3 | import_depends |
| 79 | D_GOVERNANCE | D_AUTONOMY_CORE | 3 | contract,import_depends |
| 80 | D_GOVERNANCE | D_GOV_DRIFT | 3 | contract,runtime |
| 81 | D_GOVERNANCE | D_INFRA_RECOVERY | 3 | import_depends |
| 82 | D_GOVERNANCE | D_INTEGRATION_GATEWAY | 3 | contract,import_depends,runtime |
| 83 | D_GOVERNANCE | D_REPORTING | 3 | import_depends |
| 84 | D_GOVERNANCE | D_RISK | 3 | import_depends |
| 85 | D_GOV_ENFORCEMENT | D_INFRA_RECOVERY | 3 | import_depends |
| 86 | D_GOV_ENFORCEMENT | D_SECURITY | 3 | import_depends |
| 87 | D_GOV_SCRIPTS | D_INTEGRATION | 3 | import_depends |
| 88 | D_INFRA_RUNTIME | D_INTEGRATION | 3 | import_depends |
| 89 | D_INTEGRATION | D_INTELLIGENCE | 3 | import_depends |
| 90 | D_INTELLIGENCE | D_BACKTEST | 3 | import_depends |
| 91 | D_ML_TRAIN | D_SHARED | 3 | import_depends |
| 92 | D_RISK | D_SHARED | 3 | import_depends |
| 93 | D_RISK | D_TRADING | 3 | import_depends |
| 94 | D_SECURITY | D_TRADING | 3 | import_depends |
| 95 | D_TRADING | D_INFRA_TELEMETRY | 3 | import_depends |
| 96 | D_TRADING | D_OPS | 3 | import_depends |
| 97 | D_AUTONOMY_CORE | D_INTELLIGENCE | 2 | import_depends |
| 98 | D_FUNDAMENTAL_SIGNAL | D_FACTOR | 2 | contract,import_depends |
| 99 | D_FRONTEND | D_TRADING | 2 | import_depends |
| 100 | D_BACKTEST | D_SHARED | 2 | import_depends |
| 101 | D_SECURITY | D_INTEGRATION | 2 | import_depends |
| 102 | D_GOV_SCRIPTS | D_TRADING | 2 | import_depends |
| 103 | D_FRONTEND | D_EX_CORE | 2 | import_depends |
| 104 | D_INTELLIGENCE | D_GOV_ENFORCEMENT | 2 | import_depends |
| 105 | D_SECURITY_LLM | D_GOVERNANCE | 2 | import_depends |
| 106 | D_AUDITTEST | D_INFRA_TELEMETRY | 2 | test_depends |
| 107 | D_GOVERNANCE | D_INFRA_A2A | 2 | import_depends |
| 108 | D_AUDITTEST | D_PF_CORE | 2 | test_depends |
| 109 | D_FRONTEND | D_BACKTEST | 2 | import,import_depends |
| 110 | D_SHARED | D_ML_TRAIN | 2 | import_depends |
| 111 | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | 2 | import_depends |
| 112 | D_INTEGRATION | D_AUTONOMY_CORE | 2 | import_depends |
| 113 | D_SIGQC | D_TRADING | 2 | import_depends |
| 114 | D_TRADING | D_INFRA_RECOVERY | 2 | import_depends |
| 115 | D_AUDITTEST | D_INTEGRATION_GATEWAY | 2 | test_depends |
| 116 | D_INTEGRATION_GATEWAY | D_SECURITY_LLM | 2 | import_depends |
| 117 | D_AUDITTEST | D_FUNDAMENTAL_SIGNAL | 2 | test_depends |
| 118 | D_ML_TRAIN | D_TRADING | 2 | import_depends |
| 119 | D_EX_CORE | D_BACKTEST | 2 | import_depends |
| 120 | D_OPS | D_SHARED | 2 | import_depends |
| 121 | D_GOV_SCRIPTS | D_AUTONOMY_CORE | 2 | import_depends |
| 122 | D_AUDITTEST | D_POSITION | 2 | test_depends |
| 123 | D_AUDITTEST | D_GOV_SCRIPTS | 2 | test_depends |
| 124 | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | 2 | import_depends,runtime |
| 125 | D_PF_CORE | D_SHARED | 2 | import_depends |
| 126 | D_FUNDAMENTAL_SIGNAL | D_SHARED | 2 | import_depends |
| 127 | D_AUTONOMY_CORE | D_SECURITY_LLM | 2 | import_depends,runtime |
| 128 | D_SECURITY | D_INTELLIGENCE | 1 | import_depends |
| 129 | D_AUTONOMY_CORE | D_SECURITY | 1 | runtime |
| 130 | D_AUDITTEST | D_GOV_DRIFT | 1 | runtime |
| 131 | D_SHARED | D_GOVERNANCE | 1 | import_depends |
| 132 | D_SHARED | D_GOV_ENFORCEMENT | 1 | import_depends |
| 133 | D_SHARED | D_SIMULATION | 1 | import_depends |
| 134 | D_SHARED | D_TRADING | 1 | import_depends |
| 135 | D_SIMULATION | D_SHARED | 1 | import_depends |
| 136 | D_FACTOR | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 137 | D_GOV_ENFORCEMENT | D_GOV_DRIFT | 1 | runtime |
| 138 | D_GOV_DRIFT | D_SECURITY | 1 | runtime |
| 139 | D_AUDITTEST | D_REPORTING | 1 | test_depends |
| 140 | D_GOV_DRIFT | D_GOV_ENFORCEMENT | 1 | runtime |
| 141 | D_GOV_AUDIT | D_GOVERNANCE | 1 | runtime |
| 142 | D_GOV_SCRIPTS | D_INFRA_TELEMETRY | 1 | import_depends |
| 143 | D_TRADING | D_INFRA_A2A | 1 | import_depends |
| 144 | D_GOV_SCRIPTS | D_SECURITY | 1 | import_depends |
| 145 | D_GOV_SCRIPTS | D_INTELLIGENCE | 1 | import_depends |
| 146 | D_INFRA_A2A | D_GOVERNANCE | 1 | import_depends |
| 147 | D_AUDITTEST | D_SIMULATION | 1 | test_depends |
| 148 | D_GOVERNANCE | D_SIMULATION | 1 | import_depends |
| 149 | D_GOVERNANCE | D_PF_CORE | 1 | import_depends |
| 150 | D_GOVERNANCE | D_OPS | 1 | import_depends |
| 151 | D_INFRA_RUNTIME | D_TRADING | 1 | import_depends |
| 152 | D_INFRA_TELEMETRY | D_GOVERNANCE | 1 | import_depends |
| 153 | D_GOVERNANCE | D_ML_TRAIN | 1 | data |
| 154 | D_AUTONOMY_CORE | D_GOV_DRIFT | 1 | runtime |
| 155 | D_INTEGRATION | D_INFRA_RECOVERY | 1 | import_depends |
| 156 | D_INTEGRATION | D_SECURITY_LLM | 1 | import_depends |
| 157 | D_INTEGRATION_GATEWAY | D_GOV_ENFORCEMENT | 1 | import_depends |
| 158 | D_INTEGRATION_GATEWAY | D_INFRA_RECOVERY | 1 | import_depends |
| 159 | D_INTEGRATION_GATEWAY | D_INFRA_TELEMETRY | 1 | import_depends |
| 160 | D_GOVERNANCE | D_GOV_SCRIPTS | 1 | import_depends |
| 161 | D_INTEGRATION_GATEWAY | D_SECURITY | 1 | import_depends |
| 162 | D_INTELLIGENCE | D_AUTONOMY_CORE | 1 | import_depends |
| 163 | D_AUTONOMY_CORE | D_KNOWLEDGE | 1 | contract |
| 164 | D_AUTONOMY_CORE | D_INFRA_A2A | 1 | runtime |
| 165 | D_INTELLIGENCE | D_INFRA_RUNTIME | 1 | import_depends |
| 166 | D_INTELLIGENCE | D_INTEGRATION | 1 | import_depends |
| 167 | D_GOVERNANCE | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 168 | D_GOVERNANCE | D_FACTOR | 1 | import_depends |
| 169 | D_INTELLIGENCE | D_TRADING | 1 | import_depends |
| 170 | D_KNOWLEDGE | D_GOVERNANCE | 1 | runtime |
| 171 | D_MKT_DATA | D_SHARED | 1 | import_depends |
| 172 | D_BACKTEST | D_INFRA_RUNTIME | 1 | import_depends |
| 173 | D_GOVERNANCE | D_EX_CORE | 1 | import_depends |
| 174 | D_PF_CORE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 175 | D_SECURITY | D_INFRA_RUNTIME | 1 | import_depends |
