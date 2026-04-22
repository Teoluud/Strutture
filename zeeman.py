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
            magnetic_cal.fit_linear(keep_open)           # CHANGE FITTING MODEL HERE! (if needed)
            magnetic_cal.plot(f'Calibrazione del magnete {i}', 'I [A]', 'B [mT]')
            magnetic_cal.display(('%s_%i.png'%(calibration_prefix, i)), keep_open)
            p0_list.append(magnetic_cal.p0)
            p1_list.append(magnetic_cal.p1)
            e0_list.append(magnetic_cal.e0)
            e1_list.append(magnetic_cal.e1)
            cov_list.append(magnetic_cal.cov_01)
        # Convert lists to np.array
        p0_list = np.array(p0_list)
        p1_list = np.array(p1_list)
        e0_list = np.array(e0_list)
        e1_list = np.array(e1_list)
        cov_list = np.array(cov_list)
        # Calculate average
        p0_ave, e0_ave = weighted_average(p0_list, e0_list)
        p1_ave, e1_ave = weighted_average(p1_list, e1_list)
        # Calculate covariance, using its linearity and the indipendence between datasets
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
        print(f"!!!!!!!!!!!!!!!!!!! B(I) = [{p0} +/- {e0}] + [{p1} +/- {e1}]*I")
        err_b_pos: float        = 20.  # mT
        self.df['B(mT)']        = p0 + p1 * self.df['I(A)']
        self.df['err B(mT)']    = np.sqrt(e0**2 + (self.df['I(A)']*e1)**2 + 
                                          2*self.df['I(A)']*e01 + 
                                          (e1*self.df['err I(A)'])**2) + err_b_pos    # mT

def configuration_full_analysis(input_file: str) -> None:
    """ Goes through the whole analysis for a single configuration.
    """
    df = read_file(input_file)
    analysis = ZeemanAnalysis(df)
    pass        # Still needs to be implemented (kind of complicated to keep track of the differences in configurations)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-o', '--keep-open', action='store_true', dest='keep_open', default=False, help='Keeps the window open for every fit.')

    (opts, args) = parser.parse_args()
    
    # Define variables
    REFRACTION_INDEX = 1.4560
    THICKNESS = 3e-3    # m
    PLANCK = 6.626e-34  # J*s
    LIGHT_SPEED = 3e8   # m/s

    #######################################################################
    # LONGITUDINAL GEOMETRY
    #######################################################################
    df_long = read_file('zeeman_data_long.csv')
    analysis_long = ZeemanAnalysis(df_long)
    analysis_long.calculate_physics_quantities('zeeman_calibration/zeeman_calibration', opts.keep_open)
    g_long = analysis_long.make_plot('B(mT)','y','err B(mT)', 'err y', 'Rapporto in funzione di B', 'B [mT]', '#frac{#delta}{#Delta}')
    x_data = np.array(g_long.GetX())
    fit_long: FitParameterStruct = fit_linear(g_long, x_data, 1e-2, 0)
    analysis_long.display("canvas_long", g_long, save_png=False)
    mag_bohr_l = fit_long.parameters[1]*1e3 * PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS*2)
    err_mag_bohr_l = PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS*2) * fit_long.par_errors[1]*1e3
    print(f'Magnetone di Bohr (geometria longitudinale): ({mag_bohr_l:.3e} +/- {err_mag_bohr_l:.3e})J/T')

    #######################################################################
    # TRASVERSAL GEOMETRY
    #######################################################################
    df_trans = read_file('zeeman_data_trasv.csv')
    analysis_trans = ZeemanAnalysis(df_trans)
    analysis_trans.calculate_physics_quantities('zeeman_calibration/zeeman_calibration', opts.keep_open)
    
    g_trans_pos = analysis_trans.make_plot('B(mT)', 'y+', 'err B(mT)', 'err y+', 'Rapporto in funzione di B per #Delta m_L = +1', 'B [mT]', '#frac{#delta}{#Delta}')
    fit_trans_pos: FitParameterStruct = fit_linear(g_trans_pos, np.array(g_trans_pos.GetX()), 1e-2, 0)
    analysis_trans.display("canvas_trans_pos", g_trans_pos, save_png=False)
    mag_bohr_t_pos = fit_trans_pos.parameters[1]*1e3 * PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS)
    err_mag_bohr_t_pos = PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS) * fit_trans_pos.par_errors[1]*1e3
    print(f'Magnetone di Bohr (geometria trasversale, Delta m_L = +1): ({mag_bohr_t_pos:.3e} +/- {err_mag_bohr_t_pos:.3e})J/T')
    
    g_trans_neg = analysis_trans.make_plot('B(mT)', 'y-', 'err B(mT)', 'err y-', 'Rapporto in funzione di B per #Delta m_L = -1', 'B [mT]', '#frac{#delta}{#Delta}')
    fit_trans_neg: FitParameterStruct = fit_linear(g_trans_neg, np.array(g_trans_neg.GetX()), -1e-2, 0)
    analysis_trans.display("canvas_trans_neg", g_trans_neg, save_png=False)
    mag_bohr_t_neg = fit_trans_neg.parameters[1]*1e3 * PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS*-1)
    err_mag_bohr_t_neg = abs(PLANCK * LIGHT_SPEED / (2*REFRACTION_INDEX*THICKNESS*-1) * fit_trans_neg.par_errors[1]*1e3)
    print(f'Magnetone di Bohr (geometria trasversale, Delta m_L = -1): ({mag_bohr_t_neg:.3e} +/- {err_mag_bohr_t_neg:.3e})J/T')

    #######################################################################
    # FINAL RESULT
    #######################################################################
    mag_bohr, err_mag_bohr = weighted_average(np.array([mag_bohr_l,mag_bohr_t_pos,mag_bohr_t_neg]), 
                                              np.array([err_mag_bohr_l,err_mag_bohr_t_pos,err_mag_bohr_t_neg]))
    print(f'\nStima finale magnetone di Bohr: ({mag_bohr:.3e} +/ {err_mag_bohr:.3e})J/T')

    # analysis_long.df.to_csv("zeeman_long_data.csv")
    # analysis_trans.df.to_csv("zeeman_trasv_data.csv")