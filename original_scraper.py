import json
from collections import defaultdict
from curl_cffi import requests as cureq
from bs4 import BeautifulSoup


# Function to fetch and parse the page
def fetch_page(url):
    response = cureq.get(url, impersonate="chrome")
    return BeautifulSoup(response.content, 'html.parser')


# Extract main content
def extract_main_content(soup: BeautifulSoup) -> BeautifulSoup:
    return soup.find(id="main-content")


# Extract the main h2 article title
def get_article_title(main_content_extracted: BeautifulSoup) -> str or None:
    h2_tags = main_content_extracted.find_all('h2')
    if h2_tags:
        return h2_tags[0].get_text(strip=True)
    return None


# Extract the category titles
def get_category_titles(main_content_extracted: BeautifulSoup) -> list:
    main_category_titles = []
    header_div = main_content_extracted.find('header').find('div')
    if header_div:
        ul = header_div.find('ul')
        if ul:
            for li in ul.find_all('li'):
                a_tag = li.find('a')
                if a_tag:
                    main_category_titles.append(a_tag.get_text(strip=True))
    return main_category_titles


# Extract all a tags from sections
def get_a_tags(main_content_extracted: BeautifulSoup) -> list:
    all_a_tags = []
    sections = main_content_extracted.find_all('section')
    for section in sections:
        sidearm_tabs_div = section.find('div', class_='sidearm-tabs')
        if sidearm_tabs_div:
            ul = sidearm_tabs_div.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag:
                        all_a_tags.append(a_tag)
    return all_a_tags


# Extract tables and their data
def get_table_titles_and_data(main_content_extracted: BeautifulSoup) -> list:
    h5_tags = main_content_extracted.find_all('h5')
    tables = main_content_extracted.find_all('table')
    table_data_list = []

    if len(h5_tags) == 0 or len(tables) == 0:
        return table_data_list

    h5_index = 0
    table_index = 0

    for table in tables:
        table_data = {}
        title = None

        # Extract column headers
        thead = table.find('thead')
        column_headers = [th.get_text(strip=True) for th in thead.find_all('th')] if thead else []
        print(f"Column Headers: {column_headers}")

        # Determine table title
        if column_headers and (column_headers[0] == 'Index' or column_headers[0] == 'Date'):
            if h5_index < len(h5_tags):
                title = h5_tags[h5_index].get_text(strip=True)
                h5_index += 1
        elif column_headers:
            title = column_headers[0]

        if not title:
            title = f"Table {table_index}"

        print(f"Table Title: {title}")
        table_data['title'] = title
        table_data['column_headers'] = column_headers  # Add column headers to the data

        # Extract table rows
        tbody = table.find('tbody')
        rows_data = []
        rows = tbody.find_all('tr') if tbody else []

        count = 1
        for row in rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            # if first index is nothing, set index to count
            if cells[0] == "":
                cells[0] = count
            count += 1

            # Map cells to column headers
            if len(cells) != len(column_headers):
                # Handle mismatch in number of cells and headers
                print(f"Warning: Row has {len(cells)} cells but there are {len(column_headers)} headers.")
                continue

            row_dict = dict(zip(column_headers, cells))
            rows_data.append(row_dict)

        table_data['rows'] = rows_data
        table_data_list.append(table_data)

        table_index += 1

    return table_data_list


# Function to process all sections
def process_sections(a_tags_list: list, table_data_list: list, table_counts: list, start_idx=0) -> tuple:
    structured_section = defaultdict(list)
    table_index = start_idx

    for i in range(len(a_tags_list)):
        subheading = a_tags_list[i].get_text(strip=True)
        num_tables = table_counts[i]
        tables = table_data_list[table_index: table_index + num_tables]
        structured_section[subheading] = tables
        table_index += num_tables

    return structured_section, table_index


def to_json(json_dumps: str) -> str:
    # Save to a JSON file
    with open('all_tables_data111.json', 'w') as json_file:
        json_file.write(json_dumps)
    return "all_tables_data.json written"


# Main execution
if __name__ == "__main__":
    gmac_url_2023 = "https://greatmidwestsports.com/stats.aspx?path=mbball&year=2023"
    soup = fetch_page(gmac_url_2023)
    main_content = extract_main_content(soup)

    if main_content:
        # Extract data
        article_title = get_article_title(main_content)
        category_titles = get_category_titles(main_content)
        a_tags = get_a_tags(main_content)
        table_data = get_table_titles_and_data(main_content)

        print(f"Article Title: {article_title}")
        print(f"Category Titles: {category_titles}")
        print(f"Found {len(a_tags)} a tags.")
        print(f"Total Tables Extracted: {len(table_data)}")

        # Define subheadings and number of tables per subheading
        team_stats_subheadings = a_tags[:7]
        team_stats_table_per_subheading = [3, 2, 3, 2, 5, 2, 4]

        # Process Team Stats
        team_stats_section, table_idx = process_sections(team_stats_subheadings, table_data,
                                                         team_stats_table_per_subheading)
        all_structured_data = {"Team Stats": dict(team_stats_section)}

        # Leaders Subheadings and table counts
        leaders_subheadings = a_tags[7:13]
        leaders_table_per_subheading = [1, 1, 4, 2, 2, 1]
        leaders_section, table_idx = process_sections(leaders_subheadings, table_data, leaders_table_per_subheading,
                                                      start_idx=table_idx)
        all_structured_data["Leaders"] = dict(leaders_section)

        # Results Subheadings and table counts
        results_subheadings = a_tags[13:15]
        results_table_per_subheading = [1, 13]
        results_section, table_idx = process_sections(results_subheadings, table_data, results_table_per_subheading,
                                                      start_idx=table_idx)
        all_structured_data["Results"] = dict(results_section)

        # Game Highs Subheadings and table counts
        game_highs_subheadings = a_tags[15:]
        game_highs_table_per_subheading = [16, 0]
        game_highs_section, table_idx = process_sections(game_highs_subheadings, table_data,
                                                         game_highs_table_per_subheading, start_idx=table_idx)
        all_structured_data["Game Highs"] = dict(game_highs_section)

        # Convert defaultdict to regular dict for JSON serialization
        all_structured_data = {k: dict(v) for k, v in all_structured_data.items()}

        # Add the article_title as the top-level key in the JSON structure
        final_json_structure = {article_title: all_structured_data}

        # Output the structured data as JSON
        json_output = json.dumps(final_json_structure, indent=4)
        print(to_json(json_output))

    else:
        print("Error: 'main-content' section not found in the HTML.")

