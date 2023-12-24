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
    players: list
    steps: int
    regressor: object
    lags: int

    def __post_init__(self):
        self.results = []

    def predict(self, player: str):
        self.data = self.df.loc[self.df["PLAYER"] == player]
        self.data["FORECAST_DATE"] = pd.date_range(
            "2018-01-01", periods=len(self.data), freq="MS"
        )
        self.data["FORECAST_DATE"] = pd.to_datetime(
            self.data["FORECAST_DATE"], format="%Y-%m-%d"
        )
        self.data = self.data.set_index("FORECAST_DATE")
        self.data = self.data.asfreq("MS")
        self.data = self.data["PPR"]
        end_train = max(self.data.index) - relativedelta(months=self.steps - 1)
        forecaster = ForecasterAutoreg(
            regressor=self.regressor(random_state=123), lags=self.lags
        )

        forecaster.fit(
            y=self.data.loc[
                : max(self.data.index) - relativedelta(months=self.steps - 1)
            ]
        )
        predictions = forecaster.predict(steps=self.steps)
        error_mape = mean_absolute_percentage_error(
            y_true=self.data.loc[end_train:], y_pred=predictions
        )
        self.results.append(
            [
                player,
                np.sum(self.data.loc[end_train:]),
                np.sum(predictions),
                abs(np.sum(self.data.loc[end_train:]) - np.sum(predictions))
                / np.sum(self.data.loc[end_train:]),
                error_mape,
                np.size(self.data.loc[end_train:]),
                self.lags,
                forecaster.regressor,
            ]
        )

    def predict_all(self):
        for player in self.players:
            try:
                self.predict(player=player)

            except ValueError as e:
                if (
                    "(0)" in str(e)
                    or "(1)" in str(e)
                    or "(2)" in str(e)
                    or "(3)" in str(e)
                ):
                    pass
                else:
                    self.lags = 3
                    self.predict(player=player)

        return pd.DataFrame(
            self.results,
            columns=[
                "PLAYER",
                "ACTUAL SEASON TOTAL",
                "PREDICTED",
                "SEASON MAPE",
                "GAME MAPE",
                "GAMES PREDICTED",
                "LAGS",
                "REGRESSOR",
            ],
        )
