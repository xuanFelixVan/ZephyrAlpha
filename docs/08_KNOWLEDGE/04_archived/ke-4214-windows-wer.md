---
module_id: KE-4055
title: 3.12 #66: Windows WER 禁用
category: module_blueprint
---

# 3.12 #66: Windows WER 禁用

3.12 #66: Windows WER 禁用

部署脚本中：`Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Value 1`
