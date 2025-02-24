import matplotlib.colors as mcolors
import numpy as np

# create colors

def list_colors(number_colors=10):
    cmap = mcolors.LinearSegmentedColormap.from_list("",
                                                    ["salmon", "darkviolet","pink", 'cornflowerblue', "indigo", "violet", "teal", "orange",
                                                     'lightcoral', 'cadetblue', 'lightseagreen', "khaki", 'turquoise', "palevioletred", "purple",
                                                     "forestgreen", 'deepskyblue', 'mediumseagreen', 'aquamarine', 'dodgerblue','seagreen','darkorange',
                                                    'coral', 'royalblue', 'tomato','darkcyan'],
                                                    N=number_colors)

    # Generar valores interpolados en el rango del colormap
    color_indices = np.linspace(0, 1, number_colors)
    color_list = [cmap(index) for index in color_indices]
    return color_list