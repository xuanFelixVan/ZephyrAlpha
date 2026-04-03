# QMT Simple Check Script
# Minimal Chinese characters to avoid encoding issues

Write-Host "=== QMT Client Check ===" -ForegroundColor Cyan
Write-Host ""

# Check QMT processes
Write-Host "1. Checking for QMT processes..." -ForegroundColor Yellow

try {
    $processes = Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "*qmt*" -or 
        $_.ProcessName -like "*think*" -or
        $_.ProcessName -like "*guojin*"
    }
    
    if ($processes) {
        Write-Host "   Found QMT processes:" -ForegroundColor Green
        foreach ($p in $processes) {
            Write-Host "   - $($p.ProcessName) (PID: $($p.Id))" -ForegroundColor White
        }
    } else {
        Write-Host "   No QMT processes found." -ForegroundColor Red
        Write-Host "   Please start QMT client." -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Error checking processes." -ForegroundColor Red
}

Write-Host ""

# Check paths
Write-Host "2. Checking important paths..." -ForegroundColor Yellow

# Use variables for paths to avoid encoding issues in string literals
$path1 = "E:\国金QMT交易端模拟"
$path2 = "D:\国金证券QMT交易端"
$path3 = "E:\国金QMT交易端模拟\userdata_mini"
$path4 = "D:\国金证券QMT交易端\userdata_mini"

$paths = @($path1, $path2, $path3, $path4)

foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host "   [OK] Path exists" -ForegroundColor Green
    } else {
        Write-Host "   [MISSING] $p" -ForegroundColor Red
    }
}

Write-Host ""

# Check config file
Write-Host "3. Checking configuration..." -ForegroundColor Yellow

if (Test-Path ".env.qmt") {
    Write-Host "   [OK] Configuration file found" -ForegroundColor Green
} else {
    Write-Host "   [MISSING] .env.qmt not found" -ForegroundColor Red
}

Write-Host ""

# Critical instructions
Write-Host "4. IMPORTANT INSTRUCTIONS" -ForegroundColor Red
Write-Host "   =======================" -ForegroundColor Red
Write-Host ""
Write-Host "   For QMT API to work:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   a) Start QMT client" -ForegroundColor White
Write-Host "   b) Login with: 8886156677 / 134752" -ForegroundColor White
Write-Host "   c) CHECK 'Minimal Mode' or 'Independent Trading'" -ForegroundColor Green
Write-Host "   d) Wait 30 seconds after login" -ForegroundColor White
Write-Host ""
Write-Host "   Then test with:" -ForegroundColor Yellow
Write-Host "   .\scripts\activate_qmt_simple.ps1" -ForegroundColor White
Write-Host "   qmtpython scripts\test_qmt_connection_v6.py" -ForegroundColor White

Write-Host ""
Write-Host "=== Check Complete ===" -ForegroundColor Cyan
