import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-darkgrid")
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from dateutil.relativedelta import relativedelta
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from dataclasses import dataclass


@dataclass
class Predict:
    df: pd.DataFrame
    player: str
    steps: int
    regressor: object
    lags: int

    def __post_init__(self):
        self.error_players = []
        self.data = self.df.loc[self.df["PLAYER"] == self.player]
        self.data["FORECAST_DATE"] = pd.date_range(
            "2018-01-01", periods=len(self.data), freq="MS"
        )
        self.data["FORECAST_DATE"] = pd.to_datetime(
            self.data["FORECAST_DATE"], format="%Y-%m-%d"
        )
        self.data = self.data.set_index("FORECAST_DATE")
        self.data = self.data.asfreq("MS")
        self.data = self.data["PPR"]
        self.length = len(self.data)
        if self.lags*2 > int(self.length):
            print('Not enough data. Adjusting lags.')
            self.lags = int(round(self.length / 2, 0) - 1)
            self.steps = self.lags
        
        if int(self.length) == 2:
            print('Not enough data. Adjusting lags.')
            self.lags = 1
            self.steps = 1

        self.end_train = max(self.data.index) - relativedelta(months=self.lags - 1)

    def eval(self):
        forecaster = ForecasterAutoreg(
            regressor=self.regressor(random_state=123), lags=self.lags
        )

        forecaster.fit(
            y=self.data.loc[
                : max(self.data.index) - relativedelta(months=self.lags - 1)
            ]
        )
        predictions = forecaster.predict(steps=self.steps)
        error_mape = mean_absolute_percentage_error(
            y_true=self.data.loc[self.end_train :], y_pred=predictions
        )
        error_rsme = np.sqrt(
            mean_squared_error(
                y_true=self.data.loc[self.end_train :], y_pred=predictions
            )
        )
        self.results = [
            self.player,
            np.sum(self.data.loc[self.end_train :]),
            np.sum(predictions),
            abs(np.sum(self.data.loc[self.end_train :]) - np.sum(predictions)) / np.sum(self.data.loc[self.end_train :]),
            error_mape,
            error_rsme,
            np.size(self.data.loc[self.end_train :]),
            self.lags,
            forecaster.regressor,
        ]

        columns = [
            "PLAYER",
            "ACTUAL SEASON TOTAL",
            "PREDICTED",
            "SEASON MAPE",
            "GAME MAPE",
            "GAME RSME",
            "GAMES PREDICTED",
            "LAGS",
            "REGRESSOR",
        ]

        # Create a DataFrame with a single row and the specified columns
        result_df = pd.DataFrame([self.results], columns=columns)
        return result_df
   
