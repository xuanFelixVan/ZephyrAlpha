# audit-mcp-simple.ps1 - 简化版审计工具MCP包装器
# 专门解决"Connection closed"错误

# 设置执行策略
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 从stdin读取所有输入
$inputText = [Console]::In.ReadToEnd()

if ($inputText) {
    try {
        # 尝试解析JSON-RPC请求
        $request = $inputText | ConvertFrom-Json
        $method = $request.method
        $id = $request.id
        
        Write-Host "[MCP] 收到请求: $method (ID: $id)" | Out-Null
        
        if ($method -eq "tools/list") {
            # 返回工具列表
            $tools = @(
                @{
                    name = "bandit-security-scanner"
                    description = "Python安全漏洞扫描工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "pylint-code-analyzer"
                    description = "Python代码质量分析工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "mypy-type-checker"
                    description = "Python类型检查工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "safety-dependency-checker"
                    description = "Python依赖安全扫描工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "pydocstyle-doc-checker"
                    description = "Python文档一致性检查工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "yamllint-config-checker"
                    description = "YAML配置检查工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                },
                @{
                    name = "markdownlint-doc-validator"
                    description = "Markdown文档质量检查工具"
                    inputSchema = @{
                        type = "object"
                        properties = @{}
                    }
                }
            )
            
            $response = @{
                jsonrpc = "2.0"
                id = $id
                result = @{
                    tools = $tools
                }
            }
            
            $responseJson = $response | ConvertTo-Json -Depth 10
            Write-Host $responseJson
        }
        elseif ($method -eq "tools/call") {
            $toolName = $request.params.name
            Write-Host "[MCP] 调用工具: $toolName" | Out-Null
            
            # 执行对应的工具
            $output = ""
            $errorOutput = ""
            
            switch ($toolName) {
                "bandit-security-scanner" {
                    $output = bandit -r src/ -f json 2>&1
                }
                "pylint-code-analyzer" {
                    $output = pylint src/ --output-format=json 2>&1
                }
                "mypy-type-checker" {
                    $output = mypy src/ 2>&1
                }
                "safety-dependency-checker" {
                    $output = safety check --json 2>&1
                }
                "pydocstyle-doc-checker" {
                    $output = pydocstyle src/ 2>&1
                }
                "yamllint-config-checker" {
                    $output = yamllint -f parsable config/ 2>&1
                }
                "markdownlint-doc-validator" {
                    $output = npx markdownlint-cli docs/ 2>&1
                }
                default {
                    $errorOutput = "未知的工具: $toolName"
                }
            }
            
            $content = @()
            
            if ($output) {
                $content += @{
                    type = "text"
                    text = $output.ToString()
                }
            }
            
            if ($errorOutput) {
                $content += @{
                    type = "text"
                    text = "错误: $errorOutput"
                }
            }
            
            $response = @{
                jsonrpc = "2.0"
                id = $id
                result = @{
                    content = $content
                }
            }
            
            $responseJson = $response | ConvertTo-Json -Depth 10
            Write-Host $responseJson
        }
        else {
            # 其他请求
            $response = @{
                jsonrpc = "2.0"
                id = $id
                result = @{}
            }
            
            $responseJson = $response | ConvertTo-Json -Depth 10
            Write-Host $responseJson
        }
    }
    catch {
        # 错误处理
        $errorResponse = @{
            jsonrpc = "2.0"
            id = $null
            error = @{
                code = -32700
                message = "解析错误: $_"
            }
        }
        $errorJson = $errorResponse | ConvertTo-Json -Depth 10
        Write-Host $errorJson
    }
}
else {
    # 没有输入，保持运行（防止连接关闭）
    Write-Host "[MCP] 等待请求..." | Out-Null
    Start-Sleep -Seconds 300  # 保持运行5分钟
}