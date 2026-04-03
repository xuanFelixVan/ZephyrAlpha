# QMT连接问题完整诊断报告

**诊断时间**: 2026-04-03 19:35  
**诊断对象**: 国金证券QMT交易端连接问题  
**诊断结果**: 发现根本原因并已部分修复

---

## 📊 诊断总结

### ✅ 已确认正常的部分

| 检查项 | 状态 | 说明 |
|--------|------|------|
| **userdata_mini文件夹** | ✅ 存在 | 路径正确 |
| **up_queue_xtquant文件** | ✅ 存在 | 账号有策略交易权限 |
| **down_queue文件** | ✅ 存在 | 交易队列正常 |
| **写入权限** | ✅ 正常 | 可以创建文件 |
| **xtdata数据接口** | ✅ 成功 | 可以获取行情数据 |
| **xtquant库安装** | ✅ 已安装 | 版本: xtquant_250516 |

### ❌ 发现的问题

| 问题 | 严重程度 | 状态 | 影响 |
|------|---------|------|------|
| **Python版本不兼容** | 🔴 高 | ❌ 未修复 | API导入失败，连接返回-1 |
| **路径格式不正确** | 🟡 中 | ✅ 已修复 | 可能导致连接失败 |
| **Session冲突** | 🟢 低 | ⚠️  需注意 | 连接失败 |

---

## 🔍 详细诊断过程

### 阶段1: 初始连接测试

**测试脚本**: `test_qmt_connection_v3.py`

**测试结果**:
```
✅ 数据接口测试成功 - 获取到 5234 只股票
❌ 交易接口连接失败，返回码: -1
```

**初步诊断**: 数据接口可用，交易接口不可用

---

### 阶段2: 权限诊断

**诊断脚本**: `diagnose_qmt_permission.py`

**关键发现**:
```
✅ 找到 up_queue_xtquant 文件 (2 个)
  → 说明账号有策略交易权限
```

**结论**: 排除了账号权限问题

---

### 阶段3: 深度诊断

**诊断脚本**: `diagnose_qmt_deep.py`

**关键发现**:

#### 1. 路径格式问题 ✅ 已修复

**问题**:
```
❌ 错误路径: E:/国金QMT交易端模拟/bin.x64
✅ 正确路径: E:/国金QMT交易端模拟/userdata_mini
```

**官方文档**:
> miniqmt：路径指定到安装目录下 `\userdata_mini` 文件夹

**修复操作**:
- 已更新 `.env.qmt` 文件
- 将路径从 `bin.x64` 改为 `userdata_mini`

#### 2. Python版本问题 ❌ 未修复

**问题**:
```
❌ 当前版本: Python 3.13.12
✅ 官方支持: Python 3.6 - 3.12 (64位)
```

**官方文档**:
> XtQuant 目前提供的库包括 64 位 Python 3.6、3.7、3.8、3.9、3.10、3.11、3.12版本

**影响**:
- `XtAccount` 导入失败
- 交易接口连接返回 -1

**错误信息**:
```
❌ xtquant导入失败: cannot import name 'XtAccount' from 'xtquant.xttrader'
```

---

## 📋 解决方案

### 🔴 立即修复项（必须）

#### 创建Python 3.12虚拟环境

**方案1: 使用conda（推荐）**

```bash
# 步骤1: 创建环境
conda create -n qmt python=3.12 -y

# 步骤2: 激活环境
conda activate qmt

# 步骤3: 安装依赖
pip install xtquant pandas numpy

# 步骤4: 验证安装
python -c "import xtquant; print('✅ xtquant安装成功')"
```

**方案2: 使用venv**

```bash
# 前提：需要先安装Python 3.12

# 步骤1: 下载Python 3.12
# 访问: https://www.python.org/downloads/
# 下载: Python 3.12.x (64位)

# 步骤2: 创建虚拟环境
py -3.12 -m venv qmt_env

# 步骤3: 激活环境
qmt_env\Scripts\activate  # Windows

# 步骤4: 安装依赖
pip install xtquant pandas numpy
```

---

### 🟡 验证配置（重要）

#### 1. 验证Python版本

```bash
python --version
# 应该显示: Python 3.12.x

python -c "import sys; print(f'Python {sys.version}')"
# 确认是64位版本
```

#### 2. 验证xtquant安装

```bash
python -c "import xtquant; print('✅ xtquant可用')"
python -c "from xtquant import xtdata; print('✅ xtdata可用')"
python -c "from xtquant.xttrader import XtQuantTrader; print('✅ xttrader可用')"
```

#### 3. 验证路径配置

```bash
# 检查 .env.qmt 文件
cat .env.qmt

# 确认路径格式：
# QMT_SIMULATION_CLIENT_PATH=E:/国金QMT交易端模拟/userdata_mini
# QMT_LIVE_CLIENT_PATH=E:/国金QMT交易端实盘/userdata_mini
```

---

### 🟢 测试连接（最后步骤）

#### 1. 启动QMT客户端

```
1. 打开国金QMT软件
2. 在登录界面，勾选【极简模式】或【独立交易】
3. 输入账号密码登录
4. 确认登录成功
```

#### 2. 运行测试脚本

```bash
# 激活qmt环境
conda activate qmt

# 运行测试
python scripts/test_qmt_connection_v4.py
```

#### 3. 预期结果

```
✅ 数据接口测试成功
✅ 交易接口连接成功
✅ 账户订阅成功
✅ 资产查询成功
```

---

## 🎯 根本原因分析

### 问题链条

```
Python 3.13 (不兼容)
    ↓
xtquant API导入失败
    ↓
XtAccount类不存在
    ↓
交易接口连接返回-1
    ↓
无法进行程序化交易
```

### 解决链条

```
创建Python 3.12环境
    ↓
正确安装xtquant库
    ↓
API导入成功
    ↓
交易接口连接成功
    ↓
可以程序化交易
```

---

## 📚 参考文档

### 官方文档

1. **迅投知识库**: https://dict.thinktrader.net/
2. **Native API文档**: https://dict.thinktrader.net/nativeApi/start_now.html
3. **Inner API文档**: https://dict.thinktrader.net/innerApi/start_now.html

### 社区资源

1. **迅投官方论坛**: https://www.xuntou.net/
2. **国金MiniQMT连接问题**: https://www.xuntou.net/forum.php?mod=viewthread&tid=1705

### 本地文档

1. **PDF说明文档**: `D:\ZephyrAlpha\迅投QMT极速策略交易系统说明文档.pdf`
2. **连接故障排查**: `docs/05_IMPLEMENTATION/04_OPERATIONS/QMT_CONNECTION_TROUBLESHOOTING.md`
3. **MiniQMT登录指南**: `docs/05_IMPLEMENTATION/04_OPERATIONS/QMT_MINIQMT_LOGIN_GUIDE.md`

---

## ⚠️  重要提示

### Python版本要求

- ✅ **必须使用**: Python 3.6 - 3.12 (64位)
- ❌ **不支持**: Python 3.13+ 或 32位版本

### QMT客户端要求

- ✅ **必须启动**: QMT客户端必须先启动
- ✅ **必须登录**: 以极简模式或独立交易模式登录
- ✅ **路径正确**: 配置文件指向 `userdata_mini` 文件夹

### 账号权限要求

- ✅ **已确认**: 您的账号有策略交易权限
- ✅ **已确认**: up_queue_xtquant文件存在

---

## 📈 下一步行动

### 立即执行（今天）

1. ✅ **创建Python 3.12环境**
   ```bash
   conda create -n qmt python=3.12 -y
   conda activate qmt
   pip install xtquant pandas numpy
   ```

2. ✅ **验证环境配置**
   ```bash
   python --version
   python -c "import xtquant; print('✅ 成功')"
   ```

3. ✅ **重新测试连接**
   ```bash
   python scripts/test_qmt_connection_v4.py
   ```

### 后续任务（本周）

1. 📝 **更新项目文档**
   - 记录Python版本要求
   - 更新环境配置指南

2. 🧪 **完善测试脚本**
   - 添加更多错误处理
   - 增加自动化诊断

3. 📊 **实现QMT执行器**
   - 基于成功的连接测试
   - 集成到Layer 5策略执行层

---

## 📞 技术支持

### 如遇问题

1. **检查Python版本**: `python --version`
2. **检查xtquant安装**: `pip show xtquant`
3. **检查QMT客户端**: 确认已启动并登录
4. **查看日志**: 运行诊断脚本查看详细信息

### 联系方式

- **国金证券客服**: 95310
- **迅投官方论坛**: https://www.xuntou.net/

---

**报告生成时间**: 2026-04-03 19:35  
**诊断工具版本**: v4.0  
**下次审计建议**: 环境配置完成后重新测试
