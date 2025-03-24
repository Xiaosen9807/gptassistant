@echo off
set current_dir=%cd%
echo The address is: %current_dir%
@REM python %current_dir%\test.py
python %current_dir%\scripts\main.py --function completion -fc "%current_dir%\notes.txt" -fs "%current_dir%\system.txt" -s "openai"
pause