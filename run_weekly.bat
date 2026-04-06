@echo off
cd /d "E:\Himanshu Work\Automation"
python scripts/run.py --ai
echo Weekly job completed at %date% %time% >> .tmp/scheduler.log