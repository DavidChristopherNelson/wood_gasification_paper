import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

# Given data points for 'Days since ramp up' and 'Estimated horsepower of retrofitted vehicles'
days_since_ramp_up = [0, 92, 274, 457, 639, 822, 1004, 1187, 1370, 1553, 1735]
estimated_hp = [0, 419477.8, 1989726.2, 2949371.25, 2851494.1, 3028677.05,
                3054948.4, 3091048.8, 2980092.85, 3040829.4, 3036477.85]
errors = [0.0, 74679.2360182784, 330879.959546071, 471947.894262791, 441828.739594565,
          468433.133075141, 459835.09425471, 471200.694563979, 454348.856692435,
          456448.467667923, 460527.11142038]

# Creating the plot
plt.figure(figsize=(15, 10))

# Plotting the estimated horsepower data with error bars
plt.errorbar(days_since_ramp_up, estimated_hp, yerr=errors, fmt='o', color='blue',
             ecolor='lightgray', elinewidth=3, capsize=5, label='Estimated horsepower with error', linewidth=3.0)


# Linear line with a given slope and intercept at y=0
slope = 6606.40310562299
intercept = 0  # y-intercept is at y=0
# Generate a range of x values from 0 to the maximum of the provided data for the linear line
x_values = np.linspace(0, max(days_since_ramp_up), 1000)
# Calculate the corresponding y values for the linear line
y_values_linear = slope * x_values + intercept
# Plotting the linear line
plt.plot(x_values, y_values_linear, color='orangered', linestyle='--', label=f'Linear fit (slope={slope})', linewidth=3.0)

# Adding labels and title
plt.xlabel('Days Since Ramp Up (days)', fontsize=24)
plt.ylabel('Horsepower of Retrofitted Vehicles (hp)', fontsize=24)

# Adding a legend to the plot
plt.legend(fontsize=20)

# Adding grid for better readability
plt.grid(True)

plt.tight_layout()
plt.xlim([0, 1750])
plt.ylim([0, 4000000])
plt.tick_params(axis='both', which='major', labelsize=16)

# Define a custom formatter function
def custom_formatter(x, pos):
  return r'${:.2f}\times10^{{6}}$'.format(x / 10**6)

# Apply the custom formatter to the y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(custom_formatter))

plt.savefig('plot_swedish_gasification.tiff', dpi=500, bbox_inches='tight')

# Displaying the plot
plt.show()
