---
standard_type: µèÇµ£»µûçµí?
applicable_scope: õ║ñµÿôµëºÞíî
compliance_level: ÕêØÕºïµáçÕçå
parent_document: ../INDEX.md
implementation_status: Þ«¥Þ«íÚÿÂµ«Á
owner: µëºÞíîÕ▒éÞ┤ƒÞ┤úõ║║
responsibility:
  - 扩展功能、辅助模块、支撑文档
version: 1.0.0
module_id: EXE_PYTHON_VERSION_FIX
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

# Pythonþëêµ£¼Úù«ÚóÿÞºúÕå│µû╣µíê
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


## Úù«ÚóÿÞ»èµû¡

```
Õ¢ôÕëìPythonþëêµ£¼: Python 3.13.12
Úù«Úóÿ: PyTorchþø«Õëìõ©ìµö»µîüPython 3.13
PyTorchµö»µîüþëêµ£¼: Python 3.8-3.12
```

---

## ÞºúÕå│µû╣µíê

### µû╣µíêõ©Ç´╝Üõ¢┐þö¿CondaÕêøÕ╗║Python 3.10þÄ»Õóâ´╝êµÄ¿ÞìÉ´╝ëÔ¡ÉÔ¡ÉÔ¡ÉÔ¡ÉÔ¡?

#### µ¡ÑÚ¬ñ1: Õ«ëÞúàMiniconda´╝êÕªéµ×£µ£¬Õ«ëÞúà´╝?

õ©ïÞ¢¢Õ£░ÕØÇ: https://docs.conda.io/en/latest/miniconda.html

#### µ¡ÑÚ¬ñ2: ÕêøÕ╗║Python 3.10þÄ»Õóâ

```powershell
# ÕêøÕ╗║µû░þÄ»Õó?
conda create -n live-analysis python=3.10 -y

# µ┐Çµ┤╗þÄ»Õó?
conda activate live-analysis

# Ú¬îÞ»üPythonþëêµ£¼
python --version
```

#### µ¡ÑÚ¬ñ3: Õ«ëÞúàCUDAþëêµ£¼þÜäPyTorch

```powershell
# Õ«ëÞúàPyTorch CUDA 12.1þëêµ£¼
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# µêûõ¢┐þö¿pipÕ«ëÞúà
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### µ¡ÑÚ¬ñ4: Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû

```powershell
pip install openai-whisper transformers accelerate requests ffmpeg-python
```

#### µ¡ÑÚ¬ñ5: õ©ïÞ¢¢Whisperµ¿íÕ×ï

```powershell
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

---

### µû╣µíêõ║î´╝ÜÕ«ëÞúàPython 3.12´╝êµ¼íÚÇë´╝ëÔ¡ÉÔ¡ÉÔ¡ÉÔ¡É

#### µ¡ÑÚ¬ñ1: õ©ïÞ¢¢Python 3.12

õ©ïÞ¢¢Õ£░ÕØÇ: https://www.python.org/downloads/release/python-3120/

#### µ¡ÑÚ¬ñ2: Õ«ëÞúàµùÂÚÇëµï®"Add Python to PATH"

#### µ¡ÑÚ¬ñ3: õ¢┐þö¿Python 3.12Þ┐ÉÞíîÕ«ëÞúàÞäÜµ£¼

```powershell
# õ¢┐þö¿pyÕÉ»Õè¿ÕÖ¿µîçÕ«Üþëêµ£?
py -3.12 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

py -3.12 -m pip install openai-whisper transformers accelerate requests ffmpeg-python
```

---

### µû╣µíêõ©ë´╝Üõ¢┐þö¿þÄ░µ£ëþÜäCPUþëêµ£¼PyTorch´╝êõ©┤µùÂµû╣µíê´╝ëÔ¡ÉÔ¡ÉÔ¡?

Õªéµ×£µÜéµùÂõ©ìµâ│Õ«ëÞúàµû░Pythonþëêµ£¼´╝îÕÅ»õ╗Ñþ╗ºþ╗¡õ¢┐þö¿CPUþëêµ£¼´╝?

```powershell
# Õ«ëÞúàCPUþëêµ£¼þÜäPyTorch
pip install torch torchvision torchaudio

# Õ«ëÞúàWhisper
pip install openai-whisper

# Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû
pip install transformers accelerate requests ffmpeg-python
```

**µ│¿µäÅ**: CPUþëêµ£¼ÚÇƒÕ║ªÞ¥âµàó´╝îõ¢åÕÅ»õ╗Ñµ¡úÕ©©ÕÀÑõ¢£ÒÇ?

---

## µÄ¿ÞìÉµû╣µíêÕ»╣µ»ö

| µû╣µíê | ÚÜ¥Õ║ª | µÇºÞâ¢ | µÄ¿ÞìÉÕ║?|
|------|------|------|--------|
| CondaþÄ»Õóâ | õ©¡þ¡ë | µ£Çõ¢?| Ô¡ÉÔ¡ÉÔ¡ÉÔ¡ÉÔ¡?|
| Python 3.12 | þ«ÇÕì?| µ£Çõ¢?| Ô¡ÉÔ¡ÉÔ¡ÉÔ¡É |
| CPUþëêµ£¼ | µ£Çþ«ÇÕì?| Þ¥âµàó | Ô¡ÉÔ¡ÉÔ¡?|

---

## Õ┐½ÚÇƒÕ╝ÇÕºï´╝êCondaµû╣µíê´╝?

```powershell
# 1. ÕêøÕ╗║þÄ»Õóâ
conda create -n live-analysis python=3.10 -y

# 2. µ┐Çµ┤╗þÄ»Õó?
conda activate live-analysis

# 3. Õ«ëÞúàPyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# 4. Õ«ëÞúàÕàÂõ╗ûõ¥ØÞÁû
pip install openai-whisper transformers accelerate requests ffmpeg-python

# 5. õ©ïÞ¢¢Whisperµ¿íÕ×ï
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 6. Ú¬îÞ»üÕ«ëÞúà
python test_rtx3090_models.py
```

---

## Ú¬îÞ»üÕ«ëÞúà

Þ┐ÉÞíîµÁïÞ»òÞäÜµ£¼Ú¬îÞ»üµëÇµ£ëþ╗äõ╗Â´╝Ü

```powershell
conda activate live-analysis
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
```

---

## Õ©©ÞºüÚù«Úóÿ

### Q1: CondaÕ«ëÞúàÚÇƒÕ║ªµà?

**ÞºúÕå│µû╣µíê**: õ¢┐þö¿Õø¢ÕåàÚò£ÕâÅ

```powershell
# Úàìþ¢«µ©àÕìÄÚò£ÕâÅ
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes
```

### Q2: CUDAþëêµ£¼õ©ìÕî╣Úà?

**ÞºúÕå│µû╣µíê**: µúÇµƒÑCUDAþëêµ£¼

```powershell
# µúÇµƒÑCUDAþëêµ£¼
nvidia-smi

# µá╣µì«CUDAþëêµ£¼ÚÇëµï®PyTorchþëêµ£¼
# CUDA 12.1: pytorch-cuda=12.1
# CUDA 11.8: pytorch-cuda=11.8
```

### Q3: Whisperõ©ïÞ¢¢ÚÇƒÕ║ªµà?

**ÞºúÕå│µû╣µíê**: õ¢┐þö¿Õø¢ÕåàÚò£ÕâÅ

```powershell
# Þ«¥þ¢«HuggingFaceÚò£ÕâÅ
$env:HF_ENDPOINT = "https://hf-mirror.com"

# þäÂÕÉÄõ©ïÞ¢¢µ¿íÕ×ï
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```

---

## õ©ïõ©Çµ¡?

Õ«ëÞúàÕ«îµêÉÕÉÄ´╝îÞ»À´╝Ü

1. **Ú¬îÞ»üÕ«ëÞúà**: `python test_rtx3090_models.py`
2. **µïëÕÅûµø┤Õñºµ¿íÕ×ï**: `ollama pull qwen2.5:32b`
3. **Úàìþ¢«þ│╗þ╗ƒ**: þ╝ûÞ¥æ `config_local_rtx3090.yaml`
4. **ÕÉ»Õè¿þ│╗þ╗ƒ**: `python main.py`

---

**ÕêøÕ╗║µùÑµ£ƒ**: 2026-04-02
**Úù«Úóÿ**: Python 3.13õ©ìµö»µîüPyTorch
**ÞºúÕå│µû╣µíê**: õ¢┐þö¿CondaÕêøÕ╗║Python 3.10þÄ»Õóâ
