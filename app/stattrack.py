import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import mysql.connector

# APP TITLE
st.title("📈 Stat Track 🛣️")

# DATABASE CONNECTION
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql@naveen45",
    database="stattrack"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS stattrack")

print("Database Ready")

def load_data(query):
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data)

def display_df(df):
    df_display = df.copy()
    df_display.columns = [col.replace("_", " ").title() for col in df_display.columns]
    st.dataframe(df_display, hide_index=True, use_container_width=True)

# SIDEBAR NAVIGATION
st.sidebar.title("📊 Navigation")
tabs = ["🏠 Overview", "⚔️ Matches", "👥 Teams", "🧍 Players", "🔫 Agents", "🏅 Leaderboards"]
choice = st.sidebar.radio("Go to:", tabs)

# 🏠 OVERVIEW TAB
if choice == "🏠 Overview":
    st.header("🏠 Overall Summary")
    tab1, tab2, tab3 = st.tabs(["Teams", "Players", "Agents"])

    with tab1:
        st.subheader("🏆 Top Teams (by Win %)")
        df_teams = load_data("SELECT * FROM view_team_performance ORDER BY win_rate DESC LIMIT 5;")
        display_df(df_teams.drop("team_id", axis=1))

        fig = go.Figure(go.Bar(
            x=df_teams["win_rate"],
            y=df_teams["team_name"],
            orientation="h",
            marker=dict(color="#4bc0c0"),
            text=df_teams["win_rate"].round(2),
            textposition="auto"
        ))
        fig.update_layout(title="Top Teams by Win %", xaxis_title="Win Rate (%)", yaxis_title="", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("👥 Top Players (by Rating)")
        df_players = load_data("SELECT * FROM view_player_aggregate ORDER BY avg_rating DESC LIMIT 5;")
        display_df(df_players[["player_name", "team_name", "avg_rating", "avg_kills"]])

        fig = go.Figure(go.Bar(
            x=df_players["avg_rating"],
            y=df_players["player_name"],
            orientation="h",
            marker=dict(color="#36a2eb"),
            text=df_players["avg_rating"].round(2),
            textposition="auto"
        ))
        fig.update_layout(title="Top Players by Rating", xaxis_title="Average Rating", yaxis_title="", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("🔫 Top Agents (by Pick %)")
        df_agents = load_data("SELECT * FROM view_agent_overview ORDER BY pick_percent DESC LIMIT 5;")
        display_df(df_agents[["agent_name", "role", "pick_percent", "win_percent_with_agent"]])

        fig = go.Figure(go.Bar(
            x=df_agents["pick_percent"],
            y=df_agents["agent_name"],
            orientation="h",
            marker=dict(color="#ff9f40"),
            text=df_agents["pick_percent"].round(2),
            textposition="auto"
        ))
        fig.update_layout(title="Top Agents by Pick %", xaxis_title="Pick %", yaxis_title="", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ⚔️ MATCHES TAB
elif choice == "⚔️ Matches":
    st.header("⚔️ Match Results : Head to Head")

    df_matches = load_data("SELECT * FROM view_match_summary;")

    if df_matches.empty:
        st.warning("No match data available.")
    else:
        team_options = sorted(pd.concat([df_matches["team1"], df_matches["team2"]]).unique())
        team1 = st.selectbox("Select Team 1", team_options)
        team2 = st.selectbox("Select Team 2", team_options)

        filtered = df_matches[
            ((df_matches["team1"] == team1) & (df_matches["team2"] == team2)) |
            ((df_matches["team1"] == team2) & (df_matches["team2"] == team1))
        ]

        wins = filtered["winner"].value_counts()
        team1_wins, team2_wins = wins.get(team1, 0), wins.get(team2, 0)
        total = team1_wins + team2_wins

        if total == 0:
            st.warning("No matches found between these teams.")
        else:
            team1_pct = team1_wins / total * 100
            team2_pct = team2_wins / total * 100

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[team1_pct],
                y=["Head-to-Head"],
                orientation='h',
                name=team1,
                marker=dict(color="#3bf0f6"),
                text=f"{team1_pct:.1f}%"
            ))
            fig.add_trace(go.Bar(
                x=[team2_pct],
                y=["Head-to-Head"],
                orientation='h',
                name=team2,
                marker=dict(color="#ec4899"),
                text=f"{team2_pct:.1f}%"
            ))

            fig.update_layout(
                barmode="stack",
                title=f"Head to Head: {team1} vs {team2}",
                showlegend=True,
                height=250,
                xaxis=dict(visible=False),
                yaxis=dict(showticklabels=False)
            )
            st.plotly_chart(fig, use_container_width=True)

        display_df(filtered)

        if not filtered.empty:
            match_id = st.selectbox("Select Match", filtered["game_id"])
            query = f"SELECT * FROM view_player_stats WHERE game_id = {match_id};"
            df_stats = load_data(query)
            st.subheader("ScoreBoard")
            display_df(df_stats.drop(["player_id", "game_id"], axis=1))

# 👥 TEAMS TAB
elif choice == "👥 Teams":
    st.header("👥 Team Statistics & Player Summary")

    df_team_perf = load_data("SELECT * FROM view_team_performance;")
    st.subheader("🏆 Team Performance Overview")
    display_df(df_team_perf.drop("team_id", axis=1))

    if not df_team_perf.empty:
        team_selected = st.selectbox("Select a Team", sorted(df_team_perf["team_name"].unique()))
        query = f"SELECT * FROM view_team_player_summary WHERE team_name = '{team_selected}';"
        df_team_players = load_data(query)
        st.subheader(f"Player Summary for {team_selected}")
        display_df(df_team_players)

        metric = st.selectbox("Select Metric for Comparison", ["rating", "kills", "assists", "deaths"])
        if metric in df_team_players.columns:
            fig = go.Figure(go.Bar(
                x=df_team_players[metric],
                y=df_team_players["player_name"],
                orientation="h",
                marker=dict(color="#8e5ea2"),
                text=df_team_players[metric].round(2),
                textposition="auto"
            ))
            fig.update_layout(title=f"{team_selected} Players by {metric.title()}", xaxis_title=metric.title(), yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

# 🧍 PLAYERS TAB
elif choice == "🧍 Players":
    st.header("🧍 Player Statistics")

    df_player = load_data("SELECT * FROM view_player_aggregate;")

    if not df_player.empty:
        player_selected = st.selectbox("Select a Player", sorted(df_player["player_name"].unique()))
        player_team = df_player.loc[df_player["player_name"] == player_selected, "team_name"].values[0]

        st.subheader("Aggregate Stats")
        display_df(df_player[df_player["player_name"] == player_selected].drop("player_id", axis=1))

        st.subheader("🕸️ Overall Performance Radar")

        radar_metrics = ["avg_rating", "avg_acs", "avg_kills", "avg_assists", "avg_kast", "avg_hs"]
        player_stats = df_player[df_player["player_name"] == player_selected][radar_metrics].iloc[0]

        normalized = {}
        for metric in radar_metrics:
            min_val = df_player[metric].min()
            max_val = df_player[metric].max()
            val = player_stats[metric]
            if max_val != min_val:
                normalized[metric] = (val - min_val) / (max_val - min_val)
            else:
                normalized[metric] = 0.5  

        categories = [m.replace("avg_", "").upper() for m in radar_metrics]
        values = list(normalized.values())
        values += values[:1]  

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=player_selected,
            line_color="#5d36eb"
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
            ),
            showlegend=False,
            title=f"{player_selected}'s Performance Profile"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 📊 PERFORMANCE BY AGENT
        st.subheader("📊 Performance by Agent")
        df_agent_perf = load_data(f"SELECT * FROM view_player_by_agent WHERE player_name = '{player_selected}';")
        display_df(df_agent_perf.drop(["player_id","player_name","team_name"], axis=1))

        if not df_agent_perf.empty:
            sizes = df_agent_perf["games_played_with_agent"]
            labels = df_agent_perf["agent_name"]
            explode_label = labels[sizes.idxmax()]
            fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, pull=[0.1 if a == explode_label else 0 for a in labels])])
            fig.update_layout(title="Agent Usage Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)

        # 🎭 PERFORMANCE BY ROLE
        st.subheader("🎭 Performance by Role")
        df_role_perf = load_data(f"SELECT * FROM view_player_by_role WHERE player_name = '{player_selected}';")
        display_df(df_role_perf.drop(["player_id","player_name","team_name"], axis=1))

        if not df_role_perf.empty:
            sizes = df_role_perf["games_played_in_role"]
            labels = df_role_perf["role"]
            explode_label = labels[sizes.idxmax()]
            fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, pull=[0.1 if a == explode_label else 0 for a in labels])])
            fig.update_layout(title="Role Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)

# 🔫 AGENTS TAB
elif choice == "🔫 Agents":
    st.header("🔫 Agent Performance Overview")

    df_agents = load_data("SELECT * FROM view_agent_overview;")
    display_df(df_agents)

    role_colors = {
        "Duelist": "#ff6384",
        "Initiator": "#36a2eb",
        "Controller": "#9966ff",
        "Sentinel": "#ffcd56"
    }

    for role in ["Duelist", "Initiator", "Controller", "Sentinel"]:
        subset = df_agents[df_agents["role"] == role]
        if not subset.empty:
            fig = go.Figure(go.Bar(
                x=subset["win_percent_with_agent"],
                y=subset["agent_name"],
                orientation="h",
                marker=dict(color=role_colors.get(role, "#aaa")),
                text=subset["win_percent_with_agent"].round(1),
                textposition="auto"
            ))
            fig.update_layout(title=f"{role} Agents by Win %", xaxis_title="Win %", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

# 🏅 LEADERBOARDS TAB
elif choice == "🏅 Leaderboards":
    st.header("🏅 Player Leaderboards")

    df_leader = load_data("SELECT * FROM view_player_aggregate;")
    metric = st.selectbox("Metric to Rank Players:", ["avg_rating", "avg_acs", "avg_kills", "avg_assists", "avg_hs"])
    top_n = st.slider("Show Top N Players", 5, 50, 10)
    df_top = df_leader.sort_values(by=metric, ascending=False).head(top_n)
    display_df(df_top[["player_name", "team_name", metric, "games_played"]])

    fig = go.Figure(go.Histogram(x=df_leader[metric], nbinsx=25, marker_color="#4bc0c0"))
    fig.update_layout(title=f"Distribution of {metric.title()} among Players", xaxis_title=metric.title(), yaxis_title="Number of Players")
    st.plotly_chart(fig, use_container_width=True)
