import pandas as pd
from numpy import zeros, ones, array, empty, arange, exp, pi, sqrt, nan
from pandas import DataFrame, read_csv

from gekko import GEKKO
from gekko.gekko import EquationObj

import matplotlib.pyplot as plt


class TransferOption:
    idx = 0
    def __init__(self, 
                 order=1,
                 no_gain=0,
                 no_ramp=1,
                 is_dt=1,
                 gain_lb=None,
                 gain_ub=None,
                 tau_lb=0,
                 tau_ub=None,
                 theta_lb=0,
                 theta_ub=None,
                 name=None):
        
        self.name = name
        self.id = None

        self.order = order
        self.no_gain = no_gain
        self.no_ramp = no_ramp
        self.is_zeta = 1
        self.is_dt = is_dt

        self.gain = None
        self.gain_lb = gain_lb
        self.gain_ub = gain_ub
        
        self.tau = None
        self.tau_lb = tau_lb
        self.tau_ub = tau_ub
        
        self.theta = None
        self.theta_lb = theta_lb
        self.theta_ub = theta_ub

        self.tau_1 = None
        self.tau_2 = None
        self.zeta = None
        
        self.ts = None
        self.tr = None
        self.os = None
        
    def calc_step_info(self, t, yout):
        yout = abs(yout)
        
        if self.order == 1:
            self.ts = 4*self.tau
            self.tr = 2.2*self.tau
            self.os = 0.0
        elif self.order == 2:
            if self.zeta == 0:
                self.ts = 1e20
            else:
                self.ts = 3*self.tau/self.zeta
            self.tr = 1.8*self.tau
            if not self.zeta:
                self.os = 100
            elif self.zeta >= 1:
                self.os = 0
            elif self.zeta < 0:
                self.os = nan
            else:
                self.os= 100*exp(-pi*self.zeta/sqrt(1-self.zeta**2))

            # try:
            #     self.ts = t[next(len(yout)-i for i in range(2,len(yout)-1) if abs(yout[-i]/yout[-1])<1.02)]-t[0]
            # except:
            #     self.ts = t[-1]
            # self.tr = t[next(i for i in range(0,len(yout)-1) if yout[i]>yout[-1]*.90)]-t[0]
            # self.os = (yout.max()/yout[-1]-1)*100
        
    def get_model_info(self):
        return (self.order, self.gain, self.tau, self.theta, self.zeta)
        
    def get_step_info(self):
        return (self.ts, self.tr, self.os)
    
    @staticmethod
    def add_idx():
        TransferOption.idx += 1
        
    @staticmethod
    def reset_idx():
        TransferOption.idx = 0


class TransferItem(GEKKO):
    def __init__(self):
        super().__init__(remote=False)

        self.mv = None
        self.cv = None
        
        self.dt = None        
        self.u_ss = None

        self.const_den = False
        self.option_dict = {}

        self.gain = None
        self.tau = None
        self.theta = None
        self.zeta = None
        self.tc = None
        self.tt = None
        
        self.tau_max = None
        self.sim_time = None

        self.t = None
        self.um = None
        self.xm = None
        self.dxm_dt = None
        self.ym = None

        self.nu = None
        self.ny = None

        # self.shift = "mean"
        self.label = None
        self.status = None

    @staticmethod
    def empty_array(mode, dim):
        """
        Create empty numpy arrays to contain gekko objects
        mode = 0 -> zeros
        mode = 1 -> ones
        """
        if mode == 0:
            return zeros(shape=dim, dtype=object)
        if mode == 1:
            return ones(shape=dim, dtype=object)

    def build(self):
        """
        Define a gekko object for the problem
        """
        self.mv = list(self.option_dict.keys())
        nu = len(self.mv)

        # define dead time and dummy time variables
        tt = self.Param(0, name='_time_')
        # self.Equation(tt.dt() == 1)
        tc = empty(shape=nu, dtype=object)

        # define gain (k), time constant (tau) and theta as empty arrays
        gain = empty(shape=nu, dtype=object)
        tau = empty(shape=nu, dtype=object)
        theta = empty(shape=nu, dtype=object)
        zeta = empty(shape=nu, dtype=object)

        # define input and output gekko variables
        um = empty(shape=nu, dtype=object)
        xm = empty(shape=nu, dtype=object)
        ym = empty(shape=1, dtype=object)
        dxm_dt = empty(shape=nu, dtype=object)

        ym[0] = self.CV(value=0, lb=None, ub=None, name=self.cv[0])
        # ym[0].fstatus = 1
        output_eq = "%s=" % (ym[0])

        for i in range(nu):
            option_item: TransferOption = self.option_dict[self.mv[i]]

            # initialize dummy time
            tc[i] = self.Var(value=0, lb=None, ub=None, name="_tc_%i" % (i+1))

            # initialize tau values
            if option_item.no_ramp:
                tau[i] = self.FV(value=0.1, lb=option_item.tau_lb, ub=option_item.tau_ub, name="tau%i" % (i+1))
                tau[i].status = 1
            else:
                tau[i] = 1

            # initialize gain values
            if option_item.no_gain:
                gain[i] = 1
            else:
                gain[i] = self.FV(value=0.1, lb=option_item.gain_lb, ub=option_item.gain_ub, name="K%i" % (i+1))
                gain[i].status = 1

            if option_item.is_dt:
                theta[i] = self.FV(value=1, integer=False, lb=option_item.theta_lb, ub=option_item.theta_ub, name="theta%i" % (i+1))
                theta[i].status = 1
            else:
                theta[i] = 0

            if option_item.order == 2:
                zeta[i] = self.FV(value=2, lb=-10, ub=10, name="zeta%i" % (i + 1))
                zeta[i].status = 1

                dxm_dt[i] = self.Var(value=0, lb=None, ub=None, name='d' + 'x%i' % (i + 1) + '/dt')

            um[i] = self.Var(value=0, lb=None, ub=None, name=self.mv[i])
            xm[i] = self.SV(value=0, lb=None, ub=None, name="x%i" % (i+1))
            xm[i].fstatus = 1

        # create the equations
        for i in range(nu):
            option_item: TransferOption = self.option_dict[self.mv[i]]
            if option_item.order == 1:
                state_eq = "%s*$%s" % (tau[i], xm[i]) if option_item.no_ramp else "$%s" % (xm[i])
            elif option_item.order == 2:
                d_state_eq = "%s=$%s" % (dxm_dt[i], xm[i])
                d_state_eq_obj = EquationObj(d_state_eq)
                self._equations.append(d_state_eq_obj)
                state_eq = "%s^2*$%s" % (tau[i], dxm_dt[i]) if option_item.no_ramp else "$%s" % (dxm_dt[i])
                if option_item.no_ramp:
                    state_eq += "+2*%s*%s*$%s" % (tau[i], zeta[i], xm[i]) if option_item.is_zeta else ""
            else:
                state_eq = "Model Order Not Implemented"
            state_eq += "+%s" % (xm[i]) if option_item.no_ramp else ""
            state_eq += "=%s" % (um[i]) if option_item.no_gain else "=%s*%s" % (gain[i], um[i])

            state_eq_obj = EquationObj(state_eq)
            self._equations.append(state_eq_obj)

            # force same denominator for all the transfer functions corresponding to an output
            if self.const_den and i != 0:
                tau[i].fstatus = 0
                additional_eq = "%s=%s" % (tau[0], tau[i])
                additional_eq_obj = EquationObj(additional_eq)
                self._equations.append(additional_eq_obj)
                if option_item.order == 2:
                    zeta[i].fstatus = 0
                    additional_eq = "%s=%s" % (zeta[0], zeta[i])
                    additional_eq_obj = EquationObj(additional_eq)
                    self._equations.append(additional_eq_obj)

            self.Equation(tc[i] == tt - theta[i])

            output_eq += "%s+" % (xm[i])

        output_eq = output_eq[:-1]
        output_eq_obj = EquationObj(output_eq)
        self._equations.append(output_eq_obj)

        # define the object variables
        self.nu = nu
        self.tc = tc
        self.tt = tt
        self.um = um
        self.xm = xm
        self.dxm_dt = dxm_dt
        self.ym = ym
        self.gain = gain
        self.tau = tau
        self.theta = theta
        self.zeta = zeta

    def identify(self, df):
        df = df.copy()
        # if self.shift == 'initial':
        #     df_ss = df[self.cv].iloc[0].to_numpy()
        #     df -= df.iloc[0]
        
        
        t_df = pd.to_datetime(df.index)
        t = (t_df.values - t_df.values[0]) / 1e9
        self.dt = float(t[1]-t[0])
        
        u_df = df[self.mv]
        y_df = df[self.cv]

        # self.u_ss = df[self.mv].mean().to_numpy()
        self.u_ss = df[self.mv].iloc[0].to_numpy()
        u_df -= self.u_ss

        u = u_df.to_numpy().T
        y = y_df.to_numpy().T

        self.t = t
        self.tt.value = t
        self.time = self.t
        # self.options.MAX_ITER = 1e5
        for i in range(self.nu):
            option_item: TransferOption = self.option_dict[self.mv[i]]

            if not option_item.no_gain:
                self.gain[i].status = 1
                self.gain[i].fstatus = 1

            if option_item.no_ramp:
                self.tau[i].status = 1
                self.tau[i].fstatus = 1

            if option_item.is_dt:
                self.theta[i].status = 1
                self.theta[i].fstatus = 1

            self.tc[i].value = self.t
            self.um[i].value = u[i]

            self.cspline(self.tc[i], self.um[i], self.t, u[i], bound_x=True)

        self.ym[0].value = y[0]
        # self.ym[0].fstatus = 1
        self.ym[0].status = 0
        # yp = self.Param(value=y[0].T)

        # self.Minimize((yp-self.ym[0]) ** 2)
        # self.Solver = 2
        self.options.IMODE = 5
        self.solve(disp=False)

        self.label = [tag_label + '_tf' for tag_label in y_df.columns]
        
        # save optimal values
        for (i, mv_i) in enumerate(self.mv):
            option_item: TransferOption = self.option_dict[mv_i]

            if not option_item.no_gain:
                option_item.gain = self.gain[i][-1]

            if option_item.no_ramp:
                option_item.tau = self.tau[i][-1]

            if option_item.is_dt:
                option_item.theta = self.theta[i][-1]
            if option_item.order == 2:
                if option_item.is_zeta:
                    option_item.zeta = self.zeta[i][-1]

        self.status = True

        return self.ym.copy()

    def simulate(self, u_df):
        u_df = u_df.copy()
        self._connections = []
        self._objects = []
        self.clear_data()

        if u_df.index.dtype == 'float64' or 'int64':
            t = u_df.index.values
        elif u_df.index.dtype == 'O':
            t_df = pd.to_datetime(u_df.index)
            t = (t_df.values - t_df.values[0]) / 1e9
        else:
            t_df = pd.to_datetime(u_df.index)
            t = (t_df.values - t_df.values[0]) / 1e9

        self.t = t
        self.time = self.t

        u_df -= self.u_ss
        
        u = u_df.to_numpy().T
        
        for i in range(self.nu):
            option_item: TransferOption = self.option_dict[self.mv[i]]

            if not option_item.no_gain:
                self.gain[i].status = 0
                self.gain[i].fstatus = 0
                self.gain[i].value = self.gain[i].value[0]

            if option_item.no_ramp:
                self.tau[i].status = 0
                self.tau[i].fstatus = 0
                self.tau[i].value = self.tau[i].value[0]

            if option_item.is_dt:
                self.theta[i].status = 0
                self.theta[i].fstatus = 0
                self.theta[i].value = self.theta[i].value[0]

            if option_item.is_zeta and option_item.order == 2:
                self.zeta[i].status = 0
                self.zeta[i].fstatus = 0
                self.zeta[i].value = self.zeta[i].value[0]

            if option_item.order == 2:
                self.dxm_dt[i].value = self.ym[0].value

            self.um[i].value = u[i]
            # self.um[i].status = 0

            self.xm[i].value = 0
            self.xm[i].fstatus = 0
            self.tc[i].value = self.t
            # self.tc[i].lower = 0

            self.cspline(self.tc[i], self.um[i], self.t, u[i], bound_x=True)

        self.tt.value = t
        self.ym[0].value = 0
        self.ym[0].status = 1
        # self.ym[0].fstatus = 0
        # self.Solver = 2

        self.options.IMODE = 5
        self.solve(disp=False)

        return self.ym.copy()


# df = read_csv("../../signal_df.csv", index_col='Time')
# df = read_csv("../../new.csv", index_col='Unnamed: 0')

# df = df.iloc[50:]
# # df = df - df.iloc[0]
# # df = df.iloc[100:250]

# # Import CSV data file
# # Column 1 = time (t)
# # Column 2 = input (u)
# # Column 3 = output (y)
# # url = 'http://apmonitor.com/pdc/uploads/Main/data_sopdt.txt'
# # df = read_csv('data_sopdt.txt', index_col='Time')
# df -= df.iloc[0]
# # t = df.index.values
# # u = df['u'].values
# # y = df['y'].values




# tf = TransferItem()

# o1 = TransferOption()
# o2 = TransferOption()

# # o1.name = 'u1'
# # o1.no_ramp = 1
# # o1.no_gain = 0
# # o1.order = 1
# # # o1.is_zeta = 0
# # o2.name = 'u2'
# # o2.no_ramp = 1
# # o2.no_gain = 0
# # o2.order = 1
# # tf.option_dict['u1'] = o1
# # tf.option_dict['u2'] = o2

# o1.name = 'F_cw'
# o1.no_ramp = 1
# o1.no_gain = 0
# o1.order = 1
# # o1.is_zeta = 0
# o2.name = 'T1'
# o2.no_ramp = 1
# o2.no_gain = 0
# o2.order = 1
# tf.option_dict['F_cw'] = o1
# tf.option_dict['T1'] = o2

# tf.mv = ['F_cw', 'T1']
# tf.cv = ['CA2']
# tf.const_den = False
# tf.build()
# yp_ = tf.identify(df)

# Time = arange(0, 1000, 10)
# u = zeros((2, 100))
# u[0][int(100 / 10):] = 1

# u_df = DataFrame(u.T, columns=tf.mv)
# u_df += 0

# u_df.set_index(Time, inplace=True)

# y_i = tf.simulate(u_df=u_df)

# plt.plot(y_i[0])
# plt.show()






# u0_df = df[tf.mv]
# u_df = u0_df
# # u = u_df.to_numpy().T
# u_df_valid = u_df.iloc[10:]
# yp = tf.simulate(u_df_valid)
# yp = array(yp.tolist()).T
# yp_df = DataFrame(yp, columns=tf.label, index=u_df_valid.index)

# plt.plot(df['y2'],'k.-',lw=2,label='Process Data')
# plt.plot(yp_df,'r--',lw=2,label='Optimized SOPDT')
# plt.xticks(rotation=45)
# plt.legend()
# plt.show()

# print('Kp: ', tf.gain[0].value[0])
# print('taup: ',  tf.tau[0].value[0])
# print('thetap: ', tf.theta[0].value[0])
# print('zetap: ', tf.zeta[0].value[0])
