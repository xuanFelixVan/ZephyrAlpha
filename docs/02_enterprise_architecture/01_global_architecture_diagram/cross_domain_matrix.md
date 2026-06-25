---
doc_type: cross_domain_matrix
title: 域间依赖矩阵
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 域间依赖矩阵

> **文档作用 / Purpose**: 以矩阵形式展示所有功能域之间的依赖关系，识别高耦合域和独立域，为架构解耦提供依据。

> 本文档由 generate_cross_domain_matrix.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 18:42:33
> 数据源: depgraph.db edges表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 跨域依赖对数 | 239 |
| 跨域依赖边总数 | 3634 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D-GOVERNANCE | D-OPS | 385 | import_depends,test_depends,config_depends,runtime |
| D-GOVERNANCE | D-INTEGRATION | 237 | import_depends,test_depends,contract,data |
| D-GOVERNANCE | D-TRADING | 226 | import_depends,test_depends |
| D-GOVERNANCE | D-AUTONOMY_CORE | 213 | import_depends,test_depends,contract,runtime |
| D-GOVERNANCE | D-SECURITY | 207 | import_depends,test_depends,contract,runtime |
| D-GOVERNANCE | D-SHARED | 185 | import_depends,test_depends |
| D-GOVERNANCE | D-GOV-ENFORCEMENT | 168 | import_depends,test_depends,runtime |
| D-GOVERNANCE | D-GOV_AUDIT | 140 | import_depends,test_depends,contract,runtime |
| D-AUTONOMY_PERM | D-SECURITY | 138 | import_depends,test_depends,contract |
| D-GOVERNANCE | D-INFRA_RUNTIME | 125 | import_depends,test_depends,config_depends,runtime |
| D-GOVERNANCE | D-BEHAVIORAL_AUDIT | 89 | import_depends,test_depends |
| D-INTEGRATION | D-SHARED | 71 | import_depends,runtime |
| D-TRADING | D-INTEGRATION | 56 | import_depends,event |
| D-SECURITY | D-BEHAVIORAL_AUDIT | 51 | import_depends |
| D-GOVERNANCE | D-INTELLIGENCE | 50 | import_depends,test_depends |
| D-TRADING | D-SHARED | 43 | import_depends,contract |
| D-GOV_AUDIT | D-SHARED | 42 | import_depends,runtime |
| D-INFRA_RUNTIME | D-SHARED | 36 | import_depends |
| D-INFRA_RECOVERY | D-INFRA_RUNTIME | 33 | import_depends |
| D-OPS | D-INFRA_RUNTIME | 33 | import_depends,test_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D-GOVERNANCE | D-OPS | 385 | import_depends,test_depends,config_depends,runtime |
| 2 | D-GOVERNANCE | D-INTEGRATION | 237 | import_depends,test_depends,contract,data |
| 3 | D-GOVERNANCE | D-TRADING | 226 | import_depends,test_depends |
| 4 | D-GOVERNANCE | D-AUTONOMY_CORE | 213 | import_depends,test_depends,contract,runtime |
| 5 | D-GOVERNANCE | D-SECURITY | 207 | import_depends,test_depends,contract,runtime |
| 6 | D-GOVERNANCE | D-SHARED | 185 | import_depends,test_depends |
| 7 | D-GOVERNANCE | D-GOV-ENFORCEMENT | 168 | import_depends,test_depends,runtime |
| 8 | D-GOVERNANCE | D-GOV_AUDIT | 140 | import_depends,test_depends,contract,runtime |
| 9 | D-AUTONOMY_PERM | D-SECURITY | 138 | import_depends,test_depends,contract |
| 10 | D-GOVERNANCE | D-INFRA_RUNTIME | 125 | import_depends,test_depends,config_depends,runtime |
| 11 | D-GOVERNANCE | D-BEHAVIORAL_AUDIT | 89 | import_depends,test_depends |
| 12 | D-INTEGRATION | D-SHARED | 71 | import_depends,runtime |
| 13 | D-TRADING | D-INTEGRATION | 56 | import_depends,event |
| 14 | D-SECURITY | D-BEHAVIORAL_AUDIT | 51 | import_depends |
| 15 | D-GOVERNANCE | D-INTELLIGENCE | 50 | import_depends,test_depends |
| 16 | D-TRADING | D-SHARED | 43 | import_depends,contract |
| 17 | D-GOV_AUDIT | D-SHARED | 42 | import_depends,runtime |
| 18 | D-INFRA_RUNTIME | D-SHARED | 36 | import_depends |
| 19 | D-INFRA_RECOVERY | D-INFRA_RUNTIME | 33 | import_depends |
| 20 | D-OPS | D-INFRA_RUNTIME | 33 | import_depends,test_depends |
| 21 | D-GOV-SCRIPTS | D-GOVERNANCE | 30 | import_depends |
| 22 | D-OPS | D-GOVERNANCE | 29 | import_depends,test_depends,config_depends,contract,runtime |
| 23 | D-TRADING | D-GOVERNANCE | 29 | import_depends,runtime,contract |
| 24 | D-GOV-DOCS | D-GOVERNANCE | 28 | import_depends,runtime |
| 25 | D-AUTONOMY_CORE | D-INTEGRATION | 26 | import_depends,data |
| 26 | D-GOVERNANCE | D-GOV_DRIFT | 26 | import_depends,test_depends,config_depends,runtime,contract,data |
| 27 | D-INFRA_RUNTIME | D-INTEGRATION | 23 | import_depends |
| 28 | D-GOV_AUDIT | D-GOVERNANCE | 21 | import_depends,config_depends,runtime,contract |
| 29 | D-GOV-DOCS | D-SHARED | 20 | import_depends |
| 30 | D-INFRA_A2A | D-SHARED | 18 | import_depends |
| 31 | D-FUNDAMENTAL_SIGNAL | D-TRADING | 17 | import_depends |
| 32 | D-GOVERNANCE | D-MKT_DATA | 16 | test_depends |
| 33 | D-INTEGRATION | D-INTELLIGENCE | 16 | import_depends |
| 34 | D-KNOWLEDGE | D-INTEGRATION | 16 | import_depends,test_depends |
| 35 | D-OPS | D-SHARED | 15 | import_depends,test_depends,runtime |
| 36 | D-GOVERNANCE | D-RISK | 14 | test_depends |
| 37 | D-INFRA_A2A | D-INFRA_RUNTIME | 14 | import_depends |
| 38 | D-GOV-ENFORCEMENT | D-INTEGRATION | 13 | import_depends |
| 39 | D-GOV-SCRIPTS | D-INTEGRATION | 13 | import_depends |
| 40 | D-GOV_AUDIT | D-GOV_DRIFT | 13 | import_depends,runtime |
| 41 | D-KNOWLEDGE | D-GOVERNANCE | 13 | import_depends,test_depends,runtime |
| 42 | D-GOV-DOCS | D-GOV-ENFORCEMENT | 12 | import_depends |
| 43 | D-GOVERNANCE | D-GOV-SCRIPTS | 12 | test_depends |
| 44 | D-GOVERNANCE | D-SIMULATION | 12 | test_depends |
| 45 | D-INFRA_TELEMETRY | D-INFRA_RUNTIME | 12 | import_depends |
| 46 | D-PF_CORE | D-GOVERNANCE | 12 | import_depends,contract |
| 47 | D-TRADING | D-SECURITY | 12 | import_depends |
| 48 | D-COMPLIANCE | D-GOVERNANCE | 11 | import_depends,contract |
| 49 | D-COMPLIANCE | D-GOV_AUDIT | 11 | import_depends |
| 50 | D-GOV-DOCS | D-INTEGRATION | 11 | import_depends |
| 51 | D-GOV-SCRIPTS | D-INFRA_RUNTIME | 11 | import_depends |
| 52 | D-INTEGRATION | D-GOVERNANCE | 11 | import_depends,config_depends |
| 53 | D-REPORTING | D-GOVERNANCE | 11 | import_depends,contract |
| 54 | D-RISK | D-TRADING | 11 | import_depends,contract |
| 55 | D-TRADING | D-GOV_AUDIT | 11 | import_depends,contract |
| 56 | D-EX_CORE | D-GOVERNANCE | 10 | import_depends,config_depends |
| 57 | D-GOV-SCRIPTS | D-GOV-ENFORCEMENT | 10 | import_depends |
| 58 | D-GOV_DRIFT | D-GOVERNANCE | 10 | import_depends,test_depends,config_depends,runtime |
| 59 | D-SHARED | D-INTEGRATION | 10 | import_depends,contract,data |
| 60 | D-INFRA_RUNTIME | D-GOVERNANCE | 9 | import_depends |
| 61 | D-REPORTING | D-TRADING | 9 | import_depends |
| 62 | D-AUTONOMY_CORE | D-SHARED | 8 | import_depends,runtime |
| 63 | D-GOV-ENFORCEMENT | D-SHARED | 8 | import_depends |
| 64 | D-GOVERNANCE | D-FRONTEND | 8 | test_depends |
| 65 | D-GOVERNANCE | D-FUNDAMENTAL_SIGNAL | 8 | test_depends |
| 66 | D-GOVERNANCE | D-GOV_RULE | 8 | import_depends,test_depends,runtime |
| 67 | D-GOV_DRIFT | D-BEHAVIORAL_AUDIT | 8 | test_depends |
| 68 | D-GOV_DRIFT | D-GOV_AUDIT | 8 | import_depends,runtime,data |
| 69 | D-INFRA_OPS | D-GOVERNANCE | 8 | import_depends,test_depends,config_depends |
| 70 | D-OPS | D-INTEGRATION | 8 | import_depends,runtime |
| 71 | D-GOV_AUDIT_TESTS | D-GOV_AUDIT | 7 | test_depends |
| 72 | D-INFRA_RECOVERY | D-GOV_AUDIT | 7 | import_depends |
| 73 | D-INTELLIGENCE | D-GOVERNANCE | 7 | import_depends,config_depends |
| 74 | D-INTELLIGENCE | D-INTEGRATION | 7 | import_depends,data |
| 75 | D-SECURITY | D-SHARED | 7 | import_depends,runtime |
| 76 | D-GOVERNANCE | D-EX_CORE | 6 | test_depends |
| 77 | D-GOVERNANCE | D-INFRA_A2A | 6 | import_depends |
| 78 | D-GOVERNANCE | D-INFRA_OPS | 6 | data,runtime |
| 79 | D-GOVERNANCE | D-PF_CORE | 6 | test_depends |
| 80 | D-GOV_AUDIT | D-SECURITY | 6 | import_depends |
| 81 | D-INFRA_OPS | D-SHARED | 6 | import_depends,runtime |
| 82 | D-OPS | D-AUTONOMY_CORE | 6 | import_depends,test_depends |
| 83 | D-SHARED | D-INFRA_RUNTIME | 6 | import_depends |
| 84 | D-SHARED | D-OPS | 6 | import_depends |
| 85 | D-TRADING | D-GOV-ENFORCEMENT | 6 | import_depends,contract |
| 86 | D-TRADING | D-INTELLIGENCE | 6 | import_depends |
| 87 | D-CROSS_ASSET | D-TRADING | 5 | import_depends,contract |
| 88 | D-FACTOR | D-GOVERNANCE | 5 | import_depends,config_depends |
| 89 | D-GOV-ENFORCEMENT | D-BEHAVIORAL_AUDIT | 5 | import_depends |
| 90 | D-GOV_AUDIT | D-GOV-ENFORCEMENT | 5 | import_depends,runtime |
| 91 | D-GOV_AUDIT | D-INFRA_RUNTIME | 5 | import_depends |
| 92 | D-GOV_AUDIT | D-INTEGRATION | 5 | import_depends |
| 93 | D-INFRA_RECOVERY | D-SHARED | 5 | import_depends |
| 94 | D-INTEGRATION | D-SECURITY | 5 | import_depends,contract |
| 95 | D-OPS | D-SECURITY | 5 | import_depends,test_depends |
| 96 | D-SECURITY | D-GOV-ENFORCEMENT | 5 | import_depends |
| 97 | D-SECURITY | D-GOVERNANCE | 5 | import_depends,data |
| 98 | D-SECURITY | D-GOV_AUDIT | 5 | import_depends |
| 99 | D-AUTONOMY_CORE | D-SECURITY | 4 | import_depends,contract |
| 100 | D-FRONTEND | D-GOVERNANCE | 4 | import_depends |
| 101 | D-GOV-ENFORCEMENT | D-GOV_AUDIT | 4 | import_depends |
| 102 | D-GOVERNANCE | D-AUTONOMY_PERM | 4 | runtime,contract |
| 103 | D-GOVERNANCE | D-FACTOR | 4 | test_depends |
| 104 | D-INFRA_RECOVERY | D-GOVERNANCE | 4 | import_depends |
| 105 | D-INFRA_RUNTIME | D-GOV_AUDIT | 4 | import_depends |
| 106 | D-INTELLIGENCE | D-ML_TRAIN | 4 | import_depends |
| 107 | D-OPS | D-TRADING | 4 | import_depends |
| 108 | D-SECURITY | D-INTEGRATION | 4 | import_depends,data |
| 109 | D-TRADING | D-AUTONOMY_CORE | 4 | import_depends,runtime |
| 110 | D-TRADING | D-INFRA_RUNTIME | 4 | import_depends,contract |
| 111 | D-AUTONOMY_CORE | D-GOV_AUDIT | 3 | import_depends |
| 112 | D-AUTONOMY_PERM | D-GOVERNANCE | 3 | test_depends,config_depends |
| 113 | D-BEHAVIORAL_AUDIT | D-INTEGRATION | 3 | import_depends |
| 114 | D-EX_CORE | D-TRADING | 3 | import_depends |
| 115 | D-FRONTEND | D-OPS | 3 | import_depends,contract |
| 116 | D-GOV-ENFORCEMENT | D-GOVERNANCE | 3 | import_depends |
| 117 | D-GOV-SCRIPTS | D-RISK | 3 | import_depends |
| 118 | D-GOV-SCRIPTS | D-SHARED | 3 | import_depends |
| 119 | D-GOV_AUDIT_TESTS | D-SECURITY | 3 | test_depends |
| 120 | D-INFRA_A2A | D-GOVERNANCE | 3 | import_depends |
| 121 | D-INFRA_TELEMETRY | D-SHARED | 3 | import_depends |
| 122 | D-INTEGRATION | D-GOV-ENFORCEMENT | 3 | import_depends |
| 123 | D-INTELLIGENCE | D-SIMULATION | 3 | import_depends |
| 124 | D-ML_TRAIN | D-TRADING | 3 | import_depends,contract |
| 125 | D-OPS | D-BEHAVIORAL_AUDIT | 3 | import_depends,runtime |
| 126 | D-SHARED | D-GOVERNANCE | 3 | import_depends |
| 127 | D-SIMULATION | D-INTEGRATION | 3 | import_depends,contract |
| 128 | D-TRADING | D-GOV_DRIFT | 3 | import_depends,runtime |
| 129 | D-TRADING | D-OPS | 3 | import_depends,runtime |
| 130 | D-AUTONOMY_CORE | D-GOVERNANCE | 2 | import_depends |
| 131 | D-AUTONOMY_CORE | D-INTELLIGENCE | 2 | import_depends |
| 132 | D-AUTONOMY_PERM | D-INTEGRATION | 2 | test_depends |
| 133 | D-BEHAVIORAL_AUDIT | D-GOVERNANCE | 2 | import_depends |
| 134 | D-BEHAVIORAL_AUDIT | D-GOV_AUDIT | 2 | import_depends |
| 135 | D-COMPLIANCE | D-GOV_DRIFT | 2 | import_depends |
| 136 | D-GOV-DOCS | D-INTELLIGENCE | 2 | import_depends |
| 137 | D-GOV-ENFORCEMENT | D-SECURITY | 2 | import_depends |
| 138 | D-GOV-SCRIPTS | D-GOV_AUDIT | 2 | import_depends |
| 139 | D-GOV-SCRIPTS | D-OPS | 2 | import_depends |
| 140 | D-GOV-SCRIPTS | D-SECURITY | 2 | import_depends |
| 141 | D-GOVERNANCE | D-CROSS_ASSET | 2 | test_depends |
| 142 | D-GOVERNANCE | D-REPORTING | 2 | import_depends |
| 143 | D-GOV_AUDIT | D-BEHAVIORAL_AUDIT | 2 | import_depends |
| 144 | D-GOV_AUDIT | D-OPS | 2 | import_depends |
| 145 | D-GOV_AUDIT | D-TRADING | 2 | import_depends |
| 146 | D-GOV_AUDIT_TESTS | D-GOV-ENFORCEMENT | 2 | test_depends |
| 147 | D-INFRA_OPS | D-GOV_AUDIT | 2 | import_depends |
| 148 | D-INFRA_OPS | D-SECURITY | 2 | runtime,contract |
| 149 | D-INFRA_RECOVERY | D-INTEGRATION | 2 | import_depends |
| 150 | D-INTEGRATION | D-AUTONOMY_CORE | 2 | import_depends |
| 151 | D-INTEGRATION | D-GOV_AUDIT | 2 | import_depends |
| 152 | D-INTEGRATION | D-TRADING | 2 | import_depends |
| 153 | D-INTELLIGENCE | D-GOV-ENFORCEMENT | 2 | import_depends,contract |
| 154 | D-MKT_DATA | D-GOVERNANCE | 2 | config_depends |
| 155 | D-ML_TRAIN | D-SHARED | 2 | import_depends |
| 156 | D-PF_ALLOC | D-GOVERNANCE | 2 | import_depends,config_depends |
| 157 | D-PF_ALLOC | D-SHARED | 2 | import_depends,contract |
| 158 | D-SECURITY | D-TRADING | 2 | import_depends |
| 159 | D-SHARED | D-ML_TRAIN | 2 | import_depends |
| 160 | D-ALT_DATA | D-SHARED | 1 | contract |
| 161 | D-AUTONOMY_CORE | D-GOV-ENFORCEMENT | 1 | import_depends |
| 162 | D-AUTONOMY_PERM | D-AUTONOMY_CORE | 1 | test_depends |
| 163 | D-AUTONOMY_PERM | D-GOV_AUDIT | 1 | test_depends |
| 164 | D-AUTONOMY_PERM | D-INFRA_RUNTIME | 1 | test_depends |
| 165 | D-BEHAVIORAL_AUDIT | D-SHARED | 1 | import_depends |
| 166 | D-CROSS_ASSET | D-SHARED | 1 | import_depends |
| 167 | D-DATA_ENG | D-SHARED | 1 | contract |
| 168 | D-DATA_SEC | D-GOVERNANCE | 1 | import_depends |
| 169 | D-DATA_SEC | D-OPS | 1 | import_depends |
| 170 | D-EX_SOR | D-SHARED | 1 | contract |
| 171 | D-FACTOR | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 172 | D-FACTOR | D-SHARED | 1 | import_depends |
| 173 | D-FACTOR | D-SIGLEGACY | 1 | contract |
| 174 | D-FRONTEND | D-INFRA_OPS | 1 | import_depends |
| 175 | D-FRONTEND | D-SHARED | 1 | import_depends |
| 176 | D-FUNDAMENTAL_SIGNAL | D-GOVERNANCE | 1 | import_depends |
| 177 | D-GOV-SCRIPTS | D-EX_CORE | 1 | import_depends |
| 178 | D-GOV-SCRIPTS | D-FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 179 | D-GOV-SCRIPTS | D-INTELLIGENCE | 1 | import_depends |
| 180 | D-GOV-SCRIPTS | D-MKT_DATA | 1 | import_depends |
| 181 | D-GOV-SCRIPTS | D-SIMULATION | 1 | import_depends |
| 182 | D-GOVERNANCE | D-GOV-DOCS | 1 | runtime |
| 183 | D-GOVERNANCE | D-KNOWLEDGE | 1 | contract |
| 184 | D-GOVERNANCE | D-ML_TRAIN | 1 | data |
| 185 | D-GOVERNANCE | D-PF_ALLOC | 1 | import_depends |
| 186 | D-GOV_AUDIT | D-INFRA_OPS | 1 | data |
| 187 | D-GOV_AUDIT_TESTS | D-GOV_DRIFT | 1 | test_depends |
| 188 | D-GOV_AUDIT_TESTS | D-OPS | 1 | test_depends |
| 189 | D-GOV_AUDIT_TESTS | D-SHARED | 1 | test_depends |
| 190 | D-GOV_DRIFT | D-AUTONOMY_PERM | 1 | runtime |
| 191 | D-GOV_DRIFT | D-GOV-ENFORCEMENT | 1 | runtime |
| 192 | D-GOV_DRIFT | D-GOV-SCRIPTS | 1 | import_depends |
| 193 | D-GOV_DRIFT | D-INFRA_OPS | 1 | data |
| 194 | D-GOV_DRIFT | D-INTEGRATION | 1 | data |
| 195 | D-GOV_DRIFT | D-SECURITY | 1 | test_depends |
| 196 | D-GOV_RULE | D-INTEGRATION | 1 | import_depends |
| 197 | D-GOV_RULE | D-OPS | 1 | contract |
| 198 | D-GOV_RULE | D-SECURITY | 1 | contract |
| 199 | D-GOV_RULE | D-SHARED | 1 | import_depends |
| 200 | D-INFRA_A2A | D-GOV_AUDIT | 1 | import_depends |
| 201 | D-INFRA_A2A | D-INTEGRATION | 1 | import_depends |
| 202 | D-INFRA_OPS | D-INFRA_RUNTIME | 1 | import_depends |
| 203 | D-INFRA_OPS | D-INTEGRATION | 1 | data |
| 204 | D-INFRA_OPS | D-OPS | 1 | import_depends |
| 205 | D-INFRA_RUNTIME | D-OPS | 1 | import_depends |
| 206 | D-INFRA_TELEMETRY | D-BEHAVIORAL_AUDIT | 1 | import_depends |
| 207 | D-INFRA_TELEMETRY | D-GOVERNANCE | 1 | import_depends |
| 208 | D-INFRA_TELEMETRY | D-OPS | 1 | import_depends |
| 209 | D-INTEGRATION | D-GOV_RULE | 1 | runtime |
| 210 | D-INTEGRATION | D-INFRA_OPS | 1 | data |
| 211 | D-INTEGRATION | D-OPS | 1 | import_depends |
| 212 | D-INTELLIGENCE | D-AUTONOMY_CORE | 1 | import_depends |
| 213 | D-INTELLIGENCE | D-INFRA_RUNTIME | 1 | import_depends |
| 214 | D-INTELLIGENCE | D-SECURITY | 1 | runtime |
| 215 | D-INTELLIGENCE | D-SHARED | 1 | import_depends |
| 216 | D-INTELLIGENCE | D-TRADING | 1 | import_depends |
| 217 | D-KNOWLEDGE | D-AUTONOMY_CORE | 1 | test_depends |
| 218 | D-KNOWLEDGE | D-SHARED | 1 | contract |
| 219 | D-ML_SERVE | D-SHARED | 1 | contract |
| 220 | D-OPS | D-GOV_AUDIT | 1 | test_depends |
| 221 | D-OPS | D-GOV_DRIFT | 1 | import_depends |
| 222 | D-OPS | D-INFRA_OPS | 1 | data |
| 223 | D-PF_ALLOC | D-TRADING | 1 | import_depends |
| 224 | D-PF_CORE | D-REPORTING | 1 | import_depends |
| 225 | D-PF_CORE | D-TRADING | 1 | import_depends |
| 226 | D-POSITION | D-GOVERNANCE | 1 | config_depends |
| 227 | D-POSITION | D-SHARED | 1 | contract |
| 228 | D-RISK | D-GOVERNANCE | 1 | config_depends |
| 229 | D-RISK | D-SHARED | 1 | import_depends |
| 230 | D-SECURITY | D-INTELLIGENCE | 1 | import_depends |
| 231 | D-SECURITY | D-OPS | 1 | contract |
| 232 | D-SELL_DECISION | D-SHARED | 1 | contract |
| 233 | D-SHARED | D-GOV_AUDIT | 1 | import_depends |
| 234 | D-SHARED | D-INFRA_A2A | 1 | import_depends |
| 235 | D-SHARED | D-SIMULATION | 1 | import_depends |
| 236 | D-SIGLEGACY | D-GOVERNANCE | 1 | contract |
| 237 | D-TRADING | D-BEHAVIORAL_AUDIT | 1 | import_depends |
| 238 | D-TRADING | D-GOV-DOCS | 1 | runtime |
| 239 | D-TRADING | D-INFRA_OPS | 1 | runtime |
