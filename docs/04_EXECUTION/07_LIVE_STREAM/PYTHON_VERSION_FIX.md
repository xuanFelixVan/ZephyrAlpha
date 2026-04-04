---
standard_type: 技术文�?
applicable_scope: 交易执行
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 执行层负责人
version: 1.0.0
module_id: EXE_PYTHON_VERSION_FIX
created_date: 2026-04-02
last_updated: 2026-04-02
---
# Python版本问题解决方案

## 问题诊断

```
当前Python版本: Python 3.13.12
问题: PyTorch目前不支持Python 3.13
PyTorch支持版本: Python 3.8-3.12
```

---

## 解决方案

### 方案一：使用Conda创建Python 3.10环境（推荐）⭐⭐⭐⭐�?

#### 步骤1: 安装Miniconda（如果未安装�?

下载地址: https://docs.conda.io/en/latest/miniconda.html

#### 步骤2: 创建Python 3.10环境

```powershell
# 创建新环�?
conda create -n live-analysis python=3.10 -y

# 激活环�?
conda activate live-analysis

# 验证Python版本
python --version
```

#### 步骤3: 安装CUDA版本的PyTorch

```powershell
# 安装PyTorch CUDA 12.1版本
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# 或使用pip安装
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### 步骤4: 安装其他依赖

```powershell
pip install openai-whisper transformers accelerate requests ffmpeg-python
```

#### 步骤5: 下载Whisper模型

```powershell
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

---

### 方案二：安装Python 3.12（次选）⭐⭐⭐⭐

#### 步骤1: 下载Python 3.12

下载地址: https://www.python.org/downloads/release/python-3120/

#### 步骤2: 安装时选择"Add Python to PATH"

#### 步骤3: 使用Python 3.12运行安装脚本

```powershell
# 使用py启动器指定版�?
py -3.12 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

py -3.12 -m pip install openai-whisper transformers accelerate requests ffmpeg-python
```

---

### 方案三：使用现有的CPU版本PyTorch（临时方案）⭐⭐�?

如果暂时不想安装新Python版本，可以继续使用CPU版本�?

```powershell
# 安装CPU版本的PyTorch
pip install torch torchvision torchaudio

# 安装Whisper
pip install openai-whisper

# 安装其他依赖
pip install transformers accelerate requests ffmpeg-python
```

**注意**: CPU版本速度较慢，但可以正常工作�?

---

## 推荐方案对比

| 方案 | 难度 | 性能 | 推荐�?|
|------|------|------|--------|
| Conda环境 | 中等 | 最�?| ⭐⭐⭐⭐�?|
| Python 3.12 | 简�?| 最�?| ⭐⭐⭐⭐ |
| CPU版本 | 最简�?| 较慢 | ⭐⭐�?|

---

## 快速开始（Conda方案�?

```powershell
# 1. 创建环境
conda create -n live-analysis python=3.10 -y

# 2. 激活环�?
conda activate live-analysis

# 3. 安装PyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# 4. 安装其他依赖
pip install openai-whisper transformers accelerate requests ffmpeg-python

# 5. 下载Whisper模型
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 6. 验证安装
python test_rtx3090_models.py
```

---

## 验证安装

运行测试脚本验证所有组件：

```powershell
conda activate live-analysis
python test_rtx3090_models.py
```

**预期结果**:

```
�?CUDA: 通过
�?OLLAMA: 通过
�?WHISPER: 通过
�?FINBERT: 通过
�?OLLAMA_MODEL: 通过

总计: 5/5 测试通过
```

---

## 常见问题

### Q1: Conda安装速度�?

**解决方案**: 使用国内镜像

```powershell
# 配置清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes
```

### Q2: CUDA版本不匹�?

**解决方案**: 检查CUDA版本

```powershell
# 检查CUDA版本
nvidia-smi

# 根据CUDA版本选择PyTorch版本
# CUDA 12.1: pytorch-cuda=12.1
# CUDA 11.8: pytorch-cuda=11.8
```

### Q3: Whisper下载速度�?

**解决方案**: 使用国内镜像

```powershell
# 设置HuggingFace镜像
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 然后下载模型
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

---

## 下一�?

安装完成后，请：

1. **验证安装**: `python test_rtx3090_models.py`
2. **拉取更大模型**: `ollama pull qwen2.5:32b`
3. **配置系统**: 编辑 `config_local_rtx3090.yaml`
4. **启动系统**: `python main.py`

---

**创建日期**: 2026-04-02
**问题**: Python 3.13不支持PyTorch
**解决方案**: 使用Conda创建Python 3.10环境
