from .tf_item import TransferItem, TransferOption
from numpy import empty, array, zeros, arange
from pandas import DataFrame


class TF(TransferItem):
    def __init__(self):
        super().__init__()
        self.y_ss = DataFrame()
        self.models = {}
        
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
            
        return yp_df


    def predict(self, u_df: DataFrame = None):
        u_df = u_df.copy()
        self.y_ss = u_df.iloc[0].to_numpy()
        u_df -= u_df.iloc[0]
        yp_df = DataFrame()

        for cv_i in self.cv:
            model: TransferItem = self.models[cv_i]
            # u_df -= model.u_ss
            y_i = model.simulate(u_df=u_df)
            yp_df[model.cv[0]+"_tf"] = array(y_i[0])
            
        yp_df += self.y_ss
        
        return yp_df
    
    def step_response(self, mv_name, cv_name):
        # simulation time = 12 * tau
        # for cv_i in self.cv:
        model: TransferItem = self.models[cv_name]
        
        # for (i, mv_i) in enumerate(model.mv):
        option_item = model.option_dict[mv_name]
        
        tau = option_item.tau if option_item.tau else 1
        
        tf = 25*tau
        Time = arange(0, tf+1, model.dt)
        sim_ts = len(Time)

        u = zeros((model.nu, sim_ts))
        u[option_item.id][int(9*tau/model.dt):] = 1
        
        u_df = DataFrame(u.T, columns=model.mv)
        # u_df += model.u_ss
        
        u_df.set_index(Time, inplace=True)
        
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
        
        
        






