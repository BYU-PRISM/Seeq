from pandas import DataFrame
from math import floor


def test_train_split(x_df: DataFrame = DataFrame(), y_df: DataFrame = DataFrame(), train_ratio: float = 0.75) \
        -> (DataFrame, DataFrame, DataFrame, DataFrame):
    if x_df.empty or y_df.empty:
        return x_df, x_df, y_df, y_df

    k = len(x_df)

    x_train: DataFrame = x_df.iloc[:floor(k * train_ratio)]
    x_valid: DataFrame = x_df.iloc[floor(k * train_ratio):]
    y_train: DataFrame = y_df.iloc[:floor(k * train_ratio)]
    y_valid: DataFrame = y_df.iloc[floor(k * train_ratio):]

    return x_train, x_valid, y_train, y_valid


def shifter(df_o: DataFrame, dummy_state) -> DataFrame:
    df_n = DataFrame()
    for i in range(dummy_state):
        for tag in df_o.columns:
            df_n[tag + '_d{}'.format(i)] = df_o[tag].shift(i)
    df_n.fillna(method='bfill', inplace=True)

    return df_n
