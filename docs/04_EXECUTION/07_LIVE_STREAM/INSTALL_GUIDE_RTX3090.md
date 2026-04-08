---
parent_document: ../INDEX.md
responsibility:
- 操作指南编写与使用说明与系统维护管理
version: 1.0.0
module_id: EXE_INSTALL_GUIDE_RTX309
created_date: 2026-04-02
last_updated: '2026-04-07'
status: Active
owner: 首席文档架构师
---
---

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容



---


```
```

---





```powershell
pip uninstall torch torchvision torchaudio

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```


```python
import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")
```


```
GPU: NVIDIA GeForce RTX 3090
```

---


```powershell
pip install openai-whisper

```

---


```powershell
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```


---


```powershell
ollama pull qwen2.5:32b

ollama pull deepseek-r1:32b
```


---



```powershell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

pip uninstall -y torch torchvision torchaudio

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install openai-whisper

pip install transformers accelerate requests

python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

python -c "
import torch
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host ""
```


```powershell
.\install_dependencies.ps1
```

---



```powershell
pip uninstall -y torch torchvision torchaudio

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```


```powershell
pip install openai-whisper
```


```powershell
pip install transformers accelerate requests ffmpeg-python
```


```powershell
# Whisper large-v3
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```

---



```powershell
python test_rtx3090_models.py
```


```

```

---



```

```


```powershell
ollama pull qwen2.5:32b
```

```

```

---




```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```



```powershell
export HF_ENDPOINT=https://hf-mirror.com
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```




---
