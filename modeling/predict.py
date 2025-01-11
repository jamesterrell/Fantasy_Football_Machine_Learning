from skforecast.recursive import ForecasterRecursive
from dataclasses import dataclass
import pandas as pd


@dataclass
class Predict:
    """
    A class to predict a specific player's performance using a forecasting model.

    Attributes:
    -----------
    df : pd.DataFrame
        The DataFrame containing player data with a "PLAYER" column and a "PPR" column.
    player : str
        The name of the player to predict performance for.
    steps : int
        The number of future time steps (months) to forecast.
    regressor : object
        The regression model to use for forecasting.
    lags : int
        The number of lagged values to use for the autoregressive model.

    Methods:
    --------
    __post_init__():
        Sets up the data for prediction, including filtering the player's data and setting up forecast dates.
    predict_season():
        Fits the forecasting model on historical data and makes predictions for the specified number of future steps.
        Returns a list with the player's name and the sum of the predicted values.
    """

    df: pd.DataFrame
    player: str
    steps: int
    regressor: object
    lags: int

    def __post_init__(self) -> None:
        """
        Post-initialization processing to set up data for the prediction.

        This method filters the DataFrame to include only the data for the specified player,
        sets up forecast dates, and ensures the time series data is properly formatted.
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
        Fits the forecasting model on historical player data and makes predictions.

        This method trains the autoregressive model using the specified regressor and lagged values,
        then predicts the player's performance for the given number of future steps.

        Returns:
        --------
        list
            A list containing the player's name and the sum of the predicted performance values.
            If insufficient data is available, a message is printed indicating the lack of data.
        """
        try:
            forecaster = ForecasterRecursive(
                regressor=self.regressor(random_state=123), lags=self.lags
            )

            forecaster.fit(y=self.data)
            predictions = forecaster.predict(steps=self.steps)

            return [self.player, predictions.sum()]
        except ValueError:
            print(
                f"{self.player} has insufficient data. Only {self.length} games on record, adjusting lags"
            )
            forecaster = ForecasterRecursive(
                regressor=self.regressor(random_state=123), lags=self.length-1
            )

            forecaster.fit(y=self.data)
            predictions = forecaster.predict(steps=self.steps)

            return [self.player, predictions.sum()]
