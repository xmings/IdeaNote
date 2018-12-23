rem 指定笔记文件存储目录
set NoteDir=E:\MyNote

rem 指定笔记服务监听端口
set Port=5555

rem 指定笔记服务主程序
set NoteApp=E:\Source\Python\IdeaNote\app.py

rem 后台运行笔记服务
start /min python %NoteApp% %Port% %NoteDir%