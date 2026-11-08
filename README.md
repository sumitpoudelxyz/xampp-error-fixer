# 🔧 XAMPP Error Fixer

A powerful Windows tool that automatically detects and fixes common XAMPP issues with just one click!

## ✨ Core Features

- **🔍 Auto-Detection**: Automatically finds your XAMPP installation
- **🛠️ Smart Fixes**: Resolves MySQL "stopped unexpectedly" errors
- **🚪 Port Management**: Handles Apache port conflicts (80, 443, etc.)
- **📦 Safe Backups**: Creates backups before making any changes
- **🎯 One-Click Solution**: Fix multiple issues with a single run

## 🚀 Quick Start


### Option 1: Run Python Script (Make sure to have python and pip installed)-Recommended
**Check if both python and pip is available or not**
```bash
    python --version && pip --version
```
**Install xamppfixer through pip**
```bash
    pip install xamppfixer
```
**Run it**
```bash
    xfix
```

### Option 2: Run the EXE (Recommended)
 
```bash
    git clone https://github.com/sumitpoudelxyz/xampp-error-fixer
```

```bash
    cd xampp-error-fixer/
```

```bash
    xampp_fixer.bat
```

1. **Open Terminal**
2. **Follow** `the on-screen prompts`
3. **Done!** `Your XAMPP should be working`



### Option 3: Run Python Script (Make sure to have python installed)
- **Python installation checker**
```bash
    python --version
```
- **Download or clone the folder again if not Downloaded before**
1. **Open** `Command Prompt as Administrator`
```bash 
    git clone https://github.com/sumitpoudelxyz/xampp-error-fixer
```
```bash
    cd xampp-error-fixer
```
```bash
    cd "Repair Scripts"
```
 **Run**: `python xampp_repair.py`
 ```bash
    python xampp_repair.py
```


## 🎯 What It Fixes

| Problem | Solution |
|---------|----------|
| ❌ MySQL won't start | Repairs database files |
| ❌ Apache port conflicts | Finds free ports or stops conflicting services |
| ❌ "MySQL stopped unexpectedly" | Restores from backup database |
| ❌ Services keep crashing | Cleans corrupted configuration |

## 📋 Requirements

- **Windows 10/11** (Windows 8.1+ supported)
- **XAMPP installed** on C:, D:, E:, or F: drive

## 🛡️ Safety Features

- ✅ Creates automatic backups
- ✅ Non-destructive fixes
- ✅ Preserves your databases
- ✅ Clean rollback options

## 📖 How to Use

1. **Close XAMPP** Control Panel completely
2. **Run** `xampp_fixer.exe` 
3. **Let it diagnose** your XAMPP installation
4. **Choose fixes** when prompted
5. **Open XAMPP** Control Panel and start services

## 💡 Pro Tips

- Close XAMPP Control Panel before running
- Keep the generated backups safe
- Test your websites after fixing

## 🆘 Common Issues

**"Access Denied"** → Run as Administrator  
**"XAMPP Not Found"** → Install XAMPP in standard location  
**"Port Still Busy"** → Restart your computer and try again

## 📞 Support

If you encounter any issues:
1. Ensure XAMPP is properly installed
2. Try restarting your computer
3. Create an issue on GitHub with error details

---

**⚡ Made for the XAMPP community**

*Fix your XAMPP errors in seconds, not hours!*
