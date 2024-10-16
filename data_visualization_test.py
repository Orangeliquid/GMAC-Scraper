import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Testing of this file specifically
json_file = "2023-2024 Men's Basketball Overall Statistics 2024-10-12.json"
# Load the JSON data
with open(json_file, "r") as file:
    data = json.load(file)

# Extract the main section titles
top_level_key = "2023-2024 Men's Basketball Overall Statistics"
if top_level_key in data:
    section_titles = list(data[top_level_key].keys())
else:
    section_titles = []

# Display the section titles
# print("Section Titles:", section_titles)

section_dict = {}
for section in section_titles:
    # print("_____________________________")
    subsection_list = list(data[top_level_key][section].keys())
    # print(subsection_list)
    section_dict[section] = subsection_list

# print(f"This is section_dict: {section_dict}")

subtitle_dict = {}
for section in section_dict:
    for subtitle in section_dict[section]:
        # print("_____________________________")
        # print(subtitle)
        subtitle_list = list(data[top_level_key][section][subtitle].keys())
        subtitle_dict[subtitle] = subtitle_list

# print(f"This is subtitle_dict = {subtitle_dict}")


def create_bar_chart(main_category, subcategory, table):
    # Navigate to the 'Offense' section and extract rows
    offense_data = data["2023-2024 Men's Basketball Overall Statistics"][main_category][subcategory][table]["rows"]
    offense_column_headers = data["2023-2024 Men's Basketball Overall Statistics"][main_category][subcategory][table]["column_headers"]
    # print(offense_column_headers)

    # Convert the rows into a pandas DataFrame
    df = pd.DataFrame(offense_data)
    print(df)

    column_headers_available = []
    for column_header in offense_column_headers:
        try:
            # example: df['PTS'] = pd.to_numeric(df['PTS'])
            df[column_header] = pd.to_numeric(df[column_header])
            column_headers_available.append(column_header)
            print(f"successfully changed to pd numeric: '{column_header}'")
        except:
            print(f"error cannot process '{column_header}'")

    print(f"Available Y headers: {column_headers_available}")
    y_input = int(input("Please choose a Y header from above - enter the number of item above: "))
    y_input = column_headers_available[y_input - 1]
    # print(df)  # To check if the data is loaded correctly

    # Example: Bar chart of teams by total points scored
    # plt.figure(figsize=(10, 6))
    df.plot(kind='bar', x='Team', y=y_input, legend=False, color='skyblue')
    plt.title(f'{table} | {y_input}')
    plt.ylabel(y_input)
    plt.xlabel('Teams')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


create_bar_chart("Team Stats", "Scoring", "Offense")
# ---------------------------------------------------------------------------------------------------------------------
# Scatter plot of Games Played vs Average Points per Game
# sns.scatterplot(data=df, x='G', y='AVG/G', hue='Team', palette='deep')
# plt.title('Games Played vs Average Points per Game')
# plt.show()

# Step 4: Create the sunburst chart
# fig = px.sunburst(
#     df,
#     path=['Team'],  # You can add more hierarchy levels if needed
#     values='PTS',  # Size of the segments
#     color='PTS',  # Color based on points scored
#     color_continuous_scale='Blues',
#     title='Points Scored by Teams in 2023-2024 Season'
# )
#
# # Show the plot
# fig.show()
