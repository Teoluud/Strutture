from utils import *

class Calibration:
    """ Lambda - pixel conversion using PyROOT.
    """

    def __init__(self, input_file: str, x_column: str, y_column: str, err_x_col: str = '', err_y_col: str = '') -> None:
        """ Constructor.
        """
        self.dataframe: pd.DataFrame = read_file(input_file)
        # ROOT expects double-precision floats (float64)
        self.x: np.ndarray      = self.dataframe[x_column].to_numpy(dtype=np.float64)
        self.y: np.ndarray      = self.dataframe[y_column].to_numpy(dtype=np.float64)
        # ROOT needs an array for both errors even if they are zero
        self.err_x: np.ndarray  = np.zeros(len(self.x), dtype=np.float64) if err_x_col == '' else self.dataframe[err_x_col].to_numpy(dtype=np.float64)
        self.err_y: np.ndarray  = np.zeros(len(self.y), dtype=np.float64) if err_y_col == '' else self.dataframe[err_y_col].to_numpy(dtype=np.float64)
        self.npoints: int       = len(self.x)
        # Initialize the Graph
        self.graph = ROOT.TGraphErrors(self.npoints, self.x, self.y, self.err_x, self.err_y)

    def plot(self, title:str, xlabel: str, ylabel: str) -> None:
        """ Intializes graph and canvas.
        """
        self.graph.SetTitle(f"{title};{xlabel};{ylabel}")
        self.graph.SetMarkerStyle(20) # Filled circle
        self.graph.SetMarkerSize(0.8)
        self.graph.SetMarkerColor(ROOT.kBlue) 
        self.graph.SetLineColor(ROOT.kBlue) 
        # Initialize the Canvas
        self.canvas = ROOT.TCanvas("canvas", "Calibration Fit", 1000, 700) 
        self.canvas.cd()
        self.graph.Draw("AP")   # "A" draws axes, "P" draws markers

    def fit_linear(self) -> None:
        """ Performs a linear fit using ROOT's Minuit fitter.
        """
        # Define a 1D linear function
        min_x, max_x = np.min(self.x), np.max(self.x)
        self.fit_func = ROOT.TF1("linear_fit", "pol1", min_x, max_x) 
        # Set initial guesses for [intercept, slope]
        self.fit_func.SetParameters(1.0, 1.0) 
        self.fit_func.SetLineColor(ROOT.kRed)

        fit_result = self.graph.Fit(self.fit_func, "S")
        # Extract parameters
        self.p0 = self.fit_func.GetParameter(0) # Intercept
        self.e0 = self.fit_func.GetParError(0)
        self.p1 = self.fit_func.GetParameter(1) # Slope
        self.e1 = self.fit_func.GetParError(1)
        self.cov_01 = fit_result.GetCovarianceMatrix()[0, 1]
        chi2 = self.fit_func.GetChisquare()
        ndf = self.fit_func.GetNDF()
        reduced_chi2 = chi2 / ndf if ndf > 0 else 0
        pvalue = self.fit_func.GetProb()
        print(f"Fitted parameters: Intercept = {self.p0:.3f} ± {self.e0:.3f}, Slope = {self.p1:.3f} ± {self.e1:.3f}")
        print(f"Chi-squared: {chi2:.3f}")
        print(f"Degrees of freedom: {ndf}")
        print(f"Reduced Chi-squared: {reduced_chi2:.3f}")
        print(F"P-value: {pvalue:.3f}")
        # Tell ROOT to display the fit parameters in a stat box on the canvas
        ROOT.gStyle.SetOptFit(1111)

    def display(self, save_path: str = "calibration_fit.pdf", keep_open: bool = False) -> None:
        """ Updates the canvas, saves it, and keeps the script alive to view it.
        """
        self.canvas.cd()
        # Force ROOT to physically draw the canvas so the stat box is created
        self.canvas.Update() 
        # Grab the stat box from the graph's list of functions
        stat_box = self.graph.GetListOfFunctions().FindObject("stats")
        if stat_box:
            # Move the box using Normalized Device Coordinates (0.0 to 1.0) to the top-left corner
            stat_box.SetX1NDC(0.15)  # Left edge 
            stat_box.SetX2NDC(0.35)  # Right edge 
            stat_box.SetY1NDC(0.70)  # Bottom edge 
            stat_box.SetY2NDC(0.88)  # Top edge
            # Tell the canvas we made a change and update it again
            self.canvas.Modified()
            self.canvas.Update()
        # Save PDF
        self.canvas.SaveAs(save_path)
        print(f"Plot successfully saved to {save_path}")
        # Keep the Python script from exiting immediately so you can see the window
        if keep_open:
            input("Press Enter to exit and close the plot...")

if __name__ == '__main__':
    lambda_pixel = Calibration('lambda_pixel.csv', 'pixel', 'lambda', 'semi-ampiezza')
    lambda_pixel.plot('Lambda - Pixel Calibration', 'Pixel', '#lambda [nm]')
    lambda_pixel.fit_linear()
    lambda_pixel.display('lambda_pixel_fit.pdf')

    pixel_arb   = Calibration('pixel_unarb.csv', 'un arb', 'pixel', 'err un arb', 'semi-ampiezza')
    pixel_arb.plot('Pixel - Arbitrary Unit Calibration', 'Arbitrary Unit', 'Pixel')
    pixel_arb.fit_linear()
    pixel_arb.display('pixel_unarb_fit.pdf')