# XAMPP Error Fixer

A Windows utility for diagnosing common Apache and MySQL startup problems in XAMPP.

> **Safety note:** This project is under active improvement. Automatic MySQL data repair is disabled because the previous implementation could delete database files. The tool does not guarantee that it can repair every XAMPP installation.

## Current capabilities and limitations

- Detects XAMPP in the standard `C:\\xampp`, `D:\\xampp`, `E:\\xampp`, or `F:\\xampp` locations.
- Checks Apache's configured listening ports and can suggest alternate ports.
- Creates a timestamped backup of Apache's `httpd.conf` before changing it.
- Does **not** kill processes by executable name or stop unrelated Apache/MySQL services.
- Does **not** currently repair MySQL data files or run live service tests automatically.

The project currently expects a standard Windows XAMPP installation. Custom install paths are not discovered automatically yet.

## Requirements

- Windows 10 or 11
- XAMPP installed in one of the standard locations above
- Python 3.9 or newer to run the source script

## Run from source

1. Clone the repository:
   ```powershell
   git clone https://github.com/sumitpoudelxyz/xampp-error-fixer.git
   cd xampp-error-fixer
   ```
2. Open Command Prompt or PowerShell as Administrator if you need to inspect or edit protected Apache configuration files.
3. Run:
   ```powershell
   python "Repair Scripts\\xampp_repair.py"
   ```

The script may request elevated permissions for operations that need them. Review prompts carefully and keep your own backup of the complete XAMPP directory before making configuration changes.

## Run the batch launcher

The `xampp_fixer.bat` launcher currently expects a prebuilt executable at `Repair Scripts\\dist\\xampp_repair.exe`. If that executable is not present in your checkout, use the Python source instructions above. The batch launcher and packaged distribution are being aligned.

## Tests

The automated tests use temporary directories and mocked operating-system commands; they do not require an XAMPP installation and do not modify real database files.

Install the test dependency and run:

```powershell
python -m pip install pytest
python -m pytest -q
```

## Reporting a problem

Please open a GitHub issue and include:

- Windows version and XAMPP version
- Whether XAMPP is installed in a standard location
- The exact error message (remove passwords, tokens, and private paths)
- Relevant Apache or MySQL log excerpts, with sensitive information removed

## Safety and project status

This is community-maintained software and is provided without a guarantee of successful repair. Do not run repair utilities against your only copy of important data. Back up databases and configuration files before troubleshooting.
