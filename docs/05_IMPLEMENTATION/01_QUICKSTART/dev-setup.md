---
module_id: DEV_SETUP_9427
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_05
responsibility: 01_QUICKSTART
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
##  目标











完成本指南后，你将：





-  拥有完整?Python 开发环?





-  能够运行项目代码





-  可以开始编写策略











```
```---
```











##  前置要求











- Python 3.8+ (推荐 3.10)





- Git (可选，用于版本管理)





- 5GB 磁盘空间











```
```---
```











##  快速搭?











### Step 1: 检?Python 版本











```bash





python --version





# ?





python3 --version





```











**要求**: Python 3.8 或更高版?











如果未安装，前往 [python.org](https://www.python.org/downloads/) 下载?











### Step 2: 克隆项目（如已有代码可跳过）











```bash





git clone <your-repo-url>





cd ZephyrAlpha





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











激活后，命令行前缀应显?`(venv)`?











### Step 4: 安装依赖











```bash





pip install --upgrade pip





pip install -r requirements.txt





```











**国内加?**





```bash





pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple





```











### Step 5: 验证安装











```bash





python -c "import sys; print(f'Python: {sys.version}')"





python -c "import pandas; print(f'Pandas: {pandas.__version__}')"





```











无错误输出即表示成功能











```
```---
```











##  可选配?











### 1. 配置 IDE











**VS Code:**





1. 安装 Python 扩展





2. 选择解释器：`Ctrl+Shift+P`  "Python: Select Interpreter"





3. 选择 `venv` 环境











**PyCharm:**





1. File  Settings  Project  Python Interpreter





2. 添加  Existing Environment  选择 `venv/bin/python`











### 2. 安装开发工?











```bash





# 代码格式?





pip install black isort











# 代码检?





pip install flake8 pylint











# 测试





pip install pytest pytest-cov





```











### 3. 配置 Git（可选）











```bash





git config --global user.name "Your Name"





git config --global user.email "your.email@example.com"





```











```
```---
```











##  验证清单











- [ ] Python 版本 >= 3.8





- [ ] 虚拟环境已激?





- [ ] 依赖安装成功





- [ ] 能够导入 pandas、numpy











```
```---
```











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











### Q2: 虚拟环境激活失?











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





# 删除虚拟环境，重新创?





rm -rf venv  # Linux/Mac





rmdir /s venv  # Windows











python -m venv venv





pip install -r requirements.txt





```











```
```---
```











##  下一?











环境搭建完成后：











1. 前往 2. 学习 开发规范





3. 阅读 











```
```---
```











**最后更?*: 2026-03-28  





**状?*:  可用





