# Miniconda安装指南（5分钟）

## 📋 安装步骤

### 步骤1: 下载Miniconda（2分钟）

1. 打开浏览器，访问：
   ```
   https://docs.conda.io/en/latest/miniconda.html
   ```

2. 向下滚动到"Windows installers"部分

3. 点击下载：
   ```
   Miniconda3 Windows 64-bit
   ```
   文件名类似：`Miniconda3-latest-Windows-x86_64.exe`

---

### 步骤2: 安装Miniconda（2分钟）

1. 双击运行下载的安装程序

2. 欢迎界面：点击 **Next**

3. 许可协议：点击 **I Agree**

4. 安装类型：选择 **Just Me (recommended)**，点击 **Next**

5. 安装路径：使用默认路径，点击 **Next**

6. 高级选项（重要！）：
   - ✅ **勾选** "Add Miniconda3 to my PATH environment variable"
   - ✅ **勾选** "Register Miniconda3 as my default Python"
   - 点击 **Install**

7. 等待安装完成，点击 **Next**，然后点击 **Finish**

---

### 步骤3: 重启终端（30秒）

1. **关闭当前所有终端窗口**

2. **重新打开一个新的PowerShell终端**

---

### 步骤4: 创建Python 3.12环境（1分钟）

在新打开的终端中运行：

```powershell
# 创建环境
conda create -n qmt python=3.12 -y

# 激活环境
conda activate qmt

# 安装依赖
pip install xtquant pandas numpy

# 验证安装
python --version
```

**预期输出**：
```
Python 3.12.x
```

---

### 步骤5: 测试QMT连接（1分钟）

```powershell
# 确保在qmt环境中
conda activate qmt

# 运行验证脚本
python scripts/verify_qmt_environment.py
```

**预期结果**：
```
✅ Python版本: 3.12.x
✅ xtquant库可用
✅ XtAccount类可用
```

---

## ⚠️ 重要提示

### 安装时必须勾选PATH选项！

```
安装界面示例：
┌─────────────────────────────────────┐
│ Advanced Options                    │
│                                     │
│ ☑️ Add Miniconda3 to my PATH        │ ← 必须勾选！
│    environment variable             │
│                                     │
│ ☑️ Register Miniconda3 as my        │ ← 建议勾选
│    default Python                   │
│                                     │
│ [Install]  [Cancel]                 │
└─────────────────────────────────────┘
```

### 如果忘记勾选PATH选项

需要手动添加到PATH：
1. 右键"此电脑" → 属性 → 高级系统设置
2. 环境变量 → 系统变量 → Path → 编辑
3. 添加以下路径：
   ```
   C:\Users\你的用户名\miniconda3
   C:\Users\你的用户名\miniconda3\Scripts
   C:\Users\你的用户名\miniconda3\Library\bin
   ```

---

## 🎯 验证安装成功

运行以下命令：

```powershell
# 检查conda版本
conda --version
# 应显示: conda 24.x.x

# 检查Python版本
python --version
# 应显示: Python 3.12.x

# 检查环境列表
conda env list
# 应显示: qmt 环境
```

---

## 📞 遇到问题？

### 问题1: conda命令找不到

**原因**：未勾选PATH选项或未重启终端

**解决**：
1. 重启终端
2. 如果还不行，重新安装并勾选PATH选项

### 问题2: Python版本仍然是3.13

**原因**：未激活qmt环境

**解决**：
```powershell
conda activate qmt
python --version
```

### 问题3: pip安装失败

**原因**：网络问题

**解决**：使用国内镜像
```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xtquant pandas numpy
```

---

## 🚀 安装完成后

1. **启动QMT客户端**
   - 打开国金QMT软件
   - 登录时勾选【极简模式】或【独立交易】

2. **激活qmt环境**
   ```powershell
   conda activate qmt
   ```

3. **运行测试脚本**
   ```powershell
   python scripts/test_qmt_connection_v4.py
   ```

4. **预期结果**
   ```
   ✅ 数据接口连接成功
   ✅ 交易接口连接成功
   ✅ 账户订阅成功
   ```

---

**预计总时间**: 5-7分钟
