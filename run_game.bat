@echo off
setlocal
pushd "%~dp0"

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    echo Python venv not found at .venv\Scripts\python.exe
    echo Please create/activate the venv first.
    pause
)

popd
endlocal
