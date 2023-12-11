import pandas as pd

df_stats = pd.read_csv(r'database/player_game_stats.csv')
df_stats['GAME_ORDER'] = df_stats['Unnamed: 0']
df_stats.drop(columns=['Unnamed: 0'], inplace=True)
df_stats.iloc[:,0:2] = df_stats.iloc[:,0:2].astype(float)
df_stats.iloc[:,3:5] = df_stats.iloc[:,3:5].astype(float)
df_stats.iloc[:,6] = df_stats.iloc[:,6].astype(float)
df_stats.iloc[:,11:47] = df_stats.iloc[:,11:47].astype(float)
df_stats.to_csv('database/DIM_PLAYER_GAMES.csv')