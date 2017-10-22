"""

All things graphing, like an oscilliscope, etc

"""


import numpy as np
import matplotlib.pyplot as plt



# shows basic sample data
def show_data(samples):
    plt.plot(samples)
    plt.xlabel("Sample")
    plt.ylabel("Sample Value")
    plt.show()



