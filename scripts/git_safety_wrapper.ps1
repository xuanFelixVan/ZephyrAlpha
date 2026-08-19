# =============================================================================
# File: scripts/git_safety_wrapper.ps1
# Title: ZephyrAlpha Git/PowerShell safety wrapper function set (65 memo Phase 1, layers L1+L2+L4+L5+L6)
# Owner: ZephyrAlpha-Owner
# Created: 2026-08-14
# Author: AI-GIT-001
# Status: production
# True-Source: this file is the single source of wrapper functions; $PROFILE only dot-sources it (install_git_safety_wrapper.ps1 handles install/uninstall)
# Design-Spec: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/65_git_safety_governance.md sections 7.1/7.10/7.14/7.17.2/7.23/7.32
# Related-Issues: #ARCH-GIT-CLEAN-GUARD-FIX; #ARCH-WORKTREE-WIPE-GOV-001
# Creation-Token: auto-git-safety-wrapper-phase1-20260814
# Scope-Decisions: (1) 7.1.4 ProxyCommand not adopted - hand-written param block covers all AI-workflow params (-Credential etc. unused in this repo); (2) 7.17.2 .git guard mounted on 4 delete functions only (Remove-Item/rd/del/rm); write-class (Set-Content/Out-File/Add-Content/New-Item) deferred to open questions
# Encoding: ASCII-only by gate INJ-007 (PowerShell 5.1 ANSI decoding) - keep all messages English
# =============================================================================
# ALGO_FLOW:
#   1. Session ID injection (7.32): generate UUID when ZEPHYR_SESSION_ID absent - identity for audit/task board
#   2. Real git.exe detection (7.1.1): env ZEPHYR_REAL_GIT_PATH > registry > common paths > fallback 'git.exe'
#   3. _ZephyrAuditLog (7.10/7.27): per-session JSONL (no Mutex, append-only post-hoc forensics)
#   4. git() (7.1.1+7.23): dangerous subcommand pattern match -> BLOCKED + escape hint; 7.14 fail-open (catch -> passthrough + FAIL_OPEN audit)
#      + 66 memo ruling 7: read-tree/update-index/write-tree/hash-object blocked unless ZEPHYR_SERIALIZER_MODE=1
#   5. Remove-Item/rd/del/rm (7.1.2): CRITICAL_BLOCKS absolute ban + recursive/batch pattern block + TEMP whitelist
#      + 7.17.2 .git dir write hard-block (all delete functions) + 7.14 fail-open
#   6. format/vssadmin delete/diskpart (7.1.2 CRITICAL): fail-closed hard block, no escape, no try/catch
# =============================================================================

#requires -Version 5.1

# ---------- 7.32 Session ID injection (L6) + 7.33 AI-channel attribution (tracker #58) ----------
if (-not $env:ZEPHYR_SESSION_ID) {
    # 7.33: Trae AI RunCommand spawns one short-lived powershell per command, all sharing
    # parent agent-tool-host.exe (-NoProfile hardcoded, profile never loads; wrapper reaches
    # this channel via profile-snapshot injection). A per-process UUID would fragment audit
    # into one file per command - anchor session identity to the stable toolhost parent.
    $global:_zephyrChannel = 'interactive'
    try {
        $_ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID" -Property ParentProcessId -ErrorAction Stop).ParentProcessId
        $_pp = Get-Process -Id $_ppid -ErrorAction Stop
        if ($_pp.ProcessName -eq 'agent-tool-host') {
            $global:_zephyrChannel = 'ai-runcommand'
            $env:ZEPHYR_SESSION_ID = 'ai-{0}-{1}' -f $_pp.Id, $_pp.StartTime.ToString('yyyyMMddHHmmss')
        }
    } catch { }  # attribution failure falls back to per-process UUID, never blocks
    if (-not $env:ZEPHYR_SESSION_ID) {
        $env:ZEPHYR_SESSION_ID = [guid]::NewGuid().ToString()
    }
    $env:ZEPHYR_SESSION_START = (Get-Date).ToString('o')
}

# ---------- 7.1.1 real git.exe detection (avoid recursion via function name git) ----------
if (-not $script:_realGit) {
    $script:_realGit = $env:ZEPHYR_REAL_GIT_PATH
    if (-not $script:_realGit) {
        $script:_realGit = (Get-ItemProperty 'HKLM:\SOFTWARE\GitForWindows' -ErrorAction SilentlyContinue).InstallPath
        if ($script:_realGit) { $script:_realGit = Join-Path $script:_realGit 'cmd\git.exe' }
    }
    if (-not $script:_realGit -or -not (Test-Path $script:_realGit)) {
        foreach ($_p in @('C:\Program Files\Git\cmd\git.exe', 'C:\Program Files (x86)\Git\cmd\git.exe', "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe")) {
            if (Test-Path $_p) { $script:_realGit = $_p; break }
        }
    }
    if (-not $script:_realGit) { $script:_realGit = 'git.exe' }  # final fallback
}

# ---------- 7.10+7.27 audit log (L5, v2.1.0 simplified: per-session file, no Mutex) ----------
function _ZephyrAuditLog {
    param([string]$Command, [string]$Action, [string]$Reason, [string]$EscapeHint = '')
    try {
        $_logDir = Join-Path $env:USERPROFILE '.zephyr_audit'
        if (-not (Test-Path $_logDir)) { New-Item -ItemType Directory -Path $_logDir -Force | Out-Null }
        $_session = if ($env:ZEPHYR_SESSION_ID) { $env:ZEPHYR_SESSION_ID } else { 'nosession' }
        $_logFile = Join-Path $_logDir ("audit_{0:yyyyMMdd}_{1}.jsonl" -f (Get-Date), $_session)
        $_entry = @{
            timestamp = (Get-Date).ToString('o')
            action    = $Action
            command   = $Command
            reason    = $Reason
            session   = $env:ZEPHYR_SESSION_ID
            pid       = $PID
        }
        if ($global:_zephyrChannel) { $_entry.channel = $global:_zephyrChannel }
        if ($EscapeHint) { $_entry.escape_hint = $EscapeHint }
        # UTF-8 without BOM (PS 5.1 Add-Content -Encoding UTF8 emits BOM, breaking JSONL line-1 parsing)
        $_line = $_entry | ConvertTo-Json -Compress
        [System.IO.File]::AppendAllText($_logFile, $_line + "`n", [System.Text.UTF8Encoding]::new($false))
    } catch { }  # audit failure stays silent - never blocks the main command
}

# ---------- 7.17.2 .git dir write hard-block (L4, mounted on delete functions) ----------
function _ZephyrCheckGitDirProtection {
    param([string[]]$Paths)
    foreach ($p in $Paths) {
        if ($p) {
            $_resolvedPath = Resolve-Path $p -ErrorAction SilentlyContinue
            $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
            if ($resolved -and ($resolved -match '[\\/]\.git[\\/]' -or $resolved -match '[\\/]\.git$')) {
                Write-Host "[SAFE] HARDBLOCKED: write into .git dir - $resolved" -ForegroundColor Red
                _ZephyrAuditLog -Command "write to $resolved" -Action 'HARDBLOCKED' -Reason '.git dir write permanently blocked'
                return $false
            }
        }
    }
    return $true
}

# ---------- 7.1.1 Part A + 7.23: git interception (L1, 7.14 fail-open) ----------
function git {
    try {
        $cmd = if ($args.Count -gt 0) { $args[0] } else { '' }
        $fullArgs = $args -join ' '
        $blocked = $false
        $reason = ''
        if ($cmd -eq 'clean' -and ($fullArgs -notmatch '(?:^|\s)-(?:n|-dry-run)(?:\s|$)')) {
            $blocked = $true; $reason = 'git clean deletes untracked files (physical delete, no recycle bin)'
        } elseif ($cmd -eq 'reset' -and ($fullArgs -match '--hard|--merge')) {
            $blocked = $true; $reason = 'git reset --hard/--merge discards uncommitted changes'
        } elseif ($cmd -eq 'restore' -and ($fullArgs -match '--worktree' -or ($fullArgs -notmatch '--staged'))) {
            $blocked = $true; $reason = 'git restore discards file changes'
        } elseif ($cmd -eq 'checkout') {
            # PS 5.1 swallows bare '--' before it reaches $args (verified 2026-08-14), so
            # "checkout -- <path>" and "checkout <branch>" look identical at this layer.
            # Resolution: rev-parse --verify the first non-switch arg. ref -> branch switch (allow);
            # existing path -> discard-changes (block); missing -> let real git error out (allow).
            $_nonSwitch = @($args | Select-Object -Skip 1 | Where-Object { $_ -notmatch '^-' })
            if ($_nonSwitch.Count -gt 0) {
                $_first = $_nonSwitch[0]
                if ($_first -eq '.') {
                    $blocked = $true; $reason = 'git checkout . discards all uncommitted changes'
                } else {
                    $_isRef = $false
                    try {
                        & $script:_realGit rev-parse --verify --quiet $_first 2>$null | Out-Null
                        $_isRef = ($LASTEXITCODE -eq 0)
                    } catch { $_isRef = $false }
                    if ($_isRef) {
                        # checkout <ref> [<path>...] form (bare -- swallowed): existing path after ref -> discard
                        foreach ($_p in @($_nonSwitch | Select-Object -Skip 1)) {
                            if (Test-Path $_p) { $blocked = $true; $reason = "git checkout $_first -- $_p discards file changes"; break }
                        }
                    } elseif (Test-Path $_first) {
                        $blocked = $true; $reason = 'git checkout -- <path> discards file changes'
                    }
                }
            }
        } elseif ($cmd -eq 'stash' -and ($args.Count -lt 2 -or $args[1] -notin @('list', 'show'))) {
            $blocked = $true; $reason = 'git stash moves/deletes uncommitted changes'
        } elseif ($cmd -eq 'rm' -and ($fullArgs -notmatch '--cached')) {
            $blocked = $true; $reason = 'git rm deletes files from worktree'
        } elseif ($cmd -eq 'branch' -and ($fullArgs -cmatch '(?:^|\s)-D(?:\s|$)|--delete-force')) {
            # tracker #72: -match is case-insensitive, so safe 'git branch -d' was blocked as -D.
            # Fix: -cmatch (case-sensitive) + boundary-anchored -D (same idiom as -n/-f rules
            # above) - '-d' passes, branch names containing '-D' (e.g. my-D-branch) pass,
            # only a standalone force-delete -D is blocked.
            $blocked = $true; $reason = 'git branch -D force-deletes branch (may lose unmerged code)'
        } elseif ($cmd -eq 'push' -and ($fullArgs -match '(?:^|\s)-(?:f|-force)(?:\s|$)' -and $fullArgs -notmatch '--force-with-lease')) {
            $blocked = $true; $reason = 'git push --force overwrites remote history (may lose others code)'
        } elseif ($cmd -eq 'filter-branch' -or $cmd -eq 'filter-repo') {
            $blocked = $true; $reason = "git $cmd rewrites history - irreversible (7.23)"
        } elseif ($cmd -eq 'reflog' -and $args.Count -gt 1 -and $args[1] -eq 'expire') {
            $blocked = $true; $reason = 'git reflog expire erases forensic evidence (7.23)'
        } elseif ($cmd -eq 'gc' -and ($fullArgs -match '--prune=(now|all)')) {
            $blocked = $true; $reason = 'git gc --prune=now physically deletes unreachable objects (7.23)'
        } elseif ($cmd -in @('read-tree', 'update-index', 'write-tree', 'hash-object') -and $env:ZEPHYR_SERIALIZER_MODE -ne '1') {
            # 66 memo ruling 7 (incident 6 root cause): plumbing commands manipulate the shared
            # index/object db directly, bypassing every hook/gate - read-tree invisibly wiped the
            # shared staged area on 2026-08-12. Serializer whitelist: ZEPHYR_SERIALIZER_MODE=1.
            $blocked = $true; $reason = "git $cmd manipulates shared index/object db directly (66 memo incident 6). Serializer whitelist: `$env:ZEPHYR_SERIALIZER_MODE=1"
        }

        if ($blocked) {
            Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs - $reason" -ForegroundColor Red
            Write-Host "  escape hatch (after safety check): & '$script:_realGit' $fullArgs" -ForegroundColor Yellow
            _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $reason -EscapeHint "& '$script:_realGit' $fullArgs"
            $global:LASTEXITCODE = 1
            return
        }
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'ALLOWED' -Reason 'safe command'
        & $script:_realGit @args
    } catch {
        # 7.14 fail-open: wrapper error passes through to real git, never blocks work
        _ZephyrAuditLog -Command "git $($args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $script:_realGit @args
    }
}

# ---------- 7.1.2 Part B: PowerShell/CMD native destructive command interception (L2) ----------
# save builtin cmdlet reference first (avoid recursion after function override)
if (-not $script:_realRemoveItem) {
    $script:_realRemoveItem = (Get-Command Microsoft.PowerShell.Management\Remove-Item -ErrorAction SilentlyContinue)
}

# Remove builtin AllScope aliases so guard FUNCTIONS can take over.
# PS 5.1 facts (verified 2026-08-14): precedence is Alias > Function > Cmdlet; AllScope aliases
# (rm/del/rd/rmdir/erase) can neither be shadowed by functions nor retargeted via Set-Alias
# ("The AllScope option cannot be removed"). Only removal via the real Remove-Item works.
foreach ($_aliasName in @('rm', 'rd', 'rmdir', 'del', 'erase')) {
    if (Test-Path "Alias:\$_aliasName") {
        & $script:_realRemoveItem "Alias:\$_aliasName" -Force -ErrorAction SilentlyContinue
    }
}

# CRITICAL_BLOCKS: absolutely forbidden, no escape hatch (system-level destruction)
$script:_criticalBlocks = @(
    'format ', 'vssadmin delete', 'wbadmin delete', 'cipher /w', 'diskpart', 'reg delete', 'bcdedit',
    'netsh advfirewall', 'schtasks /delete', 'schtasks /create', 'schtasks /change', 'sc delete', 'sc stop',
    'powershell -enc', 'powershell -encodedcommand', 'powershell.exe -enc', '-encodedcommand'
)

function Remove-Item {
    [CmdletBinding()]
    param([Parameter(Mandatory=$false, Position=0)][string[]]$Path, [switch]$Recurse, [switch]$Force,
        [switch]$Confirm, [switch]$WhatIf, [string]$Filter, [string[]]$Include, [string[]]$Exclude, [string]$LiteralPath)
    try {
        $fullCmd = "Remove-Item $($args -join ' ')"
        foreach ($pattern in $script:_criticalBlocks) {
            if ($fullCmd -like "*$pattern*") {
                Write-Host "[SAFE] HARDBLOCKED: $pattern - system-level destruction (always blocked, no escape)" -ForegroundColor Red
                _ZephyrAuditLog -Command $fullCmd -Action 'HARDBLOCKED' -Reason "CRITICAL_BLOCKS: $pattern"
                return
            }
        }
        # 7.17.2 .git dir delete hard-block
        $_targets = @()
        if ($Path) { $_targets += $Path }
        if ($LiteralPath) { $_targets += $LiteralPath }
        if (-not (_ZephyrCheckGitDirProtection -Paths $_targets)) { return }

        if ($Recurse -and $Force) {
            $targetPath = if ($Path) { $Path[0] } elseif ($LiteralPath) { $LiteralPath } else { '' }
            $isTemp = $false
            if ($targetPath -and $env:TEMP) {
                $_resolvedPath = Resolve-Path $targetPath -ErrorAction SilentlyContinue  # PS 5.1 compatible
                $resolvedTarget = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
                if ($resolvedTarget -and $resolvedTarget.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $isTemp = $true
                }
            }
            if (-not $isTemp) {
                Write-Host "[SAFE] BLOCKED: Remove-Item -Recurse -Force - recursive force delete (physical, no recycle bin)" -ForegroundColor Red
                Write-Host "  escape hatch (after safety check): & `$script:_realRemoveItem -Recurse -Force <path>" -ForegroundColor Yellow
                _ZephyrAuditLog -Command $fullCmd -Action 'BLOCKED' -Reason 'Remove-Item -Recurse -Force recursive force delete' -EscapeHint '& $_realRemoveItem -Recurse -Force <path>'
                return
            }
        }
        _ZephyrAuditLog -Command $fullCmd -Action 'ALLOWED' -Reason 'safe Remove-Item call'
        & $script:_realRemoveItem @PSBoundParameters
    } catch {
        # 7.14 fail-open
        _ZephyrAuditLog -Command "Remove-Item $($args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $script:_realRemoveItem @PSBoundParameters
    }
}

# rd/rmdir/del/erase/rm function guards (aliases removed above, so functions now bind).
function rd {
    param([Parameter(Position=0)][string]$Path, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    try {
        # positional binding puts '/s' into $Path - must inspect the merged string
        $_all = @($Path) + @($Args)
        if (($_all -join ' ') -match '/s') {
            if (-not (_ZephyrCheckGitDirProtection -Paths @($Path))) { $global:LASTEXITCODE = 1; return }
            Write-Host "[SAFE] BLOCKED: rd /s - CMD recursive directory delete" -ForegroundColor Red
            _ZephyrAuditLog -Command "rd $($_all -join ' ')" -Action 'BLOCKED' -Reason 'rd /s CMD recursive delete'
            $global:LASTEXITCODE = 1
            return
        }
        & $script:_realRemoveItem -Path $Path @Args
    } catch {
        _ZephyrAuditLog -Command "rd $Path $($Args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $script:_realRemoveItem -Path $Path @Args
    }
}

function del {
    param([Parameter(Position=0)][string[]]$Path, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    try {
        # positional binding puts '/s' into $Path - must inspect the merged string
        $_all = @($Path) + @($Args)
        $argStr = $_all -join ' '
        if ($argStr -match '/s|/f') {
            if (-not (_ZephyrCheckGitDirProtection -Paths $Path)) { $global:LASTEXITCODE = 1; return }
            Write-Host "[SAFE] BLOCKED: del $argStr - CMD batch/force delete" -ForegroundColor Red
            _ZephyrAuditLog -Command "del $argStr" -Action 'BLOCKED' -Reason "del $argStr CMD batch/force delete"
            $global:LASTEXITCODE = 1
            return
        }
        & $script:_realRemoveItem -Path $Path @Args
    } catch {
        _ZephyrAuditLog -Command "del $Path $argStr" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $script:_realRemoveItem -Path $Path @Args
    }
}

# rm guard (if GnuWin32 coreutils rm is on PATH, passthrough when safe)
function rm {
    try {
        $argStr = $args -join ' '
        if ($argStr -match '(?:^|\s)-(?:rf|fr)(?:\s|$)') {
            if (-not (_ZephyrCheckGitDirProtection -Paths @($args))) { $global:LASTEXITCODE = 1; return }
            $isTemp = $false
            foreach ($a in $args) {
                if ($a -notmatch '^-' -and $a -and $env:TEMP) {
                    $_resolvedPath = Resolve-Path $a -ErrorAction SilentlyContinue  # PS 5.1 compatible
                    $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
                    if ($resolved -and $resolved.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) { $isTemp = $true; break }
                }
            }
            if (-not $isTemp) {
                Write-Host "[SAFE] BLOCKED: rm -rf - Unix recursive force delete" -ForegroundColor Red
                _ZephyrAuditLog -Command "rm $argStr" -Action 'BLOCKED' -Reason 'rm -rf recursive force delete'
                $global:LASTEXITCODE = 1
                return
            }
        }
        $_realRm = Get-Command rm.exe -ErrorAction SilentlyContinue
        if ($_realRm) { & $_realRm.Source @args } else { & $script:_realRemoveItem @args }
    } catch {
        _ZephyrAuditLog -Command "rm $($args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $script:_realRemoveItem @args
    }
}

# rmdir/erase fall back to rd/del guards (their builtin aliases were removed above)
Set-Alias -Name rmdir -Value rd -Force -ErrorAction SilentlyContinue
Set-Alias -Name erase -Value del -Force -ErrorAction SilentlyContinue

# ---------- CRITICAL command overrides - fail-closed hard block, no escape, no try/catch (7.14 ruling) ----------
function format {
    param([string]$Drive, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    Write-Host "[SAFE] HARDBLOCKED: format - disk formatting (system-level destruction, always blocked)" -ForegroundColor Red
    _ZephyrAuditLog -Command "format $Drive $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'format disk'
    $global:LASTEXITCODE = 1
}
function vssadmin {
    param([string]$SubCommand, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    if ($SubCommand -eq 'delete') {
        Write-Host "[SAFE] HARDBLOCKED: vssadmin delete - shadow copy deletion (backup destruction)" -ForegroundColor Red
        _ZephyrAuditLog -Command "vssadmin $SubCommand $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'vssadmin delete destroys backups'
        $global:LASTEXITCODE = 1
        return
    }
    $_realCmd = Get-Command vssadmin.exe -ErrorAction SilentlyContinue
    if ($_realCmd) { & $_realCmd.Source $SubCommand @Args }
}
function diskpart {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    Write-Host "[SAFE] HARDBLOCKED: diskpart - disk partition operation (system-level destruction)" -ForegroundColor Red
    _ZephyrAuditLog -Command "diskpart $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'diskpart partition operation'
    $global:LASTEXITCODE = 1
}
