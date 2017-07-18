import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "queue", "idna"],
    "includes": ["data", "config"],
    "excludes": ["tkinter"]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="SonarIssues",
    version="1.0",
    description = "Aplicación que genera informes de incidencias de Sonar",
    options = {"build_exe": build_exe_options},
    executables = [Executable("SonarIssues.py", base = base)])