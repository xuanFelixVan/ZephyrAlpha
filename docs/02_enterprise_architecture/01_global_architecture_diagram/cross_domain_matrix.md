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
| 跨域依赖对数 | 437 |
| 跨域依赖边总数 | 3900 |

## 跨域依赖 Top 20（按边数降序）

| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|------|--------|:---:|---------|
| D_INFRA_RUNTIME | D_SHARED | 187 | config_depends,import_depends,test_depends |
| D_GOVERNANCE | D_GOV_SCRIPTS | 131 | config_depends,test_depends |
| D_AUTONOMY_PERM | D_SECURITY | 130 | import_depends,test_depends |
| D_GOVERNANCE | D_SHARED | 110 | import_depends,test_depends |
| D_GOV_SCRIPTS | D_GOV_RULE | 96 | test_depends |
| D_GOVERNANCE | D_GOV_CODE_QUALITY | 89 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_OPS_RESILIENCE | 69 | import_depends,test_depends |
| D_AUTONOMY_CORE | D_FBL_VERIFICATION | 66 | test_depends |
| D_INTEGRATION | D_SHARED | 66 | import_depends |
| D_GOV_REPAIR | D_GOVERNANCE | 66 | config_depends,import_depends |
| D_AUTONOMY_CORE | D_FEEDBACK_LOOP | 64 | test_depends |
| D_GOV_AUDIT | D_GOV_DRIFT | 58 | import_depends,test_depends |
| D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | 57 | import_depends,test_depends |
| D_INFRASTRUCTURE | D_SHARED | 56 | config_depends,import_depends,test_depends |
| D_GOV_SCRIPTS | D_SHARED | 52 | import_depends,test_depends |
| D_GOVERNANCE | D_GOV_ENFORCEMENT | 51 | import_depends,test_depends |
| D_GOV_AUDIT | D_SHARED | 50 | import_depends,test_depends |
| D_AUTONOMY_CORE | D_INFRA_RUNTIME | 48 | import_depends,test_depends |
| D_COMPLIANCE | D_GOV_DRIFT | 45 | import_depends |
| D_SECURITY | D_GOV_DRIFT | 44 | import_depends |

## 完整跨域依赖清单

| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |
|:---:|------|--------|:---:|---------|
| 1 | D_INFRA_RUNTIME | D_SHARED | 187 | config_depends,import_depends,test_depends |
| 2 | D_GOVERNANCE | D_GOV_SCRIPTS | 131 | config_depends,test_depends |
| 3 | D_AUTONOMY_PERM | D_SECURITY | 130 | import_depends,test_depends |
| 4 | D_GOVERNANCE | D_SHARED | 110 | import_depends,test_depends |
| 5 | D_GOV_SCRIPTS | D_GOV_RULE | 96 | test_depends |
| 6 | D_GOVERNANCE | D_GOV_CODE_QUALITY | 89 | import_depends,test_depends |
| 7 | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | 69 | import_depends,test_depends |
| 8 | D_AUTONOMY_CORE | D_FBL_VERIFICATION | 66 | test_depends |
| 9 | D_INTEGRATION | D_SHARED | 66 | import_depends |
| 10 | D_GOV_REPAIR | D_GOVERNANCE | 66 | config_depends,import_depends |
| 11 | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | 64 | test_depends |
| 12 | D_GOV_AUDIT | D_GOV_DRIFT | 58 | import_depends,test_depends |
| 13 | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | 57 | import_depends,test_depends |
| 14 | D_INFRASTRUCTURE | D_SHARED | 56 | config_depends,import_depends,test_depends |
| 15 | D_GOV_SCRIPTS | D_SHARED | 52 | import_depends,test_depends |
| 16 | D_GOVERNANCE | D_GOV_ENFORCEMENT | 51 | import_depends,test_depends |
| 17 | D_GOV_AUDIT | D_SHARED | 50 | import_depends,test_depends |
| 18 | D_AUTONOMY_CORE | D_INFRA_RUNTIME | 48 | import_depends,test_depends |
| 19 | D_COMPLIANCE | D_GOV_DRIFT | 45 | import_depends |
| 20 | D_SECURITY | D_GOV_DRIFT | 44 | import_depends |
| 21 | D_GOVERNANCE | D_GOV_AUDIT | 44 | import_depends,test_depends |
| 22 | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | 43 | import_depends,test_depends |
| 23 | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | 42 | import_depends,test_depends |
| 24 | D_SECURITY_LLM | D_SECURITY | 41 | config_depends,import_depends,test_depends |
| 25 | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | 40 | import_depends |
| 26 | D_SECURITY | D_FBL_VERIFICATION | 36 | test_depends |
| 27 | D_TRADING | D_INFRA_RUNTIME | 36 | import_depends,test_depends |
| 28 | D_AUTONOMY_CORE | D_INTEGRATION | 35 | import_depends,test_depends |
| 29 | D_ORCHESTRATOR | D_SHARED | 34 | import_depends,test_depends |
| 30 | D_FEEDBACK_LOOP | D_FBL_DETECTORS | 33 | import_depends,test_depends |
| 31 | D_GOVERNANCE | D_INFRA_RUNTIME | 29 | config_depends,import_depends,test_depends |
| 32 | D_SECURITY | D_SHARED | 29 | import_depends,test_depends |
| 33 | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | 29 | import_depends,test_depends |
| 34 | D_TRADING | D_ORCHESTRATOR | 29 | import_depends,test_depends |
| 35 | D_AUTONOMY_CORE | D_SHARED | 26 | import_depends,test_depends |
| 36 | D_GOVERNANCE | D_TRADING | 26 | import_depends,test_depends |
| 37 | D_SHARED | D_INFRA_RUNTIME | 26 | config_depends,import_depends,test_depends |
| 38 | D_GOVERNANCE | D_GOV_RULE | 25 | import_depends,test_depends |
| 39 | D_GOVERNANCE | D_INTEGRATION | 24 | config_depends,import_depends,test_depends |
| 40 | D_GOV_AUDIT | D_FBL_DIAGNOSERS | 24 | test_depends |
| 41 | D_GOV_REPAIR | D_GOV_AUDIT | 23 | import_depends |
| 42 | D_GOV_DRIFT | D_SHARED | 22 | import_depends |
| 43 | D_GOVERNANCE | D_INFRA_RECOVERY | 22 | import_depends,test_depends |
| 44 | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | 21 | import_depends |
| 45 | D_DATA | D_SHARED | 21 | import_depends,test_depends |
| 46 | D_GOV_AUDIT | D_GOVERNANCE | 21 | config_depends,import_depends,test_depends |
| 47 | D_SHARED | D_GOVERNANCE | 21 | test_depends |
| 48 | D_GOVERNANCE | D_AUTONOMY_CORE | 21 | import_depends,test_depends |
| 49 | D_TRADING | D_SHARED | 20 | import_depends,test_depends |
| 50 | D_SECURITY_LLM | D_SHARED | 20 | test_depends |
| 51 | D_SECURITY_LLM | D_INFRA_RUNTIME | 19 | test_depends |
| 52 | D_INTELLIGENCE | D_SHARED | 19 | import_depends,test_depends |
| 53 | D_GOV_ENFORCEMENT | D_GOV_RULE | 18 | import_depends,test_depends |
| 54 | D_GOV_KB | D_SHARED | 18 | import_depends |
| 55 | D_INFRA_RECOVERY | D_SHARED | 18 | import_depends |
| 56 | D_INFRA_RUNTIME | D_GOVERNANCE | 18 | import_depends,test_depends |
| 57 | D_INFRA_RUNTIME | D_INTEGRATION | 17 | import_depends |
| 58 | D_FEEDBACK_LOOP | D_SHARED | 17 | import_depends |
| 59 | D_GOV_ENFORCEMENT | D_SHARED | 17 | import_depends,test_depends |
| 60 | D_GOVERNANCE | D_SECURITY | 16 | import_depends,test_depends |
| 61 | D_KNOWLEDGE | D_GOV_KB | 16 | test_depends |
| 62 | D_GOV_AUDIT | D_FEEDBACK_LOOP | 15 | import_depends,test_depends |
| 63 | D_GOV_REPAIR | D_TRADING | 15 | import_depends |
| 64 | D_GOVERNANCE | D_INTELLIGENCE | 15 | import_depends,test_depends |
| 65 | D_FRONTEND | D_FEEDBACK_LOOP | 15 | import_depends,test_depends |
| 66 | D_GOV_ENFORCEMENT | D_FBL_VERIFICATION | 14 | test_depends |
| 67 | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | 14 | config_depends,import_depends |
| 68 | D_INFRA_RUNTIME | D_INFRA_A2A | 14 | import_depends,test_depends |
| 69 | D_GOV_RULE | D_SHARED | 14 | import_depends |
| 70 | D_INTEGRATION | D_INFRA_RUNTIME | 14 | import_depends |
| 71 | D_GOVERNANCE | D_OPS | 14 | import_depends,test_depends |
| 72 | D_GOVERNANCE | D_GOV_REPAIR | 14 | import_depends,test_depends |
| 73 | D_AUDITTEST | D_BACKTEST | 13 | test_depends |
| 74 | D_DATA | D_GOVERNANCE | 13 | config_depends,test_depends |
| 75 | D_GOVERNANCE | D_INFRASTRUCTURE | 13 | import_depends |
| 76 | D_GOVERNANCE | D_INFRA_A2A | 13 | config_depends,import_depends |
| 77 | D_GOV_AUDIT | D_SECURITY | 13 | import_depends,test_depends |
| 78 | D_INTEGRATION_GATEWAY | D_INTEGRATION | 13 | import_depends |
| 79 | D_INTELLIGENCE | D_INFRA_RUNTIME | 13 | import_depends,test_depends |
| 80 | D_INTELLIGENCE | D_OPS | 13 | test_depends |
| 81 | D_SHARED | D_GOV_OPS_RESILIENCE | 13 | test_depends |
| 82 | D_AUTONOMY_CORE | D_FBL_DIAGNOSERS | 12 | test_depends |
| 83 | D_AUTONOMY_CORE | D_GOV_OPS_RESILIENCE | 12 | test_depends |
| 84 | D_SHARED | D_INFRASTRUCTURE | 12 | config_depends,import_depends |
| 85 | D_GOV_OPS_RESILIENCE | D_SHARED | 12 | import_depends |
| 86 | D_SECURITY_LLM | D_FEEDBACK_LOOP | 12 | test_depends |
| 87 | D_FUNDAMENTAL_SIGNAL | D_TRADING | 11 | import_depends |
| 88 | D_GOV_REPAIR | D_INFRA_RUNTIME | 11 | import_depends |
| 89 | D_GOVERNANCE | D_GOV_DRIFT | 11 | import_depends,test_depends |
| 90 | D_GOV_SCRIPTS | D_GOVERNANCE | 11 | config_depends,import_depends,test_depends |
| 91 | D_EX_CORE | D_GOVERNANCE | 11 | import_depends |
| 92 | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | 10 | import_depends |
| 93 | D_COMPLIANCE | D_GOV_AUDIT | 10 | import_depends |
| 94 | D_INFRA_A2A | D_SHARED | 10 | import_depends |
| 95 | D_GOV_AUDIT | D_FBL_DETECTORS | 10 | test_depends |
| 96 | D_INFRA_TELEMETRY | D_INFRA_RUNTIME | 10 | import_depends |
| 97 | D_AUTONOMY_CORE | D_ORCHESTRATOR | 9 | test_depends |
| 98 | D_REPORTING | D_INFRASTRUCTURE | 9 | import_depends |
| 99 | D_AUTONOMY_CORE | D_SECURITY | 8 | import_depends,test_depends |
| 100 | D_GOV_OPS_RESILIENCE | D_INTEGRATION | 8 | import_depends |
| 101 | D_GOV_AUDIT | D_FBL_VERIFICATION | 8 | test_depends |
| 102 | D_GOV_AUDIT | D_INFRA_RUNTIME | 8 | test_depends |
| 103 | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | 8 | import_depends,test_depends |
| 104 | D_GOV_KB | D_GOV_RULE | 8 | import_depends |
| 105 | D_ORCHESTRATOR | D_INTEGRATION | 8 | import_depends |
| 106 | D_GOV_DRIFT | D_GOVERNANCE | 8 | import_depends |
| 107 | D_INFRA_RUNTIME | D_SECURITY | 8 | import_depends,test_depends |
| 108 | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | 7 | import_depends,test_depends |
| 109 | D_GOVERNANCE | D_FRONTEND | 7 | test_depends |
| 110 | D_SECURITY | D_SECURITY_LLM | 7 | config_depends,import_depends |
| 111 | D_INFRA_A2A | D_GOVERNANCE | 7 | import_depends,test_depends |
| 112 | D_GOV_REPAIR | D_INFRASTRUCTURE | 7 | import_depends |
| 113 | D_INFRA_A2A | D_GOV_AUDIT | 7 | test_depends |
| 114 | D_GOV_OPS_RESILIENCE | D_OPS | 7 | import_depends |
| 115 | D_AUTONOMY_CORE | D_FBL_DETECTORS | 7 | test_depends |
| 116 | D_AUTONOMY_CORE | D_GOVERNANCE | 7 | test_depends |
| 117 | D_COMPLIANCE | D_SECURITY | 7 | import_depends |
| 118 | D_GOVERNANCE | D_GOV_KB | 7 | config_depends,import_depends,test_depends |
| 119 | D_GOV_CODE_QUALITY | D_SHARED | 7 | import_depends |
| 120 | D_GOV_ENFORCEMENT | D_SECURITY | 6 | import_depends,test_depends |
| 121 | D_GOV_ENFORCEMENT | D_GOV_AUDIT | 6 | import_depends |
| 122 | D_FRONTEND | D_GOVERNANCE | 6 | import_depends |
| 123 | D_TRADING | D_INFRASTRUCTURE | 6 | import_depends,test_depends |
| 124 | D_GOV_ENFORCEMENT | D_GOV_DRIFT | 6 | import_depends,test_depends |
| 125 | D_GOV_DRIFT | D_GOV_AUDIT | 6 | import_depends |
| 126 | D_INTELLIGENCE | D_ML_TRAIN | 6 | config_depends,import_depends |
| 127 | D_EX_CORE | D_AUTONOMY_CORE | 6 | test_depends |
| 128 | D_INFRA_RUNTIME | D_GOV_AUDIT | 6 | import_depends,test_depends |
| 129 | D_INFRA_RUNTIME | D_INTELLIGENCE | 5 | import_depends |
| 130 | D_SECURITY_LLM | D_INTEGRATION | 5 | test_depends |
| 131 | D_INFRA_RUNTIME | D_TRADING | 5 | import_depends,test_depends |
| 132 | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | 5 | import_depends |
| 133 | D_GOV_REPAIR | D_GOV_ENFORCEMENT | 5 | import_depends |
| 134 | D_INFRA_RECOVERY | D_ORCHESTRATOR | 5 | test_depends |
| 135 | D_KNOWLEDGE | D_FEEDBACK_LOOP | 5 | test_depends |
| 136 | D_INTELLIGENCE | D_GOV_DRIFT | 5 | test_depends |
| 137 | D_GOV_RULE | D_INTEGRATION | 5 | import_depends |
| 138 | D_INTEGRATION | D_GOVERNANCE | 5 | config_depends,import_depends |
| 139 | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | 5 | import_depends,test_depends |
| 140 | D_AUTONOMY_CORE | D_GOV_AUDIT | 5 | import_depends,test_depends |
| 141 | D_GOV_REPAIR | D_GOV_DRIFT | 5 | import_depends |
| 142 | D_GOV_DRIFT | D_SECURITY | 5 | import_depends |
| 143 | D_INFRA_RECOVERY | D_GOV_AUDIT | 5 | import_depends |
| 144 | D_INFRA_RUNTIME | D_INFRA_RECOVERY | 5 | import_depends,test_depends |
| 145 | D_GOV_CODE_QUALITY | D_GOVERNANCE | 5 | import_depends |
| 146 | D_KNOWLEDGE | D_INTELLIGENCE | 4 | test_depends |
| 147 | D_OPS | D_SHARED | 4 | import_depends |
| 148 | D_INTELLIGENCE | D_FEEDBACK_LOOP | 4 | test_depends |
| 149 | D_GOV_OPS_RESILIENCE | D_SECURITY | 4 | import_depends |
| 150 | D_INFRASTRUCTURE | D_INFRA_RUNTIME | 4 | test_depends |
| 151 | D_AUTONOMY_CORE | D_INTELLIGENCE | 4 | import_depends,test_depends |
| 152 | D_INFRA_RUNTIME | D_AUTONOMY_CORE | 4 | config_depends,import_depends,test_depends |
| 153 | D_INFRA_RUNTIME | D_GOV_RULE | 4 | import_depends,test_depends |
| 154 | D_GOV_REPAIR | D_GOV_CODE_QUALITY | 4 | import_depends |
| 155 | D_INTEGRATION | D_GOV_AUDIT | 4 | import_depends,test_depends |
| 156 | D_FEEDBACK_LOOP | D_GOVERNANCE | 4 | import_depends |
| 157 | D_GOV_KB | D_INTEGRATION | 4 | import_depends |
| 158 | D_GOV_AUDIT | D_GOV_RULE | 4 | import_depends,test_depends |
| 159 | D_RISK | D_TRADING | 4 | import_depends,test_depends |
| 160 | D_EX_CORE | D_INFRASTRUCTURE | 4 | import_depends |
| 161 | D_SECURITY | D_GOV_AUDIT | 4 | import_depends |
| 162 | D_GOV_AUDIT | D_INFRA_A2A | 4 | test_depends |
| 163 | D_INTELLIGENCE | D_INTEGRATION | 4 | import_depends,test_depends |
| 164 | D_SECURITY | D_GOV_RULE | 4 | import_depends |
| 165 | D_GOV_REPAIR | D_OPS | 4 | import_depends |
| 166 | D_INTEGRATION | D_OPS | 4 | import_depends |
| 167 | D_SHARED | D_FEEDBACK_LOOP | 4 | import_depends,test_depends |
| 168 | D_SHARED | D_GOV_AUDIT | 4 | import_depends,test_depends |
| 169 | D_SHARED | D_GOV_DRIFT | 4 | test_depends |
| 170 | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | 4 | import_depends |
| 171 | D_SHARED | D_SECURITY | 4 | test_depends |
| 172 | D_KNOWLEDGE | D_GOV_RULE | 4 | test_depends |
| 173 | D_GOV_AUDIT | D_INTELLIGENCE | 4 | test_depends |
| 174 | D_INTELLIGENCE | D_FBL_DIAGNOSERS | 4 | test_depends |
| 175 | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | 4 | import_depends |
| 176 | D_TRADING | D_GOVERNANCE | 4 | import_depends |
| 177 | D_INTELLIGENCE | D_GOV_KB | 3 | import_depends |
| 178 | D_GOV_ENFORCEMENT | D_GOVERNANCE | 3 | import_depends,test_depends |
| 179 | D_FRONTEND | D_SHARED | 3 | import_depends |
| 180 | D_FEEDBACK_LOOP | D_GOV_AUDIT | 3 | test_depends |
| 181 | D_SHARED | D_DATA | 3 | test_depends |
| 182 | D_SHARED | D_FBL_DETECTORS | 3 | test_depends |
| 183 | D_ORCHESTRATOR | D_GOVERNANCE | 3 | import_depends |
| 184 | D_SHARED | D_FBL_VERIFICATION | 3 | test_depends |
| 185 | D_ML_TRAIN | D_SHARED | 3 | import_depends |
| 186 | D_INTEGRATION | D_SECURITY | 3 | import_depends |
| 187 | D_INFRA_RUNTIME | D_GOV_DRIFT | 3 | import_depends,test_depends |
| 188 | D_FRONTEND | D_FBL_DETECTORS | 3 | test_depends |
| 189 | D_SHARED | D_GOV_CODE_QUALITY | 3 | test_depends |
| 190 | D_INFRASTRUCTURE | D_SECURITY | 3 | test_depends |
| 191 | D_INFRA_RUNTIME | D_FBL_DETECTORS | 3 | test_depends |
| 192 | D_AUDITTEST | D_GOVERNANCE | 3 | test_depends |
| 193 | D_SHARED | D_GOV_RULE | 3 | import_depends,test_depends |
| 194 | D_GOV_ENFORCEMENT | D_FBL_DIAGNOSERS | 3 | test_depends |
| 195 | D_GOV_AUDIT | D_INFRA_RECOVERY | 3 | test_depends |
| 196 | D_INFRA_RECOVERY | D_SECURITY | 3 | import_depends,test_depends |
| 197 | D_GOV_ENFORCEMENT | D_FBL_DETECTORS | 3 | test_depends |
| 198 | D_GOV_OPS_RESILIENCE | D_GOV_KB | 3 | import_depends |
| 199 | D_GOV_AUDIT | D_INTEGRATION | 3 | import_depends |
| 200 | D_INTELLIGENCE | D_AUTONOMY_CORE | 3 | import_depends,test_depends |
| 201 | D_INFRA_RECOVERY | D_INFRA_RUNTIME | 3 | import_depends,test_depends |
| 202 | D_AUTONOMY_CORE | D_GOV_RULE | 3 | import_depends,test_depends |
| 203 | D_FEEDBACK_LOOP | D_INTEGRATION | 3 | import_depends |
| 204 | D_INFRASTRUCTURE | D_ORCHESTRATOR | 3 | test_depends |
| 205 | D_FBL_DETECTORS | D_FEEDBACK_LOOP | 3 | import_depends |
| 206 | D_GOV_AUDIT | D_TRADING | 3 | test_depends |
| 207 | D_INFRA_RECOVERY | D_GOV_DRIFT | 3 | test_depends |
| 208 | D_INTELLIGENCE | D_BACKTEST | 3 | import_depends |
| 209 | D_SIGLEGACY | D_TRADING | 3 | import_depends |
| 210 | D_GOVERNANCE | D_RISK | 3 | import_depends |
| 211 | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | 3 | import_depends |
| 212 | D_TRADING | D_EX_CORE | 3 | test_depends |
| 213 | D_ORCHESTRATOR | D_INFRA_RUNTIME | 3 | import_depends |
| 214 | D_BACKTEST | D_GOVERNANCE | 3 | import_depends |
| 215 | D_INTELLIGENCE | D_GOVERNANCE | 3 | import_depends,test_depends |
| 216 | D_TRADING | D_GOV_ENFORCEMENT | 3 | import_depends,test_depends |
| 217 | D_SECURITY | D_INFRA_RUNTIME | 3 | import_depends |
| 218 | D_SECURITY | D_GOVERNANCE | 3 | import_depends |
| 219 | D_INTELLIGENCE | D_GOV_RULE | 3 | import_depends,test_depends |
| 220 | D_RISK | D_INFRASTRUCTURE | 3 | import_depends,test_depends |
| 221 | D_INTEGRATION | D_INTELLIGENCE | 3 | import_depends |
| 222 | D_INTEGRATION | D_GOV_KB | 3 | import_depends |
| 223 | D_EX_CORE | D_TRADING | 3 | import_depends |
| 224 | D_INTEGRATION | D_AUTONOMY_CORE | 3 | import_depends |
| 225 | D_GOV_AUDIT | D_AUTONOMY_CORE | 3 | test_depends |
| 226 | D_COMPLIANCE | D_GOVERNANCE | 3 | import_depends |
| 227 | D_AUTONOMY_CORE | D_INFRA_RECOVERY | 3 | test_depends |
| 228 | D_PF_CORE | D_GOVERNANCE | 3 | import_depends |
| 229 | D_GOVERNANCE | D_FBL_DIAGNOSERS | 2 | test_depends |
| 230 | D_GOV_ENFORCEMENT | D_INTEGRATION | 2 | import_depends,test_depends |
| 231 | D_GOV_ENFORCEMENT | D_OPS | 2 | import_depends |
| 232 | D_GOV_KB | D_GOVERNANCE | 2 | import_depends |
| 233 | D_INTELLIGENCE | D_SECURITY | 2 | test_depends |
| 234 | D_EX_CORE | D_BACKTEST | 2 | import_depends |
| 235 | D_KNOWLEDGE | D_FBL_DIAGNOSERS | 2 | test_depends |
| 236 | D_GOV_OPS_RESILIENCE | D_GOV_RULE | 2 | import_depends |
| 237 | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | 2 | import_depends |
| 238 | D_KNOWLEDGE | D_ORCHESTRATOR | 2 | test_depends |
| 239 | D_ML_TRAIN | D_TRADING | 2 | import_depends |
| 240 | D_OPS | D_GOV_DRIFT | 2 | import_depends |
| 241 | D_OPS | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 242 | D_ORCHESTRATOR | D_AUTONOMY_CORE | 2 | import_depends |
| 243 | D_ORCHESTRATOR | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 244 | D_GOVERNANCE | D_DATA | 2 | import_depends |
| 245 | D_ORCHESTRATOR | D_SECURITY | 2 | import_depends |
| 246 | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 247 | D_PF_ALLOC | D_SHARED | 2 | import_depends |
| 248 | D_RISK | D_GOV_CODE_QUALITY | 2 | test_depends |
| 249 | D_RISK | D_SHARED | 2 | import_depends,test_depends |
| 250 | D_SECURITY | D_FEEDBACK_LOOP | 2 | import_depends,test_depends |
| 251 | D_SECURITY | D_GOV_OPS_RESILIENCE | 2 | import_depends,test_depends |
| 252 | D_SECURITY | D_INTEGRATION | 2 | import_depends |
| 253 | D_GOV_REPAIR | D_INFRA_RECOVERY | 2 | import_depends |
| 254 | D_SECURITY_LLM | D_FBL_DIAGNOSERS | 2 | test_depends |
| 255 | D_GOV_REPAIR | D_SHARED | 2 | import_depends |
| 256 | D_GOV_RULE | D_GOVERNANCE | 2 | import_depends |
| 257 | D_GOV_RULE | D_GOV_AUDIT | 2 | import_depends |
| 258 | D_GOV_RULE | D_GOV_DRIFT | 2 | import_depends |
| 259 | D_SHARED | D_FBL_DIAGNOSERS | 2 | test_depends |
| 260 | D_GOV_RULE | D_GOV_ENFORCEMENT | 2 | config_depends,import_depends |
| 261 | D_SHARED | D_GOV_ENFORCEMENT | 2 | test_depends |
| 262 | D_SHARED | D_INTEGRATION | 2 | test_depends |
| 263 | D_SHARED | D_ML_TRAIN | 2 | import_depends |
| 264 | D_SHARED | D_ORCHESTRATOR | 2 | test_depends |
| 265 | D_BACKTEST | D_SHARED | 2 | import_depends |
| 266 | D_SHARED | D_SIMULATION | 2 | import_depends,test_depends |
| 267 | D_SIGLEGACY | D_SHARED | 2 | import_depends |
| 268 | D_SIGQC | D_TRADING | 2 | import_depends |
| 269 | D_GOV_SCRIPTS | D_FBL_VERIFICATION | 2 | test_depends |
| 270 | D_GOV_AUDIT | D_REPORTING | 2 | import_depends |
| 271 | D_FRONTEND | D_BACKTEST | 2 | import,import_depends |
| 272 | D_FRONTEND | D_EX_CORE | 2 | import_depends |
| 273 | D_FRONTEND | D_FBL_DIAGNOSERS | 2 | test_depends |
| 274 | D_GOV_SCRIPTS | D_ORCHESTRATOR | 2 | test_depends |
| 275 | D_GOV_SCRIPTS | D_SECURITY | 2 | test_depends |
| 276 | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | 2 | import_depends |
| 277 | D_INFRASTRUCTURE | D_FBL_VERIFICATION | 2 | test_depends |
| 278 | D_INFRASTRUCTURE | D_FEEDBACK_LOOP | 2 | test_depends |
| 279 | D_INFRASTRUCTURE | D_GOV_CODE_QUALITY | 2 | test_depends |
| 280 | D_INFRASTRUCTURE | D_GOV_DRIFT | 2 | test_depends |
| 281 | D_AUTONOMY_PERM | D_INFRA_RUNTIME | 2 | test_depends |
| 282 | D_GOV_DOCS | D_GOV_DRIFT | 2 | runtime |
| 283 | D_GOV_DRIFT | D_GOV_DOCS | 2 | runtime |
| 284 | D_FEEDBACK_LOOP | D_GOV_DRIFT | 2 | import_depends |
| 285 | D_INFRA_RECOVERY | D_FBL_VERIFICATION | 2 | test_depends |
| 286 | D_GOV_DRIFT | D_INTEGRATION | 2 | import_depends |
| 287 | D_EX_CORE | D_SHARED | 2 | import_depends |
| 288 | D_INFRA_RUNTIME | D_FBL_DIAGNOSERS | 2 | test_depends |
| 289 | D_AUTONOMY_PERM | D_GOVERNANCE | 2 | config_depends |
| 290 | D_GOV_ENFORCEMENT | D_FEEDBACK_LOOP | 2 | test_depends |
| 291 | D_DATA | D_FBL_VERIFICATION | 2 | test_depends |
| 292 | D_INFRA_TELEMETRY | D_SHARED | 2 | import_depends |
| 293 | D_INTEGRATION | D_FBL_DETECTORS | 2 | test_depends |
| 294 | D_INTEGRATION | D_GOV_RULE | 2 | import_depends |
| 295 | D_INTEGRATION | D_INFRA_RECOVERY | 2 | import_depends,test_depends |
| 296 | D_AUTONOMY_CORE | D_GOV_CODE_QUALITY | 1 | test_depends |
| 297 | D_FRONTEND | D_TRADING | 1 | import_depends |
| 298 | D_FUNDAMENTAL_SIGNAL | D_SIGLEGACY | 1 | config_depends |
| 299 | D_GOVERNANCE | D_EX_CORE | 1 | import_depends |
| 300 | D_GOVERNANCE | D_FBL_DETECTORS | 1 | test_depends |
| 301 | D_GOVERNANCE | D_FBL_VERIFICATION | 1 | test_depends |
| 302 | D_GOVERNANCE | D_FEEDBACK_LOOP | 1 | test_depends |
| 303 | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | 1 | import_depends |
| 304 | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | 1 | import_depends |
| 305 | D_AUTONOMY_CORE | D_EX_CORE | 1 | test_depends |
| 306 | D_FBL_VERIFICATION | D_SECURITY | 1 | import_depends |
| 307 | D_FBL_VERIFICATION | D_GOV_AUDIT | 1 | import_depends |
| 308 | D_FBL_DIAGNOSERS | D_SHARED | 1 | import_depends |
| 309 | D_GOVERNANCE | D_INTEGRATION_GATEWAY | 1 | import_depends |
| 310 | D_FACTOR | D_SIGLEGACY | 1 | import_depends |
| 311 | D_GOVERNANCE | D_ORCHESTRATOR | 1 | import_depends |
| 312 | D_GOVERNANCE | D_REPORTING | 1 | import_depends |
| 313 | D_GOVERNANCE | D_SECURITY_LLM | 1 | import_depends |
| 314 | D_GOVERNANCE | D_SIGLEGACY | 1 | import_depends |
| 315 | D_GOVERNANCE | D_SIMULATION | 1 | import_depends |
| 316 | D_EX_CORE | D_INFRA_RECOVERY | 1 | test_depends |
| 317 | D_GOV_AUDIT | D_GOV_CODE_QUALITY | 1 | test_depends |
| 318 | D_GOV_AUDIT | D_GOV_DOCS | 1 | runtime |
| 319 | D_GOV_AUDIT | D_GOV_ENFORCEMENT | 1 | test_depends |
| 320 | D_DATA | D_INTEGRATION | 1 | test_depends |
| 321 | D_GOV_AUDIT | D_ORCHESTRATOR | 1 | test_depends |
| 322 | D_TRADING | D_INTEGRATION | 1 | test_depends |
| 323 | D_DATA | D_GOV_RULE | 1 | test_depends |
| 324 | D_GOV_CODE_QUALITY | D_AUTONOMY_CORE | 1 | import_depends |
| 325 | D_DATA | D_GOV_REPAIR | 1 | test_depends |
| 326 | D_GOV_CODE_QUALITY | D_GOV_SCRIPTS | 1 | config_depends |
| 327 | D_GOV_CODE_QUALITY | D_INFRA_RUNTIME | 1 | import_depends |
| 328 | D_GOV_DOCS | D_INFRA_RUNTIME | 1 | runtime |
| 329 | D_GOV_DRIFT | D_INFRA_RECOVERY | 1 | import_depends |
| 330 | D_DATA | D_GOV_ENFORCEMENT | 1 | import_depends |
| 331 | D_DATA | D_FEEDBACK_LOOP | 1 | test_depends |
| 332 | D_GOV_ENFORCEMENT | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 333 | D_DATA | D_FBL_DIAGNOSERS | 1 | test_depends |
| 334 | D_GOV_ENFORCEMENT | D_INFRASTRUCTURE | 1 | import_depends |
| 335 | D_GOV_ENFORCEMENT | D_ORCHESTRATOR | 1 | test_depends |
| 336 | D_COMPLIANCE | D_INFRA_RUNTIME | 1 | import_depends |
| 337 | D_GOV_OPS_RESILIENCE | D_FACTOR | 1 | import_depends |
| 338 | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | 1 | import_depends |
| 339 | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 340 | D_GOV_OPS_RESILIENCE | D_INFRA_RUNTIME | 1 | import_depends |
| 341 | D_GOV_REPAIR | D_AUTONOMY_CORE | 1 | import_depends |
| 342 | D_GOV_REPAIR | D_FACTOR | 1 | import_depends |
| 343 | D_COMPLIANCE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 344 | D_GOV_REPAIR | D_GOV_KB | 1 | import_depends |
| 345 | D_GOV_REPAIR | D_GOV_RULE | 1 | import_depends |
| 346 | D_GOV_REPAIR | D_INFRA_A2A | 1 | import_depends |
| 347 | D_GOV_RULE | D_GOV_SCRIPTS | 1 | config_depends |
| 348 | D_GOV_RULE | D_INFRA_RECOVERY | 1 | import_depends |
| 349 | D_GOV_RULE | D_INFRA_RUNTIME | 1 | import_depends |
| 350 | D_GOV_SCRIPTS | D_AUTONOMY_CORE | 1 | test_depends |
| 351 | D_GOV_SCRIPTS | D_FBL_DETECTORS | 1 | test_depends |
| 352 | D_GOV_SCRIPTS | D_FEEDBACK_LOOP | 1 | test_depends |
| 353 | D_GOV_SCRIPTS | D_GOV_DRIFT | 1 | test_depends |
| 354 | D_GOV_SCRIPTS | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 355 | D_BACKTEST | D_INFRA_RUNTIME | 1 | import_depends |
| 356 | D_GOV_SCRIPTS | D_INFRA_RECOVERY | 1 | test_depends |
| 357 | D_GOV_SCRIPTS | D_INFRA_RUNTIME | 1 | test_depends |
| 358 | D_INFRASTRUCTURE | D_AUTONOMY_CORE | 1 | test_depends |
| 359 | D_INFRASTRUCTURE | D_FBL_DETECTORS | 1 | test_depends |
| 360 | D_INFRASTRUCTURE | D_GOVERNANCE | 1 | test_depends |
| 361 | D_INFRASTRUCTURE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 362 | D_INFRA_A2A | D_FEEDBACK_LOOP | 1 | test_depends |
| 363 | D_INFRA_A2A | D_GOV_DRIFT | 1 | test_depends |
| 364 | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 365 | D_INFRA_A2A | D_INFRA_RUNTIME | 1 | import_depends |
| 366 | D_INFRA_A2A | D_SECURITY | 1 | test_depends |
| 367 | D_INFRA_RECOVERY | D_FBL_DETECTORS | 1 | test_depends |
| 368 | D_INFRA_RECOVERY | D_GOVERNANCE | 1 | import_depends |
| 369 | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | 1 | test_depends |
| 370 | D_INFRA_RECOVERY | D_GOV_OPS_RESILIENCE | 1 | import_depends |
| 371 | D_INFRA_RECOVERY | D_POSITION | 1 | test_depends |
| 372 | D_AUTONOMY_PERM | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 373 | D_INFRA_RUNTIME | D_GOV_REPAIR | 1 | test_depends |
| 374 | D_INFRA_RUNTIME | D_INFRASTRUCTURE | 1 | import_depends |
| 375 | D_AUTONOMY_CORE | D_TRADING | 1 | test_depends |
| 376 | D_INFRA_RUNTIME | D_OPS | 1 | import_depends |
| 377 | D_INFRA_RUNTIME | D_ORCHESTRATOR | 1 | import_depends |
| 378 | D_INTEGRATION | D_FEEDBACK_LOOP | 1 | test_depends |
| 379 | D_INTEGRATION | D_INFRASTRUCTURE | 1 | import_depends |
| 380 | D_AUTONOMY_CORE | D_OPS | 1 | test_depends |
| 381 | D_INTEGRATION | D_TRADING | 1 | import_depends |
| 382 | D_INTEGRATION_GATEWAY | D_GOVERNANCE | 1 | import_depends |
| 383 | D_AUDITTEST | D_TRADING | 1 | test_depends |
| 384 | D_INTELLIGENCE | D_EX_CORE | 1 | test_depends |
| 385 | D_INTELLIGENCE | D_FBL_DETECTORS | 1 | test_depends |
| 386 | D_INTELLIGENCE | D_FBL_VERIFICATION | 1 | test_depends |
| 387 | D_INTELLIGENCE | D_FRONTEND | 1 | test_depends |
| 388 | D_INTELLIGENCE | D_GOV_CODE_QUALITY | 1 | test_depends |
| 389 | D_INTELLIGENCE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 390 | D_TRADING | D_PF_CORE | 1 | test_depends |
| 391 | D_TRADING | D_REPORTING | 1 | test_depends |
| 392 | D_INTELLIGENCE | D_ORCHESTRATOR | 1 | test_depends |
| 393 | D_INTELLIGENCE | D_SIGLEGACY | 1 | test_depends |
| 394 | D_INTELLIGENCE | D_TRADING | 1 | import_depends |
| 395 | D_KNOWLEDGE | D_AUTONOMY_CORE | 1 | test_depends |
| 396 | D_KNOWLEDGE | D_GOV_AUDIT | 1 | test_depends |
| 397 | D_KNOWLEDGE | D_GOV_DRIFT | 1 | test_depends |
| 398 | D_KNOWLEDGE | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 399 | D_KNOWLEDGE | D_INFRA_RUNTIME | 1 | runtime |
| 400 | D_MKT_DATA | D_INFRASTRUCTURE | 1 | import_depends |
| 401 | D_ML_TRAIN | D_INTELLIGENCE | 1 | config_depends |
| 402 | D_OPS | D_GOVERNANCE | 1 | import_depends |
| 403 | D_OPS | D_INFRA_RECOVERY | 1 | import_depends |
| 404 | D_ORCHESTRATOR | D_FEEDBACK_LOOP | 1 | import_depends |
| 405 | D_ORCHESTRATOR | D_GOV_DRIFT | 1 | import_depends |
| 406 | D_ORCHESTRATOR | D_INFRASTRUCTURE | 1 | import_depends |
| 407 | D_AUTONOMY_CORE | D_GOV_REPAIR | 1 | test_depends |
| 408 | D_PF_ALLOC | D_GOVERNANCE | 1 | import_depends |
| 409 | D_PF_ALLOC | D_INFRASTRUCTURE | 1 | import_depends |
| 410 | D_PF_CORE | D_GOV_ENFORCEMENT | 1 | import_depends |
| 411 | D_PF_CORE | D_PF_ALLOC | 1 | import_depends |
| 412 | D_RISK | D_FBL_DETECTORS | 1 | test_depends |
| 413 | D_RISK | D_GOVERNANCE | 1 | test_depends |
| 414 | D_RISK | D_GOV_RULE | 1 | test_depends |
| 415 | D_RISK | D_ORCHESTRATOR | 1 | test_depends |
| 416 | D_AUTONOMY_CORE | D_GOV_KB | 1 | import_depends |
| 417 | D_SECURITY | D_GOV_KB | 1 | test_depends |
| 418 | D_SECURITY | D_INTELLIGENCE | 1 | import_depends |
| 419 | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | 1 | test_depends |
| 420 | D_SECURITY_LLM | D_FBL_VERIFICATION | 1 | test_depends |
| 421 | D_SECURITY_LLM | D_GOV_OPS_RESILIENCE | 1 | test_depends |
| 422 | D_SECURITY_LLM | D_GOV_RULE | 1 | test_depends |
| 423 | D_SECURITY_LLM | D_INFRA_A2A | 1 | test_depends |
| 424 | D_AUTONOMY_CORE | D_GOV_DRIFT | 1 | test_depends |
| 425 | D_SECURITY_LLM | D_ORCHESTRATOR | 1 | test_depends |
| 426 | D_SHARED | D_FUNDAMENTAL_SIGNAL | 1 | test_depends |
| 427 | D_SHARED | D_INFRA_A2A | 1 | test_depends |
| 428 | D_SHARED | D_INFRA_RECOVERY | 1 | test_depends |
| 429 | D_SHARED | D_INTELLIGENCE | 1 | test_depends |
| 430 | D_SHARED | D_OPS | 1 | test_depends |
| 431 | D_SHARED | D_POSITION | 1 | test_depends |
| 432 | D_SIGLEGACY | D_FACTOR | 1 | import_depends |
| 433 | D_SIMULATION | D_INFRASTRUCTURE | 1 | import_depends |
| 434 | D_TRADING | D_FEEDBACK_LOOP | 1 | test_depends |
| 435 | D_TRADING | D_GOV_AUDIT | 1 | import_depends |
| 436 | D_FEEDBACK_LOOP | D_SECURITY | 1 | import_depends |
| 437 | D_FEEDBACK_LOOP | D_ORCHESTRATOR | 1 | import_depends |
