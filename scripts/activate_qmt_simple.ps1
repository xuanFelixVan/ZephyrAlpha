# QMT Environment Activation Script (Simple)
# No Chinese characters to avoid encoding issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QMT Python 3.12 Environment Activation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Miniconda path
$miniconda_path = "E:\Miniconda"
$conda_exe = "$miniconda_path\Scripts\conda.exe"

if (-not (Test-Path $conda_exe)) {
    Write-Host "ERROR: conda.exe not found at: $conda_exe" -ForegroundColor Red
    Write-Host "Please check Miniconda installation path" -ForegroundColor Yellow
    exit 1
}

Write-Host "Miniconda path: $miniconda_path" -ForegroundColor Green

# 2. Add Miniconda to PATH (current session)
Write-Host "Adding Miniconda to PATH..." -ForegroundColor Yellow
$env:Path = "$miniconda_path;$miniconda_path\Scripts;$miniconda_path\Library\bin;$env:Path"

# 3. Check conda version
try {
    $conda_version = & $conda_exe --version
    Write-Host "conda version: $conda_version" -ForegroundColor Green
} catch {
    Write-Host "ERROR: conda command not available" -ForegroundColor Red
    Write-Host "Try restarting your terminal or adding paths manually:" -ForegroundColor Yellow
    Write-Host "  E:\Miniconda" -ForegroundColor White
    Write-Host "  E:\Miniconda\Scripts" -ForegroundColor White
    Write-Host "  E:\Miniconda\Library\bin" -ForegroundColor White
    exit 1
}

# 4. Check QMT environment
$env_name = "qmt"
$env_path = "$env:USERPROFILE\.conda\envs\$env_name"

Write-Host "`nChecking QMT environment: $env_name" -ForegroundColor Yellow
Write-Host "Environment path: $env_path" -ForegroundColor Gray

if (-not (Test-Path "$env_path\python.exe")) {
    Write-Host "ERROR: QMT environment not found!" -ForegroundColor Red
    Write-Host "Please create the environment first:" -ForegroundColor Yellow
    Write-Host "  conda create --prefix `"$env_path`" python=3.12 -y" -ForegroundColor White
    Write-Host "  conda activate $env_name" -ForegroundColor White
    Write-Host "  pip install xtquant pandas numpy" -ForegroundColor White
    exit 1
}

Write-Host "QMT environment found: $env_path" -ForegroundColor Green

# 5. Direct Python path
$qmt_python = "$env_path\python.exe"
$qmt_pip = "$env_path\Scripts\pip.exe"

Write-Host "`nDirect Python path: $qmt_python" -ForegroundColor Cyan
Write-Host "Direct pip path: $qmt_pip" -ForegroundColor Cyan

# 6. Quick test commands
Write-Host "`nQuick test commands:" -ForegroundColor Yellow
Write-Host "1. Check Python version:" -ForegroundColor White
Write-Host "   & `"$qmt_python`" --version" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test xtquant import:" -ForegroundColor White
Write-Host "   & `"$qmt_python`" -c `"import xtquant; print('xtquant import OK')`"" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run QMT connection test:" -ForegroundColor White
Write-Host "   & `"$qmt_python`" scripts\test_qmt_connection_v6.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Run QMT diagnosis:" -ForegroundColor White
Write-Host "   & `"$qmt_python`" scripts\diagnose_qmt_permission.py" -ForegroundColor Gray

# 7. Create aliases for convenience
Write-Host "`nFor convenience, you can create aliases:" -ForegroundColor Cyan
Write-Host "  Set-Alias qmtpython `"$qmt_python`"" -ForegroundColor White
Write-Host "  Set-Alias qmtpip `"$qmt_pip`"" -ForegroundColor White
Write-Host ""
Write-Host "Then use:" -ForegroundColor Cyan
Write-Host "  qmtpython scripts\test_qmt_connection_v6.py" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Activation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Make sure QMT client is running in 'Minimal Mode'!" -ForegroundColor Yellow
Write-Host "1. Start QMT client" -ForegroundColor White
Write-Host "2. Login with account: 8886156677" -ForegroundColor White
Write-Host "3. Check 'Minimal Mode' or 'Independent Trading' checkbox" -ForegroundColor White
Write-Host "4. Click Login" -ForegroundColor White
Write-Host ""
Write-Host "Then run the test: & `"$qmt_python`" scripts\test_qmt_connection_v6.py" -ForegroundColor White
