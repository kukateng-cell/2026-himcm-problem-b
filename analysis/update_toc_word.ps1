$ErrorActionPreference = "Stop"
$path = "C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($path)
    $n = $d.TablesOfContents.Count
    Write-Output ("TOCs: " + $n)
    for ($i = 1; $i -le $n; $i++) { $d.TablesOfContents.Item($i).Update() }
    $d.Fields.Update() | Out-Null
    $d.Repaginate()
    Write-Output ("pages(Word): " + $d.ComputeStatistics(2))
    $d.Save()
    $d.Close()
    Write-Output "saved"
} finally {
    $w.Quit()
}
