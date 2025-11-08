-- Запрос 5: Комплексный анализ эволюции боевого стиля бойцов


WITH fighter_chronological_fights AS (
    -- CTE 1: История боев каждого бойца с хронологической нумерацией
    SELECT 
        fbi.fighter_link,
        fbi.fighter_name,
        fbi.fight_link,
        el.event_date,
        fd.weight_category,
        fd.is_title,
        tfs.sig_str_got,
        tfs.sig_str_percent,
        tfs.td_got,
        tfs.sub_att,
        tss.head_str_got,
        tss.body_str_got,
        tss.leg_str_got,
        tss.clinch_str_got,
        tss.ground_str_got,
        fbi.fight_result,
        ROW_NUMBER() OVER (PARTITION BY fbi.fighter_link ORDER BY el.event_date) as fight_sequence,
        ROW_NUMBER() OVER (PARTITION BY fbi.fighter_link ORDER BY el.event_date DESC) as fights_from_recent
    FROM dds.fight_base_info fbi
    JOIN dds.fight_detail fd ON fbi.fight_link = fd.fight_link
    JOIN raw.fight_stat_link fsl ON fbi.fight_link = fsl.fight_link
    JOIN dds.event_link el ON fsl.event_link = el.event_link
    JOIN dds.total_fight_stat tfs ON fbi.fight_link = tfs.fight_link AND fbi.fighter_name = tfs.fighter
    JOIN dds.total_significant_strikes tss ON fbi.fight_link = tss.fight_link AND fbi.fighter_name = tss.fighter
),
fighter_style_periods AS (
    -- CTE 2: Анализ боевого стиля в разные периоды карьеры
    SELECT 
        fighter_link,
        fighter_name,
        CASE 
            WHEN fight_sequence <= 3 THEN 'Ранний'
            WHEN fight_sequence > 3 AND fight_sequence <= 10 THEN 'Развивающийся'
            WHEN fight_sequence > 10 AND fight_sequence <= 20 THEN 'Опытный'
            ELSE 'Пик карьеры'
        END as career_period,
        ROUND(AVG(sig_str_got), 2) as avg_sig_strikes,
        ROUND(AVG(sig_str_percent), 1) as avg_accuracy,
        ROUND(AVG(td_got), 2) as avg_takedowns,
        ROUND(AVG(sub_att), 2) as avg_sub_attempts,
        ROUND(AVG(head_str_got), 2) as avg_head_strikes,
        ROUND(AVG(body_str_got), 2) as avg_body_strikes,
        ROUND(AVG(leg_str_got), 2) as avg_leg_strikes,
        ROUND(AVG(clinch_str_got), 2) as avg_clinch_strikes,
        ROUND(AVG(ground_str_got), 2) as avg_ground_strikes,
        COUNT(*) as fights_in_period,
        SUM(CASE WHEN fight_result = 'W' THEN 1 ELSE 0 END) as wins_in_period
    FROM fighter_chronological_fights
    GROUP BY fighter_link, fighter_name, career_period
),
style_evolution AS (
    -- CTE 3: Определение эволюции стиля (ранний vs текущий)
    SELECT 
        fsp_early.fighter_link,
        fsp_early.fighter_name,
        fsp_early.avg_sig_strikes as early_sig_strikes,
        (
            SELECT fsp_current.avg_sig_strikes 
            FROM fighter_style_periods fsp_current 
            WHERE fsp_current.fighter_link = fsp_early.fighter_link 
            AND fsp_current.career_period = 'Пик карьеры'
            LIMIT 1
        ) as current_sig_strikes,
        fsp_early.avg_takedowns as early_takedowns,
        (
            SELECT fsp_current.avg_takedowns 
            FROM fighter_style_periods fsp_current 
            WHERE fsp_current.fighter_link = fsp_early.fighter_link 
            AND fsp_current.career_period = 'Пик карьеры'
            LIMIT 1
        ) as current_takedowns,
        fsp_early.avg_accuracy as early_accuracy,
        (
            SELECT fsp_current.avg_accuracy 
            FROM fighter_style_periods fsp_current 
            WHERE fsp_current.fighter_link = fsp_early.fighter_link 
            AND fsp_current.career_period = 'Пик карьеры'
            LIMIT 1
        ) as current_accuracy,
        (
            SELECT fsp_current.fights_in_period 
            FROM fighter_style_periods fsp_current 
            WHERE fsp_current.fighter_link = fsp_early.fighter_link 
            AND fsp_current.career_period = 'Пик карьеры'
            LIMIT 1
        ) as peak_fights
    FROM fighter_style_periods fsp_early
    WHERE fsp_early.career_period = 'Ранний'
)
SELECT 
    fighter_name,
    early_sig_strikes,
    current_sig_strikes,
    ROUND(((COALESCE(current_sig_strikes, 0) - COALESCE(early_sig_strikes, 0)) / NULLIF(COALESCE(early_sig_strikes, 1), 0)) * 100, 1) as sig_strike_change_percent,
    early_takedowns,
    current_takedowns,
    ROUND(((COALESCE(current_takedowns, 0) - COALESCE(early_takedowns, 0)) / NULLIF(COALESCE(early_takedowns, 0.1), 0)) * 100, 1) as takedown_change_percent,
    early_accuracy,
    current_accuracy,
    ROUND(COALESCE(current_accuracy, 0) - COALESCE(early_accuracy, 0), 1) as accuracy_change,
    CASE 
        WHEN COALESCE(current_sig_strikes, 0) > COALESCE(early_sig_strikes, 0) * 1.2 AND COALESCE(current_accuracy, 0) > COALESCE(early_accuracy, 0) 
        THEN 'Значительное улучшение в ударной технике'
        WHEN COALESCE(early_takedowns, 0) > 0 AND COALESCE(current_takedowns, 0) > COALESCE(early_takedowns, 0) * 1.2 
        THEN 'Развитие борцовской техники'
        WHEN COALESCE(current_sig_strikes, 0) < COALESCE(early_sig_strikes, 0) * 0.8 
        THEN 'Переход на защитный стиль'
        WHEN COALESCE(early_accuracy, 0) > 0 AND COALESCE(current_accuracy, 0) > COALESCE(early_accuracy, 0) * 1.5 
        THEN 'Повышение технической точности'
        ELSE 'Стабильный стиль'
    END as style_evolution
FROM style_evolution
WHERE COALESCE(peak_fights, 0) >= 5  -- Минимум 5 боев в пике карьеры
ORDER BY sig_strike_change_percent DESC NULLS LAST;
