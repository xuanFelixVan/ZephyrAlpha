"""
RTX 3090 24GB 模型配置测试脚本
快速测试您的硬件配置和模型性能
"""

import sys
import time
import json
import subprocess
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def check_cuda():
    """检查CUDA和GPU"""
    print_header("1. 检查CUDA和GPU")
    
    try:
        import torch
        print_success(f"PyTorch版本: {torch.__version__}")
        print_success(f"CUDA可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print_success(f"CUDA版本: {torch.version.cuda}")
            print_success(f"GPU数量: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print_success(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            
            return True
        else:
            print_error("CUDA不可用")
            return False
    except ImportError:
        print_error("PyTorch未安装")
        return False

def check_ollama():
    """检查Ollama服务"""
    print_header("2. 检查Ollama服务")
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print_success("Ollama服务运行正常")
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                print_info("已安装的模型:")
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            model_name = parts[0]
                            model_size = parts[2]
                            print(f"  - {model_name} ({model_size})")
            
            return True
        else:
            print_error("Ollama服务异常")
            return False
    except FileNotFoundError:
        print_error("Ollama未安装")
        print_info("请访问: https://ollama.ai/")
        return False
    except subprocess.TimeoutExpired:
        print_error("Ollama服务超时")
        return False

def test_whisper():
    """测试Whisper模型"""
    print_header("3. 测试Whisper模型")
    
    try:
        import whisper
        import torch
        
        print_info("加载Whisper large-v3模型...")
        start_time = time.time()
        
        model = whisper.load_model('large-v3', device='cuda')
        
        load_time = time.time() - start_time
        print_success(f"模型加载成功 (耗时: {load_time:.1f}秒)")
        
        model_size = sum(p.numel() for p in model.parameters()) / 1e9
        print_success(f"模型参数量: {model_size:.2f}B")
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / 1024**3
            print_success(f"GPU显存占用: {gpu_memory:.2f} GB")
        
        return True
    except ImportError:
        print_error("Whisper未安装")
        print_info("安装命令: pip install openai-whisper")
        return False
    except Exception as e:
        print_error(f"Whisper测试失败: {str(e)}")
        return False

def test_finbert():
    """测试FinBERT模型"""
    print_header("4. 测试FinBERT模型")
    
    try:
        from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
        import torch
        
        print_info("加载FinBERT模型...")
        start_time = time.time()
        
        model_name = "yiyanghkust/finbert-tone"
        sentiment_pipeline = pipeline(
            'sentiment-analysis',
            model=model_name,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        load_time = time.time() - start_time
        print_success(f"模型加载成功 (耗时: {load_time:.1f}秒)")
        
        test_texts = [
            "今天市场表现不错，看好后市发展。",
            "股价大跌，投资者信心受挫。",
            "市场震荡，观望情绪浓厚。"
        ]
        
        print_info("测试情感分析:")
        for text in test_texts:
            result = sentiment_pipeline(text)[0]
            print(f"  文本: {text}")
            print(f"  结果: {result['label']} (置信度: {result['score']:.2f})")
            print()
        
        return True
    except ImportError:
        print_error("Transformers未安装")
        print_info("安装命令: pip install transformers")
        return False
    except Exception as e:
        print_error(f"FinBERT测试失败: {str(e)}")
        return False

def test_ollama_model():
    """测试Ollama模型"""
    print_header("5. 测试Ollama模型")
    
    try:
        import requests
        
        models_to_test = ['deepseek-r1:14b', 'qwen2.5:32b']
        
        for model in models_to_test:
            print_info(f"测试模型: {model}")
            
            try:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': model,
                        'prompt': '你好，请简单介绍一下自己。',
                        'stream': False,
                        'options': {'num_predict': 50}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print_success(f"{model} 测试成功")
                    print(f"响应: {result['response'][:100]}...")
                    print()
                    return True
                else:
                    print_warning(f"{model} 测试失败 (状态码: {response.status_code})")
            except requests.exceptions.Timeout:
                print_warning(f"{model} 响应超时")
            except Exception as e:
                print_warning(f"{model} 测试失败: {str(e)}")
        
        return False
    except ImportError:
        print_error("Requests未安装")
        print_info("安装命令: pip install requests")
        return False

def show_recommendations():
    """显示推荐配置"""
    print_header("6. 推荐配置")
    
    print("🏆 推荐方案一：使用现有模型（立即可用）")
    print("  语音识别: Whisper large-v3 (本地)")
    print("  内容分析: deepseek-r1:14b (已有)")
    print("  情感分析: FinBERT (本地)")
    print("  显存占用: ~20GB / 24GB")
    print()
    
    print("🥈 推荐方案二：拉取更大模型（最佳性能）")
    print("  语音识别: Whisper large-v3 (本地)")
    print("  内容分析: qwen2.5:32b (推荐拉取)")
    print("  情感分析: FinBERT (本地)")
    print("  显存占用: ~22GB / 24GB")
    print()
    
    print("📥 拉取命令:")
    print("  ollama pull qwen2.5:32b")
    print()

def show_next_steps():
    """显示下一步操作"""
    print_header("7. 下一步操作")
    
    print("1. 编辑配置文件:")
    print("   config_local_rtx3090.yaml")
    print()
    
    print("2. 添加主播列表:")
    print("   streamer_list.json")
    print()
    
    print("3. 运行系统:")
    print("   python main.py")
    print()

def main():
    print("\n" + "="*60)
    print("  RTX 3090 24GB 模型配置测试")
    print("="*60)
    
    results = {
        'cuda': check_cuda(),
        'ollama': check_ollama(),
        'whisper': test_whisper(),
        'finbert': test_finbert(),
        'ollama_model': test_ollama_model()
    }
    
    show_recommendations()
    show_next_steps()
    
    print_header("测试结果汇总")
    
    total = len(results)
    passed = sum(results.values())
    
    for test, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test.upper():15} {status}")
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print_success("所有测试通过！系统可以正常运行。")
    elif passed >= 3:
        print_warning("部分测试通过，系统可以基本运行。")
    else:
        print_error("测试失败较多，请检查环境配置。")

if __name__ == "__main__":
    main()
