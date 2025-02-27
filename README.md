taskkill /IM ollama.exe /F
set OLLAMA_HOST=0.0.0.0:11434
ollama serve
-----------------------------------------------
powershell.exe "ipconfig | findstr IPv4"
export OLLAMA_HOST="http://172.20.128.1:11434"