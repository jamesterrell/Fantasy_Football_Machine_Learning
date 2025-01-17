import requests
from bs4 import BeautifulSoup as BS
import re
import pandas as pd
import warnings
import time

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.filterwarnings(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def scrape_sp(player_code: str):
    """
    Scrapes advanced rushing and receiving statistics for a given skill player from Pro Football Reference.

    This function sends an HTTP GET request to the specified URL for the player's advanced statistics,
    parses the HTML content, and returns a DataFrame with cleaned and standardized column names.
    If certain columns related to rushing or receiving statistics are not present, they are added with default values of zero.

    Parameters:
    -----------
    player_code : str
        The code representing the player on the Pro Football Reference website (e.g., "B/BradTo00").

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the player's game-by-game advanced rushing and receiving statistics, with standardized column names.
    """
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
    """
    Scrapes passing statistics for a given quarterback from Pro Football Reference.

    This function sends an HTTP GET request to the specified URL for the player's passing statistics,
    parses the HTML content, and returns a DataFrame with cleaned and standardized column names.
    The function filters out games where the quarterback did not play or was inactive due to various reasons.

    Parameters:
    -----------
    player_code : str
        The code representing the quarterback on the Pro Football Reference website (e.g., "B/BradTo00").

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the quarterback's game-by-game passing statistics, with standardized column names.
    """
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
    """
    Collects and merges advanced rushing/receiving and passing statistics for a given player.

    This function first waits for a brief period to avoid being blocked by the server for making too many requests.
    It then calls the `scrape_sp` function to retrieve advanced rushing/receiving stats, and attempts to call `scrape_qb`
    for passing stats. If successful, the two DataFrames are merged. If a KeyError occurs, default values are assigned
    to missing passing statistics. If an AttributeError occurs, an error message is printed.

    Parameters:
    -----------
    player_code_str : str
        The code representing the player on the Pro Football Reference website (e.g., "B/BradTo00").

    Returns:
    --------
    pd.DataFrame
        A merged DataFrame containing the player's game-by-game statistics, including both rushing/receiving and passing stats.
    """
    time.sleep(6.1)  # you get put in "jail" for more than 10 requests in a minute
    df_np = scrape_sp(player_code=player_code_str)
    try:
        df_p = scrape_qb(player_code=player_code_str)
        df_all = pd.merge(df_np, df_p, how="left", on="DATE", suffixes=["", "_y"])
        columns_to_drop = df_all.filter(like="_y").columns
        df_all = df_all.drop(columns=columns_to_drop)
        print(f"{player_code_str} done.")
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
        print(f"{player_code_str} done.")
        return df_all2
    except AttributeError as e:
        print(player_code_str, str(e))


def scrape_defense(year: int, defense: str):
    """
    Scrapes defensive game-by-game statistics for a specific team in a given year from Pro Football Reference.

    This function sends an HTTP GET request to the specified URL for the team's defensive statistics for the given year,
    parses the HTML content, and returns a DataFrame with cleaned and standardized column names. The DataFrame
    includes statistics such as passing completions, attempts, yards, touchdowns, interceptions, and rushing attempts, yards, and touchdowns.

    Parameters:
    -----------
    year : int
        The year for which the defensive statistics are to be scraped (e.g., 2023).
    defense : str
        The abbreviation of the defensive team (e.g., "NE" for New England Patriots).

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the defensive team's game-by-game statistics for the specified year, with standardized column names.
    """
    URL = f"https://www.pro-football-reference.com/teams/{defense}/{year}/gamelog/"

    res = requests.get(URL, verify=False)

    soup = BS(res.content, "html.parser")

    table = soup.find_all("table", {"id": f"gamelog_opp{year}"})

    test = soup.find_all("td", {"data-stat": "opp"}, limit=17)

    code_list = []
    for i in test:
        html_string = str(i)

        # Regular expression to match the three-letter team code
        match = re.search(r"/teams/([a-z]{3})/", html_string)

        if match:
            team_code = match.group(1)
        else:
            print("No match found")
        code_list.append(team_code)

    df = pd.read_html(str(table))[0]
    flattened_columns = ["_".join(col).strip() for col in df.columns.values]
    df.columns = flattened_columns
    df.rename(
        columns={
            "Unnamed: 0_level_0_Week": "WEEK",
        },
        inplace=True,
    )
    df.columns = df.columns.str.upper()
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace("/", "_")
    df.columns = df.columns.str.replace(".", "")
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.replace("%", "_PCT")
    df["YEAR"] = year
    df["WEEK"] = df["WEEK"].astype(float)
    df["DEF_TEAM"] = defense.upper()
    # the purpose of this is to make sure code_list's length
    # matches up with the rest of the dataframe. The NFL
    # season legnth changed from 16 to 17 in 2021, so we need
    # to account for that here.
    df["OPP_CODE"] = code_list[: len(df["DEF_TEAM"])]
    df["OPP_CODE"] = df["OPP_CODE"].str.upper()

    df_def = df[
        [
            "DEF_TEAM",
            "OPP_CODE",
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
