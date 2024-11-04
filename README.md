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

Важная информация:
1) Для корректной работы программы файлы siriusglobal.py и postreq.py должны находиться в одной папке
2) Также для корректной работы программы должны быть установлены все библиотеки, перечисленные в описании файла siriusglobal.py выше
3) Программа взаимодействует только с видео формата .mp4
4) По результату выполнения программы будет создана папка extracted_audio, содержащая видео, скачанные с диска, извлеченные из них аудиодорожки в формате .wav и их транскрипции в формате .txt
