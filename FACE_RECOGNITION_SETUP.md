# Face Recognition Setup Guide (Windows)

This guide covers installation and environment setup for:
- Visual Studio Build Tools (C++ workload)
- CMake
- Python virtualenv
- dlib (compiled with CMake)
- face_recognition
- face_recognition_models

## 1) Start with Python virtual environment

1. Open PowerShell.
2. Navigate to repo:
   ```powershell
   cd "c:\Users\Mr. Barry\Documents\gospel\church-attendance-management-system"
   ```
3. Create venv (if not already):
   ```powershell
   python -m venv .venv
   ```
4. Activate venv:
   ```powershell
   & ".\.venv\Scripts\Activate.ps1"
   ```

## 2) Install Visual Studio + CMake

1. Download "Visual Studio community" from:
   - https://visualstudio.microsoft.com/

2. Run installer and select:
   - "Desktop development with C++" workload (includes MSVC).


## 3) Ensure correct PATH for CMake

If `cmake --version` fails, add path manually (adjust for your install):

```powershell
$cmakePath = "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";" + $cmakePath, "User")
```

Close and reopen VS Code after this.

## 4) Install Python build dependencies in venv

```powershell
pip install --upgrade pip setuptools wheel
```

## 5) Install `dlib` and `face_recognition` (with CMake in PATH)

```powershell
python -m pip install dlib face_recognition
```

If `dlib` fails to build and CMake still not found, confirm locally with:

```powershell
where.exe cmake
cmake --version
```

## 6) Install `face_recognition_models`

```powershell
python -m pip install face_recognition_models
```

If installation gives `pkg_resources` error, ensure setuptools is installed:

```powershell
python -m pip install --upgrade setuptools
```

The package can optionally be installed from GitHub:

```powershell
python -m pip install git+https://github.com/ageitgey/face_recognition_models
```

## 7) Validate imports

```powershell
python -c "import face_recognition, dlib, face_recognition_models; print('OK', face_recognition.__version__, dlib.__version__, face_recognition_models.__version__)"
```

Expected output example:
`OK 1.2.3 20.0.0 0.1.0`

## 8) Configure VS Code interpreter

1. `Ctrl+Shift+P` → `Python: Select Interpreter`.
2. Choose: `c:\Users\Mr. Barry\Documents\gospel\church-attendance-management-system\.venv\Scripts\python.exe`.
3. Restart VS Code for lint/signals to reflect environment changes.

## 9) Pin versions in requirements

In `apis/requirements.txt`, add (or update):

- `dlib==20.0.0`
- `face_recognition==1.2.3`
- `face_recognition_models==0.1.0`

Then optionally sync:

```powershell
python -m pip freeze > apis\requirements.txt
```

---

## Troubleshooting

- If `ModuleNotFoundError` persists for face libraries, ensure your active interpreter is the venv location and not user/global Python.
- If `dlib` still fails with CMake not found, verify the exact PATH and that the command in a fresh shell returns a version.
- Use `python -m pip show dlib face_recognition face_recognition_models` to check install status.


## Notes
- `face_recognition` depends on `dlib` binary compilation in Windows; building can take several minutes.
- The above commands were verified in this repository environment.
