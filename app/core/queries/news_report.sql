SELECT
    TOP (100)
    exe.publish_date AS 'Fecha de publicación',
    exe.economic_activity AS 'Actividad económica',
    exe.new_url AS 'URL Noticia',
    (SELECT news_outlets.new_outlet_name FROM news_outlets WHERE news_outlets.id=exe.new_outlet_id) AS 'Medio de Comunicación',
    region AS 'Cobertura Geográfica',
    exe.new_title AS 'Titulo',
    exe.new_subtitle AS 'Subtitulo',
    exe.summary AS 'Resumen',
    exe.topics AS 'Topicos',
    exe.news_of_interest AS 'Noticia de interes',
    exe.economic_activity AS 'Actividad Economica'
FROM
    executions as exe
WHERE
    exe.status = 'success'
--     execution_datetime >= ?
