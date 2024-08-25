from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from dateutil.relativedelta import relativedelta
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from dataclasses import dataclass
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-darkgrid")


@dataclass
class Evaluate:
    """
    A class to evaluate a forecasting model for a specific player's performance.

    Attributes:
    -----------
    df : pd.DataFrame
        The DataFrame containing player data with a "PLAYER" column and a "PPR" column.
    player : str
        The name of the player to evaluate.
    steps : int
        The number of steps (months) to forecast into the future.
    regressor : object
        The regression model to use for forecasting.
    lags : int
        The number of lagged values to use for the autoregressive model.

    Methods:
    --------
    __post_init__():
        Initializes the evaluation, checks data sufficiency, and sets up the training period.
    eval():
        Performs the forecasting and evaluation of the model, returns a DataFrame with evaluation results.
    """

    df: pd.DataFrame
    player: str
    steps: int
    regressor: object
    lags: int

    def __post_init__(self) -> None:
        """
        Post-initialization processing to set up data for the evaluation.

        This method filters the data for the specific player, sets up forecast dates,
        checks if there is enough data to perform the evaluation, and adjusts lags and steps if needed.
        """
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

        # If they don't have at least double the lag amount of games, there's not enough data to
        # evaluate how well the model worked, so we make an adjustment.
        # This is only an issue for model eval, we can ignore this for prediction.
        if self.lags * 2 > int(self.length):
            print(f"Not enough data. Adjusting lags for {self.player}.")
            self.lags = int(round(self.length / 2, 0) - 1)
            self.steps = self.lags

        # If they don't have at least double the step amount of games, there's not enough data to
        # evaluate how well the model worked, so we make an adjustment.
        # This is only an issue for model eval, we can ignore this for prediction.
        if self.steps * 2 > int(self.length):
            self.steps = int(round(self.length / 2, 0) - 1)
            print(f"Not enough data. Adjusting steps for {self.player}.")

        if int(self.length) == 2:
            print(f"Not enough data. Adjusting lags for {self.player}.")
            self.lags = 1
            self.steps = 1

        self.end_train = max(self.data.index) - relativedelta(months=self.steps - 1)

    def eval(self) -> pd.DataFrame:
        """
        Evaluates the forecasting model by fitting it on historical data and making predictions.

        Returns:
        --------
        result_df : pd.DataFrame
            A DataFrame containing evaluation metrics such as MAPE, RMSE, actual season total,
            predicted total, and details about the forecasting model used.
        """
        try:
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
                abs(np.sum(self.data.loc[self.end_train :]) - np.sum(predictions))
                / np.sum(self.data.loc[self.end_train :]),
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
        except ValueError or TypeError:
            print(f"{self.player} does not have enough data.")
