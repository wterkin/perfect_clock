@echo off
pause
C:\langs\python\env\esp\Scripts\esptool.exe --port COM4 -baud 460800 write_flash --flashsize=detect 0 %1 