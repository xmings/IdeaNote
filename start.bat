@echo off
echo   /$$$$$$       /$$                     /$$   /$$             /$$
echo  ^|_  $$_/      ^| $$                    ^| $$$ ^| $$            ^| $$              
echo    ^| $$    /$$$$$$$  /$$$$$$   /$$$$$$ ^| $$$$^| $$  /$$$$$$  /$$$$$$    /$$$$$$ 
echo    ^| $$   /$$__  $$ /$$__  $$ ^|____  $$^| $$ $$ $$ /$$__  $$^|_  $$_/   /$$__  $$
echo    ^| $$  ^| $$  ^| $$^| $$$$$$$$  /$$$$$$$^| $$  $$$$^| $$  \ $$  ^| $$    ^| $$$$$$$$
echo    ^| $$  ^| $$  ^| $$^| $$_____/ /$$__  $$^| $$\  $$$^| $$  ^| $$  ^| $$ /$$^| $$_____/
echo   /$$$$$$^|  $$$$$$$^|  $$$$$$$^|  $$$$$$$^| $$ \  $$^|  $$$$$$/  ^|  $$$$/^|  $$$$$$$
echo  ^|______/ \_______/ \_______/ \_______/^|__/  \__/ \______/    \___/   \_______/
echo ׼������IdeaNote,���Ժ�...
echo=
echo 1. �ر�IdeaNote
wmic process where "CommandLine like '%%IdeaNote%%' and name='python.exe'" call terminate
echo=

rem ����ʼ�Ŀ¼
set NoteDir=E:\MyNote

rem �������˿�
set Port=5555

rem ����IdeaNote���������ļ�
set IdeaNoteDir=E:\DataCarrer\IdeaNote\

echo 2. ����IdeaNote
pushd %IdeaNoteDir%
git pull
popd

echo 3. ����IdeaNote
start /b python %IdeaNoteDir%app.py %Port% %NoteDir%

echo IdeaNote�����ɹ�, ׼���˳�
pause