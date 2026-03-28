# 开发环境搭建 (5 分钟)

> **适用**: Windows/Linux/Mac  
> **时间**: 5 分钟  
> **难度**: 

---

##  目标

完成本指南后，你将：
-  拥有完整的 Python 开发环境
-  能够运行项目代码
-  可以开始编写策略

---

##  前置要求

- Python 3.8+ (推荐 3.10)
- Git (可选，用于版本管理)
- 5GB 磁盘空间

---

##  快速搭建

### Step 1: 检查 Python 版本

```bash
python --version
# 或
python3 --version
```

**要求**: Python 3.8 或更高版本

如果未安装，前往 [python.org](https://www.python.org/downloads/) 下载。

### Step 2: 克隆项目（如已有代码可跳过）

```bash
git clone <your-repo-url>
cd quant_system_v4
```

### Step 3: 创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

激活后，命令行前缀应显示 `(venv)`。

### Step 4: 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**国内加速:**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Step 5: 验证安装

```bash
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
```

无错误输出即表示成功。

---

##  可选配置

### 1. 配置 IDE

**VS Code:**
1. 安装 Python 扩展
2. 选择解释器：`Ctrl+Shift+P`  "Python: Select Interpreter"
3. 选择 `venv` 环境

**PyCharm:**
1. File  Settings  Project  Python Interpreter
2. 添加  Existing Environment  选择 `venv/bin/python`

### 2. 安装开发工具

```bash
# 代码格式化
pip install black isort

# 代码检查
pip install flake8 pylint

# 测试
pip install pytest pytest-cov
```

### 3. 配置 Git（可选）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

##  验证清单

- [ ] Python 版本 >= 3.8
- [ ] 虚拟环境已激活
- [ ] 依赖安装成功
- [ ] 能够导入 pandas、numpy

---

##  常见问题

### Q1: pip 安装依赖失败

**错误**: `Could not find a version that satisfies the requirement...`

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 虚拟环境激活失败

**Windows 错误**: `无法加载文件，因为在此系统上禁止运行脚本`

**解决方案**:
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q3: 依赖冲突

**错误**: `ERROR: Cannot install ... and ... because these package versions have conflicting versions.`

**解决方案**:
```bash
# 删除虚拟环境，重新创建
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

python -m venv venv
pip install -r requirements.txt
```

---

##  下一步

环境搭建完成后：

1. 前往 [第一次回测](./first-backtest.md)
2. 学习 [开发规范](../02_DEVELOPMENT/README.md)
3. 阅读 [配置标准](../02_DEVELOPMENT/config-standard.md)

---

**最后更新**: 2026-03-28  
**状态**:  可用
