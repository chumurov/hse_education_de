-- Запрос 1: Процент досрочных побед и решений по годам


WITH yearly_fight_stats AS (
    -- CTE: Подсчет побед по типам и годам
    SELECT 
        EXTRACT(YEAR FROM el.event_date)::INTEGER as fight_year,
        fbi.fighter_name,
        COUNT(DISTINCT fbi.fight_link) as total_fights,
        SUM(CASE WHEN fbi.fight_result = 'W' THEN 1 ELSE 0 END) as total_wins,
        SUM(CASE 
            WHEN fbi.fight_result = 'W' AND fd.method IN ('KO/TKO', 'TKO - Doctor''s Stoppage', 'Submission', 'Other') 
            THEN 1 
            ELSE 0 
        END) as early_wins,
        SUM(CASE 
            WHEN fbi.fight_result = 'W' AND fd.method IN ('Decision - Unanimous', 'Decision - Split', 'Decision - Majority') 
            THEN 1 
            ELSE 0 
        END) as decision_wins
    FROM dds.fight_base_info fbi
    JOIN dds.fight_detail fd ON fbi.fight_link = fd.fight_link
    JOIN raw.fight_stat_link fsl ON fbi.fight_link = fsl.fight_link
    JOIN dds.event_link el ON fsl.event_link = el.event_link
    WHERE EXTRACT(YEAR FROM el.event_date) >= 2015  -- Данные с 2015 года
    GROUP BY EXTRACT(YEAR FROM el.event_date), fbi.fighter_name
    HAVING COUNT(DISTINCT fbi.fight_link) >= 3  -- Минимум 3 боя в год
)
SELECT 
    ROW_NUMBER() OVER (PARTITION BY fight_year ORDER BY early_wins DESC) as rank,
    fight_year,
    fighter_name,
    total_fights,
    total_wins,
    early_wins,
    decision_wins,
    ROUND(early_wins::numeric / NULLIF(total_wins, 0) * 100, 1) as early_win_rate_percent,
    ROUND(decision_wins::numeric / NULLIF(total_wins, 0) * 100, 1) as decision_win_rate_percent,
    ROUND(total_wins::numeric / total_fights * 100, 1) as overall_win_rate_percent
FROM yearly_fight_stats
WHERE total_wins > 0  -- Только бойцы с минимум одной победой
ORDER BY fight_year DESC, rank ASC;
