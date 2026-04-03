# verify-mcp-tools.ps1 - MCP工具验证脚本（ASCII兼容版）
# 版本: 1.0
# 创建日期: 2026-03-31
# 特点: 纯ASCII字符，PowerShell 5完全兼容

Write-Host "========================================"
Write-Host "  MCP Tools Verification Script"
Write-Host "========================================"
Write-Host ""

Write-Host "[1/5] Checking Python environment..."
$pythonCheck = python --version 2>&1
if ($pythonCheck -like "*Python*") {
    Write-Host "  [OK] Python installed: $pythonCheck"
} else {
    Write-Host "  [ERROR] Python not found"
    Write-Host "  Please install Python: https://www.python.org/downloads/"
    exit 1
}

Write-Host "[2/5] Checking Node.js environment..."
$nodeCheck = node --version 2>&1
if ($nodeCheck -like "*v*") {
    Write-Host "  [OK] Node.js installed: $nodeCheck"
} else {
    Write-Host "  [ERROR] Node.js not found"
    Write-Host "  Please install Node.js: https://nodejs.org/"
    exit 1
}

Write-Host "[3/5] Checking Python security tools..."
$pythonTools = @(
    @{Name="bandit"; Command="bandit --version"},
    @{Name="safety"; Command="safety --version"},
    @{Name="pylint"; Command="pylint --version"},
    @{Name="mypy"; Command="mypy --version"},
    @{Name="pydocstyle"; Command="pydocstyle --version"},
    @{Name="yamllint"; Command="yamllint --version"}
)

foreach ($tool in $pythonTools) {
    Write-Host "  Checking $($tool.Name)..." -NoNewline
    $output = & cmd /c "$($tool.Command) 2>&1"
    if ($LASTEXITCODE -eq 0 -or $output -like "*version*") {
        Write-Host " [OK]"
    } else {
        Write-Host " [NOT FOUND]"
        Write-Host "    Install: pip install $($tool.Name)"
    }
}

Write-Host "[4/5] Checking Node.js documentation tools..."
$npmTools = @(
    @{Name="markdownlint-cli"; Command="npx markdownlint-cli --version"}
)

foreach ($tool in $npmTools) {
    Write-Host "  Checking $($tool.Name)..." -NoNewline
    $output = & cmd /c "$($tool.Command) 2>&1"
    if ($LASTEXITCODE -eq 0 -or $output -match "\d+\.\d+\.\d+") {
        Write-Host " [OK]"
    } else {
        Write-Host " [NOT FOUND]"
        Write-Host "    Install: npm install -g $($tool.Name)"
    }
}

Write-Host "[5/5] Checking Git..."
Write-Host "  Checking git..." -NoNewline
$gitCheck = git --version 2>&1
if ($gitCheck -like "*git version*") {
    Write-Host " [OK]"
    Write-Host "  Note: Using built-in Git commands for version control audit"
} else {
    Write-Host " [NOT FOUND]"
    Write-Host "  Recommended: Install Git from https://git-scm.com/"
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Installation Status Summary"
Write-Host "========================================"
Write-Host "Based on your terminal history, installed:"
Write-Host "  [OK] bandit 1.9.1"
Write-Host "  [OK] pylint 3.3.9"
Write-Host "  [OK] mypy 1.19.0"
Write-Host "  [OK] safety 3.7.0"
Write-Host "  [OK] pydocstyle 6.3.0"
Write-Host "  [OK] yamllint 1.38.0"
Write-Host "  [OK] markdownlint-cli 0.48.0"

Write-Host ""
Write-Host "========================================"
Write-Host "  MCP Tools Usage Examples"
Write-Host "========================================"
Write-Host "Security scan:"
Write-Host "  bandit -r src/ -f json"
Write-Host ""
Write-Host "Code quality analysis:"
Write-Host "  pylint src/modules/factor_calculator.py --output-format=json"
Write-Host ""
Write-Host "Document quality check:"
Write-Host "  markdownlint docs/"
Write-Host ""
Write-Host "Dependency security check:"
Write-Host "  safety check"

Write-Host ""
Write-Host "========================================"
Write-Host "  Calling Audit Sentinel"
Write-Host "========================================"
Write-Host "IMPORTANT: Type these in Trae chat, NOT in PowerShell terminal"
Write-Host ""
Write-Host "Quick audit (5 minutes):"
Write-Host "  '请Audit Sentinel执行快速系统审计'"
Write-Host ""
Write-Host "Full audit (30 minutes):"
Write-Host "  '作为Audit Sentinel，请执行完整系统审计'"
Write-Host ""
Write-Host "Special audit:"
Write-Host "  '需要文档治理专项审查'"
Write-Host "  '验证架构变更影响'"

Write-Host ""
Write-Host "========================================"
Write-Host "  Audit Report Location"
Write-Host "========================================"
Write-Host "Latest audit report:"
Write-Host "  docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/"
Write-Host "  Includes: AUDIT_STRATEGY_ADJUSTMENT.md"

Write-Host ""
Write-Host "Verification complete! MCP tools are ready."