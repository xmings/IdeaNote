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

rem 定义IdeaNote的主程序文件
set IdeaNoteDir=E:\DataCarrer\Python\IdeaNote\

echo 2. 更新IdeaNote
pushd %IdeaNoteDir%
git pull
popd

echo 3. 启动IdeaNote
start /b python %IdeaNoteDir%app.py

echo IdeaNote启动成功, 准备退出
pause