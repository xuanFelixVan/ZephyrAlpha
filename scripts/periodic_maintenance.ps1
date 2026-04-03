# 定期维护脚本
# 每周/每月运行一次，确保文档质量

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清风量化系统文档质量定期检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state"

# 创建报告目录
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 开始执行文档质量检查..." -ForegroundColor Yellow
Write-Host ""

# 1. 文档审计
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 1/3 执行文档审计..." -ForegroundColor Green
python scripts/document_auditor.py --all --project-root "d:/ZephyrAlpha" --output "$reportDir\audit_report_$timestamp.json"
Write-Host ""

# 2. 链接检查
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 2/3 执行链接检查..." -ForegroundColor Green
python scripts/link_fixer.py --scan --report --output "$reportDir\link_report_$timestamp.json"
Write-Host ""

# 3. 元数据检查
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 3/3 执行元数据检查..." -ForegroundColor Green
python scripts/metadata_enhancer.py --scan --report --output "$reportDir\metadata_report_$timestamp.json"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "质量检查完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "报告已保存到: $reportDir" -ForegroundColor Yellow
Write-Host "时间戳: $timestamp" -ForegroundColor Yellow
Write-Host ""

# 显示摘要
Write-Host "建议后续操作:" -ForegroundColor Cyan
Write-Host "  1. 查看审计报告: $reportDir\audit_report_$timestamp.json"
Write-Host "  2. 修复损坏链接: python scripts/link_fixer.py --fix"
Write-Host "  3. 完善元数据: python scripts/metadata_enhancer.py --enhance"
Write-Host ""
