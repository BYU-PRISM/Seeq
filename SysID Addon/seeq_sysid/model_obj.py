from os import environ

import matplotlib.pyplot as plt

environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from gekko import GEKKO
from numpy import vstack, ones, zeros, reshape, where, linalg, dot, array
from statsmodels.tsa.stattools import grangercausalitytests

# from seeq_sysid._backend import *

from tensorflow import get_logger
from tensorflow.keras import layers, callbacks, Sequential, optimizers
from keras_tuner import RandomSearch, BayesianOptimization, HyperModel, Hyperband
from pandas import read_csv, DataFrame
get_logger().setLevel('ERROR')


class Model_Obj:
    def __init__(self):
        self.status = False
        self.df = None
        self.label = None
        self.formula = None
        self.mv = None
        self.cv = None
        self.yp = None
        self.error = None
        self.error_best = 1e50000
        self.thresh = 1e-6
        self.order = 4

        self.n = None
        self.m = None
        self.d = None

        self.na_min = None
        self.na_max = None
        self.na = None

        self.nb_min = None
        self.nb_max = None
        self.nb = None

        self.nk_min = None
        self.nk_max = None
        self.nk = None

        self.p = None
        self.q = None

        self.eps = None
        self.A = None
        self.B = None
        self.C = None
        self.D = None

        self.alpha = None
        self.beta = None

        self.model = None
        self.history = None
        self.window = None
        self.units = None
        self.layers = None
        self.Min = None
        self.Max = None

    def identify(self, df: DataFrame = None):
        pass

    def predict(self, df: DataFrame = None):
        pass

    def forecast(self, df: DataFrame = None):
        pass





class ARX(Model_Obj):
    '''
    ARX Model: y(k+1) = a_0*y(k)+a_1*y(k-1)+...+a_(na-1)*y(k-na+1)
                      + b_0+u(k)+b_1*u(k-1)+...+b_(nb-1)*u(k-na+1)

    Function Inputs:
    u: Input(s)   [pandas DataFrame]
    y: Output(s)  [pandas DataFrame]
    na: AutoRegressive term order / Ex: na=2 -> a_0*y(k) + a_1*y(k-1)
    nb: eXogenous input order     / Ex: nb=2 -> b_0*u(k) + b_1*u(k-1)
    nk: Input Delay               / Ex: nk=2 -> b_0*u(k-2) + b_1*u(k-3)
    n_u: No. of Inputs
    n_y: No. of Outputs

    ----------------------------------------------------------------

    - Option 1: User can specify Input/Output DataFrame and na/nb
    - Option 2: User just specify a DataFrame and Granger Causality identify input(s)/output(s) and Identify the ARX model
    '''

    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

    def identify(self, df: DataFrame = None):

        self.df = df
        U = df[self.mv]
        Y = df[self.cv]

        T = list(range(len(Y.index)))

        for i_a in range(self.na_min, self.na_max + 1):
            for i_b in range(self.nb_min, self.nb_max + 1):
                for i_k in range(self.nk_min, self.nk_max + 1):
                    m = GEKKO(remote=False)
                    yp, p, _K = m.sysid(T, U, Y, i_a, i_b, i_k, pred='meas', shift='calc')

                    e = (Y.to_numpy() - yp) ** 2
                    e = sum(sum(e)) / len(e)

                    if e < self.error_best:
                        self.error_best = e
                        self.p = p
                        self.na = i_a
                        self.nb = i_b
                        self.nk = i_k
                        self.yp = yp

        self.yp = DataFrame(yp)

        self.status = True

    #         return inputs, outputs

    def predict(self, df: DataFrame = None):
        U = df[self.mv]
        Y = df[self.cv]

        ly, NY = Y.shape
        lu, NU = U.shape
        NA = self.na
        NB = self.nb
        NK = self.nk

        A = reshape(self.p['a'].transpose(), [NY, NA])
        B = self.p['b']
        C = self.p['c']

        Nd_max = max(NA, NB + NK)

        YP = Y.iloc[:Nd_max].to_numpy()
        NI = max(0, NA - NB - NK)
        for k in range(NI, lu - NB - NK):
            y_p = zeros(NY)
            for i in range(NY):
                y_p[i] = A[i][::-1].dot(Y[k:k + NA].iloc[:, [i]]) + C[i]
                for j in range(NU):
                    y_p[i] += B[i].transpose()[j][::-1].dot(U[k:k + NB + NK].iloc[:, [j]])

            YP = vstack([YP, y_p])

        labels = []
        for label in Y.columns:
            labels.append(label + '_pred')

        YP = DataFrame(YP, columns=labels)
        YP.fillna(method='ffill', inplace=True)
        YP.fillna(method='bfill', inplace=True)
        self.yp = YP

        return YP

    def forecast(self, df: DataFrame = None):
        U = df[self.mv]
        Y = df[self.cv]

        ly, NY = Y.shape
        lu, NU = U.shape
        NA = self.na
        NB = self.nb
        NK = self.nk

        A = reshape(self.p['a'].transpose(), [NY, NA])
        B = self.p['b']
        C = self.p['c']

        Nd_max = max(NA, NB + NK)

        YP = Y.iloc[:Nd_max].to_numpy()
        yo = YP[-NA:].transpose()

        NI = max(0, NA - NB - NK)
        for k in range(NI, lu - NB - NK):
            y_p = zeros(NY)
            for i in range(NY):
                y_p[i] = A[i][::-1].dot(yo[i]) + C[i]
                for j in range(NU):
                    y_p[i] += B[i].transpose()[j][::-1].dot(U[k:k + NB + NK].iloc[:, [j]])
                yo[i][:NA - 1] = yo[i][1:]
                yo[i][-1] = y_p[i]
            YP = vstack([YP, y_p])


        self.label = [tag_label + '_pred' for tag_label in Y.columns]

        YP = DataFrame(YP, columns=self.label)
        YP.fillna(method='ffill', inplace=True)
        YP.fillna(method='bfill', inplace=True)
        return YP

    def create_formula(self, tags):
        u_name = self.mv
        y_name = self.cv

        n_y = self.p['a'].shape[1]
        n_u = self.p['b'].shape[2]
        n_a = self.p['a'].shape[0]
        n_bk = self.p['b'].shape[1]

        yf_name = create_formula_variable_name(y_name)
        uf_name = create_formula_variable_name(u_name)

        formula_dic = {}
        for tag in range(len(yf_name)):
            formula_dic[yf_name[tag]] = tags[tags['Name'] == y_name[tag]]

        for tag in range(len(uf_name)):
            formula_dic[uf_name[tag]] = tags[tags['Name'] == u_name[tag]]

        time_interval = self.df.index[1] - self.df.index[0]

        timestep = time_interval.total_seconds()

        formula_list = []

        for i in range(n_y):
            formula = ''
            for j in range(n_a):
                formula += ' {}.move({}s)*({})\n+'.format(yf_name[i], (j + 1) * (-timestep), self.p['a'][j][i])

            for k in range(n_u):
                for j in range(n_bk):
                    formula += ' {}.move({}s)*({})\n+'.format(uf_name[k], (j + 1) * (-timestep), self.p['b'][i][j][k])

            formula += str(self.p['c'][i])

            formula_list.append({
                'Name': '{} arx'.format(y_name[i]),
                'Type': 'CalculatedSignal',
                'Description': 'ARX Model {} Formula '.format(y_name[i]),
                'Formula': formula,
                'Formula Parameters': formula_dic
            })

        self.formula = DataFrame(formula_list)

    def granger_causality(self, X: DataFrame):
        n = len(X.columns)
        granger_coe = DataFrame(ones((n, n)), columns=X.columns, index=X.columns)
        grangered_struct = {}
        cause = []
        effect = []

        n_a = 1
        n_b = 1
        for x in X.columns:
            for y in X.columns:
                if x == y:
                    continue
                try:
                    rel, d, pvalue = granger_causality(X[x], X[y], 5)
                except:
                    continue
                if pvalue < 1e-6:
                    grangered_struct[rel] = (d, pvalue)
                    granger_coe[rel[1]][rel[0]] = pvalue
                    if rel[1] not in effect:
                        effect.append(rel[1])
                        n_b = max(n_b, d)
                    else:
                        n_b = max(n_b, d)

                    if rel[0] not in cause:
                        cause.append(rel[0])

                    if (rel[0] in effect) & (rel[0] in cause):
                        cause.remove(rel[0])
                        n_a = max(n_a, d)
                    # grangered_struct[(rel[1], rel[0])] = (-1.0, 1e-5)
                    # granger_coe[rel[0]][rel[1]] = 1e-5

        U = X[cause]
        Y = X[effect]

        return U, Y, n_a, n_b


# Subspace Model
class Subspace(Model_Obj):
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method = 'DMDc'

        self.U_ss = None
        self.X_ss = None

    def identify(self, df: DataFrame = None):
        u_df = df[self.mv]
        X_df = df[self.cv]

        U_ss = u_df.head(1).to_numpy()
        X_ss = X_df.head(1).to_numpy()
        self.U_ss = U_ss
        self.X_ss = X_ss

        self.label = [tag_label + '_pred' for tag_label in X_df.columns]
        U_real = u_df.to_numpy()
        X_real = X_df.to_numpy()

        U = (U_real - U_ss).T
        X = (X_real - X_ss).T

        if self.method == 'DMDc':

            n = X.shape[0]
            m = U.shape[0]

            u = U[:, :-1]
            X1 = X[:, :-1]
            X2 = X[:, 1:]

            omega = vstack([X1, u])

            Ut, St, Vht = linalg.svd(omega, full_matrices=False)
            thresh_t = 1e-6
            try:
                r_t = where(St < thresh_t)[0][0]
            except:
                r_t = len(St)
            #         r_t = order

            ut = Ut[:, :r_t]
            st = St[:r_t]
            vht = Vht[:r_t, :]

            ut1 = ut[:n, :]
            ut2 = ut[n:n + m, :]

            Uh, Sh, Vhh = linalg.svd(X2, full_matrices=False)

            #         thresh_h = 1e-6
            #         try:
            #             r_h = where(Sh < thresh_t)[0][0]
            #         except:
            #             r_h = len(Sh)

            r_h = self.order

            uh = Uh[:, :r_h]
            # sh = Sh[:r_h]
            # vhh = Vhh[:r_h, :]

            Atilde = (uh.T.dot(X2).dot(vht.T) * (st ** -1)).dot(ut1.T).dot(uh)
            Btilde = (uh.T.dot(X2).dot(vht.T) * (st ** -1)).dot(ut2.T)
            Ctilde = uh
            Dtilde = zeros((n, m))

            self.A = Atilde
            self.B = Btilde
            self.C = Ctilde
            self.D = Dtilde

        elif self.method == 'N4SID':
            pass
    
    
    def simulate(self, U, X0):
        A = self.A
        B = self.B
        C = self.C
        D = self.D

        steps = U.shape[0]

        x = zeros((steps, A.shape[0]))
        ys = zeros((steps, C.shape[0]))
        x[0] = X0
                  
        for i in range(1, steps):
            x[i] = dot(A, x[i-1]) + dot(B, U[i-1])
            ys[i] = dot(C, x[i]) + dot(D, U[i])
                  
        return x, ys

    def forecast(self, df: DataFrame = None):
        u_df = df[self.mv]

        U_real = u_df.to_numpy()

        U = U_real - self.U_ss
        
        X0 = zeros((self.A.shape[0],))

        x, ys = self.simulate(U, X0)
        
        Ys = ys + self.X_ss

        YP = DataFrame(Ys, columns=self.label)
        self.yp = YP

        return YP


# Neural Network (RNN)
class NN(Model_Obj):
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.nn_type = 'RNN'

    def normalize(self, df: DataFrame = None):
        df_norm = (df-self.Min) / (self.Max-self.Min)
        return df_norm

    def denormalize(self, df_norm: DataFrame = None):
        df = df_norm[self.cv] * (self.Max[self.cv]-self.Min[self.cv]) + self.Min[self.cv]
        return df

    def create_snapshot(self, in_df: DataFrame = None, out_df: DataFrame = None):
        L = len(in_df)

        x_train = []
        y_train = []

        if in_df is not None:
            for i in range(self.window, L - 1):
                x_train.append(in_df.iloc[i - self.window:i].to_numpy())
            x_train = array(x_train)
    
        if out_df is not None:
            for i in range(self.window, L - 1):
                y_train.append(out_df.iloc[i + 1].to_numpy())
            y_train = array(y_train)



        return x_train, y_train

    def build_model(self, hp):
        model = Sequential()
        model.add(
            layers.SimpleRNN(
                input_shape=(self.window, self.p),
                units=hp.Int("units1", min_value=5, max_value=205, step=20),
                return_sequences=True,
            )
        )
        model.add(layers.Dropout(0.1))
        model.add(layers.Flatten())
        model.add(layers.Dense(self.q,
                               activation="linear"))
        model.compile(
            optimizer=optimizers.Adam(),
            loss="MSE",
            metrics=["accuracy"],
        )

        return model


    def identify(self, df: DataFrame = None):

        # Advanced Options
        tune_es = callbacks.EarlyStopping(monitor='val_loss', patience=1, min_delta=1e-4)
        fit_es = callbacks.EarlyStopping(monitor='val_loss', patience=15)

        self.p = len(self.mv+self.cv)
        self.q = len(self.cv)

        df_norm = self.normalize(df=df)

        in_df = df_norm[self.mv+self.cv]
        out_df = df_norm[self.cv]
        self.label = [tag_label + '_pred' for tag_label in out_df.columns]

        x_train, y_train = self.create_snapshot(in_df=in_df, out_df=out_df)

        tuner = BayesianOptimization(
            hypermodel=self.build_model,
            objective="val_loss",
            max_trials=6,
            num_initial_points=2,
            alpha=1e-4,
            beta=2.6,
            overwrite=True,
            directory="temp_dir",
            project_name="Seeq_NN",
        )

        tuner.search(x_train, y_train, epochs=2, validation_split=0.2, verbose=0, callbacks=[tune_es])

        # Get the optimal hyperparameters
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
        model = tuner.hypermodel.build(best_hps)

        self.history = model.fit(x_train, y_train, epochs=1000, validation_split=0.2, callbacks=[fit_es], verbose=0)

        self.model = model

    
    def forecast(self, df: DataFrame = None):
        df_norm = self.normalize(df=df)

        in_df = df_norm[self.mv+self.cv]
        
        x_train, _ = self.create_snapshot(in_df=in_df)
    
        yh_norm = self.model.predict(x_train)

        YP_norm = DataFrame(yh_norm, columns=self.cv)
        YP = self.denormalize(YP_norm)

        YP.columns = self.label

        return YP
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def granger_causality(X, Y, d):
    p_XY = 100
    p_YX = 100
    d_XY = 100
    d_YX = 100

    df = DataFrame(columns=['X', 'Y'], data=zip(X, Y))
    gc_res = grangercausalitytests(df, d, verbose=False)
    min([gc_res[k][0]['params_ftest'][1] for k in gc_res])
    for delay in gc_res:
        if gc_res[delay][0]['params_ftest'][1] < p_XY:
            p_XY = gc_res[delay][0]['params_ftest'][1]
            d_XY = delay

    df = DataFrame(columns=['Y', 'X'], data=zip(Y, X))
    gc_res = grangercausalitytests(df, d, verbose=False)
    min([gc_res[k][0]['params_ftest'][1] for k in gc_res])
    for delay in gc_res:
        if gc_res[delay][0]['params_ftest'][1] < p_YX:
            p_YX = gc_res[delay][0]['params_ftest'][1]
            d_YX = delay

    if p_XY < p_YX:
        return (Y.name, X.name), d_XY, p_XY
    else:
        return (X.name, Y.name), d_YX, p_YX


# df = read_csv('../signal_df.csv')
# df.set_index('Time', drop=True, inplace=True)
# nn = NN()
# nn.Min = df.min()
# nn.Max = df.max()
# nn.mv = ['F_cw']
# nn.cv = ['T1']
# nn.window = 10
# nn.identify(df)
# yp = nn.forecast(df)
# plt.plot(yp)
# plt.plot(df[nn.cv].iloc[nn.window:])
