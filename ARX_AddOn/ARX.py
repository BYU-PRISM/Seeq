from gekko import GEKKO
from pandas import DataFrame, concat
from numpy import linspace, array, ndarray, append, vstack, ones, zeros, reshape
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests


'''
ARX Model: y(k+1) = a_1*y(k)+a_2*y(k-1)+...+a_na*y(k-na+1) 
                  + b_1+u(k)+b_2*u(k-1)+...+b_nb*u(k-na+1)

Function Inputs:
u: Input(s)   [pandas DataFrame]
y: Output(s)  [pandas DataFrame]
na: AutoRegressive term order / Ex: na=2 -> a_1*y(k) + a_2*y(k-1)
nb: eXogenous input order     / Ex: nb=2 -> b_1*u(k) + b_2*u(k-1)
n_u: No. of Inputs
n_y: No. of Outputs

----------------------------------------------------------------

- Option 1: User can specify Input/Output DataFrame and na/nb
- Option 2: User just specify a DataFrame and Granger Causality identify input(s)/output(s) and Identify the ARX model

'''


class ARX:
    def __init__(self):
        self.p = None
        self.yp = None
        self.n_a = None
        self.n_b = None


    def identify(self, U: DataFrame = None, Y: DataFrame = None, T: DataFrame = None, NA: int = 1, NB: int = 1, NK: int = 0):
        if Y is None:
            U, Y, NA, NB = self.granger_causality(U)
            inputs = U.columns.values
            outputs = Y.columns.values
            print('inputs= {}'.format(inputs))
            print('outputs= {}'.format(outputs))
        else:
            inputs = U.columns.values
            outputs = Y.columns.values
        
        if T is None:
            try:
                T = U['Time'].values
            except:
                pass
        T = list(range(len(Y.index)))
        self.n_a = NA
        self.n_b = NB
        self.n_k = NK
        m = GEKKO(remote=False)
        yp, self.p, _K = m.sysid(T, U, Y, NA, NB, NK, pred='meas', shift='calc')
        self.yp = DataFrame(yp)
        
        return inputs, outputs




    def predict(self, U: DataFrame, Y: DataFrame):
        ly, NY = Y.shape
        lu, NU = U.shape
        NA = self.n_a
        NB = self.n_b
        NK = self.n_k
        
        A = reshape(self.p['a'].transpose(), [NY, NA])
        B = self.p['b']
        C = self.p['c']

        Nd_max = max(NA, NB+NK)

        YP = Y.iloc[:Nd_max].to_numpy()
        NI = max(0, NA-NB-NK)
        for k in range(NI, lu -NB-NK):
            y_p = zeros(NY)
            for i in range(NY):
                y_p[i] = A[i][::-1].dot(Y[k:k + NA].iloc[:, [i]]) + C[i]
                for j in range(NU):
                    y_p[i] += B[i].transpose()[j][::-1].dot(U[k:k + NB + NK].iloc[:, [j]])

            YP = vstack([YP, y_p])

        labels = []
        for label in Y.columns:
            labels.append(label+'_pred')

        YP = DataFrame(YP, columns=labels)
        self.yp = YP

        return YP


    def forecast(self, U: DataFrame, Y: DataFrame):
        ly, NY = Y.shape
        lu, NU = U.shape
        NA = self.n_a
        NB = self.n_b
        NK = self.n_k

        A = reshape(self.p['a'].transpose(), [NY, NA])
        B = self.p['b']
        C = self.p['c']

        Nd_max = max(NA, NB+NK)

        YP = Y.iloc[:Nd_max].to_numpy()
        yo = YP[-NA:].transpose()

        NI = max(0, NA-NB-NK)
        for k in range(NI, lu-NB-NK):
            y_p = zeros(NY)
            for i in range(NY):
                y_p[i] = A[i][::-1].dot(yo[i]) + C[i]
                for j in range(NU):
                    y_p[i] += B[i].transpose()[j][::-1].dot(U[k:k + NB + NK].iloc[:, [j]])
                yo[i][:NA-1] = yo[i][1:]
                yo[i][-1] = y_p[i]
            YP = vstack([YP, y_p])
        
        labels = []
        for label in Y.columns:
            labels.append(label+'_pred')

        YP = DataFrame(YP, columns=labels)
        YP.fillna(method='ffill', inplace=True)
        YP.fillna(method='bfill', inplace=True)
        return YP


    def granger_causality(self, X: DataFrame):
        n = len(X.columns)
        granger_coe = DataFrame(ones((n, n)), columns=X.columns, index=X.columns)
        grangered_struct = {}
        cause = []
        effect = []
        delay = []
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

    # def summary(self):
    #     summary_str = 'y(k+1) = '
        # for a_i in self.p['a']



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

