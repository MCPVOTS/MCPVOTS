# Organize Base Repositories by Category
# This script organizes cloned repositories into categorized folders

param(
    [switch]$DryRun
)

$baseDir = $PSScriptRoot

# Define category mappings
$categories = @{
    # Core Protocol
    "contracts"                 = "01-Core-Protocol"
    "contract-deployments"      = "01-Core-Protocol"
    "optimism"                  = "01-Core-Protocol"
    "op-geth"                   = "01-Core-Protocol"
    "op-enclave"                = "01-Core-Protocol"

    # Developer Tools
    "op-viem"                   = "02-Developer-Tools"
    "op-wagmi"                  = "02-Developer-Tools"
    "account-sdk"               = "02-Developer-Tools"
    "paymaster"                 = "02-Developer-Tools"
    "foundry"                   = "02-Developer-Tools"
    "keyspace"                  = "02-Developer-Tools"
    "keyspace-client"           = "02-Developer-Tools"
    "keyspace-recovery-service" = "02-Developer-Tools"

    # Infrastructure
    "bridge"                    = "03-Infrastructure"
    "node"                      = "03-Infrastructure"
    "reth"                      = "03-Infrastructure"
    "rollup-boost"              = "03-Infrastructure"
    "blob-archiver"             = "03-Infrastructure"
    "nitro-validator"           = "03-Infrastructure"
    "framework"                 = "03-Infrastructure"

    # Applications & Demos
    "web"                       = "04-Applications"
    "docs"                      = "04-Applications"
    "demos"                     = "04-Applications"
    "commerce-payments"         = "04-Applications"
    "onchainsummer.xyz"         = "04-Applications"
    "land-sea-and-sky"          = "04-Applications"
    "sub-account-demo"          = "04-Applications"
    "benchmark"                 = "04-Applications"
    "transaction-latency"       = "04-Applications"

    # Security & Audit
    "pessimism"                 = "05-Security"
    "FCL-ecdsa-verify-audit"    = "05-Security"
    "fp-test-cases"             = "05-Security"
    "fault-proof-monitors"      = "05-Security"

    # Identity & Names
    "basenames"                 = "06-Identity"
    "webauthn-sol"              = "06-Identity"
    "eip712sign"                = "06-Identity"

    # Utilities
    "chains"                    = "07-Utilities"
    "guides"                    = "07-Utilities"
    "brand-kit"                 = "07-Utilities"
    "tips"                      = "07-Utilities"
    "withdrawer"                = "07-Utilities"

    # MCP & AI
    "base-mcp"                  = "08-MCP-AI"
    "base-builder-mcp"          = "08-MCP-AI"

    # Mobile & Hardware
    "usbwallet"                 = "09-Mobile-Hardware"
    "nfc-relayer"               = "09-Mobile-Hardware"

    # Miscellaneous
    ".github"                   = "10-Misc"
    "go-ethereum-rpc"           = "10-Misc"
    "goleveldb"                 = "10-Misc"
    "go-bip39"                  = "10-Misc"
    "loader-v3-go-bindings"     = "10-Misc"
    "sol2base"                  = "10-Misc"
    "mcm-go"                    = "10-Misc"
    "task-signing-tool"         = "10-Misc"
    "RRC-7755-poc"              = "10-Misc"
    "eip-7702-proxy"            = "10-Misc"
    "node-reth"                 = "10-Misc"
    "triedb"                    = "10-Misc"
    "pos-dapp"                  = "10-Misc"
    "dev"                       = "10-Misc"
    "infra"                     = "10-Misc"
    "infra-routing"             = "10-Misc"
    "bridge-explorer"           = "10-Misc"
    "based-ox"                  = "10-Misc"
    "onramp-workshop"           = "10-Misc"
    "base-account-privy"        = "10-Misc"
    "op-rbuilder"               = "10-Misc"
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath "$baseDir\organization_log.txt" -Append -Encoding UTF8
    Write-Host $Message
}

Write-Log "Starting repository organization process"

$organized = 0
$skipped = 0

# Get all repository directories
$repos = Get-ChildItem -Directory | Where-Object { $_.Name -ne "organized" -and -not $_.Name.StartsWith(".") }

foreach ($repo in $repos) {
    $repoName = $repo.Name

    if ($categories.ContainsKey($repoName)) {
        $category = $categories[$repoName]
        $categoryPath = Join-Path $baseDir "organized\$category"

        if (-not (Test-Path $categoryPath)) {
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $categoryPath -Force | Out-Null
            }
            Write-Log "Created category directory: $category"
        }

        $sourcePath = $repo.FullName
        $destPath = Join-Path $categoryPath $repoName

        if ($DryRun) {
            Write-Log "[DRY RUN] Would move: $repoName -> $category\$repoName"
        }
        else {
            try {
                Move-Item -Path $sourcePath -Destination $destPath -Force
                Write-Log "Moved: $repoName -> $category\$repoName"
                $organized++
            }
            catch {
                Write-Log "Failed to move $repoName : $_"
                $skipped++
            }
        }
    }
    else {
        Write-Log "No category found for: $repoName (keeping in root)"
        $skipped++
    }
}

Write-Log "Organization completed. Organized: $organized, Skipped: $skipped"
Write-Log "Check organization_log.txt for details"

if ($DryRun) {
    Write-Host ""
    Write-Host "This was a dry run. No files were actually moved."
    Write-Host "Run without -DryRun to perform the actual organization."
}
