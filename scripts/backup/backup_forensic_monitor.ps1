# [BLUEPRINT] MOD-INF-043 | backup_forensic_monitor.ps1
# Forensic life-sign monitor for backup run instances (st-backfix-20261010, T4+T5).
#
# WHY: .runtime/tmp/fwin_backup_monitor.ps1 (5216 case, 2026-10-10) had a broken
# death branch: its event dump wrote NOTHING on target death - no EVT lines and no
# EVT_DUMP_FAIL - because (a) Get-WinEvent finding zero events is silent, (b) a
# null $e.Message would crash the .Substring chain mid-dump, and (c) it had no
# access to the real evidence channel (the process-start trap log; OS event logs
# are empty for userland TerminateProcess kills). This rewrite follows the
# VERIFIED form of .runtime/tmp/procstart_trap_20261010.ps1:
#   1. TARGET_DEATH marker first, then the dump (death detection is itself evidence);
#   2. null-safe per-event lines, one bad event never aborts the burst;
#   3. explicit "none within window" lines - absence is evidence (userland kill);
#   4. killer-candidate extraction: START lines from the standing trap log within
#      [death-5min, death+2min] (the killer must START before it kills; work order T5).
#
# Modes:
#   -WatchPid N        : watch one PID (default 15s sampling per handoff note:
#                        60s windows missed short robocopy children), full death
#                        forensics on its disappearance, then exit.
#   -Patrol            : one-shot. Tracks the current .runtime/backup.lock holder
#                        in a state file; on "tracked holder died" extracts killer
#                        candidates from the standing trap log into a case file;
#                        on "new holder" re-arms tracking. Exit either way.
#
# ASCII-only (PS5.1 non-BOM-safe). Observational only: writes nothing outside
# [TTL] task_bound
# .runtime/tmp/ and logs/. Never signals, never kills, never touches backup locks.
param(
  [int]$WatchPid = 0,
  [switch]$Patrol,
  [int]$SampleSeconds = 15,
  [string]$LogPath = "",
  [string]$TrapLog = "D:\ZephyrAlpha\.runtime\tmp\procstart_trap_standing.log",
  [string]$LockFile = "D:\ZephyrAlpha\.runtime\backup.lock",
  [string]$PatrolStatePath = "D:\ZephyrAlpha\.runtime\tmp\backfix_patrol_state.json",
  [string]$CaseDir = "D:\ZephyrAlpha\.runtime\tmp",
  [string]$Session = "st-backfix-20261010"
)
$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"

function LogLine([string]$s, [string]$Path) {
  $line = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " | " + $s
  Add-Content -Path $Path -Value $line -Encoding UTF8
}

# ---- null-safe event dump (T4 fix core) ----
# Returns the number of events actually written. A zero return is RECORDED as an
# explicit "none" line: an empty OS event window around a silent death is the
# side-signal of a userland kill, and the old script left that fact unlogged.
function Dump-EventWindow([string]$LogName, [int]$Minutes, [string]$Path, [object]$Anchor = $null) {
  $count = 0
  # Window anchor (backfix T4, 2026-10-11): the dump used to key off the wall clock, so
  # a patrol reading 30 min after a death scanned [now-15min, now] and could leave the
  # true death minute OUTSIDE the window -- observed on case #15, where the EVT rows
  # covered 12:20:07-12:24:46 while the real exit line was 12:19:17. With an anchor the
  # window is [death-Min, death+2min]: the death minute can no longer fall out of the
  # readout, and post-mortem noise stays visible. Evidence widening only - no event is
  # dropped and no judgment or threshold moves. No anchor -> old behaviour unchanged.
  $fh = @{LogName = $LogName }
  if ($null -eq $Anchor) {
    $fh.StartTime = (Get-Date).AddMinutes(-$Minutes)
    $winDesc = "anchored=now"
  } else {
    $fh.StartTime = $Anchor.AddMinutes(-$Minutes)
    $fh.EndTime = $Anchor.AddMinutes(2)
    $winDesc = "anchored=death[" + $fh.StartTime.ToString("HH:mm:ss") + ".." + $fh.EndTime.ToString("HH:mm:ss") + "]"
  }
  try {
    $ev = Get-WinEvent -FilterHashtable $fh -MaxEvents 40 -ErrorAction SilentlyContinue
    foreach ($e in @($ev)) {
      if ($null -eq $e) { continue }
      try {
        $msg = ""
        if ($null -ne $e.Message) {
          $msg = ($e.Message -replace "\r\n", " ")
          if ($msg.Length -gt 100) { $msg = $msg.Substring(0, 100) }
        }
        LogLine ("EVT_" + $LogName + " " + $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss") + " id=" + $e.Id + " " + $e.ProviderName + " :: " + $msg) $Path
        $count++
      } catch { LogLine ("EVT_ITEM_ERR " + $_.Exception.Message) $Path }
    }
  } catch { LogLine ("EVT_QUERY_FAIL " + $LogName + " " + $_.Exception.Message) $Path }
  if ($count -eq 0) { LogLine ("EVT_" + $LogName + " none within " + $Minutes + "min window " + $winDesc + " (empty OS log = userland kill side-signal)") $Path }
  return $count
}

# ---- killer-candidate extraction from the standing trap log ----
# Standing trap line shapes (procstart_trap form):
#   "2026-10-10 11:29:07 | START pid=123 name=foo.exe :: C:\...\foo.exe -arg"
#   "2026-10-10 11:29:07 | EXIT  pid=123 name=foo.exe"
# Candidates: START lines in [death-5min, death+2min], excluding the victim itself.
# Returns list of "timestamp|pid|name|cmdline" strings; also writes a case file.
function Get-KillerCandidates([datetime]$DeathTime, [int]$VictimPid, [string]$Path) {
  $cands = @()
  try {
    if (-not (Test-Path $TrapLog)) { LogLine "KILLER_SCAN trap log missing: $TrapLog" $Path; return $cands }
    $lo = $DeathTime.AddMinutes(-5); $hi = $DeathTime.AddMinutes(2)
    foreach ($raw in [System.IO.File]::ReadLines($TrapLog)) {
      if ($raw -notmatch '^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| START pid=(\d+) name=(\S+) :: (.*)$') { continue }
      try { $ts = [datetime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm:ss", $null) } catch { continue }
      if ($ts -lt $lo -or $ts -gt $hi) { continue }
      if ([int]$matches[2] -eq $VictimPid) { continue }
      $cands += ("{0}|pid={1}|{2}|{3}" -f $matches[1], $matches[2], $matches[3], $matches[4])
    }
  } catch { LogLine ("KILLER_SCAN_ERR " + $_.Exception.Message) $Path }
  # case file: one per death, ASCII, includes verdict placeholders for T5 adjudication
  try {
    $casePath = Join-Path $CaseDir ("backfix_killer_case_{0}.md" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
    $lines = @()
    $lines += "# killer candidate case (auto-extracted by backup_forensic_monitor.ps1)"
    $lines += "- session: $Session"
    $lines += "- victim_pid: $VictimPid"
    $lines += "- death_time: " + $DeathTime.ToString("yyyy-MM-dd HH:mm:ss")
    $lines += "- trap_log: $TrapLog"
    $lines += "- window: [death-5min, death+2min] per work order T5"
    $lines += "- rule: the killer must START before it kills; human/AI adjudication names ONE"
    if ($cands.Count -eq 0) { $lines += "- candidates: NONE (trap log gap or killer pre-dated window - widen manually)" }
    else { $lines += "- candidates:"; foreach ($c in $cands) { $lines += ("  - " + $c) } }
    [System.IO.File]::WriteAllLines($casePath, $lines, (New-Object System.Text.UTF8Encoding($false)))
    LogLine "KILLER_CASE written: $casePath (candidates=$($cands.Count))" $Path
  } catch { LogLine ("KILLER_CASE_ERR " + $_.Exception.Message) $Path }
  return $cands
}

# ---- death forensics burst (shared by both modes) ----
function Invoke-DeathForensics([int]$VictimPid, [datetime]$DeathTime, [string]$Path) {
  LogLine ("TARGET_DEATH pid=" + $VictimPid + " detected_at=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) $Path
  $null = Dump-EventWindow -LogName "System" -Minutes 15 -Path $Path -Anchor $DeathTime
  $null = Dump-EventWindow -LogName "Application" -Minutes 15 -Path $Path -Anchor $DeathTime
  $c = Get-KillerCandidates -DeathTime $DeathTime -VictimPid $VictimPid -Path $Path
  LogLine ("FORENSICS_DONE candidates=" + $c.Count) $Path
}

# ==================== Mode: Patrol (one-shot, 30min cadence driver) ====================
if ($Patrol) {
  $pLog = if ($LogPath -ne "") { $LogPath } else { Join-Path $CaseDir "backfix_patrol.log" }
  $prev = $null
  if (Test-Path $PatrolStatePath) {
    try { $prev = Get-Content $PatrolStatePath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $prev = $null }
  }
  # current holder
  $holderPid = 0; $holderStart = ""
  try {
    $lockRaw = Get-Content $LockFile -Raw -ErrorAction Stop
    if ($lockRaw -match 'PID:(\d+)') { $holderPid = [int]$matches[1] }
    if ($lockRaw -match 'START:(\S+)') { $holderStart = $matches[1] }
  } catch { $holderPid = 0 }
  $nowIso = (Get-Date).ToString("o")
  if ($holderPid -gt 0) {
    $alive = $null -ne (Get-Process -Id $holderPid -ErrorAction SilentlyContinue)
    LogLine ("PATROL holder=" + $holderPid + " alive=" + $alive + " start=" + $holderStart) $pLog
    if ($prev -and $prev.tracked_pid -gt 0 -and $prev.tracked_pid -ne $holderPid -and -not $prev.death_reported) {
      # tracked instance is gone from the lock: confirm its real death time from trap EXIT line
      $vPid = [int]$prev.tracked_pid
      $deathTime = $null
      try {
        foreach ($raw in [System.IO.File]::ReadLines($TrapLog)) {
          if ($raw -match ('^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| EXIT  pid=' + $vPid + ' ')) {
            try { $deathTime = [datetime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm:ss", $null) } catch { }
          }
        }
      } catch { }
      if (-not $deathTime) { $deathTime = Get-Date }
      LogLine ("PATROL death of tracked pid=" + $vPid + " at " + $deathTime.ToString("yyyy-MM-dd HH:mm:ss") + " - forensics follow") $pLog
      Invoke-DeathForensics -VictimPid $vPid -DeathTime $deathTime -Path $pLog
      @{ tracked_pid = $holderPid; tracked_start = $holderStart; first_seen = $nowIso; death_reported = $false; note = "re-armed on new holder after death" } |
        ConvertTo-Json | Set-Content -Path $PatrolStatePath -Encoding UTF8
    } elseif (-not $prev -or $prev.tracked_pid -ne $holderPid) {
      @{ tracked_pid = $holderPid; tracked_start = $holderStart; first_seen = $nowIso; death_reported = $false; note = "armed" } |
        ConvertTo-Json | Set-Content -Path $PatrolStatePath -Encoding UTF8
      LogLine ("PATROL armed on pid=" + $holderPid) $pLog
    } else {
      LogLine ("PATROL no change (tracked=" + $holderPid + ")") $pLog
    }
  } else {
    LogLine "PATROL lock free or unreadable" $pLog
    if ($prev -and $prev.tracked_pid -gt 0 -and -not $prev.death_reported) {
      $vPid = [int]$prev.tracked_pid
      LogLine ("PATROL lock vanished while tracking pid=" + $vPid + " - could be clean finish (Release-Lock in finally) or death; checking trap EXIT") $pLog
      $deathTime = $null
      try {
        foreach ($raw in [System.IO.File]::ReadLines($TrapLog)) {
          if ($raw -match ('^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| EXIT  pid=' + $vPid + ' ')) {
            try { $deathTime = [datetime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm:ss", $null) } catch { }
          }
        }
      } catch { }
      if ($deathTime) {
        LogLine ("PATROL tracked pid=" + $vPid + " has trap EXIT at " + $deathTime.ToString("yyyy-MM-dd HH:mm:ss")) $pLog
        Invoke-DeathForensics -VictimPid $vPid -DeathTime $deathTime -Path $pLog
      } else {
        LogLine ("PATROL no trap EXIT for pid=" + $vPid + " - treat as clean finish; forensics skipped") $pLog
      }
      @{ tracked_pid = 0; tracked_start = ""; first_seen = $nowIso; death_reported = $true; note = "lock free after track" } |
        ConvertTo-Json | Set-Content -Path $PatrolStatePath -Encoding UTF8
    }
  }
  exit 0
}

# ==================== Mode: WatchPid (life-sign + death forensics) ====================
if ($WatchPid -le 0) { Write-Host "usage: -WatchPid <pid> or -Patrol"; exit 1 }
$wLog = if ($LogPath -ne "") { $LogPath } else { Join-Path $CaseDir ("backfix_monitor_{0}.log" -f $WatchPid) }
LogLine ("MONITOR_START target=" + $WatchPid + " sample=" + $SampleSeconds + "s session=" + $Session) $wLog
$lastCpu = 0.0
$cycle = 0
while ($true) {
  $cycle++
  $p = Get-Process -Id $WatchPid -ErrorAction SilentlyContinue
  if (-not $p) {
    Invoke-DeathForensics -VictimPid $WatchPid -DeathTime (Get-Date) -Path $wLog
    LogLine "MONITOR_EXIT_ON_TARGET_DEATH" $wLog
    exit 0
  }
  $cpuD = [math]::Round($p.CPU - $lastCpu, 1)
  $lastCpu = $p.CPU
  # children snapshot (15s window catches short robocopy/python calls - handoff note)
  $kids = ""
  try {
    $cs = Get-CimInstance Win32_Process -Filter ("ParentProcessId=" + $WatchPid) -ErrorAction SilentlyContinue
    foreach ($c in $cs) {
      $cl = ""; if ($c.CommandLine) { $cl = $c.CommandLine }
      if ($cl.Length -gt 90) { $cl = $cl.Substring(0, 90) }
      $kids = $kids + " [" + $c.Name + "|" + $cl + "]"
    }
  } catch { $kids = " KIDS_ERR" }
  $stM = "-"
  try { $stM = (Get-Item (Join-Path $ProjectRoot "data\databases\backup_state.json") -ErrorAction Stop).LastWriteTime.ToString("HH:mm:ss") } catch { }
  $lockTxt = "LOCK_FREE"
  try { $lockTxt = (Get-Content $LockFile -Raw -ErrorAction Stop).Trim() } catch { }
  $gM = "-"
  try { $gM = (Get-Item "G:\ch_backup_disk2.vhdx" -ErrorAction SilentlyContinue).LastWriteTime.ToString("HH:mm:ss") } catch { }
  LogLine ("cycle=" + $cycle + " alive=True cpu_total=" + [math]::Round($p.CPU, 1) + " cpu_d=" + $cpuD + " state_mtime=" + $stM + " lock=[" + $lockTxt + "] G_mtime=" + $gM + " kids=" + $kids) $wLog
  Start-Sleep -Seconds $SampleSeconds
}
