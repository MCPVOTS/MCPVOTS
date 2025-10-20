# Continue cloning Base repositories
# This script clones repositories that haven't been cloned yet

param(
    [int]$DelaySeconds = 2
)

$baseDir = $PSScriptRoot
$repoListFile = Join-Path $baseDir "base_repos.txt"
$logFile = Join-Path $baseDir "clone_log.txt"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Host $Message
}

Write-Log "Continuing Base repositories clone process"

if (-not (Test-Path $repoListFile)) {
    Write-Log "Error: Repository list file not found: $repoListFile"
    exit 1
}

$repositories = Get-Content $repoListFile | Where-Object { $_ -and $_.Trim() -ne "" }

$clonedCount = 0
$skippedCount = 0

foreach ($repoName in $repositories) {
    $repoName = $repoName.Trim()
    if ([string]::IsNullOrEmpty($repoName)) { continue }

    $repoPath = Join-Path $baseDir $repoName

    if (Test-Path $repoPath) {
        Write-Log "Repository already exists: $repoName"
        $skippedCount++
        continue
    }

    Write-Log "Cloning repository: $repoName"

    try {
        $process = Start-Process -FilePath "git" -ArgumentList "clone", "https://github.com/base/$repoName.git", $repoName -NoNewWindow -Wait -PassThru

        if ($process.ExitCode -eq 0) {
            Write-Log "Successfully cloned: $repoName"
            $clonedCount++
        }
        else {
            Write-Log "Failed to clone: $repoName (Exit code: $($process.ExitCode))"
        }
    }
    catch {
        Write-Log "Error cloning $repoName : $_"
    }

    # Small delay to avoid rate limiting
    Start-Sleep -Seconds $DelaySeconds
}

Write-Log "Clone continuation completed. Cloned: $clonedCount, Skipped: $skippedCount, Total processed: $($repositories.Count)"
Write-Log "Check $logFile for details"
