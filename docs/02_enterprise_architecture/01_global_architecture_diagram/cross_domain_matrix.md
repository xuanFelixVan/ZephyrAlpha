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
| 域总数 | 63 |
| 跨域依赖对数 | 467 |
| 跨域依赖边总数 | 3939 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D_INFRA_RUNTIME | D_SHARED | 189 | config_depends,import_depends,test_depends |
| D_GOV_SCRIPTS | D_GOVERNANCE | 164 | config_depends,import_depends,test_depends |
| D_AUTONOMY_PERM | D_SECURITY | 118 | test_depends |
| D_GOV_SCRIPTS | D_GOV_RULE | 102 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_CODE_QUALITY | 90 | import_depends,test_depends |
| D_GOVERNANCE | D_SHARED | 84 | import_depends,runtime,test_depends |
| D_GOV_SCRIPTS | D_SHARED | 79 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_OPS_RESILIENCE | 66 | import_depends,test_depends |
| D_AUTONOMY_CORE | D_FBL_VERIFICATION | 66 | test_depends |
| D_AUTONOMY_CORE | D_FEEDBACK_LOOP | 65 | runtime,test_depends |
| D_INTEGRATION | D_SHARED | 65 | import_depends |
| D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | 58 | import_depends,runtime,test_depends |
| D_GOV_AUDIT | D_GOV_DRIFT | 58 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_ENFORCEMENT | 53 | contract,data,import_depends,test_depends |
| D_GOV_AUDIT | D_SHARED | 50 | import_depends,test_depends |
| D_INFRASTRUCTURE | D_SHARED | 50 | config_depends,import_depends,test_depends |
| D_AUTONOMY_CORE | D_INFRA_RUNTIME | 48 | import_depends,test_depends |
| D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | 48 | import_depends,test_depends |
| D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | 46 | import_depends |
| D_COMPLIANCE | D_GOV_DRIFT | 45 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D_INFRA_RUNTIME | D_SHARED | 189 | config_depends,import_depends,test_depends |
| 2 | D_GOV_SCRIPTS | D_GOVERNANCE | 164 | config_depends,import_depends,test_depends |
| 3 | D_AUTONOMY_PERM | D_SECURITY | 118 | test_depends |
| 4 | D_GOV_SCRIPTS | D_GOV_RULE | 102 | import_depends,test_depends |
| 5 | D_GOVERNANCE | D_GOV_CODE_QUALITY | 90 | import_depends,test_depends |
| 6 | D_GOVERNANCE | D_SHARED | 84 | import_depends,runtime,test_depends |
| 7 | D_GOV_SCRIPTS | D_SHARED | 79 | import_depends,test_depends |
| 8 | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | 66 | import_depends,test_depends |
| 9 | D_AUTONOMY_CORE | D_FBL_VERIFICATION | 66 | test_depends |
| 10 | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | 65 | runtime,test_depends |
| 11 | D_INTEGRATION | D_SHARED | 65 | import_depends |
| 12 | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | 58 | import_depends,runtime,test_depends |
| 13 | D_GOV_AUDIT | D_GOV_DRIFT | 58 | import_depends,test_depends |
| 14 | D_GOVERNANCE | D_GOV_ENFORCEMENT | 53 | contract,data,import_depends,test_depends |
| 15 | D_GOV_AUDIT | D_SHARED | 50 | import_depends,test_depends |
| 16 | D_INFRASTRUCTURE | D_SHARED | 50 | config_depends,import_depends,test_depends |
| 17 | D_AUTONOMY_CORE | D_INFRA_RUNTIME | 48 | import_depends,test_depends |
| 18 | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | 48 | import_depends,test_depends |
| 19 | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | 46 | import_depends |
| 20 | D_COMPLIANCE | D_GOV_DRIFT | 45 | import_depends |
| 21 | D_GOVERNANCE | D_GOV_AUDIT | 45 | config_depends,import_depends,test_depends |
| 22 | D_GOV_REPAIR | D_GOVERNANCE | 44 | config_depends,import_depends |
| 23 | D_SECURITY | D_GOV_DRIFT | 44 | import_depends |
| 24 | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | 44 | import_depends,runtime,test_depends |
| 25 | D_SECURITY_LLM | D_SECURITY | 41 | config_depends,import_depends,test_depends |
| 26 | D_SECURITY | D_FBL_VERIFICATION | 36 | test_depends |
| 27 | D_TRADING | D_INFRA_RUNTIME | 36 | import_depends,test_depends |
| 28 | D_AUTONOMY_CORE | D_INTEGRATION | 35 | import_depends,test_depends |
| 29 | D_FEEDBACK_LOOP | D_FBL_DETECTORS | 34 | import_depends,runtime,test_depends |
| 30 | D_ORCHESTRATOR | D_SHARED | 34 | import_depends,test_depends |
| 31 | D_SECURITY | D_SHARED | 29 | import_depends,test_depends |
| 32 | D_TRADING | D_ORCHESTRATOR | 29 | import_depends,test_depends |
| 33 | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | 28 | import_depends,test_depends |
| 34 | D_AUTONOMY_CORE | D_SHARED | 26 | import_depends,test_depends |
| 35 | D_SHARED | D_INFRA_RUNTIME | 25 | config_depends,import_depends,test_depends |
| 36 | D_DATA | D_SHARED | 25 | import_depends,test_depends |
| 37 | D_GOV_AUDIT | D_FBL_DIAGNOSERS | 24 | test_depends |
| 38 | D_GOVERNANCE | D_INFRA_RUNTIME | 23 | config_depends,import_depends,runtime,test_depends |
| 39 | D_GOV_REPAIR | D_GOV_AUDIT | 23 | import_depends |
| 40 | D_GOV_DRIFT | D_SHARED | 22 | import_depends |
| 41 | D_GOVERNANCE | D_INFRA_RECOVERY | 22 | import_depends,test_depends |
| 42 | D_SHARED | D_GOVERNANCE | 21 | test_depends |
| 43 | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | 21 | import_depends |
| 44 | D_GOV_AUDIT | D_GOVERNANCE | 20 | import_depends,test_depends |
| 45 | D_GOVERNANCE | D_AUTONOMY_CORE | 20 | runtime,test_depends |
| 46 | D_SECURITY_LLM | D_SHARED | 20 | test_depends |
| 47 | D_GOVERNANCE | D_GOV_RULE | 19 | import_depends,test_depends |
| 48 | D_SECURITY_LLM | D_INFRA_RUNTIME | 19 | test_depends |
| 49 | D_INTELLIGENCE | D_SHARED | 19 | import_depends,test_depends |
| 50 | D_TRADING | D_SHARED | 18 | import_depends,test_depends |
| 51 | D_GOV_KB | D_SHARED | 18 | import_depends |
| 52 | D_GOV_ENFORCEMENT | D_GOV_RULE | 18 | import_depends,test_depends |
| 53 | D_INFRA_RECOVERY | D_SHARED | 18 | import_depends |
| 54 | D_INFRA_RUNTIME | D_GOVERNANCE | 18 | import_depends,test_depends |
| 55 | D_INFRA_RUNTIME | D_INTEGRATION | 18 | import_depends |
| 56 | D_GOVERNANCE | D_INTEGRATION | 18 | import_depends,test_depends |
| 57 | D_FEEDBACK_LOOP | D_SHARED | 17 | import_depends |
| 58 | D_GOV_ENFORCEMENT | D_SHARED | 17 | import_depends,test_depends |
| 59 | D_KNOWLEDGE | D_GOV_KB | 16 | test_depends |
| 60 | D_GOVERNANCE | D_SECURITY | 15 | import_depends,test_depends |
| 61 | D_FRONTEND | D_FEEDBACK_LOOP | 15 | import_depends,test_depends |
| 62 | D_INFRA_RUNTIME | D_INFRA_A2A | 15 | import_depends,test_depends |
| 63 | D_GOV_AUDIT | D_FEEDBACK_LOOP | 15 | import_depends,test_depends |
| 64 | D_GOV_ENFORCEMENT | D_FBL_VERIFICATION | 14 | test_depends |
| 65 | D_GOV_RULE | D_SHARED | 14 | import_depends |
| 66 | D_GOVERNANCE | D_INTELLIGENCE | 14 | import_depends,test_depends |
| 67 | D_GOVERNANCE | D_OPS | 14 | import_depends,test_depends |
| 68 | D_GOVERNANCE | D_INFRA_A2A | 14 | config_depends,import_depends,runtime |
| 69 | D_GOVERNANCE | D_INFRASTRUCTURE | 14 | config_depends,import_depends |
| 70 | D_INTEGRATION | D_INFRA_RUNTIME | 14 | import_depends |
| 71 | D_GOVERNANCE | D_GOV_DRIFT | 14 | contract,import_depends,runtime,test_depends |
| 72 | D_DATA | D_GOVERNANCE | 14 | config_depends,test_depends |
| 73 | D_AUDITTEST | D_BACKTEST | 13 | test_depends |
| 74 | D_GOV_AUDIT | D_SECURITY | 13 | import_depends,test_depends |
| 75 | D_INTEGRATION_GATEWAY | D_INTEGRATION | 13 | import_depends |
| 76 | D_INTELLIGENCE | D_INFRA_RUNTIME | 13 | import_depends,test_depends |
| 77 | D_INTELLIGENCE | D_OPS | 13 | test_depends |
| 78 | D_SHARED | D_GOV_OPS_RESILIENCE | 13 | test_depends |
| 79 | D_GOV_OPS_RESILIENCE | D_SHARED | 12 | import_depends |
| 80 | D_SHARED | D_INFRASTRUCTURE | 12 | config_depends,import_depends |
| 81 | D_AUTONOMY_CORE | D_FBL_DIAGNOSERS | 12 | test_depends |
| 82 | D_AUTONOMY_CORE | D_GOV_OPS_RESILIENCE | 12 | test_depends |
| 83 | D_SECURITY_LLM | D_FEEDBACK_LOOP | 12 | test_depends |
| 84 | D_AUTONOMY_CORE | D_GOVERNANCE | 12 | data,runtime,test_depends |
| 85 | D_GOV_REPAIR | D_INFRA_RUNTIME | 11 | import_depends |
| 86 | D_COMPLIANCE | D_GOV_AUDIT | 11 | import_depends |
| 87 | D_TRADING | D_INFRASTRUCTURE | 11 | import_depends,test_depends |
| 88 | D_GOV_DRIFT | D_GOVERNANCE | 10 | import_depends,runtime |
| 89 | D_GOV_DOCS | D_GOVERNANCE | 10 | contract,data,runtime |
| 90 | D_GOV_SCRIPTS | D_GOV_REPAIR | 10 | import_depends |
| 91 | D_INFRA_A2A | D_SHARED | 10 | import_depends |
| 92 | D_INFRA_TELEMETRY | D_INFRA_RUNTIME | 10 | import_depends |
| 93 | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | 10 | import_depends |
| 94 | D_GOV_AUDIT | D_INFRA_RUNTIME | 10 | test_depends |
| 95 | D_GOV_AUDIT | D_FBL_DETECTORS | 10 | test_depends |
| 96 | D_AUTONOMY_CORE | D_ORCHESTRATOR | 9 | test_depends |
| 97 | D_REPORTING | D_INFRASTRUCTURE | 9 | import_depends |
| 98 | D_GOVERNANCE | D_GOV_KB | 8 | config_depends,import_depends,runtime,test_depends |
| 99 | D_INFRA_RUNTIME | D_SECURITY | 8 | import_depends,test_depends |
| 100 | D_ORCHESTRATOR | D_INTEGRATION | 8 | import_depends |
| 101 | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | 8 | import_depends,test_depends |
| 102 | D_AUTONOMY_CORE | D_SECURITY | 8 | import_depends,test_depends |
| 103 | D_GOV_SCRIPTS | D_INFRA_RUNTIME | 8 | import_depends,test_depends |
| 104 | D_GOV_OPS_RESILIENCE | D_INTEGRATION | 8 | import_depends |
| 105 | D_GOV_AUDIT | D_FBL_VERIFICATION | 8 | test_depends |
| 106 | D_GOVERNANCE | D_GOV_DOCS | 8 | contract,runtime |
| 107 | D_GOV_KB | D_GOV_RULE | 8 | import_depends |
| 108 | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | 7 | import_depends,test_depends |
| 109 | D_GOV_CODE_QUALITY | D_SHARED | 7 | import_depends |
| 110 | D_COMPLIANCE | D_SECURITY | 7 | import_depends |
| 111 | D_GOV_OPS_RESILIENCE | D_OPS | 7 | import_depends |
| 112 | D_INFRA_A2A | D_GOVERNANCE | 7 | import_depends,test_depends |
| 113 | D_GOVERNANCE | D_FRONTEND | 7 | test_depends |
| 114 | D_SECURITY | D_SECURITY_LLM | 7 | config_depends,import_depends |
| 115 | D_INFRA_A2A | D_GOV_AUDIT | 7 | test_depends |
| 116 | D_AUTONOMY_CORE | D_FBL_DETECTORS | 7 | test_depends |
| 117 | D_INFRA_RUNTIME | D_AUTONOMY_CORE | 6 | config_depends,import_depends,test_depends |
| 118 | D_EX_CORE | D_AUTONOMY_CORE | 6 | test_depends |
| 119 | D_EX_CORE | D_TRADING | 6 | import_depends |
| 120 | D_GOV_ENFORCEMENT | D_SECURITY | 6 | import_depends,test_depends |
| 121 | D_GOV_DRIFT | D_GOV_AUDIT | 6 | import_depends |
| 122 | D_GOV_ENFORCEMENT | D_GOV_AUDIT | 6 | import_depends |
| 123 | D_GOVERNANCE | D_GOV_SCRIPTS | 6 | config_depends,import_depends,test_depends |
| 124 | D_INTELLIGENCE | D_ML_TRAIN | 6 | config_depends,import_depends |
| 125 | D_INFRA_RUNTIME | D_GOV_AUDIT | 6 | import_depends,test_depends |
| 126 | D_GOV_ENFORCEMENT | D_GOV_DRIFT | 6 | import_depends,test_depends |
| 127 | D_EX_CORE | D_GOVERNANCE | 6 | import_depends |
| 128 | D_INFRA_RUNTIME | D_INTELLIGENCE | 5 | import_depends |
| 129 | D_INFRA_RECOVERY | D_GOV_AUDIT | 5 | import_depends |
| 130 | D_AUTONOMY_CORE | D_GOV_AUDIT | 5 | import_depends,test_depends |
| 131 | D_GOV_CODE_QUALITY | D_GOVERNANCE | 5 | import_depends |
| 132 | D_INFRA_RUNTIME | D_TRADING | 5 | import_depends,test_depends |
| 133 | D_INFRA_RUNTIME | D_GOV_RULE | 5 | import_depends,test_depends |
| 134 | D_GOV_RULE | D_INTEGRATION | 5 | import_depends |
| 135 | D_GOV_DRIFT | D_SECURITY | 5 | import_depends |
| 136 | D_KNOWLEDGE | D_FEEDBACK_LOOP | 5 | test_depends |
| 137 | D_SECURITY_LLM | D_INTEGRATION | 5 | test_depends |
| 138 | D_INTELLIGENCE | D_GOV_DRIFT | 5 | test_depends |
| 139 | D_FRONTEND | D_GOVERNANCE | 5 | import_depends,runtime |
| 140 | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | 5 | import_depends,runtime |
| 141 | D_INFRA_RUNTIME | D_INFRA_RECOVERY | 5 | import_depends,test_depends |
| 142 | D_GOV_REPAIR | D_GOV_DRIFT | 5 | import_depends |
| 143 | D_SHARED | D_DATA | 5 | test_depends |
| 144 | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | 5 | import_depends |
| 145 | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | 5 | import_depends,test_depends |
| 146 | D_INFRA_RECOVERY | D_ORCHESTRATOR | 5 | test_depends |
| 147 | D_GOV_REPAIR | D_GOV_CODE_QUALITY | 4 | import_depends |
| 148 | D_SHARED | D_FEEDBACK_LOOP | 4 | import_depends,test_depends |
| 149 | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | 4 | import_depends |
| 150 | D_GOV_KB | D_INTEGRATION | 4 | import_depends |
| 151 | D_GOVERNANCE | D_FBL_VERIFICATION | 4 | runtime,test_depends |
| 152 | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | 4 | config_depends |
| 153 | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | 4 | import_depends |
| 154 | D_SECURITY | D_GOV_RULE | 4 | import_depends |
| 155 | D_GOVERNANCE | D_GOV_REPAIR | 4 | import_depends,test_depends |
| 156 | D_SECURITY | D_GOV_AUDIT | 4 | import_depends |
| 157 | D_RISK | D_TRADING | 4 | import_depends,test_depends |
| 158 | D_EX_CORE | D_INFRASTRUCTURE | 4 | import_depends |
| 159 | D_OPS | D_SHARED | 4 | import_depends |
| 160 | D_KNOWLEDGE | D_INTELLIGENCE | 4 | test_depends |
| 161 | D_KNOWLEDGE | D_GOV_RULE | 4 | test_depends |
| 162 | D_SHARED | D_SECURITY | 4 | test_depends |
| 163 | D_INTELLIGENCE | D_INTEGRATION | 4 | import_depends,test_depends |
| 164 | D_INTELLIGENCE | D_FEEDBACK_LOOP | 4 | test_depends |
| 165 | D_INTELLIGENCE | D_FBL_DIAGNOSERS | 4 | test_depends |
| 166 | D_INTELLIGENCE | D_BACKTEST | 4 | import_depends,test_depends |
| 167 | D_INTEGRATION | D_OPS | 4 | import_depends |
| 168 | D_INTEGRATION | D_GOV_AUDIT | 4 | import_depends,test_depends |
| 169 | D_INTEGRATION | D_GOVERNANCE | 4 | import_depends |
| 170 | D_GOV_AUDIT | D_GOV_RULE | 4 | import_depends,test_depends |
| 171 | D_GOV_AUDIT | D_INFRA_A2A | 4 | test_depends |
| 172 | D_GOV_REPAIR | D_GOV_ENFORCEMENT | 4 | import_depends |
| 173 | D_SHARED | D_GOV_DRIFT | 4 | test_depends |
| 174 | D_GOV_AUDIT | D_INTELLIGENCE | 4 | test_depends |
| 175 | D_AUTONOMY_CORE | D_INTELLIGENCE | 4 | import_depends,test_depends |
| 176 | D_SHARED | D_GOV_AUDIT | 4 | import_depends,test_depends |
| 177 | D_FEEDBACK_LOOP | D_GOVERNANCE | 4 | import_depends |
| 178 | D_FEEDBACK_LOOP | D_INTEGRATION | 4 | import_depends,runtime |
| 179 | D_INFRASTRUCTURE | D_INFRA_RUNTIME | 4 | test_depends |
| 180 | D_GOV_SCRIPTS | D_GOV_OPS_RESILIENCE | 4 | import_depends,test_depends |
| 181 | D_GOV_SCRIPTS | D_DATA | 4 | import_depends |
| 182 | D_GOV_REPAIR | D_OPS | 4 | import_depends |
| 183 | D_TRADING | D_GOVERNANCE | 4 | import_depends |
| 184 | D_GOV_OPS_RESILIENCE | D_SECURITY | 4 | import_depends |
| 185 | D_INFRASTRUCTURE | D_SECURITY | 3 | test_depends |
| 186 | D_FRONTEND | D_FBL_DETECTORS | 3 | test_depends |
| 187 | D_FRONTEND | D_SHARED | 3 | import_depends |
| 188 | D_FUNDAMENTAL_SIGNAL | D_SIGLEGACY | 3 | config_depends |
| 189 | D_FUNDAMENTAL_SIGNAL | D_TRADING | 3 | import_depends |
| 190 | D_GOVERNANCE | D_FEEDBACK_LOOP | 3 | runtime,test_depends |
| 191 | D_FBL_DETECTORS | D_FEEDBACK_LOOP | 3 | import_depends |
| 192 | D_GOVERNANCE | D_RISK | 3 | import_depends |
| 193 | D_GOVERNANCE | D_SECURITY_LLM | 3 | contract,import_depends,runtime |
| 194 | D_GOVERNANCE | D_TRADING | 3 | import_depends,test_depends |
| 195 | D_GOV_AUDIT | D_AUTONOMY_CORE | 3 | test_depends |
| 196 | D_GOV_AUDIT | D_INFRA_RECOVERY | 3 | test_depends |
| 197 | D_GOV_AUDIT | D_INTEGRATION | 3 | import_depends |
| 198 | D_GOV_AUDIT | D_TRADING | 3 | test_depends |
| 199 | D_GOV_DOCS | D_FBL_VERIFICATION | 3 | contract,runtime |
| 200 | D_GOV_ENFORCEMENT | D_FBL_DETECTORS | 3 | test_depends |
| 201 | D_GOV_ENFORCEMENT | D_FBL_DIAGNOSERS | 3 | test_depends |
| 202 | D_GOV_ENFORCEMENT | D_GOVERNANCE | 3 | import_depends,test_depends |
| 203 | D_COMPLIANCE | D_GOVERNANCE | 3 | import_depends |
| 204 | D_BACKTEST | D_SHARED | 3 | import_depends |
| 205 | D_GOV_OPS_RESILIENCE | D_GOV_KB | 3 | import_depends |
| 206 | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | 3 | import_depends |
| 207 | D_BACKTEST | D_GOVERNANCE | 3 | import_depends |
| 208 | D_GOV_SCRIPTS | D_AUTONOMY_CORE | 3 | import_depends,test_depends |
| 209 | D_GOV_SCRIPTS | D_INTEGRATION | 3 | import_depends |
| 210 | D_GOV_SCRIPTS | D_ORCHESTRATOR | 3 | import_depends,test_depends |
| 211 | D_GOV_SCRIPTS | D_SECURITY | 3 | import_depends,test_depends |
| 212 | D_INFRASTRUCTURE | D_ORCHESTRATOR | 3 | test_depends |
| 213 | D_INFRA_RECOVERY | D_GOV_DRIFT | 3 | test_depends |
| 214 | D_INFRA_RECOVERY | D_INFRA_RUNTIME | 3 | import_depends,test_depends |
| 215 | D_INFRA_RECOVERY | D_SECURITY | 3 | import_depends,test_depends |
| 216 | D_INFRA_RUNTIME | D_FBL_DETECTORS | 3 | test_depends |
| 217 | D_INFRA_RUNTIME | D_GOV_DRIFT | 3 | import_depends,test_depends |
| 218 | D_AUTONOMY_CORE | D_INFRA_RECOVERY | 3 | test_depends |
| 219 | D_INTEGRATION | D_AUTONOMY_CORE | 3 | import_depends |
| 220 | D_INTEGRATION | D_GOV_KB | 3 | import_depends |
| 221 | D_INTEGRATION | D_INTELLIGENCE | 3 | import_depends |
| 222 | D_INTEGRATION | D_SECURITY | 3 | import_depends |
| 223 | D_AUTONOMY_CORE | D_GOV_RULE | 3 | import_depends,test_depends |
| 224 | D_INTELLIGENCE | D_AUTONOMY_CORE | 3 | import_depends,test_depends |
| 225 | D_INTELLIGENCE | D_GOVERNANCE | 3 | import_depends,test_depends |
| 226 | D_INTELLIGENCE | D_GOV_KB | 3 | import_depends |
| 227 | D_INTELLIGENCE | D_GOV_RULE | 3 | import_depends,test_depends |
| 228 | D_ML_TRAIN | D_SHARED | 3 | import_depends |
| 229 | D_ORCHESTRATOR | D_GOVERNANCE | 3 | import_depends |
| 230 | D_ORCHESTRATOR | D_INFRA_RUNTIME | 3 | import_depends |
| 231 | D_RISK | D_INFRASTRUCTURE | 3 | import_depends,test_depends |
| 232 | D_SECURITY | D_GOVERNANCE | 3 | import_depends |
| 233 | D_SECURITY | D_INFRA_RUNTIME | 3 | import_depends |
| 234 | D_SHARED | D_FBL_DETECTORS | 3 | test_depends |
| 235 | D_SHARED | D_FBL_VERIFICATION | 3 | test_depends |
| 236 | D_SHARED | D_GOV_CODE_QUALITY | 3 | test_depends |
| 237 | D_AUDITTEST | D_GOVERNANCE | 3 | test_depends |
| 238 | D_SHARED | D_GOV_RULE | 3 | import_depends,test_depends |
| 239 | D_TRADING | D_GOV_ENFORCEMENT | 3 | import_depends,test_depends |
| 240 | D_FEEDBACK_LOOP | D_GOV_AUDIT | 3 | test_depends |
| 241 | D_EX_CORE | D_SHARED | 2 | import_depends |
| 242 | D_SIGQC | D_TRADING | 2 | import_depends |
| 243 | D_INTEGRATION | D_FBL_DETECTORS | 2 | test_depends |
| 244 | D_RISK | D_GOV_CODE_QUALITY | 2 | test_depends |
| 245 | D_INFRASTRUCTURE | D_GOV_CODE_QUALITY | 2 | test_depends |
| 246 | D_FRONTEND | D_BACKTEST | 2 | import,import_depends |
| 247 | D_DATA | D_MKT_DATA | 2 | data |
| 248 | D_RISK | D_SHARED | 2 | import_depends,test_depends |
| 249 | D_INFRA_RUNTIME | D_FBL_DIAGNOSERS | 2 | test_depends |
| 250 | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | 2 | contract,test_depends |
| 251 | D_SECURITY | D_FEEDBACK_LOOP | 2 | import_depends,test_depends |
| 252 | D_INFRASTRUCTURE | D_GOV_DRIFT | 2 | test_depends |
| 253 | D_INTELLIGENCE | D_SECURITY | 2 | test_depends |
| 254 | D_AUTONOMY_CORE | D_GOV_DRIFT | 2 | runtime,test_depends |
| 255 | D_GOV_DOCS | D_INFRA_A2A | 2 | contract,runtime |
| 256 | D_SECURITY | D_GOV_OPS_RESILIENCE | 2 | import_depends,test_depends |
| 257 | D_INTEGRATION | D_GOV_RULE | 2 | import_depends |
| 258 | D_AUTONOMY_PERM | D_INFRA_RUNTIME | 2 | test_depends |
| 259 | D_SECURITY | D_INTEGRATION | 2 | import_depends |
| 260 | D_KNOWLEDGE | D_FBL_DIAGNOSERS | 2 | test_depends |
| 261 | D_INTEGRATION | D_INFRA_RECOVERY | 2 | import_depends,test_depends |
| 262 | D_AUTONOMY_CORE | D_GOV_DOCS | 2 | runtime |
| 263 | D_SECURITY_LLM | D_FBL_DIAGNOSERS | 2 | test_depends |
| 264 | D_INFRA_RECOVERY | D_FBL_VERIFICATION | 2 | test_depends |
| 265 | D_SHARED | D_ORCHESTRATOR | 2 | test_depends |
| 266 | D_EX_CORE | D_BACKTEST | 2 | import_depends |
| 267 | D_FUNDAMENTAL_SIGNAL | D_SHARED | 2 | import_depends |
| 268 | D_SHARED | D_GOV_ENFORCEMENT | 2 | test_depends |
| 269 | D_FRONTEND | D_FBL_DIAGNOSERS | 2 | test_depends |
| 270 | D_FEEDBACK_LOOP | D_GOV_DRIFT | 2 | import_depends |
| 271 | D_KNOWLEDGE | D_ORCHESTRATOR | 2 | test_depends |
| 272 | D_GOVERNANCE | D_FBL_DIAGNOSERS | 2 | test_depends |
| 273 | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 274 | D_AUTONOMY_PERM | D_GOVERNANCE | 2 | config_depends |
| 275 | D_SHARED | D_SIMULATION | 2 | import_depends,test_depends |
| 276 | D_SHARED | D_FBL_DIAGNOSERS | 2 | test_depends |
| 277 | D_ML_TRAIN | D_TRADING | 2 | import_depends |
| 278 | D_GOV_SCRIPTS | D_GOV_AUDIT | 2 | import_depends |
| 279 | D_OPS | D_GOV_DRIFT | 2 | import_depends |
| 280 | D_OPS | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 281 | D_GOV_SCRIPTS | D_FBL_VERIFICATION | 2 | test_depends |
| 282 | D_TRADING | D_INTEGRATION | 2 | import_depends,test_depends |
| 283 | D_GOV_OPS_RESILIENCE | D_GOV_RULE | 2 | import_depends |
| 284 | D_GOV_KB | D_GOVERNANCE | 2 | import_depends |
| 285 | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | 2 | import_depends |
| 286 | D_ORCHESTRATOR | D_AUTONOMY_CORE | 2 | import_depends |
| 287 | D_GOV_AUDIT | D_REPORTING | 2 | import_depends |
| 288 | D_GOV_ENFORCEMENT | D_OPS | 2 | import_depends |
| 289 | D_TRADING | D_EX_CORE | 2 | test_depends |
| 290 | D_GOV_ENFORCEMENT | D_INTEGRATION | 2 | import_depends,test_depends |
| 291 | D_INFRASTRUCTURE | D_FBL_VERIFICATION | 2 | test_depends |
| 292 | D_ORCHESTRATOR | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 293 | D_GOV_DOCS | D_INTEGRATION | 2 | contract,runtime |
| 294 | D_GOV_DOCS | D_GOV_DRIFT | 2 | runtime |
| 295 | D_GOVERNANCE | D_DATA | 2 | import_depends |
| 296 | D_SHARED | D_INTEGRATION | 2 | test_depends |
| 297 | D_ORCHESTRATOR | D_SECURITY | 2 | import_depends |
| 298 | D_GOV_ENFORCEMENT | D_FEEDBACK_LOOP | 2 | test_depends |
| 299 | D_DATA | D_FBL_VERIFICATION | 2 | test_depends |
| 300 | D_BACKTEST | D_DATA | 2 | import_depends |
| 301 | D_INFRASTRUCTURE | D_FEEDBACK_LOOP | 2 | test_depends |
| 302 | D_PF_ALLOC | D_INFRASTRUCTURE | 2 | import_depends |
| 303 | D_GOV_REPAIR | D_INFRA_RECOVERY | 2 | import_depends |
| 304 | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 305 | D_INFRA_TELEMETRY | D_SHARED | 2 | import_depends |
| 306 | D_PF_CORE | D_GOVERNANCE | 2 | import_depends |
| 307 | D_GOV_RULE | D_GOVERNANCE | 2 | import_depends |
| 308 | D_GOV_RULE | D_GOV_AUDIT | 2 | import_depends |
| 309 | D_GOV_RULE | D_GOV_DRIFT | 2 | import_depends |
| 310 | D_GOV_RULE | D_GOV_ENFORCEMENT | 2 | config_depends,import_depends |
| 311 | D_FRONTEND | D_EX_CORE | 2 | import_depends |
| 312 | D_GOV_SCRIPTS | D_GOV_ENFORCEMENT | 2 | import_depends |
| 313 | D_GOV_DRIFT | D_INTEGRATION | 2 | import_depends |
| 314 | D_INTELLIGENCE | D_FRONTEND | 1 | test_depends |
| 315 | D_INTELLIGENCE | D_FUNDAMENTAL_SIGNAL | 1 | test_depends |
| 316 | D_SIGLEGACY | D_FACTOR | 1 | contract |
| 317 | D_INTELLIGENCE | D_GOV_CODE_QUALITY | 1 | test_depends |
| 318 | D_GOVERNANCE | D_SIMULATION | 1 | import_depends |
| 319 | D_INTELLIGENCE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 320 | D_TRADING | D_PF_CORE | 1 | test_depends |
| 321 | D_GOVERNANCE | D_SIGLEGACY | 1 | import_depends |
| 322 | D_TRADING | D_REPORTING | 1 | test_depends |
| 323 | D_INTELLIGENCE | D_ORCHESTRATOR | 1 | test_depends |
| 324 | D_AUTONOMY_CORE | D_GOV_REPAIR | 1 | test_depends |
| 325 | D_INTELLIGENCE | D_TRADING | 1 | import_depends |
| 326 | D_KNOWLEDGE | D_AUTONOMY_CORE | 1 | test_depends |
| 327 | D_GOVERNANCE | D_REPORTING | 1 | import_depends |
| 328 | D_KNOWLEDGE | D_GOV_AUDIT | 1 | test_depends |
| 329 | D_KNOWLEDGE | D_GOV_DRIFT | 1 | test_depends |
| 330 | D_KNOWLEDGE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 331 | D_GOVERNANCE | D_ML_TRAIN | 1 | data |
| 332 | D_KNOWLEDGE | D_INFRA_RUNTIME | 1 | runtime |
| 333 | D_GOVERNANCE | D_KNOWLEDGE | 1 | contract |
| 334 | D_MKT_DATA | D_INFRASTRUCTURE | 1 | import_depends |
| 335 | D_ML_TRAIN | D_INTELLIGENCE | 1 | config_depends |
| 336 | D_SIMULATION | D_INFRASTRUCTURE | 1 | import_depends |
| 337 | D_OPS | D_GOVERNANCE | 1 | import_depends |
| 338 | D_OPS | D_INFRA_RECOVERY | 1 | import_depends |
| 339 | D_GOVERNANCE | D_INTEGRATION_GATEWAY | 1 | import_depends |
| 340 | D_ORCHESTRATOR | D_FEEDBACK_LOOP | 1 | import_depends |
| 341 | D_ORCHESTRATOR | D_GOV_DRIFT | 1 | import_depends |
| 342 | D_ORCHESTRATOR | D_INFRASTRUCTURE | 1 | import_depends |
| 343 | D_TRADING | D_FEEDBACK_LOOP | 1 | test_depends |
| 344 | D_EX_CORE | D_INFRA_RECOVERY | 1 | test_depends |
| 345 | D_AUTONOMY_CORE | D_GOV_KB | 1 | import_depends |
| 346 | D_PF_ALLOC | D_GOVERNANCE | 1 | import_depends |
| 347 | D_PF_ALLOC | D_SHARED | 1 | import_depends |
| 348 | D_PF_CORE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 349 | D_PF_CORE | D_PF_ALLOC | 1 | import_depends |
| 350 | D_RISK | D_FBL_DETECTORS | 1 | test_depends |
| 351 | D_RISK | D_GOVERNANCE | 1 | test_depends |
| 352 | D_RISK | D_GOV_RULE | 1 | test_depends |
| 353 | D_RISK | D_ORCHESTRATOR | 1 | test_depends |
| 354 | D_FACTOR | D_FUNDAMENTAL_SIGNAL | 1 | import_depends |
| 355 | D_TRADING | D_GOV_AUDIT | 1 | import_depends |
| 356 | D_FACTOR | D_GOVERNANCE | 1 | runtime |
| 357 | D_SECURITY | D_GOV_KB | 1 | test_depends |
| 358 | D_FACTOR | D_INFRA_RUNTIME | 1 | runtime |
| 359 | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | 1 | import_depends |
| 360 | D_SECURITY | D_INTELLIGENCE | 1 | import_depends |
| 361 | D_FBL_DIAGNOSERS | D_SHARED | 1 | import_depends |
| 362 | D_SECURITY_LLM | D_FBL_VERIFICATION | 1 | test_depends |
| 363 | D_FBL_VERIFICATION | D_GOV_AUDIT | 1 | import_depends |
| 364 | D_SECURITY_LLM | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 365 | D_SECURITY_LLM | D_GOV_RULE | 1 | test_depends |
| 366 | D_SECURITY_LLM | D_INFRA_A2A | 1 | test_depends |
| 367 | D_AUTONOMY_CORE | D_GOV_CODE_QUALITY | 1 | test_depends |
| 368 | D_FBL_VERIFICATION | D_SECURITY | 1 | import_depends |
| 369 | D_SECURITY_LLM | D_ORCHESTRATOR | 1 | test_depends |
| 370 | D_GOVERNANCE | D_FBL_DETECTORS | 1 | test_depends |
| 371 | D_GOVERNANCE | D_FACTOR | 1 | runtime |
| 372 | D_FEEDBACK_LOOP | D_SECURITY | 1 | import_depends |
| 373 | D_AUTONOMY_CORE | D_EX_CORE | 1 | test_depends |
| 374 | D_GOV_OPS_RESILIENCE | D_FACTOR | 1 | import_depends |
| 375 | D_GOV_KB | D_INFRA_RUNTIME | 1 | runtime |
| 376 | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | 1 | import_depends |
| 377 | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 378 | D_GOVERNANCE | D_EX_CORE | 1 | import_depends |
| 379 | D_GOV_OPS_RESILIENCE | D_INFRA_RUNTIME | 1 | import_depends |
| 380 | D_GOV_ENFORCEMENT | D_ORCHESTRATOR | 1 | test_depends |
| 381 | D_SHARED | D_FUNDAMENTAL_SIGNAL | 1 | test_depends |
| 382 | D_GOV_ENFORCEMENT | D_INFRASTRUCTURE | 1 | import_depends |
| 383 | D_GOV_REPAIR | D_AUTONOMY_CORE | 1 | import_depends |
| 384 | D_GOV_REPAIR | D_FACTOR | 1 | import_depends |
| 385 | D_BACKTEST | D_INFRA_RUNTIME | 1 | import_depends |
| 386 | D_GOV_ENFORCEMENT | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 387 | D_COMPLIANCE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 388 | D_GOV_REPAIR | D_GOV_KB | 1 | import_depends |
| 389 | D_GOV_REPAIR | D_GOV_RULE | 1 | import_depends |
| 390 | D_GOV_REPAIR | D_INFRA_A2A | 1 | import_depends |
| 391 | D_COMPLIANCE | D_INFRA_RUNTIME | 1 | import_depends |
| 392 | D_GOV_REPAIR | D_TRADING | 1 | import_depends |
| 393 | D_GOV_RULE | D_GOV_SCRIPTS | 1 | config_depends |
| 394 | D_GOV_RULE | D_INFRA_RECOVERY | 1 | import_depends |
| 395 | D_GOV_RULE | D_INFRA_RUNTIME | 1 | import_depends |
| 396 | D_GOV_DRIFT | D_INFRA_RECOVERY | 1 | import_depends |
| 397 | D_GOV_SCRIPTS | D_FBL_DETECTORS | 1 | test_depends |
| 398 | D_GOV_SCRIPTS | D_FEEDBACK_LOOP | 1 | test_depends |
| 399 | D_AUTONOMY_PERM | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 400 | D_GOV_SCRIPTS | D_GOV_DRIFT | 1 | test_depends |
| 401 | D_GOV_DRIFT | D_INFRA_A2A | 1 | runtime |
| 402 | D_GOV_DRIFT | D_GOV_SCRIPTS | 1 | import_depends |
| 403 | D_GOV_SCRIPTS | D_INFRA_RECOVERY | 1 | test_depends |
| 404 | D_GOV_DRIFT | D_GOV_ENFORCEMENT | 1 | runtime |
| 405 | D_FEEDBACK_LOOP | D_ORCHESTRATOR | 1 | import_depends |
| 406 | D_GOV_SCRIPTS | D_INTELLIGENCE | 1 | import_depends |
| 407 | D_FUNDAMENTAL_SIGNAL | D_FACTOR | 1 | import_depends |
| 408 | D_AUTONOMY_CORE | D_TRADING | 1 | test_depends |
| 409 | D_INFRASTRUCTURE | D_AUTONOMY_CORE | 1 | test_depends |
| 410 | D_INFRASTRUCTURE | D_FBL_DETECTORS | 1 | test_depends |
| 411 | D_INFRASTRUCTURE | D_GOVERNANCE | 1 | test_depends |
| 412 | D_INFRASTRUCTURE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 413 | D_INFRASTRUCTURE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 414 | D_GOV_DRIFT | D_GOV_DOCS | 1 | runtime |
| 415 | D_GOV_DRIFT | D_FBL_VERIFICATION | 1 | runtime |
| 416 | D_AUTONOMY_CORE | D_SECURITY_LLM | 1 | runtime |
| 417 | D_INFRA_A2A | D_FEEDBACK_LOOP | 1 | test_depends |
| 418 | D_GOV_DOCS | D_SECURITY_LLM | 1 | contract |
| 419 | D_INFRA_A2A | D_GOV_DRIFT | 1 | test_depends |
| 420 | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 421 | D_INFRA_A2A | D_INFRA_RUNTIME | 1 | import_depends |
| 422 | D_INFRA_A2A | D_SECURITY | 1 | test_depends |
| 423 | D_INFRA_RECOVERY | D_FBL_DETECTORS | 1 | test_depends |
| 424 | D_INFRA_RECOVERY | D_GOVERNANCE | 1 | import_depends |
| 425 | D_GOV_DOCS | D_GOV_KB | 1 | runtime |
| 426 | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | 1 | test_depends |
| 427 | D_INFRA_RECOVERY | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 428 | D_FRONTEND | D_TRADING | 1 | import_depends |
| 429 | D_GOV_DOCS | D_GOV_ENFORCEMENT | 1 | runtime |
| 430 | D_INFRA_RECOVERY | D_POSITION | 1 | test_depends |
| 431 | D_SHARED | D_INFRA_A2A | 1 | test_depends |
| 432 | D_GOV_DOCS | D_GOV_AUDIT | 1 | runtime |
| 433 | D_INFRA_RUNTIME | D_DATA | 1 | import_depends |
| 434 | D_SHARED | D_INFRA_RECOVERY | 1 | test_depends |
| 435 | D_GOV_DOCS | D_FEEDBACK_LOOP | 1 | runtime |
| 436 | D_GOV_DOCS | D_AUTONOMY_CORE | 1 | runtime |
| 437 | D_GOV_CODE_QUALITY | D_INFRA_RUNTIME | 1 | import_depends |
| 438 | D_FEEDBACK_LOOP | D_DATA_SEC | 1 | runtime |
| 439 | D_GOV_CODE_QUALITY | D_GOV_SCRIPTS | 1 | config_depends |
| 440 | D_INFRA_RUNTIME | D_GOV_REPAIR | 1 | test_depends |
| 441 | D_GOV_CODE_QUALITY | D_DATA | 1 | import_depends |
| 442 | D_INFRA_RUNTIME | D_INFRASTRUCTURE | 1 | import_depends |
| 443 | D_AUTONOMY_CORE | D_OPS | 1 | test_depends |
| 444 | D_GOV_CODE_QUALITY | D_AUTONOMY_CORE | 1 | import_depends |
| 445 | D_DATA | D_FBL_DIAGNOSERS | 1 | test_depends |
| 446 | D_INFRA_RUNTIME | D_OPS | 1 | import_depends |
| 447 | D_INFRA_RUNTIME | D_ORCHESTRATOR | 1 | import_depends |
| 448 | D_GOV_AUDIT | D_ORCHESTRATOR | 1 | test_depends |
| 449 | D_GOV_AUDIT | D_GOV_ENFORCEMENT | 1 | test_depends |
| 450 | D_SHARED | D_INTELLIGENCE | 1 | test_depends |
| 451 | D_INTEGRATION | D_FEEDBACK_LOOP | 1 | test_depends |
| 452 | D_DATA | D_FEEDBACK_LOOP | 1 | test_depends |
| 453 | D_GOV_AUDIT | D_GOV_DOCS | 1 | runtime |
| 454 | D_SHARED | D_OPS | 1 | test_depends |
| 455 | D_INTEGRATION | D_INFRASTRUCTURE | 1 | import_depends |
| 456 | D_AUTONOMY_CORE | D_INFRA_A2A | 1 | contract |
| 457 | D_GOV_AUDIT | D_GOV_CODE_QUALITY | 1 | test_depends |
| 458 | D_SHARED | D_POSITION | 1 | test_depends |
| 459 | D_INTEGRATION | D_TRADING | 1 | import_depends |
| 460 | D_INTEGRATION_GATEWAY | D_GOVERNANCE | 1 | import_depends |
| 461 | D_AUDITTEST | D_TRADING | 1 | test_depends |
| 462 | D_DATA | D_GOV_ENFORCEMENT | 1 | import_depends |
| 463 | D_INTELLIGENCE | D_EX_CORE | 1 | test_depends |
| 464 | D_INTELLIGENCE | D_FBL_DETECTORS | 1 | test_depends |
| 465 | D_DATA | D_GOV_RULE | 1 | test_depends |
| 466 | D_INTELLIGENCE | D_FBL_VERIFICATION | 1 | test_depends |
| 467 | D_DATA | D_INTEGRATION | 1 | test_depends |
