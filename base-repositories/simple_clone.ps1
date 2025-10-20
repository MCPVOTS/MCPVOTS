# Simple PowerShell script to clone Base repositories
# Usage: .\simple_clone.ps1

param(
    [switch]$SkipLargeRepos = $true
)

$baseDir = $PSScriptRoot
$repoList = Join-Path $baseDir "base_repos.txt"
$logFile = Join-Path $baseDir "simple_clone_log.txt"

Write-Host "Starting simple Base repositories clone process..."
"$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Starting simple clone process" | Out-File -FilePath $logFile -Append

if (-not (Test-Path $repoList)) {
    Write-Host "Error: Repository list file not found: $repoList"
    exit 1
}

# Large repositories to skip
$largeRepos = @("optimism", "op-geth", "reth", "node-reth", "goleveldb", "go-ethereum-rpc")

$repositories = Get-Content $repoList | Where-Object { $_ -and $_.Trim() -ne "" }

foreach ($repo in $repositories) {
    $repoName = $repo.Trim()

    if ($SkipLargeRepos -and $repoName -in $largeRepos) {
        Write-Host "Skipping large repository: $repoName"
        "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Skipping large repo: $repoName" | Out-File -FilePath $logFile -Append
        continue
    }

    $repoPath = Join-Path $baseDir $repoName

    if (Test-Path $repoPath) {
        Write-Host "Repository already exists: $repoName"
        "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Already exists: $repoName" | Out-File -FilePath $logFile -Append
    }
    else {
        Write-Host "Cloning repository: $repoName"
        "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Cloning: $repoName" | Out-File -FilePath $logFile -Append

        try {
            & git clone "https://github.com/base/$repoName.git" $repoPath
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Successfully cloned: $repoName"
                "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Cloned: $repoName" | Out-File -FilePath $logFile -Append
            }
            else {
                Write-Host "Failed to clone: $repoName"
                "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Failed clone: $repoName" | Out-File -FilePath $logFile -Append
            }
        }
        catch {
            Write-Host "Error cloning $repoName : $_"
            "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Error cloning $repoName : $_" | Out-File -FilePath $logFile -Append
        }
    }

    # Small delay to avoid rate limiting
    Start-Sleep -Seconds 3
}

Write-Host "Simple clone process completed. Check $logFile for details."
"$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - Simple clone process completed" | Out-File -FilePath $logFile -Append
