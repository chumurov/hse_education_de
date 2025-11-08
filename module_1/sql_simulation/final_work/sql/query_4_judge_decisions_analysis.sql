-- Запрос 4: Анализ тенденций в судейских решениях для конкретного события


WITH event_fights AS (
    -- CTE 1: Получить все бои конкретного события
    SELECT 
        fsl.event_link,
        fsl.fight_link,
        el.event_name,
        el.event_date,
        fbi_red.fighter_name as red_fighter,
        fbi_blue.fighter_name as blue_fighter,
        fd.method,
        fbi_red.fight_result as red_result
    FROM raw.fight_stat_link fsl
    JOIN dds.event_link el ON fsl.event_link = el.event_link
    JOIN dds.fight_base_info fbi_red ON fsl.fight_link = fbi_red.fight_link AND fbi_red.corner = 'red'
    JOIN dds.fight_base_info fbi_blue ON fsl.fight_link = fbi_blue.fight_link AND fbi_blue.corner = 'blue'
    JOIN dds.fight_detail fd ON fsl.fight_link = fd.fight_link
    WHERE el.event_date >= CURRENT_DATE - INTERVAL '90 days'  -- Последние 90 дней
),
judge_decisions AS (
    -- CTE 2: Решения судей для боев этого события
    SELECT 
        ef.event_link,
        ef.fight_link,
        ef.red_fighter,
        ef.blue_fighter,
        frd.judge,
        frd.score,
        SPLIT_PART(frd.score, '-', 1)::int as red_score,
        SPLIT_PART(frd.score, '-', 2)::int as blue_score,
        CASE 
            WHEN SPLIT_PART(frd.score, '-', 1)::int > SPLIT_PART(frd.score, '-', 2)::int THEN 'Red'
            WHEN SPLIT_PART(frd.score, '-', 1)::int < SPLIT_PART(frd.score, '-', 2)::int THEN 'Blue'
            ELSE 'Tie'
        END as judge_decision,
        ROW_NUMBER() OVER (PARTITION BY ef.fight_link ORDER BY frd.judge) as judge_number,
        COUNT(*) OVER (PARTITION BY ef.fight_link) as total_judges
    FROM event_fights ef
    LEFT JOIN dds.fight_referee_decisions frd ON ef.fight_link = frd.fight_link
),
decision_summary AS (
    -- CTE 3: Сводка по решениям для каждого боя
    SELECT 
        jd.event_link,
        jd.fight_link,
        jd.red_fighter,
        jd.blue_fighter,
        SUM(CASE WHEN jd.judge_decision = 'Red' THEN 1 ELSE 0 END) as red_votes,
        SUM(CASE WHEN jd.judge_decision = 'Blue' THEN 1 ELSE 0 END) as blue_votes,
        SUM(CASE WHEN jd.judge_decision = 'Tie' THEN 1 ELSE 0 END) as tie_votes,
        MAX(jd.total_judges) as judges_count
    FROM judge_decisions jd
    GROUP BY jd.event_link, jd.fight_link, jd.red_fighter, jd.blue_fighter
)
SELECT 
    ds.event_link,
    ds.fight_link,
    ds.red_fighter,
    ds.blue_fighter,
    ds.red_votes,
    ds.blue_votes,
    ds.tie_votes
FROM decision_summary ds
ORDER BY ds.event_link, ds.fight_link;
