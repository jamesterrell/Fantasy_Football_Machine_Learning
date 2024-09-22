import pandas as pd

def create_summary_stats(data: pd.DataFrame, combine_with: pd.DataFrame):
    data['Rolling_3_Avg'] = data.groupby('PLAYER')['PPR'].rolling(3).mean().reset_index(level=0, drop=True)
    data['Rolling_5_Avg'] = data.groupby('PLAYER')['PPR'].rolling(5).mean().reset_index(level=0, drop=True)
    data['Rolling_8_Avg'] = data.groupby('PLAYER')['PPR'].rolling(8).mean().reset_index(level=0, drop=True)
    data['Rolling_8_Stddev'] = data.groupby('PLAYER')['PPR'].rolling(8).std().reset_index(level=0, drop=True)

    # Step 2: Get the last rolling averages for each player (last game played)
    df_rolling = data.groupby('PLAYER').agg({
        'Rolling_3_Avg': 'last',
        'Rolling_5_Avg': 'last',
        'Rolling_8_Avg': 'last',
        'Rolling_8_Stddev': 'last',
    }).reset_index()

    # Step 3: Merge with df_preds to get projected points alongside rolling averages
    df_combined = pd.merge(combine_with, df_rolling, on='PLAYER', how='left')
    return df_combined

def create_streamlit_table(data: pd.DataFrame, PPR_adj: float, pass_td_adj: int):
    data.iloc[:, 0:2] = data.iloc[:, 0:2].astype(float)
    data.iloc[:, 3:5] = data.iloc[:, 3:5].astype(float)
    data.iloc[:, 6] = data.iloc[:, 6].astype(float)
    data.iloc[:, 11:47] = data.iloc[:, 11:47].astype(float)
    data.fillna(0, inplace=True)
    try: 
        data["PPR"] = (
            PPR_adj * data["RECEIVING_REC"]
            + (1 / 10) * data["RECEIVING_YDS"]
            + (6) * data["RECEIVING_TD"]
            + (1 / 10) * data["RUSHING_YDS"]
            + (6) * data["RUSHING_TD"]
            + (1 / 25) * data['PASSING_YDS']
            + (pass_td_adj) * data['PASSING_TD']
        )
    except KeyError:
                data["PPR"] = (
            PPR_adj * data["RECEIVING_REC"]
            + (1 / 10) * data["RECEIVING_YDS"]
            + (6) * data["RECEIVING_TD"]
            + (1 / 10) * data["RUSHING_YDS"]
            + (6) * data["RUSHING_TD"]
        )
    return data