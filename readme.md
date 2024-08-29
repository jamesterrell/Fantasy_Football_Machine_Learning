# NFL Player Performance Analysis and Forecasting

This project focuses on analyzing and forecasting NFL player performance using web scraping, data processing, and machine learning techniques. By leveraging player statistics from Pro Football Reference, the project aims to provide insights into player trends, predict future performance, and offer valuable data for decision-making in sports analytics.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Data Scraping and Cleaning](#data-scraping-and-cleaning)
7. [Forecasting Model](#forecasting-model)
8. [License](#license)

## Introduction

The NFL Player Performance Analysis and Forecasting project utilizes Python libraries such as `requests`, `BeautifulSoup`, `pandas`, and `skforecast` to scrape NFL player data, clean and standardize it, and apply forecasting models to predict future player performance. This project is designed for sports analysts, fantasy football enthusiasts, and data scientists interested in sports data analytics.

## Features

- **Web Scraping**: Collects detailed game-by-game statistics for NFL players from Pro Football Reference.
- **Data Cleaning and Standardization**: Cleans raw data, standardizes column names, handles missing values, and filters out irrelevant data points.
- **Forecasting Models**: Implements time series forecasting using autoregressive models to predict future player performance.
- **Comprehensive Data Merging**: Combines different types of player statistics (e.g., rushing, receiving, passing) for a holistic analysis.
- **Application Potential**: Useful for fantasy sports, sports betting, team management, and coaching analytics.

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/NFL-Player-Performance-Analysis.git
    ```

2. **Navigate to the project directory**:

    ```bash
    cd NFL-Player-Performance-Analysis
    ```

3. **Install required packages**:

    ```bash
    pip install -r requirements.txt
    ```

   The `requirements.txt` file should include the following dependencies:

    ```text
    requests
    beautifulsoup4
    pandas
    skforecast
    ```

## Usage

1. **Scraping Player Data**:

   Use the `scrape_sp` and `scrape_qb` functions to scrape player statistics. Provide the player's code as a string argument.

    ```python
    from scraper import scrape_sp, scrape_qb

    # Example usage
    player_data = scrape_sp('B/BradTo00')
    qb_data = scrape_qb('B/BradTo00')
    ```

2. **Getting All Stats**:

   The `get_all_stats` function merges rushing/receiving stats with passing stats for a comprehensive view.

    ```python
    from scraper import get_all_stats

    # Example usage
    all_stats = get_all_stats('B/BradTo00')
    ```

3. **Forecasting Player Performance**:

   Use the `Predict` class to create a forecasting model and predict player performance for a specified number of steps.

    ```python
    from forecaster import Predict
    from sklearn.linear_model import LinearRegression

    # Example usage
    df = player_data  # Assuming this DataFrame is preloaded with player stats
    predictor = Predict(df=df, player='Tom Brady', steps=12, regressor=LinearRegression, lags=3)
    forecast = predictor.predict_season()
    ```

## Project Structure

- `scraper.py`: Contains functions for scraping NFL player data and cleaning it.
- `forecaster.py`: Contains the `Predict` class for building and using forecasting models.
- `requirements.txt`: List of required Python packages.
- `README.md`: Project documentation.

## Data Scraping and Cleaning

### `scrape_sp(player_code: str)`

Scrapes rushing and receiving stats for a given player using the player code. Cleans and standardizes the data, renaming columns and handling missing values.

### `scrape_qb(player_code: str)`

Scrapes quarterback passing stats for a given player using the player code. Cleans and standardizes the data, ensuring consistent and reliable data for analysis.

### `get_all_stats(player_code_str: str)`

Merges rushing/receiving stats with passing stats, handles discrepancies, and returns a comprehensive DataFrame with all relevant statistics.

## Forecasting Model

### `Predict` Class

A class designed to forecast a player's performance using historical data. The class uses an autoregressive model to make predictions and can be adapted to use different regression models.

- **Attributes**:
  - `df`: DataFrame containing player data.
  - `player`: Name of the player.
  - `steps`: Number of steps (months) to forecast.
  - `regressor`: Regression model used for forecasting.
  - `lags`: Number of lagged values for the autoregressive model.

- **Methods**:
  - `__post_init__()`: Initializes data for the specific player and sets up forecast dates.
  - `predict_season()`: Fits the forecasting model and predicts future performance, returning a DataFrame with prediction results.

