---
module_id: KE-module_blu-3_12__66__windows_wer-000
title: 3.12 #66: Windows WER 禁用
category: module_blueprint
---

# 3.12 #66: Windows WER 禁用

3.12 #66: Windows WER 禁用

部署脚本中：`Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Value 1`
