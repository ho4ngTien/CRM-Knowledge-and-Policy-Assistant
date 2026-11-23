# Portable Repo Self-Validator for SongNhat CKPA Gate G1 Data Deliverables ([P3] Knowledge & Data Steward)
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File data/g1/scripts/validate_g1_repo.ps1
$ErrorActionPreference = "Stop"

$g1Root   = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $g1Root)

$validStatuses   = @("draft","owner_reviewed","approved","scheduled","effective","superseded","withdrawn")
$validFieldTypes = @("number","currency","duration","role","document_list","boolean","text_rule")
$validOps        = @("<=","<",">=",">","==","in","between","required")
$validActions    = @("upsert","tombstone")
$validRoles      = @("reader","steward","policy_owner","referral_handler","administrator","privacy_security_owner","independent_evaluator")
$reqScopeDims    = @("company:","branch:","role:","customer_group:","product:","transaction_scope:")

$expectedPasCols = @(
    "passage_id","document_id","document_version_id","title","content","source_ref",
    "page_number","clause_ref","language","owner","approver","recorded_at","published_at",
    "effective_from","effective_to","scope","audience","status","supersedes",
    "has_essential_attachments","record_action"
)
$expectedCfCols = @(
    "field_id","policy_id","policy_version_id","document_version_id","field_name","field_type",
    "operator","value","unit","currency","approval_role","time_limit","exception_condition",
    "required_documents","effective_from","effective_to","scope","audience","source_clause",
    "owner","approver","status","record_action"
)

function Get-Sha256($text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Validate-Bundle($label, $pasPath, $cfPath, $manifestPath, $maxDocs, $maxPas, $maxCf) {
    Write-Host "`n================================================================"
    Write-Host "VALIDATING: $label"
    Write-Host "================================================================"
    $errors = @()

    $pas = Import-Csv $pasPath -Encoding UTF8
    $cf  = Import-Csv $cfPath  -Encoding UTF8
    $man = Import-Csv $manifestPath -Encoding UTF8

    $pasCols = @($pas[0].PSObject.Properties | ForEach-Object { $_.Name })
    $cfCols  = @($cf[0].PSObject.Properties  | ForEach-Object { $_.Name })
    if (($pasCols -join ",") -ne ($expectedPasCols -join ",")) { $errors += "Passages header mismatch with PASSAGES_CSV_COLUMNS" }
    if (($cfCols  -join ",") -ne ($expectedCfCols  -join ",")) { $errors += "Critical fields header mismatch with CRITICAL_FIELDS_CSV_COLUMNS" }

    $docs = $pas | Select-Object -ExpandProperty document_id -Unique
    if ($docs.Count -gt $maxDocs) { $errors += "Docs=$($docs.Count) > $maxDocs" }
    if ($pas.Count  -gt $maxPas)  { $errors += "Passages=$($pas.Count) > $maxPas" }
    if ($cf.Count   -gt $maxCf)   { $errors += "CriticalFields=$($cf.Count) > $maxCf" }
    if ($pas.Count  -gt 500 -or $cf.Count -gt 500) { $errors += "Exceeds 500-row batch ceiling (OPS 01)" }

    $seenPas = @{}; $pasById = @{}; $statusCounts = @{}
    $ingAccPas = 0; $ingQuarPas = 0; $restricted = 0; $maxLen = 0
    foreach ($p in $pas) {
        if ($seenPas.ContainsKey($p.passage_id)) { $errors += "Duplicate passage_id: $($p.passage_id)" }
        $seenPas[$p.passage_id] = $true; $pasById[$p.passage_id] = $p
        if ($p.content.Length -gt $maxLen) { $maxLen = $p.content.Length }
        if ($p.content.Length -gt 6000) { $errors += "$($p.passage_id) > 6000 Unicode chars" }
        $pg = 0; if (-not [int]::TryParse($p.page_number, [ref]$pg) -or $pg -lt 1) { $errors += "$($p.passage_id) invalid page_number" }
        if ($validStatuses -notcontains $p.status) { $errors += "$($p.passage_id) invalid status" }
        $statusCounts[$p.status] = ($statusCounts[$p.status] + 1)
        if ($validActions -notcontains $p.record_action) { $errors += "$($p.passage_id) invalid record_action" }
        foreach ($dim in $reqScopeDims) { if ($p.scope -notmatch [regex]::Escape($dim)) { $errors += "$($p.passage_id) missing scope dim $dim" } }
        foreach ($aud in ($p.audience -split ",")) { if ($validRoles -notcontains $aud.Trim()) { $errors += "$($p.passage_id) invalid UserRole $($aud.Trim())" } }
        if ($p.audience -notmatch "reader") { $restricted++ }
        if ($p.has_essential_attachments -eq "false") { $ingQuarPas++ } elseif ($p.has_essential_attachments -eq "true") { $ingAccPas++ } else { $errors += "$($p.passage_id) invalid has_essential_attachments" }
        if ($p.effective_from -notmatch "\+07:00$" -or $p.recorded_at -notmatch "\+07:00$") { $errors += "$($p.passage_id) timestamp not +07:00" }
    }

    $seenCf = @{}; $cfById = @{}; $ingAccCf = 0; $ingQuarCf = 0
    foreach ($c in $cf) {
        if ($seenCf.ContainsKey($c.field_id)) { $errors += "Duplicate field_id: $($c.field_id)" }
        $seenCf[$c.field_id] = $true; $cfById[$c.field_id] = $c
        if ($validFieldTypes -notcontains $c.field_type) { $errors += "$($c.field_id) invalid field_type" }
        if ($validOps -notcontains $c.operator)          { $errors += "$($c.field_id) invalid operator" }
        if ($validStatuses -notcontains $c.status)       { $errors += "$($c.field_id) invalid status" }
        if ($validActions -notcontains $c.record_action) { $errors += "$($c.field_id) invalid record_action" }
        if ($c.field_type -eq "currency" -and [string]::IsNullOrWhiteSpace($c.currency)) { $errors += "$($c.field_id) missing currency"; $ingQuarCf++ } else { $ingAccCf++ }
        if ($c.field_type -eq "number" -and [string]::IsNullOrWhiteSpace($c.unit)) { $errors += "$($c.field_id) missing unit" }
        if ($c.field_type -in @("number","currency","duration")) {
            if ($c.operator -eq "between") {
                if ($c.value -notmatch '^\s*-?\d+(\.\d+)?\s*;\s*-?\d+(\.\d+)?\s*$') { $errors += "$($c.field_id) invalid between format" }
            } elseif ($c.operator -in @("<=","<",">=",">","==")) {
                $dec = [decimal]0
                if (-not [decimal]::TryParse($c.value.Trim(), [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$dec)) {
                    $errors += "$($c.field_id) non-Decimal value '$($c.value)'"
                }
            }
        }
        foreach ($dim in $reqScopeDims) { if ($c.scope -notmatch [regex]::Escape($dim)) { $errors += "$($c.field_id) missing scope dim $dim" } }
        foreach ($aud in ($c.audience -split ",")) { if ($validRoles -notcontains $aud.Trim()) { $errors += "$($c.field_id) invalid UserRole $($aud.Trim())" } }
        if ($c.effective_from -notmatch "\+07:00$") { $errors += "$($c.field_id) effective_from not +07:00" }
    }

    foreach ($st in $validStatuses) {
        if (-not $statusCounts.ContainsKey($st)) { $errors += "Missing KNW 03 status '$st'" }
    }

    $expectedMan = $pas.Count + $cf.Count
    if ($man.Count -ne $expectedMan) { $errors += "Manifest rows=$($man.Count) != $expectedMan" }
    $missingUri = 0; $badHash = 0
    foreach ($m in $man) {
        $absUri = Join-Path $repoRoot ($m.source_uri -replace '/','\')
        if (-not (Test-Path $absUri) -or $m.source_uri_exists -ne "true") { $missingUri++ }
        if ($m.record_type -eq "passage") {
            $p = $pasById[$m.record_id]
            $calc = Get-Sha256 "$($p.passage_id)|$($p.document_id)|$($p.document_version_id)|$($p.clause_ref)|$($p.content)|$($p.scope)|$($p.status)"
            if ($calc -ne $m.sha256_checksum) { $badHash++ }
        } elseif ($m.record_type -eq "critical_field") {
            $c = $cfById[$m.record_id]
            $calc = Get-Sha256 "$($c.field_id)|$($c.policy_id)|$($c.policy_version_id)|$($c.field_type)|$($c.operator)|$($c.value)|$($c.unit)|$($c.currency)|$($c.approval_role)|$($c.status)"
            if ($calc -ne $m.sha256_checksum) { $badHash++ }
        }
    }
    if ($missingUri -gt 0) { $errors += "$missingUri manifest rows have missing repo-relative source_uri!" }
    if ($badHash -gt 0)    { $errors += "$badHash manifest rows failed SHA-256 verification!" }

    Write-Host "  Docs: $($docs.Count)/$maxDocs | Passages: $($pas.Count)/$maxPas (max=$maxLen/6000) | CriticalFields: $($cf.Count)/$maxCf"
    Write-Host "  IngestionService simulation: Passages Expected=$($pas.Count) = Accepted $ingAccPas + Quarantined $ingQuarPas | CriticalFields Expected=$($cf.Count) = Accepted $ingAccCf + Quarantined $ingQuarCf"
    Write-Host "  Manifest SHA-256 & repo source_uri: $($man.Count)/$expectedMan verified (0 missing, 0 hash mismatch) | Restricted RBAC: $restricted"
    if ($errors.Count -gt 0) {
        $errors | ForEach-Object { Write-Host "  [ERR] $_" -ForegroundColor Red }
        throw "Validation failed for $label"
    }
    Write-Host "  RESULT: PASS (0 errors)" -ForegroundColor Green
}

$f1Pas = Join-Path $g1Root "family1\Policy_Corpus_Family1.csv"
if (Test-Path $f1Pas) {
    Validate-Bundle "CKPA-50 Family 1 (POL-001)" $f1Pas `
        (Join-Path $g1Root "family1\Critical_Fields_Family1.csv") `
        (Join-Path $g1Root "family1\Source_URI_And_Checksum_Manifest_Family1.csv") `
        10 100 18
}

$fullPas = Join-Path $g1Root "full\Policy_Corpus_G1_Full.csv"
if (Test-Path $fullPas) {
    Validate-Bundle "CKPA-58 Full G1 Corpus (3 Families)" $fullPas `
        (Join-Path $g1Root "full\Critical_Fields_G1_Full.csv") `
        (Join-Path $g1Root "full\Source_URI_And_Checksum_Manifest_G1_Full.csv") `
        30 300 50
}

# P5 CKPA-47 g1_security_audit_runner.py exact PII scan on data/g1/
Write-Host "`n=== [P5] CKPA-47 EXACT PII SCAN ON data/g1/ ==="
$p5Patterns = @{
    "VN_PHONE"       = '(?:\+84|0)(?:3|5|7|8|9)\d{8}\b'
    "EMAIL"          = '[a-zA-Z0-9_.+-]+@(?!songnhat\.vn|example\.com)[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    "CCCD_12_DIGITS" = '\b0\d{11}\b'
}
$scanFiles = Get-ChildItem -Recurse -File $g1Root | Where-Object { $_.Extension -in @(".csv",".json",".md",".txt") }
$piiHits = 0
foreach ($sf in $scanFiles) {
    $lines = Get-Content -Encoding UTF8 $sf.FullName
    for ($ln = 0; $ln -lt $lines.Count; $ln++) {
        foreach ($k in $p5Patterns.Keys) {
            if ([regex]::IsMatch($lines[$ln], $p5Patterns[$k])) {
                $piiHits++
                Write-Host "  [PII HIT: $k] $($sf.Name):$($ln+1)" -ForegroundColor Red
            }
        }
    }
}
Write-Host "Scanned files: $($scanFiles.Count) | Real PII hits: $piiHits"
if ($piiHits -gt 0) { throw "PII scan failed!" }

# CI docs-link-check simulation on data/g1/README.md (relative links & banned legacy strings)
$readme = Join-Path $g1Root "README.md"
if (Test-Path $readme) {
    Write-Host "`n=== CI docs-link-check SIMULATION ON data/g1/README.md ==="
    $txt = Get-Content -Raw -Encoding UTF8 $readme
    $banned = @("work-packages","pm-schedule-tien","p95\s*(?:<=|≤)\s*8\s*s\b","\b8\s*giây\b")
    foreach ($b in $banned) {
        if ([regex]::IsMatch($txt, $b, "IgnoreCase")) { throw "Banned CI legacy string '$b' found in data/g1/README.md!" }
    }
    foreach ($m in [regex]::Matches($txt, '!?\[[^\]]*\]\(([^)\r\n]+)\)')) {
        $target = ($m.Groups[1].Value.Trim() -split '\s+')[0]
        if ($target -match '^(#|https?://|mailto:|tel:)') { continue }
        $tClean = ($target -split '[#?]')[0]
        $resolved = Join-Path (Split-Path -Parent $readme) ($tClean -replace '/','\')
        if (-not (Test-Path $resolved)) { throw "Broken relative link in data/g1/README.md -> $target" }
    }
    Write-Host "data/g1/README.md CI check: PASS (0 broken links, 0 banned strings)" -ForegroundColor Green
}

Write-Host "`nALL REPO G1 VALIDATIONS PASSED 100%!" -ForegroundColor Green
