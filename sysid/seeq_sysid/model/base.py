from pandas import DataFrame


class Model:
    def __init__(self):
        self.status = False
        self.label = None
        self.model = None
        self.df = None
        self.label = None
        self.formula = None
        self.mv = None
        self.cv = None
        self.nu = None
        self.ny = None
        self.yp = None
        self.error = None
        self.error_best = 1e9
        self.eval_best = 1e9
        self.thresh = 1e-6
        self.order = 4

        self.u_ss = None
        self.x_ss = None
        self.y_ss = None
        # self.n = None
        # self.m = None
        # self.d = None
        #
        # self.p = None
        # self.q = None

        # self.eps = None
        # self.A = None
        # self.B = None
        # self.C = None
        # self.D = None

        # self.alpha = None
        # self.beta = None

    def identify(self, df: DataFrame = None):
        pass

    def predict(self, df: DataFrame = None):
        pass

    def forecast(self, df: DataFrame = None):
        pass
