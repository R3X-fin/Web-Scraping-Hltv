from bs4 import BeautifulSoup
import cloudscraper
import re

# Function to get player stats from a game page
def get_player_stats(game_url, scraper):
    response = scraper.get(game_url)
    game_bs = BeautifulSoup(response.text, "lxml")
    
    # Extract player stats for the game
    player_rows = game_bs.select("tr:has(td.players)")
    player_stats = []
    for row in player_rows:
        try:
            name = row.select_one("td.players")
            k_d = row.select_one("td.kd.text-center")
            plus_minus = row.select_one("td.plus-minus.text-center.gtSmartphone-only")
            adr = row.select_one("td.adr.text-center")
            kast = row.select_one("td.kast.text-center")
            rating_text = row.select_one("td.rating.text-center")
            
            if name and k_d and plus_minus and adr and kast and rating_text:
                name = name.get_text().strip()
                k_d = k_d.get_text().strip()
                plus_minus = plus_minus.get_text().strip()
                adr = adr.get_text().strip()
                kast = kast.get_text().strip().replace('%', '')
                rating = float(re.sub(r'[^\d.]', '', rating_text.get_text().strip()))
                
                # Check if ADR and KAST are numeric to filter out teams
                if adr.replace('.', '', 1).isdigit() and kast.replace('.', '', 1).isdigit():
                    stats = {
                        "name": name,
                        "k_d": k_d,
                        "plus_minus": plus_minus,
                        "adr": adr,
                        "kast": kast,
                        "rating": rating
                    }
                    player_stats.append(stats)
        except (AttributeError, ValueError) as e:
            # Skip rows without complete stats
            continue
    
    return player_stats

# Main function to scrape HLTV stats for a chosen date
def scrape_hltv_stats(date):
    scraper = cloudscraper.create_scraper()

    response = scraper.get(f"http://www.hltv.org/results?startDate={date}&endDate={date}")
    bs = BeautifulSoup(response.text, "lxml")

    # Find all game links within the results-sublist class
    results_sublist = bs.find_all("div", class_="results-sublist")
    game_links = []

    for sublist in results_sublist:
        links = sublist.select("a.a-reset[href*='/matches/']")
        game_links.extend(links)

    all_stats = []

    for link in game_links:
        game_url = "http://www.hltv.org" + link["href"]
        player_stats = get_player_stats(game_url, scraper)
        all_stats.extend(player_stats)

    # Use a dictionary to keep track of the first stats for each player
    player_dict = {}
    for stats in all_stats:
        name = stats['name']
        if name not in player_dict:
            player_dict[name] = stats
            # Debugging: Print when a player is added to the dictionary
            print(f"Added player in dictionary: {name} with stats: {stats}")

    # Convert the dictionary values to a list
    unique_stats = list(player_dict.values())

    # Find the best ratings from the day
    if unique_stats:
        best_stats = sorted(unique_stats, key=lambda x: x["rating"], reverse=True)[:5]
        print("\nBest HLTV Stats for the chosen date:")
        for stats in best_stats:
            print(f"Player: {stats['name']}")
            print(f"  K-D: {stats['k_d']}")
            print(f"  +/-: {stats['plus_minus']}")
            print(f"  ADR: {stats['adr']}")
            print(f"  KAST: {stats['kast']}")
            print(f"  Rating: {stats['rating']}\n")
    else:
        print("No stats found for the chosen date.")

# Input the date you want to search for
date = input("Enter the date you want to search for (YYYY-MM-DD): ")
scrape_hltv_stats(date)