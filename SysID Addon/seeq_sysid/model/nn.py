from os import environ
environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from pandas import DataFrame, concat
from numpy import array
from tensorflow import get_logger
get_logger().setLevel('ERROR')

from tensorflow.keras import layers, callbacks, Sequential, optimizers
from keras_tuner import RandomSearch, BayesianOptimization, HyperModel, Hyperband

from .base import Model


# Neural Network (RNN)
class NN(Model):
    def __init__(self):
        super().__init__()

        self.p = None
        self.q = None
        self.nn_type = 'RNN'
        self.mode = None
        self.options = None
        self.tuner = None
        self.units = None
        self.n_layers = None
        self.batch_size = None
        self.max_trials = None

        self.model = None
        self.history = None
        self.window = 10
        self.Min = None
        self.Max = None

    def normalize(self, df: DataFrame = None):
        df_norm = (df - self.Min) / (self.Max - self.Min)
        return df_norm

    def denormalize(self, df_norm: DataFrame = None):
        df = df_norm[self.cv] * (self.Max[self.cv] - self.Min[self.cv]) + self.Min[self.cv]
        return df

    def create_snapshot(self, in_df: DataFrame = None, out_df: DataFrame = None):
        n_step = len(in_df)

        x_train = []
        y_train = []

        if in_df is not None:
            for i in range(self.window, n_step):
                x_train.append(in_df.iloc[i - self.window:i].to_numpy())
            x_train = array(x_train)

        if out_df is not None:
            for i in range(self.window, n_step):
                y_train.append(out_df.iloc[i].to_numpy())
            y_train = array(y_train)

        return x_train, y_train

    def option_maker(self):
        if self.mode == 0:  # Mode = Low
            self.units = list(range(5, 206, 20))
            self.n_layers = [1]
            self.batch_size = [32]
            self.max_trials = 6

        elif self.mode == 1:  # Mode = Medium
            self.units = list(range(5, 206, 20))
            self.n_layers = [1, 2, 3]
            self.batch_size = [32]
            self.max_trials = 15

        elif self.mode == 2:  # Mode = High
            self.units = list(range(5, 206, 20))
            self.n_layers = [1, 2, 3]
            self.batch_size = [32, 64, 128]
            self.max_trials = 30

    def identify(self, df: DataFrame = None):
        # Set Mode Options
        self.option_maker()

        # Early Stopping
        tune_es = callbacks.EarlyStopping(monitor='val_loss', patience=3)
        fit_es = callbacks.EarlyStopping(monitor='val_loss', patience=15)

        # Number of Inputs & Outputs
        self.p = len(self.mv + self.cv)
        self.q = len(self.cv)

        # Normalize data
        df_norm = self.normalize(df=df)

        # Input/Output Data
        in_df = df_norm[self.mv + self.cv]
        out_df = df_norm[self.cv]

        # Data Label
        self.label = [tag_label + '_nn' for tag_label in out_df.columns]

        # Create Data Snapshots for NN
        x_train, y_train = self.create_snapshot(in_df=in_df, out_df=out_df)

        # Setup Hyperparameter Optimizer
        hypermodel = HyperNN(units=self.units, n_layers=self.n_layers, p=self.p, q=self.q, window=self.window)
        tuner = HyperTuner(
            auto_bs=self.batch_size,
            hypermodel=hypermodel,
            objective="val_loss",
            max_trials=self.max_trials,
            num_initial_points=2,
            alpha=1e-4,
            beta=2.6,
            overwrite=True,
            directory="temp_dir",
            project_name="Seeq_NN",
        )

        tuner.oracle.multi_worker = True

        # Run Hyperparameter Optimizer
        tuner.search(x_train, y_train,
                     epochs=20, validation_split=0.2,
                     verbose=0, callbacks=[tune_es])
        self.tuner = tuner

        # Get the optimal hyperparameters
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

        model = tuner.hypermodel.build(best_hps)

        # Training Performance
        self.history = model.fit(x_train, y_train, epochs=1000, validation_split=0.2, callbacks=[fit_es], verbose=0)

        # Save Model
        self.model = model

        self.status = True

    def forecast(self, df: DataFrame = None):
        df_norm = self.normalize(df=df)

        in_df = df_norm[self.mv+self.cv]
        x_train, _ = self.create_snapshot(in_df=in_df)

        yp_norm = self.model.predict(x_train)

        yp_norm_df = DataFrame(yp_norm, columns=self.cv)
        yp_df = self.denormalize(yp_norm_df)
        dummy_rows = df[self.cv].iloc[:self.window].shift(self.window)
        yp_df = concat([dummy_rows, yp_df], ignore_index=True)
        yp_df.fillna(method='bfill', inplace=True)
        yp_df.columns = self.label

        return yp_df


class HyperNN(HyperModel):
    def __init__(self, units: list, n_layers: list, p: int, q: int, window: int, *args, **kwargs):
        self.units = units
        self.n_layers = n_layers
        self.p = p
        self.q = q
        self.window = window
        super(HyperNN, self).__init__(*args, **kwargs)

    def build(self, hp):
        model = Sequential()
        n_layers = hp.Choice(name='n_layers', values=self.n_layers)
        for i_layer in range(n_layers):
            layer_name = "units{}".format(i_layer)
            model.add(
                layers.SimpleRNN(
                    input_shape=(self.window, self.p),
                    units=hp.Choice(layer_name, values=self.units),
                    return_sequences=True,
                )
            )
            model.add(layers.Dropout(0.25))
        model.add(layers.Flatten())
        model.add(layers.Dense(self.q,
                               activation="linear"))
        model.compile(
            optimizer=optimizers.Adam(),
            loss="MSE",
            metrics=["accuracy"]
        )

        return model


class HyperTuner(BayesianOptimization):
    def __init__(self, auto_bs: list, *args, **kwargs):
        self.auto_bs = auto_bs
        super(HyperTuner, self).__init__(*args, **kwargs)

    def run_trial(self, trial, *args, **kwargs):
        kwargs['batch_size'] = trial.hyperparameters.Choice('batch_size', self.auto_bs)
        super(HyperTuner, self).run_trial(trial, *args, **kwargs)
