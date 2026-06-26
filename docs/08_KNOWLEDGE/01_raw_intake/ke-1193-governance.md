---
module_id: KE-1107
status: active
title: Cursor 崩溃 / 无响应
category: governance
ttl: permanent
---

# Cursor 崩溃 / 无响应

Cursor 崩溃 / 无响应

1. 确认 Cursor 的本地未保存更改是否还在——重启 Cursor 后通常会自动恢复未保存文件
2. 如果文件已保存但怀疑内容损坏：优先运行 `python scripts/hooks/check_encoding.py` 验证编码完整性
3. **如果 `check_encoding.py` 不存在**（脚本尚未实现）：在 PowerShell 中运行 `Get-Content -Encoding UTF8 <文件路径> -First 5` 手动验证文件前 5 行是否正常，确认无乱码或 BOM 异常
4. 如果重启后文件列表异常（如打开文件丢失）：记录到 Session Log，标注"CURSOR-CRASH-YYYYMMDD"，后续 session 续接时需逐文件验证状态
