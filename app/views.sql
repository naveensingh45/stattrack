-- Match Summary 
CREATE OR REPLACE VIEW view_match_summary AS
SELECT 
    g.game_id,
    t1.team_name AS team1,
    t2.team_name AS team2,
    g.map,
    CASE 
        WHEN g.winner_id = g.team1_id THEN t1.team_name
        WHEN g.winner_id = g.team2_id THEN t2.team_name
        ELSE NULL
    END AS winner,
    g.w_score,
    g.l_score
FROM games g
JOIN teams t1 ON g.team1_id = t1.team_id
JOIN teams t2 ON g.team2_id = t2.team_id;

-- Player stats
CREATE VIEW view_player_stats AS
SELECT 
    p.player_id,
    p.player_name,
    t.team_name,
    a.agent_name,
    a.role,
    s.rating,
    s.acs,
    s.kills,
    s.deaths,
    s.assists,
    s.kast_percent,
    s.adr,
    s.hs_percent,
    s.first_kills,
    s.first_deaths,
    s.game_id
FROM stats s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
JOIN agents a ON s.agent_id = a.agent_id;

-- Aggregate Player Stats
CREATE VIEW view_player_aggregate AS
SELECT 
    p.player_id,
    p.player_name,
    t.team_name,
    COUNT(s.game_id) AS games_played,
    ROUND(AVG(s.rating), 2) AS avg_rating,
    ROUND(AVG(s.acs), 1) AS avg_acs,
    ROUND(AVG(s.kills), 1) AS avg_kills,
    ROUND(AVG(s.deaths), 1) AS avg_deaths,
    ROUND(AVG(s.assists), 1) AS avg_assists,
    ROUND(AVG(s.kast_percent), 1) AS avg_kast,
    ROUND(AVG(s.hs_percent), 1) AS avg_hs
FROM stats s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
GROUP BY p.player_id, p.player_name, t.team_name;

-- Player by Agent
CREATE VIEW view_player_by_agent AS
SELECT 
    p.player_id,
    p.player_name,
    t.team_name,
    a.agent_name,
    ROUND(AVG(s.rating), 2) AS avg_rating,
    ROUND(AVG(s.acs), 1) AS avg_acs,
    ROUND(AVG(s.kills), 1) AS avg_kills,
    COUNT(s.game_id) AS games_played_with_agent
FROM stats s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
JOIN agents a ON s.agent_id = a.agent_id
GROUP BY p.player_id, p.player_name, t.team_name, a.agent_name;

-- Player by Role
CREATE VIEW view_player_by_role AS
SELECT 
    p.player_id,
    p.player_name,
    t.team_name,
    a.role,
    ROUND(AVG(s.rating), 2) AS avg_rating,
    ROUND(AVG(s.acs), 1) AS avg_acs,
    ROUND(AVG(s.kills), 1) AS avg_kills,
    COUNT(s.game_id) AS games_played_in_role
FROM stats s
JOIN players p ON s.player_id = p.player_id
JOIN teams t ON p.team_id = t.team_id
JOIN agents a ON s.agent_id = a.agent_id
GROUP BY p.player_id, p.player_name, t.team_name, a.role;

-- Team Performance
CREATE VIEW view_team_performance AS
SELECT 
    t.team_id,
    t.team_name,
    COUNT(DISTINCT g.game_id) AS total_matches,
    SUM(CASE WHEN g.winner_id = t.team_id THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN g.winner_id != t.team_id THEN 1 ELSE 0 END) AS losses,
    ROUND(
        (SUM(CASE WHEN g.winner_id = t.team_id THEN 1 ELSE 0 END) / COUNT(DISTINCT g.game_id)) * 100, 2
    ) AS win_rate
FROM teams t
LEFT JOIN games g ON t.team_id IN (g.team1_id, g.team2_id)
GROUP BY t.team_id, t.team_name;

-- Team Player Summary
CREATE VIEW view_team_player_summary AS
SELECT 
    t.team_name,
    p.player_name,
    COALESCE(ROUND(AVG(s.rating), 2), 'N/A') AS avg_rating,
    COALESCE(ROUND(AVG(s.acs), 1), 'N/A') AS avg_acs,
    COALESCE(ROUND(AVG(s.kills), 1), 'N/A') AS avg_kills,
    COALESCE(ROUND(AVG(s.deaths), 1), 'N/A') AS avg_deaths,
    COUNT(s.game_id) AS games_played
FROM players p
JOIN teams t ON p.team_id = t.team_id
LEFT JOIN stats s ON s.player_id = p.player_id
GROUP BY t.team_name, p.player_name;

-- Agent Overview
CREATE VIEW view_agent_overview AS
SELECT 
    a.agent_name,
    a.role,
    COUNT(DISTINCT s.game_id) AS games_picked,
    ROUND(
        COUNT(DISTINCT s.game_id) / (SELECT COUNT(DISTINCT game_id) FROM games) * 100, 2
    ) AS pick_percent,
    ROUND(
        SUM(CASE WHEN g.winner_id = p.team_id THEN 1 ELSE 0 END) 
        / COUNT(s.game_id) * 100, 2
    ) AS win_percent_with_agent
FROM stats s
JOIN players p ON s.player_id = p.player_id
JOIN agents a ON s.agent_id = a.agent_id
JOIN games g ON s.game_id = g.game_id
GROUP BY a.agent_name, a.role;