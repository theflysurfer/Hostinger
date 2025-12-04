# Comprehensive SSH connection test for Hostinger VPS
# Tests network connectivity, SSH service, and authentication

param(
    [string]$Server = "69.62.108.82",
    [string]$User = "automation",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = "Continue"

Write-Host "🔍 SSH Connection Diagnostic for $User@$Server" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Test 1: Network Connectivity
Write-Host "`n1️⃣  Testing network connectivity..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $Server -Count 4 -ErrorAction SilentlyContinue

if ($pingResult) {
    $successRate = ($pingResult | Where-Object { $_.Status -eq "Success" }).Count
    Write-Host "   ✅ Server is reachable ($successRate/4 packets received)" -ForegroundColor Green
    $avgTime = ($pingResult | Where-Object { $_.Status -eq "Success" } | Measure-Object -Property Latency -Average).Average
    Write-Host "   📊 Average latency: $([math]::Round($avgTime, 0))ms" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Server is not reachable" -ForegroundColor Red
    Write-Host "   Check your internet connection or server status" -ForegroundColor Yellow
    exit 1
}

# Test 2: Firewall Check
Write-Host "`n2️⃣  Testing firewall (port 22 connectivity)..." -ForegroundColor Yellow
$portTest = Test-NetConnection -ComputerName $Server -Port 22 -WarningAction SilentlyContinue

if ($portTest.TcpTestSucceeded) {
    Write-Host "   ✅ Port 22 is accessible (no firewall blocking)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Port 22 is BLOCKED by firewall" -ForegroundColor Red
    Write-Host "   🔧 Possible causes:" -ForegroundColor Yellow
    Write-Host "      - TinyWall is blocking SSH" -ForegroundColor White
    Write-Host "      - Windows Firewall blocking outbound port 22" -ForegroundColor White
    Write-Host "      - Corporate firewall/proxy" -ForegroundColor White
    Write-Host "`n   Solutions:" -ForegroundColor Yellow
    Write-Host "      1. Disable TinyWall temporarily to test" -ForegroundColor White
    Write-Host "      2. Add exception for ssh.exe in firewall" -ForegroundColor White
    Write-Host "      3. Check Windows Firewall outbound rules" -ForegroundColor White
    exit 1
}

# Test 3: SSH Key Existence
Write-Host "`n3️⃣  Checking SSH key..." -ForegroundColor Yellow
if (Test-Path $KeyPath) {
    Write-Host "   ✅ SSH key found: $KeyPath" -ForegroundColor Green

    # Check permissions
    $acl = Get-Acl $KeyPath
    $accessRules = $acl.Access | Where-Object { $_.IsInherited -eq $false }

    if ($accessRules.Count -eq 1) {
        Write-Host "   ✅ Key has proper permissions (1 access rule)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Key has $($accessRules.Count) access rules (should be 1)" -ForegroundColor Yellow
        Write-Host "   Run fix-ssh-permissions.ps1 to fix this" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ SSH key not found: $KeyPath" -ForegroundColor Red
    Write-Host "   Generate a new key with: ssh-keygen -t ed25519" -ForegroundColor Yellow
    exit 1
}

# Test 4: SSH Connection
Write-Host "`n4️⃣  Testing SSH connection..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=10 -o BatchMode=yes "$User@$Server" "echo 'SSH_OK'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ SSH connection successful!" -ForegroundColor Green
    Write-Host "   Response: $sshTest" -ForegroundColor Gray
} else {
    Write-Host "   ❌ SSH connection failed" -ForegroundColor Red

    # Analyze error
    if ($sshTest -match "Permission denied") {
        Write-Host "   🔧 Issue: Permission denied (key authentication failed)" -ForegroundColor Yellow
        Write-Host "   Solutions:" -ForegroundColor Yellow
        Write-Host "      1. Run fix-ssh-permissions.ps1" -ForegroundColor White
        Write-Host "      2. Verify your public key is in ~/.ssh/authorized_keys on server" -ForegroundColor White
        Write-Host "      3. Try: ssh-add `"$KeyPath`"" -ForegroundColor White
    } elseif ($sshTest -match "Connection refused") {
        Write-Host "   🔧 Issue: SSH service is not running on server" -ForegroundColor Yellow
        Write-Host "   Contact server administrator" -ForegroundColor White
    } elseif ($sshTest -match "timeout") {
        Write-Host "   🔧 Issue: Connection timeout (firewall or network)" -ForegroundColor Yellow
        Write-Host "   Check firewall settings" -ForegroundColor White
    } else {
        Write-Host "   Error details:" -ForegroundColor Yellow
        Write-Host "   $sshTest" -ForegroundColor Gray
    }

    Write-Host "`n   Running verbose connection test..." -ForegroundColor Cyan
    ssh -v "$User@$Server" "echo 'test'" 2>&1 | Select-String -Pattern "debug1:|Permission denied|Connection"

    exit 1
}

# Test 5: Server Information
Write-Host "`n5️⃣  Gathering server information..." -ForegroundColor Yellow
$serverInfo = ssh "$User@$Server" "uname -a && df -h / | tail -1" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Server info retrieved:" -ForegroundColor Green
    Write-Host "   $serverInfo" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  Could not retrieve server info" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "✅ SSH diagnostics complete!" -ForegroundColor Green
