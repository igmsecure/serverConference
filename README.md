### serverConference

### Репозиторий по курсу «Разработка Интернет-Приложений»

---

#### Практическиая работа №2

---

Предметная область — `Сайт конференции`. `Услуги` - авторы статей, `заявки` - заявка на публикацию статьи

---

- **Цель работы**: разработка структуры базы данных и ее подключение к бэкенду 
- **Порядок показа**: показать панель администратора/adminer, добавить запись, посмотреть данные через select в БД, показать шаблоны страниц. Объяснить модели, контроллеры для созданных таблиц
- **Контрольные вопросы**: ORM, SQL, модель и миграции
- **ER диаграмма**: таблицы, связи, столбцы, типы столбцов и их длина, первичные, внешние ключи
- **Задание**: Создание базы данных `PostgreSQL` по теме работы, подключение к созданному шаблонизатору

Необходимо разработать структуру БД по выбранной теме и ее реализовать с учетом требований ниже. Использовать таблицу `услуг` в страницах разработанного приложения. Наполнить таблицы БД данными через `админку Django` или `Adminer`. Получение `услуг`, поиск и фильтрацию удаленных записей сделать через `ORM`.

Для карточек таблицы `услуг` добавить кнопку логического удаления услуги (через статус) с помощью выполнения SQL запроса без ORM.

**Требования к БД**: 

Обязательно наличие 4 таблицы: `услуг` (статус удален/действует, изображение), `заявок` (статус, дата создания, дата формирования, дата завершения, `создатель` и `модератор`), `м-м заявки-услуги` (составной первичный ключ), `пользователей`

Обязательно наличие 5 или более статусов `заявок`: черновик, удалён, сформирован, завершён, отклонён. Названия таблиц и их полей должны соответствовать предметной области. 
