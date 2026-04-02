-- ============================================================
-- Upsert all known employees into Neon production
-- Source: current local employee roster (80 employees)
-- Safe to run multiple times
-- ============================================================

BEGIN;

WITH source_employees (
    first_name,
    last_name,
    work_email,
    phone,
    mobile,
    work_location,
    status,
    employment_type,
    hire_date,
    country_code
) AS (
    VALUES
        ('Abdelhamid','Mouawad','abdelhamid@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Amgad','Zakaria','abdelrahman@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Abdul Rahman','Omar','abdul@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','AF'),
        ('Alaa','Ahmed','alaa.a@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Alaa','Jizzini','alaa.j@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Alaa','Sayed','alaa.s@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','PS'),
        ('Muhammad  ','Al Emam ','alemam@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Ali','Faraj','alif@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Ali ','Karake','alik@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Amena ','Zabateh','amena@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Amro','Al Mzayyen','amro@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','PS'),
        ('Angela','Sami','angela@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Aya','Darwish','aya.d@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Bushra ','Kholani','buchra@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Carine','Mattar','carine@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Cemile','Hasanoğlu','cemile@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Dr. Hazem','El Haddad','charbel@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Cihad','Sakka','cihad@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Ekramullah','Safi','ekramullah@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','AF'),
        ('Muhammed Enes','Karabeyeser','enes@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Gokce','Kaya Allende','gokce@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Habiba','Samy Sams','habiba@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Hadeel','Ayyash','hadeel@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','PS'),
        ('Hadi','Bdeir','hadi@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Hanadi','Ali ahmad','Hanadi@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Hanine','El Husseini','hanine@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Hend ','Hassan','hassan@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Hazem ','Hamada Elmanawy','hazem.m@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Heba','Wataney','heba.w@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Hussein ','Haj Hassan','Hussein.hh@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Ibrahim','Khaled','ibrahim@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Imad','Bazzi','imad@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Iman','Abdel Latif','iman.a@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('İsra ','Hacali','isra@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Jad','Wehbe','jad@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Jumana','Sarrajoğlu','jumana@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Mohammed ','Kamal','kamal@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Khalid ','Rifaie','khalid@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Mohammad ','Kholani','kholani@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Mahmoud ','Hassan Abdel Baqi Ajami','mahmoudh@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Maiwand','Rohani','maiwand@inara.org','+905376259033','+93788880088',NULL,'ACTIVE','FULL_TIME','2024-01-01','US'),
        ('Malik','Alrifaii','malik@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Maram ','Zakaria Saad','maram@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mariam','Sherif Ahmed Maher','mariam.s@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mariam','Yamany','mariamy@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Marwa ','El khalil ','marwa@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Maysoun','Mohamed Abdallah','maysoun@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mentallah','Asaad','menna@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mer ','Wais','mer@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Mohamed ','Sobhy','mohamed@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mohamed ','Abd El Aziz Mohamed Mahmoud Fouda','mohamedf@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Mona ','Chahla ','mona.c@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Mona','Kumsan','mona.k@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Mona','Al-Masri','mona@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','PS'),
        ('Nadeen','Abdo','nadeen@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Nadim','El Roz','nadime@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Nadine','Jawad','nadine@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Naim','Ugutmen','naim@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Nofa  ','Abazz','nofa@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Nour','Dandach','nour.d@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Nour','Ghoussaini','nourg@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Nour  ','Al-Hussein','nourh@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Omnia','Aboulmagd','omnia@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Omina','Osama Ibrahim','omniao@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Patricia','Sebaaly','patricia@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Rahaf ','Byad','rahaf@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Rahma ','Al Masri','rahma@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Rahmatullah','Arsalan','rahmatullah@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','GB'),
        ('Rawan','Nasser','rawan@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Razan ','Akram','razan@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Sara','Mohsen','sara.m@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Sara','Ahmed Montser','saram@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Sham ','Al-Hussein','sham@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','SY'),
        ('Sibel','Arbar','sibel@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','TR'),
        ('Soha','Shaer','soha@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Tatiana','Al Khraby','tatiana@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Yara','El Zakka','yaraz@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB'),
        ('Yousra','Sharekh','yousra@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','PS'),
        ('Yousra','Hamrouch','yousrah@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','EG'),
        ('Zeinab','Mukdad','Zeinab.m@inara.org',NULL,NULL,NULL,'ACTIVE','FULL_TIME','2025-12-07','LB')
),
normalized_source AS (
    SELECT
        BTRIM(first_name) AS first_name,
        BTRIM(last_name) AS last_name,
        work_email,
        NULLIF(BTRIM(COALESCE(phone, '')), '') AS phone,
        NULLIF(BTRIM(COALESCE(mobile, '')), '') AS mobile,
        NULLIF(BTRIM(COALESCE(work_location, '')), '') AS work_location,
        status::employmentstatus AS status,
        employment_type::employmenttype AS employment_type,
        hire_date::date AS hire_date,
        COALESCE(NULLIF(BTRIM(COALESCE(country_code, '')), ''), 'LB') AS country_code
    FROM source_employees
),
updated AS (
    UPDATE employees e
    SET first_name = src.first_name,
        last_name = src.last_name,
        work_email = src.work_email,
        phone = src.phone,
        mobile = src.mobile,
        work_location = COALESCE(src.work_location, e.work_location),
        status = src.status,
        employment_type = src.employment_type,
        hire_date = COALESCE(src.hire_date, e.hire_date),
        country_code = src.country_code,
        user_id = COALESCE(e.user_id, u.id),
        updated_at = NOW()
    FROM normalized_source src
    LEFT JOIN users u
        ON LOWER(u.email) = LOWER(src.work_email)
       AND u.is_deleted = false
    WHERE LOWER(e.work_email) = LOWER(src.work_email)
    RETURNING e.work_email
),
max_emp AS (
    SELECT COALESCE(MAX(CAST(SPLIT_PART(employee_number, '-', 2) AS INT)), 0) AS max_num
    FROM employees
    WHERE employee_number ~ '^EMP-[0-9]+$'
),
missing_source AS (
    SELECT
        src.*,
        u.id AS user_id,
        ROW_NUMBER() OVER (ORDER BY LOWER(src.work_email)) AS rn
    FROM normalized_source src
    LEFT JOIN employees e
        ON LOWER(e.work_email) = LOWER(src.work_email)
    LEFT JOIN users u
        ON LOWER(u.email) = LOWER(src.work_email)
       AND u.is_deleted = false
    WHERE e.id IS NULL
),
inserted AS (
    INSERT INTO employees (
        id,
        user_id,
        employee_number,
        first_name,
        last_name,
        work_email,
        phone,
        mobile,
        work_location,
        status,
        employment_type,
        hire_date,
        country_code,
        created_at,
        updated_at,
        is_deleted
    )
    SELECT
        gen_random_uuid(),
        ms.user_id,
        'EMP-' || LPAD((me.max_num + ms.rn)::TEXT, 3, '0'),
        ms.first_name,
        ms.last_name,
        ms.work_email,
        ms.phone,
        ms.mobile,
        ms.work_location,
        ms.status,
        ms.employment_type,
        ms.hire_date,
        ms.country_code,
        NOW(),
        NOW(),
        false
    FROM missing_source ms
    CROSS JOIN max_emp me
    RETURNING work_email
)
SELECT
    (SELECT COUNT(*) FROM normalized_source) AS source_employees,
    (SELECT COUNT(*) FROM updated) AS updated_rows,
    (SELECT COUNT(*) FROM inserted) AS inserted_rows,
    (SELECT COUNT(*) FROM employees WHERE is_deleted = false) AS total_employees_after;

COMMIT;

SELECT employee_number, first_name, last_name, work_email, user_id IS NOT NULL AS linked
FROM employees
WHERE is_deleted = false
ORDER BY employee_number;