$ErrorActionPreference = "Stop"
$doc = "C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
$pdf = "C:\Users\kukat\Desktop\USA\_extract\v1.3_word.pdf"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($doc)
    $d.ExportAsFixedFormat($pdf, 17)  # wdExportFormatPDF
    $d.Repaginate()
    Write-Output ("pages(Word): " + $d.ComputeStatistics(2))
    $d.Close($false)
    Write-Output "exported"
} finally {
    $w.Quit()
}
