---
doc_type: cross_domain_matrix
title: 域间依赖矩阵
version: "1.0"
status: active
date: 2026-06-26
owner: auto-generator
ttl: permanent
---

# 域间依赖矩阵

> **文档作用 / Purpose**: 以矩阵形式展示所有功能域之间的依赖关系，识别高耦合域和独立域，为架构解耦提供依据。

> 本文档由 generate_cross_domain_matrix.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-26 18:51:26
> 数据源: depgraph.db edges表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 跨域依赖对数 | 217 |
| 跨域依赖边总数 | 3554 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D-GOVERNANCE | D-OPS | 385 | import_depends,test_depends,config_depends,runtime |
| D-GOVERNANCE | D-INTEGRATION | 231 | import_depends,test_depends |
| D-GOVERNANCE | D-TRADING | 226 | import_depends,test_depends |
| D-GOVERNANCE | D-AUTONOMY_CORE | 214 | import_depends,test_depends,contract,runtime |
| D-GOVERNANCE | D-SECURITY | 206 | import_depends,test_depends,contract,runtime |
| D-GOVERNANCE | D-SHARED | 185 | import_depends,test_depends |
| D-GOVERNANCE | D-GOV_ENFORCEMENT | 168 | import_depends,test_depends,runtime |
| D-GOVERNANCE | D-GOV_AUDIT | 140 | import_depends,test_depends,contract,runtime |
| D-AUTONOMY_PERM | D-SECURITY | 137 | import_depends,test_depends |
| D-GOVERNANCE | D-INFRA_RUNTIME | 125 | import_depends,test_depends,config_depends,runtime |
| D-GOVERNANCE | D-BEHAVIORAL_AUDIT | 89 | import_depends,test_depends |
| D-INTEGRATION | D-SHARED | 70 | import_depends |
| D-TRADING | D-INTEGRATION | 52 | import_depends,event |
| D-SECURITY | D-BEHAVIORAL_AUDIT | 51 | import_depends |
| D-GOVERNANCE | D-INTELLIGENCE | 50 | import_depends,test_depends |
| D-TRADING | D-SHARED | 42 | import_depends,contract |
| D-GOV_AUDIT | D-SHARED | 41 | import_depends |
| D-INFRA_RUNTIME | D-SHARED | 36 | import_depends |
| D-INFRA_RECOVERY | D-INFRA_RUNTIME | 33 | import_depends |
| D-OPS | D-INFRA_RUNTIME | 33 | import_depends,test_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D-GOVERNANCE | D-OPS | 385 | import_depends,test_depends,config_depends,runtime |
| 2 | D-GOVERNANCE | D-INTEGRATION | 231 | import_depends,test_depends |
| 3 | D-GOVERNANCE | D-TRADING | 226 | import_depends,test_depends |
| 4 | D-GOVERNANCE | D-AUTONOMY_CORE | 214 | import_depends,test_depends,contract,runtime |
| 5 | D-GOVERNANCE | D-SECURITY | 206 | import_depends,test_depends,contract,runtime |
| 6 | D-GOVERNANCE | D-SHARED | 185 | import_depends,test_depends |
| 7 | D-GOVERNANCE | D-GOV_ENFORCEMENT | 168 | import_depends,test_depends,runtime |
| 8 | D-GOVERNANCE | D-GOV_AUDIT | 140 | import_depends,test_depends,contract,runtime |
| 9 | D-AUTONOMY_PERM | D-SECURITY | 137 | import_depends,test_depends |
| 10 | D-GOVERNANCE | D-INFRA_RUNTIME | 125 | import_depends,test_depends,config_depends,runtime |
| 11 | D-GOVERNANCE | D-BEHAVIORAL_AUDIT | 89 | import_depends,test_depends |
| 12 | D-INTEGRATION | D-SHARED | 70 | import_depends |
| 13 | D-TRADING | D-INTEGRATION | 52 | import_depends,event |
| 14 | D-SECURITY | D-BEHAVIORAL_AUDIT | 51 | import_depends |
| 15 | D-GOVERNANCE | D-INTELLIGENCE | 50 | import_depends,test_depends |
| 16 | D-TRADING | D-SHARED | 42 | import_depends,contract |
| 17 | D-GOV_AUDIT | D-SHARED | 41 | import_depends |
| 18 | D-INFRA_RUNTIME | D-SHARED | 36 | import_depends |
| 19 | D-INFRA_RECOVERY | D-INFRA_RUNTIME | 33 | import_depends |
| 20 | D-OPS | D-INFRA_RUNTIME | 33 | import_depends,test_depends |
| 21 | D-GOV_SCRIPTS | D-GOVERNANCE | 30 | import_depends |
| 22 | D-OPS | D-GOVERNANCE | 29 | import_depends,test_depends,config_depends,runtime |
| 23 | D-TRADING | D-GOVERNANCE | 28 | import_depends,runtime,contract |
| 24 | D-GOV_DOCS | D-GOVERNANCE | 26 | import_depends,runtime |
| 25 | D-GOVERNANCE | D-GOV_DRIFT | 25 | import_depends,test_depends,config_depends,runtime,contract |
| 26 | D-AUTONOMY_CORE | D-INTEGRATION | 24 | import_depends |
| 27 | D-INFRA_RUNTIME | D-INTEGRATION | 22 | import_depends |
| 28 | D-GOV_AUDIT | D-GOVERNANCE | 21 | import_depends,config_depends,runtime,contract |
| 29 | D-GOV_DOCS | D-SHARED | 19 | import_depends |
| 30 | D-INFRA_A2A | D-SHARED | 18 | import_depends |
| 31 | D-FUNDAMENTAL_SIGNAL | D-TRADING | 17 | import_depends |
| 32 | D-GOVERNANCE | D-MKT_DATA | 16 | test_depends |
| 33 | D-INTEGRATION | D-INTELLIGENCE | 16 | import_depends |
| 34 | D-KNOWLEDGE | D-INTEGRATION | 16 | import_depends,test_depends |
| 35 | D-GOVERNANCE | D-RISK | 14 | test_depends |
| 36 | D-INFRA_A2A | D-INFRA_RUNTIME | 14 | import_depends |
| 37 | D-OPS | D-SHARED | 14 | import_depends,test_depends |
| 38 | D-GOV_AUDIT | D-GOV_DRIFT | 13 | import_depends,runtime |
| 39 | D-GOV_ENFORCEMENT | D-INTEGRATION | 13 | import_depends |
| 40 | D-GOV_SCRIPTS | D-INTEGRATION | 13 | import_depends |
| 41 | D-KNOWLEDGE | D-GOVERNANCE | 13 | import_depends,test_depends,runtime |
| 42 | D-GOVERNANCE | D-GOV_SCRIPTS | 12 | test_depends |
| 43 | D-GOVERNANCE | D-SIMULATION | 12 | test_depends |
| 44 | D-INFRA_TELEMETRY | D-INFRA_RUNTIME | 12 | import_depends |
| 45 | D-PF_CORE | D-GOVERNANCE | 12 | import_depends,contract |
| 46 | D-TRADING | D-SECURITY | 12 | import_depends |
| 47 | D-COMPLIANCE | D-GOV_AUDIT | 11 | import_depends |
| 48 | D-GOV_DOCS | D-INTEGRATION | 11 | import_depends |
| 49 | D-GOV_SCRIPTS | D-INFRA_RUNTIME | 11 | import_depends |
| 50 | D-INTEGRATION | D-GOVERNANCE | 11 | import_depends,config_depends |
| 51 | D-TRADING | D-GOV_AUDIT | 11 | import_depends,contract |
| 52 | D-COMPLIANCE | D-GOVERNANCE | 10 | import_depends |
| 53 | D-EX_CORE | D-GOVERNANCE | 10 | import_depends,config_depends |
| 54 | D-GOV_DOCS | D-GOV_ENFORCEMENT | 10 | import_depends |
| 55 | D-GOV_DRIFT | D-GOVERNANCE | 10 | import_depends,test_depends,config_depends,runtime |
| 56 | D-GOV_SCRIPTS | D-GOV_ENFORCEMENT | 10 | import_depends |
| 57 | D-REPORTING | D-GOVERNANCE | 10 | import_depends |
| 58 | D-RISK | D-TRADING | 10 | import_depends |
| 59 | D-INFRA_RUNTIME | D-GOVERNANCE | 9 | import_depends |
| 60 | D-REPORTING | D-TRADING | 9 | import_depends |
| 61 | D-GOVERNANCE | D-FRONTEND | 8 | test_depends |
| 62 | D-GOVERNANCE | D-FUNDAMENTAL_SIGNAL | 8 | test_depends |
| 63 | D-GOV_DRIFT | D-BEHAVIORAL_AUDIT | 8 | test_depends |
| 64 | D-GOV_ENFORCEMENT | D-SHARED | 8 | import_depends |
| 65 | D-INFRA_OPS | D-GOVERNANCE | 8 | import_depends,test_depends,config_depends |
| 66 | D-OPS | D-AUTONOMY_CORE | 8 | import_depends,test_depends,runtime |
| 67 | D-AUDITTEST | D-GOV_AUDIT | 7 | test_depends |
| 68 | D-GOVERNANCE | D-GOV_RULE | 7 | import_depends,test_depends |
| 69 | D-GOV_DRIFT | D-GOV_AUDIT | 7 | import_depends,runtime |
| 70 | D-INFRA_RECOVERY | D-GOV_AUDIT | 7 | import_depends |
| 71 | D-INTELLIGENCE | D-GOVERNANCE | 7 | import_depends,config_depends |
| 72 | D-SHARED | D-INTEGRATION | 7 | import_depends |
| 73 | D-AUTONOMY_CORE | D-SHARED | 6 | import_depends |
| 74 | D-GOVERNANCE | D-EX_CORE | 6 | test_depends |
| 75 | D-GOVERNANCE | D-INFRA_A2A | 6 | import_depends |
| 76 | D-GOVERNANCE | D-PF_CORE | 6 | test_depends |
| 77 | D-GOV_AUDIT | D-SECURITY | 6 | import_depends |
| 78 | D-INTELLIGENCE | D-INTEGRATION | 6 | import_depends |
| 79 | D-OPS | D-INTEGRATION | 6 | import_depends,runtime |
| 80 | D-SHARED | D-INFRA_RUNTIME | 6 | import_depends |
| 81 | D-SHARED | D-OPS | 6 | import_depends |
| 82 | D-TRADING | D-GOV_ENFORCEMENT | 6 | import_depends,contract |
| 83 | D-TRADING | D-INTELLIGENCE | 6 | import_depends |
| 84 | D-CROSS_ASSET | D-TRADING | 5 | import_depends,contract |
| 85 | D-FACTOR | D-GOVERNANCE | 5 | import_depends,config_depends |
| 86 | D-GOV_AUDIT | D-GOV_ENFORCEMENT | 5 | import_depends,runtime |
| 87 | D-GOV_AUDIT | D-INFRA_RUNTIME | 5 | import_depends |
| 88 | D-GOV_AUDIT | D-INTEGRATION | 5 | import_depends |
| 89 | D-GOV_ENFORCEMENT | D-BEHAVIORAL_AUDIT | 5 | import_depends |
| 90 | D-INFRA_RECOVERY | D-SHARED | 5 | import_depends |
| 91 | D-OPS | D-SECURITY | 5 | import_depends,test_depends |
| 92 | D-SECURITY | D-GOV_AUDIT | 5 | import_depends |
| 93 | D-SECURITY | D-GOV_ENFORCEMENT | 5 | import_depends |
| 94 | D-SECURITY | D-SHARED | 5 | import_depends |
| 95 | D-FRONTEND | D-GOVERNANCE | 4 | import_depends |
| 96 | D-GOVERNANCE | D-AUTONOMY_PERM | 4 | runtime,contract |
| 97 | D-GOVERNANCE | D-FACTOR | 4 | test_depends |
| 98 | D-GOV_ENFORCEMENT | D-GOV_AUDIT | 4 | import_depends |
| 99 | D-INFRA_RECOVERY | D-GOVERNANCE | 4 | import_depends |
| 100 | D-INFRA_RUNTIME | D-GOV_AUDIT | 4 | import_depends |
| 101 | D-INTEGRATION | D-SECURITY | 4 | import_depends |
| 102 | D-INTELLIGENCE | D-ML_TRAIN | 4 | import_depends |
| 103 | D-OPS | D-TRADING | 4 | import_depends |
| 104 | D-SECURITY | D-GOVERNANCE | 4 | import_depends |
| 105 | D-TRADING | D-INFRA_RUNTIME | 4 | import_depends,contract |
| 106 | D-AUDITTEST | D-SECURITY | 3 | test_depends |
| 107 | D-AUTONOMY_CORE | D-GOV_AUDIT | 3 | import_depends |
| 108 | D-AUTONOMY_CORE | D-SECURITY | 3 | import_depends |
| 109 | D-AUTONOMY_PERM | D-GOVERNANCE | 3 | test_depends,config_depends |
| 110 | D-BEHAVIORAL_AUDIT | D-INTEGRATION | 3 | import_depends |
| 111 | D-EX_CORE | D-TRADING | 3 | import_depends |
| 112 | D-GOV_ENFORCEMENT | D-GOVERNANCE | 3 | import_depends |
| 113 | D-GOV_SCRIPTS | D-RISK | 3 | import_depends |
| 114 | D-GOV_SCRIPTS | D-SHARED | 3 | import_depends |
| 115 | D-INFRA_A2A | D-GOVERNANCE | 3 | import_depends |
| 116 | D-INFRA_TELEMETRY | D-SHARED | 3 | import_depends |
| 117 | D-INTEGRATION | D-GOV_ENFORCEMENT | 3 | import_depends |
| 118 | D-INTELLIGENCE | D-SIMULATION | 3 | import_depends |
| 119 | D-OPS | D-BEHAVIORAL_AUDIT | 3 | import_depends,runtime |
| 120 | D-SHARED | D-GOVERNANCE | 3 | import_depends |
| 121 | D-TRADING | D-AUTONOMY_CORE | 3 | import_depends |
| 122 | D-TRADING | D-GOV_DRIFT | 3 | import_depends,runtime |
| 123 | D-TRADING | D-OPS | 3 | import_depends,runtime |
| 124 | D-AUDITTEST | D-GOV_ENFORCEMENT | 2 | test_depends |
| 125 | D-AUTONOMY_CORE | D-GOVERNANCE | 2 | import_depends |
| 126 | D-AUTONOMY_CORE | D-INTELLIGENCE | 2 | import_depends |
| 127 | D-AUTONOMY_PERM | D-INTEGRATION | 2 | test_depends |
| 128 | D-BEHAVIORAL_AUDIT | D-GOVERNANCE | 2 | import_depends |
| 129 | D-BEHAVIORAL_AUDIT | D-GOV_AUDIT | 2 | import_depends |
| 130 | D-COMPLIANCE | D-GOV_DRIFT | 2 | import_depends |
| 131 | D-FRONTEND | D-OPS | 2 | import_depends |
| 132 | D-GOVERNANCE | D-CROSS_ASSET | 2 | test_depends |
| 133 | D-GOVERNANCE | D-REPORTING | 2 | import_depends |
| 134 | D-GOV_AUDIT | D-BEHAVIORAL_AUDIT | 2 | import_depends |
| 135 | D-GOV_AUDIT | D-OPS | 2 | import_depends |
| 136 | D-GOV_AUDIT | D-TRADING | 2 | import_depends |
| 137 | D-GOV_DOCS | D-INTELLIGENCE | 2 | import_depends |
| 138 | D-GOV_ENFORCEMENT | D-SECURITY | 2 | import_depends |
| 139 | D-GOV_SCRIPTS | D-GOV_AUDIT | 2 | import_depends |
| 140 | D-GOV_SCRIPTS | D-OPS | 2 | import_depends |
| 141 | D-GOV_SCRIPTS | D-SECURITY | 2 | import_depends |
| 142 | D-INFRA_OPS | D-GOV_AUDIT | 2 | import_depends |
| 143 | D-INFRA_RECOVERY | D-INTEGRATION | 2 | import_depends |
| 144 | D-INTEGRATION | D-AUTONOMY_CORE | 2 | import_depends |
| 145 | D-INTEGRATION | D-GOV_AUDIT | 2 | import_depends |
| 146 | D-INTEGRATION | D-TRADING | 2 | import_depends |
| 147 | D-INTELLIGENCE | D-GOV_ENFORCEMENT | 2 | import_depends,contract |
| 148 | D-MKT_DATA | D-GOVERNANCE | 2 | config_depends |
| 149 | D-ML_TRAIN | D-SHARED | 2 | import_depends |
| 150 | D-ML_TRAIN | D-TRADING | 2 | import_depends |
| 151 | D-PF_ALLOC | D-GOVERNANCE | 2 | import_depends,config_depends |
| 152 | D-PF_ALLOC | D-SHARED | 2 | import_depends,contract |
| 153 | D-SECURITY | D-INTEGRATION | 2 | import_depends |
| 154 | D-SECURITY | D-TRADING | 2 | import_depends |
| 155 | D-SHARED | D-ML_TRAIN | 2 | import_depends |
| 156 | D-SIMULATION | D-INTEGRATION | 2 | import_depends |
| 157 | D-AUDITTEST | D-GOV_DRIFT | 1 | test_depends |
| 158 | D-AUDITTEST | D-OPS | 1 | test_depends |
| 159 | D-AUDITTEST | D-SHARED | 1 | test_depends |
| 160 | D-AUTONOMY_CORE | D-GOV_ENFORCEMENT | 1 | import_depends |
| 161 | D-AUTONOMY_PERM | D-AUTONOMY_CORE | 1 | test_depends |
| 162 | D-AUTONOMY_PERM | D-GOV_AUDIT | 1 | test_depends |
| 163 | D-AUTONOMY_PERM | D-INFRA_RUNTIME | 1 | test_depends |
| 164 | D-BEHAVIORAL_AUDIT | D-SHARED | 1 | import_depends |
| 165 | D-CROSS_ASSET | D-SHARED | 1 | import_depends |
| 166 | D-DATA_SEC | D-GOVERNANCE | 1 | import_depends |
| 167 | D-DATA_SEC | D-OPS | 1 | import_depends |
| 168 | D-FACTOR | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 169 | D-FACTOR | D-SHARED | 1 | import_depends |
| 170 | D-FRONTEND | D-INFRA_OPS | 1 | import_depends |
| 171 | D-FRONTEND | D-SHARED | 1 | import_depends |
| 172 | D-FUNDAMENTAL_SIGNAL | D-GOVERNANCE | 1 | import_depends |
| 173 | D-GOVERNANCE | D-GOV_DOCS | 1 | runtime |
| 174 | D-GOVERNANCE | D-KNOWLEDGE | 1 | contract |
| 175 | D-GOVERNANCE | D-ML_TRAIN | 1 | data |
| 176 | D-GOVERNANCE | D-PF_ALLOC | 1 | import_depends |
| 177 | D-GOV_DRIFT | D-AUTONOMY_PERM | 1 | runtime |
| 178 | D-GOV_DRIFT | D-GOV_ENFORCEMENT | 1 | runtime |
| 179 | D-GOV_DRIFT | D-GOV_SCRIPTS | 1 | import_depends |
| 180 | D-GOV_DRIFT | D-SECURITY | 1 | test_depends |
| 181 | D-GOV_RULE | D-INTEGRATION | 1 | import_depends |
| 182 | D-GOV_RULE | D-SHARED | 1 | import_depends |
| 183 | D-GOV_SCRIPTS | D-EX_CORE | 1 | import_depends |
| 184 | D-GOV_SCRIPTS | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 185 | D-GOV_SCRIPTS | D-INTELLIGENCE | 1 | import_depends |
| 186 | D-GOV_SCRIPTS | D-MKT_DATA | 1 | import_depends |
| 187 | D-GOV_SCRIPTS | D-SIMULATION | 1 | import_depends |
| 188 | D-INFRA_A2A | D-GOV_AUDIT | 1 | import_depends |
| 189 | D-INFRA_A2A | D-INTEGRATION | 1 | import_depends |
| 190 | D-INFRA_OPS | D-INFRA_RUNTIME | 1 | import_depends |
| 191 | D-INFRA_OPS | D-OPS | 1 | import_depends |
| 192 | D-INFRA_OPS | D-SHARED | 1 | import_depends |
| 193 | D-INFRA_RUNTIME | D-OPS | 1 | import_depends |
| 194 | D-INFRA_TELEMETRY | D-BEHAVIORAL_AUDIT | 1 | import_depends |
| 195 | D-INFRA_TELEMETRY | D-GOVERNANCE | 1 | import_depends |
| 196 | D-INFRA_TELEMETRY | D-OPS | 1 | import_depends |
| 197 | D-INTEGRATION | D-OPS | 1 | import_depends |
| 198 | D-INTELLIGENCE | D-AUTONOMY_CORE | 1 | import_depends |
| 199 | D-INTELLIGENCE | D-INFRA_RUNTIME | 1 | import_depends |
| 200 | D-INTELLIGENCE | D-SHARED | 1 | import_depends |
| 201 | D-INTELLIGENCE | D-TRADING | 1 | import_depends |
| 202 | D-KNOWLEDGE | D-AUTONOMY_CORE | 1 | test_depends |
| 203 | D-OPS | D-FACTOR | 1 | runtime |
| 204 | D-OPS | D-GOV_AUDIT | 1 | test_depends |
| 205 | D-OPS | D-GOV_DRIFT | 1 | import_depends |
| 206 | D-PF_ALLOC | D-TRADING | 1 | import_depends |
| 207 | D-PF_CORE | D-REPORTING | 1 | import_depends |
| 208 | D-PF_CORE | D-TRADING | 1 | import_depends |
| 209 | D-POSITION | D-GOVERNANCE | 1 | config_depends |
| 210 | D-RISK | D-GOVERNANCE | 1 | config_depends |
| 211 | D-RISK | D-SHARED | 1 | import_depends |
| 212 | D-SECURITY | D-INTELLIGENCE | 1 | import_depends |
| 213 | D-SHARED | D-GOV_AUDIT | 1 | import_depends |
| 214 | D-SHARED | D-INFRA_A2A | 1 | import_depends |
| 215 | D-SHARED | D-SIMULATION | 1 | import_depends |
| 216 | D-TRADING | D-BEHAVIORAL_AUDIT | 1 | import_depends |
| 217 | D-TRADING | D-GOV_DOCS | 1 | runtime |
