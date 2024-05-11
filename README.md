# Stepic_project_312
Engineering workshop. 312 group 1st course MIPT. API Stepic project.

> [!IMPORTANT]
> Create API application at [Stepic API application](https://stepik.org/oauth2/applications/): `client type - confidentional`, `autorization grant type - client credentials` , otherwise you won't be able to work in net. Later, you need to use `client id` and `client secret` from it.

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
	> Например в <https://stepik.org/course/73/syllabus> --id=73

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


# Usage of Classes from src/API/

There are 4 main classes: `Course`, `Section`, `Lesson` and all types of `Step`
Every class has these methods:
* **send()** --- send object's changes (create/update/delete) to *Stepik.org* 
	(**send_all()** for `Course`)
* **save()** --- save your object to root/your directory. Original file's type - **yaml**
* **dict_info()** --- return your object in dictionary view
* **load_from_net()** --- fill object with information from *Stepic.org* by it's id
* **delete_network()** --- dangerous deleting object from Stepik.org without checks
* **load_from_dict()** --- fill object with information from dictionary
* **load_from_file()** --- fill object with information from file
* **add_*****object*****()** --- add child object inside
* **delete_*****object*****()** --- mark to delete child object. Locally, before **send()**, nothing will happen.
* **get_structure()** --- return simplified **dict_info()**. (Except for `Step`)

and these fields:
* **id** --- *None* before sending
* **title** --- even for `Step` - just for convenient managing
* **params** --- dictionary of extended parameters, such as **description** for `Course` and `Section`

Every object, except for `Step`, has field with child objects:
* **sections** --- for `Course`
* **units** --- for `Section` (every unit stores lesson)
* **steps** --- for `Lesson`

## Child containig fields

From `Course`, the main parent object, you can get the `Step`, the smallest child object along the following path:
```
step = course.sections[i].units[j].lesson.steps[k]
```
So, using this path, you can change objects' order.

## OAuthSession

Every method, connecting with server accepts **OAuthSession**.
This class exists for autorization at Stepic.org.
### Stepic API application
Create your application with [Stepic API application](https://stepik.org/oauth2/applications/) --- `client type - confidentional`, `autorization grant type - client credentials`
First initialization OAuthSession accepts your **client_id** and **client_secret**. Next time, it will be saved, so can be called simplier, for example:
```
a.send(session = OAuthSession())
```

For `Course`, for convenient managing, you can tie session with **auth()** method:
```
a.auth(OAuthSession())
```
After that, you don't have to pass session to every net-connecting method.

## Load_from_net()
Flags:
* **source** --- load all steps' information. Without this flag you can't add new steps, but requests are easier, and files stores only step's ids

## Save()
Flags:
* **copy** --- delete all id's. With it you can easily copy every object, without linking it to the source
* **filename** --- save your object to specified directory with specified type.
>  For **Course**: all included lessons will be saved to the same directory, as the main file

## Send()

This method send itself, and all objects inside. If something went wrong, it will stop return a response of problem object.

For example, if I created incorrect step, this code:
```
return course.send_all()
```
will be equal to 
```
return problem_step.send()
```
and all next objects won't be sent.

## Delete_network()

Dangerous deleting object from *Stepic.org* without any checks. It's better to use this method withoud parenting objects: for them nothing will happened, that can cause to wrong objects managing.

It's better to use:
## Delete_*object*()
This method mark object inside to delete (or remove for Lessons).
Local changes will happen only after **send()** method.
> Warning: remember about unchanging indexing before sending.

For `Lesson`: it can be untied from `Section` with parent object's **remove_lesson()** method.
