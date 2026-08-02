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
| 域总数 | 72 |
| 跨域依赖对数 | 287 |
| 跨域依赖边总数 | 2000 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D_INFRA_RUNTIME | D_SHARED | 165 | import_depends |
| D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | 88 | import_depends,test_depends |
| D_GOVERNANCE | D_SHARED | 71 | import_depends,test_depends |
| D_INTEGRATION | D_SHARED | 61 | import_depends |
| D_GOV_AUDIT | D_SHARED | 59 | import_depends,test_depends |
| D_GOV_SCRIPTS | D_GOVERNANCE | 59 | import_depends |
| D_GOVERNANCE | D_GOV_SCRIPTS | 45 | import_depends,test_depends |
| D_SECURITY | D_GOV_DRIFT | 44 | import_depends |
| D_COMPLIANCE | D_GOV_DRIFT | 43 | import_depends |
| D_ORCHESTRATOR | D_SHARED | 42 | import_depends |
| D_SECURITY | D_SHARED | 39 | import_depends |
| D_GOV_SCRIPTS | D_SHARED | 36 | import_depends |
| D_FEEDBACK_LOOP | D_FBL_VERIFICATION | 35 | import_depends |
| D_GOV_DRIFT | D_SHARED | 34 | import_depends |
| D_INFRA_RECOVERY | D_SHARED | 34 | import_depends |
| D_TRADING | D_SHARED | 28 | import_depends,test_depends |
| D_GOV_ENFORCEMENT | D_GOV_AUDIT | 25 | import_depends |
| D_AUTONOMY_CORE | D_SHARED | 25 | import_depends,test_depends |
| D_GOV_ENFORCEMENT | D_SHARED | 22 | import_depends |
| D_FEEDBACK_LOOP | D_SHARED | 22 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D_INFRA_RUNTIME | D_SHARED | 165 | import_depends |
| 2 | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | 88 | import_depends,test_depends |
| 3 | D_GOVERNANCE | D_SHARED | 71 | import_depends,test_depends |
| 4 | D_INTEGRATION | D_SHARED | 61 | import_depends |
| 5 | D_GOV_AUDIT | D_SHARED | 59 | import_depends,test_depends |
| 6 | D_GOV_SCRIPTS | D_GOVERNANCE | 59 | import_depends |
| 7 | D_GOVERNANCE | D_GOV_SCRIPTS | 45 | import_depends,test_depends |
| 8 | D_SECURITY | D_GOV_DRIFT | 44 | import_depends |
| 9 | D_COMPLIANCE | D_GOV_DRIFT | 43 | import_depends |
| 10 | D_ORCHESTRATOR | D_SHARED | 42 | import_depends |
| 11 | D_SECURITY | D_SHARED | 39 | import_depends |
| 12 | D_GOV_SCRIPTS | D_SHARED | 36 | import_depends |
| 13 | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | 35 | import_depends |
| 14 | D_GOV_DRIFT | D_SHARED | 34 | import_depends |
| 15 | D_INFRA_RECOVERY | D_SHARED | 34 | import_depends |
| 16 | D_TRADING | D_SHARED | 28 | import_depends,test_depends |
| 17 | D_GOV_ENFORCEMENT | D_GOV_AUDIT | 25 | import_depends |
| 18 | D_AUTONOMY_CORE | D_SHARED | 25 | import_depends,test_depends |
| 19 | D_GOV_ENFORCEMENT | D_SHARED | 22 | import_depends |
| 20 | D_FEEDBACK_LOOP | D_SHARED | 22 | import_depends |
| 21 | D_AUTONOMY_CORE | D_INFRA_RUNTIME | 22 | import_depends,test_depends |
| 22 | D_GOV_RULE | D_SHARED | 22 | import_depends |
| 23 | D_GOV_CODE_QUALITY | D_SHARED | 20 | import_depends |
| 24 | D_TRADING | D_INFRASTRUCTURE | 20 | import_depends,test_depends |
| 25 | D_INTELLIGENCE | D_SHARED | 19 | import_depends |
| 26 | D_DATA | D_SHARED | 19 | import_depends |
| 27 | D_EX_SOR | D_SHARED | 16 | import_depends |
| 28 | D_REPORTING | D_SHARED | 16 | import_depends,test_depends |
| 29 | D_EX_CORE | D_INFRASTRUCTURE | 16 | import_depends,test_depends |
| 30 | D_GOV_SCRIPTS | D_INTEGRATION | 14 | import_depends |
| 31 | D_GOV_OPS_RESILIENCE | D_SHARED | 13 | import_depends |
| 32 | D_INTEGRATION | D_INFRA_RUNTIME | 13 | import_depends |
| 33 | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | 12 | import_depends |
| 34 | D_POSITION | D_SHARED | 12 | import_depends |
| 35 | D_GOV_AUDIT | D_GOVERNANCE | 12 | import_depends |
| 36 | D_DATA_ENG | D_DATA | 12 | import |
| 37 | D_INFRA_RUNTIME | D_GOVERNANCE | 12 | import_depends |
| 38 | D_RISK | D_SHARED | 11 | import_depends |
| 39 | D_EX_CORE | D_TRADING | 11 | contract,import_depends |
| 40 | D_EX_CORE | D_GOVERNANCE | 10 | contract,import_depends |
| 41 | D_INFRASTRUCTURE | D_SHARED | 10 | import_depends |
| 42 | D_REPORTING | D_INFRASTRUCTURE | 10 | import_depends,test_depends |
| 43 | D_PF_CORE | D_BACKTEST | 10 | import_depends,test_depends |
| 44 | D_PF_CORE | D_INFRASTRUCTURE | 9 | contract,import_depends |
| 45 | D_GOVERNANCE | D_INTELLIGENCE | 9 | import_depends |
| 46 | D_GOVERNANCE | D_INFRA_RUNTIME | 9 | import_depends,test_depends |
| 47 | D_GOVERNANCE | D_GOV_ENFORCEMENT | 9 | import_depends,test_depends |
| 48 | D_BACKTEST | D_SHARED | 9 | import_depends |
| 49 | D_GOV_OPS_RESILIENCE | D_INTEGRATION | 9 | import_depends |
| 50 | D_INFRA_A2A | D_SHARED | 9 | import_depends |
| 51 | D_FUNDAMENTAL_SIGNAL | D_INFRASTRUCTURE | 9 | import_depends |
| 52 | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | 8 | import_depends |
| 53 | D_GOV_CODE_QUALITY | D_GOVERNANCE | 8 | import_depends,test_depends |
| 54 | D_GOV_AUDIT | D_GOV_ENFORCEMENT | 8 | import_depends,test_depends |
| 55 | D_INFRA_RUNTIME | D_INTEGRATION | 8 | import_depends |
| 56 | D_EX_SOR | D_INFRASTRUCTURE | 7 | import_depends |
| 57 | D_EX_CORE | D_SHARED | 7 | import_depends,test_depends |
| 58 | D_GOV_SCRIPTS | D_INFRA_RUNTIME | 7 | import_depends |
| 59 | D_GOV_DRIFT | D_GOV_AUDIT | 7 | import_depends |
| 60 | D_GOV_OPS_RESILIENCE | D_OPS | 7 | import_depends |
| 61 | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | 7 | import_depends |
| 62 | D_MKT_DATA | D_SHARED | 7 | import_depends |
| 63 | D_GOV_AUDIT | D_GOV_SCRIPTS | 7 | import_depends |
| 64 | D_GOV_DRIFT | D_GOV_SCRIPTS | 7 | import_depends |
| 65 | D_GOV_DRIFT | D_GOVERNANCE | 7 | import_depends |
| 66 | D_FEEDBACK_LOOP | D_FBL_DETECTORS | 6 | import_depends |
| 67 | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | 6 | import_depends,test_depends |
| 68 | D_GOV_ENFORCEMENT | D_SECURITY | 6 | import_depends,test_depends |
| 69 | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | 6 | import_depends |
| 70 | D_TRADING | D_INFRA_RUNTIME | 6 | import_depends |
| 71 | D_PF_CORE | D_RISK | 6 | contract,import_depends |
| 72 | D_INTEGRATION | D_INTELLIGENCE | 6 | import_depends |
| 73 | D_GOVERNANCE | D_INFRASTRUCTURE | 6 | import_depends |
| 74 | D_GOVERNANCE | D_INFRA_A2A | 6 | import_depends |
| 75 | D_GOVERNANCE | D_SECURITY | 6 | import_depends,test_depends |
| 76 | D_GOV_AUDIT | D_GOV_CODE_QUALITY | 6 | import_depends |
| 77 | D_GOV_AUDIT | D_GOV_DRIFT | 6 | import_depends |
| 78 | D_GOV_SCRIPTS | D_GOV_RULE | 6 | import_depends |
| 79 | D_SIMULATION | D_SHARED | 5 | import_depends |
| 80 | D_INFRA_RUNTIME | D_SECURITY | 5 | import_depends |
| 81 | D_FUNDAMENTAL_SIGNAL | D_TRADING | 5 | import_depends |
| 82 | D_COMPLIANCE | D_SECURITY | 5 | import_depends |
| 83 | D_INFRA_RUNTIME | D_DATA | 5 | import_depends,test_depends |
| 84 | D_MKT_DATA | D_INFRASTRUCTURE | 5 | import_depends,test_depends |
| 85 | D_GOV_AUDIT | D_SECURITY | 5 | import_depends |
| 86 | D_PF_CORE | D_SHARED | 5 | import_depends |
| 87 | D_SECURITY | D_GOV_AUDIT | 5 | import_depends |
| 88 | D_GOV_SCRIPTS | D_DATA | 5 | import_depends |
| 89 | D_GOVERNANCE | D_INTEGRATION | 5 | import_depends |
| 90 | D_GOV_OPS_RESILIENCE | D_SECURITY | 4 | import_depends |
| 91 | D_INTELLIGENCE | D_ML_TRAIN | 4 | import_depends |
| 92 | D_MKT_DATA | D_DATA | 4 | import_depends,runtime |
| 93 | D_GOVERNANCE | D_OPS | 4 | import_depends |
| 94 | D_INFRA_RECOVERY | D_GOV_AUDIT | 4 | import_depends |
| 95 | D_GOV_RULE | D_GOV_SCRIPTS | 4 | import_depends |
| 96 | D_OPS | D_SHARED | 4 | import_depends |
| 97 | D_PF_ALLOC | D_SHARED | 4 | import_depends |
| 98 | D_FEEDBACK_LOOP | D_GOVERNANCE | 4 | import_depends |
| 99 | D_GOVERNANCE | D_GOV_RULE | 4 | import_depends |
| 100 | D_EX_CORE | D_SELL_DECISION | 4 | runtime |
| 101 | D_GOVERNANCE | D_GOV_AUDIT | 4 | import_depends |
| 102 | D_INFRA_RUNTIME | D_GOV_RULE | 4 | import_depends |
| 103 | D_GOV_SCRIPTS | D_GOV_AUDIT | 4 | import_depends |
| 104 | D_SHARED | D_INFRA_RUNTIME | 4 | import_depends |
| 105 | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | 4 | import_depends |
| 106 | D_TRADING | D_GOVERNANCE | 4 | import_depends |
| 107 | D_AUTONOMY_CORE | D_INTEGRATION | 4 | import_depends |
| 108 | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | 4 | import_depends |
| 109 | D_SECURITY | D_GOV_RULE | 4 | import_depends |
| 110 | D_INTEGRATION | D_GOVERNANCE | 4 | import_depends |
| 111 | D_ML_TRAIN | D_SHARED | 3 | import_depends |
| 112 | D_AUTONOMY_CORE | D_GOV_AUDIT | 3 | import_depends |
| 113 | D_AUTONOMY_PERM | D_GOV_SCRIPTS | 3 | import_depends |
| 114 | D_BACKTEST | D_DATA | 3 | import_depends |
| 115 | D_DATA | D_GOV_ENFORCEMENT | 3 | import_depends,test_depends |
| 116 | D_EX_CORE | D_BACKTEST | 3 | import_depends |
| 117 | D_EX_CORE | D_FACTOR | 3 | import_depends |
| 118 | D_FACTOR | D_DATA | 3 | import_depends |
| 119 | D_FBL_DETECTORS | D_FEEDBACK_LOOP | 3 | import_depends |
| 120 | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | 3 | import_depends |
| 121 | D_GOVERNANCE | D_DATA | 3 | import_depends |
| 122 | D_GOVERNANCE | D_GOV_CODE_QUALITY | 3 | import_depends |
| 123 | D_GOVERNANCE | D_GOV_DRIFT | 3 | import_depends |
| 124 | D_GOVERNANCE | D_INFRA_RECOVERY | 3 | import_depends |
| 125 | D_GOV_AUDIT | D_GOV_RULE | 3 | import_depends,test_depends |
| 126 | D_GOV_CODE_QUALITY | D_DATA | 3 | import_depends,test_depends |
| 127 | D_GOV_DRIFT | D_SECURITY | 3 | import_depends |
| 128 | D_GOV_ENFORCEMENT | D_GOVERNANCE | 3 | import_depends |
| 129 | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | 3 | import_depends |
| 130 | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | 3 | import_depends |
| 131 | D_GOV_REPAIR | D_OPS | 3 | import_depends |
| 132 | D_GOV_RULE | D_GOVERNANCE | 3 | import_depends |
| 133 | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | 3 | import_depends |
| 134 | D_INFRA_RUNTIME | D_GOV_AUDIT | 3 | import_depends |
| 135 | D_INFRA_RUNTIME | D_GOV_DRIFT | 3 | import_depends |
| 136 | D_INFRA_RUNTIME | D_INFRA_A2A | 3 | import_depends |
| 137 | D_INFRA_RUNTIME | D_INTELLIGENCE | 3 | import_depends |
| 138 | D_INFRA_RUNTIME | D_TRADING | 3 | import_depends |
| 139 | D_INTEGRATION | D_AUTONOMY_CORE | 3 | import_depends |
| 140 | D_INTEGRATION | D_GOV_AUDIT | 3 | import_depends |
| 141 | D_INTEGRATION | D_OPS | 3 | import_depends |
| 142 | D_INTEGRATION | D_SECURITY | 3 | import_depends |
| 143 | D_ORCHESTRATOR | D_GOVERNANCE | 3 | import_depends |
| 144 | D_PF_CORE | D_FACTOR | 3 | import_depends |
| 145 | D_PF_CORE | D_GOVERNANCE | 3 | import_depends |
| 146 | D_PF_CORE | D_PF_ALLOC | 3 | import_depends |
| 147 | D_PF_CORE | D_POSITION | 3 | import_depends |
| 148 | D_RISK | D_TRADING | 3 | import_depends |
| 149 | D_SECURITY | D_INFRA_RUNTIME | 3 | import_depends |
| 150 | D_TRADING | D_ORCHESTRATOR | 3 | import_depends |
| 151 | D_FACTOR | D_SHARED | 2 | import_depends |
| 152 | D_POSITION | D_INFRASTRUCTURE | 2 | import_depends,test_depends |
| 153 | D_FEEDBACK_LOOP | D_INTEGRATION | 2 | import_depends |
| 154 | D_FACTOR | D_INFRASTRUCTURE | 2 | import_depends |
| 155 | D_REPORTING | D_EX_CORE | 2 | import_depends,test_depends |
| 156 | D_GOVERNANCE | D_RISK | 2 | import_depends |
| 157 | D_GOV_SCRIPTS | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 158 | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | 2 | test_depends |
| 159 | D_RISK | D_INFRASTRUCTURE | 2 | import_depends |
| 160 | D_ML_TRAIN | D_TRADING | 2 | import_depends |
| 161 | D_INTEGRATION | D_GOV_RULE | 2 | import_depends |
| 162 | D_OPS | D_GOV_DRIFT | 2 | import_depends |
| 163 | D_OPS | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 164 | D_OPS | D_GOV_SCRIPTS | 2 | import_depends |
| 165 | D_INFRA_RUNTIME | D_AUTONOMY_CORE | 2 | import_depends |
| 166 | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 167 | D_ORCHESTRATOR | D_AUTONOMY_CORE | 2 | import_depends |
| 168 | D_GOV_CODE_QUALITY | D_GOV_AUDIT | 2 | import_depends |
| 169 | D_SECURITY | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 170 | D_BACKTEST | D_EX_CORE | 2 | import_depends |
| 171 | D_GOV_SCRIPTS | D_GOV_CODE_QUALITY | 2 | import_depends |
| 172 | D_TRADING | D_EX_CORE | 2 | import,runtime |
| 173 | D_ORCHESTRATOR | D_INFRA_RUNTIME | 2 | import_depends |
| 174 | D_GOV_OPS_RESILIENCE | D_GOV_RULE | 2 | import_depends |
| 175 | D_GOV_ENFORCEMENT | D_OPS | 2 | import_depends |
| 176 | D_FRONTEND | D_SHARED | 2 | import_depends |
| 177 | D_ORCHESTRATOR | D_SECURITY | 2 | import_depends |
| 178 | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 179 | D_GOV_CODE_QUALITY | D_SECURITY | 2 | import_depends |
| 180 | D_PF_ALLOC | D_INFRASTRUCTURE | 2 | import_depends |
| 181 | D_FEEDBACK_LOOP | D_GOV_DRIFT | 2 | import_depends |
| 182 | D_GOV_ENFORCEMENT | D_GOV_SCRIPTS | 2 | import_depends |
| 183 | D_INTELLIGENCE | D_GOV_RULE | 2 | import_depends |
| 184 | D_GOV_AUDIT | D_REPORTING | 2 | import_depends |
| 185 | D_INTELLIGENCE | D_INTEGRATION | 2 | import_depends |
| 186 | D_FRONTEND | D_GOVERNANCE | 2 | import_depends |
| 187 | D_SELL_DECISION | D_SHARED | 2 | import_depends |
| 188 | D_GOV_RULE | D_GOV_AUDIT | 2 | import_depends |
| 189 | D_GOV_RULE | D_GOV_DRIFT | 2 | import_depends |
| 190 | D_GOV_DOCS | D_GOV_SCRIPTS | 2 | test_depends |
| 191 | D_FUNDAMENTAL_SIGNAL | D_SHARED | 2 | import_depends |
| 192 | D_GOV_CODE_QUALITY | D_GOV_SCRIPTS | 2 | import_depends |
| 193 | D_INFRA_RECOVERY | D_SECURITY | 2 | import_depends |
| 194 | D_FEEDBACK_LOOP | D_SECURITY | 1 | import_depends |
| 195 | D_FEEDBACK_LOOP | D_ORCHESTRATOR | 1 | import_depends |
| 196 | D_ML_TRAIN | D_DATA | 1 | data |
| 197 | D_ML_TRAIN | D_ORCHESTRATOR | 1 | runtime |
| 198 | D_OPS | D_GOVERNANCE | 1 | import_depends |
| 199 | D_OPS | D_INFRA_RECOVERY | 1 | import_depends |
| 200 | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | 1 | import_depends |
| 201 | D_ORCHESTRATOR | D_FEEDBACK_LOOP | 1 | import_depends |
| 202 | D_ORCHESTRATOR | D_GOV_DRIFT | 1 | import_depends |
| 203 | D_ORCHESTRATOR | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 204 | D_ORCHESTRATOR | D_INTEGRATION | 1 | import_depends |
| 205 | D_PF_ALLOC | D_GOVERNANCE | 1 | import_depends |
| 206 | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | 1 | import_depends |
| 207 | D_TRADING | D_GOV_AUDIT | 1 | import_depends |
| 208 | D_AUTONOMY_CORE | D_SECURITY | 1 | import_depends |
| 209 | D_FBL_VERIFICATION | D_GOV_AUDIT | 1 | import_depends |
| 210 | D_AUTONOMY_CORE | D_ORCHESTRATOR | 1 | import_depends |
| 211 | D_TRADING | D_INTEGRATION | 1 | import_depends |
| 212 | D_PF_CORE | D_REPORTING | 1 | import_depends |
| 213 | D_FBL_DIAGNOSERS | D_SHARED | 1 | import_depends |
| 214 | D_POSITION | D_RISK | 1 | runtime |
| 215 | D_FACTOR | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 216 | D_EX_SOR | D_EX_CORE | 1 | import_depends |
| 217 | D_REPORTING | D_TRADING | 1 | import_depends |
| 218 | D_RISK | D_POSITION | 1 | runtime |
| 219 | D_RISK | D_SECURITY | 1 | import_depends |
| 220 | D_EX_CORE | D_RISK | 1 | runtime |
| 221 | D_AUTONOMY_CORE | D_GOV_RULE | 1 | import_depends |
| 222 | D_SECURITY | D_AUTONOMY_CORE | 1 | import_depends |
| 223 | D_SECURITY | D_FEEDBACK_LOOP | 1 | import_depends |
| 224 | D_SECURITY | D_GOVERNANCE | 1 | import_depends |
| 225 | D_EX_CORE | D_REPORTING | 1 | data |
| 226 | D_EX_CORE | D_PF_CORE | 1 | import_depends |
| 227 | D_COMPLIANCE | D_INFRA_RUNTIME | 1 | import_depends |
| 228 | D_TRADING | D_POSITION | 1 | import_depends |
| 229 | D_GOV_OPS_RESILIENCE | D_FACTOR | 1 | import_depends |
| 230 | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 231 | D_SECURITY | D_INTELLIGENCE | 1 | import_depends |
| 232 | D_GOV_OPS_RESILIENCE | D_INFRA_RUNTIME | 1 | import_depends |
| 233 | D_GOV_ENFORCEMENT | D_INTEGRATION | 1 | import_depends |
| 234 | D_GOV_OPS_RESILIENCE | D_INTELLIGENCE | 1 | import_depends |
| 235 | D_GOV_ENFORCEMENT | D_INFRA_RUNTIME | 1 | import_depends |
| 236 | D_GOV_ENFORCEMENT | D_INFRASTRUCTURE | 1 | import_depends |
| 237 | D_GOV_REPAIR | D_AUTONOMY_CORE | 1 | import_depends |
| 238 | D_GOV_REPAIR | D_GOVERNANCE | 1 | import_depends |
| 239 | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | 1 | runtime |
| 240 | D_SELL_DECISION | D_POSITION | 1 | runtime |
| 241 | D_GOV_RULE | D_GOV_ENFORCEMENT | 1 | config_depends |
| 242 | D_GOV_ENFORCEMENT | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 243 | D_GOV_RULE | D_INFRA_RECOVERY | 1 | import_depends |
| 244 | D_GOV_DRIFT | D_INTEGRATION | 1 | import_depends |
| 245 | D_GOV_RULE | D_INFRA_RUNTIME | 1 | import_depends |
| 246 | D_GOV_DRIFT | D_INFRA_RECOVERY | 1 | import_depends |
| 247 | D_GOV_DRIFT | D_GOV_ENFORCEMENT | 1 | import_depends |
| 248 | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | 1 | import_depends |
| 249 | D_GOV_SCRIPTS | D_GOV_REPAIR | 1 | import_depends |
| 250 | D_GOV_CODE_QUALITY | D_INFRA_RUNTIME | 1 | import_depends |
| 251 | D_GOV_CODE_QUALITY | D_INFRASTRUCTURE | 1 | import_depends |
| 252 | D_GOV_SCRIPTS | D_INTELLIGENCE | 1 | import_depends |
| 253 | D_GOV_SCRIPTS | D_ORCHESTRATOR | 1 | import_depends |
| 254 | D_GOV_SCRIPTS | D_SECURITY | 1 | import_depends |
| 255 | D_INFRASTRUCTURE | D_GOV_AUDIT | 1 | import_depends |
| 256 | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 257 | D_GOV_CODE_QUALITY | D_AUTONOMY_CORE | 1 | import_depends |
| 258 | D_INFRA_RECOVERY | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 259 | D_INFRA_RECOVERY | D_INFRA_RUNTIME | 1 | import_depends |
| 260 | D_GOV_AUDIT | D_INFRA_RUNTIME | 1 | import_depends |
| 261 | D_INFRA_RUNTIME | D_FACTOR | 1 | import |
| 262 | D_SHARED | D_FEEDBACK_LOOP | 1 | import_depends |
| 263 | D_GOV_AUDIT | D_FEEDBACK_LOOP | 1 | import_depends |
| 264 | D_SHARED | D_GOV_RULE | 1 | import_depends |
| 265 | D_SHARED | D_INFRASTRUCTURE | 1 | import_depends |
| 266 | D_GOVERNANCE | D_TRADING | 1 | import_depends |
| 267 | D_INFRA_RUNTIME | D_GOV_REPAIR | 1 | import_depends |
| 268 | D_INFRA_RUNTIME | D_INFRASTRUCTURE | 1 | import_depends |
| 269 | D_BACKTEST | D_INFRA_RUNTIME | 1 | import_depends |
| 270 | D_INFRA_RUNTIME | D_INFRA_RECOVERY | 1 | import_depends |
| 271 | D_GOVERNANCE | D_REPORTING | 1 | import_depends |
| 272 | D_SHARED | D_ML_TRAIN | 1 | import_depends |
| 273 | D_INFRA_RUNTIME | D_OPS | 1 | import_depends |
| 274 | D_INFRA_RUNTIME | D_ORCHESTRATOR | 1 | import_depends |
| 275 | D_GOVERNANCE | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 276 | D_SIGQC | D_INFRASTRUCTURE | 1 | import_depends |
| 277 | D_SIGQC | D_TRADING | 1 | import_depends |
| 278 | D_FUNDAMENTAL_SIGNAL | D_FACTOR | 1 | import_depends |
| 279 | D_SIMULATION | D_INFRASTRUCTURE | 1 | import_depends |
| 280 | D_INTEGRATION | D_INFRA_RECOVERY | 1 | import_depends |
| 281 | D_FUNDAMENTAL_SIGNAL | D_ASHARE_SIGNAL | 1 | event |
| 282 | D_FRONTEND | D_TRADING | 1 | import_depends |
| 283 | D_BACKTEST | D_GOVERNANCE | 1 | import_depends |
| 284 | D_INTEGRATION | D_TRADING | 1 | import_depends |
| 285 | D_INTELLIGENCE | D_INFRA_RUNTIME | 1 | import_depends |
| 286 | D_FRONTEND | D_FEEDBACK_LOOP | 1 | import_depends |
| 287 | D_INTELLIGENCE | D_TRADING | 1 | import_depends |
