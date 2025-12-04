# Fix SSH key permissions on Windows
# This script removes inherited permissions and sets proper access for SSH private keys

param(
    [string]$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
)

Write-Host "🔧 Fixing SSH key permissions..." -ForegroundColor Yellow
Write-Host "   Key: $KeyPath" -ForegroundColor Gray

# Verify key exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "❌ SSH key not found at: $KeyPath" -ForegroundColor Red
    Write-Host "   Please specify the correct path with -KeyPath parameter" -ForegroundColor Yellow
    exit 1
}

# Get current ACL
$acl = Get-Acl $KeyPath

# Disable inheritance and remove inherited permissions
Write-Host "   Removing inherited permissions..." -ForegroundColor Gray
$acl.SetAccessRuleProtection($true, $false)

# Remove all existing access rules
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }

# Add only current user with full control
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "   Setting permissions for: $user" -ForegroundColor Gray
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $user,
    "FullControl",
    "Allow"
)
$acl.AddAccessRule($rule)

# Apply new ACL
Set-Acl $KeyPath $acl

Write-Host "✅ SSH key permissions fixed" -ForegroundColor Green

# Verify permissions
Write-Host "`n📋 Current permissions:" -ForegroundColor Cyan
$newAcl = Get-Acl $KeyPath
$newAcl.Access | Format-Table IdentityReference, FileSystemRights, AccessControlType -AutoSize

Write-Host "✅ Key is now secured for SSH use" -ForegroundColor Green
