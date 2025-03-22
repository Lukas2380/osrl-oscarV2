import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

# Create tables (example: users table)
cursor.executescript("""
CREATE TABLE IF NOT EXISTS vcGenerators (
    channel_id INTEGER PRIMARY KEY,   -- The generator channel ID
    channel_name TEXT NOT NULL,       -- The name of the generated VC
    user_limit INTEGER NOT NULL       -- Max users for the new VC
);

CREATE TABLE IF NOT EXISTS temporaryVCs (
    temp_channel_id INTEGER PRIMARY KEY,  -- The ID of the created VC
    owner_id INTEGER NOT NULL,            -- The user who triggered it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When it was created
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ladderStats (
    user_id INTEGER PRIMARY KEY,          -- Unique ID for each player
    wins INTEGER DEFAULT 0,               -- Number of wins
    losses INTEGER DEFAULT 0,             -- Number of losses
    current_streak INTEGER DEFAULT 0,     -- Current win streak (positive or negative)
    highest_winstreak INTEGER DEFAULT 0,  -- Highest win streak
    highest_lossstreak INTEGER DEFAULT 0, -- Highest loss streak
    total_matches INTEGER DEFAULT 0,      -- Total number of matches played
    win_rate REAL DEFAULT 0.0,            -- Win rate (percentage)
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bets (
    bet_id INTEGER PRIMARY KEY,
    player_id INTEGER,           -- The player who placed the bet
    betted_on_player_id INTEGER, -- The player being bet on
    amount INTEGER,              -- Bet amount in coins
    bet_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (betted_on_player_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS userCooldowns (
    user_id INTEGER PRIMARY KEY,  
    last_claim TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_challenge TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lockedPlayers (
    player_id INTEGER PRIMARY KEY,  -- The player who is locked
    position INTEGER,               -- Position in the leaderboard
    locked_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When the player was locked
    FOREIGN KEY (player_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,           -- Unique player ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Account creation date
);

CREATE TABLE IF NOT EXISTS wallets (
    user_id INTEGER PRIMARY KEY,           -- Unique player ID
    coins INTEGER DEFAULT 0,               -- The amount of coins the player has
    activitybonusMessages INTEGER DEFAULT 0,   -- Coins earned from activity bonus messages
    activitybonusVCtime INTEGER DEFAULT 0,     -- Coins earned from activity bonus VC time
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE 
);

CREATE TABLE IF NOT EXISTS ladderChallenges (
    challenge_id INTEGER PRIMARY KEY,
    player1_id INTEGER,
    player2_id INTEGER,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isGuardianChallenge BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (player1_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (player2_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS matchHistorySeries (
    series_id INTEGER PRIMARY KEY,
    player1_id INTEGER,
    player2_id INTEGER,
    player1_score INTEGER DEFAULT 0,
    player2_score INTEGER DEFAULT 0,
    winner_id INTEGER,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player1_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (player2_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (winner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Maybe add Indexes for matchHistorySeries (NOT matchHistory)
-- CREATE INDEX idx_matchHistorySeries_player1 ON matchHistorySeries(player1_id);
-- CREATE INDEX idx_matchHistorySeries_player2 ON matchHistorySeries(player2_id);
-- CREATE INDEX idx_matchHistorySeries_winner ON matchHistorySeries(winner_id);
-- CREATE INDEX idx_matchHistorySeries_date ON matchHistorySeries(date DESC);
""")

# Commit and close
conn.commit()
conn.close()

print("Database setup complete!")
