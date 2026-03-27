from calibration import *

class PhotoconductivityAnalysis(DataAnalysis):
    """ Class that manages the analysis.
    """
    
    def __init__(self, dataframe: pd.DataFrame) -> None:
        """ Constructor.
        """
        super().__init__(dataframe)
    
    def calculate_physics_quantities(self, spec_cal: Calibration, mono_cal: Calibration, R: float, ERR_R: float, ERR_U: float) -> None:
        """ Calculates quantities and their errors, adds them to df.
        """
        # Access constants from the calibration objects
        p0_pix, p1_pix = spec_cal.p0, spec_cal.p1
        e0_pix, e1_pix, e01_pix = spec_cal.e0, spec_cal.e1, spec_cal.cov_01
        p0_arb, p1_arb = mono_cal.p0, mono_cal.p1
        e0_arb, e1_arb, e01_arb = mono_cal.e0, mono_cal.e1, mono_cal.cov_01
        # Calculate lambda
        u = self.df['un arb']
        self.df['lambda'] = p0_pix + p1_pix * (p0_arb + p1_arb * u)
        self.df['err lambda'] = np.sqrt(e0_pix**2 +
                                          (p0_arb+p1_arb*u)**2*e1_pix**2 +
                                          2*(p0_arb+p1_arb*u)*e01_pix +
                                          p1_pix**2*e0_arb**2 +
                                          (p1_pix*u)**2*e1_arb**2 +
                                          2*p1_pix**2*u*e01_arb + 
                                          (p1_pix*p1_arb*ERR_U)**2)
        # Calculate transmittance
        self.df['transmittance'] = self.df['vpp fotod_sample'] / self.df['vpp fotod_ref']
        self.df['err transmittance'] = self.df['transmittance'] * np.sqrt((self.df['err vpp fotod_sample']/self.df['vpp fotod_sample'])**2 +
                                                                          (self.df['err vpp fotod_ref']/self.df['vpp fotod_ref'])**2)
        self.df['deriv_transmittance'] = np.gradient(self.df['transmittance'], self.df['lambda'])
        d_lambda = self.df['lambda'].shift(-1) - self.df['lambda'].shift(1)
        d_trans = self.df['transmittance'].shift(-1) - self.df['transmittance'].shift(1)
        et_prev = self.df['err transmittance'].shift(1)
        et_next = self.df['err transmittance'].shift(-1)
        el_prev = self.df['err lambda'].shift(1)
        el_next = self.df['err lambda'].shift(-1)
        self.df['err deriv_transmittance'] = 1 / d_lambda * np.sqrt(et_next**2 + et_prev**2 + (d_trans/d_lambda)**2 * (el_next**2 + el_prev**2))
        # Calculate photocurrent
        self.df['photocurrent'] = self.df['vpp fotoc'] / R * 1e6      # nA
        self.df['err photocurrent'] = self.df['photocurrent'] * np.sqrt((self.df['err vpp fotoc']/self.df['vpp fotoc'])**2 +
                                                                        (ERR_R/R)**2)
        self.df['deriv_photocurrent'] = np.gradient(self.df['photocurrent'], self.df['lambda'])


if __name__ == "__main__":

    R: float = 1e6
    ERR_R: float = 0.05*R
    ERR_U: float = 1.
    # Create dataframe
    data_df     = read_file('data.csv')
    ref_df      = read_file('reference.csv')
    merged_df   = pd.merge(data_df, ref_df, on='un arb', suffixes=('_sample','_ref'))
    # Calibration
    spectrometer_cal = Calibration('lambda_pixel.csv', 'pixel', 'lambda', 'semi-ampiezza')
    spectrometer_cal.fit_linear()
    monochromator_cal = Calibration('pixel_unarb.csv', 'un arb', 'pixel', 'err un arb', 'semi-ampiezza')
    monochromator_cal.fit_linear()
    analysis = PhotoconductivityAnalysis(merged_df)
    analysis.calculate_physics_quantities(spec_cal=spectrometer_cal, mono_cal=monochromator_cal, R=R, ERR_R=ERR_R, ERR_U=ERR_U)
    # Create canvas
    xmin: float = analysis.df['lambda'].min() - 10
    xmax: float = analysis.df['lambda'].max() + 10
    ymin: float = 0
    ymax: float = analysis.df['photocurrent'].max() * 1.1
    c_dual  = ROOT.TCanvas("c_dual", "c_dual", 1000, 800)
    pad1    = ROOT.TPad("pad1", "pad1", 0, 0, 1, 1)
    pad1.SetLeftMargin(0.15)
    pad1.SetRightMargin(0.15)
    pad1.Draw()
    pad1.cd()
    # Draw transmittance plot
    g_trans = analysis.make_plot('lambda', 'transmittance', 'err lambda', 'err transmittance', '', '#lambda [nm]', 'transmittance')
    g_trans.Draw("AP")
    # Create overlapping transparent pad
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 1)
    pad2.SetLeftMargin(0.15)
    pad2.SetRightMargin(0.15)
    pad2.SetFillStyle(4000)
    pad2.SetFrameFillStyle(0)
    pad2.Range(xmin, ymin, xmax, ymax)
    pad2.Draw()
    pad2.cd()
    # Draw photocurrent plot
    g_phot = analysis.make_plot('lambda', 'photocurrent', 'err lambda', 'err photocurrent', 'Transmittance and Photocurrent', '#lambda [nm]', 'I [nA]')
    g_phot.SetMarkerColor(ROOT.kRed + 1)
    g_phot.SetMarkerStyle(20)
    g_phot.GetXaxis().SetLabelSize(0)
    g_phot.GetXaxis().SetTickLength(0)
    g_phot.GetYaxis().SetTitleOffset(1.0)
    g_phot.Draw("APY+")
    # Draw legend
    legend = ROOT.TLegend(0.2, 0.7, 0.4, 0.8)
    legend.AddEntry(g_trans, "Transmittance", "ple")
    legend.AddEntry(g_phot, "Photocurrent", "ple")
    legend.SetBorderSize(0)
    legend.Draw()

    g_ref = analysis.make_plot('lambda', 'vpp fotod_ref', 'err lambda', 'err vpp fotod_ref', 'Reference Spectrum', '#lambda [nm]', 'Vpp [mV]')
    analysis.display('c_ref', g_ref)

    #g_d_trans = analysis.make_plot('lambda', 'deriv_transmittance', 'err lambda', 'err deriv_transmittance', 'Derivative', '#lambda [nm]', 'dT/d#lambda [nm^-1]')
    g_d_trans = analysis.make_simple_plot('lambda', 'deriv_transmittance', 'Derivative', '#lambda [nm]', 'dT/d#lambda [nm^-1]')
    g_d_trans.Fit("gaus", "R", "", 620, 640)
    fit_func = g_d_trans.GetFunction("gaus")
    fit_func.SetNpx(1000)
    analysis.display('c_d_trans', g_d_trans)
    

    input("Press Enter to exit and close the plot...")