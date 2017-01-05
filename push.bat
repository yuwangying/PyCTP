set d=%date:~0,10%
set t=%time:~0,8%
set timestamp=%d% %t%

git add .
git commit -m "%timestamp% backup from windows"
git push origin PyCTP_Dev
echo "Finished Push!"
pause