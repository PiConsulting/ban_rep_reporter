SELECT
    region AS 'Región',
    count(new_id) AS "Total noticias",
    sum(CASE WHEN news_of_interest = 1 THEN 1 ELSE 0 END) AS "Total noticias de interes",
    sum(CASE WHEN news_of_interest = 0 THEN 0 ELSE 1 END) AS "Total noticias sin interes"
FROM
    executions
-- where
--     execution_date >= ?
GROUP BY
    region
ORDER BY
    region