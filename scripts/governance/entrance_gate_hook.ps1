# entrance_gate_hook.ps1 -- PreToolUse entrance ticket-check launcher (MOD-GOV-115).
# Pure ASCII per repo ops red-line 9.7 (PowerShell 5.1 decodes BOM-less files as GBK).
# Chain: ZCode hook runner -> this launcher -> entrance_gate_hook.py.
# Why a launcher: the hook process PATH is uncontrolled (bare "python" may be absent
# or be a wrong-version interpreter), and relaying hook stdin through the pipeline
# would re-encode non-ASCII tool_input via the console codepage. So we probe the
# standard per-user Python install locations first, then PATH; and we relay stdin
# as raw bytes through a temp file (encoding-safe hand-off).
# Fail-open contract (mirrors entrance_gate_hook.py ERROR_CONTRACT): any internal
# error in THIS launcher => exit 0 (never block construction on fence defects).

$ErrorActionPreference = "Stop"

function Find-PythonExe {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python310\python.exe")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    try { return (Get-Command python -ErrorAction Stop).Source } catch { return $null }
}

try {
    $py = Find-PythonExe
    if (-not $py) { exit 0 }

    $ms = New-Object System.IO.MemoryStream
    [Console]::OpenStandardInput().CopyTo($ms)

    $tmp = [IO.Path]::GetTempFileName()
    try {
        [IO.File]::WriteAllBytes($tmp, $ms.ToArray())
        $script = Join-Path $PSScriptRoot "entrance_gate_hook.py"
        $env:PYTHONIOENCODING = "utf-8"
        & $py $script $tmp
        exit $LASTEXITCODE
    } finally {
        Remove-Item $tmp -ErrorAction SilentlyContinue
    }
} catch {
    exit 0
}
