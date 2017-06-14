@echo off
set d=%date:~0,10%
set t=%time:~0,8%
set timestamp=%d% %t%

git status

set /p comments=please input commit comments:

git status
git add .
git commit -m "%timestamp% %comments%"
git push origin PyCTP_Dev
echo "Finished Push!"
pause