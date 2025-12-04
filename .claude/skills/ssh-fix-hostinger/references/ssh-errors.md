# SSH Connection Errors Reference

Complete reference for SSH connection errors to Hostinger VPS and their solutions.

## Permission Errors

### `Permission denied (publickey)`

**Symptoms**:
```
debug1: Connecting to 69.62.108.82 [69.62.108.82] port 22.
debug1: connect to address 69.62.108.82 port 22: Permission denied
ssh: connect to host 69.62.108.82 port 22: Permission denied
```

**Root Causes**:
1. **Firewall blocking SSH (most common)** - TinyWall or Windows Firewall blocking port 22
2. SSH key permissions too open (common on Windows)
3. Public key not added to server's `~/.ssh/authorized_keys`
4. Key not loaded in ssh-agent
5. Wrong key being used

**Solutions**:

1. **Check firewall first** (most likely cause):
   ```powershell
   # Test if port 22 is reachable
   Test-NetConnection -ComputerName 69.62.108.82 -Port 22
   ```
   If `TcpTestSucceeded : False`, check:
   - TinyWall: Temporarily disable to test, then add exception for SSH
   - Windows Firewall: Add outbound rule for port 22
   - Corporate firewall/proxy: May need VPN or proxy configuration

2. Fix key permissions (Windows):
   ```powershell
   scripts/fix-ssh-permissions.ps1
   ```

3. Verify public key on server:
   ```bash
   # From another working connection or web console
   cat ~/.ssh/authorized_keys | grep "your-key-comment"
   ```

4. Add key to ssh-agent:
   ```bash
   eval $(ssh-agent -s)
   ssh-add ~/.ssh/id_ed25519
   ```

5. Specify key explicitly:
   ```bash
   ssh -i ~/.ssh/id_ed25519 automation@69.62.108.82
   ```

### `Bad permissions` or `Permissions are too open`

**Symptoms**:
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for 'id_ed25519' are too open.
```

**Root Cause**: SSH key file has permissions that allow other users to read it.

**Solution**: Run `scripts/fix-ssh-permissions.ps1` to set proper Windows ACLs.

## Connection Errors

### `Connection refused`

**Symptoms**:
```
ssh: connect to host 69.62.108.82 port 22: Connection refused
```

**Root Causes**:
1. SSH service (sshd) not running on server
2. Firewall blocking port 22
3. Server is down

**Solutions**:
1. Check if server is reachable: `ping 69.62.108.82`
2. Contact hosting provider to verify SSH service status
3. Check server via Hostinger web console

### `Connection timed out`

**Symptoms**:
```
ssh: connect to host 69.62.108.82 port 22: Connection timed out
```

**Root Causes**:
1. Server firewall blocking connections
2. Network firewall/proxy blocking port 22
3. Server is down
4. Wrong IP address

**Solutions**:
1. Verify IP address: `nslookup srv759970.hstgr.cloud`
2. Test from different network
3. Check Hostinger control panel for server status
4. Try using VPN if corporate firewall blocks SSH

## Authentication Errors

### `No supported authentication methods available`

**Symptoms**:
```
debug1: No more authentication methods to try.
Permission denied (publickey).
```

**Root Cause**: Server requires public key authentication but client has no valid keys.

**Solutions**:
1. Generate new SSH key: `ssh-keygen -t ed25519 -C "your-email@example.com"`
2. Add public key to server via Hostinger control panel
3. Test with password authentication (if enabled): `ssh -o PreferredAuthentications=password automation@69.62.108.82`

### `Too many authentication failures`

**Symptoms**:
```
Received disconnect from 69.62.108.82: Too many authentication failures
```

**Root Cause**: ssh-agent offering too many keys, server rejects after 5 attempts.

**Solutions**:
1. Use `IdentitiesOnly yes` in SSH config:
   ```
   Host srv759970
     HostName 69.62.108.82
     User automation
     IdentityFile ~/.ssh/id_ed25519
     IdentitiesOnly yes
   ```

2. Or specify key explicitly: `ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes automation@69.62.108.82`

## Key Format Errors

### `invalid format`

**Symptoms**:
```
Load key "id_ed25519": invalid format
```

**Root Causes**:
1. Key file corrupted
2. Wrong file (public key instead of private)
3. File encoding issue (Windows line endings)

**Solutions**:
1. Verify it's the private key (no `.pub` extension)
2. Check file starts with `-----BEGIN OPENSSH PRIVATE KEY-----`
3. Regenerate key if corrupted
4. Convert line endings: `dos2unix ~/.ssh/id_ed25519`

## Windows-Specific Issues

### Inherited Permissions

**Symptom**: Connection worked before, fails after Windows update or file move.

**Root Cause**: Windows reapplied inherited permissions from parent folder.

**Solution**: Run `scripts/fix-ssh-permissions.ps1` after any Windows update.

### Git Bash vs PowerShell

**Issue**: `chmod 600` in Git Bash doesn't properly set Windows ACLs.

**Solution**: Always use PowerShell script for permission fixes on Windows.

### OneDrive Sync

**Symptom**: SSH keys in OneDrive-synced folders may have permission issues.

**Solution**:
1. Move SSH keys to non-synced location: `C:\Users\username\.ssh`
2. Exclude `.ssh` folder from OneDrive sync
3. Fix permissions with PowerShell script

### TinyWall Firewall Blocking SSH

**Symptom**:
- `Permission denied` error at connection level (before authentication)
- `Test-NetConnection -Port 22` shows `TcpTestSucceeded : False`
- Worked previously, suddenly stopped working

**Root Cause**: TinyWall firewall is blocking outbound SSH connections on port 22.

**Diagnostic**:
```powershell
Test-NetConnection -ComputerName 69.62.108.82 -Port 22
```
If `TcpTestSucceeded : False`, firewall is likely blocking.

**Solution**:

**Option 1: Add exception (recommended)**
1. Open TinyWall tray icon
2. Select "Manage" → "Add exception"
3. Add exception for SSH client (`C:\Windows\System32\OpenSSH\ssh.exe`)
4. Or add exception for Git Bash SSH (`C:\Program Files\Git\usr\bin\ssh.exe`)

**Option 2: Temporarily disable to test**
1. Right-click TinyWall tray icon
2. Select "Disable firewall"
3. Test SSH connection
4. Re-enable and add proper exception

**Option 3: Allow port 22 outbound**
1. Open TinyWall → "Manage"
2. Add custom rule for outbound TCP port 22

**Note**: After adding exception, no reboot required. Test immediately with:
```bash
ssh automation@69.62.108.82 "echo 'SSH OK'"
```

## Configuration Issues

### Wrong Host in Config

**Symptom**: Connection works with IP but not with alias.

**Root Cause**: SSH config file has wrong hostname or user.

**Solution**: Verify `~/.ssh/config`:
```
Host srv759970
  HostName 69.62.108.82
  User automation
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

### Multiple Config Files

**Issue**: OpenSSH checks multiple config locations, may use wrong one.

**Locations (in order)**:
1. Command-line options
2. `~/.ssh/config` (user config)
3. `/etc/ssh/ssh_config` (system config)

**Solution**: Ensure user config has correct settings and use `-F` to specify config file explicitly.

## Debugging Commands

### Verbose Connection Test

```bash
ssh -vvv automation@69.62.108.82
```

Output shows:
- Config files being read
- Keys being tried
- Authentication methods
- Connection details

### Check Key Fingerprint

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

Compare with server's authorized_keys fingerprint.

### Test Specific Key

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes automation@69.62.108.82
```

### Check SSH Config

```bash
ssh -G srv759970
```

Shows final configuration after parsing all config files.

## Quick Diagnostic Checklist

When SSH fails, check in order:

1. ✅ Network connectivity: `ping 69.62.108.82`
2. ✅ SSH service: `telnet 69.62.108.82 22` (should see SSH banner)
3. ✅ Key exists: `ls -l ~/.ssh/id_ed25519`
4. ✅ Key permissions: `Get-Acl ~/.ssh/id_ed25519` (Windows) or `ls -l` (Unix)
5. ✅ Key format: `head -1 ~/.ssh/id_ed25519` (should be `-----BEGIN OPENSSH PRIVATE KEY-----`)
6. ✅ Public key on server: Verify via Hostinger control panel
7. ✅ SSH config: `ssh -G srv759970` to see effective configuration
8. ✅ Verbose test: `ssh -vvv automation@69.62.108.82` for detailed diagnostics

If all checks pass but connection still fails, run `scripts/test-ssh-connection.ps1` for comprehensive diagnostics.
