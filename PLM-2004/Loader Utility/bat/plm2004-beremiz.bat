@echo off

:: PLM-2004
:: Loader of Berimiz application
:: 2020, lamsystems-it.ru
:: v.1.01.01


:: COM-port
set Com="COM7"


:: Other settings =====================

:: Path to stm32flash.exe
set Bin=stm32flash.exe

:: Path to build-directory
set DirBuild=build

:: COM-port baudrate
set Spd=115200

:: Start execution at specified address (0 = flash start)
REM =address
set g=0x0

:: Specify start address and optionally length in bytes for read/write/erase operations
REM =address[:length]
set S=0x08020000

:: Start ==============================

echo %date% %time%

if not exist %Bin% (
    echo Error! File %Bin% is not exists!
    @pause
    exit
)

if not exist %DirBuild% (
    echo Error! Directory %DirBuild% is not exists!
    @pause
    exit
)

:: Search hex-files in DirBuild
for /r "%DirBuild%" %%a in (*.hex) do (
    :: Load hex-file
    echo %Bin% -w %DirBuild%\%%~nxa -v -g %g% -S %S% -b %Spd% %Com%
    %Bin% -w %DirBuild%\%%~nxa -v -g %g% -S %S% -b %Spd% %Com%
    echo The Application download is completed.
    @pause
    exit
)

echo Error! The directory "%DirBuild%" has no file "*.hex".
@pause

:: Start End ==========================
