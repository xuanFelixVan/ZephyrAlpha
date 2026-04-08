---
module_id: MCP_WRAPPER_SOLUTION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
responsibility:
  - 系统功能模块
---

# 🔧 MCP包装器解决方案 - 彻底解决"Connection closed"错误

## 📋 **问题诊断**

### **根本原因**
命令行工具（bandit、pylint、mypy等）是**一次性执行工具**，而MCP服务器需要**长期运行进程**。

| 类型 | 行为模式 | 输出格式 | 生命周期 |
|------|----------|----------|----------|
| **真正的MCP服务器** | 长期运行，通过stdin/stdout接收JSON-RPC请求 | 响应JSON-RPC格式 | 持续运行，处理多个请求 |
| **命令行工具** | 执行一次，输出结果，然后退出 | 文本/JSON输出 | 单次执行，立即退出 |

**错误机制**：
```
Trae → 启动进程 → 工具执行 → 输出结果 → 进程退出 → Trae检测到连接关闭 → 报告"MCP error -32000: Connection closed"
```

## 🚀 **解决方案：MCP包装器**

创建PowerShell包装器，将7个命令行工具包装为**真正的MCP服务器**。

### **已创建的解决方案文件**

#### **1. MCP包装器脚本**（按推荐顺序）
- **[audit-mcp-basic.ps1](file:///d:/ZephyrAlpha/.trae/audit-mcp-basic.ps1)** - **推荐使用**：纯ASCII版本，PowerShell 5完全兼容
- **[audit-mcp-simple.ps1](file:///d:/ZephyrAlpha/.trae/audit-mcp-simple.ps1)** - 简化版包装器，专门解决连接问题
- **[audit-mcp-wrapper.ps1](file:///d:/ZephyrAlpha/.trae/audit-mcp-wrapper.ps1)** - 完整版包装器（更多功能）

#### **2. 更新后的MCP配置文件**
- **[mcp-audit-wrapper-basic.json](file:///d:/ZephyrAlpha/.trae/mcp-audit-wrapper-basic.json)** - **推荐使用**：使用纯ASCII包装器的完整配置
- **[mcp-audit-wrapper.json](file:///d:/ZephyrAlpha/.trae/mcp-audit-wrapper.json)** - 完整MCP配置文件
- **[mcp-wrapper-updated.json](file:///d:/ZephyrAlpha/.trae/mcp-wrapper-updated.json)** - 备用版本

#### **3. 原始配置文件备份**
- **[mcp-global-updated.json](file:///d:/ZephyrAlpha/.trae/mcp-global-updated.json)** - 包含所有独立工具配置（有连接问题）

## 🛠️ **操作步骤**

### **第一步：备份原配置文件**
```powershell
# 手动操作：在文件管理器中
1. 打开目录: C:\Users\fanzi\AppData\Roaming\Trae CN\User\
2. 复制文件: mcp.json → mcp.json.backup
```

### **第二步：替换MCP配置文件**
```powershell
# 手动操作：
1. 打开文件: C:\Users\fanzi\AppData\Roaming\Trae CN\User\mcp.json
2. 全选删除所有内容
3. 复制下方完整配置
4. 粘贴并保存
```

### **第三步：重启Trae智能体**
1. **完全关闭Trae应用程序**
2. **重新打开Trae**
3. **等待MCP服务器初始化**

### **第四步：验证配置生效**
在Trae智能体聊天界面测试：
```
请调用audit-tools-wrapper工具列表
请进行代码安全扫描
```

## 📋 **完整MCP配置文件**

复制下方完整JSON配置，粘贴到 `C:\Users\fanzi\AppData\Roaming\Trae CN\User\mcp.json`：

```json
{
    "mcpServers": {
        "context7": {
            "command": "npx",
            "args": [
                "-y",
                "@upstash/context7-mcp@latest"
            ],
            "env": {},
            "fromGalleryId": "byted-mcp-volcengine.3rd_party_mcp_server_context7"
        },
        "xmind": {
            "command": "npx",
            "args": [
                "-y",
                "@41px/mcp-xmind",
                "D:/ZephyrAlpha"
            ]
        },
        "pdf-reader-mcp": {
            "command": "npx",
            "args": [
                "@sylphlab/pdf-reader-mcp"
            ],
            "env": {},
            "fromGalleryId": "byted-mcp-volcengine.pdf-reader-mcp"
        },
        "Pandoc": {
            "command": "uvx",
            "args": [
                "mcp-pandoc"
            ],
            "env": {},
            "fromGalleryId": "vivekVells.mcp-pandoc"
        },
        "TH_MCP": {
            "url": "https://mcp.tonghu.top/sse?apiKey=您在瞳虎mcp平台上申请的apiKey",
            "fromGalleryId": "byted-mcp-volcengine.THOCR"
        },
        "Fetch": {
            "command": "uvx",
            "args": [
                "mcp-server-fetch"
            ],
            "env": {},
            "fromGalleryId": "modelcontextprotocol.servers_fetch"
        },
        "File System": {
            "command": "npx -y @bunas/fs-mcp@latest",
            "args": [],
            "env": {
                "API_KEY": ""
            },
            "fromGalleryId": "bunasQ.fs"
        },
        "audit-tools-wrapper": {
            "command": "powershell",
            "args": [
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "d:\\ZephyrAlpha\\.trae\\audit-mcp-basic.ps1"
            ],
            "description": "Audit tools MCP wrapper - Fixes 'Connection closed' error, includes 7 audit tools"
        }
    }
}
```

## 🔧 **MCP包装器工作原理**

### **支持的工具列表**
包装器包含7个审计工具：
1. **bandit-security-scanner** - Python安全漏洞扫描
2. **pylint-code-analyzer** - Python代码质量分析  
3. **mypy-type-checker** - Python类型检查
4. **safety-dependency-checker** - Python依赖安全扫描
5. **pydocstyle-doc-checker** - Python文档一致性检查
6. **yamllint-config-checker** - YAML配置检查
7. **markdownlint-doc-validator** - Markdown文档质量检查

### **工作流程**
```
Trae请求 → JSON-RPC → PowerShell包装器 → 调用对应工具 → 收集输出 → JSON-RPC响应 → Trae
```

### **关键特性**
- ✅ **保持连接**：包装器持续运行，防止连接关闭
- ✅ **JSON-RPC兼容**：输出符合MCP协议标准格式
- ✅ **超时处理**：防止工具执行时间过长
- ✅ **错误处理**：捕获并返回工具执行错误
- ✅ **统一管理**：7个工具统一通过一个MCP服务器访问

## 🧪 **验证测试**

### **1. 验证工具安装**
```powershell
# 运行验证脚本
cd d:\ZephyrAlpha
.\\.trae\skills\audit-sentinel\verify-mcp-tools.ps1
```

### **2. 手动测试工具**
```powershell
# 测试各个工具（命令行）
bandit -r src/ -f json
pylint src/ --output-format=json
mypy src/
safety check --json
pydocstyle src/
yamllint -f parsable config/
npx markdownlint-cli docs/
```

### **3. 测试包装器脚本**
```powershell
# 测试包装器基本功能
cd d:\ZephyrAlpha
.\\.trae\test-mcp-wrapper.ps1
```

## 🔄 **更新Audit Sentinel智能体**

### **SKILL.md更新**
**[SKILL.md](file:///d:/ZephyrAlpha/.trae/skills/audit-sentinel/SKILL.md)** 已更新配置说明：

#### **新的MCP调用方式**
```bash
# 通过包装器调用审计工具
请调用audit-tools-wrapper进行安全扫描
请调用audit-tools-wrapper检查代码质量
请调用audit-tools-wrapper验证文档格式
```

#### **更新工具映射表**
| 审计层级 | 原工具调用 | 新包装器调用 |
|----------|------------|--------------|
| **L1文件系统层** | PowerShell命令 | 保持不变 |
| **L2文档内容层** | markdownlint + pydocstyle | 通过audit-tools-wrapper |
| **L3专业标准层** | bandit + pylint + mypy + safety + yamllint | 通过audit-tools-wrapper |

### **智能体调用示例**
```bash
# 快速系统审计（包装器版本）
请 Audit Sentinel 执行快速系统审计（使用MCP包装器）

# 三层审计工作流
1. L1文件系统审计：PowerShell命令自动执行
2. L2文档内容审计：调用audit-tools-wrapper中的markdownlint/pydocstyle
3. L3专业标准审计：调用audit-tools-wrapper中的bandit/pylint/mypy/safety/yamllint
```

## ⚠️ **故障排除**

### **常见问题及解决**

#### **1. 包装器启动失败**
**症状**: Trae无法启动MCP服务器
**解决**:
```powershell
# 检查PowerShell执行策略
Get-ExecutionPolicy

# 临时允许脚本执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

#### **2. 工具调用无响应**
**症状**: 调用工具后无输出
**解决**:
1. 检查工具是否已安装：运行 `verify-mcp-tools.ps1`
2. 检查路径是否正确：确保 `d:\ZephyrAlpha\.trae\` 路径存在
3. 重启Trae智能体

#### **3. 输出格式错误**
**症状**: Trae无法解析工具输出
**解决**:
1. 检查包装器脚本是否有语法错误
2. 查看Trae日志文件：`C:\Users\fanzi\AppData\Roaming\Trae CN\Logs\`

### **日志检查**
```powershell
# 查看Trae日志（如有权限）
Get-Content "C:\Users\fanzi\AppData\Roaming\Trae CN\Logs\*.log" -Tail 50
```

## 📊 **性能优化建议**

### **短期优化**
1. **并行执行**：包装器支持同时调用多个工具
2. **缓存结果**：相同工具的多次调用可缓存结果
3. **超时调整**：根据工具执行时间调整timeout参数

### **长期优化**
1. **专用MCP服务器**：寻找或开发专门的审计工具MCP服务器
2. **性能监控**：添加工具执行时间和资源使用监控
3. **批量处理**：支持批量审计多个文件/目录

## 🎯 **预期效果**

### **配置成功后**
- ✅ **无连接错误**：MCP error -32000: Connection closed 错误消失
- ✅ **工具列表显示**：Trae智能体后台显示 `audit-tools-wrapper`
- ✅ **正常调用**：智能体可正常调用所有7个审计工具
- ✅ **三层审计**：Audit Sentinel智能体可执行完整的三层审计工作流

### **智能体能力**
1. **自动化审计**：一键执行全系统三层审计
2. **专业标准**：满足专业量化机构文档治理要求
3. **高效执行**：审计效率提升，无连接中断问题
4. **可扩展性**：轻松添加新的审计工具到包装器

## 📝 **文件清单**

### **核心文件**
1. `audit-mcp-simple.ps1` - MCP包装器主脚本
2. `mcp-audit-wrapper.json` - 完整的MCP配置文件
3. `MCP_WRAPPER_SOLUTION.md` - 本解决方案文档

### **参考文件**
4. `audit-mcp-wrapper.ps1` - 完整功能包装器
5. `mcp-wrapper-updated.json` - 备用配置文件
6. `mcp-global-updated.json` - 原始独立工具配置
7. `test-mcp-wrapper.ps1` - 包装器测试脚本

### **验证文件**
8. `verify-mcp-tools.ps1` - 工具安装验证脚本
9. 各 `mcp-server-*.json` - 独立工具配置文件（已废弃）

## 🔗 **相关资源**

### **项目文件**
- **[SKILL.md](file:///d:/ZephyrAlpha/.trae/skills/audit-sentinel/SKILL.md)** - Audit Sentinel智能体完整定义
- **[mcp-audit-wrapper.json](file:///d:/ZephyrAlpha/.trae/mcp-audit-wrapper.json)** - 推荐配置文件
- **[audit-mcp-simple.ps1](file:///d:/ZephyrAlpha/.trae/audit-mcp-simple.ps1)** - 简化版包装器脚本

### **原始配置文件位置**
- `C:\Users\fanzi\AppData\Roaming\Trae CN\User\mcp.json` - Trae全局MCP配置

---

## ✅ **总结**

### **问题根源**：命令行工具 ≠ MCP服务器
### **解决方案**：PowerShell MCP包装器
### **执行步骤**：备份 → 替换配置 → 重启 → 验证
### **预期结果**：无连接错误，正常调用7个审计工具

### **立即行动**
1. **备份当前配置**：复制 `mcp.json` 为 `mcp.json.backup`
2. **替换配置文件**：使用上方完整JSON配置
3. **重启Trae智能体**：完全重启应用程序
4. **验证解决方案**：测试审计工具调用

**完成以上步骤后，所有"MCP error -32000: Connection closed"错误将得到解决，Audit Sentinel智能体将能正常调用所有审计工具执行专业级三层审计工作。** 🚀