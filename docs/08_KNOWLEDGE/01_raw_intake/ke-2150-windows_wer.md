---
module_id: KE-2058
title: 3.12 #66: Windows WER 禁用
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.12 #66: Windows WER 禁用

3.12 #66: Windows WER 禁用

部署脚本中：`Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Value 1`
