# Область видимости

lesson = 588212

## TEXT Something what I made up right now

And some bullshit right here, oh yea.1

## QUIZ BALAS

TEXTBEGIN
A. `DWQE`
HINT:SDOWJ
B. `WQDOJW`
C.`WDWWQ`
TEXTEND

A. `ujn`
HINT: DWPQKEDW
B. `dwosqwmsdowqk`
HINT: Nope

SHUFFLE: false
ANSWER: A


## CHOICE Сравнение указателей

Еще один желаемый формат вопроса. Для размышлений.

Как проверить, что `s` и `p` указывают на одну и ту же область памяти?

+) `s == p`
HINT: молодец

-) `*s == *p`
HINT: значения ты сравнил, а адреса кто будет сравнивать?

-) `s[0] == p[0]`

-) `strcmp(s, p)`

-) `strcmp(s, p) == 0`

SHUFFLE: false
HINT: общая подсказка

## TASKINLINE Работа со словарем

Купили фрукты. Сделали словарь фрукт (ключ) и цена за 1 килограмм (значение).

Допишите код:

CODE
import json

# создаем словарь
fruit = {
    'apple': 50,
    'banana': 90,
    'orange': 60,
    'grape': 100,
    'mango': 110
}
# печатаем словарь
print(fruit)

# lemon стоит 120 рублей за 1 кг

# есть дешевые бананы 67 рублей за 1 кг, запомним их

# удалим из словаря mango

# яблоки apple стали на x рублей дороже
x = int(input())

# печатаем словарь

# печатаем словарь красиво

TEST
11
----
{'apple': 50, 'banana': 90, 'orange': 60, 'grape': 100, 'mango': 110}
{'apple': 61, 'banana': 67, 'orange': 60, 'grape': 100, 'lemon': 120}
{
    "apple": 61,
    "banana": 67,
    "orange": 60,
    "grape": 100,
    "lemon": 120
}
====