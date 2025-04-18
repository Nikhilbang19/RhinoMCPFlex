@echo off
echo ===== RhinoMCP Installation Script =====
echo.

echo Installing Python dependencies...
pip install -r rhino_mcp/requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies! Please check your Python installation.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo Installing RhinoMCP package in development mode...
cd rhino_mcp
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo Error installing RhinoMCP package! Please check your Python installation.
    cd ..
    pause
    exit /b 1
)
cd ..
echo RhinoMCP package installed successfully.
echo.

echo ===== Installation Complete =====
echo.
echo To use RhinoMCP:
echo 1. Start Rhino and run rhino_mcp_client.py in the Rhino Python editor
echo 2. Configure Claude Desktop using the instructions in the README
echo.
echo Press any key to exit...
pause > nul 