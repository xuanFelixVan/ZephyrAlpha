---
module_id: DOC_ENCODING_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 文档治理标准
applicable_scope: 全系统文档编码规范
compliance_level: 专业标准
parent_document: ./INDEX.md
---

# 文档编码规范

> 清风量化系统 - 文档编码统一标准
> **核心定位**: 确保所有文档使用统一编码，提升跨平台兼容性和版本控制效率

---

## 1. 强制要求

### 1.1 编码标准

| 项目 | 要求 | 说明 |
|------|------|------|
| **文件编码** | UTF-8 without BOM | 所有Markdown文档必须使用UTF-8编码，不带BOM |
| **换行符** | LF (Linux风格) | 统一使用LF换行符，不使用CRLF |
| **文件扩展名** | .md | 所有文档使用.md扩展名 |
| **文件命名** | UPPERCASE_WITH_UNDERSCORES | 大写字母+下划线命名 |

### 1.2 禁止事项

- ❌ 禁止使用UTF-8 with BOM编码
- ❌ 禁止使用UTF-16编码
- ❌ 禁止使用ANSI编码
- ❌ 禁止使用CRLF换行符（Windows默认）
- ❌ 禁止在文件名中使用空格、中文等特殊字符

---

## 2. 验证方法

### 2.1 PowerShell验证脚本

```powershell
# 验证单个文件编码
function Test-FileEncoding {
    param([string]$FilePath)
    
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    $firstBytes = $bytes[0..2]
    
    if ($firstBytes[0] -eq 0xEF -and $firstBytes[1] -eq 0xBB -and $firstBytes[2] -eq 0xBF) {
        return "UTF-8 with BOM"
    } elseif ($firstBytes[0] -eq 0xFF -and $firstBytes[1] -eq 0xFE) {
        return "UTF-16 LE"
    } elseif ($firstBytes[0] -eq 0xFE -and $firstBytes[1] -eq 0xFF) {
        return "UTF-16 BE"
    } else {
        return "UTF-8 without BOM or ANSI"
    }
}

# 批量验证目录下所有.md文件
function Test-AllMarkdownFiles {
    param([string]$DirectoryPath)
    
    Get-ChildItem -Path $DirectoryPath -Recurse -Filter "*.md" | ForEach-Object {
        $encoding = Test-FileEncoding -FilePath $_.FullName
        if ($encoding -ne "UTF-8 without BOM or ANSI") {
            Write-Host "⚠️ $($_.FullName) : $encoding" -ForegroundColor Yellow
        } else {
            Write-Host "✅ $($_.FullName) : UTF-8 without BOM" -ForegroundColor Green
        }
    }
}
```

### 2.2 Python验证脚本

```python
import os
from pathlib import Path

def check_file_encoding(file_path):
    """检查文件编码"""
    with open(file_path, 'rb') as f:
        raw = f.read(3)
    
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'UTF-8 with BOM'
    elif raw.startswith(b'\xff\xfe'):
        return 'UTF-16 LE'
    elif raw.startswith(b'\xfe\xff'):
        return 'UTF-16 BE'
    else:
        return 'UTF-8 without BOM or ANSI'

def check_all_markdown_files(directory):
    """检查目录下所有Markdown文件的编码"""
    for md_file in Path(directory).rglob('*.md'):
        encoding = check_file_encoding(md_file)
        if encoding != 'UTF-8 without BOM or ANSI':
            print(f"⚠️ {md_file} : {encoding}")
        else:
            print(f"✅ {md_file} : UTF-8 without BOM")
```

---

## 3. 修复方法

### 3.1 PowerShell修复脚本

```powershell
# 转换单个文件为UTF-8 without BOM
function ConvertTo-Utf8NoBom {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
    [System.IO.File]::WriteAllText($FilePath, $content, $Utf8NoBomEncoding)
    
    Write-Host "✅ 已转换: $FilePath" -ForegroundColor Green
}

# 批量转换目录下所有.md文件
function Convert-AllMarkdownFiles {
    param([string]$DirectoryPath)
    
    Get-ChildItem -Path $DirectoryPath -Recurse -Filter "*.md" | ForEach-Object {
        $encoding = Test-FileEncoding -FilePath $_.FullName
        if ($encoding -ne "UTF-8 without BOM or ANSI") {
            ConvertTo-Utf8NoBom -FilePath $_.FullName
        }
    }
}
```

### 3.2 Python修复脚本

```python
import os
from pathlib import Path

def convert_to_utf8_no_bom(file_path):
    """转换文件为UTF-8 without BOM"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    
    print(f"✅ 已转换: {file_path}")

def convert_all_markdown_files(directory):
    """转换目录下所有Markdown文件为UTF-8 without BOM"""
    for md_file in Path(directory).rglob('*.md'):
        encoding = check_file_encoding(md_file)
        if encoding != 'UTF-8 without BOM or ANSI':
            convert_to_utf8_no_bom(md_file)
```

### 3.3 VS Code手动修复

1. 打开文件
2. 点击右下角编码显示（如"UTF-8 with BOM"）
3. 选择"Reopen with Encoding" → "UTF-8"
4. 再次点击编码显示
5. 选择"Save with Encoding" → "UTF-8"

---

## 4. 编辑器配置

### 4.1 VS Code配置

在项目根目录创建`.vscode/settings.json`：

```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "files.eol": "\n",
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true,
    
    "[markdown]": {
        "files.encoding": "utf8",
        "files.eol": "\n"
    }
}
```

### 4.2 Git配置

在项目根目录创建`.gitattributes`：

```
* text=auto eol=lf
*.md text eol=lf
```

### 4.3 EditorConfig

在项目根目录创建`.editorconfig`：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
charset = utf-8
end_of_line = lf
```

---

## 5. CI/CD集成

### 5.1 GitHub Actions检查

```yaml
name: Document Encoding Check

on: [push, pull_request]

jobs:
  check-encoding:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check Markdown file encoding
        run: |
          python scripts/check_encoding.py docs/
      
      - name: Check line endings
        run: |
          find docs -name "*.md" -exec file {} \; | grep -v "ASCII text\|UTF-8 Unicode text"
```

### 5.2 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "检查文档编码..."

# 获取所有暂存的.md文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')

for FILE in $STAGED_FILES; do
    # 检查文件编码
    ENCODING=$(file -bi "$FILE" | grep -o 'charset=[^;]*' | cut -d= -f2)
    
    if [ "$ENCODING" != "utf-8" ]; then
        echo "❌ 错误: $FILE 使用了不正确的编码: $ENCODING"
        echo "请使用UTF-8 without BOM编码"
        exit 1
    fi
    
    # 检查BOM
    if [ "$(head -c 3 "$FILE" | od -An -tx1)" = " ef bb bf" ]; then
        echo "❌ 错误: $FILE 包含BOM"
        echo "请使用UTF-8 without BOM编码"
        exit 1
    fi
    
    # 检查换行符
    if file "$FILE" | grep -q "CRLF"; then
        echo "⚠️ 警告: $FILE 使用CRLF换行符"
        echo "建议使用LF换行符"
    fi
done

echo "✅ 文档编码检查通过"
```

---

## 6. 常见问题

### Q1: 为什么不能使用UTF-8 with BOM？

**A**: BOM（Byte Order Mark）会导致以下问题：
- Git diff显示混乱
- 某些工具解析错误
- 文件合并冲突
- 跨平台兼容性问题

### Q2: 如何在Windows上保持LF换行符？

**A**: 
1. 配置Git：`git config --global core.autocrlf false`
2. 配置VS Code：`"files.eol": "\n"`
3. 使用`.gitattributes`强制LF

### Q3: 如何批量修复现有文档？

**A**: 使用提供的PowerShell或Python脚本批量转换：
```powershell
Convert-AllMarkdownFiles -DirectoryPath "docs/"
```

---

## 7. 检查清单

### 新文档创建检查

- [ ] 文件编码为UTF-8 without BOM
- [ ] 换行符为LF
- [ ] 文件名使用UPPERCASE_WITH_UNDERSCORES
- [ ] 文件扩展名为.md
- [ ] 包含标准YAML元数据

### 文档提交前检查

- [ ] 运行编码检查脚本
- [ ] 确认无BOM
- [ ] 确认换行符为LF
- [ ] Git diff无编码相关问题

---

## 8. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-04-04 | 初始版本，建立文档编码规范 |

---

**规范版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师
