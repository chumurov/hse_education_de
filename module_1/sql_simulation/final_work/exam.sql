SELECT
    fighter as "Боец", 

    -- любимая область
    CASE
        WHEN head_total >= body_total AND head_total >= leg_total THEN 'Head'
        WHEN body_total >= head_total AND body_total >= leg_total THEN 'Body'
        ELSE 'Leg'
    END  as "Любимая область",

    -- % любимой области
    ROUND(
        GREATEST(head_total, body_total, leg_total) * 100.0 / NULLIF(total_strikes, 0),
        2
    ) as "% в любимую область",

    -- количество ударов в любимую область
    GREATEST(head_total, body_total, leg_total) AS "Удары в любимую область",

    -- детальная статистика
    total_strikes "Всего ударов"


FROM (
    SELECT
        fighter_ref,
        fighter,
        SUM(head_str_got) AS head_total,
        SUM(body_str_got) AS body_total,
        SUM(leg_str_got) AS leg_total,
        SUM(head_str_got + body_str_got + leg_str_got) AS total_strikes
    FROM dds.total_significant_strikes
    WHERE round = 'total'
    GROUP BY fighter_ref, fighter
) t

ORDER BY total_strikes DESC;
