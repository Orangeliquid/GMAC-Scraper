import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Testing of this file specifically
json_file = "2023-2024 Men's Basketball Overall Statistics 2024-10-12.json"
teams_in_league = 13
# Load the JSON data
with open(json_file, "r") as file:
    data = json.load(file)

top_lvl_key = list(data.keys())[0]


def extract_keys(data_passed, level_name):
    try:
        return list(data_passed[level_name].keys())
    except KeyError:
        return f"{level_name} not found in JSON."


def get_avg_stat(data_passed, structure_list):
    # Navigate through the nested structure dynamically
    data_lvl = data_passed[top_lvl_key]
    for key in structure_list[:-1]:  # Traverse all but the last key
        data_lvl = data_lvl[key]

    # Now, data_lvl is the level where 'rows' is located
    df_data = pd.DataFrame(data_lvl['rows'])

    # Clean the DataFrame: Convert specified column to appropriate data type
    df_data[structure_list[-1]] = pd.to_numeric(df_data[structure_list[-1]])

    # Calculate the average points per game (assuming 13 games for now)
    results = df_data[structure_list[-1]].sum() / len(df_data)  # Use len(df_data) for dynamic game count
    return results


structured_averages = {}
# Use League Averages: You'll need to calculate league averages for the following statistics to normalize the PER:
lp_avg_games_played_structure = ["Team Stats", "Scoring", "Offense", 'G']
lp_avg_games_played = get_avg_stat(data, lp_avg_games_played_structure)
print(f"Avg Games Played: {lp_avg_games_played}")
structured_averages["Avg_Games_Played"] = lp_avg_games_played

# Points | Team Stats - Scoring - Offense - AVG/G
lp_avg_points_per_game_structure = ["Team Stats", "Scoring", "Offense", 'AVG/G']
lp_avg_points_per_game = get_avg_stat(data, lp_avg_points_per_game_structure)
print(f"Avg Points PG: {lp_avg_points_per_game}")
structured_averages["Avg_Points_PG"] = lp_avg_points_per_game

# Assists | Team Stats - Misc - Assists - AVG/G
lp_avg_assists_per_game_structure = ["Team Stats", "Misc", "Assists", "AVG/G"]
lp_avg_assists_per_game = get_avg_stat(data, lp_avg_assists_per_game_structure)
print(f"Avg Assists PG: {lp_avg_assists_per_game}")
structured_averages["Avg_Assists_PG"] = lp_avg_assists_per_game

# Rebounds | Team Stats - Rebounding - Combined Team Rebounds - AVG/G
lp_avg_rebounds_per_game_structure = ["Team Stats", "Rebounding", "Combined Team Rebounds", "AVG/G"]
lp_avg_rebounds_per_game = get_avg_stat(data, lp_avg_rebounds_per_game_structure)
print(f"Avg Rebounds PG: {lp_avg_rebounds_per_game}")
structured_averages["Avg_Rebounds_PG"] = lp_avg_rebounds_per_game

# Field Goals Made (FGM) | Team Stats - Field Goals - Team FG Percentage - FGM
lp_avg_fgm_per_game_structure = ["Team Stats", "Field Goals", "Team FG Percentage", "FGM"]
lp_avg_fgm_per_game = get_avg_stat(data, lp_avg_fgm_per_game_structure) / lp_avg_games_played
print(f"Avg FGM PG: {lp_avg_fgm_per_game}")
structured_averages["Avg_FGM_PG"] = lp_avg_fgm_per_game

# Field Goals Attempted (FGA) | Team Stats - Field Goals - Team FG Percentage - FGA
lp_avg_fga_per_game_structure = ["Team Stats", "Field Goals", "Team FG Percentage", "FGA"]
lp_avg_fga_per_game = get_avg_stat(data, lp_avg_fga_per_game_structure) / lp_avg_games_played
print(f"Avg FGA PG: {lp_avg_fga_per_game}")
structured_averages["Avg_FGA_PG"] = lp_avg_fga_per_game

# Free Throws Made (FTM) | Team Stats - Free Throws - Team FT Percentage - FTM
lp_avg_ftm_per_game_structure = ["Team Stats", "Free Throws", "Team FT Percentage", "FTM"]
lp_avg_ftm_per_game = get_avg_stat(data, lp_avg_ftm_per_game_structure) / lp_avg_games_played
print(f"Avg FTM PG: {lp_avg_ftm_per_game}")
structured_averages["Avg_FTM_PG"] = lp_avg_ftm_per_game

# Free Throws Attempted (FTA) | Team Stats - Free Throws - Team FT Percentage - FTA
lp_avg_fta_per_game_structure = ["Team Stats", "Free Throws", "Team FT Percentage", "FTA"]
lp_avg_fta_per_game = get_avg_stat(data, lp_avg_fta_per_game_structure) / lp_avg_games_played
print(f"Avg FTA PG: {lp_avg_fta_per_game}")
structured_averages["Avg_FTA_PG"] = lp_avg_fta_per_game

# Turnovers (TO) | Team Stats - Turnovers - Turnover Margin - AVG
lp_avg_to_per_game_structure = ["Team Stats", "Turnovers", "Turnover Margin", "AVG"]
lp_avg_to_per_game = get_avg_stat(data, lp_avg_to_per_game_structure)
print(f"Avg TO PG: {lp_avg_to_per_game}")
structured_averages["Avg_TO_PG"] = lp_avg_to_per_game

# Steals (STL) | Team Stats - Misc - Steals - AVG/G
lp_avg_stl_per_game_structure = ["Team Stats", "Misc", "Steals", "AVG/G"]
lp_avg_stl_per_game = get_avg_stat(data, lp_avg_stl_per_game_structure)
print(f"Avg STL PG: {lp_avg_stl_per_game}")
structured_averages["Avg_STL_PG"] = lp_avg_stl_per_game

# Blocks (BLK) | Team Stats - Misc - Blocked Shots - AVG/G
lp_avg_blk_per_game_structure = ["Team Stats", "Misc", "Blocked Shots", "AVG/G"]
lp_avg_blk_per_game = get_avg_stat(data, lp_avg_blk_per_game_structure)
print(f"Avg BLK PG: {lp_avg_blk_per_game}")
structured_averages["Avg_BLK_PG"] = lp_avg_blk_per_game

# Personal Fouls (PF) | Game Highs - Team - Fouls - PF
lp_avg_pf_per_game_structure = ["Game Highs", "Team", "Fouls", "PF"]
lp_avg_pf_per_game = get_avg_stat(data, lp_avg_pf_per_game_structure)
print(f"Avg PF PG: {lp_avg_pf_per_game}")
structured_averages["Avg_PF_PG"] = lp_avg_pf_per_game

print(structured_averages)

# ------------------------------------------------------------------------------------------
# Player stats
# PTS = 118
# FGM = 40
# FGA = 101
# OREB = 18
# DREB = 55
# AST = 15
# STL = 8
# BLK = 6
# PF = 14
# TO = 12
# MP = 257

# # Calculate PER
# PER = (1 / MP) * (
#     PTS + 0.4 * FGM - 0.7 * FGA +
#     0.7 * OREB + 0.3 * DREB +
#     STL + 0.7 * AST + 0.7 * BLK -
#     0.4 * PF - TO
# )
#
# print(f"JeJuan Weatherspoon's PER: {PER:.2f}")
