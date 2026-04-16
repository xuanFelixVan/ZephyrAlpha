@echo off
REM 清风量化系统 - 缓存清理脚本 (Windows批处理版本)
REM 版本: v1.0
REM 创建日期: 2026-04-01
REM 维护者: Audit Sentinel

echo ============================================
echo  清风量化系统 - 缓存清理工具
echo ============================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 显示帮助信息
if "%1"=="--help" (
    echo 使用方法:
    echo   clean_cache.bat [参数]
    echo.
    echo 参数:
    echo   --dry-run    只显示要清理的文件，不实际删除
    echo   --verbose    显示详细输出
    echo   --all        清理所有缓存（包括可能需要保留的）
    echo   --help       显示此帮助信息
    echo.
    echo 示例:
    echo   clean_cache.bat --dry-run --verbose
    echo   clean_cache.bat
    echo   clean_cache.bat --all
    pause
    exit /b 0
)

REM 执行Python清理脚本
echo 正在执行缓存清理...
echo.

python scripts\clean_cache.py %*

if errorlevel 1 (
    echo.
    echo 清理过程中发生错误，请检查上面的输出信息。
) else (
    echo.
    echo 清理完成！
)

echo.
pause
