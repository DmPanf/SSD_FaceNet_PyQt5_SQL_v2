### пример структуры таблицы SQL:

1. `access_log`
    - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `event_type` (TEXT) — "ip-cam-in" или "ip-cam-out"
    - `year` (INTEGER)
    - `month` (INTEGER)
    - `date` (TEXT) — в формате ГГГГ-ММ-ДД
    - `time` (TEXT) — в формате ЧЧ-ММ-СС
    - `full_name` (TEXT)
    - `department` (TEXT)
    - `email` (TEXT)
    - `birth_date` (TEXT) — в формате ГГГГ-ММ-ДД
    - `position` (TEXT)
    - `mobile_phone` (TEXT)
    - `birth_city` (TEXT)

Эта структура позволяет сохранить все необходимые данные. Вы можете использовать SQL запрос для создания такой таблицы:

```sql
CREATE TABLE access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    year INTEGER,
    month INTEGER,
    date TEXT,
    time TEXT,
    full_name TEXT,
    department TEXT,
    email TEXT,
    birth_date TEXT,
    position TEXT,
    mobile_phone TEXT,
    birth_city TEXT
);
```

Это базовый пример, и вы можете его модифицировать в зависимости от конкретных потребностей.

---

## Для приведения базы данных к 3-й нормальной форме (3NF), можно разбить одну большую таблицу на несколько меньших, чтобы избежать дублирования данных:

1. `employees`
    - `employee_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `full_name` (TEXT)
    - `department` (TEXT)
    - `email` (TEXT)
    - `birth_date` (TEXT)
    - `position` (TEXT)
    - `mobile_phone` (TEXT)
    - `birth_city` (TEXT)

2. `events`
    - `event_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `event_type` (TEXT) — "ip-cam-in" или "ip-cam-out"

3. `access_log`
    - `log_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `employee_id` (INTEGER, FOREIGN KEY REFERENCES `employees(employee_id)`)
    - `event_id` (INTEGER, FOREIGN KEY REFERENCES `events(event_id)`)
    - `year` (INTEGER)
    - `month` (INTEGER)
    - `date` (TEXT)
    - `time` (TEXT)

С SQL запросами для создания этих таблиц:

```sql
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    department TEXT,
    email TEXT,
    birth_date TEXT,
    position TEXT,
    mobile_phone TEXT,
    birth_city TEXT
);

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT
);

CREATE TABLE access_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    event_id INTEGER,
    year INTEGER,
    month INTEGER,
    date TEXT,
    time TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
```

Эта структура уменьшает дублирование данных и делает базу данных более гибкой и легко поддерживаемой.
