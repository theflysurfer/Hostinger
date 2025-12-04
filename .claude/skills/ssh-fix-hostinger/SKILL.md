---
name: ssh-fix-hostinger
description: This skill should be used when SSH connection to Hostinger VPS (srv759970, automation@69.62.108.82) fails with "Permission denied" errors. It diagnoses and fixes SSH key permission issues on Windows that prevent successful authentication.
---

# SSH Connection Repair for Hostinger VPS

Diagnose and repair SSH connection issues to Hostinger VPS (srv759970) at `automation@69.62.108.82`.

## When to Use

Use this skill when encountering:
- `Permission denied (publickey)` errors
- `connect to host 69.62.108.82 port 22: Permission denied`
- SSH connection that worked previously but suddenly fails
- Key permission warnings on Windows

## Diagnostic Workflow

### Step 1: Test Network Connectivity

Verify the server is reachable:

```bash
ping -n 4 69.62.108.82
```

Expected: 3-4 packets received (some loss is acceptable).

### Step 2: Test SSH Connection

Attempt verbose SSH connection:

```bash
ssh -v -o ConnectTimeout=10 automation@69.62.108.82 "echo 'SSH OK'"
```

Look for:
- `Permission denied` → Key permission issue (continue to Step 3)
- `Connection refused` → SSH service down on server
- `Connection timeout` → Network/firewall issue

### Step 3: Check SSH Key Permissions

On Windows, SSH keys must have restricted permissions. The key file should ONLY be accessible by the current user.

Common issue: Inherited permissions from parent folders allow other users/groups to access the key, which OpenSSH rejects for security.

## Repair Workflow

### Fix SSH Key Permissions (Windows)

Use the PowerShell script to repair permissions:

```powershell
scripts/fix-ssh-permissions.ps1
```

Or manually via PowerShell:

```powershell
$keyPath = "$env:USERPROFILE\.ssh\id_ed25519"

# Remove inheritance and all existing permissions
$acl = Get-Acl $keyPath
$acl.SetAccessRuleProtection($true, $false)
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }

# Add only current user with full control
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "FullControl", "Allow")
$acl.AddAccessRule($rule)

Set-Acl $keyPath $acl
```

### Verify Fix

After fixing permissions, test the connection:

```bash
ssh automation@69.62.108.82 "echo 'SSH connection OK'"
```

Expected output: `SSH connection OK`

If still failing, try adding the key to ssh-agent:

```bash
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"
```

## Common Scenarios

### Scenario 1: Connection Worked 1 Hour Ago, Now Fails

**Root cause**: Windows updates or security software may reset file permissions.

**Solution**:
1. Run `scripts/fix-ssh-permissions.ps1`
2. Test connection
3. If issue persists, check if Windows Defender or antivirus modified key file

### Scenario 2: Multiple SSH Keys

If using multiple keys, specify the key explicitly:

```bash
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" automation@69.62.108.82
```

Or configure in `~/.ssh/config`:

```
Host srv759970
  HostName 69.62.108.82
  User automation
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

### Scenario 3: Git Bash vs PowerShell

Permission syntax differs:
- **PowerShell**: Use `scripts/fix-ssh-permissions.ps1`
- **Git Bash**: `chmod 600 ~/.ssh/id_ed25519` (may not work reliably on Windows)

## Server Information

- **Host**: `automation@69.62.108.82`
- **Alias**: `srv759970` (if configured in `~/.ssh/config`)
- **Key type**: ED25519
- **Key location**: `%USERPROFILE%\.ssh\id_ed25519`

## Key Principles

- SSH keys must have 600-equivalent permissions (owner read/write only)
- Windows inherited permissions often cause "too open" errors
- Permission fixes must remove ALL access rules before adding current user
- After any Windows update, key permissions may need re-applying
- Using SSH config aliases (`srv759970`) simplifies commands

## Troubleshooting Reference

See `references/ssh-errors.md` for complete error reference and solutions.

## Scripts

- `scripts/fix-ssh-permissions.ps1` - Fix SSH key permissions on Windows
- `scripts/test-ssh-connection.ps1` - Comprehensive SSH connection test
