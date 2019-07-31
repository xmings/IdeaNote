@echo off
echo   /$$$$$$       /$$                     /$$   /$$             /$$
echo  ^|_  $$_/      ^| $$                    ^| $$$ ^| $$            ^| $$              
echo    ^| $$    /$$$$$$$  /$$$$$$   /$$$$$$ ^| $$$$^| $$  /$$$$$$  /$$$$$$    /$$$$$$ 
echo    ^| $$   /$$__  $$ /$$__  $$ ^|____  $$^| $$ $$ $$ /$$__  $$^|_  $$_/   /$$__  $$
echo    ^| $$  ^| $$  ^| $$^| $$$$$$$$  /$$$$$$$^| $$  $$$$^| $$  \ $$  ^| $$    ^| $$$$$$$$
echo    ^| $$  ^| $$  ^| $$^| $$_____/ /$$__  $$^| $$\  $$$^| $$  ^| $$  ^| $$ /$$^| $$_____/
echo   /$$$$$$^|  $$$$$$$^|  $$$$$$$^|  $$$$$$$^| $$ \  $$^|  $$$$$$/  ^|  $$$$/^|  $$$$$$$
echo  ^|______/ \_______/ \_______/ \_______/^|__/  \__/ \______/    \___/   \_______/
echo 准备启动IdeaNote,请稍后...
echo=
echo 1. 关闭IdeaNote
wmic process where "CommandLine like '%%IdeaNote%%' and name='python.exe'" call terminate
echo=

rem 定义笔记目录
set NoteDir=E:\MyNote

rem 定义服务端口
set Port=5555

rem 定义IdeaNote的主程序文件
set IdeaNoteDir=E:\DataCarrer\IdeaNote\

echo 2. 更新IdeaNote
pushd %IdeaNoteDir%
git pull
popd

echo 3. 启动IdeaNote
start /b python %IdeaNoteDir%app.py %Port% %NoteDir%

echo IdeaNote启动成功, 准备退出
pause