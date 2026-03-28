# 常见问题解答 (FAQ)

> **用途**: 快速定位和解决常见问题  
> **更新**: 2026-03-28

---

##  目录

- [环境安装](#环境安装)
- [数据问题](#数据问题)
- [回测问题](#回测问题)
- [实盘问题](#实盘问题)
- [配置问题](#配置问题)

---

##  环境安装

### Q: Python 版本不兼容

**错误**: `SyntaxError: invalid syntax`

**原因**: Python 版本 < 3.8

**解决方案**:
```bash
# 检查版本
python --version

# 升级 Python（使用 pyenv 或直接下载）
# https://www.python.org/downloads/
```

### Q: 依赖安装失败

**错误**: `Could not find a version that satisfies the requirement...`

**解决方案**:
```bash
# 1. 升级 pip
python -m pip install --upgrade pip

# 2. 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 清理缓存
pip cache purge
pip install -r requirements.txt
```

### Q: 虚拟环境问题

**错误**: `ModuleNotFoundError: No module named 'pandas'`

**原因**: 未激活虚拟环境

**解决方案**:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 验证
which python  # 应指向 venv 目录
```

---

##  数据问题

### Q: 数据下载失败

**错误**: `Failed to download data`

**可能原因**:
1. 网络连接问题
2. 数据源不可用
3. 权限不足

**解决方案**:
```bash
# 1. 检查网络
ping www.example.com

# 2. 更换数据源
python scripts/download_data.py --source alternative

# 3. 手动下载数据
# 从数据提供商网站下载 CSV，放到 data/raw/
```

### Q: 数据格式错误

**错误**: `KeyError: 'close'` 或 `ValueError: could not convert string to float`

**原因**: CSV 文件格式不正确

**解决方案**:
检查 CSV 列名，必须包含：
- `date` 或 `datetime`: 时间戳
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

### Q: 数据缺失

**错误**: `No data found for date range`

**解决方案**:
```bash
# 1. 检查数据文件
ls -lh data/raw/

# 2. 查看数据范围
python scripts/check_data.py --symbol IF

# 3. 补充数据
python scripts/download_data.py --symbol IF --start 2023-01-01
```

---

##  回测问题

### Q: 回测结果为空

**现象**: 回测报告无交易记录

**可能原因**:
1. 策略信号未触发
2. 数据时间范围不匹配
3. 策略参数过于严格

**解决方案**:
```bash
# 1. 检查策略配置
cat config/strategies/active.yaml

# 2. 放宽参数
# 编辑策略文件，调整阈值

# 3. 查看日志
tail -f logs/backtest.log
```

### Q: 回测收益率异常高

**现象**: 年化收益 > 1000%

**可能原因**:
1. 未来函数（使用了未来数据）
2. 未考虑滑点和手续费
3. 数据有错误

**解决方案**:
- 检查策略代码，确保无未来函数
- 添加手续费和滑点设置
- 验证数据质量

### Q: 回测速度慢

**现象**: 回测 1 年数据需要 > 10 分钟

**优化方案**:
```python
# 1. 使用向量化计算（避免循环）
# 2. 减少数据频率（如从 1 分钟改为 5 分钟）
# 3. 缩短回测时间范围
```

---

##  实盘问题

### Q: 无法连接交易所

**错误**: `Connection timeout`

**解决方案**:
```bash
# 1. 检查网络
ping trader.ctp.com

# 2. 检查防火墙
# 确保端口未被阻止

# 3. 使用备用服务器
# 修改 config/trading.yaml 中的连接地址
```

### Q: 订单被拒绝

**错误**: `Order rejected: Insufficient funds`

**原因**:
1. 账户资金不足
2. 保证金不足
3. 超出持仓限制

**解决方案**:
- 检查账户可用资金
- 降低开仓手数
- 查看交易所持仓限制

### Q: 实盘与回测差异大

**原因**:
1. 滑点和手续费设置不当
2. 市场冲击未考虑
3. 数据质量差异

**解决方案**:
- 调整滑点参数（建议 1-2 个跳价）
- 增加手续费率
- 使用更高质量的数据

---

##  配置问题

### Q: 配置文件找不到

**错误**: `FileNotFoundError: config.yaml`

**解决方案**:
```bash
# 1. 复制配置模板
cp config/config.example.yaml config/config.yaml

# 2. 检查路径
pwd
ls config/
```

### Q: 环境变量未设置

**错误**: `KeyError: 'API_KEY'`

**解决方案**:
```bash
# Windows (PowerShell)
$env:API_KEY="your_key"

# Linux/Mac
export API_KEY="your_key"

# 或添加到 .env 文件
echo "API_KEY=your_key" >> .env
```

### Q: 配置不生效

**原因**: 配置文件格式错误

**解决方案**:
```bash
# 验证 YAML 格式
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# 检查缩进
# YAML 对缩进敏感，确保使用空格而非 Tab
```

---

##  其他问题

### Q: 日志文件过大

**问题**: `logs/` 目录占用 > 10GB

**解决方案**:
```bash
# 1. 清理旧日志
rm logs/*.log.*.gz

# 2. 配置日志轮转
# 编辑 config/logging.yaml，设置 maxBytes

# 3. 定期清理脚本
# 添加到 crontab
0 0 * * 0 find logs/ -name "*.log.*.gz" -delete
```

### Q: 系统运行缓慢

**可能原因**:
1. 内存不足
2. CPU 占用过高
3. 磁盘 IO 瓶颈

**解决方案**:
```bash
# 1. 检查资源使用
top  # Linux/Mac
Task Manager  # Windows

# 2. 减少并发策略数量
# 3. 使用 SSD 存储
# 4. 增加系统内存
```

---

##  获取帮助

如果以上 FAQ 未解决你的问题：

1. **查看日志**: `logs/error.log`
2. **搜索 Issues**: GitHub Issues
3. **查看文档**: [../README.md](../README.md)
4. **联系维护者**: 提交 Issue 或邮件

---

**最后更新**: 2026-03-28  
**状态**:  持续更新
