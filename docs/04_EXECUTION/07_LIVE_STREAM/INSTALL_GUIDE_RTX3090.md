---
standard_type: 实施指南
applicable_scope: 交易执行
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 执行层负责人
version: 1.0.0
module_id: EXE_INSTALL_GUIDE_RTX309
created_date: 2026-04-02
last_updated: 2026-04-02
---
# RTX 3090 环境配置安装指南

> 测试日期: 2026-04-02
> 硬件配置: RTX 3090 24GB + 64GB RAM + i7-12700KF

---

## 📊 测试结果分析

```
✅ Ollama服务: 正常
✅ FinBERT: 正常
❌ CUDA: PyTorch是CPU版本，需要重新安装
❌ Whisper: 未安装
❌ Ollama模型: deepseek-r1:14b响应超时（可能是CPU推理慢）
```

---

## 🚀 快速修复方案

### 步骤1: 安装CUDA版本的PyTorch

**问题**: 当前PyTorch是CPU版本（2.9.1+cpu），无法使用GPU

**解决方案**:

```powershell
# 卸载CPU版本的PyTorch
pip uninstall torch torchvision torchaudio

# 安装CUDA 12.1版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**验证安装**:

```python
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"CUDA版本: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

**预期输出**:

```
PyTorch版本: 2.x.x+cu121
CUDA可用: True
CUDA版本: 12.1
GPU: NVIDIA GeForce RTX 3090
```

---

### 步骤2: 安装Whisper

```powershell
# 安装OpenAI Whisper
pip install openai-whisper

# 验证安装
python -c "import whisper; print('Whisper安装成功')"
```

---

### 步骤3: 下载Whisper large-v3模型

```powershell
# 下载并加载模型（会自动下载到本地）
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

**预计时间**: 5-10分钟
**下载大小**: ~3GB

---

### 步骤4: （可选）拉取更大的Ollama模型

```powershell
# 拉取Qwen2.5 32B（推荐）
ollama pull qwen2.5:32b

# 或拉取DeepSeek-R1 32B
ollama pull deepseek-r1:32b
```

**预计时间**: 30-60分钟
**下载大小**: ~20GB

---

## 🛠️ 一键安装脚本

创建一个PowerShell脚本 `install_dependencies.ps1`:

```powershell
# RTX 3090 环境配置一键安装脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RTX 3090 环境配置安装" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 卸载CPU版本的PyTorch
Write-Host "步骤1: 卸载CPU版本的PyTorch..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio

# 2. 安装CUDA版本的PyTorch
Write-Host "步骤2: 安装CUDA版本的PyTorch..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. 安装Whisper
Write-Host "步骤3: 安装Whisper..." -ForegroundColor Yellow
pip install openai-whisper

# 4. 安装其他依赖
Write-Host "步骤4: 安装其他依赖..." -ForegroundColor Yellow
pip install transformers accelerate requests

# 5. 下载Whisper large-v3模型
Write-Host "步骤5: 下载Whisper large-v3模型..." -ForegroundColor Yellow
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 6. 验证安装
Write-Host "步骤6: 验证安装..." -ForegroundColor Yellow
python -c "
import torch
print(f'PyTorch版本: {torch.__version__}')
print(f'CUDA可用: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✅ 安装完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "  1. 运行测试: python test_rtx3090_models.py"
Write-Host "  2. 拉取更大模型: ollama pull qwen2.5:32b"
Write-Host "  3. 启动系统: python main.py"
Write-Host ""
```

**运行方式**:

```powershell
.\install_dependencies.ps1
```

---

## 📝 手动安装步骤

### 1. 安装CUDA版本的PyTorch

```powershell
# 卸载旧版本
pip uninstall -y torch torchvision torchaudio

# 安装CUDA 12.1版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. 安装Whisper

```powershell
pip install openai-whisper
```

### 3. 安装其他依赖

```powershell
pip install transformers accelerate requests ffmpeg-python
```

### 4. 下载模型

```powershell
# Whisper large-v3
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# FinBERT（已下载）
# python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```

---

## ✅ 验证安装

运行测试脚本验证所有组件:

```powershell
python test_rtx3090_models.py
```

**预期结果**:

```
✅ CUDA: 通过
✅ OLLAMA: 通过
✅ WHISPER: 通过
✅ FINBERT: 通过
✅ OLLAMA_MODEL: 通过

总计: 5/5 测试通过
✅ 所有测试通过！系统可以正常运行。
```

---

## 🎯 推荐配置

### 方案一：使用现有模型（立即可用）

```
语音识别: Whisper large-v3 (本地)
内容分析: deepseek-r1:14b (已有)
情感分析: FinBERT (本地)

显存占用: ~20GB / 24GB
性能评级: ⭐⭐⭐⭐⭐
```

### 方案二：拉取更大模型（最佳性能）

```powershell
# 拉取Qwen2.5 32B
ollama pull qwen2.5:32b
```

```
语音识别: Whisper large-v3 (本地)
内容分析: qwen2.5:32b (推荐拉取)
情感分析: FinBERT (本地)

显存占用: ~22GB / 24GB
性能评级: ⭐⭐⭐⭐⭐ (最高)
```

---

## 🔧 常见问题

### Q1: PyTorch CUDA版本安装失败

**解决方案**:

```powershell
# 尝试CUDA 11.8版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Q2: Whisper下载速度慢

**解决方案**:

```powershell
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

### Q3: Ollama模型响应超时

**原因**: CPU推理速度慢

**解决方案**: 安装CUDA版本的PyTorch后，Ollama会自动使用GPU加速

---

## 📚 相关文档

- [RTX 3090最佳模型配置](./RTX3090_BEST_MODELS.md)
- [配置文件](./config_local_rtx3090.yaml)
- [部署脚本](./deploy_rtx3090.ps1)
- [测试脚本](./test_rtx3090_models.py)

---

**创建日期**: 2026-04-02
**更新日期**: 2026-04-02
