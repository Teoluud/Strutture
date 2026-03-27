from calibration import *

class ZeemanAnalysis(DataAnalysis):
    """ Class that handles zeeman data analysis.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """ Constructor.
        """
        super().__init__(dataframe)

    def calibration_average(self, calibration_prefix: str) -> tuple[float, float, float, float]:
        """ Fits the 4 calibration datasets and returns the average.
        """
        p0_list = []
        p1_list = []
        e0_list = []
        e1_list = []
        for i in range(1,5):
            cal_file: str = '%s_%i.csv' % (calibration_prefix, i)
            magnetic_cal = Calibration(cal_file, 'I(A)', 'B(mT)', 'err I(A)', 'err B(mT)')
            magnetic_cal.fit_linear()           # CHANGE FITTING MODEL HERE! (if needed)
            magnetic_cal.plot(f'Calibrazione del magnete {i}', 'I [A]', 'B [mT]')
            magnetic_cal.display(('%s_%i.jpeg'%(calibration_prefix, i)))
            p0_list.append(magnetic_cal.p0)
            p1_list.append(magnetic_cal.p1)
            e0_list.append(magnetic_cal.e0)
            e1_list.append(magnetic_cal.e1)
            #e01_cal = magnetic_cal.cov_01       # Think about propagating covariance
        # Convert lists to np.array
        p0_list = np.array(p0_list)
        p1_list = np.array(p1_list)
        e0_list = np.array(e0_list)
        e1_list = np.array(e1_list)
        # Calculate average
        p0_ave, e0_ave = weighted_average(p0_list, e0_list)
        p1_ave, e1_ave = weighted_average(p1_list, e1_list)
        return p0_ave, p1_ave, e0_ave, e1_ave

    def calculate_physics_quantities(self, calibration_prefix: str) -> None:
        """ Calculates quantities and their errors, adds them to df.
        """
        p0, p1, e0, e1 = self.calibration_average(calibration_prefix)
        # Calculate magnetic field
        err_b_pos: float        = 20.  # mT
        self.df['B(mT)']        = p0 + p1 * self.df['I(A)']
        self.df['err B(mT)']    = np.sqrt(e0**2 + (self.df['I(A)']*e1)**2 + 
                                          #2*self.df['I(A)']*e01_cal + 
                                          (e1*self.df['err I(A)'])**2) + err_b_pos    # mT


if __name__ == '__main__':
    df = read_file('zeeman_data.csv')
    analysis = ZeemanAnalysis(df)
    analysis.calculate_physics_quantities('zeeman_calibration/zeeman_calibration')
    print(analysis.df)