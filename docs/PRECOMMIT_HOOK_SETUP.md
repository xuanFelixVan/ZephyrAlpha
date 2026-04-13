---
module_id: AUTO_PRECOMMIT_HOOK_SETUP
status: Auto-generated
generated_date: 2026-04-13
---

# ZephyrAlpha 预提交治理钩子安装说明

## 快速安装

### 方式 1: 手动（推荐用于 Windows）

```bash
# 在仓库根目录执行
cp scripts/hooks/pre-commit-governance-check.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 方式 2: Husky（跨平台）

```bash
# 安装 husky (需要 Node.js)
npx husky install

# 添加钩子
npx husky add .husky/pre-commit "python scripts/hooks/pre-commit-governance-check.py"
```

## 功能

钩子在每次 commit 前自动运行，执行以下检查：

1. **运行 sentinel_l1_governance_scan.py**
   - 扫描所有 Markdown 文件
   - 检测断链和重复 module_id
   
2. **治理健康度检查**
   - 断链数 > 100 → 阻止提交 ❌
   - 重复 module_id > 20 → 阻止提交 ❌
   - 健康度检查通过 → 允许提交 ✅

3. **自动报告**
   ```
   [pre-commit] 📊 治理健康度快照:
     断链数         : 35
     重复 module_id : 13
   [pre-commit] ✅ 治理健康度检查通过
   ```

## 跳过钩子（不推荐）

如果需要绕过钩子，可以使用：

```bash
git commit --no-verify -m "your message"
```

## 修改阈值

编辑 `scripts/hooks/pre-commit-governance-check.py`，修改：

```python
BROKEN_LINK_THRESHOLD = 100    # 允许的最大断链数
DUPLICATE_THRESHOLD = 20       # 允许的最大重复组数
```

## 故障排除

**钩子未执行**：
- 检查文件权限: `chmod +x .git/hooks/pre-commit`
- 检查 Python 路径：`which python` 或 `which python3`
- Windows 用户可改为 `python scripts/hooks/pre-commit-governance-check.py`

**总是失败**：
- 运行 `python scripts/audit/sentinel_l1_governance_scan.py` 检查是否有其他问题
- 查看 `docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json` 的断链数

