---
module_id: 04_EXECUTION_07_LIVE_STREAM_PYTHON_VERSION_FIX
layer: layer_04
version: 1.0.0
status: Active
responsibility:
  - Python Version Fix相关业务
parent_document: ../INDEX.md
created_date: 2026-04-02
last_updated: 2026-04-07
owner: 首席文档架构师
---

```powershell

conda create -n live-analysis python=3.10 -y



conda activate live-analysis



python --version

```





```powershell

conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y



pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

```





```powershell

pip install openai-whisper transformers accelerate requests ffmpeg-python

```





```powershell

python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

```



```
```---
```













```powershell

py -3.12 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121



py -3.12 -m pip install openai-whisper transformers accelerate requests ffmpeg-python

```



```
```---
```







```powershell

pip install torch torchvision torchaudio



pip install openai-whisper



pip install transformers accelerate requests ffmpeg-python

```





```
```---
```





|------|------|------|--------|



```
```---
```





```powershell

conda create -n live-analysis python=3.10 -y



conda activate live-analysis



conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y



pip install openai-whisper transformers accelerate requests ffmpeg-python



python -c "import whisper; whisper.load_model('large-v3', device='cuda')"



python test_rtx3090_models.py

```



```
```---
```







```powershell

conda activate live-analysis

python test_rtx3090_models.py

```





```



```



```
```---
```









```powershell

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/

conda config --set show_channel_urls yes

```







```powershell

nvidia-smi



# CUDA 12.1: pytorch-cuda=12.1

# CUDA 11.8: pytorch-cuda=11.8

```







```powershell

$env:HF_ENDPOINT = "https://hf-mirror.com"



python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

```



```
```---
```
