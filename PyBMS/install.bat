:: Copyright (c) 2022 Analog Devices, Inc. All Rights Reserved.
:: This software is proprietary to Analog Devices, Inc. and its licensors.

IF NOT EXIST venv\Scripts\python.exe (
    echo "VENV not found, setting up Virtual Environment"
    CALL C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\Scripts\pip.exe install virtualenv
    IF %ERRORLEVEL% NEQ 0 pip install virtualenv
    CALL C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe -m virtualenv venv
    IF %ERRORLEVEL% NEQ 0 python -m virtualenv venv
    CALL .\venv\Scripts\activate.bat
    pip install ADI_pyBMS_gen6-2.0.7-py3-none-any.whl
    deactivate
) ELSE (
    echo "VENV found, Check if all packages are installed"
    CALL .\venv\Scripts\activate.bat
    pip install -r requirements.txt
)