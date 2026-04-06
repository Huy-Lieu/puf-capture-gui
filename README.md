# PUFResponses (RealTerm Capture Controller)

This project provides a small **Tkinter GUI** to control **RealTerm** (via COM) and capture serial output to files with consistent naming.

## Prerequisites

- Windows
- RealTerm installed (COM object: `Realterm.RealtermIntf`)
- Python 3.x

## Setup

Create/activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run (GUI)

From the repo root:

```powershell
.\.venv\Scripts\Activate.ps1
python .\run_gui.py
```

You can also run the older entrypoint:

```powershell
python .\RealTermControllerUI.py
```

## Notes

- The main GUI lives in `ui/main_window.py`.
- Legacy/experimental scripts were moved into `scripts/legacy/`.

