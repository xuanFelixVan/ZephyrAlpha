# 测试MCP包装器
Write-Host "测试MCP包装器..."

# 测试1: 测试工具列表请求
$testRequest = @{
    jsonrpc = "2.0"
    id = "test-1"
    method = "tools/list"
} | ConvertTo-Json

Write-Host "发送请求: $testRequest"
Write-Host ""

# 模拟输入
$testRequest | & "d:\ZephyrAlpha\.trae\audit-mcp-simple.ps1"

Write-Host ""
Write-Host "测试完成"
