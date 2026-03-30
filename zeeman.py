from calibration import *

class ZeemanAnalysis(DataAnalysis):
    """ Class that handles zeeman data analysis.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """ Constructor.
        """
        super().__init__(dataframe)

    def calibration_average(self, calibration_prefix: str, keep_open: bool) -> tuple[tuple[float, float], tuple[float, float], float]:
        """ Fits the 4 calibration datasets and returns the average.
        """
        p0_list = []
        p1_list = []
        e0_list = []
        e1_list = []
        cov_list = []
        for i in range(1,5):
            cal_file: str = '%s_%i.csv' % (calibration_prefix, i)
            magnetic_cal = Calibration(cal_file, 'I(A)', 'B(mT)', 'err I(A)', 'err B(mT)')
            magnetic_cal.fit_linear()           # CHANGE FITTING MODEL HERE! (if needed)
            magnetic_cal.plot(f'Calibrazione del magnete {i}', 'I [A]', 'B [mT]')
            magnetic_cal.display(('%s_%i.jpeg'%(calibration_prefix, i)), keep_open)
            p0_list.append(magnetic_cal.p0)
            p1_list.append(magnetic_cal.p1)
            e0_list.append(magnetic_cal.e0)
            e1_list.append(magnetic_cal.e1)
            cov_list.append(magnetic_cal.cov_01)       # Think about propagating covariance
        # Convert lists to np.array
        p0_list = np.array(p0_list)
        p1_list = np.array(p1_list)
        e0_list = np.array(e0_list)
        e1_list = np.array(e1_list)
        cov_list = np.array(cov_list)
        # Calculate average
        p0_ave, e0_ave = weighted_average(p0_list, e0_list)
        p1_ave, e1_ave = weighted_average(p1_list, e1_list)
        weight0 = 1/e0_list**2
        weight1 = 1/e1_list**2
        weight_tot_0 = np.sum(weight0)
        weight_tot_1 = np.sum(weight1)
        cov01 = float(1/(weight_tot_0*weight_tot_1) * np.sum(weight0*weight1*cov_list))        
        return (p0_ave, e0_ave), (p1_ave, e1_ave), cov01

    def calculate_physics_quantities(self, calibration_prefix: str, keep_open: bool) -> None:
        """ Calculates quantities and their errors, adds them to df.
        """
        (p0, e0), (p1, e1), e01 = self.calibration_average(calibration_prefix, keep_open)
        # Calculate magnetic field
        err_b_pos: float        = 20.  # mT
        self.df['B(mT)']        = p0 + p1 * self.df['I(A)']
        self.df['err B(mT)']    = np.sqrt(e0**2 + (self.df['I(A)']*e1)**2 + 
                                          2*self.df['I(A)']*e01 + 
                                          (e1*self.df['err I(A)'])**2) + err_b_pos    # mT


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-o', '--keep-open', action='store_true', dest='keep_open', default=False, help='Keeps the window open for every fit.')

    (opts, args) = parser.parse_args()
    df = read_file('zeeman_data.csv')
    analysis = ZeemanAnalysis(df)
    analysis.calculate_physics_quantities('zeeman_calibration/zeeman_calibration', opts.keep_open)
    graph = analysis.make_plot('B(mT)','y','err B(mT)', 'err y', 'Rapporto in funzione di B', 'B [mT]', '#frac{#delta}{#Delta}')
    x_data = np.array(graph.GetX())
    (p0, e0), (p1, e1), cov = fit_linear(graph, x_data, 1e-2, 0)
    analysis.display("canvas", graph)
    # Define variables
    REFRACTION_INDEX = 1.4560
    THICKNESS = 3e-3 # m
    PLANCK = 6.626e-34 # Js
    LIGHT_SPEED = 3e8   #m/s
    mag_bohr = p1*1e3 * PLANCK * LIGHT_SPEED / (4*REFRACTION_INDEX*THICKNESS)
    err_mag_bohr = PLANCK * LIGHT_SPEED / (4*REFRACTION_INDEX*THICKNESS) * e1*1e3
    print(f'Prima stima magnetone di Bohr: ({mag_bohr:.3e} +/- {err_mag_bohr:.3e})J/T')