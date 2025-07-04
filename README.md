# Duality
## Описание
Duality - это 2D платформер с механикой телепортации между двумя параллельными мирами. Игрок может перемещаться между верхним и нижним миром, собирать ключи и открывать двери для прохождения уровней.

![alt text](https://github.com/DugarovBator/Hackaton/blob/main/game.jpg?raw=true)

## Особенности игры
- Два параллельных мира (верхний и нижний)
- Механика телепортации между мирами
- Система анимаций для персонажа
- Сбор предметов и взаимодействие с окружением
- Реалистичная физика (гравитация, прыжки)

## Управление
- A/D - движение влево/вправо
- Shift + A/D - бег
- S - присесть
- Пробел - прыжок
- Q/E - телепортация вниз/вверх
 -ESC - возврат в меню

## Требования
- Python 3.7+
- pygame 2.6.1

## Установка
### Windows
1. Клонируйте репозиторий:

```bash
git clone https://github.com/DugarovBator/Hackaton.git
```
```bash
cd Hackaton
```
2. Установите зависимости:
```bash
venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
3. Запустите игру:

```bash
python app.py
```

### macOS / Linux
1. Клонируйте репозиторий:

```bash
git clone https://github.com/DugarovBator/Hackaton.git
```
```bash
cd Hackaton
```
2. Установите зависимости:
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
3. Запустите игру:

```bash
python3 app.py
```

## Структура проекта
```text
duality/
├── assets/
│   ├── background.png
│   ├── doors.png
│   ├── player.png
│   ├── right_sign.png
│   └── yellow_keys.png
├── main.py
├── README.md
└── requirements.txt
```

## Авторы
- @konstantinbatorov
- @DugarovBator

## Лицензия
Проект распространяется по лицензии CC0 1.0 Universal. Подробнее в LICENSE
