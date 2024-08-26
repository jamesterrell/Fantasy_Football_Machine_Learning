import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import warnings
import time

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.filterwarnings(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def scrape_sp(player_code: str):
    URL = f"https://www.pro-football-reference.com/players/{player_code}/gamelog/advanced/"
    res = requests.get(URL, verify=False)
    soup = BS(res.content, "html.parser")
    table = soup.find("table", {"id": "advanced_rushing_and_receiving"})
    name = soup.find_all("span", attrs={"itemprop": "name"})
    df = pd.read_html(str(table))[0]
    flattened_columns = ["_".join(col).strip() for col in df.columns.values]
    df.columns = flattened_columns
    df.rename(
        columns={
            "Unnamed: 0_level_0_Rk": "GAME_ORDER",
            "Unnamed: 1_level_0_Year": "YEAR",
            "Unnamed: 2_level_0_Date": "DATE",
            "Unnamed: 3_level_0_G#": "GAME_NUMBER",
            "Unnamed: 4_level_0_Week": "WEEK",
            "Unnamed: 5_level_0_Age": "AGE",
            "Unnamed: 6_level_0_Tm": "TEAM",
            "Unnamed: 8_level_0_Opp": "OPPONENT",
            "Unnamed: 9_level_0_Result": "RESULT",
        },
        inplace=True,
    )
    df.drop(columns=["Unnamed: 7_level_0_Unnamed: 7_level_1"], inplace=True)
    df.columns = df.columns.str.upper()
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace("/", "_")
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.replace("%", "_PCT")
    df = df.loc[df["DATE"].str.contains("-") == True]  # noqa: E712
    df["PLAYER"] = str(name[3].text)
    df.fillna(0, inplace=True)
    if "RUSHING_YDS" not in df.columns:
        df["RUSHING_ATT"] = 0
        df["RUSHING_YDS"] = 0
        df["RUSHING_TD"] = 0
        df["RUSHING_1D"] = 0
        df["RUSHING_YBC"] = 0
        df["RUSHING_YBC_ATT"] = 0
        df["RUSHING_YAC"] = 0
        df["RUSHING_YAC_ATT"] = 0
        df["RUSHING_BRKTKL"] = 0
        df["RUSHING_ATT_BR"] = 0

    if "RECEIVING_YDS" not in df.columns:
        df["RECEIVING_TGT"] = 0
        df["RECEIVING_REC"] = 0
        df["RECEIVING_YDS"] = 0
        df["RECEIVING_TD"] = 0
        df["RECEIVING_1D"] = 0
        df["RECEIVING_YBC"] = 0
        df["RECEIVING_YBC_R"] = 0
        df["RECEIVING_YAC"] = 0
        df["RECEIVING_YAC_R"] = 0
        df["RECEIVING_ADOT"] = 0
        df["RECEIVING_BRKTKL"] = 0
        df["RECEIVING_REC_BR"] = 0
        df["RECEIVING_DROP"] = 0
        df["RECEIVING_DROP_PCT"] = 0
        df["RECEIVING_INT"] = 0
        df["RECEIVING_RAT"] = 0

    df = df[
        [
            "GAME_ORDER",
            "YEAR",
            "DATE",
            "GAME_NUMBER",
            "WEEK",
            "PLAYER",
            "AGE",
            "TEAM",
            "OPPONENT",
            "RESULT",
            "RUSHING_ATT",
            "RUSHING_YDS",
            "RUSHING_TD",
            "RUSHING_1D",
            "RUSHING_YBC",
            "RUSHING_YBC_ATT",
            "RUSHING_YAC",
            "RUSHING_YAC_ATT",
            "RUSHING_BRKTKL",
            "RUSHING_ATT_BR",
            "RECEIVING_TGT",
            "RECEIVING_REC",
            "RECEIVING_YDS",
            "RECEIVING_TD",
            "RECEIVING_1D",
            "RECEIVING_YBC",
            "RECEIVING_YBC_R",
            "RECEIVING_YAC",
            "RECEIVING_YAC_R",
            "RECEIVING_ADOT",
            "RECEIVING_BRKTKL",
            "RECEIVING_REC_BR",
            "RECEIVING_DROP",
            "RECEIVING_DROP_PCT",
            "RECEIVING_INT",
            "RECEIVING_RAT",
        ]
    ]
    return df


def scrape_qb(player_code: str):
    URL = f"https://www.pro-football-reference.com/players/{player_code}/gamelog"
    res = requests.get(URL, verify=False)
    soup = BS(res.content, "html.parser")
    table_pass = soup.find_all("table")
    df_pass = pd.read_html(str(table_pass))[0]
    flattened_columns = ["_".join(col).strip() for col in df_pass.columns.values]
    df_pass.columns = flattened_columns
    df_pass.rename(
        columns={
            "Unnamed: 0_level_0_Rk": "GAME_ORDER",
            "Unnamed: 1_level_0_Year": "YEAR",
            "Unnamed: 2_level_0_Date": "DATE",
            "Unnamed: 3_level_0_G#": "GAME_NUMBER",
            "Unnamed: 4_level_0_Week": "WEEK",
            "Unnamed: 5_level_0_Age": "AGE",
            "Unnamed: 6_level_0_Tm": "TEAM",
            "Unnamed: 8_level_0_Opp": "OPPONENT",
            "Unnamed: 9_level_0_Result": "RESULT",
            "Unnamed: 10_level_0_GS": "GAME_STARTED",
        },
        inplace=True,
    )
    df_pass.drop(columns=["Unnamed: 7_level_0_Unnamed: 7_level_1"], inplace=True)
    df_pass.columns = df_pass.columns.str.upper()
    df_pass.columns = df_pass.columns.str.replace(".", "")
    df_pass.columns = df_pass.columns.str.replace("/", "_")
    df_pass.columns = df_pass.columns.str.replace(".", "")
    df_pass.columns = df_pass.columns.str.replace(" ", "_")
    df_pass.columns = df_pass.columns.str.replace("%", "_PCT")
    df_pass = df_pass.loc[df_pass["DATE"].str.contains("-") == True]  # noqa: E712
    df_pass = df_pass.loc[df_pass["GAME_STARTED"].str.contains("Did Not Play") == False]  # noqa: E712
    df_pass = df_pass.loc[df_pass["GAME_STARTED"].str.contains("Inactive") == False]  # noqa: E712
    df_pass = df_pass.loc[
        df_pass["GAME_STARTED"].str.contains("Injured Reserve") == False  # noqa: E712
    ]
    df_pass = df_pass.loc[
        df_pass["GAME_STARTED"].str.contains("COVID-19 List") == False  # noqa: E712
    ]
    df_pass = df_pass.filter(
        items=[
            "GAME_ORDER",
            "YEAR",
            "DATE",
            "GAME_NUMBER",
            "WEEK",
            "AGE",
            "TEAM",
            "OPPONENT",
            "RESULT",
            "PASSING_CMP",
            "PASSING_ATT",
            "PASSING_CMP_PCT",
            "PASSING_YDS",
            "PASSING_TD",
            "PASSING_INT",
            "PASSING_RATE",
            "PASSING_SK",
            "PASSING_YDS1",
            "PASSING_Y_A",
            "PASSING_AY_A",
        ]
    )
    df_pass.fillna(0, inplace=True)
    return df_pass


def get_all_stats(player_code_str: str):
    time.sleep(6.1) # you get put in "jail" for more than 10 requests in a minute
    df_np = scrape_sp(player_code=player_code_str)
    try:
        df_p = scrape_qb(player_code=player_code_str)
        df_all = pd.merge(df_np, df_p, how="left", on="DATE", suffixes=["", "_y"])
        columns_to_drop = df_all.filter(like="_y").columns
        df_all = df_all.drop(columns=columns_to_drop)
        print(f'{player_code_str} done.')
        return df_all
    except KeyError:
        df_np["PASSING_CMP"] = 0
        df_np["PASSING_ATT"] = 0
        df_np["PASSING_CMP_PCT"] = 0
        df_np["PASSING_YDS"] = 0
        df_np["PASSING_TD"] = 0
        df_np["PASSING_INT"] = 0
        df_np["PASSING_RATE"] = 0
        df_np["PASSING_SK"] = 0
        df_np["PASSING_YDS1"] = 0
        df_np["PASSING_Y_A"] = 0
        df_np["PASSING_AY_A"] = 0
        df_all2 = df_np
        print(f'{player_code_str} done.')
        return df_all2
    except AttributeError as e:
        print(player_code_str, str(e))

def scrape_defense(year, defense):
    URL = f"https://www.pro-football-reference.com/teams/{defense}/{year}/gamelog/"

    res = requests.get(URL, verify=False)

    soup = BS(res.content, "html.parser")

    table = soup.find_all("table", {"id": f"gamelog_opp{year}"})
    df = pd.read_html(str(table))[0]
    flattened_columns = ["_".join(col).strip() for col in df.columns.values]
    df.columns = flattened_columns
    df.rename(
        columns={
            "Unnamed: 0_level_0_Week": "WEEK",
        },
        inplace=True,
    )
    # df.drop(columns=["Unnamed: 7_level_0_Unnamed: 7_level_1"], inplace=True)
    df.columns = df.columns.str.upper()
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace("/", "_")
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.replace("%", "_PCT")

    # df.fillna(0, inplace=True)
    df["YEAR"] = year
    df["WEEK"] = df["WEEK"].astype(float)
    df["DEF_TEAM"] = defense.upper()
    df
    df_def = df[
        [
            "DEF_TEAM",
            "YEAR",
            "WEEK",
            "SCORE_OPP",
            "PASSING_CMP",
            "PASSING_ATT",
            "PASSING_YDS",
            "PASSING_TD",
            "PASSING_INT",
            "PASSING_SK",
            "PASSING_Y_A",
            "PASSING_NY_A",
            "PASSING_CMP_PCT",
            "PASSING_RATE",
            "RUSHING_ATT",
            "RUSHING_YDS",
            "RUSHING_Y_A",
            "RUSHING_TD",
        ]
    ]
    
    return df_def
