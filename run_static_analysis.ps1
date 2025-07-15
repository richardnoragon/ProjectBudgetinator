# Static Analysis Runner for ProjectBudgetinator
# PowerShell script to run all static analysis tools

param(
    [string[]]$Tools = @("mypy", "pylint", "flake8", "bandit", "black", "isort"),
    [switch]$FixFormatting,
    [switch]$InstallDeps,
    [switch]$Quiet
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Function to run a command and capture results
function Invoke-AnalysisTool {
    param(
        [string]$ToolName,
        [string[]]$Command,
        [string]$Description
    )
    
    if (-not $Quiet) {
        Write-Host "`n$('='*60)" -ForegroundColor Cyan
        Write-Host "Running $ToolName - $Description" -ForegroundColor Cyan
        Write-Host "$('='*60)" -ForegroundColor Cyan
        Write-Host "Command: $($Command -join ' ')" -ForegroundColor Gray
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        $result = & $Command[0] $Command[1..($Command.Length-1)] 2>&1
        $exitCode = $LASTEXITCODE
        $stopwatch.Stop()
        
        $success = $exitCode -eq 0
        
        if (-not $Quiet) {
            if ($success) {
                Write-ColorOutput Green "$ToolName completed successfully in $($stopwatch.Elapsed.TotalSeconds.ToString('F2'))s"
            } else {
                Write-ColorOutput Red "$ToolName failed with exit code $exitCode in $($stopwatch.Elapsed.TotalSeconds.ToString('F2'))s"
            }
            
            if ($result) {
                Write-Host "`nOutput:" -ForegroundColor Yellow
                Write-Host $result
            }
        }
        
        return @{
            Tool = $ToolName
            Success = $success
            ExitCode = $exitCode
            Duration = $stopwatch.Elapsed.TotalSeconds
            Output = $result -join "`n"
        }
    }
    catch {
        $stopwatch.Stop()
        if (-not $Quiet) {
            Write-ColorOutput Red "Error running $ToolName: $($_.Exception.Message)"
        }
        return @{
            Tool = $ToolName
            Success = $false
            ExitCode = -1
            Duration = $stopwatch.Elapsed.TotalSeconds
            Output = $_.Exception.Message
        }
    }
}

# Main script
Write-Host "ProjectBudgetinator Static Analysis Runner" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Using: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-ColorOutput Red "Error: Python is not installed or not in PATH"
    exit 1
}

# Create build directory
if (-not (Test-Path "build")) {
    New-Item -ItemType Directory -Path "build" | Out-Null
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "`nInstalling/updating dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Red "Failed to install dependencies"
        exit 1
    }
}

# Define tool configurations
$toolConfigs = @{
    "mypy" = @{
        Command = @("python", "-m", "mypy", "src/", "--config-file", "mypy.ini")
        Description = "Type checking"
    }
    "pylint" = @{
        Command = @("python", "-m", "pylint", "src/", "--rcfile", ".pylintrc")
        Description = "Code quality analysis"
    }
    "flake8" = @{
        Command = @("python", "-m", "flake8", "src/", "--config", ".flake8")
        Description = "Style and basic error checking"
    }
    "bandit" = @{
        Command = @("python", "-m", "bandit", "-r", "src/", "-c", ".bandit", "-f", "txt")
        Description = "Security vulnerability scanning"
    }
    "black" = @{
        Command = @("python", "-m", "black", "--check", "--diff", "src/")
        Description = "Code formatting check"
    }
    "isort" = @{
        Command = @("python", "-m", "isort", "--check-only", "--diff", "src/")
        Description = "Import sorting check"
    }
}

# If FixFormatting is requested, modify black and isort commands
if ($FixFormatting) {
    $toolConfigs["black"].Command = @("python", "-m", "black", "src/")
    $toolConfigs["black"].Description = "Code formatting (fixing)"
    $toolConfigs["isort"].Command = @("python", "-m", "isort", "src/")
    $toolConfigs["isort"].Description = "Import sorting (fixing)"
}

# Run selected tools
$results = @()
$totalStart = Get-Date

foreach ($tool in $Tools) {
    if ($toolConfigs.ContainsKey($tool)) {
        $config = $toolConfigs[$tool]
        $result = Invoke-AnalysisTool -ToolName $tool -Command $config.Command -Description $config.Description
        $results += $result
    } else {
        Write-ColorOutput Red "Unknown tool: $tool"
    }
}

$totalDuration = (Get-Date) - $totalStart

# Generate summary
if (-not $Quiet) {
    Write-Host "`n$('='*80)" -ForegroundColor Cyan
    Write-Host "STATIC ANALYSIS SUMMARY" -ForegroundColor Cyan
    Write-Host "$('='*80)" -ForegroundColor Cyan
    
    $passed = ($results | Where-Object { $_.Success }).Count
    $failed = $results.Count - $passed
    
    Write-Host "Total tools run: $($results.Count)"
    Write-Host "Passed: $passed" -ForegroundColor Green
    Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
    Write-Host "Total time: $($totalDuration.TotalSeconds.ToString('F2')) seconds"
    Write-Host ""
    
    # Tool-by-tool results
    foreach ($result in $results) {
        $status = if ($result.Success) { "✓ PASS" } else { "✗ FAIL" }
        $color = if ($result.Success) { "Green" } else { "Red" }
        Write-Host "$($result.Tool.PadRight(15)) | " -NoNewline
        Write-ColorOutput $color "$($status.PadRight(8))"
        Write-Host " | $($result.Duration.ToString('F2').PadLeft(6))s | Exit: $($result.ExitCode)"
    }
    
    Write-Host ""
    
    if ($failed -gt 0) {
        Write-Host "RECOMMENDATIONS:" -ForegroundColor Yellow
        Write-Host "- Review the output above to identify specific issues"
        Write-Host "- For formatting issues, run with -FixFormatting switch"
        Write-Host "- For type issues, add type annotations to your code"
        Write-Host "- For security issues, review and fix the flagged code"
    } else {
        Write-ColorOutput Green "🎉 All static analysis checks passed! Your code is in great shape."
    }
    
    Write-Host ""
    Write-Host "For more information:"
    Write-Host "- MyPy: https://mypy.readthedocs.io/"
    Write-Host "- Pylint: https://pylint.readthedocs.io/"
    Write-Host "- Flake8: https://flake8.pycqa.org/"
    Write-Host "- Bandit: https://bandit.readthedocs.io/"
    Write-Host "- Black: https://black.readthedocs.io/"
    Write-Host "- isort: https://pycqa.github.io/isort/"
}

# Save results to JSON
$jsonResults = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    project_root = (Get-Location).Path
    tools_run = $Tools
    fix_formatting = $FixFormatting.IsPresent
    summary = @{
        total_tools = $results.Count
        passed = ($results | Where-Object { $_.Success }).Count
        failed = ($results | Where-Object { -not $_.Success }).Count
        total_duration = $totalDuration.TotalSeconds
    }
    results = $results
}

$jsonPath = "build/static_analysis_results.json"
$jsonResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding utf8
Write-Host "Results saved to: $jsonPath" -ForegroundColor Gray

# Exit with appropriate code
$exitCode = if (($results | Where-Object { -not $_.Success }).Count -gt 0) { 1 } else { 0 }
exit $exitCode
