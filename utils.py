import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import ROOT

def read_file(input_file: str) -> pd.DataFrame:
    """ Imports the CSV into a dataframe.
    """
    df: pd.DataFrame = pd.read_csv(input_file, comment='#')
    return df

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
        ex: np.ndarray  = self.df[ex_col].to_numpy(dtype=np.float64)
        ey: np.ndarray  = self.df[ey_col].to_numpy(dtype=np.float64)
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
    
    def display(self, canvas_name: str, graph) -> None:
        canvas = ROOT.TCanvas(canvas_name, canvas_name, 1000, 800)
        canvas.cd()
        graph.Draw("AP")