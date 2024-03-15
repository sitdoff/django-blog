# Коллективный блог

## Что это?

Это коллективный блог, в котором пользователю может быть назначена определенная роль, в зависимости от которой у него будет определенный функционал.
Роли присваиваются путем переключения булевых значений записи пользователя в базе данных.

Все функции для пользователей с различными ролями реализованы через взаимодействие с основным сайтом и не требуют доступа в кабинет администратора.

В данный момент реализованы следующие роли:

-   `user` - Обычный пользователь, которому не присвоены никакие роли. Не имеет возможности как либо влиять на контент сайта, кроме как оставлять комментарии под статьями.
-   `author` - Автор статей. Может создавать черновики статей и отсылать их на модерацию редакторам. Как только автор считает статью готовой, он меняет её статус
    и она уходит на рассмотрение редактору. Автор может удалить свой черновик. С момента снятия статуса черновика автор не имеет доступа к статье. Автор имеет доступ
    к только к своим черновикам.
-   `staff` - Редактор с доступом к статьям, представленным на модерацию. Редактор может просматривать представленные авторами статьи и брать на редактирование те,
    которые ему интересны. После того, как редактор взял статью, она закрепляется за ним и становится невидна остальными редакторам.Редактор может вносить правки
    в неопубликованные статьи на свое усмотрение,опубликовать статью на сайте, либо же может вернуть статье статус черновика. В последнем случае статья возвращается
    в список черновиков автора. В случае публикации статья начинает отображаться в общем списке статей и обычные пользователи получают к ней доступ и могут оставлять
    комментарии.
-   `authorstaff` - Комбинация ролей, которая дает возможность пользователю пользоваться всеми функциями автора и редактора.

## Особенности проекта

-   Реализована система подписок, дающая возможность пользователю отслеживать посты определенных авторов.
-   Отправка писем при регистрации и изменении статуса статьи реальзована асинхронно с помощью Celery+Redis.
-   Используется расширенный класс пользователя на основе класса AbstractUser.
-   В процессе реализации проекта были созданы миксины, регулирующие доступ к разделам сайта, на основе стандартных.
-   Была реализована частично динамическая форма редактирования поста, в которой поведение при сохранении зависит от выбранного статуса статьи.
-   Функции сайта максимально покрыты тестами.
-   В качестве встроенного в формы редактора был использован [django-ckeditor](https://github.com/django-ckeditor).
-   Для создания слагов использована библиотека [python-slugify](https://pypi.org/project/python-slugify/)
-   ВНИМАНИЕ! Письма сохраняются в файлы в папке emails. Ищите их там.
-   На фронте был использован [Neuron template](https://www.tooplate.com/view/2085-neuron)

## Запуск

Сейчас запуск проекта возможен с использованием Docker Compose.

Для того, чтобы запустить проект локально, вам надо выполнить следующee:

1. Склонировать репозиторий

```bash
git clone https://github.com/sitdoff/django-blog.git
```

2. Перейти в папку склонированного проекта, создать файл `.env` и заполнить его данными. Пример файла присутствует в проекте и называется `.env_example`.

3. Выполнить команду

```bash
docker compose up --build
```

Все необходимые контейнеры будут созданы и заполнены автоматически. При первом запуске будут применены миграции к базе данных, а так же будет создан суперпользователь
с данными, которые были указаны в файле `.env`. Так же будут созданы демонстрационные учетные записи для каждой из ролей с данными `<имя роли>:test_password`, то есть
для роли `authorstaff` данные для входа будут:

```
login: authorstaff
password: test_password
```

После успешного запуска, сайт станет доступен по адресу http://localhost:8000/.

## Обновления

Проект периодически обновляется, добавляются небольшие улучшения.
