import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import ROOT

def read_file(input_file: str) -> pd.DataFrame:
    """ Imports the CSV into a dataframe.
    """
    df: pd.DataFrame = pd.read_csv(input_file, comment='#')
    return df

def numeric_derivative():
    """ Calculates the derivative of a dataset.
    """
    
    pass


class FitParameterStruct:
    """ Class that works like a struct for fit parameters.
    """

    def __init__(self, parameter_list: list, par_errors_list: list = [], covariance_list: list = []) -> None:
        """ Constructor.
        """
        self.parameters = parameter_list
        self.par_errors = par_errors_list
        self.covariance = covariance_list


def fit_linear(graph, x: np.ndarray, param0=1.0, param1=1.0) -> FitParameterStruct:
    """ Performs a linear fit using ROOT's Minuit fitter.
    """
    # Define a 1D linear function
    min_x, max_x = np.min(x), np.max(x)
    fit_func = ROOT.TF1("linear_fit", "pol1", min_x, max_x) 
    # Set initial guesses for [intercept, slope]
    fit_func.SetParameters(param0, param1) 
    fit_func.SetLineColor(ROOT.kRed)

    fit_result = graph.Fit(fit_func, "S")
    # Extract parameters
    p0 = fit_func.GetParameter(0) # Intercept
    e0 = fit_func.GetParError(0)
    p1 = fit_func.GetParameter(1) # Slope
    e1 = fit_func.GetParError(1)
    cov_01 = fit_result.GetCovarianceMatrix()[0, 1]
    fit_struct = FitParameterStruct([p0, p1], [e0, e1], [cov_01])
    chi2 = fit_func.GetChisquare()
    ndf = fit_func.GetNDF()
    reduced_chi2 = chi2 / ndf if ndf > 0 else 0
    pvalue = fit_func.GetProb()
    print(f"Fitted parameters: Intercept = {p0:.3f} ± {e0:.3f}, Slope = {p1:.3f} ± {e1:.3f}")
    print(f"Chi-squared: {chi2:.3f}")
    print(f"Degrees of freedom: {ndf}")
    print(f"Reduced Chi-squared: {reduced_chi2:.3f}")
    print(f"P-value: {pvalue:.3f}")
    # Tell ROOT to display the fit parameters in a stat box on the canvas
    ROOT.gStyle.SetOptFit(1111)
    return fit_struct

def weighted_average(value: np.ndarray, sigma: np.ndarray) -> tuple[float, float]:
    """ Returns average weighted with the inverse variance.
    """
    weight = 1/sigma**2
    average = float(np.sum(value*weight) / np.sum(weight))
    error = np.sqrt(1 / np.sum(weight))
    return average, error

class DataAnalysis:
    """ Class for generic data analysis methods.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """ Constructor.
        """
        self.df: pd.DataFrame = dataframe
        self.graphs = []

    def make_plot(self, x_col:str, y_col: str, ex_col:str, ey_col: str, title: str, xlabel: str, ylabel: str) -> ROOT.TGraphErrors:
        """ Creates the graph and returns it.
        """
        x: np.ndarray   = self.df[x_col].to_numpy(dtype=np.float64)
        y: np.ndarray   = self.df[y_col].to_numpy(dtype=np.float64)
        ex: np.ndarray  = np.zeros(len(x), dtype=np.float64) if ex_col == '' else self.df[ex_col].to_numpy(dtype=np.float64)
        ey: np.ndarray  = np.zeros(len(y), dtype=np.float64) if ey_col == '' else self.df[ey_col].to_numpy(dtype=np.float64)
        n: int          = len(x)
        # Create the graph
        graph: ROOT.TGraphErrors = ROOT.TGraphErrors(n, x, y, ex, ey)
        graph.SetTitle(f"{title};{xlabel};{ylabel}")
        graph.SetMarkerStyle(21)
        graph.SetMarkerColor(ROOT.kBlue + 2)
        self.graphs.append(graph)
        return graph
    
    def make_simple_plot(self, x_col: str, y_col: str, title: str, xlabel: str, ylabel: str) -> ROOT.TGraph:
        """ Creates a TGraph (without error bars).
        """
        x: np.ndarray   = self.df[x_col].to_numpy(dtype=np.float64)
        y: np.ndarray   = self.df[y_col].to_numpy(dtype=np.float64)
        n: int          = len(x)
        graph: ROOT.TGraph = ROOT.TGraph(n, x, y)
        graph.SetTitle(f"{title};{xlabel};{ylabel}")
        graph.SetMarkerStyle(21)
        graph.SetMarkerColor(ROOT.kBlue + 2)
        self.graphs.append(graph)
        return graph
    
    def display(self, canvas_name: str, graph, save_png:bool = False) -> None:
        canvas = ROOT.TCanvas(canvas_name, canvas_name, 1920, 1080)
        canvas.cd()
        graph.Draw("AP")
        if save_png:
             canvas.SaveAs(f"{canvas_name}.png")
        input("Press Enter to exit and close the plot...")
