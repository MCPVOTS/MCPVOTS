# Base Repositories Clone and Update Script
# This script clones all Base organization repositories and sets up daily updates

param(
    [switch]$UpdateOnly,
    [switch]$SkipLargeRepos
)

$baseDir = $PSScriptRoot
$reposFile = Join-Path $baseDir "base_repos.txt"
$logFile = Join-Path $baseDir "clone_log.txt"

# Large repositories to skip if requested
$largeRepos = @("optimism", "op-geth", "reth", "node-reth", "goleveldb", "go-ethereum-rpc")

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append
    Write-Host $Message
}

function Clone-Repository {
    param([string]$repoName)

    if ($SkipLargeRepos -and $repoName -in $largeRepos) {
        Write-Log "Skipping large repository: $repoName"
        return
    }

    $repoPath = Join-Path $baseDir $repoName

    if (Test-Path $repoPath) {
        if ($UpdateOnly) {
            Write-Log "Updating repository: $repoName"
            Push-Location $repoPath
            try {
                git pull --rebase
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Successfully updated: $repoName"
                }
                else {
                    Write-Log "Failed to update: $repoName"
                }
            }
            catch {
                Write-Log "Error updating $repoName : $_"
            }
            Pop-Location
        }
        else {
            Write-Log "Repository already exists: $repoName"
        }
    }
    else {
        Write-Log "Cloning repository: $repoName"
        try {
            git clone "https://github.com/base/$repoName.git" $repoPath
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Successfully cloned: $repoName"
            }
            else {
                Write-Log "Failed to clone: $repoName"
            }
        }
        catch {
            Write-Log "Error cloning $repoName : $_"
        }
    }
}

# Main execution
Write-Log "Starting Base repositories $($UpdateOnly ? 'update' : 'clone') process"

if (-not (Test-Path $reposFile)) {
    Write-Log "Error: Repository list file not found: $reposFile"
    exit 1
}

$repositories = Get-Content $reposFile | Where-Object { $_ -and $_.Trim() -ne "" }

Write-Log "Found $($repositories.Count) repositories to process"

foreach ($repo in $repositories) {
    Clone-Repository -repoName $repo.Trim()
    Start-Sleep -Milliseconds 500  # Rate limiting
}

Write-Log "Process completed. Check $logFile for details."
