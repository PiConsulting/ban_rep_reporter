SELECT
    execution_datetime AS 'Fecha de ejecución',
    count(new_id) AS "Total Noticias",
    sum(CASE WHEN news_of_interest = 1 THEN 1 ELSE 0 END) AS "Total Noticias de interes",
    sum(CASE WHEN news_of_interest = 0 THEN 0 ELSE 1 END) AS "Total Noticias sin interes"
FROM
    executions
GROUP BY
    execution_datetime
ORDER BY
    execution_datetime