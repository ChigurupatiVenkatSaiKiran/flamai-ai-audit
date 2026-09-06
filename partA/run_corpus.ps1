python corpus_prep.py > corpus_prep_log.txt 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS"
    Get-Content corpus_prep_log.txt | Select-Object -Last 20
} else {
    Write-Host "FAILED"
    Get-Content corpus_prep_log.txt | Select-Object -Last 30
}
