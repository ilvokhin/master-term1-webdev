### Лабораторная работа по сетевому программированию #2-7

#### Задание
Вариант №6. Разработать сайт анекдотов, в котором есть следующие возможности:
- регистрация пользователей
- иерархия доступа (админ и обычный пользователь)
- управление (CRUD) анекдотами для админов
- лента анекдотов для пользователей и гостей
- управление (CRUD) тегами (для админов)
- прикрепление любого количества тегов к одному анекдоту
- избранные анекдоты
- like счетчик для каждого анекдота

#### Deploy
```
# install system dependencies
sudo apt-get install -y python python-pip python-dev couchdb git
# install python dependencies
sudo pip install Flask couchdbkit
# clone repo
git clone https://github.com/r3t/master-term1-webdev.git
cd master-term1-webdev/lab2
# init database views
python init_db.py
# run app
python funny.py
```

#### Автор
Ильвохин Дима

