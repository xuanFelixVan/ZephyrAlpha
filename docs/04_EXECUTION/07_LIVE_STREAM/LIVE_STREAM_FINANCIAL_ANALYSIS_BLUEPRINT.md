﻿---
module_id: LIVESTREAMFINANCIALANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 执行团队
responsibility:
  - 蓝图设计、架构规划
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
module_id: LIVE_STREAM_FINANCIAL_ANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
standard_type: 专业量化机构直播金融分析系统标准
容分析与因子生成
compliance_level: 专业机构标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---

> **核心职责**: Live Stream Financial Analysis蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Live Stream Financial Analysis蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


>
容分析与预测因子生成系统
> **技术栈**: DouyinLiveRecorder + Whisper(本地) + Qwen2.5/DeepSeek(本地) + FinBERT(本地)
> **设计原则**: 轻量化、自动化、智能化、可扩展、本地化部署

## 📋 系统概述



### 系统特点

?

### 适用场景

助投资决策
4. **研究机构**: 研究社交媒体对金融市场的影响

---


### 方案对比

| 对比维度 | 云端API方案 | 本地模型方案 | 推荐 |
|---------|------------|-------------|------|
| **


---

### 1. 语音识别模型 (Whisper)

#### 方案A: OpenAI Whisper API（云端）

```python
import openai

def transcribe_with_api(audio_path: str):
    """使用OpenAI Whisper API转录"""
    client = openai.OpenAI(api_key="your-api-key")
    
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh"
        )
    
    return transcript.text
```


#### 方案B: 本地Whisper模型（推荐）

```python
import whisper
import torch

class LocalWhisperTranscriber:
    
    def __init__(self, model_size: str = "medium", device: str = "cuda"):
        """
        初始化本地Whisper模型
        
        Args:
            model_size: 模型大小 (tiny/base/small/medium/large-v3)
            device: 运行设备 (cuda/cpu)
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=self.device)
        
    
    def transcribe(self, audio_path: str, language: str = "zh") -> dict:
        """转录音频"""
        result = self.model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            fp16=False  # CPU推理时使用FP32
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result.get("language", language)
        }

# 使用示例
transcriber = LocalWhisperTranscriber(model_size="medium")
result = transcriber.transcribe("recording.mp3")
```

**模型选择建议**:

|------|--------|---------|------|--------|---------|
| base | 74M | ~1GB | 很快 | 82% | 日常使用 |
| large-v3 | 1550M | ~10GB |


---

### 2.
容分析模型 (大语言模型)

#### 方案A: OpenAI GPT-4 API（云端）

```python
from openai import OpenAI

def analyze_with_gpt4(transcript: str):
    """使用GPT-4分析"""
    client = OpenAI(api_key="your-api-key")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
容：\n{transcript}"}
        ]
    )
    
    return response.choices[0].message.content
```



**选项1: DeepSeek-V3（推荐）**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalDeepSeekAnalyzer:
    
    def __init__(self, model_path: str = "deepseek-ai/deepseek-llm-7b-chat"):
        """
        初始化DeepSeek模型
        
        Args:
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
    
    def analyze(self, transcript: str) -> dict:
容"""

?
{transcript}

{{
    "market_view": "看多/看空/震荡",
    "confidence": 0-10的信心度,
    "sectors": ["推荐板块1", "推荐板块2"],
    "stocks": [
        {{
            "code": "股票代码",
            "name": "股票名称",
"action": "
            "reason": "推荐理由"
        }}
    ],
    "risks": ["风险提示1", "风险提示2"],
"key_points": ["
}}"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 解析JSON响应
        import json
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        json_str = response[json_start:json_end]
        
        return json.loads(json_str)

# 使用示例
analyzer = LocalDeepSeekAnalyzer()
result = analyzer.analyze(transcript_text)
```


```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalQwenAnalyzer:
    
    def __init__(self, model_path: str = "Qwen/Qwen2.5-7B-Instruct"):
        """
        初始化Qwen模型
        
        Args:
            model_path: 模型路径
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
    
    def analyze(self, transcript: str) -> dict:
容"""
        messages = [
            {
                "role": "system",
            },
            {
                "role": "user",
            }
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=2000,
            temperature=0.3
        )
        
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        """解析响应"""
        import json
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except:
            return {
                "market_view": "震荡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": []
            }

# 使用示例
analyzer = LocalQwenAnalyzer()
result = analyzer.analyze(transcript_text)
```

**选项3: Ollama本地部署（最简单）**

```python
import requests
import json

class OllamaAnalyzer:
    
    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        """
        
        Args:
            base_url: Ollama服务地址
        """
        self.model_name = model_name
        self.base_url = base_url
        
    
    def analyze(self, transcript: str) -> dict:
容"""

?
{transcript}

{{
    "market_view": "看多/看空/震荡",
    "confidence": 0-10的信心度,
    "sectors": ["推荐板块1", "推荐板块2"],
    "stocks": [],
    "risks": [],
    "key_points": []
}}"""
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2000
                }
            }
        )
        
        result = response.json()
        response_text = result["response"]
        
        # 解析JSON
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except:
            return {
                "market_view": "震荡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": []
            }

# 使用示例
#
Ollama: https://ollama.ai/
# 然后拉取模型: ollama pull qwen2.5:7b
# 启动服务: ollama serve

analyzer = OllamaAnalyzer(model_name="qwen2.5:7b")
result = analyzer.analyze(transcript_text)
```

**模型选择建议**:

|------|--------|---------|---------|---------|--------|
?|


---

### 3.
感分析模型 (FinBERT)


```python
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

class LocalFinBERTAnalyzer:
"""FinBERT
?""
    
    def __init__(self, model_path: str = "yiyanghkust/finbert-tone"):
        """
        初始化FinBERT模型
        
        Args:
            model_path: 模型路径
        """
        self.device = 0 if torch.cuda.is_available() else -1
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device
        )
        
    
    def analyze_sentiment(self, text: str) -> dict:
"""
感分析"""
        max_length = 512
        segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        sentiments = []
        for segment in segments:
            result = self.sentiment_pipeline(segment)
            sentiments.append(result[0])
        
感分布
        positive_count = sum(1 for s in sentiments if s['label'] == 'Positive')
        negative_count = sum(1 for s in sentiments if s['label'] == 'Negative')
        neutral_count = sum(1 for s in sentiments if s['label'] == 'Neutral')
        
        total = len(sentiments)
        
        if positive_count > negative_count and positive_count > neutral_count:
            dominant_sentiment = "Positive"
            confidence = positive_count / total
        elif negative_count > positive_count and negative_count > neutral_count:
            dominant_sentiment = "Negative"
            confidence = negative_count / total
        else:
            dominant_sentiment = "Neutral"
            confidence = neutral_count / total
        
        return {
            "sentiment": dominant_sentiment,
            "confidence": confidence,
            "distribution": {
                "positive": positive_count / total,
                "negative": negative_count / total,
                "neutral": neutral_count / total
            }
        }

# 使用示例
analyzer = LocalFinBERTAnalyzer()
result = analyzer.analyze_sentiment(transcript_text)
```


---

置建议

####

```
CPU: Intel i5-12400 / AMD Ryzen 5 5600
存: 16GB DDR4
显卡: NVIDIA RTX 3060 12GB
存储: 500GB NVMe SSD
?

支持模型:
- Whisper: small/medium
- FinBERT:
```

####

```
CPU: Intel i7-13700K / AMD Ryzen 7 7800X3D
存: 32GB DDR5
显卡: NVIDIA RTX 4070 Ti Super 16GB
存储: 1TB NVMe SSD
?

支持模型:
- Whisper: medium/large-v3
- FinBERT:
```


```
CPU: Intel i9-14900K / AMD Ryzen 9 7950X
存: 64GB DDR5
显卡: NVIDIA RTX 4090 24GB
存储: 2TB NVMe SSD
?

支持模型:
- Whisper: large-v3（实时转录）
- FinBERT:
```

---

### 5. 成本对比分析


```

Whisper API成本:
- 365? $3.6 = $1,314/?

GPT-4 API成本:
- 365? $30 = $10,950/?

```


```
:
- RTX 4070 Ti Super: 8,000
-

电费成本:



相比云端API节省: 88,000 - 15,657 = 72,343（第一年）
```


---

### 6. 部署流程

#### 步骤1: 环境准备

```bash
#
Python 3.10+
conda create -n live-analysis python=3.10
conda activate live-analysis

#
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

#
Transformers
pip install transformers accelerate

#
Whisper
pip install openai-whisper

#
pip install ffmpeg-python DrissionPage
```

#### 步骤2: 下载模型

```bash
# 下载Whisper模型
python -c "import whisper; whisper.load_model('medium')"

# 下载Qwen模型
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-7B-Instruct')"

# 下载FinBERT模型
python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```


```yaml
# config.yaml
models:
  whisper:
    type: "local"  # local / api
    model_size: "medium"
    device: "cuda"
  
  llm:
    type: "local"  # local / api
    model_name: "Qwen/Qwen2.5-7B-Instruct"
    device: "cuda"
  
  sentiment:
    type: "local"
    model_name: "yiyanghkust/finbert-tone"
    device: "cuda"
```

#### 步骤4: 运行系统

```bash
python main.py
```

---

### 7. 模型优化建议

#### ?

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 4-bit
置
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
```

****:

#### 模型微调

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./finetuned_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-5
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=your_dataset
)

trainer.train()
```

---


置**: RTX 3090 24GB + 64GB RAM + i7-12700KF
> **
?
> **创建日期**: 2026-04-02


```
?

足

足

?
```

### 已有Ollama模型分析

|------|------|--------|--------|
| qwen3:8b | 5.2GB | ?
容分析 | ⭐⭐⭐⭐ |
| deepseek-r1:8b | 5.2GB | ?
容分析 | ⭐⭐⭐⭐ |
| **deepseek-r1:14b** | 9.0GB |


```
?
?

```


```bash
# 拉取命令
ollama pull qwen2.5:32b
```

```
?
?

```

### 性能对比

|---------|--------|------|------|--------|

### 成本对比

|------|---------|-----------|----------|
| 云端API | 0 | 88,000 | 88,000 |
| 本地模型（现有） | 0 | 657 | 657 |
| 本地模型（升级） | 0 | 1,000 | 1,000 |


###

```yaml
# config_local_rtx3090.yaml
models:
  whisper:
    type: "local"
    model_size: "large-v3"
    device: "cuda"
  
  llm:
    type: "ollama"
model_name: "deepseek-r1:14b"  # ?"qwen2.5:32b"
    base_url: "http://localhost:11434"
  
  sentiment:
    type: "local"
    model_name: "yiyanghkust/finbert-tone"
    device: "cuda"
```

### 部署步骤

```bash
# 1. 拉取Whisper large-v3
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 2. 拉取FinBERT
python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"

# 3. （可选）拉取更大模型
ollama pull qwen2.5:32b

# 4. 运行部署脚本
.\deploy_rtx3090.ps1

# 5. 启动系统
python main.py
```

###

- [
- [部署脚本（PowerShell）](./deploy_rtx3090.ps1)
- [部署脚本（Bash）](./deploy_rtx3090.sh)

---



```
? ?       LiveStreamFinancialApplication                 ? ?
?
?
?
? ?(
```


```
?
?(DrissionPage)?
?
?(FFmpeg)     ?
?
?(Whisper)    ?
?
?
?(GPT-4)      ?
?
?
??FinBERT
?(FinBERT)    ?
?
?(Aggregator) ?
?
?(Factor Gen) ?
?
?(Output)     ?
```

---

## 📦 模块详细设计


#### 1.1 功能职责

- 只录制MP3音频格式
- 获取直播间实时数据（在线人数、直播间标题等）



使用DrissionPage监听直播间状态：

```python
from DrissionPage import ChromiumPage
import time
import asyncio
from typing import Dict, List
import logging

class DouyinLiveMonitor:
    """抖音直播间监控器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.page = ChromiumPage()
        self.logger = logging.getLogger(__name__)
        self.monitored_rooms = {}
    
    async def start_monitoring(self, streamer_list: List[Dict]):
        for streamer in streamer_list:
            asyncio.create_task(
                self._monitor_single_streamer(streamer)
            )
    
    async def _monitor_single_streamer(self, streamer: Dict):
        """监控单个主播"""
        while True:
            try:
                is_live = await self._check_live_status(streamer["url"])
                
                if is_live:
                    live_data = await self._get_live_room_data(streamer["url"])
                    
                    # 触发录制事件
                    await self._on_streamer_live(streamer, live_data)
                
#
                await asyncio.sleep(self.config["check_interval"])
                
            except Exception as e:
                self.logger.error(f"监控主播 {streamer['name']} 失败: {e}")
                await asyncio.sleep(60)
    
    async def _check_live_status(self, live_url: str) -> bool:
        try:
            self.page.get(live_url)
            time.sleep(2)
            
            # 检查是否有直播标识
            live_indicator = self.page.ele('css:.live-badge', timeout=3)
            return live_indicator is not None
            
        except Exception as e:
            return False
    
    async def _get_live_room_data(self, live_url: str) -> Dict:
        try:
            self.page.get(live_url)
            time.sleep(3)
            
            # 提取在线人数
            online_element = self.page.ele('css:.live-room-online-count', timeout=5)
            online_count = self._parse_count(online_element.text) if online_element else 0
            
            title_element = self.page.ele('css:.room-title', timeout=5)
            title = title_element.text if title_element else ""
            
            # 提取主播名称
            streamer_element = self.page.ele('css:.streamer-name', timeout=5)
            streamer_name = streamer_element.text if streamer_element else ""
            
            return {
                "online_count": online_count,
                "title": title,
                "streamer_name": streamer_name,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {}
    
    def _parse_count(self, count_text: str) -> int:
        try:
            count_text = count_text.strip()
            
if '? in count_text:
return int(float(count_text.replace('?, '')) * 10000)
elif '? in count_text:
return int(float(count_text.replace('?, '')) * 100000000)
            else:
                return int(count_text)
        except:
            return 0
    
    async def _on_streamer_live(self, streamer: Dict, live_data: Dict):
        self.logger.info(f"主播 {streamer['name']} 已开播，在线人数: {live_data['online_count']}")
        
        # 触发录制任务
        pass
```



```python
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Optional
import logging

class AudioRecorder:
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_path = config.get("ffmpeg_path", "ffmpeg")
        self.output_dir = Path(config.get("output_dir", "./recordings"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def record_audio(
        self,
        stream_url: str,
        streamer_name: str,
        duration: int = 3600,
        output_format: str = "mp3",
        bitrate: str = "128k"
    ) -> Optional[str]:
        """
        录制音频
        
        Args:
            stream_url: 直播流地址
            streamer_name: 主播名称
        
        Returns:
            录制文件路径
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{streamer_name}_{timestamp}.{output_format}"
            
            # 构建FFmpeg命令
            cmd = [
                self.ffmpeg_path,
"-i", stream_url,              #
?
                "-vn",                          # 忽略视频
"-c:a", "libmp3lame",          # MP3?
"-b:a", bitrate,               # ?
                "-t", str(duration),           # 录制时长
                str(output_file)
            ]
            
            
            # 异步执行录制
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
#
录制完成
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"录制完成: {output_file}")
                return str(output_file)
            else:
                self.logger.error(f"录制失败: {stderr.decode()}")
                return None
                
        except Exception as e:
            self.logger.error(f"录制异常: {e}")
            return None
    
    async def record_segmented(
        self,
        stream_url: str,
        streamer_name: str,
        segment_duration: int = 1800,
        total_duration: int = 7200
    ) -> list:
        """
        分段录制音频
        
        Args:
            stream_url: 直播流地址
            streamer_name: 主播名称
            total_duration: 总时长（秒）
        
        Returns:
            录制文件列表
        """
        recorded_files = []
        segments = total_duration // segment_duration
        
        for i in range(segments):
            output_file = await self.record_audio(
                stream_url=stream_url,
                streamer_name=f"{streamer_name}_part{i+1}",
                duration=segment_duration
            )
            
            if output_file:
                recorded_files.append(output_file)
        
        return recorded_files
```

---

### 2:

#### 2.1 功能职责

-
-
感分析



```python
import whisper
from typing import Dict, List
import logging
import time

class AudioTranscriber:
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 加载Whisper模型
        model_size = config.get("whisper_model", "base")
        self.logger.info(f"加载Whisper模型: {model_size}")
        self.model = whisper.load_model(model_size)
    
    async def transcribe(
        self,
        audio_path: str,
        language: str = "zh"
    ) -> Dict:
        """
        转录音频
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            转录结果
        """
        try:
            start_time = time.time()
            
            
            # 使用Whisper转录
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe"
            )
            
            transcript = result["text"]
            segments = [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
            
            elapsed_time = time.time() - start_time
            
            
            return {
                "text": transcript,
                "segments": segments,
                "language": result.get("language", language),
                "duration": elapsed_time
            }
            
        except Exception as e:
            self.logger.error(f"转录失败: {e}")
            return {
                "text": "",
                "segments": [],
                "error": str(e)
            }
    
    async def transcribe_batch(
        self,
        audio_files: List[str],
        language: str = "zh"
    ) -> List[Dict]:
        """批量转录音频"""
        results = []
        
        for audio_file in audio_files:
            result = await self.transcribe(audio_file, language)
            results.append(result)
        
        return results
```

**

```python
from openai import OpenAI
from typing import Dict, List
import json
import logging

class FinancialContentAnalyzer:
"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.client = OpenAI(
            api_key=config["openai_api_key"],
            base_url=config.get("openai_base_url", "https://api.openai.com/v1")
        )
        
        self.model = config.get("openai_model", "gpt-4")
    
    async def extract_key_points(
        self,
        transcript: str,
        streamer_name: str = ""
    ) -> Dict:
        """
        
        Args:
            transcript: 转录文本
            streamer_name: 主播名称
        
        Returns:
        """
        try:
            prompt = f"""

主播名称: {streamer_name}
容:
{transcript}


{{
    "market_view": "看多/看空/震荡",
    "confidence": 0-10的信心度,
    "sectors": ["推荐板块1", "推荐板块2"],
    "stocks": [
        {{
            "code": "股票代码",
            "name": "股票名称",
"action": "
            "price": "建议价格",
            "reason": "推荐理由"
        }}
    ],
    "risks": ["风险提示1", "风险提示2"],
"key_points": ["
    "timeframe": "短期/中期/长期"
}}

1. market_view
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析JSON响应
            content = response.choices[0].message.content
            
            # 提取JSON部分
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content
            
            result = json.loads(json_str)
            
            
            return result
            
        except Exception as e:
            self.logger.error(f"观点提取失败: {e}")
            return {
                "market_view": "震荡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": [],
                "timeframe": "短期",
                "error": str(e)
            }
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
感分析
        
        Args:
text:
?
        
        Returns:
感分析结果
        """
        try:
            from transformers import pipeline
            
感分析模型
            sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="yiyanghkust/finbert-tone",
                device=-1  # CPU
            )
            
            max_length = 512
            segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            sentiments = []
            for segment in segments:
                result = sentiment_analyzer(segment)
                sentiments.append(result[0])
            
#
感
            positive_count = sum(1 for s in sentiments if s['label'] == 'Positive')
            negative_count = sum(1 for s in sentiments if s['label'] == 'Negative')
            neutral_count = sum(1 for s in sentiments if s['label'] == 'Neutral')
            
            total = len(sentiments)
            
            if positive_count > negative_count and positive_count > neutral_count:
                dominant_sentiment = "Positive"
                confidence = positive_count / total
            elif negative_count > positive_count and negative_count > neutral_count:
                dominant_sentiment = "Negative"
                confidence = negative_count / total
            else:
                dominant_sentiment = "Neutral"
                confidence = neutral_count / total
            
            return {
                "sentiment": dominant_sentiment,
                "confidence": confidence,
                "distribution": {
                    "positive": positive_count / total,
                    "negative": negative_count / total,
                    "neutral": neutral_count / total
                }
            }
            
        except Exception as e:
self.logger.error(f"
感分析失败: {e}")
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "error": str(e)
            }
```

---


#### 3.1 功能职责

- 生成预测因子



```python
from typing import List, Dict
from collections import Counter
import numpy as np
import logging

class OpinionAggregator:
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.opinions = []
    
    def add_opinion(
        self,
        streamer_name: str,
        opinion: Dict,
        weight: float = 1.0,
        online_count: int = 0
    ):
        """
        添加主播观点
        
        Args:
            streamer_name: 主播名称
            opinion: 观点数据
            weight: 权重
            online_count: 在线人数
        """
        self.opinions.append({
            "streamer": streamer_name,
            "opinion": opinion,
            "weight": weight,
            "online_count": online_count,
            "timestamp": time.time()
        })
        
    
    def aggregate(self) -> Dict:
        """
        
        Returns:
            聚合结果
        """
        if not self.opinions:
            return {
                "dominant_view": "震荡",
                "consensus_ratio": 0,
                "total_streamers": 0
            }
        
        # 统计大盘看法
        view_scores = {"看多": 0.0, "看空": 0.0, "震荡": 0.0}
        
        for item in self.opinions:
            view = item["opinion"]["market_view"]
            confidence = item["opinion"]["confidence"]
            weight = item["weight"]
            
            # 加权投票
            score = weight * confidence / 10.0
            view_scores[view] += score
        
        # 确定主流观点
        dominant_view = max(view_scores, key=view_scores.get)
        total_score = sum(view_scores.values())
        consensus_ratio = view_scores[dominant_view] / total_score if total_score > 0 else 0
        
        # 统计推荐板块
        all_sectors = []
        for item in self.opinions:
            all_sectors.extend(item["opinion"].get("sectors", []))
        
        sector_counts = Counter(all_sectors)
        top_sectors = sector_counts.most_common(10)
        
        # 统计推荐个股
        all_stocks = []
        for item in self.opinions:
            all_stocks.extend(item["opinion"].get("stocks", []))
        
        stock_counts = Counter([s["code"] for s in all_stocks if "code" in s])
        top_stocks = stock_counts.most_common(10)
        
        avg_confidence = np.mean([item["opinion"]["confidence"] for item in self.opinions])
        
        # 计算平均在线人数
        avg_online_count = np.mean([item["online_count"] for item in self.opinions])
        
        return {
            "dominant_view": dominant_view,
            "consensus_ratio": consensus_ratio,
            "view_distribution": view_scores,
            "top_sectors": top_sectors,
            "top_stocks": top_stocks,
            "avg_confidence": avg_confidence,
            "avg_online_count": avg_online_count,
            "total_streamers": len(self.opinions)
        }
    
    def clear(self):
"""
空观点"""
        self.opinions = []
?)
```


```python
from typing import Dict
import numpy as np
import logging

class FactorGenerator:
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_factors(
        self,
        aggregated_opinion: Dict,
        market_data: Dict = None
    ) -> Dict:
        """
        生成预测因子
        
        Args:
            aggregated_opinion: 聚合观点
            market_data: 市场数据（可选）
        
        Returns:
            预测因子
        """
        try:
# 1.
            sentiment_factor = self._calculate_sentiment_factor(
                aggregated_opinion["dominant_view"],
                aggregated_opinion["consensus_ratio"]
            )
            
            consensus_factor = aggregated_opinion["consensus_ratio"]
            
            # 3. 影响力因子（基于主播数量和在线人数）
            influence_factor = self._calculate_influence_factor(
                aggregated_opinion["total_streamers"],
                aggregated_opinion["avg_online_count"]
            )
            
            confidence_factor = aggregated_opinion["avg_confidence"] / 10.0
            
            # 5. 板块热度因子
            sector_factors = self._calculate_sector_factors(
                aggregated_opinion["top_sectors"],
                aggregated_opinion["total_streamers"]
            )
            
            # 6. 综合因子（加权平均）
            composite_factor = self._calculate_composite_factor(
                sentiment_factor=sentiment_factor,
                consensus_factor=consensus_factor,
                influence_factor=influence_factor,
                confidence_factor=confidence_factor
            )
            
            return {
                "sentiment_factor": sentiment_factor,
                "consensus_factor": consensus_factor,
                "influence_factor": influence_factor,
                "confidence_factor": confidence_factor,
                "sector_factors": sector_factors,
                "composite_factor": composite_factor,
                "metadata": {
                    "dominant_view": aggregated_opinion["dominant_view"],
                    "total_streamers": aggregated_opinion["total_streamers"],
                    "avg_online_count": aggregated_opinion["avg_online_count"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"因子生成失败: {e}")
            return {}
    
    def _calculate_sentiment_factor(
        self,
        dominant_view: str,
        consensus_ratio: float
    ) -> float:
绪因子"""
        if dominant_view == "看多":
            return consensus_ratio
        elif dominant_view == "看空":
            return -consensus_ratio
        else:
            return 0.0
    
    def _calculate_influence_factor(
        self,
        total_streamers: int,
        avg_online_count: float
    ) -> float:
        streamer_factor = min(total_streamers / 10.0, 1.0)
        
        online_factor = min(avg_online_count / 100000.0, 1.0)
        
        influence_factor = (streamer_factor * 0.6 + online_factor * 0.4)
        
        return influence_factor
    
    def _calculate_sector_factors(
        self,
        top_sectors: list,
        total_streamers: int
    ) -> Dict[str, float]:
        """计算板块热度因子"""
        sector_factors = {}
        
        for sector, count in top_sectors:
            # 热度 = 提及次数 / 主播数量
            sector_factors[sector] = count / total_streamers
        
        return sector_factors
    
    def _calculate_composite_factor(
        self,
        sentiment_factor: float,
        consensus_factor: float,
        influence_factor: float,
        confidence_factor: float
    ) -> float:
        """计算综合因子"""
#
置
        weights = self.config.get("factor_weights", {
            "sentiment": 0.4,
            "consensus": 0.3,
            "influence": 0.2,
            "confidence": 0.1
        })
        
        # 加权平均
        composite = (
            sentiment_factor * weights["sentiment"] +
            consensus_factor * weights["consensus"] +
            influence_factor * weights["influence"] +
            confidence_factor * weights["confidence"]
        )
        
        return composite
```

---

## 🔄 完整系统集成

### 主系统类

```python
import asyncio
import logging
from typing import List, Dict
from datetime import datetime
import json

class LiveStreamFinancialSystem:
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化各模块
        self.monitor = DouyinLiveMonitor(config["monitor"])
        self.recorder = AudioRecorder(config["recorder"])
        self.transcriber = AudioTranscriber(config["transcriber"])
        self.analyzer = FinancialContentAnalyzer(config["analyzer"])
        self.aggregator = OpinionAggregator(config["aggregator"])
        self.factor_generator = FactorGenerator(config["factor_generator"])
        
        # 结果存储
        self.results = []
    
    async def run(self, streamer_list: List[Dict]):
        """
        运行系统
        
        Args:
            streamer_list: 主播列表
        """
        
        # 启动监控任务
        tasks = []
        for streamer in streamer_list:
            task = asyncio.create_task(
                self._process_streamer(streamer)
            )
            tasks.append(task)
        
#
        await asyncio.gather(*tasks)
        
        final_factors = await self._generate_final_factors()
        
        return final_factors
    
    async def _process_streamer(self, streamer: Dict):
        """处理单个主播"""
        try:
            
            is_live = await self.monitor._check_live_status(streamer["url"])
            
            if not is_live:
                return
            
            live_data = await self.monitor._get_live_room_data(streamer["url"])
            
            # 3. 获取直播流地址
            stream_url = await self._get_stream_url(streamer["url"])
            
            if not stream_url:
                self.logger.error(f"无法获取直播流地址: {streamer['name']}")
                return
            
            # 4. 录制音频
            audio_path = await self.recorder.record_audio(
                stream_url=stream_url,
                streamer_name=streamer["name"],
                duration=streamer.get("duration", 3600)
            )
            
            if not audio_path:
                self.logger.error(f"录制失败: {streamer['name']}")
                return
            
            # 5. 转录音频
            transcript = await self.transcriber.transcribe(audio_path)
            
            if not transcript["text"]:
                self.logger.error(f"转录失败: {streamer['name']}")
                return
            
# 6.
            key_points = await self.analyzer.extract_key_points(
                transcript["text"],
                streamer["name"]
            )
            
# 7.
感分析
            sentiment = await self.analyzer.analyze_sentiment(transcript["text"])
            
            # 8. 添加到聚合器
            self.aggregator.add_opinion(
                streamer_name=streamer["name"],
                opinion={
                    **key_points,
                    "sentiment": sentiment
                },
                weight=streamer.get("weight", 1.0),
                online_count=live_data.get("online_count", 0)
            )
            
            # 9. 保存结果
            result = {
                "streamer": streamer["name"],
                "live_data": live_data,
                "transcript": transcript,
                "key_points": key_points,
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            self.logger.info(f"主播 {streamer['name']} 处理完成")
            
        except Exception as e:
            self.logger.error(f"处理主播 {streamer['name']} 失败: {e}")
    
    async def _get_stream_url(self, live_url: str) -> str:
        """获取直播流地址"""
        # 这里需要实现获取直播流地址的逻辑
        # 可以使用DouyinLiveRecorder中的stream.py模块
        pass
    
    async def _generate_final_factors(self) -> Dict:
        # 聚合观点
        aggregated = self.aggregator.aggregate()
        
        # 生成因子
        factors = self.factor_generator.generate_factors(aggregated)
        
?
        factors["timestamp"] = datetime.now().isoformat()
        factors["streamer_count"] = len(self.results)
        
        return factors
    
    def save_results(self, output_path: str):
        """保存结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
```

---

##

### config.yaml

```yaml
置
system:
  version: "1.0.0"
  log_level: "INFO"

#
置
monitor:
  check_interval: 60  # 检查间隔（秒）
  headless: true  # 无头模式

#
置
recorder:
  output_dir: "./recordings"
  audio_format: "mp3"
  bitrate: "128k"
  sample_rate: 44100

置
transcriber:
  whisper_model: "base"  # tiny/base/small/medium/large
  language: "zh"

#
置
analyzer:
  openai_api_key: "${OPENAI_API_KEY}"
  openai_base_url: "https://api.openai.com/v1"
  openai_model: "gpt-4"
  sentiment_model: "yiyanghkust/finbert-tone"

#
置
aggregator:

#
置
factor_generator:
  factor_weights:
    sentiment: 0.4
    consensus: 0.3
    influence: 0.2
    confidence: 0.1

#
置
output:
  result_dir: "./results"
  factor_output: "./factors"
  save_transcript: true
  save_audio: false
```

### streamer_list.json

```json
{
  "streamers": [
    {
      "name": "股神老王",
      "url": "https://live.douyin.com/745964462470",
      "schedule": {
        "start_time": "19:00",
        "end_time": "21:00"
      },
      "weight": 1.5,
      "duration": 3600
    },
    {
      "name": "财经小李",
      "url": "https://live.douyin.com/yall1102",
      "schedule": {
        "start_time": "20:00",
        "end_time": "22:00"
      },
      "weight": 1.0,
      "duration": 3600
    },
    {
      "name": "投资达人",
      "url": "https://live.douyin.com/123456789",
      "schedule": {
        "start_time": "18:00",
        "end_time": "20:00"
      },
      "weight": 0.8,
      "duration": 3600
    }
  ]
}
```

---

## 🚀 部署方案

### 方案一: 本地部署

```bash
# 1.
git clone https://github.com/your-repo/live-stream-financial-analysis.git
cd live-stream-financial-analysis

# 2.
依赖
pip install -r requirements.txt

# 3.
FFmpeg
# Windows: 下载 https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 4.
export OPENAI_API_KEY="your-api-key"

# 5. 运行系统
python main.py
```


```dockerfile
FROM python:3.10-slim

WORKDIR /app

#
系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*

#
Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 运行
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yaml
version: '3.8'

services:
  live-analyzer:
    build: .
    volumes:
      - ./recordings:/app/recordings
      - ./results:/app/results
      - ./config:/app/config
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

---

## 📈 使用示例

### 启动系统

```python
import asyncio
import yaml
from live_stream_financial_system import LiveStreamFinancialSystem

async def main():
置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 加载主播列表
    with open('streamer_list.json', 'r', encoding='utf-8') as f:
        streamer_data = json.load(f)
    
    system = LiveStreamFinancialSystem(config)
    
    # 运行系统
    factors = await system.run(streamer_data["streamers"])
    
    # 输出结果
    print("=== 预测因子 ===")
    print(f"综合因子: {factors['composite_factor']:.3f}")
print(f"
绪因子: {factors['sentiment_factor']:.3f}")
print(f"? {factors['consensus_factor']:.2%}")
print(f"? {factors['influence_factor']:.3f}")
    print(f"热门板块: {list(factors['sector_factors'].keys())[:5]}")
    
    # 保存结果
    system.save_results(f"./results/result_{datetime.now().strftime('%Y%m%d')}.json")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 输出示例

### 因子输出

```json
{
  "sentiment_factor": 0.72,
  "consensus_factor": 0.78,
  "influence_factor": 0.85,
  "confidence_factor": 0.68,
  "sector_factors": {
    "人工智能": 0.65,
    "医药": 0.35,
    "消费": 0.28
  },
  "composite_factor": 0.734,
  "metadata": {
    "dominant_view": "看多",
    "total_streamers": 10,
    "avg_online_count": 125000
  },
  "timestamp": "2026-04-02T20:30:00"
}
```

---

## 🔧 扩展功能

### 1. 定时任务

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def scheduled_analysis():
    """定时分析任务"""
    scheduler = AsyncIOScheduler()
    
    # 每天19:00执行
    scheduler.add_job(
        run_analysis,
        'cron',
        hour=19,
        minute=0
    )
    
    scheduler.start()
```

### 2. Web界面

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/factors")
async def get_factors():
    return JSONResponse(content=latest_factors)

@app.get("/streamers")
async def get_streamers():
    """获取主播列表"""
    return JSONResponse(content=streamer_list)
```


```python
import asyncpg

async def save_to_database(factors: Dict):
    """保存因子到数据库"""
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='live_analysis'
    )
    
    await conn.execute('''
        INSERT INTO factors (
            timestamp, sentiment_factor, consensus_factor,
            influence_factor, composite_factor
        ) VALUES ($1, $2, $3, $4, $5)
    ''',
        factors['timestamp'],
        factors['sentiment_factor'],
        factors['consensus_factor'],
        factors['influence_factor'],
        factors['composite_factor']
    )
    
    await conn.close()
```

---

## 📝 注意事项

### 1. 法律合规

- ⚠️ 请遵守抖音平台的使用条款
用于个人学习和研究

### 2. ?

- ⚠️ 非官方API可能随时失效
- ⚠️ 需要稳定的网络环境
- ⚠️ Whisper转录需要足够的计算资源

### 3. 数据质量


---

## 🎯 未来优化方向

1. **性能优化**
   - 使用GPU加速Whisper转录
   - 优化并发处理能力
   - 实现增量转录

2. **功能扩展**
   - 支持更多直播平台
   - 添加实时因子更新
   - 实现因子回测

   - 训练专门的金融领域Whisper模型
   - 优化观点提取prompt

---

---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Live Stream Financial Analysis
- **模块ID**: LIVE_STREAM_FINANCIAL_ANALYSIS_001
- **蓝图文档**: [LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md](04_EXECUTION\07_LIVE_STREAM\LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 
容分析与因子生成
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-02 | **状态**: Active
