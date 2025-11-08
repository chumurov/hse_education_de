-- Запрос 3: Сравнение эффективности боевых техник по весовым категориям


WITH weight_category_stats AS (
    -- CTE: Общая статистика по весовым категориям
    SELECT 
        fd.weight_category,
        COUNT(DISTINCT fbi.fight_link) as total_fights,
        ROUND(AVG(tfs.sig_str_got), 2) as avg_sig_strikes,
        ROUND(AVG(tfs.total_str_got), 2) as avg_total_strikes,
        ROUND(AVG(tfs.td_got), 2) as avg_takedowns,
        ROUND(AVG(tfs.sub_att), 2) as avg_submission_attempts,
        ROUND(AVG(tfs.ctrl), 2) as avg_control_time
    FROM dds.fight_detail fd
    JOIN dds.fight_base_info fbi ON fd.fight_link = fbi.fight_link
    JOIN dds.total_fight_stat tfs ON fbi.fight_link = tfs.fight_link AND fbi.fighter_name = tfs.fighter
    WHERE fd.weight_category NOT IN ('Open Weight', 'Tournament')
    GROUP BY fd.weight_category
),
ranked_categories AS (
    -- Ранжирование категорий по различным метрикам
    SELECT 
        weight_category,
        total_fights,
        avg_sig_strikes,
        RANK() OVER (ORDER BY avg_sig_strikes DESC) as sig_strike_rank,
        avg_total_strikes,
        RANK() OVER (ORDER BY avg_total_strikes DESC) as total_strike_rank,
        avg_takedowns,
        RANK() OVER (ORDER BY avg_takedowns DESC) as takedown_rank,
        avg_submission_attempts,
        RANK() OVER (ORDER BY avg_submission_attempts DESC) as submission_rank,
        avg_control_time,
        RANK() OVER (ORDER BY avg_control_time DESC) as control_rank
    FROM weight_category_stats
)
SELECT 
    ranked_categories.weight_category,
    ranked_categories.total_fights,
    ranked_categories.avg_sig_strikes,
    ranked_categories.sig_strike_rank,
    ranked_categories.avg_total_strikes,
    ranked_categories.total_strike_rank,
    ranked_categories.avg_takedowns,
    ranked_categories.takedown_rank,
    ranked_categories.avg_submission_attempts,
    ranked_categories.submission_rank,
    ranked_categories.avg_control_time,
    ranked_categories.control_rank,
    -- Подзапрос: определение доминирующей техники в категории
    (
        SELECT 
            CASE 
                WHEN ranked_categories.sig_strike_rank = 1 THEN 'Значимые удары'
                WHEN ranked_categories.takedown_rank = 1 THEN 'Броски'
                WHEN ranked_categories.submission_rank = 1 THEN 'Сабмишны'
                ELSE 'Контроль'
            END
    ) as dominant_technique
FROM ranked_categories
ORDER BY total_fights DESC;
