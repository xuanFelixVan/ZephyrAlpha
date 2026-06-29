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

> 本文档由 generate_cross_domain_matrix.py 从 depgraph.db 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph.db edges表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 跨域依赖对数 | 215 |
| 跨域依赖边总数 | 3519 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D-GOVERNANCE | D_OPS | 385 | config_depends,import_depends,runtime,test_depends |
| D-GOVERNANCE | D_INTEGRATION | 231 | import_depends,test_depends |
| D-GOVERNANCE | D-TRADING | 225 | import_depends,test_depends |
| D-GOVERNANCE | D_AUTONOMY_CORE | 214 | contract,import_depends,runtime,test_depends |
| D-GOVERNANCE | D_SECURITY | 206 | contract,import_depends,runtime,test_depends |
| D-GOVERNANCE | D_SHARED | 183 | import_depends,test_depends |
| D-GOVERNANCE | D-GOV_ENFORCEMENT | 168 | import_depends,runtime,test_depends |
| D-GOVERNANCE | D-GOV_AUDIT | 140 | contract,import_depends,runtime,test_depends |
| D-AUTONOMY_PERM | D_SECURITY | 137 | import_depends,test_depends |
| D-GOVERNANCE | D_INFRA_RUNTIME | 124 | config_depends,import_depends,runtime,test_depends |
| D-GOVERNANCE | D_BEHAVIORAL_AUDIT | 88 | import_depends,test_depends |
| D_INTEGRATION | D_SHARED | 70 | import_depends |
| D_SECURITY | D_BEHAVIORAL_AUDIT | 51 | import_depends |
| D-TRADING | D_INTEGRATION | 49 | event,import_depends |
| D-GOVERNANCE | D-INTELLIGENCE | 49 | import_depends,test_depends |
| D-TRADING | D_SHARED | 42 | contract,import_depends |
| D_INFRA_RUNTIME | D_SHARED | 36 | import_depends |
| D-GOV_AUDIT | D_SHARED | 35 | import_depends |
| D_OPS | D_INFRA_RUNTIME | 33 | import_depends,test_depends |
| D_INFRA_RECOVERY | D_INFRA_RUNTIME | 33 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D-GOVERNANCE | D_OPS | 385 | config_depends,import_depends,runtime,test_depends |
| 2 | D-GOVERNANCE | D_INTEGRATION | 231 | import_depends,test_depends |
| 3 | D-GOVERNANCE | D-TRADING | 225 | import_depends,test_depends |
| 4 | D-GOVERNANCE | D_AUTONOMY_CORE | 214 | contract,import_depends,runtime,test_depends |
| 5 | D-GOVERNANCE | D_SECURITY | 206 | contract,import_depends,runtime,test_depends |
| 6 | D-GOVERNANCE | D_SHARED | 183 | import_depends,test_depends |
| 7 | D-GOVERNANCE | D-GOV_ENFORCEMENT | 168 | import_depends,runtime,test_depends |
| 8 | D-GOVERNANCE | D-GOV_AUDIT | 140 | contract,import_depends,runtime,test_depends |
| 9 | D-AUTONOMY_PERM | D_SECURITY | 137 | import_depends,test_depends |
| 10 | D-GOVERNANCE | D_INFRA_RUNTIME | 124 | config_depends,import_depends,runtime,test_depends |
| 11 | D-GOVERNANCE | D_BEHAVIORAL_AUDIT | 88 | import_depends,test_depends |
| 12 | D_INTEGRATION | D_SHARED | 70 | import_depends |
| 13 | D_SECURITY | D_BEHAVIORAL_AUDIT | 51 | import_depends |
| 14 | D-TRADING | D_INTEGRATION | 49 | event,import_depends |
| 15 | D-GOVERNANCE | D-INTELLIGENCE | 49 | import_depends,test_depends |
| 16 | D-TRADING | D_SHARED | 42 | contract,import_depends |
| 17 | D_INFRA_RUNTIME | D_SHARED | 36 | import_depends |
| 18 | D-GOV_AUDIT | D_SHARED | 35 | import_depends |
| 19 | D_OPS | D_INFRA_RUNTIME | 33 | import_depends,test_depends |
| 20 | D_INFRA_RECOVERY | D_INFRA_RUNTIME | 33 | import_depends |
| 21 | D-GOV_SCRIPTS | D-GOVERNANCE | 30 | import_depends |
| 22 | D_OPS | D-GOVERNANCE | 29 | config_depends,import_depends,runtime,test_depends |
| 23 | D-TRADING | D-GOVERNANCE | 28 | contract,import_depends,runtime |
| 24 | D-GOV_DOCS | D-GOVERNANCE | 26 | import_depends,runtime |
| 25 | D-GOVERNANCE | D-GOV_DRIFT | 25 | config_depends,contract,import_depends,runtime,test_depends |
| 26 | D_AUTONOMY_CORE | D_INTEGRATION | 24 | import_depends |
| 27 | D-GOV_AUDIT | D-GOVERNANCE | 21 | config_depends,contract,import_depends,runtime |
| 28 | D_INFRA_RUNTIME | D_INTEGRATION | 21 | import_depends |
| 29 | D-GOV_DOCS | D_SHARED | 19 | import_depends |
| 30 | D_INFRA_A2A | D_SHARED | 18 | import_depends |
| 31 | D-FUNDAMENTAL_SIGNAL | D-TRADING | 17 | import_depends |
| 32 | D-GOVERNANCE | D_MKT_DATA | 16 | test_depends |
| 33 | D-KNOWLEDGE | D_INTEGRATION | 15 | import_depends,test_depends |
| 34 | D_OPS | D_SHARED | 14 | import_depends,test_depends |
| 35 | D-GOVERNANCE | D-RISK | 14 | test_depends |
| 36 | D-KNOWLEDGE | D-GOVERNANCE | 13 | import_depends,runtime,test_depends |
| 37 | D_INFRA_A2A | D_INFRA_RUNTIME | 13 | import_depends |
| 38 | D-GOV_AUDIT | D-GOV_DRIFT | 13 | import_depends,runtime |
| 39 | D-GOV_ENFORCEMENT | D_INTEGRATION | 13 | import_depends |
| 40 | D-GOV_SCRIPTS | D_INTEGRATION | 13 | import_depends |
| 41 | D_INFRA_TELEMETRY | D_INFRA_RUNTIME | 12 | import_depends |
| 42 | D-TRADING | D_SECURITY | 12 | import_depends |
| 43 | D-PF_CORE | D-GOVERNANCE | 12 | contract,import_depends |
| 44 | D-GOVERNANCE | D-SIMULATION | 12 | test_depends |
| 45 | D-GOVERNANCE | D-GOV_SCRIPTS | 12 | test_depends |
| 46 | D-COMPLIANCE | D-GOV_AUDIT | 11 | import_depends |
| 47 | D_INTEGRATION | D-GOVERNANCE | 11 | config_depends,import_depends |
| 48 | D-TRADING | D-GOV_AUDIT | 11 | contract,import_depends |
| 49 | D-GOV_SCRIPTS | D_INFRA_RUNTIME | 11 | import_depends |
| 50 | D-GOV_DOCS | D_INTEGRATION | 11 | import_depends |
| 51 | D-EX_CORE | D-GOVERNANCE | 10 | config_depends,import_depends |
| 52 | D-GOV_DOCS | D-GOV_ENFORCEMENT | 10 | import_depends |
| 53 | D-GOV_DRIFT | D-GOVERNANCE | 10 | config_depends,import_depends,runtime,test_depends |
| 54 | D-RISK | D-TRADING | 10 | import_depends |
| 55 | D_REPORTING | D-GOVERNANCE | 10 | import_depends |
| 56 | D-COMPLIANCE | D-GOVERNANCE | 10 | import_depends |
| 57 | D-GOV_SCRIPTS | D-GOV_ENFORCEMENT | 10 | import_depends |
| 58 | D_INFRA_RUNTIME | D-GOVERNANCE | 9 | import_depends |
| 59 | D_REPORTING | D-TRADING | 9 | import_depends |
| 60 | D_OPS | D_AUTONOMY_CORE | 8 | import_depends,runtime,test_depends |
| 61 | D-GOVERNANCE | D_FRONTEND | 8 | test_depends |
| 62 | D-GOVERNANCE | D-FUNDAMENTAL_SIGNAL | 8 | test_depends |
| 63 | D-GOV_DRIFT | D_BEHAVIORAL_AUDIT | 8 | test_depends |
| 64 | D-GOV_ENFORCEMENT | D_SHARED | 8 | import_depends |
| 65 | D_INFRA_OPS | D-GOVERNANCE | 8 | config_depends,import_depends,test_depends |
| 66 | D_INFRA_RECOVERY | D-GOV_AUDIT | 7 | import_depends |
| 67 | D_SHARED | D_INTEGRATION | 7 | import_depends |
| 68 | D-GOV_DRIFT | D-GOV_AUDIT | 7 | import_depends,runtime |
| 69 | D-AUDITTEST | D-GOV_AUDIT | 7 | test_depends |
| 70 | D-GOVERNANCE | D-GOV_RULE | 7 | import_depends,test_depends |
| 71 | D-TRADING | D-INTELLIGENCE | 6 | import_depends |
| 72 | D-TRADING | D-GOV_ENFORCEMENT | 6 | contract,import_depends |
| 73 | D-GOVERNANCE | D-PF_CORE | 6 | test_depends |
| 74 | D_SHARED | D_INFRA_RUNTIME | 6 | import_depends |
| 75 | D-GOVERNANCE | D-EX_CORE | 6 | test_depends |
| 76 | D_AUTONOMY_CORE | D_SHARED | 6 | import_depends |
| 77 | D-INTELLIGENCE | D_INTEGRATION | 6 | import_depends |
| 78 | D-INTELLIGENCE | D-GOVERNANCE | 6 | config_depends,import_depends |
| 79 | D-GOVERNANCE | D_INFRA_A2A | 6 | import_depends |
| 80 | D_OPS | D_INTEGRATION | 6 | import_depends,runtime |
| 81 | D-GOV_AUDIT | D_SECURITY | 6 | import_depends |
| 82 | D_SHARED | D_OPS | 6 | import_depends |
| 83 | D-GOV_AUDIT | D-GOV_ENFORCEMENT | 5 | import_depends,runtime |
| 84 | D_OPS | D_SECURITY | 5 | import_depends,test_depends |
| 85 | D-GOV_ENFORCEMENT | D_BEHAVIORAL_AUDIT | 5 | import_depends |
| 86 | D_INFRA_RECOVERY | D_SHARED | 5 | import_depends |
| 87 | D-GOV_AUDIT | D_INTEGRATION | 5 | import_depends |
| 88 | D-CROSS_ASSET | D-TRADING | 5 | contract,import_depends |
| 89 | D_SECURITY | D-GOV_AUDIT | 5 | import_depends |
| 90 | D_SECURITY | D-GOV_ENFORCEMENT | 5 | import_depends |
| 91 | D-GOV_AUDIT | D_INFRA_RUNTIME | 5 | import_depends |
| 92 | D_SECURITY | D_SHARED | 5 | import_depends |
| 93 | D-FACTOR | D-GOVERNANCE | 5 | config_depends,import_depends |
| 94 | D-GOVERNANCE | D-AUTONOMY_PERM | 4 | contract,runtime |
| 95 | D_INFRA_RECOVERY | D-GOVERNANCE | 4 | import_depends |
| 96 | D_FRONTEND | D-GOVERNANCE | 4 | import_depends |
| 97 | D_INTEGRATION | D_SECURITY | 4 | import_depends |
| 98 | D-GOV_ENFORCEMENT | D-GOV_AUDIT | 4 | import_depends |
| 99 | D_INFRA_RUNTIME | D-GOV_AUDIT | 4 | import_depends |
| 100 | D_SECURITY | D-GOVERNANCE | 4 | import_depends |
| 101 | D-GOVERNANCE | D-FACTOR | 4 | test_depends |
| 102 | D-TRADING | D_INFRA_RUNTIME | 4 | contract,import_depends |
| 103 | D-INTELLIGENCE | D-ML_TRAIN | 4 | import_depends |
| 104 | D_OPS | D-TRADING | 4 | import_depends |
| 105 | D-GOV_SCRIPTS | D-RISK | 3 | import_depends |
| 106 | D_OPS | D_BEHAVIORAL_AUDIT | 3 | import_depends,runtime |
| 107 | D-AUTONOMY_PERM | D-GOVERNANCE | 3 | config_depends,test_depends |
| 108 | D-EX_CORE | D-TRADING | 3 | import_depends |
| 109 | D_AUTONOMY_CORE | D_SECURITY | 3 | import_depends |
| 110 | D-GOV_SCRIPTS | D_SHARED | 3 | import_depends |
| 111 | D_AUTONOMY_CORE | D-GOV_AUDIT | 3 | import_depends |
| 112 | D_SHARED | D-GOVERNANCE | 3 | import_depends |
| 113 | D-TRADING | D_OPS | 3 | import_depends,runtime |
| 114 | D-TRADING | D_AUTONOMY_CORE | 3 | import_depends |
| 115 | D-AUDITTEST | D_SECURITY | 3 | test_depends |
| 116 | D-TRADING | D-GOV_DRIFT | 3 | import_depends,runtime |
| 117 | D-GOV_ENFORCEMENT | D-GOVERNANCE | 3 | import_depends |
| 118 | D_BEHAVIORAL_AUDIT | D_INTEGRATION | 3 | import_depends |
| 119 | D_INFRA_TELEMETRY | D_SHARED | 3 | import_depends |
| 120 | D_INTEGRATION | D-GOV_ENFORCEMENT | 3 | import_depends |
| 121 | D_INTEGRATION | D-INTELLIGENCE | 3 | import_depends |
| 122 | D-INTELLIGENCE | D-SIMULATION | 3 | import_depends |
| 123 | D_SECURITY | D_INTEGRATION | 2 | import_depends |
| 124 | D-GOVERNANCE | D_REPORTING | 2 | import_depends |
| 125 | D_AUTONOMY_CORE | D-GOVERNANCE | 2 | import_depends |
| 126 | D_INFRA_A2A | D-GOVERNANCE | 2 | import_depends |
| 127 | D-GOV_DOCS | D-INTELLIGENCE | 2 | import_depends |
| 128 | D_INFRA_RECOVERY | D_INTEGRATION | 2 | import_depends |
| 129 | D_AUTONOMY_CORE | D-INTELLIGENCE | 2 | import_depends |
| 130 | D-GOV_SCRIPTS | D_SECURITY | 2 | import_depends |
| 131 | D-GOVERNANCE | D-CROSS_ASSET | 2 | test_depends |
| 132 | D-COMPLIANCE | D-GOV_DRIFT | 2 | import_depends |
| 133 | D-INTELLIGENCE | D-GOV_ENFORCEMENT | 2 | contract,import_depends |
| 134 | D_MKT_DATA | D-GOVERNANCE | 2 | config_depends |
| 135 | D-GOV_SCRIPTS | D_OPS | 2 | import_depends |
| 136 | D-PF_ALLOC | D_SHARED | 2 | contract,import_depends |
| 137 | D_BEHAVIORAL_AUDIT | D-GOV_AUDIT | 2 | import_depends |
| 138 | D-GOV_ENFORCEMENT | D_SECURITY | 2 | import_depends |
| 139 | D-GOV_SCRIPTS | D-GOV_AUDIT | 2 | import_depends |
| 140 | D_INTEGRATION | D_AUTONOMY_CORE | 2 | import_depends |
| 141 | D_BEHAVIORAL_AUDIT | D-GOVERNANCE | 2 | import_depends |
| 142 | D_INTEGRATION | D-GOV_AUDIT | 2 | import_depends |
| 143 | D-GOV_AUDIT | D_OPS | 2 | import_depends |
| 144 | D-GOV_AUDIT | D-TRADING | 2 | import_depends |
| 145 | D-AUDITTEST | D-GOV_ENFORCEMENT | 2 | test_depends |
| 146 | D-PF_ALLOC | D-GOVERNANCE | 2 | config_depends,import_depends |
| 147 | D-AUTONOMY_PERM | D_INTEGRATION | 2 | test_depends |
| 148 | D_INTEGRATION | D-TRADING | 2 | import_depends |
| 149 | D-ML_TRAIN | D-TRADING | 2 | import_depends |
| 150 | D_INFRA_OPS | D-GOV_AUDIT | 2 | import_depends |
| 151 | D-ML_TRAIN | D_SHARED | 2 | import_depends |
| 152 | D-SIMULATION | D_INTEGRATION | 2 | import_depends |
| 153 | D_SHARED | D-ML_TRAIN | 2 | import_depends |
| 154 | D-GOV_AUDIT | D_BEHAVIORAL_AUDIT | 2 | import_depends |
| 155 | D_SECURITY | D-TRADING | 2 | import_depends |
| 156 | D_FRONTEND | D_OPS | 2 | import_depends |
| 157 | D-AUTONOMY_PERM | D-GOV_AUDIT | 1 | test_depends |
| 158 | D-GOVERNANCE | D-KNOWLEDGE | 1 | contract |
| 159 | D-GOVERNANCE | D-GOV_DOCS | 1 | runtime |
| 160 | D-FUNDAMENTAL_SIGNAL | D-GOVERNANCE | 1 | import_depends |
| 161 | D_FRONTEND | D_SHARED | 1 | import_depends |
| 162 | D-GOV_DRIFT | D-AUTONOMY_PERM | 1 | runtime |
| 163 | D_FRONTEND | D_INFRA_OPS | 1 | import_depends |
| 164 | D-GOV_DRIFT | D-GOV_ENFORCEMENT | 1 | runtime |
| 165 | D-GOV_DRIFT | D-GOV_SCRIPTS | 1 | import_depends |
| 166 | D-GOV_DRIFT | D_SECURITY | 1 | test_depends |
| 167 | D-GOV_RULE | D_INTEGRATION | 1 | import_depends |
| 168 | D-GOV_RULE | D_SHARED | 1 | import_depends |
| 169 | D-GOV_SCRIPTS | D-EX_CORE | 1 | import_depends |
| 170 | D-GOV_SCRIPTS | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 171 | D-FACTOR | D_SHARED | 1 | import_depends |
| 172 | D-FACTOR | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 173 | D-GOV_SCRIPTS | D-INTELLIGENCE | 1 | import_depends |
| 174 | D-GOV_SCRIPTS | D_MKT_DATA | 1 | import_depends |
| 175 | D-GOV_SCRIPTS | D-SIMULATION | 1 | import_depends |
| 176 | D_INFRA_A2A | D-GOV_AUDIT | 1 | import_depends |
| 177 | D_DATA_SEC | D_OPS | 1 | import_depends |
| 178 | D_INFRA_A2A | D_INTEGRATION | 1 | import_depends |
| 179 | D_DATA_SEC | D-GOVERNANCE | 1 | import_depends |
| 180 | D-AUDITTEST | D-GOV_DRIFT | 1 | test_depends |
| 181 | D_INFRA_OPS | D_INFRA_RUNTIME | 1 | import_depends |
| 182 | D_INFRA_OPS | D_OPS | 1 | import_depends |
| 183 | D_INFRA_OPS | D_SHARED | 1 | import_depends |
| 184 | D-CROSS_ASSET | D_SHARED | 1 | import_depends |
| 185 | D_INFRA_RUNTIME | D_OPS | 1 | import_depends |
| 186 | D_INFRA_TELEMETRY | D_BEHAVIORAL_AUDIT | 1 | import_depends |
| 187 | D_INFRA_TELEMETRY | D-GOVERNANCE | 1 | import_depends |
| 188 | D_INFRA_TELEMETRY | D_OPS | 1 | import_depends |
| 189 | D_INTEGRATION | D_OPS | 1 | import_depends |
| 190 | D-INTELLIGENCE | D_AUTONOMY_CORE | 1 | import_depends |
| 191 | D-INTELLIGENCE | D_SHARED | 1 | import_depends |
| 192 | D-INTELLIGENCE | D-TRADING | 1 | import_depends |
| 193 | D-KNOWLEDGE | D_AUTONOMY_CORE | 1 | test_depends |
| 194 | D-AUTONOMY_PERM | D_INFRA_RUNTIME | 1 | test_depends |
| 195 | D-GOVERNANCE | D-ML_TRAIN | 1 | data |
| 196 | D_OPS | D-FACTOR | 1 | runtime |
| 197 | D_OPS | D-GOV_AUDIT | 1 | test_depends |
| 198 | D_OPS | D-GOV_DRIFT | 1 | import_depends |
| 199 | D-AUTONOMY_PERM | D_AUTONOMY_CORE | 1 | test_depends |
| 200 | D-PF_ALLOC | D-TRADING | 1 | import_depends |
| 201 | D-PF_CORE | D_REPORTING | 1 | import_depends |
| 202 | D-PF_CORE | D-TRADING | 1 | import_depends |
| 203 | D-POSITION | D-GOVERNANCE | 1 | config_depends |
| 204 | D_AUTONOMY_CORE | D-GOV_ENFORCEMENT | 1 | import_depends |
| 205 | D-RISK | D-GOVERNANCE | 1 | config_depends |
| 206 | D-RISK | D_SHARED | 1 | import_depends |
| 207 | D_SECURITY | D-INTELLIGENCE | 1 | import_depends |
| 208 | D_SHARED | D-GOV_AUDIT | 1 | import_depends |
| 209 | D_SHARED | D_INFRA_A2A | 1 | import_depends |
| 210 | D_SHARED | D-SIMULATION | 1 | import_depends |
| 211 | D-TRADING | D_BEHAVIORAL_AUDIT | 1 | import_depends |
| 212 | D-AUDITTEST | D_SHARED | 1 | test_depends |
| 213 | D-TRADING | D-GOV_DOCS | 1 | runtime |
| 214 | D-AUDITTEST | D_OPS | 1 | test_depends |
| 215 | D-GOVERNANCE | D-PF_ALLOC | 1 | import_depends |
