import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def read_file(input_file: str) -> pd.DataFrame:
    """ Imports the TSV into a dataframe.
    """
    df: pd.DataFrame = pd.read_csv(input_file, sep='\t')
    return df


class DataProcessing:
    """ Processes and elaborates the data.
    """

    def __init__(self, input_file: str, y_column: str, y_err_column: str) -> None:
        self.data_frame: pd.DataFrame   = read_file(input_file)
        self.x: np.ndarray              = self.data_frame['Un arbitr'].to_numpy()
        self.y: np.ndarray              = self.data_frame[y_column].to_numpy()
        self.y_err: np.ndarray          = self.data_frame[y_err_column].to_numpy()


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
    fotod = DataProcessing("data.txt", 'Vpp fotodiodo', 'Err vpp fotodiodo')
    print(fotod.data_frame)
    plt.scatter(fotod.x, fotod.y)
    plt.show()