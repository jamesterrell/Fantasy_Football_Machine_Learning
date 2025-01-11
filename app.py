import streamlit as st
import pandas as pd
from database.scrape import get_all_stats
from modeling.predict import Predict
from st_helpers.table_functions import create_streamlit_table, create_summary_stats
from sklearn.ensemble import RandomForestRegressor

# Load player data
@st.cache_data
def load_player_data():
    return pd.read_csv(r'database\PLAYER_CODE_KEYS.csv')

df_keys = load_player_data()

# Streamlit app
st.title("Fantasy Football Prediction App")

# User input
st.sidebar.header("Settings")
ppr_adj = st.sidebar.selectbox("PPR Adjustment", [1, 0.5, 0])
pass_td_adj = st.sidebar.selectbox("Pass TD Points", [4, 6])
selected_players = st.sidebar.multiselect("Select Players", df_keys['Player'].tolist())
game_count = st.sidebar.selectbox("Games to Project", list(range(1, 17)))

# Run analysis button
if st.sidebar.button("Run Analysis"):
    if selected_players:
        with st.spinner('''
                        Scraping Player Data...
                        Analyzing Past Performance...
                        Projecting Future Performance...
                        Please wait...
                        '''):
        # Filter selected players
            df_select = df_keys.loc[df_keys['Player'].isin(selected_players)]
            
            # Get stats for selected players
            def get_stats():
                stats = [get_all_stats(i) for i in df_select['Player Code']]
                df_raw_stats = pd.concat(stats)
                return df_raw_stats
            
            # Create streamlit table
            st_table = create_streamlit_table(data=get_stats(), PPR_adj=ppr_adj, pass_td_adj=pass_td_adj)
            
            # Make predictions
            player_pred = [
                Predict(
                    df=st_table, player=i, steps=game_count, regressor=RandomForestRegressor, lags=17
                ).predict_season() for i in list(set(st_table['PLAYER']))
            ]
            clean_data = [row for row in player_pred if row is not None]
            
            # Create prediction dataframe
            df_preds = pd.DataFrame(clean_data, columns=['PLAYER', 'Next Game(s) Projection'])
            # Display results
            st.header("Analysis Results")
            summary_stats = create_summary_stats(data=st_table, combine_with=df_preds)
            st.dataframe(summary_stats.reset_index(drop=True))
            
            # Display raw data
            st.header("Raw Data")
            st.dataframe(st_table)
        st.success("Analysis completed successfully!")
    else:
        st.warning("Please select at least one player to run the analysis.")
else:
    st.info("Please select your settings and players, then click 'Run Analysis' to see the results.")