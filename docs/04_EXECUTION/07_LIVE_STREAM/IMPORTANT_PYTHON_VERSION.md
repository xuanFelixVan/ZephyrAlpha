---
module_id: IMPORTANT_PYTHON_VERSION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - IMPORTANT_PYTHON_VERSION文档
---

﻿---
parent_document: ../INDEX.md
responsibility:
  - 交易执行系统设计与优化与实施指导
version: 1.0.0
module_id: EXE_IMPORTANT_PYTHON_VER
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容



---



```
```



```powershell
conda create -n live-analysis python=3.10 -y

conda activate live-analysis

conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

pip install openai-whisper transformers accelerate requests ffmpeg-python

python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

python test_rtx3090_models.py
```


---



```

```


|------|------|--------|--------|


|------|------|

---



```

```


```powershell
ollama pull qwen2.5:32b
```

```

```

---


|------|---------|---------|

---








---



```powershell
conda create -n live-analysis python=3.10 -y
conda activate live-analysis
```


```powershell
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
```


```powershell
pip install openai-whisper transformers accelerate requests ffmpeg-python
```


```powershell
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"
```


```powershell
python test_rtx3090_models.py
```

---