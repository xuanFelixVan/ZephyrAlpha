# RTX 3090 Environment Setup Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RTX 3090 Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Uninstall CPU version of PyTorch
Write-Host "Step 1: Uninstalling CPU version of PyTorch..." -ForegroundColor Yellow
try {
    pip uninstall -y torch torchvision torchaudio 2>&1 | Out-Null
    Write-Host "  [OK] Old PyTorch version uninstalled" -ForegroundColor Green
}
catch {
    Write-Host "  [WARN] PyTorch not installed or uninstall failed, continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Install CUDA version of PyTorch
Write-Host "Step 2: Installing CUDA version of PyTorch..." -ForegroundColor Yellow
Write-Host "  Download URL: https://download.pytorch.org/whl/cu121" -ForegroundColor Gray
Write-Host "  Estimated time: 5-10 minutes" -ForegroundColor Gray
Write-Host ""

try {
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    Write-Host "  [OK] PyTorch CUDA version installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] PyTorch installation failed" -ForegroundColor Red
    Write-Host "  Please try manual installation: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 3: Install Whisper
Write-Host "Step 3: Installing Whisper..." -ForegroundColor Yellow
try {
    pip install openai-whisper
    Write-Host "  [OK] Whisper installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Whisper installation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Install other dependencies
Write-Host "Step 4: Installing other dependencies..." -ForegroundColor Yellow
$packages = @("transformers", "accelerate", "requests", "ffmpeg-python")

foreach ($package in $packages) {
    try {
        pip install $package 2>&1 | Out-Null
        Write-Host "  [OK] $package" -ForegroundColor Green
    }
    catch {
        Write-Host "  [WARN] $package installation failed" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 5: Download Whisper large-v3 model
Write-Host "Step 5: Downloading Whisper large-v3 model..." -ForegroundColor Yellow
Write-Host "  Model size: ~3GB" -ForegroundColor Gray
Write-Host "  Estimated time: 5-10 minutes" -ForegroundColor Gray
Write-Host ""

try {
    python -c "import whisper; print('Downloading Whisper large-v3 model...'); whisper.load_model('large-v3', device='cuda')"
    Write-Host "  [OK] Whisper large-v3 model downloaded successfully" -ForegroundColor Green
}
catch {
    Write-Host "  [WARN] Whisper model download failed, please download manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Verify installation
Write-Host "Step 6: Verifying installation..." -ForegroundColor Yellow
Write-Host ""

try {
    python test_rtx3090_models.py
}
catch {
    Write-Host "  [ERROR] Verification failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run test: python test_rtx3090_models.py" -ForegroundColor White
Write-Host "  2. Pull larger model: ollama pull qwen2.5:32b" -ForegroundColor White
Write-Host "  3. Configure system: Edit config_local_rtx3090.yaml" -ForegroundColor White
Write-Host "  4. Start system: python main.py" -ForegroundColor White
Write-Host ""

Write-Host "Recommended Configuration:" -ForegroundColor Cyan
Write-Host "  Speech Recognition: Whisper large-v3 (local)" -ForegroundColor White
Write-Host "  Content Analysis: deepseek-r1:14b (existing)" -ForegroundColor White
Write-Host "  Sentiment Analysis: FinBERT (local)" -ForegroundColor White
Write-Host "  GPU Memory: ~20GB / 24GB" -ForegroundColor White
Write-Host ""

Write-Host "Optional Upgrade:" -ForegroundColor Cyan
Write-Host "  ollama pull qwen2.5:32b  # Best financial understanding" -ForegroundColor White
Write-Host "  ollama pull deepseek-r1:32b  # Best reasoning capability" -ForegroundColor White
Write-Host ""
