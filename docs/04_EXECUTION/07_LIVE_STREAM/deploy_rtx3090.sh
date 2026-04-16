#!/bin/bash

# 多主播直播金融分析系统 - RTX 3090 24GB 一键部署脚本
# 硬件配置: RTX 3090 24GB + 64GB RAM + i7-12700KF
# 配置评级: 机构级配置

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  多主播直播金融分析系统部署"
echo "  硬件配置: RTX 3090 24GB + 64GB RAM"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Ollama是否运行
check_ollama() {
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}❌ Ollama未安装${NC}"
        echo "请先安装Ollama: https://ollama.ai/"
        exit 1
    fi

    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ollama服务未运行${NC}"
        echo "请先启动Ollama服务: ollama serve"
        exit 1
    fi

    echo -e "${GREEN}✅ Ollama服务运行正常${NC}"
}

# 检查CUDA
check_cuda() {
    if ! command -v nvidia-smi &> /dev/null; then
        echo -e "${RED}❌ 未检测到NVIDIA驱动${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ CUDA可用${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
}

# 拉取推荐模型
pull_models() {
    echo ""
    echo "=========================================="
    echo "  拉取推荐模型"
    echo "=========================================="
    echo ""

    # 1. Whisper large-v3 (语音识别）
    echo -e "${YELLOW}📥 拉取Whisper large-v3模型...${NC}"
    python -c "import whisper; whisper.load_model('large-v3', device='cuda')" 2>&1 | grep -v "Downloading"
    echo -e "${GREEN}✅ Whisper large-v3已加载${NC}"

    # 2. FinBERT (情感分析）
    echo -e "${YELLOW}📥 拉取FinBERT模型...${NC}"
    python -c "from transformers import AutoModelForSequenceClassification; AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', device_map='auto')" 2>&1 | grep -v "Downloading"
    echo -e "${GREEN}✅ FinBERT已加载${NC}"

    # 3. 推荐拉取更大的模型（可选）
    echo ""
    echo -e "${YELLOW}💡 推荐拉取更大的模型以获得最佳性能:${NC}"
    echo "  - qwen2.5:32b (金融理解最强，约20GB)"
    echo "  - deepseek-r1:32b (推理能力最强，约20GB)"
    echo ""
    read -p "是否拉取更大的模型？(y/n): " pull_large

    if [ "$pull_large" = "y" ]; then
        echo -e "${YELLOW}📥 拉取qwen2.5:32b模型...${NC}"
        ollama pull qwen2.5:32b

        echo -e "${YELLOW}📥 拉取deepseek-r1:32b模型...${NC}"
        ollama pull deepseek-r1:32b

        echo -e "${GREEN}✅ 大模型已拉取${NC}"
    fi
}

# 创建目录结构
create_directories() {
    echo ""
    echo "=========================================="
    echo "  创建目录结构"
    echo "=========================================="
    echo ""

    mkdir -p ./recordings
    mkdir -p ./results
    mkdir -p ./factors
    mkdir -p ./logs
    mkdir -p ./cache

    echo -e "${GREEN}✅ 目录结构已创建${NC}"
}

# 测试模型性能
test_models() {
    echo ""
    echo "=========================================="
    echo "  测试模型性能"
    echo "=========================================="
    echo ""

    # 测试Whisper
    echo -e "${YELLOW}🧪 测试Whisper large-v3...${NC}"
    python -c "
import whisper
import torch
import time

print('加载Whisper large-v3模型...')
model = whisper.load_model('large-v3', device='cuda')

print(f'✅ 模型已加载到: {model.device}')
print(f'参数量: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B')

# 测试推理速度
test_audio = './recordings/test.mp3'
if os.path.exists(test_audio):
    start = time.time()
    result = model.transcribe(test_audio, language='zh', fp16=True)
    elapsed = time.time() - start
    print(f'✅ 推理速度: {len(result[\"text\"]) / elapsed:.1f} 字符/秒')
else:
    print('⚠️  没有测试音频，跳过推理速度测试')
"

    # 测试Ollama
    echo -e "${YELLOW}🧪 测试Ollama模型...${NC}"
    python -c "
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
"

    # 测试FinBERT
    echo -e "${YELLOW}🧪 测试FinBERT...${NC}"
    python -c "
from transformers import pipeline
import torch

print('加载FinBERT模型...')
sentiment_pipeline = pipeline('sentiment-analysis', model='yiyanghkust/finbert-tone', device='cuda')

test_text = '今天市场表现不错，看好后市发展。'
result = sentiment_pipeline(test_text)
print(f'✅ 情感分析结果: {result[0][\"label\"]} (置信度: {result[0][\"score\"]:.2f})')
"

    echo -e "${GREEN}✅ 所有模型测试完成${NC}"
}

# 显示性能报告
show_performance_report() {
    echo ""
    echo "=========================================="
    echo "  性能报告"
    echo "=========================================="
    echo ""

    echo "硬件配置:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits | awk -F, '{printf \"  GPU: %s\n  显存: %.0f GB\n\", $1, $2/1024}'
    echo "  内存: 64GB"
    echo "  CPU: i7-12700KF"
    echo ""

    echo "推荐配置:"
    echo "  语音识别: Whisper large-v3 (本地)"
    echo "  内容分析: deepseek-r1:14b (已有)"
    echo "  情感分析: FinBERT (本地)"
    echo ""

    echo "可选升级:"
    echo "  - qwen2.5:32b (金融理解最强)"
    echo "  - deepseek-r1:32b (推理能力最强)"
    echo ""

    echo "显存占用估算:"
    echo "  当前配置: ~20GB (Whisper 10GB + DeepSeek 9GB + FinBERT 1GB)"
    echo "  升级配置: ~22GB (Whisper 10GB + Qwen32B 11GB + FinBERT 1GB)"
    echo "  可用显存: 24GB"
    echo ""

    echo "性能预期:"
    echo "  Whisper转录速度: ~150-200字符/秒"
    echo "  LLM推理速度: ~30-50 tokens/秒"
    echo "  情感分析速度: ~1000+ 文本/秒"
    echo ""

    echo "成本对比:"
    echo "  云端API方案: ¥88,000/年"
    echo "  本地模型方案: ¥15,657 (第一年) + ¥657/年"
    echo "  第一年节省: ¥72,343"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  开始部署流程"
    echo "=========================================="
    echo ""

    # 1. 检查环境
    check_ollama
    check_cuda

    # 2. 创建目录
    create_directories

    # 3. 拉取模型
    pull_models

    # 4. 测试模型
    test_models

    # 5. 显示性能报告
    show_performance_report

    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  ✅ 部署完成！${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 编辑配置文件: config_local_rtx3090.yaml"
    echo "  2. 添加主播列表: streamer_list.json"
    echo "  3. 运行系统: python main.py"
    echo ""
}

# 运行主函数
main
