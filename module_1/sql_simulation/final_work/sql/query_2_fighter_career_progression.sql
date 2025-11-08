-- Запрос 2: Анализ карьерного прогресса бойцов с использованием WITH и оконных функций


WITH fighter_fight_history AS (
    -- CTE 1: История боев каждого бойца с датами
    SELECT 
        fbi.fighter_link,
        fbi.fighter_name,
        fbi.fight_link,
        el.event_date,
        fbi.fight_result,
        fd.weight_category,
        fd.is_title,
        ROW_NUMBER() OVER (PARTITION BY fbi.fighter_link ORDER BY el.event_date) as fight_number,
        ROW_NUMBER() OVER (PARTITION BY fbi.fighter_link ORDER BY el.event_date DESC) as fights_from_end
    FROM dds.fight_base_info fbi
    JOIN dds.fight_detail fd ON fbi.fight_link = fd.fight_link
    JOIN raw.fight_stat_link fsl ON fbi.fight_link = fsl.fight_link
    JOIN dds.event_link el ON fsl.event_link = el.event_link
),
progression_analysis AS (
    -- CTE 2: Анализ прогрессии (соотношение побед в разных периодах карьеры)
    SELECT 
        fighter_name,
        fighter_link,
        COUNT(*) as total_fights,
        SUM(CASE WHEN fight_number <= 5 THEN (CASE WHEN fight_result = 'W' THEN 1 ELSE 0 END) ELSE 0 END) as early_wins,
        SUM(CASE WHEN fight_number > 5 AND fight_number <= 15 THEN (CASE WHEN fight_result = 'W' THEN 1 ELSE 0 END) ELSE 0 END) as mid_wins,
        SUM(CASE WHEN fight_number > 15 THEN (CASE WHEN fight_result = 'W' THEN 1 ELSE 0 END) ELSE 0 END) as recent_wins,
        SUM(CASE WHEN is_title = true THEN 1 ELSE 0 END) as title_fights,
        SUM(CASE WHEN is_title = true AND fight_result = 'W' THEN 1 ELSE 0 END) as title_wins
    FROM fighter_fight_history
    GROUP BY fighter_link, fighter_name
    HAVING COUNT(*) >= 10  -- Минимум 10 боев
)
SELECT 
    fighter_name,
    total_fights,
    title_fights,
    title_wins,
    CASE 
        WHEN early_wins > 0 THEN ROUND(early_wins::numeric / NULLIF(5, 0) * 100, 1)
        ELSE 0 
    END as early_career_win_rate,
    CASE 
        WHEN mid_wins > 0 THEN ROUND(mid_wins::numeric / NULLIF(10, 0) * 100, 1)
        ELSE 0 
    END as mid_career_win_rate,
    CASE 
        WHEN recent_wins > 0 THEN ROUND(recent_wins::numeric / NULLIF(total_fights - 15, 0) * 100, 1)
        ELSE 0 
    END as recent_career_win_rate,
    CASE 
        WHEN early_wins > 0 AND recent_wins > 0 AND recent_wins > early_wins THEN 'Улучшение'
        WHEN early_wins > 0 AND recent_wins > 0 AND recent_wins < early_wins THEN 'Снижение'
        ELSE 'Стабильность'
    END as career_trend
FROM progression_analysis
WHERE title_fights > 0  -- Только бойцы с титульными боями
ORDER BY title_wins DESC, total_fights DESC;
