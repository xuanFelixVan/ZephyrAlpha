# Miniconda安装关键步骤检查清单

## 📋 安装时必须确认的选项

### 1. 双击运行安装程序

### 2. 安装向导步骤检查

**步骤1: 欢迎界面**
```
[Next]
```

**步骤2: 许可协议**
```
[I Agree]
```

**步骤3: 安装类型**
```
○ Just Me (recommended)    ← 选择这个
○ All Users (requires admin privileges)
[Next]
```

**步骤4: 安装路径**
```
默认路径: C:\Users\fanzi\miniconda3
[Next]
```

### ⭐⭐⭐ 关键步骤：高级选项 ⭐⭐⭐

**步骤5: 高级选项（必须截图确认）**
```
┌─────────────────────────────────────┐
│ Advanced Options                    │
│                                     │
│ ☑️ [ ] Add Miniconda3 to my PATH   │ ← 必须勾选！
│    environment variable             │
│                                     │
│ ☑️ [ ] Register Miniconda3 as my   │ ← 建议勾选
│    default Python                   │
│                                     │
│ [Install]  [Cancel]                 │
└─────────────────────────────────────┘
```

**重要**：必须确保 **两个复选框都被勾选**！

### 3. 完成安装
```
等待安装完成 → [Next] → [Finish]
```

---

## 🔧 安装后验证

### 验证1: 关闭所有终端窗口
```
1. 关闭当前所有PowerShell/CMD窗口
2. 关闭VS Code（如果打开了）
3. 关闭Trae AI的终端（如果需要）
```

### 验证2: 重新打开终端
```
1. 按 Win + R
2. 输入: powershell
3. 按回车打开新的PowerShell
```

### 验证3: 运行验证命令
```powershell
# 命令1: 检查conda版本
conda --version
# 应该显示: conda 24.x.x

# 命令2: 检查Python版本
python --version
# 应该显示: Python 3.13.x（Miniconda自带的Python）

# 命令3: 检查conda环境
conda env list
# 应该显示: base 环境
```

---

## 📝 环境配置文件创建

**不要**直接在终端输入YAML内容！而是创建文件：

### 创建 environment.yml 文件

```powershell
# 创建环境配置文件
@'
name: qmt
channels:
  - defaults
dependencies:
  - python=3.12
  - pip
  - pandas
  - numpy
  - pip:
    - xtquant
'@ | Out-File -FilePath environment.yml -Encoding UTF8

# 使用配置文件创建环境
conda env create -f environment.yml
```

---

## ⚠️ 常见错误和解决方案

### 错误1: "conda command not found"
**原因**: PATH环境变量没有配置
**解决**:
1. 重新安装Miniconda
2. 确保勾选"Add to PATH"
3. 重启所有终端

### 错误2: 安装程序闪退
**原因**: 权限问题
**解决**:
1. 右键点击安装程序
2. 选择"以管理员身份运行"

### 错误3: 下载速度慢
**解决**: 使用国内镜像
```
# 配置清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

---

## 🎯 安装完成后的正确操作

### 1. 创建QMT环境
```powershell
# 方法1: 使用命令行
conda create -n qmt python=3.12 -y

# 方法2: 使用配置文件（推荐）
# 先创建 environment.yml 文件
# 然后运行: conda env create -f environment.yml
```

### 2. 激活环境
```powershell
conda activate qmt
```

### 3. 验证Python版本
```powershell
python --version
# 应该显示: Python 3.12.x
```

### 4. 安装xtquant
```powershell
pip install xtquant pandas numpy
```

---

## 📞 需要帮助？

**如果您在安装过程中遇到问题，请提供**：

1. **安装程序的截图**（特别是高级选项页面）
2. **安装过程中的任何错误信息**
3. **安装完成后运行 `conda --version` 的输出**

**重要提醒**：不要跳过"Add to PATH"选项！这是conda命令可用的关键。
