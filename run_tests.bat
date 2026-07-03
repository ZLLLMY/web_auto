@echo off
REM 设置环境变量
set JAVA_HOME=C:\jdk-21.0.11.10-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%

REM 激活虚拟环境
call web_test\Scripts\activate.bat

REM 运行测试
python Runner.py %*

pause
