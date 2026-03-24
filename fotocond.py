from calibration import *

class DataProcessing:
    """ Processes and elaborates the data.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        pass

    def config(self, x_column: str, y_column: str, y_err_column: str) -> None:
        """ Defines the x and y arrays.
        """
        self.x: np.ndarray      = self.data_frame[x_column].to_numpy()
        self.y: np.ndarray      = self.data_frame[y_column].to_numpy()
        self.y_err: np.ndarray  = self.data_frame[y_err_column].to_numpy()


class Display(DataProcessing):
    """ Handles the graphical representation.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        pass

    def display(self) -> None:
        """ Displays the plots.
        """
        plt.show()

    def add_figure(self) -> None:
        plt.figure()


if __name__ == "__main__":

    R: float = 1e6
    ERR_R: float = 0.05*R

    data_df     = read_file('data.csv')
    ref_df      = read_file('reference.csv')
    merged_df   = pd.merge(data_df, ref_df, on='un arb', suffixes=('_sample','_ref'))
    # Calculate transmittance
    merged_df['transmittance'] = merged_df['vpp fotod_sample'] / merged_df['vpp fotod_ref']
    print(merged_df)