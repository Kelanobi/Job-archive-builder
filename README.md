# Qualitrol Job Archive

A small Windows utility that validates a job's Despatch Checklist, extracts its customer name, and creates one genuine `.lnk` shortcut to the original network job folder.

## Run from source

Requires Windows and Python 3.11 or later.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python main.py
```

Deployment paths are deliberately kept out of the interface. The source path is configured as `NETWORK_ROOT` in `config.py`. The Kelvin build writes under `C:\Users\kelvin.obi\OneDrive - Ralliant\Job files`; the Afeez build writes under `C:\Users\Afeez.Sotannde\OneDrive - Ralliant\Job files`. The packaged filename selects the appropriate profile.

## Test

```powershell
python -m pytest -q
```

Tests use temporary directories and generated selectable-text PDFs; they never write to the configured network path.

## Build the executable

Run `build\build_exe.bat`. The standalone, console-free executable is written to `dist\Qualitrol Job Archive.exe`.
The window and executable use the isolated Qualitrol **Q** mark from `assets\branding\qualitrol-q.ico`.

Use `build\build_kelvin_exe.bat` or `build\build_afeez_exe.bat` for the two user-specific builds.

Before deployment, test on a machine where the `S:` mapping and configured OneDrive path are available. For each job, the app creates a folder named `{job number} - {customer}` and places an identically named shortcut inside it. Both the base folder and job folder are created automatically when absent.

Technical errors are logged under `%LOCALAPPDATA%\Qualitrol Job Archive\logs\app.log`; customer data is not stored in a database and no network content is modified.
