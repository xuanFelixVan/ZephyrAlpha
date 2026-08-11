# Comprehensive drift fixer v3 - handles §0 catalog, §7.3 occupancy, §3 status/product rows
# Replaces stale version references with actual frontmatter versions
$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$indexPath = Join-Path $dir "00_index_trading_decision.md"
$lines = Get-Content $indexPath -Encoding UTF8

# Build actual version map from frontmatter
$files = Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' }
$actualMap = @{}
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?') {
        $actualMap[$f.BaseName] = $matches[1]
    }
}

# Find revision history start (skip everything after)
$revStart = $lines.Count
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\|\s*日期\s*\|') { $revStart = $i; break }
}

$fixLog = @()

for ($i = 0; $i -lt $revStart; $i++) {
    $line = $lines[$i]
    $origLine = $line

    foreach ($name in $actualMap.Keys) {
        $actual = $actualMap[$name]
        if ($line -notmatch [regex]::Escape($name)) { continue }

        $nameEsc = [regex]::Escape($name)

        # Pattern A: §0 catalog "| [name.md](name.md) | desc with vOLD | status |"
        if ($line -match "^\|\s*\[${nameEsc}\.md\]") {
            # Replace all vOLD in the description cell (2nd content column)
            $cells = $line -split '\|'
            if ($cells.Count -ge 4) {
                for ($c = 2; $c -lt $cells.Count - 1; $c++) {
                    $oldCell = $cells[$c]
                    # Replace version numbers, but skip "v0.x.x" if actual is "1.x.x" (avoid cross-major confusion)
                    $newCell = [regex]::Replace($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)', {
                        param($m)
                        $found = $m.Groups[1].Value
                        if ($found -ne $actual) { "v$actual" } else { $m.Value }
                    })
                    if ($newCell -ne $oldCell) {
                        $oldVer = [regex]::Match($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)').Groups[1].Value
                        if ($oldVer -and $oldVer -ne $actual) {
                            $cells[$c] = $newCell
                            $fixLog += "L$($i+1) §0: $name v$oldVer -> v$actual"
                        }
                    }
                }
                $line = $cells -join '|'
            }
            continue
        }

        # Pattern B: §7.3 occupancy "| name | topic | owner | status with vOLD |"
        if ($line -match "^\|\s*${nameEsc}\s*\|") {
            $cells = $line -split '\|'
            if ($cells.Count -ge 5) {
                # Status is typically the last content cell
                $lastIdx = $cells.Count - 2
                $oldCell = $cells[$lastIdx]
                $newCell = [regex]::Replace($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)', {
                    param($m)
                    $found = $m.Groups[1].Value
                    if ($found -ne $actual) { "v$actual" } else { $m.Value }
                })
                if ($newCell -ne $oldCell) {
                    $oldVer = [regex]::Match($oldCell, 'v([0-9]+\.[0-9]+\.[0-9]+)').Groups[1].Value
                    if ($oldVer -and $oldVer -ne $actual) {
                        $cells[$lastIdx] = $newCell
                        $fixLog += "L$($i+1) §7.3: $name v$oldVer -> v$actual"
                        $line = $cells -join '|'
                    }
                }
            }
            continue
        }

        # Pattern C: §3 status "| 状态 | ✅ 已定稿 vOLD（[name]" or "| 状态 | ✅ ... vOLD（[name]"
        if ($line -match "^\|\s*状态\s*\|" -and $line -match "\[${nameEsc}\]") {
            # Replace the FIRST version number after "已定稿 " or after "active "
            $newLine = [regex]::Replace($line, '(\| 状态 \| ✅ 已定稿 )v([0-9]+\.[0-9]+\.[0-9]+)', {
                param($m)
                $found = $m.Groups[2].Value
                if ($found -ne $actual) { "$($m.Groups[1].Value)v$actual" } else { $m.Value }
            }, 1)
            if ($newLine -ne $line) {
                $oldVer = [regex]::Match($line, '(\| 状态 \| ✅ 已定稿 )v([0-9]+\.[0-9]+\.[0-9]+)').Groups[2].Value
                if ($oldVer -and $oldVer -ne $actual) {
                    $fixLog += "L$($i+1) §3status: $name v$oldVer -> v$actual"
                    $line = $newLine
                }
            }
            continue
        }
    }

    if ($line -ne $origLine) {
        $lines[$i] = $line
    }
}

# Write back
$lines | Set-Content $indexPath -Encoding UTF8

Write-Output "=== Fixed $($fixLog.Count) drifts ==="
$fixLog | ForEach-Object { Write-Output $_ }
