# QMT环境激活脚本
# 将此脚本保存为 activate_qmt_env.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QMT Python 3.12环境激活脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查Miniconda路径
$miniconda_path = "E:\Miniconda"
$conda_exe = "$miniconda_path\Scripts\conda.exe"

if (-not (Test-Path $conda_exe)) {
    Write-Host "错误: 找不到conda.exe" -ForegroundColor Red
    Write-Host "请确认Miniconda安装在: $miniconda_path" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Miniconda路径: $miniconda_path" -ForegroundColor Green

# 2. 添加Miniconda到PATH（当前会话）
$env:Path = "$miniconda_path;$miniconda_path\Scripts;$miniconda_path\Library\bin;$env:Path"

# 3. 检查conda版本
try {
    $conda_version = & $conda_exe --version
    Write-Host "✅ conda版本: $conda_version" -ForegroundColor Green
} catch {
    Write-Host "❌ conda命令不可用" -ForegroundColor Red
    exit 1
}

# 4. 激活qmt环境
$env_name = "qmt"
$env_path = "$env:USERPROFILE\.conda\envs\$env_name"

Write-Host "`n激活环境: $env_name" -ForegroundColor Yellow
Write-Host "环境路径: $env_path" -ForegroundColor Gray

if (-not (Test-Path "$env_path\python.exe")) {
    Write-Host "❌ 找不到qmt环境" -ForegroundColor Red
    Write-Host "请先创建环境: conda create --prefix '$env_path' python=3.12 -y" -ForegroundColor Yellow
    exit 1
}

# 激活环境的两种方式：
Write-Host "`n激活环境的方式：" -ForegroundColor Cyan
Write-Host "方式1: 使用conda activate" -ForegroundColor White
Write-Host "    & '$conda_exe' 'activate' '$env_path'" -ForegroundColor Gray
Write-Host "    # 然后验证: python --version" -ForegroundColor Gray
Write-Host ""
Write-Host "方式2: 直接使用环境中的Python" -ForegroundColor White
Write-Host "    & '$env_path\python.exe' --version" -ForegroundColor Gray
Write-Host "    # 例如: & '$env_path\python.exe' scripts/test_qmt_connection.py" -ForegroundColor Gray

# 5. 设置快捷方式
Write-Host "`n快捷命令：" -ForegroundColor Cyan
Write-Host "    # 设置别名" -ForegroundColor White
Write-Host "    Set-Alias qmtpython '$env_path\python.exe'" -ForegroundColor Gray
Write-Host "    Set-Alias qmtpip '$env_path\Scripts\pip.exe'" -ForegroundColor Gray
Write-Host ""
Write-Host "    # 验证环境" -ForegroundColor White
Write-Host "    & '$env_path\python.exe' scripts/verify_xtquant_simple.py" -ForegroundColor Gray

# 6. 测试命令
Write-Host "`n测试命令：" -ForegroundColor Cyan
Write-Host "    # 验证Python版本" -ForegroundColor White
Write-Host "    & '$env_path\python.exe' --version" -ForegroundColor Gray
Write-Host ""
Write-Host "    # 验证xtquant导入" -ForegroundColor White
Write-Host "    & '$env_path\python.exe' -c `"import xtquant; print('xtquant导入成功')`"" -ForegroundColor Gray
Write-Host ""
Write-Host "    # 运行QMT连接测试" -ForegroundColor White
Write-Host "    & '$env_path\python.exe' scripts/test_qmt_connection_v5.py" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "环境激活完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意: 当前会话已添加Miniconda到PATH。" -ForegroundColor Yellow
Write-Host "要永久生效，请重新安装Miniconda并勾选'Add to PATH'选项。" -ForegroundColor Yellow
Write-Host ""
