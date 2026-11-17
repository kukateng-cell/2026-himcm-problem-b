param([string]$doc, [string]$pdf)
$ErrorActionPreference = "Stop"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($doc)
    $d.Fields.Update() | Out-Null
    $d.TablesOfContents | ForEach-Object { $_.Update() }
    $d.ExportAsFixedFormat($pdf, 17)
    $d.Repaginate()
    Write-Output ("pages(Word): " + $d.ComputeStatistics(2))
    $d.Close($false)
    Write-Output "exported"
} finally {
    $w.Quit()
}
