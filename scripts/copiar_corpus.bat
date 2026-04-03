@echo off
REM ═══════════════════════════════════════════════════════
REM CecilIA v2 — Copiar Corpus de BaseConocimiento
REM Contraloria General de la Republica de Colombia
REM ═══════════════════════════════════════════════════════
REM
REM Uso: scripts\copiar_corpus.bat
REM
REM Copia los documentos desde C:\Users\ThinPad X1\Documents\CGR\BaseConocimiento
REM hacia la carpeta corpus/ con los nombres de coleccion esperados por el sistema.
REM ═══════════════════════════════════════════════════════

set ORIGEN=C:\Users\ThinPad X1\Documents\CGR\BaseConocimiento
set DESTINO=%~dp0..\corpus

echo.
echo ===================================================
echo  CecilIA v2 — Copiando Corpus Documental
echo ===================================================
echo.
echo Origen:  %ORIGEN%
echo Destino: %DESTINO%
echo.

if not exist "%ORIGEN%" (
    echo ERROR: No se encontro el directorio origen: %ORIGEN%
    echo Verifique que la ruta es correcta.
    exit /b 1
)

REM Crear directorio destino
if not exist "%DESTINO%" mkdir "%DESTINO%"

REM Mapeo: directorio origen -> nombre coleccion
call :copiar "01_normativo"       "normativo"
call :copiar "02_institucional"   "institucional"
call :copiar "03_academico"       "academico"
call :copiar "04_tecnico_tic"     "tecnico_tic"
call :copiar "05_estadistico"     "estadistico"
call :copiar "06_jurisprudencial" "jurisprudencial"
call :copiar "07_auditoria"       "auditoria"

echo.
echo ===================================================
echo  Copia completada.
echo ===================================================
echo.
echo Para ingestar el corpus en la base vectorial:
echo   docker compose exec backend python -m scripts.ingest_corpus
echo.
exit /b 0

:copiar
set DIR_ORIGEN=%ORIGEN%\%~1
set DIR_DESTINO=%DESTINO%\%~2
if exist "%DIR_ORIGEN%" (
    echo Copiando %~1 -^> %~2 ...
    if not exist "%DIR_DESTINO%" mkdir "%DIR_DESTINO%"
    xcopy /E /Y /Q "%DIR_ORIGEN%\*" "%DIR_DESTINO%\" >nul 2>&1
    echo   OK
) else (
    echo AVISO: No se encontro %DIR_ORIGEN%, se omite.
)
goto :eof
