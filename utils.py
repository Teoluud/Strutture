import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def read_file(input_file: str) -> pd.DataFrame:
    """ Imports the TSV into a dataframe.
    """
    df: pd.DataFrame = pd.read_csv(input_file)
    return df