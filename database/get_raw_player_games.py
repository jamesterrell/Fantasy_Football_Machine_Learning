import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
from scrape import get_all_stats
pd.set_option('display.max_columns', 70)

URL = r"https://www.pro-football-reference.com/years/2023/fantasy.htm"
res = requests.get(URL, verify=False)
soup = BS(res.content, "html.parser")
table = soup.find_all("td", {"class": "left"})
players = [td.get('data-append-csv') for td in table]
players_final = [value for value in players if value is not None]
player_codes = [f"{value[0]}/{value}" for value in players_final]

stats = [get_all_stats(i) for i in player_codes[0:180]]

df_raw_stats = pd.concat(stats)
df_raw_stats.to_csv(r'database/player_game_stats.csv')