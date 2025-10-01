SELECT
     TOP (100)
        YEAR(exe.publish_date) AS 'Año',
        MONTH(exe.publish_date) AS 'Mes',
        DAY(exe.publish_date) AS 'Día',
        exe.publish_date AS 'Fecha de publicación',
        exe.economic_activity AS 'Actividad económica',
        exe.new_url AS 'Enlace Web',
        (SELECT news_outlets.new_outlet_name FROM news_outlets WHERE news_outlets.id=exe.new_outlet_id) AS 'Medio de comunicación',
        region AS 'Cobertura geográfica',
        (exe.new_title + ' \n\n ' + exe.new_subtitle) AS 'Título y subtítulo',
        exe.summary AS 'Resumen',
        exe.topics AS 'Tópicos',
        exe.news_of_interest AS 'Noticia de interés',
        exe.economic_activity AS 'Actividad económica'
FROM
    executions as exe
WHERE
    exe.status = 'success'
AND
    exe.execution_datetime >= ?
