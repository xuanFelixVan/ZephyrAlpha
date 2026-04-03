# audit-mcp-basic.ps1 - Basic MCP wrapper for audit tools
# Pure ASCII characters only for PowerShell 5 compatibility

# Read stdin input
$inputText = [Console]::In.ReadToEnd()

if ($inputText) {
    try {
        $request = $inputText | ConvertFrom-Json
        $method = $request.method
        $id = $request.id
        
        if ($method -eq "tools/list") {
            $tools = @(
                @{
                    name = "bandit-security-scanner"
                    description = "Python security scanner"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "pylint-code-analyzer"
                    description = "Python code analyzer"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "mypy-type-checker"
                    description = "Python type checker"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "safety-dependency-checker"
                    description = "Python dependency security"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "pydocstyle-doc-checker"
                    description = "Python docstring checker"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "yamllint-config-checker"
                    description = "YAML config checker"
                    inputSchema = @{ type = "object"; properties = @{} }
                },
                @{
                    name = "markdownlint-doc-validator"
                    description = "Markdown document validator"
                    inputSchema = @{ type = "object"; properties = @{} }
                }
            )
            
            $response = @{
                jsonrpc = "2.0"
                id = $id
                result = @{ tools = $tools }
            }
            
            $responseJson = $response | ConvertTo-Json -Depth 10
            Write-Host $responseJson
        }
        elseif ($method -eq "tools/call") {
            $toolName = $request.params.name
            
            $output = ""
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
            }
            
            $content = @()
            if ($output) {
                $content += @{ type = "text"; text = $output.ToString() }
            }
            
            $response = @{
                jsonrpc = "2.0"
                id = $id
                result = @{ content = $content }
            }
            
            $responseJson = $response | ConvertTo-Json -Depth 10
            Write-Host $responseJson
        }
        else {
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
        $errorResponse = @{
            jsonrpc = "2.0"
            id = $null
            error = @{ code = -32700; message = "Parse error: $_" }
        }
        $errorJson = $errorResponse | ConvertTo-Json -Depth 10
        Write-Host $errorJson
    }
}
else {
    # Keep alive for 5 minutes
    Start-Sleep -Seconds 300
}