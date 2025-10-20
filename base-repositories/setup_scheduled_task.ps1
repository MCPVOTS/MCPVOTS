# Windows Scheduled Task Setup for Daily Base Repository Updates
# Run this script as Administrator to set up daily updates

$taskName = "Base Repositories Daily Update"
$scriptPath = Join-Path $PSScriptRoot "daily_update.bat"

# Check if running as administrator
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator to set up the scheduled task."
    exit 1
}

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"  # Run at 2 AM daily
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily update of Base organization repositories"
    Write-Host "Scheduled task created successfully. The task will run daily at 2:00 AM."
    Write-Host "Task Name: $taskName"
}
catch {
    Write-Host "Failed to create scheduled task: $_"
}

Write-Host ""
Write-Host "To manually run the update:"
Write-Host "1. Double-click daily_update.bat"
Write-Host "2. Or run: .\clone_base_repos.ps1 -UpdateOnly"
Write-Host ""
Write-Host "To modify the schedule, use Task Scheduler or run this setup script again."
