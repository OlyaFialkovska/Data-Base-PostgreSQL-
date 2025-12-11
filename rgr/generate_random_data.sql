
-- Очищення всіх таблиць у правильному порядку
TRUNCATE TABLE "Freelancer_Platform_" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Customer_Platform_" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Project_" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Customer_" RESTART IDENTITY CASCADE;

-- 1-Створення sequence для Project_.id (якщо ще не існує)
DROP SEQUENCE IF EXISTS project_id_seq CASCADE;
CREATE SEQUENCE project_id_seq START 1;

-- Підв’язуємо sequence до стовпця id
ALTER TABLE "Project_"
ALTER COLUMN id SET DEFAULT nextval('project_id_seq'::regclass);

-- Якщо у Project_ уже були записи — синхронізуємо лічильник
SELECT setval('project_id_seq', COALESCE((SELECT MAX(id) FROM "Project_"), 0) + 1, false);

-- 2-Генерація псевдовипадкових даних для Customer_
INSERT INTO "Customer_" (id, "Name", "Surname", "Email", "Password")
SELECT gs AS id,
       initcap(chr(trunc(65 + random() * 25)::int)
             || chr(trunc(65 + random() * 25)::int)) AS "Name",
       initcap(chr(trunc(65 + random() * 25)::int)
             || chr(trunc(65 + random() * 25)::int)) AS "Surname",
       lower(chr(trunc(97 + random() * 25)::int)
            || chr(trunc(97 + random() * 25)::int)
            || chr(trunc(97 + random() * 25)::int)) || '@mail.com' AS "Email",
       substring(md5(random()::text) for 30) AS "Password"
FROM generate_series(1, 1000) AS gs;


-- 3-Генерація псевдовипадкових даних для Project_
-- id тепер генерується автоматично через sequence → поле id не вказуємо
INSERT INTO "Project_" ("Name", "Deadline", "Start date", "End date", "Customer_id", "Freelancer_id")
SELECT 'Project_' || gs,
       date '2024-01-01' + (random() * 365)::int,
       date '2023-01-01' + (random() * 365)::int,
       date '2024-01-01' + (random() * 365)::int,
       (SELECT id FROM "Customer_" ORDER BY random() LIMIT 1),
       (SELECT id FROM "Freelancer_" ORDER BY random() LIMIT 1)
FROM generate_series(1, 100000) AS gs;

-- 4-Приклади для звіту (ілюстрації SQL-генерації)

-- 1Генерація 100 псевдовипадкових чисел
SELECT trunc(random() * 1000)::int AS random_number
FROM generate_series(1, 100);

-- 2Генерація 5 випадкових рядків
SELECT chr(trunc(65 + random() * 25)::int)
     || chr(trunc(65 + random() * 25)::int) AS random_str
FROM generate_series(1, 5);

-- 3Генерація випадкових дат
SELECT timestamp '2023-01-01' +
       random() * (timestamp '2025-12-31' - timestamp '2023-01-01')
       AS random_date
FROM generate_series(1, 5);

-- 4Генерація email-адрес із комбінацій імен/прізвищ
SELECT first_name, last_name,
       lower(first_name || '.' || last_name) || '@example.com' AS email
FROM unnest(array['John','Ann','Bob','Kate']) AS first_name
CROSS JOIN unnest(array['Smith','Wilson','Nelson']) AS last_name
ORDER BY random();

-- 5-Перевірка результатів
SELECT COUNT(*) AS customers FROM "Customer_";
SELECT COUNT(*) AS projects FROM "Project_";

-- Перегляд кількох рядків
SELECT * FROM "Customer_" LIMIT 10;
SELECT * FROM "Project_" LIMIT 10;
