# Stepic_project_312
Engineering workshop. 312 group 1st course MIPT. API Stepic project.



# Usage(демки на момент 06.05)
На данный момент существует 4 сценария использования
* **load** --- загружает файлы курса в файлы расширения yaml, для дальнейшей работы с самим курсом
* **add** --- позволяет добавить элемент в урок или секцию в курса с помощью урока описанного, в .md или .gift
* **update** --- позволяет обновить урок в курсе с помощью урока описанного, в .md или .gift
* **struct** --- позволяет увидеть структуру курса
в примерах будет использоваться написание флагов `-C=a.yaml`,  но вы можете использовать любые удобные вам (например: `-C a.yaml`, `-C="a.yaml"`) 
## load

* `--course, -С`  --- данный флаг указывает название файла, в который будет записан курс
* `--id, -i`  --- данный флаг указывает id курса степика
	> Например в "https://stepik.org/course/73/syllabus" --id=73

Пример:
```
prog load -C=a.yaml -i=73 
```
## add

* `--course, -С`  --- данный флаг указывает название файла, в который будет записан курс
* `--section, -S`  --- данный флаг отвечает за индекс секции
* `--lesson, -L`  --- отвечает за индекс урока
* `--step, -s` --- отвечает за индекс степа
* `--md, -m` --- файл .md откуда данные должны быть взяты
* `--gift, -g` --- файл .gift откуда данные должны быть взяты
* `--title, -t` --- если вы хотите создать новый урок, то этот флаг задаст его название
* `--no-ask, -n` --- при наличии у вас не будут просить подтверждения ваших действий
Пример:
```
prog add -C=a.yaml -S=1 -L=0 -s=1 --gift=example.gift 
```
## update
(Близок к **add**)
* `--course, -С`  --- данный флаг указывает название файла, в который будет записан курс
* `--section, -S`  --- данный флаг отвечает за индекс секции
* `--lesson, -L`  --- отвечает за индекс урока
* `--step, -s` --- отвечает за индекс степа
* `--md, -m` --- файл .md откуда данные должны быть взяты
* `--gift, -g` --- файл .gift откуда данные должны быть взяты
* `--no-ask, -n` --- при наличии у вас не будут просить подтверждения ваших действий
Пример:
```
prog load -C=a.yaml -S=1 -L=0 -s=1 --gift=example.gift 
```
## struct
* `--course, -С`  --- данный флаг указывает название файла, из который будет считан курс
Пример
```
prog struc -C=a.yaml  
```

To build the table, run the file "start.py". Specify the class number as the first argument. The second argument indicates the need to update (or write for the first time) data about the class (True if needed else False). If you have file "Session_information.txt" with client_id and client_secret, don't write enything else. Otherwise third argument would be client_id and forth - client_secret, both type string