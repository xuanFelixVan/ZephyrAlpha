# Miniconda环境配置脚本
# 用于修复PATH并创建Python 3.12环境

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Miniconda环境配置脚本" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# 1. 检查Miniconda安装
Write-Host "1. 检查Miniconda安装" -ForegroundColor Yellow
$miniconda_path = "E:\Miniconda"
$conda_exe = "$miniconda_path\Scripts\conda.exe"

if (Test-Path $conda_exe) {
    Write-Host "   ✅ Miniconda安装位置: $miniconda_path" -ForegroundColor Green
    Write-Host "   ✅ conda.exe存在: $conda_exe" -ForegroundColor Green
} else {
    Write-Host "   ❌ 找不到conda.exe，请检查安装" -ForegroundColor Red
    exit 1
}

# 2. 添加Miniconda到PATH（当前会话）
Write-Host "`n2. 配置PATH环境变量（当前会话）" -ForegroundColor Yellow
$env:Path = "E:\Miniconda;E:\Miniconda\Scripts;E:\Miniconda\Library\bin;$env:Path"
Write-Host "   ✅ 已将Miniconda添加到当前会话的PATH" -ForegroundColor Green

# 3. 验证conda命令
Write-Host "`n3. 验证conda命令" -ForegroundColor Yellow
try {
    $conda_version = & $conda_exe --version
    Write-Host "   ✅ conda版本: $conda_version" -ForegroundColor Green
} catch {
    Write-Host "   ❌ conda命令验证失败: $_" -ForegroundColor Red
    exit 1
}

# 4. 检查当前Python版本
Write-Host "`n4. 检查当前Python版本" -ForegroundColor Yellow
try {
    $python_version = & "$miniconda_path\python.exe" --version
    Write-Host "   ✅ Miniconda Python版本: $python_version" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python检查失败" -ForegroundColor Red
}

# 5. 创建QMT专用Python 3.12环境
Write-Host "`n5. 创建QMT专用Python 3.12环境" -ForegroundColor Yellow
$env_name = "qmt"

# 检查环境是否已存在
Write-Host "   检查是否已存在环境 '$env_name'..." -ForegroundColor Gray
$envs = & $conda_exe env list --json | ConvertFrom-Json
$env_exists = $envs.envs | Where-Object { $_ -like "*$env_name*" }

if ($env_exists) {
    Write-Host "   ⚠️  环境 '$env_name' 已存在" -ForegroundColor Yellow
    $choice = Read-Host "   是否重新创建？(y/N)"
    if ($choice -eq 'y') {
        Write-Host "   删除现有环境..." -ForegroundColor Gray
        & $conda_exe remove --name $env_name --all --yes
    } else {
        Write-Host "   跳过环境创建" -ForegroundColor Gray
        goto ACTIVATE_ENV
    }
}

# 创建新环境
Write-Host "   正在创建Python 3.12环境 '$env_name'..." -ForegroundColor Gray
& $conda_exe create --name $env_name python=3.12 --yes

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ 环境 '$env_name' 创建成功" -ForegroundColor Green
} else {
    Write-Host "   ❌ 环境创建失败" -ForegroundColor Red
    exit 1
}

# 6. 激活环境
ACTIVATE_ENV:
Write-Host "`n6. 激活环境" -ForegroundColor Yellow
Write-Host "   激活命令: conda activate $env_name" -ForegroundColor Gray

# 注意：在脚本中激活环境需要特殊处理
# 这里提供激活命令，用户需要手动运行
Write-Host "`n请在终端中手动运行以下命令：" -ForegroundColor Cyan
Write-Host "   E:\Miniconda\Scripts\activate" -ForegroundColor White
Write-Host "   conda activate $env_name" -ForegroundColor White

# 7. 环境配置完成后的操作
Write-Host "`n7. 后续操作" -ForegroundColor Yellow
Write-Host "   环境激活后，请运行以下命令：" -ForegroundColor Gray
Write-Host "   1. 验证Python版本: python --version" -ForegroundColor White
Write-Host "   2. 安装xtquant: pip install xtquant" -ForegroundColor White
Write-Host "   3. 验证安装: python -c `"import xtquant; print('✅ xtquant安装成功')`"" -ForegroundColor White

# 8. 创建快捷脚本
Write-Host "`n8. 创建快捷脚本" -ForegroundColor Yellow
$script_content = @'
# QMT环境激活脚本
# 将此脚本保存为 activate_qmt.ps1

# 设置Miniconda路径
$miniconda_path = "E:\Miniconda"

# 添加到PATH（如果尚未添加）
$conda_paths = @(
    "$miniconda_path",
    "$miniconda_path\Scripts",
    "$miniconda_path\Library\bin"
)

foreach ($path in $conda_paths) {
    if ($env:Path -notlike "*$path*") {
        $env:Path = "$path;$env:Path"
    }
}

# 激活qmt环境
E:\Miniconda\Scripts\activate qmt

# 验证环境
Write-Host "当前Python版本:" -ForegroundColor Cyan
python --version

Write-Host "`n运行以下命令测试QMT连接:" -ForegroundColor Cyan
Write-Host "python scripts/test_qmt_connection_v4.py" -ForegroundColor White
'@

$script_content | Out-File -FilePath "activate_qmt.ps1" -Encoding UTF8
Write-Host "   ✅ 已创建快捷脚本: activate_qmt.ps1" -ForegroundColor Green
Write-Host "   使用方式: .\activate_qmt.ps1" -ForegroundColor White

# 9. 永久PATH配置建议
Write-Host "`n9. 永久PATH配置建议" -ForegroundColor Yellow
Write-Host "   为了让conda命令永久可用，建议：" -ForegroundColor Gray
Write-Host "   1. 重新运行Miniconda安装程序" -ForegroundColor White
Write-Host "   2. 确保勾选 'Add Miniconda3 to my PATH'" -ForegroundColor White
Write-Host "   3. 或者手动将以下路径添加到系统PATH：" -ForegroundColor White
Write-Host "      E:\Miniconda" -ForegroundColor Cyan
Write-Host "      E:\Miniconda\Scripts" -ForegroundColor Cyan
Write-Host "      E:\Miniconda\Library\bin" -ForegroundColor Cyan

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
