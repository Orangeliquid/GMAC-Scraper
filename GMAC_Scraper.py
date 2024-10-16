import json
from collections import defaultdict
from curl_cffi import requests as cureq
from bs4 import BeautifulSoup
from datetime import datetime


class GMAC_Scraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.main_content = None
        self.article_title = None
        self.structured_data = {}
        self.a_tags_list = []
        self.table_data_list = []

    # Method to fetch and parse the page
    def fetch_page(self):
        response = cureq.get(self.url, impersonate="chrome")
        self.soup = BeautifulSoup(response.content, 'html.parser')

    # Extract main content
    def extract_main_content(self):
        if not self.soup:
            raise Exception("Soup is not initialized. Call fetch_page() first.")
        self.main_content = self.soup.find(id="main-content")
        return self.main_content

    # Extract the main h2 article title
    def get_article_title(self):
        if not self.main_content:
            raise Exception("Main content is not available. Call extract_main_content() first.")
        h2_tags = self.main_content.find_all('h2')
        if h2_tags:
            self.article_title = h2_tags[0].get_text(strip=True)
        return self.article_title

    # Extract the category titles
    def get_category_titles(self):
        if not self.main_content:
            raise Exception("Main content is not available. Call extract_main_content() first.")
        main_category_titles = []
        header_div = self.main_content.find('header').find('div')
        if header_div:
            ul = header_div.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag:
                        main_category_titles.append(a_tag.get_text(strip=True))
        return main_category_titles

    # Extract all a tags from sections
    def get_a_tags(self):
        if not self.main_content:
            raise Exception("Main content is not available. Call extract_main_content() first.")
        sections = self.main_content.find_all('section')
        for section in sections:
            sidearm_tabs_div = section.find('div', class_='sidearm-tabs')
            if sidearm_tabs_div:
                ul = sidearm_tabs_div.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        a_tag = li.find('a')
                        if a_tag:
                            self.a_tags_list.append(a_tag)
        return self.a_tags_list

    # Extract tables and their data
    def get_table_titles_and_data(self):
        if not self.main_content:
            raise Exception("Main content is not available. Call extract_main_content() first.")
        h5_tags = self.main_content.find_all('h5')
        tables = self.main_content.find_all('table')

        if len(h5_tags) == 0 or len(tables) == 0:
            return self.table_data_list

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
                if cells[0] == "":
                    cells[0] = count
                count += 1

                if len(cells) != len(column_headers):
                    print(f"Warning: Row has {len(cells)} cells but there are {len(column_headers)} headers.")
                    continue

                row_dict = dict(zip(column_headers, cells))
                rows_data.append(row_dict)

            table_data['rows'] = rows_data
            self.table_data_list.append(table_data)
            table_index += 1

        return self.table_data_list

    # Process all sections
    def process_sections(self, a_tags_list: list, table_data_list: list, table_counts: list, start_idx=0) -> tuple:
        structured_section = defaultdict(dict)
        table_index = start_idx

        for i in range(len(a_tags_list)):
            subheading = a_tags_list[i].get_text(strip=True)
            num_tables = table_counts[i]

            # Check if table_index is going out of bounds
            if table_index + num_tables > len(table_data_list):
                print(f"Warning: Not enough tables left to process for subheading {subheading}.")
                break

            for j in range(num_tables):
                table_data = table_data_list[table_index]
                title = table_data['title']
                structured_section[subheading][title] = table_data
                table_index += 1

        return structured_section, table_index

    # Convert the structured data to JSON and save it
    def to_json(self, data, file_title):
        json_data = json.dumps(data, indent=4)
        with open(file_title, 'w') as json_file:
            json_file.write(json_data)
        return f"{file_title} written successfully."

    # New method to orchestrate the scraping workflow
    def scrape(self):
        self.fetch_page()
        self.extract_main_content()
        article_title = self.get_article_title()
        category_titles = self.get_category_titles()
        a_tags = self.get_a_tags()
        table_data = self.get_table_titles_and_data()

        print(f"Article Title: {article_title}")
        print(f"Category Titles: {category_titles}")
        print(f"Found {len(a_tags)} a tags.")
        print(f"Total Tables Extracted: {len(table_data)}")

        # Define subheadings and number of tables per subheading
        team_stats_subheadings = self.a_tags_list[:7]
        team_stats_table_per_subheading = [3, 2, 3, 2, 5, 2, 4]

        # Process Team Stats
        team_stats_section, table_idx = self.process_sections(a_tags_list=team_stats_subheadings,
                                                              table_data_list=table_data,
                                                              table_counts=team_stats_table_per_subheading)
        self.structured_data["Team Stats"] = dict(team_stats_section)

        # Leaders Subheadings and table counts
        leaders_subheadings = self.a_tags_list[7:13]
        leaders_table_per_subheading = [1, 1, 4, 2, 2, 1]

        # Process Leaders Stats
        leaders_section, table_idx = self.process_sections(a_tags_list=leaders_subheadings,
                                                           table_data_list=table_data,
                                                           table_counts=leaders_table_per_subheading,
                                                           start_idx=table_idx)
        self.structured_data["Leaders"] = dict(leaders_section)

        # Find the "Offense" table under the "Scoring" section
        offense_table = team_stats_section.get('Scoring', {}).get('Offense', None)

        if not offense_table:
            raise Exception("Offense table not found in Team Stats.")

        # Get the number of teams in conference by counting the rows in the "Offense" table
        num_teams = len(offense_table['rows'])  # Count the number of rows to get the number of teams

        # Adjust Results table per subheading dynamically
        results_table_per_subheading = [1, num_teams]

        # Process Results Stats
        results_subheadings = self.a_tags_list[13:15]
        results_section, table_idx = self.process_sections(a_tags_list=results_subheadings,
                                                           table_data_list=table_data,
                                                           table_counts=results_table_per_subheading,
                                                           start_idx=table_idx)
        self.structured_data["Results"] = dict(results_section)

        # Game Highs Subheadings and table counts
        game_highs_subheadings = self.a_tags_list[15:]
        game_highs_table_per_subheading = [16, 0]

        # Process Game Highs Stats
        game_highs_section, table_idx = self.process_sections(a_tags_list=game_highs_subheadings,
                                                              table_data_list=table_data,
                                                              table_counts=game_highs_table_per_subheading,
                                                              start_idx=table_idx)
        self.structured_data["Game Highs"] = dict(game_highs_section)

        # Convert defaultdict to regular dict for JSON serialization
        all_structured_data = {k: dict(v) for k, v in self.structured_data.items()}

        # Add the article_title as the top-level key in the JSON structure
        final_json_structure = {self.article_title: all_structured_data}

        # Get current date
        now = datetime.now()
        current_date = now.date()  # Current date

        self.to_json(data=final_json_structure, file_title=f"{self.article_title} {current_date}.json")
