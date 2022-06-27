from .tf_item import TransferItem, TransferOption
from numpy import empty, array, zeros, arange
from pandas import DataFrame
from scipy.signal import TransferFunction
from .arx import create_formula_variable_name


class TF(TransferItem):
    def __init__(self):
        super().__init__()
        self.y_ss = DataFrame()
        self.models = {}
        self.dummy = None
        self.formula = None
        
    def add_model(self, cv_name, model: TransferItem):
        self.models[cv_name] = model
        self.cv.append(cv_name)

    def identify(self, df, cv_name):
        df = df.copy()

        self.y_ss[cv_name] = df[[cv_name]].iloc[0].to_numpy()

        df -= df.iloc[0]
        
        yp_df = DataFrame()

        # self.nu = len(self.mv)
        self.ny = len(self.cv)

        # for cv_i in self.cv:
        model: TransferItem = self.models[cv_name]
        model.build()
        y_i = model.identify(df=df)
        yp_df[cv_name+"_tf"] = array(y_i[0])
        
        yp_df += self.y_ss[cv_name].to_numpy()
        
        yp_df = yp_df.set_index(df.index)
            
        return yp_df

    def predict(self, u_df, cv_name):
        u_df = u_df.copy()
        
        self.y_ss[cv_name] = u_df[[cv_name]].iloc[0].to_numpy()
        
        u_df -= u_df.iloc[0]
        
        yp_df = DataFrame()

        # for cv_i in self.cv:
        model: TransferItem = self.models[cv_name]
        # u_df -= model.u_ss
        y_i = model.simulate(u_df=u_df[model.mv])
        yp_df[cv_name+"_tf"] = array(y_i[0])
            
        yp_df += self.y_ss[cv_name].to_numpy()
        
        yp_df = yp_df.set_index(u_df.index)
        
        return yp_df
    
    def step_response(self, mv_name, cv_name):
        # simulation time = 12 * tau
        # for cv_i in self.cv:
        model: TransferItem = self.models[cv_name]
        
        # for (i, mv_i) in enumerate(model.mv):
        option_item = model.option_dict[mv_name]
        
        tau = option_item.tau if option_item.tau else 1
        
        tf = max(25*tau, 10*model.dt)
        Time = arange(0, tf+1, model.dt)
        sim_ts = len(Time)

        u = zeros((model.nu, sim_ts))
        u[option_item.id][int(9*tau/model.dt):] = 1
        
        u_df = DataFrame(u.T, columns=model.mv)
        # u_df += model.u_ss
        
        u_df.set_index(Time, inplace=True)
        self.dummy = u_df.copy()
        y_i = model.simulate(u_df=u_df)
        
        yp_df = DataFrame()
        # yp_df[cv_name+"_tf"] = array(y_i[0])/abs(option_item.gain)
        yp_df[cv_name+"_tf"] = array(y_i[0])

        # yp_df += self.y_ss
        yp_df.set_index(Time, inplace=True)
        
        option_item.calc_step_info(yp_df.index.to_numpy(), yp_df.to_numpy().T[0])
        
        return yp_df
    
    def get_step_info(self, mv_name, cv_name):
        model = self.models[cv_name]
        option_item = model.option_dict[mv_name]
        return option_item.get_step_info()
    
    def get_model_info(self, mv_name, cv_name):
        model = self.models[cv_name]
        option_item = model.option_dict[mv_name]
        return option_item.get_model_info()

    def set_sim_time(self):
        # set max time constant for each output (CV)
        for cv_i in self.cv:
            model: TransferItem = self.models[cv_i]
            model.tau_max = 1
            
            for mv_i in model.mv:
                option_item = model.option_dict[mv_i]
                if option_item.tau:
                    if option_item.tau > model.tau_max:
                        model.tau_max = option_item.tau
            
            model.sim_time = 4 * model.tau_max

    def create_formula(self, df, tags):
        y_name = self.cv

        yf_name = create_formula_variable_name(y_name)

        formula_dic = {}
        for tag in range(len(yf_name)):
            formula_dic[yf_name[tag]] = tags[tags['Name'] == y_name[tag]]

        formula_list = []

        for cv_i in range(len(self.cv)):
            cv_name = y_name[cv_i]
            y_ss = df[cv_name].iloc[0]
            y_opt = self.models[cv_name]

            u_name = y_opt.mv
            uf_name = create_formula_variable_name(u_name)
            formula = ''
            for tag in range(len(uf_name)):
                formula_dic[uf_name[tag]] = tags[tags['Name'] == u_name[tag]]

            timestep = y_opt.dt

            for mv_i in range(len(y_opt.mv)):
                mv_name = y_opt.mv[mv_i]
                u_opt = y_opt.option_dict[mv_name]
                u_ss = df[mv_name].iloc[0]

                tf_sys = TransferFunction(u_opt.num, u_opt.den)
                tfd_sys = tf_sys.to_discrete(dt=timestep, method='zoh')
                num = tfd_sys.num
                den = tfd_sys.den

                n_a = len(den)
                n_b = len(num)

                for i in range(1, n_a):
                    formula += ' ({}.move({}s)-{})*({})\n+'.format(yf_name[cv_i], i * timestep, y_ss, -den[i])

                for j in range(n_b):
                    formula += ' ({}.move({}s)-{})*({})\n+'.format(uf_name[mv_i], j * timestep + u_opt.theta, u_ss,
                                                                   num[j])

            formula += str(y_ss)

            formula_list.append({
                'Name': '{} tf'.format(y_name[cv_i]),
                'Type': 'CalculatedSignal',
                'Description': 'TF Model {} Formula '.format(y_name[cv_i]),
                'Formula': formula,
                'Formula Parameters': formula_dic
            })

        self.formula = DataFrame(formula_list)

        return self.formula
