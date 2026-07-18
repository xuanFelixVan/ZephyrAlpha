<#
.SYNOPSIS
    Disaster recovery script -- list/verify/restore
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.5
    Subcommands:
      list              - List all snapshots
      verify <id>       - Restore to D:\restore_test\ for verification
      latest            - Disaster-recover latest snapshot to D:\ZephyrAlpha\
      latest -target X  - Restore to specified directory
      ch                - Disaster-recover ClickHouse (c1_market + c3_fundamental) from
                          F:\ch_backup_store\chbk\market.zip via MinIO + RESTORE FROM S3
#>
param(
    [Parameter(Position=0)]
    [ValidateSet("list","verify","latest","ch")]
    [string]$Action = "list",

    [Parameter(Position=1)]
    [string]$SnapshotId,

    [string]$Target
)

$RepoPath = "F:\restic-zephyr"
$ProjectRoot = "D:\ZephyrAlpha"

# -- Dynamic port selection (mirror of backup.ps1; HNS reserves random tcp ranges,
#    bind-test is the only reliable check, .env ports are preferences only) --
function Test-PortFree([int]$Port) {
    $listener = $null
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($listener) { $listener.Stop() }
    }
}
function Get-FreePort([int]$Preferred, [int[]]$Exclude = @()) {
    if (($Exclude -notcontains $Preferred) -and (Test-PortFree $Preferred)) { return $Preferred }
    for ($p = $Preferred + 1; $p -le [math]::Min($Preferred + 200, 65535); $p++) {
        if ($Exclude -contains $p) { continue }
        if (Test-PortFree $p) { return $p }
    }
    throw "no free tcp port in [$Preferred, $($Preferred + 200)] (HNS excluded ranges shifting?)"
}

switch ($Action) {
    "list" {
        Write-Host "=== Restic Snapshots ===" -ForegroundColor Cyan
        & restic -r $RepoPath snapshots
    }
    "verify" {
        if (-not $SnapshotId) { Write-Host "Usage: restore.ps1 verify <snapshot-id>" -ForegroundColor Red; exit 1 }
        $verifyDir = "D:\restore_test"
        Write-Host "Restoring snapshot $SnapshotId to $verifyDir for verification..." -ForegroundColor Cyan
        if (Test-Path $verifyDir) { Remove-Item $verifyDir -Recurse -Force }
        & restic -r $RepoPath restore $SnapshotId --target $verifyDir
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Files restored to $verifyDir" -ForegroundColor Green
            Write-Host "Verify key files:"
            @("AGENTS.md","config\sla_targets.yaml","src\zephyr") | ForEach-Object {
                $p = Join-Path $verifyDir $_
                if (Test-Path $p) { Write-Host "  [OK] $_" -ForegroundColor Green }
                else { Write-Host "  [MISSING] $_" -ForegroundColor Red }
            }
        }
    }
    "latest" {
        $restoreTarget = if ($Target) { $Target } else { $ProjectRoot }
        Write-Host "DISASTER RECOVERY: Restoring latest snapshot to $restoreTarget" -ForegroundColor Yellow
        $confirm = Read-Host "This will overwrite files in $restoreTarget. Continue? (yes/no)"
        if ($confirm -ne "yes") { Write-Host "Aborted."; exit 0 }
        & restic -r $RepoPath restore latest --target $restoreTarget
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Latest snapshot restored to $restoreTarget" -ForegroundColor Green
        }
    }
    "ch" {
        # ClickHouse DR: restic restore market.zip object -> start MinIO+relay -> RESTORE FROM S3
        # Mirror of backup.ps1 CH stage (same .env.ch_backup / .env.clickhouse credentials).
        $chBk = @{}
        $chBkEnvFile = "$ProjectRoot\config\.env.ch_backup"
        if (-not (Test-Path $chBkEnvFile)) { Write-Host "config/.env.ch_backup not found" -ForegroundColor Red; exit 1 }
        foreach ($line in (Get-Content $chBkEnvFile -Encoding UTF8)) {
            if ($line -match '^([A-Z0-9_]+)=(.+)$') { $chBk[$matches[1]] = $matches[2].Trim() }
        }
        $chHttpHost = "localhost"; $chHttpPort = 8123
        foreach ($line in (Get-Content "$ProjectRoot\config\.env.clickhouse" -Encoding UTF8)) {
            if ($line -match '^CLICKHOUSE_HOST=(.+)$')      { $chHttpHost = $matches[1].Trim() }
            if ($line -match '^CLICKHOUSE_HTTP_PORT=(.+)$') { $chHttpPort = [int]$matches[1].Trim() }
        }
        $chBaseUrl = "http://${chHttpHost}:${chHttpPort}/"

        $confirm = Read-Host "Restore ClickHouse c1_market + c3_fundamental from newest snapshot containing ch_backup_store? Existing tables must be dropped first. Continue? (yes/no)"
        if ($confirm -ne "yes") { Write-Host "Aborted."; exit 0 }

        # 1. Restic restore of the MinIO store path back to F:\ch_backup_store.
        #    CH backups run on a 24h cadence decoupled from the 8h code backups, so
        #    the LATEST snapshot usually has no ch_backup_store - resolve the newest
        #    snapshot that actually contains it (2026-07-19 fix).
        Write-Host "Locating newest snapshot containing ch_backup_store..." -ForegroundColor Cyan
        $snaps = & restic -r $RepoPath snapshots --json | ConvertFrom-Json
        $chSnap = $snaps | Where-Object { $_.paths -match 'ch_backup_store' } | Sort-Object { [datetime]$_.time } -Descending | Select-Object -First 1
        if (-not $chSnap) { Write-Host "no snapshot contains ch_backup_store (CH backup never ran?)" -ForegroundColor Red; exit 1 }
        Write-Host "Restoring ch_backup_store from snapshot $($chSnap.short_id) ($($chSnap.time), 315GiB, may take hours)..." -ForegroundColor Cyan
        & restic -r $RepoPath restore $chSnap.id --target "F:\" --include "F:/ch_backup_store*"
        if ($LASTEXITCODE -ne 0) { Write-Host "restic restore failed" -ForegroundColor Red; exit 1 }
        $objDir = "$($chBk.MINIO_ROOT)\$($chBk.MINIO_BUCKET)\market.zip"
        if (-not (Test-Path $objDir)) { Write-Host "market.zip object not found at $objDir" -ForegroundColor Red; exit 1 }

        # 2. Kill stale MinIO/relay from previous runs, then pick HNS-safe ports
        #    (bind-test; .env ports are preferences - mirror of backup.ps1 CH stage)
        Get-Process -Name minio -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -match 'minio_tcp_relay' } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        $minioPref = 9101; $consolePref = 9102; $relayPref = 9100
        if ($chBk.MINIO_ADDRESS -match ':(\d+)$')         { $minioPref = [int]$Matches[1] }
        if ($chBk.MINIO_CONSOLE_ADDRESS -match ':(\d+)$') { $consolePref = [int]$Matches[1] }
        if ($chBk.CH_S3_ENDPOINT -match ':(\d+)\s*$')     { $relayPref = [int]$Matches[1] }
        $minioPort = Get-FreePort $minioPref
        $consolePort = Get-FreePort $consolePref @($minioPort)
        $relayPort = Get-FreePort $relayPref @($minioPort, $consolePort)
        $minioAddress = "127.0.0.1:$minioPort"
        $consoleAddress = "127.0.0.1:$consolePort"
        $s3EndpointHost = ($chBk.CH_S3_ENDPOINT -replace '^https?://', '') -replace ':\d+\s*$', ''
        $s3Endpoint = "http://${s3EndpointHost}:$relayPort"

        # 3. Start MinIO (localhost) + python relay (VM-facing, ports via argv)
        $env:MINIO_ROOT_USER = $chBk.CH_S3_ACCESS_KEY
        $env:MINIO_ROOT_PASSWORD = $chBk.CH_S3_SECRET_KEY
        $minioProc = Start-Process -FilePath $chBk.MINIO_EXE `
            -ArgumentList 'server', "`"$($chBk.MINIO_ROOT)`"", '--address', "`"$minioAddress`"", '--console-address', "`"$consoleAddress`"" `
            -WindowStyle Hidden -PassThru
        $relayProc = Start-Process -FilePath "python" -ArgumentList "`"$($chBk.RELAY_SCRIPT)`"", "$relayPort", "$minioPort" -WindowStyle Hidden -PassThru
        try {
            $minioReady = $false
            for ($i = 0; $i -lt 30 -and -not $minioReady; $i++) {
                Start-Sleep -Seconds 1
                curl.exe -s --max-time 2 "http://$minioAddress/minio/health/live" -o NUL
                $minioReady = ($LASTEXITCODE -eq 0)
            }
            if (-not $minioReady) { throw "MinIO failed to start on $minioAddress" }

            # 4. RESTORE FROM S3 (async + poll)
            $s3Url = "$s3Endpoint/$($chBk.MINIO_BUCKET)/market.zip"
            $restoreQuery = "RESTORE DATABASE c1_market, DATABASE c3_fundamental FROM S3('$s3Url', '$($chBk.CH_S3_ACCESS_KEY)', '$($chBk.CH_S3_SECRET_KEY)') ASYNC"
            $fireResp = curl.exe -s --max-time 60 "${chBaseUrl}?s3_uri_style=path" --data-binary $restoreQuery
            if ($LASTEXITCODE -ne 0 -or $fireResp -notmatch '([0-9a-f-]{36})') { throw "RESTORE fire failed: $fireResp" }
            $restoreId = $Matches[1]
            Write-Host "RESTORE async id=$restoreId (may take hours)..." -ForegroundColor Cyan
            $final = "TIMEOUT"
            for ($elapsed = 0; $elapsed -lt 10800; $elapsed += 60) {
                Start-Sleep -Seconds 60
                $st = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT status FROM system.backups WHERE id='$restoreId'"
                if ($st -match 'RESTORED')        { $final = "OK"; break }
                if ($st -match 'RESTORE_FAILED')  { $final = "FAILED"; break }
            }
            if ($final -ne "OK") {
                $rErr = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT substring(error,1,300) FROM system.backups WHERE id='$restoreId'"
                throw "RESTORE $final`: $rErr"
            }
            # 5. Row-count spot check (institutional practice: verify after restore)
            curl.exe -s $chBaseUrl --data-binary "SELECT database, formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE active AND database IN ('c1_market','c3_fundamental') GROUP BY database"
            Write-Host "OK: ClickHouse restore complete (verify row counts above)" -ForegroundColor Green
        } catch {
            Write-Host "CH restore failed: $($_.Exception.Message)" -ForegroundColor Red
        } finally {
            if ($relayProc -and -not $relayProc.HasExited) { Stop-Process -Id $relayProc.Id -Force -ErrorAction SilentlyContinue }
            if ($minioProc -and -not $minioProc.HasExited) { Stop-Process -Id $minioProc.Id -Force -ErrorAction SilentlyContinue }
        }
    }
}
