<#
.SYNOPSIS
    Inspect a run directory and display facts summary information.

.DESCRIPTION
    Looks for facts summary files in the specified run directory.
    Canon (Name=B): fitting output is fitting_facts_summary.json
    Legacy fallback: facts_summary.json

.PARAMETER RunDir
    Path to the run directory to inspect.

.EXAMPLE
    .\inspect_run.ps1 -RunDir "verification/runs/facts/geo_v0_s1/round01"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RunDir
)

$ErrorActionPreference = "Continue"

# --- File Resolution (Canon Name=B: fitting_facts_summary.json first) ---
$canonicalFile = "fitting_facts_summary.json"
$legacyFile = "facts_summary.json"

$selectedFile = $null
$selectedPath = $null

# Try canonical file first
$canonicalPath = Join-Path $RunDir $canonicalFile
if (Test-Path $canonicalPath) {
    $selectedFile = $canonicalFile
    $selectedPath = $canonicalPath
}

# Fallback to legacy file
if (-not $selectedFile) {
    $legacyPath = Join-Path $RunDir $legacyFile
    if (Test-Path $legacyPath) {
        $selectedFile = $legacyFile
        $selectedPath = $legacyPath
        Write-Host "[WARN] Using legacy filename: $legacyFile (canonical is $canonicalFile)" -ForegroundColor Yellow
    }
}

# Neither found
if (-not $selectedFile) {
    Write-Host "=== Inspect Run ===" -ForegroundColor Cyan
    Write-Host "Run directory: $RunDir"
    Write-Host ""
    Write-Host "[ERROR] Facts summary file not found." -ForegroundColor Red
    Write-Host "  Looked for:"
    Write-Host "    1. $canonicalFile (canonical)"
    Write-Host "    2. $legacyFile (legacy fallback)"
    Write-Host ""
    Write-Host "Ensure the run completed successfully before inspecting."
    exit 0  # No crash per ops rules
}

# --- Display Header ---
Write-Host "=== Inspect Run ===" -ForegroundColor Cyan
Write-Host "Run directory: $RunDir"
Write-Host "Using facts summary: $selectedFile" -ForegroundColor Green
Write-Host ""

# --- Parse and Display JSON ---
try {
    $jsonContent = Get-Content -Path $selectedPath -Raw | ConvertFrom-Json

    # Schema version
    if ($jsonContent.schema_version) {
        Write-Host "Schema version: $($jsonContent.schema_version)"
    }

    # Provenance info
    if ($jsonContent.provenance) {
        Write-Host ""
        Write-Host "--- Provenance ---" -ForegroundColor Yellow
        if ($jsonContent.provenance.code_fingerprint) {
            Write-Host "  code_fingerprint: $($jsonContent.provenance.code_fingerprint)"
        }
        if ($jsonContent.provenance.geometry_impl_version) {
            Write-Host "  geometry_impl_version: $($jsonContent.provenance.geometry_impl_version)"
        }
        if ($jsonContent.provenance.dataset_version) {
            Write-Host "  dataset_version: $($jsonContent.provenance.dataset_version)"
        }
    }

    # Coverage info
    if ($jsonContent.coverage) {
        Write-Host ""
        Write-Host "--- Coverage ---" -ForegroundColor Yellow
        if ($null -ne $jsonContent.coverage.has_body_measurements) {
            Write-Host "  has_body_measurements: $($jsonContent.coverage.has_body_measurements)"
        }
        if ($null -ne $jsonContent.coverage.has_garment_measurements) {
            Write-Host "  has_garment_measurements: $($jsonContent.coverage.has_garment_measurements)"
        }
        if ($jsonContent.coverage.used_keys) {
            $keyCount = $jsonContent.coverage.used_keys.Count
            Write-Host "  used_keys: $keyCount keys"
        }
    }

    # NaN info
    if ($null -ne $jsonContent.nan_rate) {
        Write-Host ""
        Write-Host "--- NaN Statistics ---" -ForegroundColor Yellow
        Write-Host "  nan_rate: $($jsonContent.nan_rate)"
    }
    if ($jsonContent.nan_count) {
        Write-Host "  nan_count.total: $($jsonContent.nan_count.total)"
        Write-Host "  nan_count.nan: $($jsonContent.nan_count.nan)"
    }

    # Reasons
    if ($jsonContent.reasons) {
        Write-Host ""
        Write-Host "--- Reasons ---" -ForegroundColor Yellow
        $jsonContent.reasons.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)"
        }
    }

    # Warnings summary
    if ($jsonContent.warnings) {
        Write-Host ""
        Write-Host "--- Warnings ---" -ForegroundColor Yellow
        $warningCount = 0
        $jsonContent.warnings.PSObject.Properties | ForEach-Object {
            $code = $_.Name
            $value = $_.Value
            if ($value -is [array]) {
                $count = $value.Count
            } elseif ($value.count) {
                $count = $value.count
            } else {
                $count = 1
            }
            Write-Host "  $code : $count"
            $warningCount += $count
        }
        Write-Host "  Total warnings: $warningCount"
    }

    Write-Host ""
    Write-Host "=== Inspection Complete ===" -ForegroundColor Cyan

} catch {
    Write-Host "[ERROR] Failed to parse JSON: $_" -ForegroundColor Red
    Write-Host "File path: $selectedPath"
    exit 0  # No crash per ops rules
}

exit 0
