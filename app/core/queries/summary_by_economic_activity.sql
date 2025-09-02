select
    economic_activity,
    count(new_id) as "total noticias",
    sum(case when news_of_interest = 1 THEN 1 ELSE 0 END) as "total noticias de interes",
    sum(case when news_of_interest = 0 THEN 0 ELSE 1 END) as "total noticias sin interes"
from
    executions
-- where
--     execution_date >= ?
group by
    economic_activity
order by
    economic_activity