![Django-app workflow](https://github.com/freemirror/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Проект представляет из себя REST API модуль к социальной сети YaMDb. 
Позволяет через различные приложения, http запросы просматривать отзывы на произведения разных категорий и жанров, коментарии к ним и их рейтинг внутри проекта.
Проект YaMDb не содержит самих произведений.
Так же авторизованным пользователям предоставляется возможность оставлять отзывы коментарии к произведениям и указывать свою оценку, а так же удалять и изменять свой контент.
Получение доступа по токену реализовано чрезе библиотеку default_token_generator.

### Запуск приложения в контейнерах(локально):

1) Клонировать репозиторий и перейти в корневую папку.
Находясь в корневой папке проекта ввести в терминале(Bash) команду
```
git clone git@github.com:freemirror/yamdb_final.git
```
2) Вводим пароль и переходим в появившуюся папку с проектом, введя команду.
```
cd yamdb_final
```

3)Далее переходим в папку infra 

```
cd infra/
```
4) Создаем в ней файл .env с переменными окружения необходимыми для работы приложения
Пример заполнения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

5)Далее запускаем docker-compose:
```
docker-compose up -d
```

6) Далее внутри контейнера web выполняем миграции, создаем суперпользователя и собираем статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
```

Проект доступен по адресу: 
http://localhost/

Остановка контейнеров:

docker-compose stop

Запуск контейнеров:

docker-compose start


Для приложения настроено Continuous Integration и Continuous Deployment.
При пуше изменений в репозиторий на github проиходит:
- Проверка кода на соответствие стандартам PEP8
- Запуск pytest и прохождение тестов
- Сборка и доставка докер-образа для контейнера web на Docker Hub
- Автоматический деплой проекта на боевой сервер
- Отправка уведомления в Telegram о том, что процесс деплоя успешно завершился
