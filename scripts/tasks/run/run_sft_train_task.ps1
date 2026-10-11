# [BLUEPRINT] MOD-SCRIPT-run_sft_train | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] scripts.run_sft_train_task
# [DOMAIN] D_ML_TRAIN
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_sft_train_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_sft_train_task.ps1 - Guard wrapper for the QLoRA sentiment SFT full run.
# Fired by Task Scheduler ZephyrAlpha_SftTrainWindow (biweekly Sunday 10:00, gpu_default group),
#   or manually: schtasks /run /tn ZephyrAlpha_SftTrainWindow
#
# Why a guard wrapper instead of a bare training command on a timer:
#   zephyr/ml_train/services/sentiment_sft_entry.py declares in its INVARIANTS that real LLM
#   training is a B-007 human-gate item ("dry_run=False ... AI must not self-trigger"). The
#   existing CLI scripts/ml/run_sft_train.py does NOT route through that entry, so a plain
#   scheduled task would silently press the Owner's button on a timer. This wrapper keeps the
#   window reservation visible to the resource scheduler while making the real run
#   opt-in-only:
#     - the task fires, checks for the authorization file, and exits 0 (no training) if absent;
#     - Owner presses the button by creating  data/runtime/sft_train_authorization.txt
#       containing the literal token  RUN_SFT_TRAIN_FULL_APPROVED  (one line, ASCII);
#     - delete that file to stop further runs (the wrapper never deletes it itself).
#   After one approved run the wrapper renames the file to .consumed so a window cannot train
#   twice on a single authorization.
#
# Hard scheduling discipline honored here (root constitution s9 items 3/4 and the Owner order
# for this shift): refuses to start inside the 01:00-04:00 ClickHouse yield window, and refuses
# to start when the GPU is already busy above GPU_BUSY_MEM_MIB (avoid contending with the
# night Ollama window).
#
# Log append-only: .runtime/logs/sft_train.log
# rc discipline (mirrors run_factory_lane_c.ps1): every segment rc captured and checked; a
#   failure logs "==== <seg> FAILED rc=N ====", raises an Alerter ERROR, exits with that rc.
# PS5.1 landmine (documented in run_factory_lane_c.ps1): with ErrorActionPreference=Stop,
#   piping python stderr through Out-File turns warnings into terminating ErrorRecords, so all
#   python calls go through cmd.exe redirection into the log.

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$AuthFile = Join-Path $RepoRoot "data\runtime\sft_train_authorization.txt"
$AuthToken = "RUN_SFT_TRAIN_FULL_APPROVED"
# Measured necessity (st-gpuwo-20261011, 2026-10-11 23:0x): transformers' AutoTokenizer reaches
# out to huggingface.co from _patch_mistral_regex -> model_info even when the weights are already
# in the local cache; with HF unreachable the run dies in ConnectTimeout before training starts.
# Both base weights (models--Qwen--Qwen2.5-7B-Instruct, 15G, 4 shards) and the FPB dataset cache
# are on disk, so the whole chain is forced offline here instead of depending on the network.
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$LogDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Log = Join-Path $LogDir "sft_train.log"
$GpuBusyMemMib = 12000

function Write-Log([string]$Line) {
    $Line | Out-File -FilePath $Log -Append -Encoding utf8
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Log "==== SFT train window fired at $stamp ===="

# Gate 1: CH yield window 01:00-04:00 - never start a 4h batch inside it.
$hour = (Get-Date).Hour
if ($hour -ge 1 -and $hour -lt 4) {
    Write-Log "==== SKIPPED: inside 01:00-04:00 ClickHouse yield window (no batch allowed) ===="
    exit 0
}

# Gate 2: Owner authorization must be present (B-007 real-training button).
if (-not (Test-Path $AuthFile)) {
    Write-Log "==== AWAITING-OWNER-AUTHORIZATION: $AuthFile absent - window reserved, zero training done ===="
    exit 0
}
$authText = (Get-Content -Path $AuthFile -Raw)
if ($authText -notmatch [regex]::Escape($AuthToken)) {
    Write-Log "==== DENIED: authorization file present but token '$AuthToken' not found ===="
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('sft_train', 'authorization file present but token missing', 'ERROR')"" >> $Log 2>&1"
    exit 1
}
# Consume the authorization so one approval cannot fire in two windows.
$consumed = "$AuthFile.consumed"
Move-Item -Path $AuthFile -Destination $consumed -Force
Write-Log "==== authorization consumed (moved to $consumed) ===="

# Gate 3: GPU must be free enough for a QLoRA 7B run (do not contend with Ollama night window).
$gpuLine = ""
try {
    $gpuLine = (nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null | Select-Object -First 1)
} catch {
    $gpuLine = ""
}
if ($gpuLine -match '^\s*(\d+)\s*$') {
    $usedMib = [int]$Matches[1]
    Write-Log "==== gpu memory used = $usedMib MiB (refuse threshold $GpuBusyMemMib MiB) ===="
    if ($usedMib -gt $GpuBusyMemMib) {
        Write-Log "==== SKIPPED: GPU busy ($usedMib MiB in use) - window reserved, retry next window ===="
        cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('sft_train', 'GPU busy at window start, skipped', 'WARN')"" >> $Log 2>&1"
        exit 0
    }
} else {
    Write-Log "==== WARN: nvidia-smi unreadable, proceeding without GPU precheck ===="
}

# Segment 1: full QLoRA SFT training + Macro-F1 validate (metrics land in data/eval/sft_metrics.json)
cmd.exe /c "python scripts\ml\run_sft_train.py --epochs 3 --batch-size 4 --grad-accum 4 >> $Log 2>&1"
$trainExit = $LASTEXITCODE
"==== train exit code $trainExit ====" | Out-File -FilePath $Log -Append -Encoding utf8
if ($trainExit -ne 0) {
    "==== train FAILED rc=$trainExit - convert step SKIPPED ====" | Out-File -FilePath $Log -Append -Encoding utf8
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('sft_train', 'train FAILED rc=$trainExit', 'ERROR')"" >> $Log 2>&1"
    exit $trainExit
}

# Segment 2: dry-run of the GGUF/Ollama chain only. Real conversion needs the llama.cpp toolchain,
# which is an Owner-gated software install (see docs/_working/gpuwo_campaign/01_anchor_reverify_lanec.yaml R-1).
# Keeping this leg at --dry-run means an approved training window can never half-install external tools.
cmd.exe /c "python scripts\ml\convert_gguf_ollama.py --dry-run >> $Log 2>&1"
$planExit = $LASTEXITCODE
"==== convert dry-run exit code $planExit ====" | Out-File -FilePath $Log -Append -Encoding utf8
if ($planExit -ne 0) {
    "==== convert dry-run FAILED rc=$planExit ====" | Out-File -FilePath $Log -Append -Encoding utf8
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('sft_train', 'convert dry-run FAILED rc=$planExit', 'ERROR')"" >> $Log 2>&1"
    exit $planExit
}

"==== SFT window chain rc all green (train/convert-plan) - E9 heartbeat ====" | Out-File -FilePath $Log -Append -Encoding utf8
cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('sft_train', 'SFT window chain green', 'INFO')"" >> $Log 2>&1"
"==== exit code 0 ====" | Out-File -FilePath $Log -Append -Encoding utf8
exit 0
