---
standard_type: Õ«×µû¢µîçÕìù
applicable_scope: õ║ñµÿôµëºÞíî
compliance_level: ÕêØÕºïµáçÕçå
parent_document: ../INDEX.md
implementation_status: Þ«¥Þ«íÚÿÂµ«Á
owner: µëºÞíîÕ▒éÞ┤ƒÞ┤úõ║║
version: 1.0.0
module_id: EXE_INSTALL_GUIDE_RTX309
created_date: 2026-04-02
last_updated: 2026-04-02
---
# RTX 3090 þÄ»ÕóâÚàìþ¢«Õ«ëÞúàµîçÕìù

> µÁïÞ»òµùÑµ£ƒ: 2026-04-02
> þí¼õ╗ÂÚàìþ¢«: RTX 3090 24GB + 64GB RAM + i7-12700KF

---

## ­ƒôè µÁïÞ»òþ╗ôµ×£Õêåµ×É

```
Ô£?Ollamaµ£ìÕèí: µ¡úÕ©©
Ô£?FinBERT: µ¡úÕ©©
ÔØ?CUDA: PyTorchµÿ»CPUþëêµ£¼´╝îÚ£ÇÞªüÚçìµû░Õ«ëÞú?
ÔØ?Whisper: µ£¬Õ«ëÞú?
ÔØ?Ollamaµ¿íÕ×ï: deepseek-r1:14bÕôìÕ║öÞÂàµùÂ´╝êÕÅ»Þâ¢µÿ»CPUµÄ¿þÉåµàó´╝ë
```

---

## ­ƒÜÇ Õ┐½ÚÇƒõ┐«Õñìµû╣µí?

### µ¡ÑÚ¬ñ1: Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorch

**Úù«Úóÿ**: Õ¢ôÕëìPyTorchµÿ»CPUþëêµ£¼´╝?.9.1+cpu´╝ë´╝îµùáµ│òõ¢┐þö¿GPU

**ÞºúÕå│µû╣µíê**:

```powershell
# Õì©Þ¢¢CPUþëêµ£¼þÜäPyTorch
pip uninstall torch torchvision torchaudio

# Õ«ëÞúàCUDA 12.1þëêµ£¼þÜäPyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Ú¬îÞ»üÕ«ëÞúà**:

```python
import torch
print(f"PyTorchþëêµ£¼: {torch.__version__}")
print(f"CUDAÕÅ»þö¿: {torch.cuda.is_available()}")
print(f"CUDAþëêµ£¼: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

**Úóäµ£ƒÞ¥ôÕç║**:

```
PyTorchþëêµ£¼: 2.x.x+cu121
CUDAÕÅ»þö¿: True
CUDAþëêµ£¼: 12.1
GPU: NVIDIA GeForce RTX 3090
```

---

### µ¡ÑÚ¬ñ2: Õ«ëÞúàWhisper

```powershell
# Õ«ëÞúàOpenAI Whisper
pip install openai-whisper

# Ú¬îÞ»üÕ«ëÞúà
python -c "import whisper; print('WhisperÕ«ëÞúàµêÉÕèƒ')"
```

---

### µ¡ÑÚ¬ñ3: õ©ïÞ¢¢Whisper large-v3µ¿íÕ×ï

```powershell
# õ©ïÞ¢¢Õ╣ÂÕèáÞ¢¢µ¿íÕ×ï´╝êõ╝ÜÞç¬Õè¿õ©ïÞ¢¢Õê░µ£¼Õ£░´╝?
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

**ÚóäÞ«íµùÂÚù┤**: 5-10ÕêåÚÆƒ
**õ©ïÞ¢¢ÕñºÕ░Å**: ~3GB

---

### µ¡ÑÚ¬ñ4: ´╝êÕÅ»ÚÇë´╝ëµïëÕÅûµø┤ÕñºþÜäOllamaµ¿íÕ×ï

```powershell
# µïëÕÅûQwen2.5 32B´╝êµÄ¿ÞìÉ´╝ë
ollama pull qwen2.5:32b

# µêûµïëÕÅûDeepSeek-R1 32B
ollama pull deepseek-r1:32b
```

**ÚóäÞ«íµùÂÚù┤**: 30-60ÕêåÚÆƒ
**õ©ïÞ¢¢ÕñºÕ░Å**: ~20GB

---

## ­ƒøá´©?õ©ÇÚö«Õ«ëÞúàÞäÜµ£?

ÕêøÕ╗║õ©Çõ©¬PowerShellÞäÜµ£¼ `install_dependencies.ps1`:

```powershell
# RTX 3090 þÄ»ÕóâÚàìþ¢«õ©ÇÚö«Õ«ëÞúàÞäÜµ£?

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RTX 3090 þÄ»ÕóâÚàìþ¢«Õ«ëÞúà" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Õì©Þ¢¢CPUþëêµ£¼þÜäPyTorch
Write-Host "µ¡ÑÚ¬ñ1: Õì©Þ¢¢CPUþëêµ£¼þÜäPyTorch..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio

# 2. Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorch
Write-Host "µ¡ÑÚ¬ñ2: Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorch..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Õ«ëÞúàWhisper
Write-Host "µ¡ÑÚ¬ñ3: Õ«ëÞúàWhisper..." -ForegroundColor Yellow
pip install openai-whisper

# 4. Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû
Write-Host "µ¡ÑÚ¬ñ4: Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû..." -ForegroundColor Yellow
pip install transformers accelerate requests

# 5. õ©ïÞ¢¢Whisper large-v3µ¿íÕ×ï
Write-Host "µ¡ÑÚ¬ñ5: õ©ïÞ¢¢Whisper large-v3µ¿íÕ×ï..." -ForegroundColor Yellow
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 6. Ú¬îÞ»üÕ«ëÞúà
Write-Host "µ¡ÑÚ¬ñ6: Ú¬îÞ»üÕ«ëÞúà..." -ForegroundColor Yellow
python -c "
import torch
print(f'PyTorchþëêµ£¼: {torch.__version__}')
print(f'CUDAÕÅ»þö¿: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Ô£?Õ«ëÞúàÕ«îµêÉ´╝? -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "õ©ïõ©Çµ¡?" -ForegroundColor Cyan
Write-Host "  1. Þ┐ÉÞíîµÁïÞ»ò: python test_rtx3090_models.py"
Write-Host "  2. µïëÕÅûµø┤Õñºµ¿íÕ×ï: ollama pull qwen2.5:32b"
Write-Host "  3. ÕÉ»Õè¿þ│╗þ╗ƒ: python main.py"
Write-Host ""
```

**Þ┐ÉÞíîµû╣Õ╝Å**:

```powershell
.\install_dependencies.ps1
```

---

## ­ƒôØ µëïÕè¿Õ«ëÞúàµ¡ÑÚ¬ñ

### 1. Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorch

```powershell
# Õì©Þ¢¢µùºþëêµ£?
pip uninstall -y torch torchvision torchaudio

# Õ«ëÞúàCUDA 12.1þëêµ£¼
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Õ«ëÞúàWhisper

```powershell
pip install openai-whisper
```

### 3. Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû

```powershell
pip install transformers accelerate requests ffmpeg-python
```

### 4. õ©ïÞ¢¢µ¿íÕ×ï

```powershell
# Whisper large-v3
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# FinBERT´╝êÕÀ▓õ©ïÞ¢¢´╝?
# python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```

---

## Ô£?Ú¬îÞ»üÕ«ëÞúà

Þ┐ÉÞíîµÁïÞ»òÞäÜµ£¼Ú¬îÞ»üµëÇµ£ëþ╗äõ╗?

```powershell
python test_rtx3090_models.py
```

**Úóäµ£ƒþ╗ôµ×£**:

```
Ô£?CUDA: ÚÇÜÞ┐ç
Ô£?OLLAMA: ÚÇÜÞ┐ç
Ô£?WHISPER: ÚÇÜÞ┐ç
Ô£?FINBERT: ÚÇÜÞ┐ç
Ô£?OLLAMA_MODEL: ÚÇÜÞ┐ç

µÇ╗Þ«í: 5/5 µÁïÞ»òÚÇÜÞ┐ç
Ô£?µëÇµ£ëµÁïÞ»òÚÇÜÞ┐ç´╝üþ│╗þ╗ƒÕÅ»õ╗Ñµ¡úÕ©©Þ┐ÉÞíîÒÇ?
```

---

## ­ƒÄ» µÄ¿ÞìÉÚàìþ¢«

### µû╣µíêõ©Ç´╝Üõ¢┐þö¿þÄ░µ£ëµ¿íÕ×ï´╝êþ½ïÕì│ÕÅ»þö¿´╝?

```
Þ»¡Úƒ│Þ»åÕê½: Whisper large-v3 (µ£¼Õ£░)
ÕåàÕ«╣Õêåµ×É: deepseek-r1:14b (ÕÀ▓µ£ë)
µâàµäƒÕêåµ×É: FinBERT (µ£¼Õ£░)

µÿ¥Õ¡ÿÕìáþö¿: ~20GB / 24GB
µÇºÞâ¢Þ»äþ║º: Ô¡ÉÔ¡ÉÔ¡ÉÔ¡ÉÔ¡?
```

### µû╣µíêõ║î´╝ÜµïëÕÅûµø┤Õñºµ¿íÕ×ï´╝êµ£Çõ¢│µÇºÞâ¢´╝?

```powershell
# µïëÕÅûQwen2.5 32B
ollama pull qwen2.5:32b
```

```
Þ»¡Úƒ│Þ»åÕê½: Whisper large-v3 (µ£¼Õ£░)
ÕåàÕ«╣Õêåµ×É: qwen2.5:32b (µÄ¿ÞìÉµïëÕÅû)
µâàµäƒÕêåµ×É: FinBERT (µ£¼Õ£░)

µÿ¥Õ¡ÿÕìáþö¿: ~22GB / 24GB
µÇºÞâ¢Þ»äþ║º: Ô¡ÉÔ¡ÉÔ¡ÉÔ¡ÉÔ¡?(µ£ÇÚ½?
```

---

## ­ƒöº Õ©©ÞºüÚù«Úóÿ

### Q1: PyTorch CUDAþëêµ£¼Õ«ëÞúàÕñ▒Þ┤Ñ

**ÞºúÕå│µû╣µíê**:

```powershell
# Õ░ØÞ»òCUDA 11.8þëêµ£¼
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Q2: Whisperõ©ïÞ¢¢ÚÇƒÕ║ªµà?

**ÞºúÕå│µû╣µíê**:

```powershell
# õ¢┐þö¿Õø¢ÕåàÚò£ÕâÅ
export HF_ENDPOINT=https://hf-mirror.com
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

### Q3: Ollamaµ¿íÕ×ïÕôìÕ║öÞÂàµùÂ

**ÕÄƒÕøá**: CPUµÄ¿þÉåÚÇƒÕ║ªµà?

**ÞºúÕå│µû╣µíê**: Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorchÕÉÄ´╝îOllamaõ╝ÜÞç¬Õè¿õ¢┐þö¿GPUÕèáÚÇ?

---

## ­ƒôÜ þø©Õà│µûçµíú

- [RTX 3090µ£Çõ¢│µ¿íÕ×ïÚàìþ¢«](./RTX3090_BEST_MODELS.md)
- [Úàìþ¢«µûçõ╗Â](./config_local_rtx3090.yaml)
- [Úâ¿þ¢▓ÞäÜµ£¼](./deploy_rtx3090.ps1)
- [µÁïÞ»òÞäÜµ£¼](./test_rtx3090_models.py)

---

**ÕêøÕ╗║µùÑµ£ƒ**: 2026-04-02
**µø┤µû░µùÑµ£ƒ**: 2026-04-02
