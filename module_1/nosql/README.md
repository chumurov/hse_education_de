# Локальная MongoDB (локальное развёртывание через Docker)

Это минимальная конфигурация для запуска MongoDB локально в контейнере Docker и примеры подключения.

## Что добавлено

- `docker-compose.yml` — служба `mongodb` с монтированными томами и healthcheck.
- `mongo-init/init.js` — скрипт инициализации, создаёт пользователя приложения и опционально добавляет тестовые данные.
- `scripts/` — удобные скрипты:
  - `start.sh` — поднять контейнер (создаёт `.env`, если его нет)
  - `stop.sh` — остановить контейнер
  - `reset.sh` — сброс данных (удаляет `./data` и запускает контейнер заново)
  - `connect.sh` — подключиться к MongoDB внутри контейнера с `mongosh`

## Быстрый запуск

1) Убедитесь, что у вас установлен Docker (и docker compose в v2):

```bash
docker --version
docker compose version
```

2) Запустите MongoDB:

```bash
cd module_1/nosql
./scripts/start.sh
```

3) Подключение:

- Через `mongosh` внутри контейнера (подходит если у вас нет mongosh локально):

```bash
./scripts/connect.sh
```

- Локальный `mongosh` (если он у вас установлен):

```bash
# подключение к контейнеру через порт
mongosh "mongodb://root:example@localhost:27017/admin"
# подключение как app user к базе appdb:
mongosh "mongodb://appuser:apppassword@localhost:27017/appdb"
```

4) Остановить контейнер:

```bash
./scripts/stop.sh
```

5) Сброс данных (удалит ./data):

```bash
./scripts/reset.sh
```

## Примечания безопасности

- Данные в `.env` хранятся в корне репозитория для удобства разработки — **не храните** реальные пароли в этом файле при публикации в Git.
- Для production используйте секреты Docker или внешние менеджеры секретов.

## Дополнительно

- Для создания дополнительного набора данных можно расширить `mongo-init/init.js`.
- Если вы используете MongoDB в приложении, добавьте строку подключения в переменные среды вашего приложения, например `MONGO_URI=mongodb://appuser:apppassword@localhost:27017/appdb`.
