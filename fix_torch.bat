@echo off
echo Desinstalando PyTorch...
C:/Users/hugod/jupyter-ai/python.exe -m pip uninstall -y torch torchvision torchaudio

echo.
echo Instalando PyTorch CPU version...
C:/Users/hugod/jupyter-ai/python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Instalacion completada!
pause
