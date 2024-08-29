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
        The number of future time steps (months) to forecast.
    regressor : object
        The regression model to use for forecasting.
    lags : int
        The number of lagged values to use for the autoregressive model.
    exogs : list, optional
        A list of column names representing exogenous variables to be used for forecasting.
        If None, the forecasting will be performed without exogenous variables.

    Methods:
    --------
    __post_init__():
        Prepares the data for evaluation, including filtering the player data, setting up the
        forecast dates, and adjusting lags and steps based on data availability.

    eval():
        Performs the forecasting and evaluation of the model, fitting it on historical data and
        making predictions. Returns a DataFrame with evaluation metrics such as MAPE, RMSE, actual
        season total, predicted total, and details about the forecasting model used.
    """

    df: pd.DataFrame
    player: str
    steps: int
    regressor: object
    lags: int
    exogs: list = None

    def __post_init__(self) -> None:
        """
        Initializes the evaluation process by setting up the data and configuration.

        This method filters the DataFrame to include only the data for the specified player,
        assigns forecast dates, checks if there is sufficient data for the evaluation, and adjusts
        the lags and steps if necessary to ensure that the model can be evaluated effectively.
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
        self.target = self.data["PPR"]
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
        Evaluates the forecasting model by fitting it on historical player data and making predictions.

        Depending on whether exogenous variables are provided, the method fits the model using those
        variables or without them. It then generates predictions for the specified number of steps
        and calculates evaluation metrics.

        Returns:
        --------
        pd.DataFrame
            A DataFrame containing evaluation metrics such as the actual season total, predicted total,
            season MAPE (Mean Absolute Percentage Error), game MAPE, game RMSE (Root Mean Squared Error),
            the number of games predicted, number of lags, and the type of regressor used.
        """
        # try:
        forecaster = ForecasterAutoreg(regressor=self.regressor, lags=self.lags)

        if self.exogs is not None:
            self.exog_vars = self.data[self.exogs]
            forecaster.fit(
                y=self.target.loc[
                    : max(self.data.index) - relativedelta(months=self.steps)
                ],
                exog=self.exog_vars[
                    : max(self.data.index) - relativedelta(months=self.steps)
                ],
            )
            predictions = forecaster.predict(
                steps=self.steps,
                exog=self.exog_vars[
                    (max(self.data.index) - relativedelta(months=self.steps - 1)) :
                ],
            )

        else:
            forecaster.fit(
                y=self.target.loc[
                    : max(self.data.index) - relativedelta(months=self.steps)
                ],
            )
            predictions = forecaster.predict(
                steps=self.steps,
            )

        error_mape = mean_absolute_percentage_error(
            y_true=self.target.loc[self.end_train :], y_pred=predictions
        )
        error_rsme = np.sqrt(
            mean_squared_error(
                y_true=self.target.loc[self.end_train :], y_pred=predictions
            )
        )
        self.results = [
            self.player,
            np.sum(self.target.loc[self.end_train :]),
            np.sum(predictions),
            abs(np.sum(self.target.loc[self.end_train :]) - np.sum(predictions))
            / np.sum(self.target.loc[self.end_train :]),
            error_mape,
            error_rsme,
            np.size(self.target.loc[self.end_train :]),
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

        result_df = pd.DataFrame([self.results], columns=columns)
        return result_df

