@echo off
echo Iniciando o Network Sentinel v1.2...

:: Inicia o Backend em uma nova janela
start cmd /k "cd backend && python -m uvicorn main:app --reload"

:: Inicia o Frontend em uma nova janela
start cmd /k "cd frontend && npm start"

echo Sistema carregando...
pause