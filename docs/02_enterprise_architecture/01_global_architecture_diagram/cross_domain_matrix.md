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
| D_GOVERNANCE | D_OPS | 385 | config_depends,import_depends,runtime,test_depends |
| D_GOVERNANCE | D_INTEGRATION | 231 | import_depends,test_depends |
| D_GOVERNANCE | D_TRADING | 225 | import_depends,test_depends |
| D_GOVERNANCE | D_AUTONOMY_CORE | 214 | contract,import_depends,runtime,test_depends |
| D_GOVERNANCE | D_SECURITY | 206 | contract,import_depends,runtime,test_depends |
| D_GOVERNANCE | D_SHARED | 183 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_ENFORCEMENT | 168 | import_depends,runtime,test_depends |
| D_GOVERNANCE | D_GOV_AUDIT | 140 | contract,import_depends,runtime,test_depends |
| D_AUTONOMY_PERM | D_SECURITY | 137 | import_depends,test_depends |
| D_GOVERNANCE | D_INFRA_RUNTIME | 124 | config_depends,import_depends,runtime,test_depends |
| D_GOVERNANCE | D_BEHAVIORAL_AUDIT | 88 | import_depends,test_depends |
| D_INTEGRATION | D_SHARED | 70 | import_depends |
| D_SECURITY | D_BEHAVIORAL_AUDIT | 51 | import_depends |
| D_TRADING | D_INTEGRATION | 49 | event,import_depends |
| D_GOVERNANCE | D_INTELLIGENCE | 49 | import_depends,test_depends |
| D_TRADING | D_SHARED | 42 | contract,import_depends |
| D_INFRA_RUNTIME | D_SHARED | 36 | import_depends |
| D_GOV_AUDIT | D_SHARED | 35 | import_depends |
| D_OPS | D_INFRA_RUNTIME | 33 | import_depends,test_depends |
| D_INFRA_RECOVERY | D_INFRA_RUNTIME | 33 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D_GOVERNANCE | D_OPS | 385 | config_depends,import_depends,runtime,test_depends |
| 2 | D_GOVERNANCE | D_INTEGRATION | 231 | import_depends,test_depends |
| 3 | D_GOVERNANCE | D_TRADING | 225 | import_depends,test_depends |
| 4 | D_GOVERNANCE | D_AUTONOMY_CORE | 214 | contract,import_depends,runtime,test_depends |
| 5 | D_GOVERNANCE | D_SECURITY | 206 | contract,import_depends,runtime,test_depends |
| 6 | D_GOVERNANCE | D_SHARED | 183 | import_depends,test_depends |
| 7 | D_GOVERNANCE | D_GOV_ENFORCEMENT | 168 | import_depends,runtime,test_depends |
| 8 | D_GOVERNANCE | D_GOV_AUDIT | 140 | contract,import_depends,runtime,test_depends |
| 9 | D_AUTONOMY_PERM | D_SECURITY | 137 | import_depends,test_depends |
| 10 | D_GOVERNANCE | D_INFRA_RUNTIME | 124 | config_depends,import_depends,runtime,test_depends |
| 11 | D_GOVERNANCE | D_BEHAVIORAL_AUDIT | 88 | import_depends,test_depends |
| 12 | D_INTEGRATION | D_SHARED | 70 | import_depends |
| 13 | D_SECURITY | D_BEHAVIORAL_AUDIT | 51 | import_depends |
| 14 | D_TRADING | D_INTEGRATION | 49 | event,import_depends |
| 15 | D_GOVERNANCE | D_INTELLIGENCE | 49 | import_depends,test_depends |
| 16 | D_TRADING | D_SHARED | 42 | contract,import_depends |
| 17 | D_INFRA_RUNTIME | D_SHARED | 36 | import_depends |
| 18 | D_GOV_AUDIT | D_SHARED | 35 | import_depends |
| 19 | D_OPS | D_INFRA_RUNTIME | 33 | import_depends,test_depends |
| 20 | D_INFRA_RECOVERY | D_INFRA_RUNTIME | 33 | import_depends |
| 21 | D_GOV_SCRIPTS | D_GOVERNANCE | 30 | import_depends |
| 22 | D_OPS | D_GOVERNANCE | 29 | config_depends,import_depends,runtime,test_depends |
| 23 | D_TRADING | D_GOVERNANCE | 28 | contract,import_depends,runtime |
| 24 | D_GOV_DOCS | D_GOVERNANCE | 26 | import_depends,runtime |
| 25 | D_GOVERNANCE | D_GOV_DRIFT | 25 | config_depends,contract,import_depends,runtime,test_depends |
| 26 | D_AUTONOMY_CORE | D_INTEGRATION | 24 | import_depends |
| 27 | D_GOV_AUDIT | D_GOVERNANCE | 21 | config_depends,contract,import_depends,runtime |
| 28 | D_INFRA_RUNTIME | D_INTEGRATION | 21 | import_depends |
| 29 | D_GOV_DOCS | D_SHARED | 19 | import_depends |
| 30 | D_INFRA_A2A | D_SHARED | 18 | import_depends |
| 31 | D_FUNDAMENTAL_SIGNAL | D_TRADING | 17 | import_depends |
| 32 | D_GOVERNANCE | D_MKT_DATA | 16 | test_depends |
| 33 | D_KNOWLEDGE | D_INTEGRATION | 15 | import_depends,test_depends |
| 34 | D_OPS | D_SHARED | 14 | import_depends,test_depends |
| 35 | D_GOVERNANCE | D_RISK | 14 | test_depends |
| 36 | D_KNOWLEDGE | D_GOVERNANCE | 13 | import_depends,runtime,test_depends |
| 37 | D_INFRA_A2A | D_INFRA_RUNTIME | 13 | import_depends |
| 38 | D_GOV_AUDIT | D_GOV_DRIFT | 13 | import_depends,runtime |
| 39 | D_GOV_ENFORCEMENT | D_INTEGRATION | 13 | import_depends |
| 40 | D_GOV_SCRIPTS | D_INTEGRATION | 13 | import_depends |
| 41 | D_INFRA_TELEMETRY | D_INFRA_RUNTIME | 12 | import_depends |
| 42 | D_TRADING | D_SECURITY | 12 | import_depends |
| 43 | D_PF_CORE | D_GOVERNANCE | 12 | contract,import_depends |
| 44 | D_GOVERNANCE | D_SIMULATION | 12 | test_depends |
| 45 | D_GOVERNANCE | D_GOV_SCRIPTS | 12 | test_depends |
| 46 | D_COMPLIANCE | D_GOV_AUDIT | 11 | import_depends |
| 47 | D_INTEGRATION | D_GOVERNANCE | 11 | config_depends,import_depends |
| 48 | D_TRADING | D_GOV_AUDIT | 11 | contract,import_depends |
| 49 | D_GOV_SCRIPTS | D_INFRA_RUNTIME | 11 | import_depends |
| 50 | D_GOV_DOCS | D_INTEGRATION | 11 | import_depends |
| 51 | D_EX_CORE | D_GOVERNANCE | 10 | config_depends,import_depends |
| 52 | D_GOV_DOCS | D_GOV_ENFORCEMENT | 10 | import_depends |
| 53 | D_GOV_DRIFT | D_GOVERNANCE | 10 | config_depends,import_depends,runtime,test_depends |
| 54 | D_RISK | D_TRADING | 10 | import_depends |
| 55 | D_REPORTING | D_GOVERNANCE | 10 | import_depends |
| 56 | D_COMPLIANCE | D_GOVERNANCE | 10 | import_depends |
| 57 | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | 10 | import_depends |
| 58 | D_INFRA_RUNTIME | D_GOVERNANCE | 9 | import_depends |
| 59 | D_REPORTING | D_TRADING | 9 | import_depends |
| 60 | D_OPS | D_AUTONOMY_CORE | 8 | import_depends,runtime,test_depends |
| 61 | D_GOVERNANCE | D_FRONTEND | 8 | test_depends |
| 62 | D_GOVERNANCE | D_FUNDAMENTAL_SIGNAL | 8 | test_depends |
| 63 | D_GOV_DRIFT | D_BEHAVIORAL_AUDIT | 8 | test_depends |
| 64 | D_GOV_ENFORCEMENT | D_SHARED | 8 | import_depends |
| 65 | D_INFRA_OPS | D_GOVERNANCE | 8 | config_depends,import_depends,test_depends |
| 66 | D_INFRA_RECOVERY | D_GOV_AUDIT | 7 | import_depends |
| 67 | D_SHARED | D_INTEGRATION | 7 | import_depends |
| 68 | D_GOV_DRIFT | D_GOV_AUDIT | 7 | import_depends,runtime |
| 69 | D_AUDITTEST | D_GOV_AUDIT | 7 | test_depends |
| 70 | D_GOVERNANCE | D_GOV_RULE | 7 | import_depends,test_depends |
| 71 | D_TRADING | D_INTELLIGENCE | 6 | import_depends |
| 72 | D_TRADING | D_GOV_ENFORCEMENT | 6 | contract,import_depends |
| 73 | D_GOVERNANCE | D_PF_CORE | 6 | test_depends |
| 74 | D_SHARED | D_INFRA_RUNTIME | 6 | import_depends |
| 75 | D_GOVERNANCE | D_EX_CORE | 6 | test_depends |
| 76 | D_AUTONOMY_CORE | D_SHARED | 6 | import_depends |
| 77 | D_INTELLIGENCE | D_INTEGRATION | 6 | import_depends |
| 78 | D_INTELLIGENCE | D_GOVERNANCE | 6 | config_depends,import_depends |
| 79 | D_GOVERNANCE | D_INFRA_A2A | 6 | import_depends |
| 80 | D_OPS | D_INTEGRATION | 6 | import_depends,runtime |
| 81 | D_GOV_AUDIT | D_SECURITY | 6 | import_depends |
| 82 | D_SHARED | D_OPS | 6 | import_depends |
| 83 | D_GOV_AUDIT | D_GOV_ENFORCEMENT | 5 | import_depends,runtime |
| 84 | D_OPS | D_SECURITY | 5 | import_depends,test_depends |
| 85 | D_GOV_ENFORCEMENT | D_BEHAVIORAL_AUDIT | 5 | import_depends |
| 86 | D_INFRA_RECOVERY | D_SHARED | 5 | import_depends |
| 87 | D_GOV_AUDIT | D_INTEGRATION | 5 | import_depends |
| 88 | D_CROSS_ASSET | D_TRADING | 5 | contract,import_depends |
| 89 | D_SECURITY | D_GOV_AUDIT | 5 | import_depends |
| 90 | D_SECURITY | D_GOV_ENFORCEMENT | 5 | import_depends |
| 91 | D_GOV_AUDIT | D_INFRA_RUNTIME | 5 | import_depends |
| 92 | D_SECURITY | D_SHARED | 5 | import_depends |
| 93 | D_FACTOR | D_GOVERNANCE | 5 | config_depends,import_depends |
| 94 | D_GOVERNANCE | D_AUTONOMY_PERM | 4 | contract,runtime |
| 95 | D_INFRA_RECOVERY | D_GOVERNANCE | 4 | import_depends |
| 96 | D_FRONTEND | D_GOVERNANCE | 4 | import_depends |
| 97 | D_INTEGRATION | D_SECURITY | 4 | import_depends |
| 98 | D_GOV_ENFORCEMENT | D_GOV_AUDIT | 4 | import_depends |
| 99 | D_INFRA_RUNTIME | D_GOV_AUDIT | 4 | import_depends |
| 100 | D_SECURITY | D_GOVERNANCE | 4 | import_depends |
| 101 | D_GOVERNANCE | D_FACTOR | 4 | test_depends |
| 102 | D_TRADING | D_INFRA_RUNTIME | 4 | contract,import_depends |
| 103 | D_INTELLIGENCE | D_ML_TRAIN | 4 | import_depends |
| 104 | D_OPS | D_TRADING | 4 | import_depends |
| 105 | D_GOV_SCRIPTS | D_RISK | 3 | import_depends |
| 106 | D_OPS | D_BEHAVIORAL_AUDIT | 3 | import_depends,runtime |
| 107 | D_AUTONOMY_PERM | D_GOVERNANCE | 3 | config_depends,test_depends |
| 108 | D_EX_CORE | D_TRADING | 3 | import_depends |
| 109 | D_AUTONOMY_CORE | D_SECURITY | 3 | import_depends |
| 110 | D_GOV_SCRIPTS | D_SHARED | 3 | import_depends |
| 111 | D_AUTONOMY_CORE | D_GOV_AUDIT | 3 | import_depends |
| 112 | D_SHARED | D_GOVERNANCE | 3 | import_depends |
| 113 | D_TRADING | D_OPS | 3 | import_depends,runtime |
| 114 | D_TRADING | D_AUTONOMY_CORE | 3 | import_depends |
| 115 | D_AUDITTEST | D_SECURITY | 3 | test_depends |
| 116 | D_TRADING | D_GOV_DRIFT | 3 | import_depends,runtime |
| 117 | D_GOV_ENFORCEMENT | D_GOVERNANCE | 3 | import_depends |
| 118 | D_BEHAVIORAL_AUDIT | D_INTEGRATION | 3 | import_depends |
| 119 | D_INFRA_TELEMETRY | D_SHARED | 3 | import_depends |
| 120 | D_INTEGRATION | D_GOV_ENFORCEMENT | 3 | import_depends |
| 121 | D_INTEGRATION | D_INTELLIGENCE | 3 | import_depends |
| 122 | D_INTELLIGENCE | D_SIMULATION | 3 | import_depends |
| 123 | D_SECURITY | D_INTEGRATION | 2 | import_depends |
| 124 | D_GOVERNANCE | D_REPORTING | 2 | import_depends |
| 125 | D_AUTONOMY_CORE | D_GOVERNANCE | 2 | import_depends |
| 126 | D_INFRA_A2A | D_GOVERNANCE | 2 | import_depends |
| 127 | D_GOV_DOCS | D_INTELLIGENCE | 2 | import_depends |
| 128 | D_INFRA_RECOVERY | D_INTEGRATION | 2 | import_depends |
| 129 | D_AUTONOMY_CORE | D_INTELLIGENCE | 2 | import_depends |
| 130 | D_GOV_SCRIPTS | D_SECURITY | 2 | import_depends |
| 131 | D_GOVERNANCE | D_CROSS_ASSET | 2 | test_depends |
| 132 | D_COMPLIANCE | D_GOV_DRIFT | 2 | import_depends |
| 133 | D_INTELLIGENCE | D_GOV_ENFORCEMENT | 2 | contract,import_depends |
| 134 | D_MKT_DATA | D_GOVERNANCE | 2 | config_depends |
| 135 | D_GOV_SCRIPTS | D_OPS | 2 | import_depends |
| 136 | D_PF_ALLOC | D_SHARED | 2 | contract,import_depends |
| 137 | D_BEHAVIORAL_AUDIT | D_GOV_AUDIT | 2 | import_depends |
| 138 | D_GOV_ENFORCEMENT | D_SECURITY | 2 | import_depends |
| 139 | D_GOV_SCRIPTS | D_GOV_AUDIT | 2 | import_depends |
| 140 | D_INTEGRATION | D_AUTONOMY_CORE | 2 | import_depends |
| 141 | D_BEHAVIORAL_AUDIT | D_GOVERNANCE | 2 | import_depends |
| 142 | D_INTEGRATION | D_GOV_AUDIT | 2 | import_depends |
| 143 | D_GOV_AUDIT | D_OPS | 2 | import_depends |
| 144 | D_GOV_AUDIT | D_TRADING | 2 | import_depends |
| 145 | D_AUDITTEST | D_GOV_ENFORCEMENT | 2 | test_depends |
| 146 | D_PF_ALLOC | D_GOVERNANCE | 2 | config_depends,import_depends |
| 147 | D_AUTONOMY_PERM | D_INTEGRATION | 2 | test_depends |
| 148 | D_INTEGRATION | D_TRADING | 2 | import_depends |
| 149 | D_ML_TRAIN | D_TRADING | 2 | import_depends |
| 150 | D_INFRA_OPS | D_GOV_AUDIT | 2 | import_depends |
| 151 | D_ML_TRAIN | D_SHARED | 2 | import_depends |
| 152 | D_SIMULATION | D_INTEGRATION | 2 | import_depends |
| 153 | D_SHARED | D_ML_TRAIN | 2 | import_depends |
| 154 | D_GOV_AUDIT | D_BEHAVIORAL_AUDIT | 2 | import_depends |
| 155 | D_SECURITY | D_TRADING | 2 | import_depends |
| 156 | D_FRONTEND | D_OPS | 2 | import_depends |
| 157 | D_AUTONOMY_PERM | D_GOV_AUDIT | 1 | test_depends |
| 158 | D_GOVERNANCE | D_KNOWLEDGE | 1 | contract |
| 159 | D_GOVERNANCE | D_GOV_DOCS | 1 | runtime |
| 160 | D_FUNDAMENTAL_SIGNAL | D_GOVERNANCE | 1 | import_depends |
| 161 | D_FRONTEND | D_SHARED | 1 | import_depends |
| 162 | D_GOV_DRIFT | D_AUTONOMY_PERM | 1 | runtime |
| 163 | D_FRONTEND | D_INFRA_OPS | 1 | import_depends |
| 164 | D_GOV_DRIFT | D_GOV_ENFORCEMENT | 1 | runtime |
| 165 | D_GOV_DRIFT | D_GOV_SCRIPTS | 1 | import_depends |
| 166 | D_GOV_DRIFT | D_SECURITY | 1 | test_depends |
| 167 | D_GOV_RULE | D_INTEGRATION | 1 | import_depends |
| 168 | D_GOV_RULE | D_SHARED | 1 | import_depends |
| 169 | D_GOV_SCRIPTS | D_EX_CORE | 1 | import_depends |
| 170 | D_GOV_SCRIPTS | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 171 | D_FACTOR | D_SHARED | 1 | import_depends |
| 172 | D_FACTOR | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 173 | D_GOV_SCRIPTS | D_INTELLIGENCE | 1 | import_depends |
| 174 | D_GOV_SCRIPTS | D_MKT_DATA | 1 | import_depends |
| 175 | D_GOV_SCRIPTS | D_SIMULATION | 1 | import_depends |
| 176 | D_INFRA_A2A | D_GOV_AUDIT | 1 | import_depends |
| 177 | D_DATA_SEC | D_OPS | 1 | import_depends |
| 178 | D_INFRA_A2A | D_INTEGRATION | 1 | import_depends |
| 179 | D_DATA_SEC | D_GOVERNANCE | 1 | import_depends |
| 180 | D_AUDITTEST | D_GOV_DRIFT | 1 | test_depends |
| 181 | D_INFRA_OPS | D_INFRA_RUNTIME | 1 | import_depends |
| 182 | D_INFRA_OPS | D_OPS | 1 | import_depends |
| 183 | D_INFRA_OPS | D_SHARED | 1 | import_depends |
| 184 | D_CROSS_ASSET | D_SHARED | 1 | import_depends |
| 185 | D_INFRA_RUNTIME | D_OPS | 1 | import_depends |
| 186 | D_INFRA_TELEMETRY | D_BEHAVIORAL_AUDIT | 1 | import_depends |
| 187 | D_INFRA_TELEMETRY | D_GOVERNANCE | 1 | import_depends |
| 188 | D_INFRA_TELEMETRY | D_OPS | 1 | import_depends |
| 189 | D_INTEGRATION | D_OPS | 1 | import_depends |
| 190 | D_INTELLIGENCE | D_AUTONOMY_CORE | 1 | import_depends |
| 191 | D_INTELLIGENCE | D_SHARED | 1 | import_depends |
| 192 | D_INTELLIGENCE | D_TRADING | 1 | import_depends |
| 193 | D_KNOWLEDGE | D_AUTONOMY_CORE | 1 | test_depends |
| 194 | D_AUTONOMY_PERM | D_INFRA_RUNTIME | 1 | test_depends |
| 195 | D_GOVERNANCE | D_ML_TRAIN | 1 | data |
| 196 | D_OPS | D_FACTOR | 1 | runtime |
| 197 | D_OPS | D_GOV_AUDIT | 1 | test_depends |
| 198 | D_OPS | D_GOV_DRIFT | 1 | import_depends |
| 199 | D_AUTONOMY_PERM | D_AUTONOMY_CORE | 1 | test_depends |
| 200 | D_PF_ALLOC | D_TRADING | 1 | import_depends |
| 201 | D_PF_CORE | D_REPORTING | 1 | import_depends |
| 202 | D_PF_CORE | D_TRADING | 1 | import_depends |
| 203 | D_POSITION | D_GOVERNANCE | 1 | config_depends |
| 204 | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 205 | D_RISK | D_GOVERNANCE | 1 | config_depends |
| 206 | D_RISK | D_SHARED | 1 | import_depends |
| 207 | D_SECURITY | D_INTELLIGENCE | 1 | import_depends |
| 208 | D_SHARED | D_GOV_AUDIT | 1 | import_depends |
| 209 | D_SHARED | D_INFRA_A2A | 1 | import_depends |
| 210 | D_SHARED | D_SIMULATION | 1 | import_depends |
| 211 | D_TRADING | D_BEHAVIORAL_AUDIT | 1 | import_depends |
| 212 | D_AUDITTEST | D_SHARED | 1 | test_depends |
| 213 | D_TRADING | D_GOV_DOCS | 1 | runtime |
| 214 | D_AUDITTEST | D_OPS | 1 | test_depends |
| 215 | D_GOVERNANCE | D_PF_ALLOC | 1 | import_depends |
