# QMT连接问题 - 快速行动清�?
> **优先�?*: P0（阻塞性问题）
> **预计解决时间**: 30分钟
> **创建时间**: 2026-04-03

---

## �?立即行动�?0分钟内完成）

### �?行动1: 获取Token�?0分钟�?
**操作步骤**�?```
1. 访问: https://xuntou.net/#/userInfo
2. 注册账号（如果还没有�?3. 获取Token
4. 编辑 .env.qmt 文件
5. 添加: QMT_TOKEN=您的Token
```

**验证**�?```bash
python scripts/test_qmt_connection_v2.py
# 应该看到: �?Token已设�?```

---

### �?行动2: 确认QMT版本�?分钟�?
**操作步骤**�?```
1. 打开QMT客户�?2. 点击"帮助" -> "关于"
3. 查看版本信息
```

**判断标准**�?- �?显示"MiniQMT" �?可以使用
- �?只显�?QMT" �?需要下载MiniQMT

**下载地址**：https://xuntou.net/

---

### �?行动3: 确认API权限�?5分钟�?
**操作步骤**�?```
1. 拨打国金证券客服: 95310
2. 询问账号 8886156677（模拟）是否开通QMT API权限
3. 询问账号 8887871993（实盘）是否开通QMT API权限
4. 如果没有，询问如何申请开�?```

**关键问题**�?- [ ] 模拟账户API权限是否开通？
- [ ] 实盘账户API权限是否开通？
- [ ] 如果未开通，申请流程是什么？

---

## 📋 完成后验�?
### 运行测试脚本
```bash
python scripts/test_qmt_connection_v2.py
```

### 预期结果
```
�?Token已设�?�?客户端路径存�?�?交易接口连接成功�?
账户资产信息:
  总资�? 1000000.00
  可用资金: 1000000.00
```

---

## 🆘 如果仍然失败

### 检查清�?- [ ] Token是否正确配置�?- [ ] QMT是否为MiniQMT版本�?- [ ] 账号API权限是否已开通？
- [ ] QMT客户端是否已启动�?- [ ] 交易账户是否已在QMT中登录？

### 联系支持
- 国金证券客服�?5310
- 迅投官方QQ群：（从 https://xuntou.net/ 获取�?
---

## 📚 详细文档

- [根本原因分析](file:///d:/ZephyrAlpha/docs/05_IMPLEMENTATION/07_OPERATIONS/QMT_CONNECTION_ROOT_CAUSE_ANALYSIS.md)
- [连接问题排查指南](file:///d:/ZephyrAlpha/docs/05_IMPLEMENTATION/07_OPERATIONS/QMT_CONNECTION_TROUBLESHOOTING.md)
- [QMT数据接口文档](file:///d:/ZephyrAlpha/docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md)

---

**创建时间**: 2026-04-03 | **预计完成时间**: 30分钟
