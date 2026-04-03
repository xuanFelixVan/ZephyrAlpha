# QMT Login Check Script
# Verifies QMT client is running and logged in correctly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QMT Client Login Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if QMT processes are running
Write-Host "1. Checking QMT processes..." -ForegroundColor Yellow

$qmt_processes = @()
try {
    # Look for common QMT process names
    $process_names = @("*qmt*", "*think*", "*guojin*", "*迅投*", "*国金*")
    
    foreach ($name in $process_names) {
        $procs = Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -like $name}
        if ($procs) {
            $qmt_processes += $procs
        }
    }
    
    if ($qmt_processes.Count -gt 0) {
        Write-Host "   Found $($qmt_processes.Count) QMT-related process(es):" -ForegroundColor Green
        foreach ($proc in $qmt_processes) {
            Write-Host "   - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor White
        }
    } else {
        Write-Host "   No QMT processes found!" -ForegroundColor Red
        Write-Host "   Please start QMT client first." -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Error checking processes: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Check QMT installation paths
Write-Host "2. Checking QMT installation paths..." -ForegroundColor Yellow

$paths_to_check = @(
    "E:\国金QMT交易端模拟",
    "D:\国金证券QMT交易端",
    "E:\国金QMT交易端模拟\userdata_mini",
    "D:\国金证券QMT交易端\userdata_mini"
)

foreach ($path in $paths_to_check) {
    if (Test-Path $path) {
        Write-Host "   ✅ $path" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $path (not found)" -ForegroundColor Red
    }
}

Write-Host ""

# 3. Check configuration file
Write-Host "3. Checking configuration file..." -ForegroundColor Yellow

$env_file = ".env.qmt"
if (Test-Path $env_file) {
    Write-Host "   ✅ $env_file found" -ForegroundColor Green
    
    # Read and display account info (masked)
    $content = Get-Content $env_file
    $sim_account = ($content | Where-Object {$_ -like "QMT_SIMULATION_ACCOUNT=*"}).Split('=')[1]
    $live_account = ($content | Where-Object {$_ -like "QMT_LIVE_ACCOUNT=*"}).Split('=')[1]
    
    if ($sim_account) {
        Write-Host "   Simulation account: $sim_account" -ForegroundColor White
    }
    if ($live_account) {
        Write-Host "   Live account: $live_account" -ForegroundColor White
    }
} else {
    Write-Host "   ❌ $env_file not found" -ForegroundColor Red
}

Write-Host ""

# 4. Critical login instructions
Write-Host "4. CRITICAL: QMT Login Requirements" -ForegroundColor Red -BackgroundColor White
Write-Host "   =========================================" -ForegroundColor Red

Write-Host "   To use MiniQMT mode (required for API access):" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Step 1: Start QMT Client" -ForegroundColor White
Write-Host "     - Double-click '国金证券QMT交易端'" -ForegroundColor Gray
Write-Host ""
Write-Host "   Step 2: Login Screen" -ForegroundColor White
Write-Host "     - Account: 8886156677 (simulation)" -ForegroundColor Gray
Write-Host "     - Password: 134752" -ForegroundColor Gray
Write-Host "     - ✅ CHECK '极简模式' or '独立交易' checkbox" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "     - Click 'Login'" -ForegroundColor Gray
Write-Host ""
Write-Host "   Step 3: Verify Login" -ForegroundColor White
Write-Host "     - Main window should appear" -ForegroundColor Gray
Write-Host "     - Status bar should show '已连接' or similar" -ForegroundColor Gray
Write-Host "     - Wait 30 seconds for full initialization" -ForegroundColor Gray

Write-Host ""
Write-Host "   Step 4: Test Connection" -ForegroundColor White
Write-Host "     - Run: .\scripts\activate_qmt_simple.ps1" -ForegroundColor Gray
Write-Host "     - Then: qmtpython scripts\test_qmt_connection_v6.py" -ForegroundColor Gray

Write-Host ""

# 5. Common issues and solutions
Write-Host "5. Common Issues and Solutions" -ForegroundColor Yellow

$issues = @(
    @{
        Issue = "Connection returns -1"
        Solution = @(
            "1. Ensure '极简模式' is checked during login",
            "2. Make sure QMT client is fully started (wait 30 sec)",
            "3. Try different session ID in test script",
            "4. Check userdata_mini folder exists and has write permission"
        )
    },
    @{
        Issue = "xtdata works but xttrader fails"
        Solution = @(
            "This means data interface is OK but trading interface fails",
            "Most likely: QMT not in MiniQMT mode",
            "Solution: Logout and login again with '极简模式' checked"
        )
    },
    @{
        Issue = "Python version warning"
        Solution = @(
            "Use the QMT Python environment:",
            "C:\Users\fanzi\.conda\envs\qmt\python.exe scripts\test_qmt_connection_v6.py"
        )
    }
)

foreach ($issue in $issues) {
    Write-Host "   Issue: $($issue.Issue)" -ForegroundColor White
    foreach ($sol in $issue.Solution) {
        Write-Host "     • $sol" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Check Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Ensure QMT is running in 'Minimal Mode'" -ForegroundColor Cyan
Write-Host "2. Run: .\scripts\activate_qmt_simple.ps1" -ForegroundColor Cyan
Write-Host "3. Run: qmtpython scripts\test_qmt_connection_v6.py" -ForegroundColor Cyan
Write-Host ""
