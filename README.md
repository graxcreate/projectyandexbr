В репозитории представлен такой набор файлов, как:
1) siriusglobal.py - основная программа, в которой создается API
   - в этой программе используются следующие библиотеки Python:
       - fastapi
       - pydantic
       - os
       - requests
       - logging
       - moviepy
       - speech_recognition
       - transformers
       - uvicorn
2) postreq.py - программа для обращения с запросом к API (P.S. - для запроса к API нужен TOKEN пользователя как входящий аргумент для работы с диском, чтобы его получить следуйте инструкциям в файле howtogettoken.md)
3) howtogettoken.md - простая инструкция по получению TOKEN'а пользователя для работы с Яндекс диском
