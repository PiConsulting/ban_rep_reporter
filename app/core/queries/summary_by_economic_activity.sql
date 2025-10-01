SELECT
    CASE WHEN economic_activity IS NULl THEN 'No Clasificado' ELSE economic_activity END AS 'Actividad Económica',
    count(new_id) AS "Total noticias",
    sum(CASE WHEN news_of_interest = 1 THEN 1 ELSE 0 END) AS "Total noticias de interes",
    sum(CASE WHEN news_of_interest = 0 THEN 1 ELSE 0 END) AS "Total noticias sin interes"
FROM
    executions
WHERE
    execution_datetime >= ?
GROUP BY
    economic_activity
ORDER BY
    economic_activity