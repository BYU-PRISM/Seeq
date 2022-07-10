from numpy import hstack, zeros, linalg
from pandas import DataFrame

from .base import Model
from .utils import test_train_split, shifter


# Subspace Model
class Subspace(Model):
    def __init__(self):
        super().__init__()
        self.method = 'Least Square'
        
        # Order Multiplier
        self.om_min = None
        self.om_max = None
        
        # Shift Type
        self.shift_type = 'Initial'

    def identify(self,
                 df: DataFrame = None):

        u_df = df[self.mv]
        y_df = df[self.cv]

        if self.shift_type == 'Initial':
            self.u_ss = u_df.head(1).to_numpy()
            self.y_ss = y_df.head(1).to_numpy()
        elif self.shift_type == 'Mean':
            self.u_ss = u_df.mean().to_numpy()
            self.y_ss = y_df.mean().to_numpy()

        u_df -= self.u_ss
        y_df -= self.y_ss

        self.label = [tag_label + '_subspace' for tag_label in y_df.columns]

        u_train, u_valid, y_train, y_valid = test_train_split(u_df, y_df)

        n_step, m = u_valid.shape

        eval_0 = 1e9
        eval_best = eval_0
        order_penalty = 1e-5
        order = 1

        if self.method == 'Least Square':
            u_valid = u_valid.to_numpy()
            y_valid = y_valid.to_numpy()
            for r in range(self.om_min, self.om_max+1):
                x_df = shifter(y_train, r)

                n_x = len(x_df.columns)
                n_y = len(y_df.columns)

                yp = x_df.shift(1)
                yp = yp.fillna(method='bfill').to_numpy()
                x_train = x_df.to_numpy()

                xp = hstack([yp, u_train])

                G = linalg.lstsq(xp, x_train, rcond=None)[0].T

                A = G[:, :-m]
                B = G[:, -m:]
                C = zeros((n_y, A.shape[0]))
                for i in range(n_y):
                    C[i, i] = 1

                D = zeros((n_y, m))

                xh = zeros((n_step, n_x))
                yh = zeros((n_step, n_y))

                for i in range(1, n_step):
                    xh[i] = A.dot(xh[i - 1]) + B.dot(u_valid[i - 1])
                    yh[i] = C.dot(xh[i - 1])

                e_val = ((yh - y_valid) ** 2).sum() / len(yh) ** 2

                if e_val + (A.shape[0] - order) * order_penalty <= eval_best:
                    A_best = A
                    B_best = B
                    C_best = C
                    D_best = D
                    order = A.shape[0]
                    eval_best = e_val

            if eval_best < eval_0:
                self.A = A_best
                self.B = B_best
                self.C = C_best
                self.D = D_best
                self.order = order
                self.eval_best = eval_best

            else:
                self.A = A
                self.B = B
                self.C = C
                self.D = D
                print('Solution Not Found')

        elif self.method == 'DMDc':
            pass

        elif self.method == 'N4SID':
            pass

        self.status = True

    def simulate(self, u, x0):
        A = self.A
        B = self.B
        C = self.C
        D = self.D

        steps = u.shape[0]

        xh = zeros((steps, A.shape[0]))
        yh = zeros((steps, C.shape[0]))
        xh[0] = x0

        for i in range(1, steps):
            xh[i] = A.dot(xh[i - 1]) + B.dot(u[i - 1])
            yh[i] = C.dot(xh[i - 1]) + D.dot(u[i - 1])

        return xh, yh

    def forecast(self, df: DataFrame = None):
        u_df = df[self.mv]

        u0 = u_df.to_numpy()

        u = u0 - self.u_ss

        x0 = zeros((self.A.shape[0],))

        x, ys = self.simulate(u, x0)

        ys += self.y_ss

        yp_df = DataFrame(ys, columns=self.label, index=df.index)
        yp_df = yp_df.shift(-1)
        yp_df.fillna(method='ffill', inplace=True)

        self.yp = yp_df

        return yp_df

# from pandas import read_csv
# import matplotlib.pyplot as plt
#
#
# x_df = read_csv('../../signal_df.csv')
# x_df.set_index('Time', drop=True, inplace=True)
# x_df = x_df.iloc[50:]
# ss = Subspace()
# ss.mv = ['F_cw']
# ss.cv = ['T1', 'T2', ]
# ss.identify(x_df)
# yp = ss.forecast(x_df)
# plt.plot(yp)
# plt.show()
