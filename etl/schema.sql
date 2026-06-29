CREATE DATABASE IF NOT EXISTS STATTRACK;
USE STATTRACK;

-- Table for teams
CREATE TABLE IF NOT EXISTS teams (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL
);

-- Table for agents
CREATE TABLE IF NOT EXISTS agents (
    agent_id INT PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL,
    role VARCHAR(255)
);

-- Table for players, with a foreign key to teams
CREATE TABLE IF NOT EXISTS players (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    team_id INT,
    CONSTRAINT fk_players_teams FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Table for games, with foreign keys to teams
CREATE TABLE IF NOT EXISTS games (
    game_id INT PRIMARY KEY,
    team1_id INT,
    team2_id INT,
    map VARCHAR(255),
    winner_id INT,
    w_score INT,
    l_score INT,
    CONSTRAINT fk_games_team1 FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    CONSTRAINT fk_games_team2 FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    CONSTRAINT fk_games_winner FOREIGN KEY (winner_id) REFERENCES teams(team_id),
    CONSTRAINT chk_winner_valid CHECK (winner_id = team1_id OR winner_id = team2_id)
);

-- Table for player stats, with foreign keys to players, games, and agents
CREATE TABLE IF NOT EXISTS stats (
    player_id INT,
    game_id INT,
    agent_id INT,
    rating FLOAT,
    acs INT,
    kills INT,
    deaths INT,
    assists INT,
    kast_percent INT,
    adr INT,
    hs_percent INT,
    first_kills INT,
    first_deaths INT,
    PRIMARY KEY (game_id, player_id),
    CONSTRAINT fk_stats_players FOREIGN KEY (player_id) REFERENCES players(player_id),
    CONSTRAINT fk_stats_games FOREIGN KEY (game_id) REFERENCES games(game_id),
    CONSTRAINT fk_stats_agents FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);
DELIMITER //
CREATE TRIGGER limit_stats_per_game
BEFORE INSERT ON stats
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM stats WHERE game_id = NEW.game_id) >= 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Each game can have only 10 player stats entries.';
    END IF;
END;
//
DELIMITER ;
