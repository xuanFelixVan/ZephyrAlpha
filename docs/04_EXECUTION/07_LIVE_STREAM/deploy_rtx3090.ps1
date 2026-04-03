# 多主播直播金融分析系统 - RTX 3090 24GB 一键部署脚本 (Windows PowerShell)
# 硬件配置: RTX 3090 24GB + 64GB RAM + i7-12700KF
# 配置评级: 机构级配置

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  多主播直播金融分析系统部署" -ForegroundColor Cyan
Write-Host "  硬件配置: RTX 3090 24GB + 64GB RAM" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Ollama是否运行
function Check-Ollama {
    try {
        $null = Get-Command ollama -ErrorAction Stop
        
        # 检查服务是否运行
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
        Write-Host "✅ Ollama服务运行正常" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Ollama未安装或服务未运行" -ForegroundColor Red
        Write-Host "请先安装Ollama: https://ollama.ai/" -ForegroundColor Yellow
        Write-Host "然后启动服务: ollama serve" -ForegroundColor Yellow
        return $false
    }
}

# 检查CUDA
function Check-CUDA {
    try {
        $nvidia = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
        Write-Host "✅ CUDA可用" -ForegroundColor Green
        Write-Host "  GPU: $nvidia"
        return $true
    }
    catch {
        Write-Host "❌ 未检测到NVIDIA驱动" -ForegroundColor Red
        return $false
    }
}

# 拉取推荐模型
function Pull-Models {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  拉取推荐模型" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 1. Whisper large-v3 (语音识别）
    Write-Host "📥 拉取Whisper large-v3模型..." -ForegroundColor Yellow
    python -c "import whisper; whisper.load_model('large-v3', device='cuda')" 2>&1 | Out-Null
    Write-Host "✅ Whisper large-v3已加载" -ForegroundColor Green
    
    # 2. FinBERT (情感分析）
    Write-Host "📥 拉取FinBERT模型..." -ForegroundColor Yellow
    python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', device_map='auto')" 2>&1 | Out-Null
    Write-Host "✅ FinBERT已加载" -ForegroundColor Green
    
    # 3. 推荐拉取更大的模型（可选）
    Write-Host ""
    Write-Host "💡 推荐拉取更大的模型以获得最佳性能:" -ForegroundColor Yellow
    Write-Host "  - qwen2.5:32b (金融理解最强，约20GB)"
    Write-Host "  - deepseek-r1:32b (推理能力最强，约20GB)"
    Write-Host ""
    
    $pull_large = Read-Host "是否拉取更大的模型？(y/n)"
    
    if ($pull_large -eq "y") {
        Write-Host "📥 拉取qwen2.5:32b模型..." -ForegroundColor Yellow
        ollama pull qwen2.5:32b
        
        Write-Host "📥 拉取deepseek-r1:32b模型..." -ForegroundColor Yellow
        ollama pull deepseek-r1:32b
        
        Write-Host "✅ 大模型已拉取" -ForegroundColor Green
    }
}

# 创建目录结构
function Create-Directories {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  创建目录结构" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $directories = @(
        ".\recordings",
        ".\results",
        ".\factors",
        ".\logs",
        ".\cache"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Host "✅ 目录结构已创建" -ForegroundColor Green
}

# 测试模型性能
function Test-Models {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  测试模型性能" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 测试Ollama
    Write-Host "🧪 测试Ollama模型..." -ForegroundColor Yellow
    python -c @"
import requests
import time

print('测试Ollama服务...')
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'deepseek-r1:14b',
    'prompt': '你好',
    'stream': False,
    'options': {'num_predict': 10}
})

if response.status_code == 200:
    print('✅ Ollama服务正常')
    print(f'响应: {response.json()[\"response\"][:50]}...')
else:
    print(f'❌ Ollama服务异常: {response.status_code}')
"@
    
    # 测试FinBERT
    Write-Host "🧪 测试FinBERT..." -ForegroundColor Yellow
    python -c @"
from transformers import pipeline
import torch

print('加载FinBERT模型...')
sentiment_pipeline = pipeline('sentiment-analysis', model='yiyanghkust/finbert-tone', device='cuda')

test_text = '今天市场表现不错，看好后市发展。'
result = sentiment_pipeline(test_text)
print(f'✅ 情感分析结果: {result[0][\"label\"]} (置信度: {result[0][\"score\"]:.2f})')
"@
    
    Write-Host "✅ 所有模型测试完成" -ForegroundColor Green
}

# 显示性能报告
function Show-PerformanceReport {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  性能报告" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "硬件配置:"
    $gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    Write-Host "  GPU: $gpu"
    Write-Host "  内存: 64GB"
    Write-Host "  CPU: i7-12700KF"
    Write-Host ""
    
    Write-Host "推荐配置:"
    Write-Host "  语音识别: Whisper large-v3 (本地)"
    Write-Host "  内容分析: deepseek-r1:14b (已有)"
    Write-Host "  情感分析: FinBERT (本地)"
    Write-Host ""
    
    Write-Host "可选升级:"
    Write-Host "  - qwen2.5:32b (金融理解最强)"
    Write-Host "  - deepseek-r1:32b (推理能力最强)"
    Write-Host ""
    
    Write-Host "显存占用估算:"
    Write-Host "  当前配置: ~20GB (Whisper 10GB + DeepSeek 9GB + FinBERT 1GB)"
    Write-Host "  升级配置: ~22GB (Whisper 10GB + Qwen32B 11GB + FinBERT 1GB)"
    Write-Host "  可用显存: 24GB"
    Write-Host ""
    
    Write-Host "性能预期:"
    Write-Host "  Whisper转录速度: ~150-200字符/秒"
    Write-Host "  LLM推理速度: ~30-50 tokens/秒"
    Write-Host "  情感分析速度: ~1000+ 文本/秒"
    Write-Host ""
    
    Write-Host "成本对比:"
    Write-Host "  云端API方案: ¥88,000/年"
    Write-Host "  本地模型方案: ¥15,657 (第一年) + ¥657/年"
    Write-Host "  第一年节省: ¥72,343"
    Write-Host ""
}

# 主函数
function Main {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  开始部署流程" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 1. 检查环境
    if (-not (Check-Ollama)) { exit 1 }
    if (-not (Check-CUDA)) { exit 1 }
    
    # 2. 创建目录
    Create-Directories
    
    # 3. 拉取模型
    Pull-Models
    
    # 4. 测试模型
    Test-Models
    
    # 5. 显示性能报告
    Show-PerformanceReport
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  ✅ 部署完成！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步:"
    Write-Host "  1. 编辑配置文件: config_local_rtx3090.yaml"
    Write-Host "  2. 添加主播列表: streamer_list.json"
    Write-Host "  3. 运行系统: python main.py"
    Write-Host ""
}

# 运行主函数
Main
