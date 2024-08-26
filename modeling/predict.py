from skforecast.ForecasterAutoreg import ForecasterAutoreg
from dataclasses import dataclass
import pandas as pd


@dataclass
class Predict:
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

        # The reason for this is to avoid errors for players that have less recorded
        # games than the specified lags
        # if self.lags >= int(self.length):
        #     print(f"Not enough data. Adjusting lags for {self.player}.")

    def predict_season(self) -> pd.DataFrame:
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

            forecaster.fit(y=self.data)
            predictions = forecaster.predict(steps=self.steps)

            return [self.player, predictions.sum()]
        except ValueError:
            print(
                f"{self.player} has insufficient data. Only {self.length} games on record"
            )
