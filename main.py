from GMAC_Scraper import GMAC_Scraper

year_to_scrape = 2023
gmac_url = f"https://greatmidwestsports.com/stats.aspx?path=mbball&year={year_to_scrape}"
scraper = GMAC_Scraper(gmac_url)
scraper.scrape()
