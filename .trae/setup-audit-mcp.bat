@echo off
REM setup-audit-mcp.bat - MCP包装器配置向导
REM 解决"MCP error -32000: Connection closed"错误

echo ========================================
echo    MCP包装器配置向导
echo    解决"Connection closed"错误
echo ========================================
echo.

echo 步骤1: 验证审计工具已安装
echo 正在运行验证脚本...
powershell -ExecutionPolicy Bypass -File "d:\ZephyrAlpha\.trae\skills\audit-sentinel\verify-mcp-tools.ps1"

echo.
echo 步骤2: 备份当前MCP配置
echo 请手动备份Trae MCP配置文件:
echo 1. 打开目录: C:\Users\fanzi\AppData\Roaming\Trae CN\User\
echo 2. 复制文件: mcp.json -> mcp.json.backup
echo.
pause

echo.
echo 步骤3: 替换MCP配置文件
echo 请打开文件: C:\Users\fanzi\AppData\Roaming\Trae CN\User\mcp.json
echo 全选删除所有内容，然后复制下方配置并粘贴保存:
echo.
echo ===== 开始复制 =====
type "d:\ZephyrAlpha\.trae\mcp-audit-wrapper-basic.json"
echo ===== 结束复制 =====
echo.
pause

echo.
echo 步骤4: 重启Trae智能体
echo 1. 完全关闭Trae应用程序
echo 2. 重新打开Trae
echo 3. 等待MCP服务器初始化
echo.
pause

echo.
echo 步骤5: 验证配置生效
echo 在Trae智能体聊天界面测试:
echo 1. 请调用audit-tools-wrapper工具列表
echo 2. 请进行代码安全扫描
echo.
echo 配置完成！
echo.
pause
