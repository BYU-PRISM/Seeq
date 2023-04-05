from gekko import GEKKO

from numpy import vstack, zeros, ones, reshape, array, zeros_like, diff
from pandas import DataFrame

from .base import Model
from re import split
from scipy.linalg import lstsq

try:
    from seeq import spy
except:
    from seeq_sysid.model.utils import SPY as spy

def create_formula_variable_name(names):
    formula_name = []
    for item in names:
        item = item.lower()
        item = split("_| | ", item)
        f_name = '$'
        
        cnt = 0
        if len(item) > 1:
            for i in item:
                f_name += i[0]
        else:
            if len(item[0]) > 4:
                f_name += item[0][0]
            else:
                f_name += item[0]

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
        self.model_struct = 'ARIMAX'

        self.best_model = None
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
        
        self.e_AR = None
        self.nh = None
        self.nh_min = 0
        self.nh_max = 1
        self.nv = None
        self.nv_min = 1
        self.nv_max = 2

    def identify(self, df: DataFrame = None):
        self.error_best = 1e900

        self.df = df.copy()
        u_df = df[self.mv]
        y_df = df[self.cv]
        ly, ny = y_df.shape
        lu, nu = u_df.shape

        t = list(range(len(y_df.index)))
        
        if len(self.mv) == 0:
            u_df = zeros((ly, 1))
        
        if 'MA' in self.model_struct:
            shift='mean'
        else:
            shift = 'calc'
    
        if (self.na_max+self.nb_max) > 0:
            for i_a in range(self.na_min, self.na_max + 1):
                for i_b in range(self.nb_min, self.nb_max + 1):
                    for i_k in range(self.nk_min, self.nk_max + 1):
                        model = GEKKO(remote=False)\

                        # ARX Model
                        yp, p, K = model.sysid(t=t, u=u_df, y=y_df, na=i_a, nb=i_b, nk=i_k, pred='meas', shift=shift)

                        e = y_df.to_numpy() - yp
                        E = sum(sum(e**2)) / len(e**2)

                        if E < self.error_best:
                            self.best_model = model
                            self.error_best = E
                            self.e_AR = e
                            self.p = p
                            self.na = i_a
                            self.nb = i_b
                            self.nk = i_k
                            self.yp = yp
                            self.K = K 
                            
        else:
            self.na = 0
            self.nb = 0
            self.nk = 0
            
        # ARIMAX
        if (self.model_struct == 'ARIMAX') or (self.model_struct == 'ARMAX') or (self.model_struct == 'MA'):
            self.res_best = 1e9
            
            if  not (self.na_max+self.nb_max > 0):
                self.p = {}
                self.p['m'] = y_df.mean().to_numpy()
                self.e_AR = y_df.to_numpy() - self.p['m']
                self.yp = ones((ly, ny))*self.p['m']

            for nv in range(self.nv_min, self.nv_max+1):
                for nh in range(self.nh_min, self.nh_max+1):
                    ma_coe = [0]*ny
                    
                    e = diff(self.e_AR, nh, axis=0)

                    for y_i in range(ny):

                        x = []
                        y = []

                        x_i_df = DataFrame()
                        y_i_df = DataFrame()

                        for i in range(nv):
                            x_i_df['e_d'+str(i+1)] = e[nv-i-1:-1-i, y_i]
                        y_i_df['e'] = e[nv:, y_i]

                        x = x_i_df.to_numpy()
                        y = y_i_df.to_numpy()
                        
                        self.temp_x = x
                        self.temp_y = y

                        ma_coe[y_i], res = lstsq(x, y, cond=1e-6)[0:2]

                        if sum(res) <= self.res_best:
                            self.nv = nv
                            self.nh = nh
                            self.p['d'] = ma_coe
                    
            e = diff(self.e_AR, self.nh, axis=0)
            
            x = []
            y_ma = [0]*ny
            
            for y_i in range(ny):
            
                x_i_df = DataFrame()
                for nv_i in range(self.nv):
                    x_i_df['e_d'+str(nv_i+1)] = e[self.nv-nv_i-1:-nv_i-1, y_i]

                x = x_i_df.to_numpy()

                y_ma[y_i] = x.dot(self.p['d'][y_i].flatten())

                self.yp[self.nv+self.nh:, y_i] = array(y_ma[y_i]).T + self.yp[self.nv+self.nh:, y_i]


        self.status = True

    def predict(self, df: DataFrame = None):
        u_df = df[self.mv]
        y_df = df[self.cv]

        ly, ny = y_df.shape
        lu, nu = u_df.shape
        na = self.na
        nb = self.nb
        nk = self.nk

        if (self.na+self.nb > 0):
            alpha = reshape(self.p['a'].transpose(), [ny, na])
            beta = self.p['b']
            c = self.p['c']

            nd_max = max(na, nb + nk)

            yp: array = y_df.iloc[:nd_max].to_numpy()
            ni = max(0, na - nb - nk)

        if self.model_struct == 'ARX':
            for k in range(nd_max, lu):
                y_p = zeros(ny)
                for i in range(ny):
                    y_p[i] = alpha[i][::-1].dot(y_df[k - na:k].iloc[:, [i]]) + c[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k - nb - nk:k].iloc[:, [j]])

                yp = vstack([yp, y_p])

        elif self.model_struct == 'FIR':
            for k in range(nd_max, lu):
                y_p = zeros(ny)
                for i in range(ny):
                    # y_p[i] = C[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k - nb - nk:k].iloc[:, [j]])

                yp = vstack([yp, y_p])
                                
        if (self.model_struct == 'ARIMAX') or (self.model_struct == 'ARMAX'):
            if nb == 0:
                nu = 0
            for k in range(nd_max, lu):
                y_p = zeros(ny)
                for i in range(ny):
                    y_p[i] = alpha[i][::-1].dot(y_df[k - na:k].iloc[:, [i]]) + c[i]
                    for j in range(nu):
                        y_p[i] += beta[i].transpose()[j][::-1].dot(u_df[k - nb - nk:k].iloc[:, [j]])

                yp = vstack([yp, y_p])
                
            e = y_df.to_numpy() - yp
             
            e = diff(e, self.nh, axis=0)

            x = []
            y_ma = [0]*ny
            
            for y_i in range(ny):
            
                x_i_df = DataFrame()
                for nv_i in range(self.nv):
                    x_i_df['e_d'+str(nv_i+1)] = e[self.nv-nv_i-1:-nv_i-1, y_i]

                x = x_i_df.to_numpy()

                y_ma[y_i] = x.dot(self.p['d'][y_i].flatten())
            
                yp[self.nv+self.nh:, y_i] = array(y_ma[y_i]).T + yp[self.nv+self.nh:, y_i]
                
        if self.model_struct == 'MA':
            e = y_df.to_numpy() - y_df.mean().to_numpy()
            
            yp = ones((ly, ny))*y_df.mean().to_numpy()
            
            x = []
            y_ma = [0]*ny
            
            for y_i in range(ny):
            
                x_i_df = DataFrame()
                for nv_i in range(self.nv):
                    x_i_df['e_d'+str(nv_i+1)] = e[self.nv-nv_i-1:-nv_i-1, y_i]

                x = x_i_df.to_numpy()

                y_ma[y_i] = x.dot(self.p['d'][y_i].flatten())
            
                yp[self.nv:, y_i] += array(y_ma[y_i]).T
                
            yp[:self.nv] = y_df.iloc[:self.nv].to_numpy()


        labels = []
        for label in y_df.columns:
            labels.append(label + '_pred')

        yp = DataFrame(yp, columns=labels)
        yp.fillna(method='ffill', inplace=True)
        yp.fillna(method='bfill', inplace=True)
        self.yp = yp

        return yp

    def forecast(self, df: DataFrame = None):
        if 'MA' in self.model_struct:
            yp = self.predict(df)
            return yp
    
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

    def create_formula(self, tags_df, signal_df, **kwargs):
        tags = tags_df.copy()

        u_name = self.mv
        y_name = self.cv

        n_y = len(self.cv)
        n_u = len(self.mv)

        yf_name = create_formula_variable_name(y_name)
        uf_name = create_formula_variable_name(u_name)
        
        formula_dic = {}
        
        # Make signals dimensionless (forced)   
        formula_list = []
        for i in range(n_u):                
            formula = ''
            formula += "{}.setUnits('')".format(uf_name[i])
            
            formula_dic[uf_name[i]] = tags[tags['Name'] == u_name[i]]
        
            formula_list.append({'Name': '{} meas'.format(u_name[i]),
                                 'Type': 'CalculatedSignal',
                                 'Description': '{}'.format(u_name[i]),
                                 'Formula': formula,
                                 'Formula Parameters': formula_dic
            })
        
        try:
            tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True),
                            quiet=True)
        except:
            tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True))
        
        tags = tags.append(tags_new, ignore_index=True)
        
        
        for tag in range(len(yf_name)):
            formula_dic[yf_name[tag]] = tags[tags['Name'] == y_name[tag]]

        for tag in range(len(uf_name)):
            formula_dic[uf_name[tag]+'m'] = tags[tags['Name'] == u_name[tag]+ ' meas']

        time_interval = self.df.index[1] - self.df.index[0]

        timestep: float = time_interval.total_seconds()

        formula_list = []

        if (self.na_max+self.nb_max)>0:
            n_a = self.na
            n_bk = self.p['b'].shape[1]
            
            for i in range(n_y):
                formula = ''
                for j in range(n_a):
                    formula += ' {}.move({}s)*({})\n+'.format(yf_name[i], (j + 1) * timestep, self.p['a'][j][i])

                for k in range(n_u):
                    for j in range(n_bk):
                        formula += ' {}.move({}s)*({})\n+'.format(uf_name[k]+'m', (j + 1) * timestep, self.p['b'][i][j][k])

                formula += str(self.p['c'][i])

                formula_list.append({
                    'Name': '{} arx model'.format(y_name[i]),
                    'Type': 'CalculatedSignal',
                    'Description': 'ARX Model {} Formula '.format(y_name[i]),
                    'Formula': formula,
                    'Formula Parameters': formula_dic
                })
            
        if self.model_struct in ['ARIMAX', 'ARMA', 'ARIMA']:
            try:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True),
                                quiet=True)
            except:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True))
                
            tags = tags.append(tags_new, ignore_index=True)
            
    
            formula_list = []
            
            for tag in range(len(yf_name)):
                formula_dic[yf_name[tag]+'am'] = tags[tags['Name'] == y_name[tag]+' arx model']
            
            for i in range(n_y):                
                formula = ''
                formula += '({} - {})'.format(yf_name[i], yf_name[i]+'am')
                
                # integration order
                for j in range(self.nh):
                    formula += '.runningDelta()'
            
                formula_list.append({'Name': '{} arx error'.format(y_name[i]),
                                     'Type': 'CalculatedSignal',
                                     'Description': 'ARX Model {} Error Formula '.format(y_name[i]),
                                     'Formula': formula,
                                     'Formula Parameters': formula_dic
                })
            
            try:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True),
                                quiet=True)
            except:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True))
            
            tags = tags.append(tags_new, ignore_index=True)

            
            # Moving Average Order
            formula_list = []
            n_v = self.nv
            
            for i in range(n_y):
                formula_dic[yf_name[i]+'ae'] = tags[tags['Name'] == y_name[i]+' arx error']
                formula = ' {}\n+'.format(yf_name[i]+'am')
                for j in range(n_v):
                    formula += ' {}.move({}s)*({})\n+'.format(yf_name[i]+'ae', (j+1) * timestep, self.p['d'][i][j][0])
                    
                formula = formula + ' 0.0'
                formula_list.append({'Name': '{} arimax model'.format(y_name[i]),
                                     'Type': 'CalculatedSignal',
                                     'Description': 'ARIMAX Model {} Formula '.format(y_name[i]),
                                     'Formula': formula,
                                     'Formula Parameters': formula_dic
                })
                
        if self.model_struct == 'MA':
            formula_list = []
            
            for i in range(n_y):                
                formula = ''
                formula += '({} - {})'.format(yf_name[i], self.p['m'][i])
                
                # integration order
                for j in range(self.nh):
                    formula += '.runningDelta()'
            
                formula_list.append({'Name': '{} ma error'.format(y_name[i]),
                                     'Type': 'CalculatedSignal',
                                     'Description': 'MA Model {} Error Formula '.format(y_name[i]),
                                     'Formula': formula,
                                     'Formula Parameters': formula_dic
                })
            
            try:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True),
                                quiet=True)
            except:
                tags_new = spy.push(metadata=DataFrame(formula_list), workbook=kwargs['workbook_id'], worksheet=kwargs['worksheet_name'], status=spy.Status(quiet=True))
            
            tags = tags.append(tags_new, ignore_index=True)

            
            # Moving Average Order
            formula_list = []
            n_v = self.nv
            
            for i in range(n_y):
                formula_dic[yf_name[i]+'me'] = tags[tags['Name'] == y_name[i]+' ma error']
                formula = ''
                for j in range(n_v):
                    formula += ' {}.move({}s)*({})\n+'.format(yf_name[i]+'me', (j+1) * timestep, self.p['d'][i][j][0])
                    
                formula = formula + ' {}'.format(self.p['m'][i])
                formula_list.append({'Name': '{} ma model'.format(y_name[i]),
                                     'Type': 'CalculatedSignal',
                                     'Description': 'MA Model {} Formula '.format(y_name[i]),
                                     'Formula': formula,
                                     'Formula Parameters': formula_dic
                })
        
        for i in range(n_y):
            formula = yf_name[i]
                
            formula_list.append({'Name': '{} meas'.format(y_name[i]),
                                 'Type': 'CalculatedSignal',
                                 'Description': y_name[i],
                                 'Formula': formula,
                                 'Formula Parameters': formula_dic
            })
            

        self.formula = DataFrame(formula_list)
