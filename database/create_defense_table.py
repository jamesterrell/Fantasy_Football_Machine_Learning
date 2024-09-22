import time
import pandas as pd
from scrape import scrape_defense


def main():
    df_tms = pd.read_csv(r"database\DIM_PLAYER_GAMES.csv")
    replace_dict = {
        "RAV": "BAL",
        "RAM": "LAR",
        "OTI": "TEN",
        "HTX": "HOU",
        "SDG": "LAC",
        "RAI": "LVR",
        "CRD": "ARI",
        "CLT": "IND",
    }
    switched_dict = {value.lower(): key.lower() for key, value in replace_dict.items()}
    teams = df_tms[["TEAM"]].drop_duplicates()
    teams["TEAM"] = teams["TEAM"].str.lower()
    teams.replace(switched_dict, inplace=True)
    teams_list = list(teams["TEAM"])
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]  # will need to change this from year to year
    dfs = []
    for year in years:
        for team in teams_list:
            try:
                df_tm = scrape_defense(year=year, defense=team)
                dfs.append(df_tm)
                time.sleep(6.1)
            except ValueError:
                print(f'no table found for team code "{team}", {year} ')
                time.sleep(6.1)
    dfns_training = pd.concat(dfs)
    dfns_training.replace(replace_dict, inplace=True)
    dfns_training.to_csv(r"database/DIM_DEFENSE.csv")
    pd.read_csv(r"database/DIM_DEFENSE.csv").drop_duplicates().to_csv(
        r"database/DIM_DEFENSE.csv"
    )


if __name__ == "__main__":
    main()
