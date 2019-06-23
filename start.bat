@echo off
echo   /$$$$$$       /$$                     /$$   /$$             /$$
echo  ^|_  $$_/      ^| $$                    ^| $$$ ^| $$            ^| $$              
echo    ^| $$    /$$$$$$$  /$$$$$$   /$$$$$$ ^| $$$$^| $$  /$$$$$$  /$$$$$$    /$$$$$$ 
echo    ^| $$   /$$__  $$ /$$__  $$ ^|____  $$^| $$ $$ $$ /$$__  $$^|_  $$_/   /$$__  $$
echo    ^| $$  ^| $$  ^| $$^| $$$$$$$$  /$$$$$$$^| $$  $$$$^| $$  \ $$  ^| $$    ^| $$$$$$$$
echo    ^| $$  ^| $$  ^| $$^| $$_____/ /$$__  $$^| $$\  $$$^| $$  ^| $$  ^| $$ /$$^| $$_____/
echo   /$$$$$$^|  $$$$$$$^|  $$$$$$$^|  $$$$$$$^| $$ \  $$^|  $$$$$$/  ^|  $$$$/^|  $$$$$$$
echo  ^|______/ \_______/ \_______/ \_______/^|__/  \__/ \______/    \___/   \_______/
echo ???????IdeaNote,?????...
echo=
echo 1. ???IdeaNote
wmic process where "CommandLine like '%%IdeaNote%%' and name='python.exe'" call terminate
echo=
echo 2. ????IdeaNote
git pull origin

rem ????????
set NoteDir=E:\MyNote

rem ?????????
set Port=5555

rem ????IdeaNote???????????
set NoteApp=E:\Source\Python\IdeaNote\app.py

echo 3. ????IdeaNote
start /b python %NoteApp% %Port% %NoteDir%

echo IdeaNote???????, ??????
pause