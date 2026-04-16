# audit-mcp-wrapper.ps1 - 审计工具MCP包装器
# 版本: 1.0
# 创建日期: 2026-04-01
# 特点: 将命令行工具包装为MCP服务器，解决"Connection closed"错误

# 工具配置映射
$toolConfigs = @{
    "bandit-security-scanner" = @{
        command = "bandit"
        args = @("-r", "src/", "-f", "json")
        description = "Python安全漏洞扫描工具"
        timeout = 30
    }
    "pylint-code-analyzer" = @{
        command = "pylint"
        args = @("src/", "--output-format=json")
        description = "Python代码质量分析工具"
        timeout = 60
    }
    "mypy-type-checker" = @{
        command = "mypy"
        args = @("src/")
        description = "Python类型检查工具"
        timeout = 30
    }
    "safety-dependency-checker" = @{
        command = "safety"
        args = @("check", "--json")
        description = "Python依赖安全扫描工具"
        timeout = 15
    }
    "pydocstyle-doc-checker" = @{
        command = "pydocstyle"
        args = @("src/")
        description = "Python文档一致性检查工具"
        timeout = 30
    }
    "yamllint-config-checker" = @{
        command = "yamllint"
        args = @("-f", "parsable", "config/")
        description = "YAML配置检查工具"
        timeout = 15
    }
    "markdownlint-doc-validator" = @{
        command = "npx"
        args = @("markdownlint-cli", "docs/")
        description = "Markdown文档质量检查工具"
        timeout = 30
    }
}

# MCP服务器主循环
function Process-MCP-Request {
    param($request)

    try {
        # 解析JSON-RPC请求
        $method = $request.method
        $id = $request.id
        $params = $request.params

        Write-Host "[MCP] 收到请求: $method (ID: $id)" -ForegroundColor Cyan

        if ($method -eq "initialize") {
            # 初始化响应
            return @{
                jsonrpc = "2.0"
                id = $id
                result = @{
                    protocolVersion = "2024-11-05"
                    serverInfo = @{
                        name = "Audit Tools MCP Wrapper"
                        version = "1.0.0"
                    }
                    capabilities = @{
                        tools = @{}
                    }
                }
            }
        }
        elseif ($method -eq "tools/list") {
            # 返回工具列表
            $tools = @()

            foreach ($toolName in $toolConfigs.Keys) {
                $config = $toolConfigs[$toolName]
                $tools += @{
                    name = $toolName
                    description = $config.description
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                }
            }

            return @{
                jsonrpc = "2.0"
                id = $id
                result = @{
                    tools = $tools
                }
            }
        }
        elseif ($method -eq "tools/call") {
            # 调用工具
            $toolName = $params.name
            Write-Host "[MCP] 调用工具: $toolName" -ForegroundColor Yellow

            if (-not $toolConfigs.ContainsKey($toolName)) {
                throw "未知的工具: $toolName"
            }

            $config = $toolConfigs[$toolName]
            $command = $config.command
            $args = $config.args

            # 构建完整命令
            $fullCommand = "$command " + ($args -join " ")
            Write-Host "[MCP] 执行命令: $fullCommand" -ForegroundColor Green

            # 执行命令（带超时）
            $output = ""
            $errorOutput = ""
            $exitCode = 0

            try {
                $process = Start-Process -FilePath $command -ArgumentList $args -NoNewWindow -PassThru -RedirectStandardOutput "temp_stdout.txt" -RedirectStandardError "temp_stderr.txt"

                # 等待进程完成或超时
                $process | Wait-Process -Timeout $config.timeout -ErrorAction SilentlyContinue

                if (-not $process.HasExited) {
                    # 超时，终止进程
                    $process | Stop-Process -Force
                    $errorOutput = "命令执行超时 (超过 $($config.timeout) 秒)"
                }
                else {
                    # 读取输出
                    if (Test-Path "temp_stdout.txt") {
                        $output = Get-Content "temp_stdout.txt" -Raw
                    }
                    if (Test-Path "temp_stderr.txt") {
                        $errorOutput = Get-Content "temp_stderr.txt" -Raw
                    }
                    $exitCode = $process.ExitCode
                }

                # 清理临时文件
                Remove-Item "temp_stdout.txt" -ErrorAction SilentlyContinue
                Remove-Item "temp_stderr.txt" -ErrorAction SilentlyContinue
            }
            catch {
                $errorOutput = "执行错误: $_"
            }

            # 构建响应
            $content = @()

            if ($output) {
                $content += @{
                    type = "text"
                    text = $output
                }
            }

            if ($errorOutput) {
                $content += @{
                    type = "text"
                    text = "错误输出: $errorOutput"
                }
            }

            if (-not $output -and -not $errorOutput) {
                $content += @{
                    type = "text"
                    text = "命令执行完成，但无输出。退出码: $exitCode"
                }
            }

            return @{
                jsonrpc = "2.0"
                id = $id
                result = @{
                    content = $content
                }
            }
        }
        else {
            # 未知方法
            return @{
                jsonrpc = "2.0"
                id = $id
                error = @{
                    code = -32601
                    message = "方法未找到: $method"
                }
            }
        }
    }
    catch {
        # 错误处理
        return @{
            jsonrpc = "2.0"
            id = $id
            error = @{
                code = -32000
                message = "服务器错误: $_"
            }
        }
    }
}

# 主程序 - 持续读取和处理JSON-RPC请求
Write-Host "========================================" -ForegroundColor Green
Write-Host "  审计工具MCP包装器 v1.0" -ForegroundColor Green
Write-Host "  支持工具: " -ForegroundColor Green
foreach ($tool in $toolConfigs.Keys) {
    Write-Host "  - $tool" -ForegroundColor Cyan
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[MCP] 服务器已启动，等待JSON-RPC请求..." -ForegroundColor Yellow

# 主循环：从stdin读取JSON-RPC请求
while ($true) {
    try {
        # 读取一行输入
        $line = $host.UI.ReadLine()

        if (-not $line) {
            # 空行或EOF，继续等待
            Start-Sleep -Milliseconds 100
            continue
        }

        # 解析JSON请求
        $request = $line | ConvertFrom-Json

        # 处理请求
        $response = Process-MCP-Request -request $request

        # 发送响应
        $responseJson = $response | ConvertTo-Json -Depth 10 -Compress
        Write-Host $responseJson

        # 如果是shutdown请求，退出
        if ($request.method -eq "shutdown") {
            Write-Host "[MCP] 收到关闭请求，退出..." -ForegroundColor Red
            break
        }
    }
    catch {
        # 输出错误响应
        $errorResponse = @{
            jsonrpc = "2.0"
            id = $null
            error = @{
                code = -32700
                message = "解析错误: $_"
            }
        }
        $errorJson = $errorResponse | ConvertTo-Json -Depth 10 -Compress
        Write-Host $errorJson
    }
}

Write-Host "[MCP] 服务器已关闭" -ForegroundColor Red
