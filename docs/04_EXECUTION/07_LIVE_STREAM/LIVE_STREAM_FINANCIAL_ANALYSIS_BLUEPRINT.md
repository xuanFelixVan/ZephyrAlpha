---
module_id: LIVESTREAMFINANCIALANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 执行团队
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: LIVE_STREAM_FINANCIAL_ANALYSIS_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: é¦å¸­èå¾æ¶æå¸?
standard_type: ä¸ä¸éåæºæç´æ­éèåæç³»ç»æ å
applicable_scope: å¤ä¸»æ­ç´æ­åå®¹åæä¸å å­çæ
compliance_level: ä¸ä¸æºææ å
parent_document: ../INDEX.md
implementation_status: è®¾è®¡é¶æ®µ
---

# å¤ä¸»æ­ç´æ­éèåæç³»ç»èå?

> æ¸é£éåç³»ç» v5.0 - å¤ä¸»æ­ç´æ­åå®¹åæä¸é¢æµå å­çæç³»ç»
> **æ ¸å¿åè½**: çæ§å¤ä¸ªæé³ä¸»æ­ç´æ­ â?å½å¶MP3é³é¢ â?AIåå®¹åæ â?è§ç¹èå â?çæé¢æµå å­
> **ææ¯æ **: DouyinLiveRecorder + Whisper(æ¬å°) + Qwen2.5/DeepSeek(æ¬å°) + FinBERT(æ¬å°)
> **è®¾è®¡åå**: è½»éåãèªå¨åãæºè½åãå¯æ©å±ãæ¬å°åé¨ç½²
> **æ¨èæ¹æ¡**: â?æ¬å°æ¨¡åé¨ç½²ï¼éåé¿æé¡¹ç®ï¼ææ¬æ´ä½ï¼éç§æ´å®å¨ï¼

## ð ç³»ç»æ¦è¿°

### æ ¸å¿ä»·å?

æ¬ç³»ç»éè¿çæ§å¤ä¸ªæé³éèä¸»æ­çç´æ­åå®¹ï¼å©ç¨AIææ¯æåå³é®è§ç¹ï¼è¿è¡å¤ç»´åº¦åæï¼æç»çæå¯ç¨äºéåäº¤æçé¢æµå å­ãç³»ç»è§£å³äºä¼ ç»éèåæä¸­ä¿¡æ¯è·åæ»åãåä¸è§ç¹åè§ãäººå·¥åææçä½ç­é®é¢ã?

### ç³»ç»ç¹ç¹

- â?**è½»éå?*: åªå½å¶MP3é³é¢ï¼èç?0%å­å¨ç©ºé´
- â?**èªå¨å?*: 24å°æ¶èªå¨çæ§ãå½å¶ãåæ?
- â?**æºè½å?*: AIèªå¨è½¬å½ãæåè§ç¹ãææåæ?
- â?**å¤æºèå**: èåå¤ä¸ªä¸»æ­è§ç¹ï¼æé«é¢æµåç¡®æ?
- â?**å å­çæ**: ç´æ¥çæå¯ç¨äºéåäº¤æçé¢æµå å­

### éç¨åºæ¯

1. **ä¸ªäººæèµè?*: è·åå¤ç»´åº¦å¸åºè§ç¹ï¼è¾å©æèµå³ç­
2. **éåäº¤æè?*: å°ä¸»æ­è§ç¹è½¬åä¸ºå¯éåçäº¤æå å­
3. **éèåæå¸?*: è¿½è¸ªå¸åºæç»ªï¼éªè¯åæç»è®?
4. **ç ç©¶æºæ**: ç ç©¶ç¤¾äº¤åªä½å¯¹éèå¸åºçå½±å

---

## ð¤ æ¨¡åéæ©ä¸é¨ç½²æ¹æ¡?

### æ¹æ¡å¯¹æ¯

| å¯¹æ¯ç»´åº¦ | äºç«¯APIæ¹æ¡ | æ¬å°æ¨¡åæ¹æ¡ | æ¨è |
|---------|------------|-------------|------|
| **ææ¬** | ææ¬¡ä»è´¹ï¼é¿æææ¬é« | ä¸æ¬¡æ§ç¡¬ä»¶æå¥ï¼é¿æææ¬ä½?| â?æ¬å°æ¨¡å |
| **éç§** | æ°æ®ä¸ä¼ äºç«¯ï¼éç§é£é?| æ°æ®æ¬å°å¤çï¼éç§å®å?| â?æ¬å°æ¨¡å |
| **ç¨³å®æ?* | ä¾èµç½ç»åAPIæå¡ | æ¬å°è¿è¡ï¼ç¨³å®æ§é« | â?æ¬å°æ¨¡å |
| **éåº¦** | åç½ç»å½±åï¼å»¶è¿é«?| æ¬å°æ¨çï¼éåº¦å¿?| â?æ¬å°æ¨¡å |
| **å¯å®å?* | åéï¼æ æ³å¾®è°?| å¯èªç±å¾®è°åä¼å | â?æ¬å°æ¨¡å |
| **é¨ç½²é¾åº¦** | ç®åï¼å³å¼å³ç¨ | éè¦ç¡¬ä»¶åææ?| â ï¸ äºç«¯API |
| **åå§æå¥** | ä½ï¼æéä»è´¹ï¼?| é«ï¼ç¡¬ä»¶éè´­ï¼?| â ï¸ äºç«¯API |

**æ¨èæ¹æ¡**: â?**æ¬å°æ¨¡åæ¹æ¡**ï¼éåé¿æé¡¹ç®ï¼?

---

### 1. è¯­é³è¯å«æ¨¡å (Whisper)

#### æ¹æ¡A: OpenAI Whisper APIï¼äºç«¯ï¼

```python
import openai

def transcribe_with_api(audio_path: str):
    """ä½¿ç¨OpenAI Whisper APIè½¬å½"""
    client = openai.OpenAI(api_key="your-api-key")
    
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh"
        )
    
    return transcript.text
```

**ææ¬**: $0.006/åéï¼?å°æ¶ç´æ­ = $0.36

#### æ¹æ¡B: æ¬å°Whisperæ¨¡åï¼æ¨èï¼

```python
import whisper
import torch

class LocalWhisperTranscriber:
    """æ¬å°Whisperè½¬å½å?""
    
    def __init__(self, model_size: str = "medium", device: str = "cuda"):
        """
        åå§åæ¬å°Whisperæ¨¡å
        
        Args:
            model_size: æ¨¡åå¤§å° (tiny/base/small/medium/large-v3)
            device: è¿è¡è®¾å¤ (cuda/cpu)
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=self.device)
        
        print(f"â?Whisperæ¨¡åå·²å è½? {model_size} on {self.device}")
    
    def transcribe(self, audio_path: str, language: str = "zh") -> dict:
        """è½¬å½é³é¢"""
        result = self.model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            fp16=False  # CPUæ¨çæ¶ä½¿ç¨FP32
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result.get("language", language)
        }

# ä½¿ç¨ç¤ºä¾
transcriber = LocalWhisperTranscriber(model_size="medium")
result = transcriber.transcribe("recording.mp3")
```

**æ¨¡åéæ©å»ºè®®**:

| æ¨¡å | åæ°é?| åå­éæ±?| éåº¦ | åç¡®ç?| æ¨èåºæ¯ |
|------|--------|---------|------|--------|---------|
| tiny | 39M | ~1GB | æå¿?| 75% | å¿«éé¢è§?|
| base | 74M | ~1GB | å¾å¿« | 82% | æ¥å¸¸ä½¿ç¨ |
| small | 244M | ~2GB | å¿?| 87% | å¹³è¡¡éæ© |
| medium | 769M | ~5GB | ä¸­ç­ | 91% | â?**æ¨è** |
| large-v3 | 1550M | ~10GB | æ?| 94% | æé«ç²¾åº?|

**æ¨è**: â?**mediumæ¨¡å**ï¼åç¡®ç91%ï¼åå­éæ±éä¸­ï¼?

---

### 2. åå®¹åææ¨¡å (å¤§è¯­è¨æ¨¡å)

#### æ¹æ¡A: OpenAI GPT-4 APIï¼äºç«¯ï¼

```python
from openai import OpenAI

def analyze_with_gpt4(transcript: str):
    """ä½¿ç¨GPT-4åæ"""
    client = OpenAI(api_key="your-api-key")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æã?},
            {"role": "user", "content": f"åæä»¥ä¸ç´æ­åå®¹ï¼\n{transcript}"}
        ]
    )
    
    return response.choices[0].message.content
```

**ææ¬**: $0.03/1K tokensï¼?å°æ¶ç´æ­ â?$2-5

#### æ¹æ¡B: æ¬å°å¤§æ¨¡åï¼æ¨èï¼?

**éé¡¹1: DeepSeek-V3ï¼æ¨èï¼**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalDeepSeekAnalyzer:
    """æ¬å°DeepSeekåæå?""
    
    def __init__(self, model_path: str = "deepseek-ai/deepseek-llm-7b-chat"):
        """
        åå§åDeepSeekæ¨¡å
        
        Args:
            model_path: æ¨¡åè·¯å¾ï¼æ¯ææ¬å°è·¯å¾æHuggingFace IDï¼?
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print(f"â?DeepSeekæ¨¡åå·²å è½? {model_path}")
    
    def analyze(self, transcript: str) -> dict:
        """åæç´æ­åå®¹"""
        prompt = f"""ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æãè¯·åæä»¥ä¸ç´æ­åå®¹ï¼æåå³é®éèè§ç¹ã?

ç´æ­åå®¹ï¼?
{transcript}

è¯·æåä»¥ä¸ä¿¡æ¯ï¼ä»¥JSONæ ¼å¼è¿åï¼?
{{
    "market_view": "çå¤/çç©º/éè¡",
    "confidence": 0-10çä¿¡å¿åº¦,
    "sectors": ["æ¨èæ¿å1", "æ¨èæ¿å2"],
    "stocks": [
        {{
            "code": "è¡ç¥¨ä»£ç ",
            "name": "è¡ç¥¨åç§°",
            "action": "ä¹°å¥/ååº/è§æ",
            "reason": "æ¨èçç±"
        }}
    ],
    "risks": ["é£é©æç¤º1", "é£é©æç¤º2"],
    "key_points": ["å³é®è§ç¹1", "å³é®è§ç¹2"]
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
        
        # è§£æJSONååº
        import json
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        json_str = response[json_start:json_end]
        
        return json.loads(json_str)

# ä½¿ç¨ç¤ºä¾
analyzer = LocalDeepSeekAnalyzer()
result = analyzer.analyze(transcript_text)
```

**éé¡¹2: Qwen2.5ï¼é¿ééä¹åé®ï¼?*

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalQwenAnalyzer:
    """æ¬å°Qwenåæå?""
    
    def __init__(self, model_path: str = "Qwen/Qwen2.5-7B-Instruct"):
        """
        åå§åQwenæ¨¡å
        
        Args:
            model_path: æ¨¡åè·¯å¾
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print(f"â?Qwenæ¨¡åå·²å è½? {model_path}")
    
    def analyze(self, transcript: str) -> dict:
        """åæç´æ­åå®¹"""
        messages = [
            {
                "role": "system",
                "content": "ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æï¼æé¿ä»ç´æ­åå®¹ä¸­æåå³é®æèµè§ç¹ã?
            },
            {
                "role": "user",
                "content": f"è¯·åæä»¥ä¸ç´æ­åå®¹ï¼æåå³é®éèè§ç¹ï¼\n\n{transcript}"
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
        """è§£æååº"""
        import json
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except:
            return {
                "market_view": "éè¡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": []
            }

# ä½¿ç¨ç¤ºä¾
analyzer = LocalQwenAnalyzer()
result = analyzer.analyze(transcript_text)
```

**éé¡¹3: Ollamaæ¬å°é¨ç½²ï¼æç®åï¼**

```python
import requests
import json

class OllamaAnalyzer:
    """Ollamaæ¬å°åæå?""
    
    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        """
        åå§åOllamaåæå?
        
        Args:
            model_name: æ¨¡ååç§° (qwen2.5:7b, deepseek-v2:16b, llama3.1:8bç­?
            base_url: Ollamaæå¡å°å
        """
        self.model_name = model_name
        self.base_url = base_url
        
        print(f"â?Ollamaåæå¨å·²åå§å? {model_name}")
    
    def analyze(self, transcript: str) -> dict:
        """åæç´æ­åå®¹"""
        prompt = f"""ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æãè¯·åæä»¥ä¸ç´æ­åå®¹ï¼æåå³é®éèè§ç¹ã?

ç´æ­åå®¹ï¼?
{transcript}

è¯·æåä»¥ä¸ä¿¡æ¯ï¼ä»¥JSONæ ¼å¼è¿åï¼?
{{
    "market_view": "çå¤/çç©º/éè¡",
    "confidence": 0-10çä¿¡å¿åº¦,
    "sectors": ["æ¨èæ¿å1", "æ¨èæ¿å2"],
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
        
        # è§£æJSON
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except:
            return {
                "market_view": "éè¡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": []
            }

# ä½¿ç¨ç¤ºä¾
# é¦åå®è£Ollama: https://ollama.ai/
# ç¶åæåæ¨¡å: ollama pull qwen2.5:7b
# å¯å¨æå¡: ollama serve

analyzer = OllamaAnalyzer(model_name="qwen2.5:7b")
result = analyzer.analyze(transcript_text)
```

**æ¨¡åéæ©å»ºè®®**:

| æ¨¡å | åæ°é?| åå­éæ±?| ä¸­æè½å | éèçè§£ | æ¨èåº?|
|------|--------|---------|---------|---------|--------|
| Qwen2.5-7B | 7B | ~14GB | â­â­â­â­â­?| â­â­â­â­ | â?**å¼ºçæ¨è** |
| DeepSeek-7B | 7B | ~14GB | â­â­â­â­ | â­â­â­â­â­?| â?**å¼ºçæ¨è** |
| Qwen2.5-14B | 14B | ~28GB | â­â­â­â­â­?| â­â­â­â­â­?| â?æ¨èï¼é«éç½®ï¼?|
| Llama3.1-8B | 8B | ~16GB | â­â­â­?| â­â­â­?| â ï¸ ä¸è?|
| Qwen2.5-32B | 32B | ~64GB | â­â­â­â­â­?| â­â­â­â­â­?| â ï¸ éè¦é«ç«¯æ¾å?|

**æ¨è**: â?**Qwen2.5-7B** æ?**DeepSeek-7B**ï¼æ§ä»·æ¯æé«ï¼

---

### 3. ææåææ¨¡å (FinBERT)

#### æ¬å°é¨ç½²æ¹æ¡ï¼å·²æ¯æï¼?

```python
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

class LocalFinBERTAnalyzer:
    """æ¬å°FinBERTææåæå?""
    
    def __init__(self, model_path: str = "yiyanghkust/finbert-tone"):
        """
        åå§åFinBERTæ¨¡å
        
        Args:
            model_path: æ¨¡åè·¯å¾
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
        
        print(f"â?FinBERTæ¨¡åå·²å è½? {model_path}")
    
    def analyze_sentiment(self, text: str) -> dict:
        """ææåæ"""
        # åæ®µå¤çï¼é¿åææ¬è¿é¿ï¼
        max_length = 512
        segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        sentiments = []
        for segment in segments:
            result = self.sentiment_pipeline(segment)
            sentiments.append(result[0])
        
        # ç»è®¡ææåå¸
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

# ä½¿ç¨ç¤ºä¾
analyzer = LocalFinBERTAnalyzer()
result = analyzer.analyze_sentiment(transcript_text)
```

**æ¨è**: â?**yiyanghkust/finbert-tone**ï¼éèé¢åä¸ç¨ï¼

---

### 4. ç¡¬ä»¶éç½®å»ºè®®

#### æä½éç½®ï¼å¥é¨çº§ï¼

```
CPU: Intel i5-12400 / AMD Ryzen 5 5600
åå­: 16GB DDR4
æ¾å¡: NVIDIA RTX 3060 12GB
å­å¨: 500GB NVMe SSD
é¢ç®: çº?6000-8000å?

æ¯ææ¨¡å:
- Whisper: small/medium
- å¤§æ¨¡å? 7Båæ°æ¨¡åï¼éååï¼?
- FinBERT: å®å¨æ¯æ
```

#### æ¨èéç½®ï¼ä¸ä¸çº§ï¼?

```
CPU: Intel i7-13700K / AMD Ryzen 7 7800X3D
åå­: 32GB DDR5
æ¾å¡: NVIDIA RTX 4070 Ti Super 16GB
å­å¨: 1TB NVMe SSD
é¢ç®: çº?12000-15000å?

æ¯ææ¨¡å:
- Whisper: medium/large-v3
- å¤§æ¨¡å? 7B-14Båæ°æ¨¡å
- FinBERT: å®å¨æ¯æ
```

#### é«æ§è½éç½®ï¼æºæçº§ï¼?

```
CPU: Intel i9-14900K / AMD Ryzen 9 7950X
åå­: 64GB DDR5
æ¾å¡: NVIDIA RTX 4090 24GB
å­å¨: 2TB NVMe SSD
é¢ç®: çº?25000-30000å?

æ¯ææ¨¡å:
- Whisper: large-v3ï¼å®æ¶è½¬å½ï¼
- å¤§æ¨¡å? 14B-32Båæ°æ¨¡å
- FinBERT: å®å¨æ¯æ
```

---

### 5. ææ¬å¯¹æ¯åæ

#### äºç«¯APIæ¹æ¡ï¼?å¹´ææ¬ï¼

```
åè®¾ï¼æ¯å¤©å½å?0ä¸ªä¸»æ­ï¼æ¯ä¸ªä¸»æ­1å°æ¶

Whisper APIææ¬:
- 10å°æ¶/å¤?Ã $0.36/å°æ¶ = $3.6/å¤?
- 365å¤?Ã $3.6 = $1,314/å¹?

GPT-4 APIææ¬:
- 10æ¬¡åæ?å¤?Ã $3/æ¬?= $30/å¤?
- 365å¤?Ã $30 = $10,950/å¹?

æ»è®¡: $12,264/å¹?â?Â¥88,000/å¹?
```

#### æ¬å°æ¨¡åæ¹æ¡ï¼?å¹´ææ¬ï¼

```
ç¡¬ä»¶æå¥ï¼æ¨èéç½®ï¼:
- RTX 4070 Ti Super: Â¥8,000
- å¶ä»ç¡¬ä»¶: Â¥7,000
- æ»è®¡: Â¥15,000ï¼ä¸æ¬¡æ§æå¥ï¼

çµè´¹ææ¬:
- åè? 300W Ã 10å°æ¶/å¤?= 3åº¦çµ/å¤?
- çµè´¹: 3åº?Ã Â¥0.6 Ã 365å¤?= Â¥657/å¹?

æ»è®¡: Â¥15,657ï¼ç¬¬ä¸å¹´ï¼ + Â¥657/å¹´ï¼åç»­æ¯å¹´ï¼?

1å¹´æ»ææ? Â¥15,657
2å¹´æ»ææ? Â¥16,314
3å¹´æ»ææ? Â¥16,971

ç¸æ¯äºç«¯APIèç: Â¥88,000 - Â¥15,657 = Â¥72,343ï¼ç¬¬ä¸å¹´ï¼
```

**ç»è®º**: â?**æ¬å°æ¨¡åæ¹æ¡é¿æææ¬æ´ä½ï¼?å¹´å³å¯åæ?*

---

### 6. é¨ç½²æµç¨

#### æ­¥éª¤1: ç¯å¢åå¤

```bash
# å®è£Python 3.10+
conda create -n live-analysis python=3.10
conda activate live-analysis

# å®è£PyTorchï¼GPUçæ¬ï¼?
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# å®è£Transformers
pip install transformers accelerate

# å®è£Whisper
pip install openai-whisper

# å®è£å¶ä»ä¾èµ
pip install ffmpeg-python DrissionPage
```

#### æ­¥éª¤2: ä¸è½½æ¨¡å

```bash
# ä¸è½½Whisperæ¨¡å
python -c "import whisper; whisper.load_model('medium')"

# ä¸è½½Qwenæ¨¡å
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-7B-Instruct')"

# ä¸è½½FinBERTæ¨¡å
python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```

#### æ­¥éª¤3: éç½®ç³»ç»

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

#### æ­¥éª¤4: è¿è¡ç³»ç»

```bash
python main.py
```

---

### 7. æ¨¡åä¼åå»ºè®®

#### éåå é?

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 4-bitéåéç½®
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# å è½½éåæ¨¡å
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
```

**ææ**: åå­å ç¨åå°75%ï¼éåº¦æå2-3å?

#### æ¨¡åå¾®è°

```python
# ä½¿ç¨èªå·±çéèæ°æ®å¾®è°æ¨¡å?
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

## ð¯ RTX 3090 24GB æä½³éç½®æ¹æ¡?

> **ç¡¬ä»¶éç½®**: RTX 3090 24GB + 64GB RAM + i7-12700KF
> **éç½®è¯çº§**: â­â­â­â­â­?æºæçº§éç½?
> **åå»ºæ¥æ**: 2026-04-02

### ç¡¬ä»¶éç½®åæ

```
â?æ¾å¡: NVIDIA RTX 3090 24GB - é«ç«¯æ¾å¡ï¼å¯è¿è¡å¤§åæ¨¡å
â?åå­: 64GB - éå¸¸åè¶³
â?å¤çå? i7-12700KF - å¼ºåCPU
â?å­å¨: 1.82TB - ç©ºé´åè¶³

éç½®è¯çº§: â­â­â­â­â­?æºæçº§éç½?
```

### å·²æOllamaæ¨¡ååæ

| æ¨¡å | å¤§å° | éç¨æ?| æ¨èåº?|
|------|------|--------|--------|
| qwen3:8b | 5.2GB | â?éååå®¹åæ | â­â­â­â­ |
| deepseek-r1:8b | 5.2GB | â?éååå®¹åæ | â­â­â­â­ |
| **deepseek-r1:14b** | 9.0GB | ââ **éå¸¸éå** | â­â­â­â­â­?|
| qwen2.5-coder:14b | 9.0GB | â ï¸ ä¸æ³¨ä»£ç  | â­â­â­?|
| qwen3-coder:30b | 18GB | â ï¸ ä¸æ³¨ä»£ç  | â­â­â­?|

### ð æ¨èæ¹æ¡ä¸ï¼ä½¿ç¨ç°ææ¨¡åï¼ç«å³å¯ç¨ï¼?

```
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? è¯­é³è¯å«: Whisper large-v3 (æ¬å°)           â?
â? - åæ°é? 1.55B                             â?
â? - æ¾å­å ç¨: ~10GB                           â?
â? - åç¡®ç? 94%                               â?
â? - éåº¦: ~150-200å­ç¬¦/ç§?                    â?
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? åå®¹åæ: deepseek-r1:14b (å·²æ)            â?
â? - åæ°é? 14B                               â?
â? - æ¾å­å ç¨: ~9GB                            â?
â? - éèçè§£: â­â­â­â­â­?                       â?
â? - æ¨çéåº¦: ~30-50 tokens/ç§?               â?
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? ææåæ: FinBERT (æ¬å°)                    â?
â? - åæ°é? 110M                              â?
â? - æ¾å­å ç¨: ~1GB                            â?
â? - éèä¸ç¨: â?                             â?
â? - éåº¦: ~1000+ ææ¬/ç§?                     â?
âââââââââââââââââââââââââââââââââââââââââââââââ?

æ»æ¾å­å ç? ~20GB / 24GB (å¯ç¨)
æ§è½è¯çº§: â­â­â­â­â­?
```

### ð¥ æ¨èæ¹æ¡äºï¼æåæ´å¤§æ¨¡åï¼æä½³æ§è½ï¼?

```bash
# æåå½ä»¤
ollama pull qwen2.5:32b
```

```
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? è¯­é³è¯å«: Whisper large-v3 (æ¬å°)           â?
â? - åæ°é? 1.55B                             â?
â? - æ¾å­å ç¨: ~10GB                           â?
â? - åç¡®ç? 94%                               â?
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? åå®¹åæ: qwen2.5:32b (æ¨èæå)            â?
â? - åæ°é? 32B                               â?
â? - æ¾å­å ç¨: ~11GB                           â?
â? - éèçè§£: â­â­â­â­â­?(æå¼?                 â?
â? - ä¸­æè½å: â­â­â­â­â­?                        â?
âââââââââââââââââââââââââââââââââââââââââââââââ?
â? ææåæ: FinBERT (æ¬å°)                    â?
â? - åæ°é? 110M                              â?
â? - æ¾å­å ç¨: ~1GB                            â?
âââââââââââââââââââââââââââââââââââââââââââââââ?

æ»æ¾å­å ç? ~22GB / 24GB (å¯ç¨)
æ§è½è¯çº§: â­â­â­â­â­?(æé«?
```

### æ§è½å¯¹æ¯

| æ¨¡åç»å | åç¡®ç?| éåº¦ | æ¾å­ | æ¨èåº?|
|---------|--------|------|------|--------|
| Whisper medium + Qwen7B | 87% / 85% | å¿?| 12GB | â­â­â­?|
| Whisper large-v3 + DeepSeek14B | 94% / 90% | ä¸?| 20GB | â­â­â­â­â­?|
| Whisper large-v3 + Qwen32B | 94% / 95% | ä¸?| 22GB | â­â­â­â­â­?|

### ææ¬å¯¹æ¯

| æ¹æ¡ | åå§æå¥ | å¹´è¿è¥ææ?| 1å¹´æ»ææ?|
|------|---------|-----------|----------|
| äºç«¯API | Â¥0 | Â¥88,000 | Â¥88,000 |
| æ¬å°æ¨¡åï¼ç°æï¼ | Â¥0 | Â¥657 | Â¥657 |
| æ¬å°æ¨¡åï¼åçº§ï¼ | Â¥0 | Â¥1,000 | Â¥1,000 |

**èç**: Â¥87,000 - Â¥87,686 / å¹?

### éç½®æä»¶

```yaml
# config_local_rtx3090.yaml
models:
  whisper:
    type: "local"
    model_size: "large-v3"
    device: "cuda"
  
  llm:
    type: "ollama"
    model_name: "deepseek-r1:14b"  # æ?"qwen2.5:32b"
    base_url: "http://localhost:11434"
  
  sentiment:
    type: "local"
    model_name: "yiyanghkust/finbert-tone"
    device: "cuda"
```

### é¨ç½²æ­¥éª¤

```bash
# 1. æåWhisper large-v3
python -c "import whisper; whisper.load_model('large-v3', device='cuda')"

# 2. æåFinBERT
python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"

# 3. ï¼å¯éï¼æåæ´å¤§æ¨¡å
ollama pull qwen2.5:32b

# 4. è¿è¡é¨ç½²èæ¬
.\deploy_rtx3090.ps1

# 5. å¯å¨ç³»ç»
python main.py
```

### ç¸å³ææ¡£

- [RTX 3090æä½³æ¨¡åéç½®è¯¦ç»è¯´æ](./RTX3090_BEST_MODELS.md)
- [éç½®æä»¶](./config_local_rtx3090.yaml)
- [é¨ç½²èæ¬ï¼PowerShellï¼](./deploy_rtx3090.ps1)
- [é¨ç½²èæ¬ï¼Bashï¼](./deploy_rtx3090.sh)

---

## ðï¸?ç³»ç»æ¶æ

### æ´ä½æ¶æå?

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   åºç¨å±?(Application Layer)                â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?       LiveStreamFinancialApplication                 â? â?
â? â? - ä»»å¡è°åº¦ç®¡ç                                        â? â?
â? â? - ç»æå¯è§åå±ç¤?                                     â? â?
â? â? - å å­è¾åºæ¥å£                                        â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                            â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   ä¸å¡å±?(Business Layer)                   â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? â?ç´æ­çæ§æå¡  â? â?åå®¹åææå¡  â? â?å å­çææå¡  â?     â?
â? âMonitorServiceâ? âAnalyzerServiceâ? âFactorService â?     â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                            â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   æ ¸å¿å±?(Core Layer)                       â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? â?é³é¢å½å¶å?   â? â?è¯­é³è½¬å½å?   â? â?è§ç¹èåå?   â?     â?
â? âAudioRecorder â? âTranscriber   â? âOpinionAggregatorâ?   â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? â?ç´æ­çæ§å?   â? â?ææåæå?   â? â?å å­è®¡ç®å?   â?     â?
â? âLiveMonitor   â? âSentimentAnalyzerâ?âFactorCalculatorâ?  â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
                            â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   åºç¡è®¾æ½å±?(Infrastructure Layer)          â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? â?FFmpeg       â? â?Whisper      â? â?OpenAI API   â?     â?
â? â?(é³é¢å½å¶)   â? â?(è¯­é³è¯å«)   â? â?(åå®¹åæ)   â?     â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
â? â?PostgreSQL   â? â?Redis        â? â?ClickHouse   â?     â?
â? â?(åæ°æ®å­å? â? â?(å®æ¶ç¼å­)   â? â?(æ¶åºæ°æ®)   â?     â?
â? ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?     â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### æ°æ®æµç¨å?

```
âââââââââââââââ?
â?æé³ç´æ­é?  â?
â?(å¤ä¸ªä¸»æ­)   â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?å®æ¶çæ§     â?â?æ£æµå¼æ­ç¶æ?
â?(DrissionPage)â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?é³é¢å½å¶     â?â?åªå½å¶MP3
â?(FFmpeg)     â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?è¯­é³è½¬å½     â?â?Whisper API
â?(Whisper)    â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?åå®¹åæ     â?â?GPT-4æåè§ç¹
â?(GPT-4)      â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?ææåæ     â?â?FinBERT
â?(FinBERT)    â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?è§ç¹èå     â?â?å¤ä¸»æ­æç¥?
â?(Aggregator) â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?å å­çæ     â?â?çæé¢æµå å­
â?(Factor Gen) â?
âââââââââââââââ?
       â?
âââââââââââââââ?
â?å å­è¾åº     â?â?éåäº¤æç³»ç»
â?(Output)     â?
âââââââââââââââ?
```

---

## ð¦ æ¨¡åè¯¦ç»è®¾è®¡

### æ¨¡å1: ç´æ­çæ§ä¸å½å?(LiveMonitor & AudioRecorder)

#### 1.1 åè½èè´£

- çæ§å¤ä¸ªæé³ä¸»æ­çç´æ­ç¶æ?
- ä¸»æ­å¼æ­æ¶èªå¨å¼å§å½å?
- åªå½å¶MP3é³é¢æ ¼å¼
- è·åç´æ­é´å®æ¶æ°æ®ï¼å¨çº¿äººæ°ãç´æ­é´æ é¢ç­ï¼

#### 1.2 ææ¯å®ç?

**ç´æ­çæ§å?(LiveMonitor)**

ä½¿ç¨DrissionPageçå¬ç´æ­é´ç¶æï¼

```python
from DrissionPage import ChromiumPage
import time
import asyncio
from typing import Dict, List
import logging

class DouyinLiveMonitor:
    """æé³ç´æ­é´çæ§å¨"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.page = ChromiumPage()
        self.logger = logging.getLogger(__name__)
        self.monitored_rooms = {}
    
    async def start_monitoring(self, streamer_list: List[Dict]):
        """å¼å§çæ§å¤ä¸ªä¸»æ?""
        for streamer in streamer_list:
            asyncio.create_task(
                self._monitor_single_streamer(streamer)
            )
    
    async def _monitor_single_streamer(self, streamer: Dict):
        """çæ§åä¸ªä¸»æ­"""
        while True:
            try:
                # æ£æ¥ç´æ­ç¶æ?
                is_live = await self._check_live_status(streamer["url"])
                
                if is_live:
                    # è·åç´æ­é´æ°æ?
                    live_data = await self._get_live_room_data(streamer["url"])
                    
                    # è§¦åå½å¶äºä»¶
                    await self._on_streamer_live(streamer, live_data)
                
                # ç­å¾ä¸æ¬¡æ£æ?
                await asyncio.sleep(self.config["check_interval"])
                
            except Exception as e:
                self.logger.error(f"çæ§ä¸»æ­ {streamer['name']} å¤±è´¥: {e}")
                await asyncio.sleep(60)
    
    async def _check_live_status(self, live_url: str) -> bool:
        """æ£æ¥ç´æ­ç¶æ?""
        try:
            self.page.get(live_url)
            time.sleep(2)
            
            # æ£æ¥æ¯å¦æç´æ­æ è¯
            live_indicator = self.page.ele('css:.live-badge', timeout=3)
            return live_indicator is not None
            
        except Exception as e:
            self.logger.error(f"æ£æ¥ç´æ­ç¶æå¤±è´? {e}")
            return False
    
    async def _get_live_room_data(self, live_url: str) -> Dict:
        """è·åç´æ­é´æ°æ?""
        try:
            self.page.get(live_url)
            time.sleep(3)
            
            # æåå¨çº¿äººæ°
            online_element = self.page.ele('css:.live-room-online-count', timeout=5)
            online_count = self._parse_count(online_element.text) if online_element else 0
            
            # æåç´æ­é´æ é¢?
            title_element = self.page.ele('css:.room-title', timeout=5)
            title = title_element.text if title_element else ""
            
            # æåä¸»æ­åç§°
            streamer_element = self.page.ele('css:.streamer-name', timeout=5)
            streamer_name = streamer_element.text if streamer_element else ""
            
            return {
                "online_count": online_count,
                "title": title,
                "streamer_name": streamer_name,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"è·åç´æ­é´æ°æ®å¤±è´? {e}")
            return {}
    
    def _parse_count(self, count_text: str) -> int:
        """è§£æäººæ°ï¼å¦ '23.5ä¸? -> 235000ï¼?""
        try:
            count_text = count_text.strip()
            
            if 'ä¸? in count_text:
                return int(float(count_text.replace('ä¸?, '')) * 10000)
            elif 'äº? in count_text:
                return int(float(count_text.replace('äº?, '')) * 100000000)
            else:
                return int(count_text)
        except:
            return 0
    
    async def _on_streamer_live(self, streamer: Dict, live_data: Dict):
        """ä¸»æ­å¼æ­äºä»¶å¤ç?""
        self.logger.info(f"ä¸»æ­ {streamer['name']} å·²å¼æ­ï¼å¨çº¿äººæ°: {live_data['online_count']}")
        
        # è§¦åå½å¶ä»»å¡
        # è¿éä¼è°ç¨AudioRecorderå¼å§å½å?
        pass
```

**é³é¢å½å¶å?(AudioRecorder)**

ä½¿ç¨FFmpegå½å¶MP3é³é¢ï¼?

```python
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Optional
import logging

class AudioRecorder:
    """é³é¢å½å¶å?""
    
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
        å½å¶é³é¢
        
        Args:
            stream_url: ç´æ­æµå°å
            streamer_name: ä¸»æ­åç§°
            duration: å½å¶æ¶é¿ï¼ç§ï¼?
            output_format: è¾åºæ ¼å¼ï¼mp3/m4aï¼?
            bitrate: é³é¢æ¯ç¹ç?
        
        Returns:
            å½å¶æä»¶è·¯å¾
        """
        try:
            # çæè¾åºæä»¶å?
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{streamer_name}_{timestamp}.{output_format}"
            
            # æå»ºFFmpegå½ä»¤
            cmd = [
                self.ffmpeg_path,
                "-i", stream_url,              # è¾å¥æµ?
                "-vn",                          # å¿½ç¥è§é¢
                "-c:a", "libmp3lame",          # MP3ç¼ç å?
                "-b:a", bitrate,               # æ¯ç¹ç?
                "-t", str(duration),           # å½å¶æ¶é¿
                "-y",                           # è¦çå·²å­å¨æä»?
                str(output_file)
            ]
            
            self.logger.info(f"å¼å§å½å? {streamer_name}, æ¶é¿: {duration}ç§?)
            
            # å¼æ­¥æ§è¡å½å¶
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # ç­å¾å½å¶å®æ
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"å½å¶å®æ: {output_file}")
                return str(output_file)
            else:
                self.logger.error(f"å½å¶å¤±è´¥: {stderr.decode()}")
                return None
                
        except Exception as e:
            self.logger.error(f"å½å¶å¼å¸¸: {e}")
            return None
    
    async def record_segmented(
        self,
        stream_url: str,
        streamer_name: str,
        segment_duration: int = 1800,
        total_duration: int = 7200
    ) -> list:
        """
        åæ®µå½å¶é³é¢
        
        Args:
            stream_url: ç´æ­æµå°å
            streamer_name: ä¸»æ­åç§°
            segment_duration: æ¯æ®µæ¶é¿ï¼ç§ï¼?
            total_duration: æ»æ¶é¿ï¼ç§ï¼
        
        Returns:
            å½å¶æä»¶åè¡¨
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

### æ¨¡å2: åå®¹è½¬å½ä¸åæ?(Transcriber & Analyzer)

#### 2.1 åè½èè´£

- å°MP3é³é¢è½¬å½ä¸ºæå­?
- æåå³é®éèè§ç¹
- è¿è¡ææåæ
- è¯å«æ¨èæ¿ååä¸ªè?

#### 2.2 ææ¯å®ç?

**è¯­é³è½¬å½å?(Transcriber)**

```python
import whisper
from typing import Dict, List
import logging
import time

class AudioTranscriber:
    """é³é¢è½¬å½å?""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # å è½½Whisperæ¨¡å
        model_size = config.get("whisper_model", "base")
        self.logger.info(f"å è½½Whisperæ¨¡å: {model_size}")
        self.model = whisper.load_model(model_size)
    
    async def transcribe(
        self,
        audio_path: str,
        language: str = "zh"
    ) -> Dict:
        """
        è½¬å½é³é¢
        
        Args:
            audio_path: é³é¢æä»¶è·¯å¾
            language: è¯­è¨ï¼zh/enï¼?
        
        Returns:
            è½¬å½ç»æ
        """
        try:
            start_time = time.time()
            
            self.logger.info(f"å¼å§è½¬å½? {audio_path}")
            
            # ä½¿ç¨Whisperè½¬å½
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe"
            )
            
            # æåææ¬ååæ®?
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
            
            self.logger.info(f"è½¬å½å®æï¼èæ¶: {elapsed_time:.2f}ç§?)
            
            return {
                "text": transcript,
                "segments": segments,
                "language": result.get("language", language),
                "duration": elapsed_time
            }
            
        except Exception as e:
            self.logger.error(f"è½¬å½å¤±è´¥: {e}")
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
        """æ¹éè½¬å½é³é¢"""
        results = []
        
        for audio_file in audio_files:
            result = await self.transcribe(audio_file, language)
            results.append(result)
        
        return results
```

**åå®¹åæå?(ContentAnalyzer)**

```python
from openai import OpenAI
from typing import Dict, List
import json
import logging

class FinancialContentAnalyzer:
    """éèåå®¹åæå?""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # åå§åOpenAIå®¢æ·ç«?
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
        æåå³é®éèè§ç¹
        
        Args:
            transcript: è½¬å½ææ¬
            streamer_name: ä¸»æ­åç§°
        
        Returns:
            å³é®è§ç¹
        """
        try:
            prompt = f"""
ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æãè¯·åæä»¥ä¸ç´æ­åå®¹ï¼æåå³é®éèè§ç¹ã?

ä¸»æ­åç§°: {streamer_name}
ç´æ­åå®¹:
{transcript}

è¯·æåä»¥ä¸ä¿¡æ¯ï¼ä»¥JSONæ ¼å¼è¿åï¼?

{{
    "market_view": "çå¤/çç©º/éè¡",
    "confidence": 0-10çä¿¡å¿åº¦,
    "sectors": ["æ¨èæ¿å1", "æ¨èæ¿å2"],
    "stocks": [
        {{
            "code": "è¡ç¥¨ä»£ç ",
            "name": "è¡ç¥¨åç§°",
            "action": "ä¹°å¥/ååº/è§æ",
            "price": "å»ºè®®ä»·æ ¼",
            "reason": "æ¨èçç±"
        }}
    ],
    "risks": ["é£é©æç¤º1", "é£é©æç¤º2"],
    "key_points": ["å³é®è§ç¹1", "å³é®è§ç¹2"],
    "timeframe": "ç­æ/ä¸­æ/é¿æ"
}}

æ³¨æï¼?
1. market_viewå¿é¡»æ?çå¤"ã?çç©º"æ?éè¡"ä¹ä¸
2. confidenceæ?-10çæ°å­ï¼è¡¨ç¤ºä¸»æ­å¯¹è§ç¹çä¿¡å¿åº?
3. å¦ææ²¡ææç¡®æå°æä¸ªå­æ®µï¼å¯ä»¥çç©?
4. ä¿æå®¢è§ï¼ä¸è¦æ·»å ä¸ªäººè§ç?
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "ä½ æ¯ä¸ä½ä¸ä¸çéèåæå¸å©æï¼æé¿ä»ç´æ­åå®¹ä¸­æåå³é®æèµè§ç¹ã?
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # è§£æJSONååº
            content = response.choices[0].message.content
            
            # æåJSONé¨å
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content
            
            result = json.loads(json_str)
            
            self.logger.info(f"è§ç¹æåå®æ: {result['market_view']}, ä¿¡å¿åº? {result['confidence']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"è§ç¹æåå¤±è´¥: {e}")
            return {
                "market_view": "éè¡",
                "confidence": 5,
                "sectors": [],
                "stocks": [],
                "risks": [],
                "key_points": [],
                "timeframe": "ç­æ",
                "error": str(e)
            }
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
        ææåæ
        
        Args:
            text: å¾åæææ?
        
        Returns:
            ææåæç»æ
        """
        try:
            from transformers import pipeline
            
            # ä½¿ç¨éèææåææ¨¡å
            sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="yiyanghkust/finbert-tone",
                device=-1  # CPU
            )
            
            # åæ®µåæï¼é¿åææ¬è¿é¿ï¼
            max_length = 512
            segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            sentiments = []
            for segment in segments:
                result = sentiment_analyzer(segment)
                sentiments.append(result[0])
            
            # ç»¼åææ
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
            self.logger.error(f"ææåæå¤±è´¥: {e}")
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "error": str(e)
            }
```

---

### æ¨¡å3: è§ç¹èåä¸å å­çæ?(Aggregator & FactorGenerator)

#### 3.1 åè½èè´£

- èåå¤ä¸ªä¸»æ­çè§ç?
- ç»è®¡è§ç¹ä¸è´æ?
- çæé¢æµå å­
- è¾åºå°éåäº¤æç³»ç»?

#### 3.2 ææ¯å®ç?

**è§ç¹èåå?(OpinionAggregator)**

```python
from typing import List, Dict
from collections import Counter
import numpy as np
import logging

class OpinionAggregator:
    """è§ç¹èåå?""
    
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
        æ·»å ä¸»æ­è§ç¹
        
        Args:
            streamer_name: ä¸»æ­åç§°
            opinion: è§ç¹æ°æ®
            weight: æé
            online_count: å¨çº¿äººæ°
        """
        self.opinions.append({
            "streamer": streamer_name,
            "opinion": opinion,
            "weight": weight,
            "online_count": online_count,
            "timestamp": time.time()
        })
        
        self.logger.info(f"æ·»å è§ç¹: {streamer_name}, è§ç¹: {opinion['market_view']}, ä¿¡å¿åº? {opinion['confidence']}")
    
    def aggregate(self) -> Dict:
        """
        èåææè§ç?
        
        Returns:
            èåç»æ
        """
        if not self.opinions:
            return {
                "dominant_view": "éè¡",
                "consensus_ratio": 0,
                "total_streamers": 0
            }
        
        # ç»è®¡å¤§ççæ³
        view_scores = {"çå¤": 0.0, "çç©º": 0.0, "éè¡": 0.0}
        
        for item in self.opinions:
            view = item["opinion"]["market_view"]
            confidence = item["opinion"]["confidence"]
            weight = item["weight"]
            
            # å ææç¥¨
            score = weight * confidence / 10.0
            view_scores[view] += score
        
        # ç¡®å®ä¸»æµè§ç¹
        dominant_view = max(view_scores, key=view_scores.get)
        total_score = sum(view_scores.values())
        consensus_ratio = view_scores[dominant_view] / total_score if total_score > 0 else 0
        
        # ç»è®¡æ¨èæ¿å
        all_sectors = []
        for item in self.opinions:
            all_sectors.extend(item["opinion"].get("sectors", []))
        
        sector_counts = Counter(all_sectors)
        top_sectors = sector_counts.most_common(10)
        
        # ç»è®¡æ¨èä¸ªè¡
        all_stocks = []
        for item in self.opinions:
            all_stocks.extend(item["opinion"].get("stocks", []))
        
        stock_counts = Counter([s["code"] for s in all_stocks if "code" in s])
        top_stocks = stock_counts.most_common(10)
        
        # è®¡ç®å¹³åä¿¡å¿åº?
        avg_confidence = np.mean([item["opinion"]["confidence"] for item in self.opinions])
        
        # è®¡ç®å¹³åå¨çº¿äººæ°
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
        """æ¸ç©ºè§ç¹"""
        self.opinions = []
        self.logger.info("è§ç¹å·²æ¸ç©?)
```

**å å­çæå?(FactorGenerator)**

```python
from typing import Dict
import numpy as np
import logging

class FactorGenerator:
    """å å­çæå?""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_factors(
        self,
        aggregated_opinion: Dict,
        market_data: Dict = None
    ) -> Dict:
        """
        çæé¢æµå å­
        
        Args:
            aggregated_opinion: èåè§ç¹
            market_data: å¸åºæ°æ®ï¼å¯éï¼
        
        Returns:
            é¢æµå å­
        """
        try:
            # 1. æç»ªå å­ï¼?1å?ï¼?
            sentiment_factor = self._calculate_sentiment_factor(
                aggregated_opinion["dominant_view"],
                aggregated_opinion["consensus_ratio"]
            )
            
            # 2. ä¸è´æ§å å­ï¼0å?ï¼?
            consensus_factor = aggregated_opinion["consensus_ratio"]
            
            # 3. å½±ååå å­ï¼åºäºä¸»æ­æ°éåå¨çº¿äººæ°ï¼
            influence_factor = self._calculate_influence_factor(
                aggregated_opinion["total_streamers"],
                aggregated_opinion["avg_online_count"]
            )
            
            # 4. ä¿¡å¿åº¦å å­ï¼0å?ï¼?
            confidence_factor = aggregated_opinion["avg_confidence"] / 10.0
            
            # 5. æ¿åç­åº¦å å­
            sector_factors = self._calculate_sector_factors(
                aggregated_opinion["top_sectors"],
                aggregated_opinion["total_streamers"]
            )
            
            # 6. ç»¼åå å­ï¼å æå¹³åï¼
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
            self.logger.error(f"å å­çæå¤±è´¥: {e}")
            return {}
    
    def _calculate_sentiment_factor(
        self,
        dominant_view: str,
        consensus_ratio: float
    ) -> float:
        """è®¡ç®æç»ªå å­"""
        if dominant_view == "çå¤":
            return consensus_ratio
        elif dominant_view == "çç©º":
            return -consensus_ratio
        else:
            return 0.0
    
    def _calculate_influence_factor(
        self,
        total_streamers: int,
        avg_online_count: float
    ) -> float:
        """è®¡ç®å½±ååå å­?""
        # ä¸»æ­æ°éå å­ï¼åè®?0ä¸ªä¸»æ­ä¸ºæ åï¼?
        streamer_factor = min(total_streamers / 10.0, 1.0)
        
        # å¨çº¿äººæ°å å­ï¼åè®?0ä¸å¨çº¿ä¸ºæ åï¼?
        online_factor = min(avg_online_count / 100000.0, 1.0)
        
        # ç»¼åå½±åå?
        influence_factor = (streamer_factor * 0.6 + online_factor * 0.4)
        
        return influence_factor
    
    def _calculate_sector_factors(
        self,
        top_sectors: list,
        total_streamers: int
    ) -> Dict[str, float]:
        """è®¡ç®æ¿åç­åº¦å å­"""
        sector_factors = {}
        
        for sector, count in top_sectors:
            # ç­åº¦ = æåæ¬¡æ° / ä¸»æ­æ°é
            sector_factors[sector] = count / total_streamers
        
        return sector_factors
    
    def _calculate_composite_factor(
        self,
        sentiment_factor: float,
        consensus_factor: float,
        influence_factor: float,
        confidence_factor: float
    ) -> float:
        """è®¡ç®ç»¼åå å­"""
        # æééç½®
        weights = self.config.get("factor_weights", {
            "sentiment": 0.4,
            "consensus": 0.3,
            "influence": 0.2,
            "confidence": 0.1
        })
        
        # å æå¹³å
        composite = (
            sentiment_factor * weights["sentiment"] +
            consensus_factor * weights["consensus"] +
            influence_factor * weights["influence"] +
            confidence_factor * weights["confidence"]
        )
        
        return composite
```

---

## ð å®æ´ç³»ç»éæ

### ä¸»ç³»ç»ç±»

```python
import asyncio
import logging
from typing import List, Dict
from datetime import datetime
import json

class LiveStreamFinancialSystem:
    """å¤ä¸»æ­ç´æ­éèåæç³»ç»?""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # åå§ååæ¨¡å
        self.monitor = DouyinLiveMonitor(config["monitor"])
        self.recorder = AudioRecorder(config["recorder"])
        self.transcriber = AudioTranscriber(config["transcriber"])
        self.analyzer = FinancialContentAnalyzer(config["analyzer"])
        self.aggregator = OpinionAggregator(config["aggregator"])
        self.factor_generator = FactorGenerator(config["factor_generator"])
        
        # ç»æå­å¨
        self.results = []
    
    async def run(self, streamer_list: List[Dict]):
        """
        è¿è¡ç³»ç»
        
        Args:
            streamer_list: ä¸»æ­åè¡¨
        """
        self.logger.info(f"ç³»ç»å¯å¨ï¼çæ?{len(streamer_list)} ä¸ªä¸»æ?)
        
        # å¯å¨çæ§ä»»å¡
        tasks = []
        for streamer in streamer_list:
            task = asyncio.create_task(
                self._process_streamer(streamer)
            )
            tasks.append(task)
        
        # ç­å¾ææä»»å¡å®æ?
        await asyncio.gather(*tasks)
        
        # çææç»å å­?
        final_factors = await self._generate_final_factors()
        
        return final_factors
    
    async def _process_streamer(self, streamer: Dict):
        """å¤çåä¸ªä¸»æ­"""
        try:
            self.logger.info(f"å¼å§å¤çä¸»æ? {streamer['name']}")
            
            # 1. æ£æ¥ç´æ­ç¶æ?
            is_live = await self.monitor._check_live_status(streamer["url"])
            
            if not is_live:
                self.logger.info(f"ä¸»æ­ {streamer['name']} æªå¼æ?)
                return
            
            # 2. è·åç´æ­é´æ°æ?
            live_data = await self.monitor._get_live_room_data(streamer["url"])
            
            # 3. è·åç´æ­æµå°å
            stream_url = await self._get_stream_url(streamer["url"])
            
            if not stream_url:
                self.logger.error(f"æ æ³è·åç´æ­æµå°å: {streamer['name']}")
                return
            
            # 4. å½å¶é³é¢
            audio_path = await self.recorder.record_audio(
                stream_url=stream_url,
                streamer_name=streamer["name"],
                duration=streamer.get("duration", 3600)
            )
            
            if not audio_path:
                self.logger.error(f"å½å¶å¤±è´¥: {streamer['name']}")
                return
            
            # 5. è½¬å½é³é¢
            transcript = await self.transcriber.transcribe(audio_path)
            
            if not transcript["text"]:
                self.logger.error(f"è½¬å½å¤±è´¥: {streamer['name']}")
                return
            
            # 6. æåå³é®è§ç¹
            key_points = await self.analyzer.extract_key_points(
                transcript["text"],
                streamer["name"]
            )
            
            # 7. ææåæ
            sentiment = await self.analyzer.analyze_sentiment(transcript["text"])
            
            # 8. æ·»å å°èåå¨
            self.aggregator.add_opinion(
                streamer_name=streamer["name"],
                opinion={
                    **key_points,
                    "sentiment": sentiment
                },
                weight=streamer.get("weight", 1.0),
                online_count=live_data.get("online_count", 0)
            )
            
            # 9. ä¿å­ç»æ
            result = {
                "streamer": streamer["name"],
                "live_data": live_data,
                "transcript": transcript,
                "key_points": key_points,
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            self.logger.info(f"ä¸»æ­ {streamer['name']} å¤çå®æ")
            
        except Exception as e:
            self.logger.error(f"å¤çä¸»æ­ {streamer['name']} å¤±è´¥: {e}")
    
    async def _get_stream_url(self, live_url: str) -> str:
        """è·åç´æ­æµå°å"""
        # è¿ééè¦å®ç°è·åç´æ­æµå°åçé»è¾
        # å¯ä»¥ä½¿ç¨DouyinLiveRecorderä¸­çstream.pyæ¨¡å
        pass
    
    async def _generate_final_factors(self) -> Dict:
        """çææç»å å­?""
        # èåè§ç¹
        aggregated = self.aggregator.aggregate()
        
        # çæå å­
        factors = self.factor_generator.generate_factors(aggregated)
        
        # æ·»å åæ°æ?
        factors["timestamp"] = datetime.now().isoformat()
        factors["streamer_count"] = len(self.results)
        
        return factors
    
    def save_results(self, output_path: str):
        """ä¿å­ç»æ"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"ç»æå·²ä¿å­? {output_path}")
```

---

## ð éç½®æä»¶

### config.yaml

```yaml
# ç³»ç»éç½®
system:
  name: "å¤ä¸»æ­ç´æ­éèåæç³»ç»?
  version: "1.0.0"
  log_level: "INFO"

# çæ§éç½®
monitor:
  check_interval: 60  # æ£æ¥é´éï¼ç§ï¼
  browser_type: "chrome"  # æµè§å¨ç±»å?
  headless: true  # æ å¤´æ¨¡å¼

# å½å¶éç½®
recorder:
  output_dir: "./recordings"
  audio_format: "mp3"
  bitrate: "128k"
  sample_rate: 44100
  segment_duration: 1800  # åæ®µæ¶é¿ï¼ç§ï¼?

# è½¬å½éç½®
transcriber:
  whisper_model: "base"  # tiny/base/small/medium/large
  language: "zh"

# åæéç½®
analyzer:
  openai_api_key: "${OPENAI_API_KEY}"
  openai_base_url: "https://api.openai.com/v1"
  openai_model: "gpt-4"
  sentiment_model: "yiyanghkust/finbert-tone"

# èåéç½®
aggregator:
  min_streamers: 3  # æå°ä¸»æ­æ°é?
  weight_by_online_count: true  # æå¨çº¿äººæ°å æ?

# å å­éç½®
factor_generator:
  factor_weights:
    sentiment: 0.4
    consensus: 0.3
    influence: 0.2
    confidence: 0.1

# è¾åºéç½®
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
      "name": "è¡ç¥èç",
      "url": "https://live.douyin.com/745964462470",
      "schedule": {
        "start_time": "19:00",
        "end_time": "21:00"
      },
      "weight": 1.5,
      "tags": ["ææ¯åæ?, "ç­çº¿æä½"],
      "duration": 3600
    },
    {
      "name": "è´¢ç»å°æ",
      "url": "https://live.douyin.com/yall1102",
      "schedule": {
        "start_time": "20:00",
        "end_time": "22:00"
      },
      "weight": 1.0,
      "tags": ["åºæ¬é?, "ä»·å¼æèµ?],
      "duration": 3600
    },
    {
      "name": "æèµè¾¾äºº",
      "url": "https://live.douyin.com/123456789",
      "schedule": {
        "start_time": "18:00",
        "end_time": "20:00"
      },
      "weight": 0.8,
      "tags": ["éåäº¤æ", "ç¨åºå?],
      "duration": 3600
    }
  ]
}
```

---

## ð é¨ç½²æ¹æ¡

### æ¹æ¡ä¸: æ¬å°é¨ç½²

```bash
# 1. åéé¡¹ç®
git clone https://github.com/your-repo/live-stream-financial-analysis.git
cd live-stream-financial-analysis

# 2. å®è£ä¾èµ
pip install -r requirements.txt

# 3. å®è£FFmpeg
# Windows: ä¸è½½ https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 4. éç½®ç¯å¢åé
export OPENAI_API_KEY="your-api-key"

# 5. è¿è¡ç³»ç»
python main.py
```

### æ¹æ¡äº? Dockeré¨ç½²

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# å®è£ç³»ç»ä¾èµ
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*

# å®è£Pythonä¾èµ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# å¤å¶ä»£ç 
COPY . .

# è¿è¡
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

## ð ä½¿ç¨ç¤ºä¾

### å¯å¨ç³»ç»

```python
import asyncio
import yaml
from live_stream_financial_system import LiveStreamFinancialSystem

async def main():
    # å è½½éç½®
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # å è½½ä¸»æ­åè¡¨
    with open('streamer_list.json', 'r', encoding='utf-8') as f:
        streamer_data = json.load(f)
    
    # åå§åç³»ç»?
    system = LiveStreamFinancialSystem(config)
    
    # è¿è¡ç³»ç»
    factors = await system.run(streamer_data["streamers"])
    
    # è¾åºç»æ
    print("=== é¢æµå å­ ===")
    print(f"ç»¼åå å­: {factors['composite_factor']:.3f}")
    print(f"æç»ªå å­: {factors['sentiment_factor']:.3f}")
    print(f"ä¸è´æ? {factors['consensus_factor']:.2%}")
    print(f"å½±åå? {factors['influence_factor']:.3f}")
    print(f"ç­é¨æ¿å: {list(factors['sector_factors'].keys())[:5]}")
    
    # ä¿å­ç»æ
    system.save_results(f"./results/result_{datetime.now().strftime('%Y%m%d')}.json")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ð è¾åºç¤ºä¾

### å å­è¾åº

```json
{
  "sentiment_factor": 0.72,
  "consensus_factor": 0.78,
  "influence_factor": 0.85,
  "confidence_factor": 0.68,
  "sector_factors": {
    "äººå·¥æºè½": 0.65,
    "æ°è½æº?: 0.58,
    "åå¯¼ä½?: 0.42,
    "å»è¯": 0.35,
    "æ¶è´¹": 0.28
  },
  "composite_factor": 0.734,
  "metadata": {
    "dominant_view": "çå¤",
    "total_streamers": 10,
    "avg_online_count": 125000
  },
  "timestamp": "2026-04-02T20:30:00"
}
```

---

## ð§ æ©å±åè½

### 1. å®æ¶ä»»å¡

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def scheduled_analysis():
    """å®æ¶åæä»»å¡"""
    scheduler = AsyncIOScheduler()
    
    # æ¯å¤©19:00æ§è¡
    scheduler.add_job(
        run_analysis,
        'cron',
        hour=19,
        minute=0
    )
    
    scheduler.start()
```

### 2. Webçé¢

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/factors")
async def get_factors():
    """è·åææ°å å­?""
    return JSONResponse(content=latest_factors)

@app.get("/streamers")
async def get_streamers():
    """è·åä¸»æ­åè¡¨"""
    return JSONResponse(content=streamer_list)
```

### 3. æ°æ®åºå­å?

```python
import asyncpg

async def save_to_database(factors: Dict):
    """ä¿å­å å­å°æ°æ®åº"""
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

## ð æ³¨æäºé¡¹

### 1. æ³å¾åè§

- â ï¸ è¯·éµå®æé³å¹³å°çä½¿ç¨æ¡æ¬¾
- â ï¸ ä»ç¨äºä¸ªäººå­¦ä¹ åç ç©¶
- â ï¸ ä¸è¦ç¨äºåä¸ç¨é?
- â ï¸ å°éä¸»æ­çç¥è¯äº§æ?

### 2. ææ¯éå?

- â ï¸ éå®æ¹APIå¯è½éæ¶å¤±æ
- â ï¸ éè¦ç¨³å®çç½ç»ç¯å¢
- â ï¸ Whisperè½¬å½éè¦è¶³å¤çè®¡ç®èµæº
- â ï¸ OpenAI APIæè°ç¨éå?

### 3. æ°æ®è´¨é

- â ï¸ ä¸»æ­è§ç¹ä»ä¾åèï¼ä¸æææèµå»ºè®?
- â ï¸ éè¦éªè¯å å­çæææ?
- â ï¸ å»ºè®®ç»åå¶ä»æ°æ®æº?

---

## ð¯ æªæ¥ä¼åæ¹å

1. **æ§è½ä¼å**
   - ä½¿ç¨GPUå éWhisperè½¬å½
   - ä¼åå¹¶åå¤çè½å
   - å®ç°å¢éè½¬å½

2. **åè½æ©å±**
   - æ¯ææ´å¤ç´æ­å¹³å°
   - æ·»å å®æ¶å å­æ´æ°
   - å®ç°å å­åæµ

3. **åç¡®æ§æå?*
   - è®­ç»ä¸é¨çéèé¢åWhisperæ¨¡å
   - ä¼åè§ç¹æåprompt
   - æ·»å å¤ç»´åº¦éªè¯?

---

**çæ¬**: 1.0.0 | **æ´æ°æ¥æ**: 2026-04-02 | **ç¶æ?*: â?å·²å®æ? 
**ä¸ä¸æ­?*: å®æ½å¼å?â?æµè¯éªè¯ â?çäº§é¨ç½²
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Live Stream Financial Analysis
- **模块ID**: LIVE_STREAM_FINANCIAL_ANALYSIS_001
- **蓝图文档**: [LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md](./04_EXECUTION\07_LIVE_STREAM\LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: å¤ä¸»æ­ç´æ­åå®¹åæä¸å å­çæ
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Live Stream Financial Analysis** | å¤ä¸»æ­ç´æ­åå®¹åæä¸å å­çæ | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-02 | **状态**: Active
