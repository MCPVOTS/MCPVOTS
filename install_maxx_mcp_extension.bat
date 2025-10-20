@echo off
echo Installing MAXX MCP Memory Extension for VSCode...

cd maxx-mcp-extension

echo Installing npm dependencies...
call npm install

echo Compiling TypeScript...
call npm run compile

echo Creating VSIX package...
call npx vsce package

echo Installation complete!
echo To install the extension, run:
echo code --install-extension maxx-mcp-extension-0.0.1.vsix

pause