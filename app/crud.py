import streamlit as st
import pandas as pd
import mysql.connector

st.title("📈Stat Track🛣️")


#Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql@naveen45",
    database="stattrack"
)
cursor = conn.cursor(dictionary=True)

# Tabs
tabs = st.tabs(["Teams", "Players", "Agents", "Games", "Player Stats"])

# --------------------------- TEAMS ---------------------------
with tabs[0]:
    st.header("Manage Teams")
    
    # CREATE TEAM
    with st.form("create_team"):
        st.subheader("Create Team")
        team_name = st.text_input("Team Name").upper()

        st.write("Add Players (at least 5 required)")
        player_names = []
        st.caption("Blank names are not allowed")
        for i in range(5):
            player_name = st.text_input(f"Player {i+1}").strip()
            if(player_name):
                player_names.append(player_name)

        submitted = st.form_submit_button("Add Team")

        if submitted:
            if not team_name:
                st.error("Please enter a team name.")
            elif len(player_names) < 5:
                st.error("A team must have at least 5 players.")
            else:
                try:
                    conn.start_transaction()
                    cursor.execute("SELECT MAX(team_id) FROM teams")
                    result = cursor.fetchone()["MAX(team_id)"]
                    max_team_id = result if result is not None else 100
                    new_team_id = max_team_id + 1

                    cursor.execute("SELECT MAX(player_id) FROM players")
                    result = cursor.fetchone()["MAX(player_id)"]
                    max_player_id = result if result is not None else 1000

                    cursor.execute(
                        "INSERT INTO teams (team_id, team_name) VALUES (%s, %s)",
                        (new_team_id, team_name)
                    )

                    for i, player_name in enumerate(player_names):
                        cursor.execute(
                            "INSERT INTO players (player_id, player_name, team_id) VALUES (%s, %s, %s)",
                            (max_player_id + i + 1, player_name, new_team_id)
                        )

                    conn.commit()
                    st.success(f"Team '{team_name}' added successfully!")

                except mysql.connector.Error as e:
                    conn.rollback()
                    st.error(f"Transaction failed: {e.msg} (Error code: {e.errno})")

    # READ TEAMS
    st.subheader("Teams")
    cursor.execute("SELECT * FROM teams")
    teams_df = pd.DataFrame(cursor.fetchall())
    st.dataframe(teams_df.reset_index(drop = True), hide_index=True, use_container_width=True)

    # UPDATE / DELETE
    with st.form("update_team"):
        team_ids = teams_df['team_id'].tolist()
        selected_team = st.selectbox("Select a team to Update", team_ids)
        new_name = st.text_input("New Team Name").upper()
        if st.form_submit_button("Update Team"):
            cursor.execute("UPDATE teams SET team_name=%s WHERE team_id=%s", (new_name, selected_team))
            conn.commit()
            st.success("Team updated successfully!")
            st.rerun()

# ------------------- PLAYERS -------------------
with tabs[1]:
    st.header("Manage Players")
    
    # CREATE PLAYER
    cursor.execute("SELECT * FROM teams")
    teams_df = pd.DataFrame(cursor.fetchall())
    team_options = teams_df.set_index('team_id')['team_name'].to_dict()
    
    with st.form("create_player"):
        player_name = st.text_input("Player Name")
        team_id = st.selectbox("Select Team", options=list(team_options.keys()), format_func=lambda x: team_options[x])
        submitted = st.form_submit_button("Add Player")
        if submitted and player_name:
            cursor.execute("SELECT MAX(player_id) FROM players;")
            result = cursor.fetchone()["MAX(player_id)"]
            max_player_id = result if result is not None else 1000
            cursor.execute("INSERT INTO players (player_id, player_name, team_id) VALUES (%s, %s, %s)", (max_player_id+1, player_name, team_id))
            conn.commit()
            st.success(f"Player '{player_name}' added successfully!")
    
    # READ PLAYERS
    st.subheader("Players")
    cursor.execute("""
        SELECT p.player_id, p.player_name, t.team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
    """)
    players_df = pd.DataFrame(cursor.fetchall())
    st.dataframe(players_df.reset_index(drop = True), hide_index=True, use_container_width=True)

# ------------------- AGENTS -------------------
with tabs[2]:
    st.header("Manage Agents")
    
    # CREATE AGENT
    with st.form("create_agent"):
        agent_name = st.text_input("Agent Name")
        role = st.selectbox("Role", options = ['Duelist', 'Initiator', 'Controller', 'Sentinel'])
        submitted = st.form_submit_button("Add Agent")
        if submitted and agent_name:
            cursor.execute("SELECT MAX(agent_id) FROM agents;")
            result = cursor.fetchone()["MAX(agent_id)"]
            max_agent_id = result if result is not None else 0
            cursor.execute("INSERT INTO agents (agent_id, agent_name, role) VALUES (%s, %s, %s)", (max_agent_id+1, agent_name, role))
            conn.commit()
            st.success(f"Agent '{agent_name}' added successfully!")

    # READ AGENTS
    st.subheader("All Agents")
    cursor.execute("SELECT * FROM agents")
    agents_df = pd.DataFrame(cursor.fetchall())
    st.dataframe(agents_df.reset_index(drop = True), hide_index=True, use_container_width=True)

# --------------------------- GAMES ---------------------------
with tabs[3]:
    st.header("Manage Games")
    
    # CREATE GAME
    with st.form("create_game"):
        cursor.execute("SELECT * FROM teams")
        teams_df = pd.DataFrame(cursor.fetchall())
        team_options = teams_df.set_index('team_id')['team_name'].to_dict()
        team1_id = st.selectbox("Team 1", options=list(team_options.keys()), format_func=lambda x: team_options[x])
        team2_id = st.selectbox("Team 2", options=[tid for tid in team_options.keys() if tid != team1_id], format_func=lambda x: team_options[x])
        game_map = st.selectbox("Map", options=['Ascent', 'Bind', 'Haven', 'Split', 'Icebox', 'Breeze', 'Fracture', 'Pearl', 'Lotus', 'Sunset', 'Abyss', 'Corrode'])
        submitted = st.form_submit_button("Add Game")
        if submitted:
            cursor.execute("SELECT MAX(game_id) FROM games;")
            result = cursor.fetchone()["MAX(game_id)"]
            max_game_id = result if result is not None else 10000
            cursor.execute("INSERT INTO games (game_id, team1_id, team2_id, map) VALUES (%s, %s, %s, %s)", (max_game_id+1, team1_id, team2_id, game_map))
            conn.commit()
            st.success("Game added successfully!")

    # ------------------- UPDATE GAMES (only games with missing winner or scores) -------------------
    st.subheader("Update Games with Missing Scores/Winner")
    cursor.execute("SELECT * FROM games WHERE winner_id IS NULL OR w_score IS NULL OR l_score IS NULL")
    incomplete_games_df = pd.DataFrame(cursor.fetchall())
    st.dataframe(incomplete_games_df.reset_index(drop=True), hide_index=True, use_container_width=True)
    if not incomplete_games_df.empty:
        with st.form("update_game_form"):
            game_to_update = st.selectbox(
                "Select Game ID to Update",
                options=incomplete_games_df['game_id'].tolist()
            )
            cursor.execute("SELECT team1_id, team2_id FROM games WHERE game_id = %s", (game_to_update,))
            result = cursor.fetchone()
            team1_id = result['team1_id']
            team2_id = result['team2_id']
            winner_id = st.selectbox(
                "Winner",
                options=[team1_id, team2_id],
                format_func=lambda x: team_options[x]
            )
            w_score = st.number_input("Winning Team Score", min_value=0, step=1)
            l_score = st.number_input("Losing Team Score", min_value=0, step=1)
            submitted_update = st.form_submit_button("Update Game Scores/Winner")
            if submitted_update:
                try:
                    cursor.execute(
                        "UPDATE games SET winner_id=%s, w_score=%s, l_score=%s WHERE game_id=%s",
                        (winner_id, w_score, l_score, game_to_update)
                    )
                    conn.commit()
                    st.success("Game updated successfully!")
                    st.rerun()
                except mysql.connector.Error as e:
                    conn.rollback()
                    st.error(f"Database error while updating: {e.msg}")

    # ------------------- DELETE INCOMPLETE GAMES -------------------
    st.subheader("Delete Incomplete Games")
    cursor.execute("SELECT * FROM games WHERE winner_id IS NULL OR w_score IS NULL OR l_score IS NULL")
    incomplete_games_df = pd.DataFrame(cursor.fetchall())
    if incomplete_games_df.empty:
        st.info("No incomplete games to delete.")
    else:
        st.dataframe(incomplete_games_df.reset_index(drop=True), hide_index=True, use_container_width=True)
        with st.form("delete_game_form"):
            game_to_delete = st.selectbox(
                "Select Game ID to Delete",
                options=incomplete_games_df["game_id"].tolist()
            )
            confirm_delete = st.checkbox("I confirm I want to delete this game and any related stats")
            submitted_delete = st.form_submit_button("Delete Game")
            if submitted_delete:
                if not confirm_delete:
                    st.warning("Please confirm deletion before proceeding.")
                else:
                    try:
                        cursor.execute("DELETE FROM stats WHERE game_id = %s", (game_to_delete,))
                        cursor.execute("DELETE FROM games WHERE game_id = %s", (game_to_delete,))
                        conn.commit()
                        st.success(f"🗑️ Game ID {game_to_delete} and related stats deleted successfully!")
                        st.rerun()
                    except mysql.connector.Error as e:
                        conn.rollback()
                        st.error(f"Database error while deleting: {e.msg}")

    # ------------------- READ GAME DETAILS -------------------
    st.subheader("View Game Details")

    with st.form("read_game_form"):
        game_id_input = st.number_input("Enter Game ID", min_value=1, step=1)
        submitted_read = st.form_submit_button("View Game Details")

        if submitted_read:
            # Fetch game info
            cursor.execute("""
                SELECT g.*, 
                    t1.team_name AS team1_name, 
                    t2.team_name AS team2_name,
                    tw.team_name AS winner_name
                FROM games g
                JOIN teams t1 ON g.team1_id = t1.team_id
                JOIN teams t2 ON g.team2_id = t2.team_id
                LEFT JOIN teams tw ON g.winner_id = tw.team_id
                WHERE g.game_id = %s
            """, (game_id_input,))
            game_info = cursor.fetchone()

            if not game_info:
                st.warning("❌ No game found with that Game ID.")
            else:
                # Handle display safely (don't hide 0)
                w_score_display = game_info['w_score'] if game_info['w_score'] is not None else "-"
                l_score_display = game_info['l_score'] if game_info['l_score'] is not None else "-"
                winner_display = game_info['winner_name'] if game_info['winner_name'] else "N/A"

                st.markdown(f"### Game ID: {game_info['game_id']}")
                st.markdown(f"**Teams:** {game_info['team1_name']} 🆚 {game_info['team2_name']}")
                st.markdown(f"**Map:** {game_info['map']}")
                st.markdown(f"**Winner:** {winner_display}")
                st.markdown(f"**Scores:** {w_score_display} - {l_score_display}")

                # Show match status
                if game_info['winner_id'] is None or game_info['w_score'] is None or game_info['l_score'] is None:
                    st.warning("⚠️ This match is incomplete.")


# --------------------------- STATS ---------------------------
with tabs[4]:
    st.header("Add Stats")

    # Step 1: Find games that don't have 10 entries
    cursor.execute("""
        SELECT g.game_id, g.team1_id, g.team2_id, g.map,
               COUNT(s.player_id) AS stat_count
        FROM games g
        LEFT JOIN stats s ON g.game_id = s.game_id
        GROUP BY g.game_id
        HAVING COUNT(s.player_id) < 10
    """)
    incomplete_games = pd.DataFrame(cursor.fetchall())

    if incomplete_games.empty:
        st.success("✅ All games already have 10 stats entries.")
    else:
        st.warning("Some games don't have 10 stat entries.")
        st.dataframe(incomplete_games, hide_index=True, use_container_width=True)

        # Select a game
        game_to_add = st.selectbox("Select a Game ID to add stats", options=incomplete_games["game_id"].tolist())

        if game_to_add:
            # Fetch team info
            cursor.execute("""
                SELECT g.team1_id, g.team2_id,
                       t1.team_name AS team1_name,
                       t2.team_name AS team2_name
                FROM games g
                JOIN teams t1 ON g.team1_id = t1.team_id
                JOIN teams t2 ON g.team2_id = t2.team_id
                WHERE g.game_id = %s
            """, (game_to_add,))
            game_info = cursor.fetchone()
            team1_id, team2_id = game_info["team1_id"], game_info["team2_id"]
            team1_name, team2_name = game_info["team1_name"], game_info["team2_name"]

            # Fetch players and agents
            cursor.execute("SELECT player_id, player_name FROM players WHERE team_id=%s", (team1_id,))
            team1_players = cursor.fetchall()
            cursor.execute("SELECT player_id, player_name FROM players WHERE team_id=%s", (team2_id,))
            team2_players = cursor.fetchall()
            cursor.execute("SELECT agent_id, agent_name FROM agents")
            agents = cursor.fetchall()
            agent_options = {a["agent_id"]: a["agent_name"] for a in agents}

            st.subheader(f"Add Stats for {team1_name} vs {team2_name}")

            with st.form("add_stats_form"):
                all_entries = []

                # ---------- TEAM 1 ----------
                st.markdown(f"### 🟥 {team1_name}")
                for i in range(5):
                    st.markdown(f"**Player Slot {i+1}**")
                    selected_player = st.selectbox(
                        f"Select Player ({team1_name})",
                        options=[p["player_id"] for p in team1_players],
                        format_func=lambda pid: next(p["player_name"] for p in team1_players if p["player_id"] == pid),
                        key=f"t1_player_{i}"
                    )
                    agent_id = st.selectbox(
                        "Agent", options=list(agent_options.keys()),
                        format_func=lambda x: agent_options[x],
                        key=f"t1_agent_{i}"
                    )

                    # Compact input layout
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        rating = st.number_input("Rating", min_value=0.0, max_value=2.0, step=0.01, key=f"t1_rating_{i}")
                    with col2:
                        acs = st.number_input("ACS", min_value=0, step=1, key=f"t1_acs_{i}")
                    with col3:
                        kills = st.number_input("Kills", min_value=0, step=1, key=f"t1_kills_{i}")
                    with col4:
                        deaths = st.number_input("Deaths", min_value=0, step=1, key=f"t1_deaths_{i}")
                    with col5:
                        assists = st.number_input("Assists", min_value=0, step=1, key=f"t1_assists_{i}")

                    col6, col7, col8, col9, col10 = st.columns(5)
                    with col6:
                        kast = st.number_input("KAST%", min_value=0, max_value=100, step=1, key=f"t1_kast_{i}")
                    with col7:
                        adr = st.number_input("ADR", min_value=0, step=1, key=f"t1_adr_{i}")
                    with col8:
                        hs = st.number_input("HS%", min_value=0, max_value=100, step=1, key=f"t1_hs_{i}")
                    with col9:
                        fk = st.number_input("FK", min_value=0, step=1, key=f"t1_fk_{i}")
                    with col10:
                        fd = st.number_input("FD", min_value=0, step=1, key=f"t1_fd_{i}")

                    all_entries.append((selected_player, game_to_add, agent_id, rating, acs, kills, deaths, assists, kast, adr, hs, fk, fd))

                # Separator between teams
                st.divider()

                # ---------- TEAM 2 ----------
                st.markdown(f"### 🟦 {team2_name}")
                for i in range(5):
                    st.markdown(f"**Player Slot {i+1}**")
                    selected_player = st.selectbox(
                        f"Select Player ({team2_name})",
                        options=[p["player_id"] for p in team2_players],
                        format_func=lambda pid: next(p["player_name"] for p in team2_players if p["player_id"] == pid),
                        key=f"t2_player_{i}"
                    )
                    agent_id = st.selectbox(
                        "Agent", options=list(agent_options.keys()),
                        format_func=lambda x: agent_options[x],
                        key=f"t2_agent_{i}"
                    )

                    # Compact input layout
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        rating = st.number_input("Rating", min_value=0.0, max_value=2.0, step=0.01, key=f"t2_rating_{i}")
                    with col2:
                        acs = st.number_input("ACS", min_value=0, step=1, key=f"t2_acs_{i}")
                    with col3:
                        kills = st.number_input("Kills", min_value=0, step=1, key=f"t2_kills_{i}")
                    with col4:
                        deaths = st.number_input("Deaths", min_value=0, step=1, key=f"t2_deaths_{i}")
                    with col5:
                        assists = st.number_input("Assists", min_value=0, step=1, key=f"t2_assists_{i}")

                    col6, col7, col8, col9, col10 = st.columns(5)
                    with col6:
                        kast = st.number_input("KAST%", min_value=0, max_value=100, step=1, key=f"t2_kast_{i}")
                    with col7:
                        adr = st.number_input("ADR", min_value=0, step=1, key=f"t2_adr_{i}")
                    with col8:
                        hs = st.number_input("HS%", min_value=0, max_value=100, step=1, key=f"t2_hs_{i}")
                    with col9:
                        fk = st.number_input("FK", min_value=0, step=1, key=f"t2_fk_{i}")
                    with col10:
                        fd = st.number_input("FD", min_value=0, step=1, key=f"t2_fd_{i}")

                    all_entries.append((selected_player, game_to_add, agent_id, rating, acs, kills, deaths, assists, kast, adr, hs, fk, fd))

                submitted = st.form_submit_button("Add Stats for Game")

                if submitted:
                    try:
                        for entry in all_entries:
                            cursor.execute("""
                                INSERT INTO stats
                                (player_id, game_id, agent_id, rating, acs, kills, deaths, assists,
                                 kast_percent, adr, hs_percent, first_kills, first_deaths)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, entry)
                        conn.commit()
                        st.success(f"✅ Stats successfully added for {team1_name} vs {team2_name} (Game ID {game_to_add})")
                        st.rerun()
                    except mysql.connector.Error as e:
                        conn.rollback()
                        st.error(f"Error adding stats: {e.msg}")

    # --------------------------- UPDATE STATS ---------------------------
    st.header("Update Player Stats")

    # Step 1: Enter Game ID
    game_id = st.number_input("Enter Game ID to Update Stats", min_value=1, step=1)

    if game_id:
        # Step 2: Fetch players who have stats for this game
        cursor.execute("""
            SELECT s.player_id, p.player_name
            FROM stats s
            JOIN players p ON s.player_id = p.player_id
            WHERE s.game_id = %s
        """, (game_id,))
        players_in_game = cursor.fetchall()

        if not players_in_game:
            st.warning("No player stats found for this Game ID.")
        else:
            selected_player = st.selectbox(
                "Select Player",
                options=[p["player_id"] for p in players_in_game],
                format_func=lambda pid: next(p["player_name"] for p in players_in_game if p["player_id"] == pid),
                key="update_player_select"
            )

            # Step 3: Fetch current stats for that player
            cursor.execute("""
                SELECT s.*, a.agent_name
                FROM stats s
                JOIN agents a ON s.agent_id = a.agent_id
                WHERE s.game_id = %s AND s.player_id = %s
            """, (game_id, selected_player))
            current_stats = cursor.fetchone()

            if current_stats:
                st.markdown("### Current Stats")
                st.dataframe(pd.DataFrame([current_stats]), hide_index=True, use_container_width=True)

                st.markdown("### Enter New Stats (all fields required)")

                # Agent and rating row
                col1, col2 = st.columns(2)
                with col1:
                    agent_id = st.number_input("Agent ID", min_value=1, step=1, key="upd_agent")
                with col2:
                    rating = st.number_input("Rating", min_value=0.0, max_value=2.0, step=0.01, key="upd_rating")

                # ACS, kills, deaths, assists row
                col3, col4, col5, col6 = st.columns(4)
                with col3:
                    acs = st.number_input("ACS", min_value=0, step=1, key="upd_acs")
                with col4:
                    kills = st.number_input("Kills", min_value=0, step=1, key="upd_kills")
                with col5:
                    deaths = st.number_input("Deaths", min_value=0, step=1, key="upd_deaths")
                with col6:
                    assists = st.number_input("Assists", min_value=0, step=1, key="upd_assists")

                # KAST, ADR, HS%, FK, FD row
                col7, col8, col9, col10, col11 = st.columns(5)
                with col7:
                    kast = st.number_input("KAST%", min_value=0, max_value=100, step=1, key="upd_kast")
                with col8:
                    adr = st.number_input("ADR", min_value=0, step=1, key="upd_adr")
                with col9:
                    hs = st.number_input("HS%", min_value=0, max_value=100, step=1, key="upd_hs")
                with col10:
                    fk = st.number_input("First Kills", min_value=0, step=1, key="upd_fk")
                with col11:
                    fd = st.number_input("First Deaths", min_value=0, step=1, key="upd_fd")

                # Step 4: Update button
                if st.button("Update Stats"):
                    try:
                        cursor.execute("""
                            UPDATE stats
                            SET agent_id = %s,
                                rating = %s,
                                acs = %s,
                                kills = %s,
                                deaths = %s,
                                assists = %s,
                                kast_percent = %s,
                                adr = %s,
                                hs_percent = %s,
                                first_kills = %s,
                                first_deaths = %s
                            WHERE player_id = %s AND game_id = %s
                        """, (
                            agent_id, rating, acs, kills, deaths, assists,
                            kast, adr, hs, fk, fd,
                            selected_player, game_id
                        ))
                        conn.commit()
                        st.success("✅ Player stats updated successfully!")
                        st.rerun()
                    except mysql.connector.Error as e:
                        conn.rollback()
                        st.error(f"Database error: {e.msg}")
