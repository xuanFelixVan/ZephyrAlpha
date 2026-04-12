---
module_id: 04_EXECUTION_07_LIVE_STREAM_IMPORTANT_PYTHON_VERSION
layer: layer_04
version: 1.0.0
status: Active
responsibility:
  - Important Python Version相关业务
parent_document: ../INDEX.md
created_date: 2026-04-02
last_updated: 2026-04-07
owner: 首席文档架构师
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

