from gekko import GEKKO

from numpy import vstack, zeros, reshape, array
from pandas import DataFrame

from .base import Model
from re import split


def create_formula_variable_name(names):
    formula_name = []
    for item in names:
        item = item.lower()
        item = split("_| | ", item)
        f_name = '$'
        for i in item:
            f_name += i
        formula_name.append(f_name)

    return formula_name


class ARX(Model):
    """ AutoRegressive with Exogenous input (ARX)
    Model Structure:
    y(k+1) = a_0*y(k)+a_1*y(k-1)+...+a_(na-1)*y(k-na+1)
              + b_0+u(k)+b_1*u(k-1)+...+b_(nb-1)*u(k-na-nk+1)
    where:
        u: Input(s)   [pandas DataFrame]
        y: Output(s)  [pandas DataFrame]
        na: AutoRegressive term order
            na=2 -> a_0*y(k) + a_1*y(k-1)
        nb: Exogenous input order
            nb=2 -> b_0*u(k) + b_1*u(k-1)
        nk: Input Delay
            nk=2 -> b_0*u(k-2) + b_1*u(k-3)
        n_u: Number of Inputs
        n_y: Number of Outputs
    """

    def __init__(self):

        super().__init__()
        self.model_struct = 'ARX'

        self.p = None
        # AR part order
        self.na_min = 0
        self.na_max = 2
        self.na = None
        # Exogenous part order
        self.nb_min = 0
        self.nb_max = 2
        self.nb = None
        # Input delay
        self.nk_min = 0
        self.nk_max = 0
        self.nk = None

    def identify(self, df: DataFrame = None):

        self.df = df
        u_df = df[self.mv]
        y_df = df[self.cv]

        t = list(range(len(y_df.index)))

        for i_a in range(self.na_min, self.na_max + 1):
            for i_b in range(self.nb_min, self.nb_max + 1):
                for i_k in range(self.nk_min, self.nk_max + 1):
                    model = GEKKO(remote=False)
                    yp, p, _K = model.sysid(t=t, u=u_df, y=y_df, na=i_a, nb=i_b, nk=i_k, pred='meas', shift='calc')

                    e = (y_df.to_numpy() - yp) ** 2
                    e = sum(sum(e)) / len(e)

                    if e < self.error_best:
                        self.error_best = e
                        self.p = p
                        self.na = i_a
                        self.nb = i_b
                        self.nk = i_k
                        self.yp = yp

        self.status = True

    def predict(self, df: DataFrame = None):
        u_df = df[self.mv]
        y_df = df[self.cv]

        ly, ny = y_df.shape
        lu, nu = u_df.shape
        na = self.na
        nb = self.nb
        nk = self.nk

        alpha = reshape(self.p['a'].transpose(), [ny, na])
        beta = self.p['b']
        c = self.p['c']

        nd_max = max(na, nb + nk)

        yp: array = y_df.iloc[:nd_max].to_numpy()
        ni = max(0, na - nb - nk)

        if self.model_struct == 'ARX':
            for k in range(ni, lu - nb - nk):
                y_p = zeros(ny)
                for i in range(ny):
                    y_p[i] = alpha[i][::-1].dot(y_df[k:k + na].iloc[:, [i]]) + c[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k:k + nb + nk].iloc[:, [j]])

                yp = vstack([yp, y_p])

        elif self.model_struct == 'FIR':
            for k in range(ni, lu - nb - nk):
                y_p = zeros(ny)
                for i in range(ny):
                    # y_p[i] = C[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k:k + nb + nk].iloc[:, [j]])

                yp = vstack([yp, y_p])

        labels = []
        for label in y_df.columns:
            labels.append(label + '_pred')

        yp = DataFrame(yp, columns=labels)
        yp.fillna(method='ffill', inplace=True)
        yp.fillna(method='bfill', inplace=True)
        self.yp = yp

        return yp

    def forecast(self, df: DataFrame = None):
        u_df = df[self.mv]
        y_df = df[self.cv]

        ly, ny = y_df.shape
        lu, nu = u_df.shape
        na = self.na
        nb = self.nb
        nk = self.nk

        alpha = reshape(self.p['a'].transpose(), [ny, na])
        beta = self.p['b']
        c = self.p['c']

        nd_max = max(na, nb + nk)

        yp = y_df.iloc[:nd_max].to_numpy()
        yo = yp[-na:].transpose()

        ni = max(0, na - nb - nk)

        if self.model_struct == 'ARX':
            for k in range(ni, lu - nb - nk):
                y_p = zeros(ny)
                for i in range(ny):
                    y_p[i] = alpha[i][::-1].dot(yo[i]) + c[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k:k + nb + nk].iloc[:, [j]])
                    yo[i][:na - 1] = yo[i][1:]
                    yo[i][-1] = y_p[i]
                yp = vstack([yp, y_p])

        elif self.model_struct == 'FIR':
            for k in range(ni, lu - nb - nk):
                y_p = zeros(ny)
                for i in range(ny):
                    y_p[i] = c[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k:k + nb + nk].iloc[:, [j]])
                    yo[i][:na - 1] = yo[i][1:]
                    yo[i][-1] = y_p[i]
                yp = vstack([yp, y_p])

        self.label = [tag_label + '_pred' for tag_label in y_df.columns]

        yp_df = DataFrame(yp, columns=self.label)
        yp_df.fillna(method='ffill', inplace=True)
        yp_df.fillna(method='bfill', inplace=True)
        return yp_df

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

        timestep: float = time_interval.total_seconds()

        formula_list = []

        for i in range(n_y):
            formula = ''
            for j in range(n_a):
                formula += ' {}.move({}s)*({})\n+'.format(yf_name[i], (j + 1) * timestep, self.p['a'][j][i])

            for k in range(n_u):
                for j in range(n_bk):
                    formula += ' {}.move({}s)*({})\n+'.format(uf_name[k], (j + 1) * timestep, self.p['b'][i][j][k])

            formula += str(self.p['c'][i])

            formula_list.append({
                'Name': '{} arx'.format(y_name[i]),
                'Type': 'CalculatedSignal',
                'Description': 'ARX Model {} Formula '.format(y_name[i]),
                'Formula': formula,
                'Formula Parameters': formula_dic
            })

        self.formula = DataFrame(formula_list)

# from pandas import read_csv
# import matplotlib.pyplot as plt
#
#
# x_df = read_csv('../../signal_df.csv')
# x_df.set_index('Time', drop=True, inplace=True)
# x_df = x_df.iloc[50:]
# arx = ARX()
#
# arx.mv = ['F_cw']
# arx.cv = ['T1', 'T2', ]
# arx.identify(x_df)
# yp = arx.forecast(x_df)
# plt.plot(yp)
# plt.show()
