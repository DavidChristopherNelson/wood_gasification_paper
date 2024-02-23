import os
import matplotlib.pyplot as plt
import pprint
import time
from numbers_utils import close_numbers_file
from numbers_utils import open_numbers_file
from numbers_utils import read_cell_value
from sample_gaussian import sample_gaussian
from matplotlib.ticker import FuncFormatter
import statistics
import numpy as np


# Clear the console
os.system('clear')
start_time = time.time()

# Closes all other numbers files that may be open just to ensure data is read
# from the correct file. This is probably not necessary.
for _ in range(5):
    close_numbers_file

# Open spreadsheet and read the required parameters.
open_numbers_file ("Gasification Model V3")

global unconverted_transport_diesel_consumption_per_hp, diesel_transport_capacity_hp, initial_delay, rate_of_gasification, converted_transport_diesel_consumption_per_hp
global unconverted_production_diesel_consumption_per_hp, diesel_production_capacity_hp, converted_production_diesel_consumption_per_hp

initial_delay_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B2"
))
initial_delay_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C2"
))
initial_diesel_reserve_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B3"
))
initial_diesel_reserve_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C3"
))
initial_gasoline_reserve_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B4"
))
initial_gasoline_reserve_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C4"
))
rate_of_gasification_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B5"
))
rate_of_gasification_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C5"
))
diesel_transport_capacity_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B6"
))
diesel_transport_capacity_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C6"
))
diesel_production_capacity_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B7"
))
diesel_production_capacity_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C7"
))
gasoline_production_capacity_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B8"
))
gasoline_production_capacity_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C8"
))
unconverted_transport_diesel_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B9"
))
unconverted_transport_diesel_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C9"
))
converted_transport_diesel_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B10"
))
converted_transport_diesel_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C10"
))
unconverted_production_diesel_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B11"
))
unconverted_production_diesel_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C11"
))
converted_production_diesel_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B12"
))
converted_production_diesel_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C12"
))
unconverted_production_gasoline_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B13"
))
unconverted_production_gasoline_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C13"
))
converted_production_gasoline_consumption_per_hp_mean = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B14"
))
converted_production_gasoline_consumption_per_hp_uncertainty = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "C14"
))

# Order of gasification
# 1.) Initial delay period
# 2.) Diesel transportation
# 3.) Diesel production
# 4.) Gasoline production

def instantaneous_diesel_transport_consumption(t):
  global is_initial_delay_over, unconverted_transport_diesel_consumption_per_hp, diesel_transport_capacity_hp, is_initial_delay_over, initial_delay\
    , is_all_diesel_transport_gasified, rate_of_gasification, converted_transport_diesel_consumption_per_hp, t_when_all_diesel_transport_gasified\
    , is_all_diesel_production_gasified
  if is_initial_delay_over == False:
    return_value = unconverted_transport_diesel_consumption_per_hp * diesel_transport_capacity_hp
    if initial_delay < t:
      is_initial_delay_over = True
    else:
      is_initial_delay_over = False
  elif is_all_diesel_transport_gasified == False:
    return_value = \
      unconverted_transport_diesel_consumption_per_hp * (diesel_transport_capacity_hp - rate_of_gasification * (t - initial_delay)) + \
      converted_transport_diesel_consumption_per_hp * (rate_of_gasification * (t - initial_delay))
    if diesel_transport_capacity_hp < rate_of_gasification * (t - initial_delay):
      is_all_diesel_transport_gasified = True
      t_when_all_diesel_transport_gasified = t
  elif is_all_diesel_transport_gasified == True:
    return_value = converted_transport_diesel_consumption_per_hp * diesel_transport_capacity_hp
  else:
    raise RuntimeError("Else statement has been reached in instantaneous_diesel_transport_consumption which is not expected")
  return return_value

def instantaneous_diesel_production_consumption(t):
  global is_all_diesel_transport_gasified, unconverted_production_diesel_consumption_per_hp, diesel_production_capacity_hp, is_all_diesel_production_gasified\
    , rate_of_gasification, t_when_all_diesel_transport_gasified, converted_production_diesel_consumption_per_hp, t_when_all_diesel_production_gasified
  if is_all_diesel_transport_gasified == False:
    return_value = unconverted_production_diesel_consumption_per_hp * diesel_production_capacity_hp
  elif is_all_diesel_transport_gasified == True and is_all_diesel_production_gasified == False:
    return_value = \
      unconverted_production_diesel_consumption_per_hp * (diesel_production_capacity_hp - rate_of_gasification * (t - t_when_all_diesel_transport_gasified)) \
      + converted_production_diesel_consumption_per_hp * (rate_of_gasification * (t - t_when_all_diesel_transport_gasified))
    if diesel_production_capacity_hp < rate_of_gasification * (t - t_when_all_diesel_transport_gasified):
      is_all_diesel_production_gasified = True
      t_when_all_diesel_production_gasified = t
  elif is_all_diesel_production_gasified == True:
    return_value = converted_production_diesel_consumption_per_hp * diesel_production_capacity_hp
  else:
    raise RuntimeError("Else statement has been reached in instantaneous_diesel_production_consumption which is not expected")
  return return_value

def instantaneous_gasoline_production_consumption(t):
  global is_all_diesel_production_gasified, unconverted_production_gasoline_consumption_per_hp, gasoline_production_capacity_hp, is_all_gasoline_production_gasified\
    , rate_of_gasification, t_when_all_diesel_production_gasified, converted_production_gasoline_consumption_per_hp, t_when_all_gasoline_production_gasified
  if is_all_diesel_production_gasified == False:
    return_value = unconverted_production_gasoline_consumption_per_hp * gasoline_production_capacity_hp
  elif is_all_diesel_production_gasified == True and is_all_gasoline_production_gasified == False:
    return_value = \
      unconverted_production_gasoline_consumption_per_hp * (gasoline_production_capacity_hp - rate_of_gasification * (t - t_when_all_diesel_production_gasified)) \
      + converted_production_gasoline_consumption_per_hp * (rate_of_gasification * (t - t_when_all_diesel_production_gasified))
    if gasoline_production_capacity_hp < rate_of_gasification * (t - t_when_all_diesel_production_gasified):
      is_all_gasoline_production_gasified = True
      t_when_all_gasoline_production_gasified = t
  elif is_all_gasoline_production_gasified == True:
    return_value = converted_production_gasoline_consumption_per_hp * gasoline_production_capacity_hp
  else:
    raise RuntimeError("Else statement has been reached in instantaneous_gasoline_production_consumption which is not expected")
  return return_value

# Define the time axis array for the plot
last_day_of_simulation = 1500
time_axis_of_plot = []
for day in range(last_day_of_simulation + 2):
  time_axis_of_plot.append(day)

# Business as usual plot
# Setting state variables
global is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, t_when_all_diesel_transport_gasified, t_when_all_diesel_production_gasified, t_when_all_gasoline_production_gasified
is_initial_delay_over = False
is_all_diesel_transport_gasified = False
is_all_diesel_production_gasified = False
is_all_gasoline_production_gasified = False
t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
t_when_all_diesel_production_gasified = False
t_when_all_gasoline_production_gasified = False

unconverted_transport_diesel_consumption_per_hp = unconverted_transport_diesel_consumption_per_hp_mean
diesel_transport_capacity_hp = diesel_transport_capacity_hp_mean
initial_delay = initial_delay_mean
rate_of_gasification = rate_of_gasification_mean
converted_transport_diesel_consumption_per_hp = converted_transport_diesel_consumption_per_hp_mean
unconverted_production_diesel_consumption_per_hp = unconverted_production_diesel_consumption_per_hp_mean
diesel_production_capacity_hp = diesel_production_capacity_hp_mean
converted_production_diesel_consumption_per_hp = converted_production_diesel_consumption_per_hp_mean
initial_diesel_reserve = initial_diesel_reserve_mean

delta_t = 1 #plotting in one day increments
business_as_usual_simulation_output = [initial_diesel_reserve] + [0] * (last_day_of_simulation + 1)

for t in range(last_day_of_simulation):
  is_initial_delay_over = False
  diesel_reserves = \
    business_as_usual_simulation_output[t] \
    - instantaneous_diesel_transport_consumption(t) * delta_t \
    - instantaneous_diesel_production_consumption(t) * delta_t
  # gasoline_reserves = \
  #   simulation_output[-1][2] \
  #   - instantaneous_gasoline_production_consumption(t) * delta_t
  # no_gasification_diesel_reserves = \
  #   simulation_output[-1][3] \
  #   - unconverted_transport_diesel_consumption_per_hp * diesel_transport_capacity_hp\
  #   - unconverted_production_diesel_consumption_per_hp * diesel_production_capacity_hp
  # simulation_output.append([t, diesel_reserves, gasoline_reserves, no_gasification_diesel_reserves, complete_gasification_diesel_reserves, is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, f"instantaneous_diesel_transport_consumption(t): {instantaneous_diesel_transport_consumption(t)}", f"instantaneous_diesel_production_consumption(t): {instantaneous_diesel_production_consumption(t)}", f"instantaneous_gasoline_production_consumption(t): {instantaneous_gasoline_production_consumption(t)}"])
  business_as_usual_simulation_output[t + 1] = diesel_reserves

# Mean plot
unconverted_transport_diesel_consumption_per_hp = unconverted_transport_diesel_consumption_per_hp_mean
diesel_transport_capacity_hp = 0.75 * diesel_transport_capacity_hp_mean
initial_delay = initial_delay_mean
rate_of_gasification = rate_of_gasification_mean
converted_transport_diesel_consumption_per_hp = converted_transport_diesel_consumption_per_hp_mean
unconverted_production_diesel_consumption_per_hp = unconverted_production_diesel_consumption_per_hp_mean
diesel_production_capacity_hp = 0.75 * diesel_production_capacity_hp_mean
converted_production_diesel_consumption_per_hp = converted_production_diesel_consumption_per_hp_mean
initial_diesel_reserve = initial_diesel_reserve_mean

# Setting state variables
is_initial_delay_over = False
is_all_diesel_transport_gasified = False
is_all_diesel_production_gasified = False
is_all_gasoline_production_gasified = False
t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
t_when_all_diesel_production_gasified = False
t_when_all_gasoline_production_gasified = False

delta_t = 1 #plotting in one day increments
mean_simulation_output = [initial_diesel_reserve] + [0] * (last_day_of_simulation + 1)

for t in range(last_day_of_simulation):
  diesel_reserves = \
    mean_simulation_output[t] \
    - instantaneous_diesel_transport_consumption(t) * delta_t \
    - instantaneous_diesel_production_consumption(t) * delta_t
  # gasoline_reserves = \
  #   simulation_output[-1][2] \
  #   - instantaneous_gasoline_production_consumption(t) * delta_t
  # no_gasification_diesel_reserves = \
  #   simulation_output[-1][3] \
  #   - unconverted_transport_diesel_consumption_per_hp * diesel_transport_capacity_hp\
  #   - unconverted_production_diesel_consumption_per_hp * diesel_production_capacity_hp
  # simulation_output.append([t, diesel_reserves, gasoline_reserves, no_gasification_diesel_reserves, complete_gasification_diesel_reserves, is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, f"instantaneous_diesel_transport_consumption(t): {instantaneous_diesel_transport_consumption(t)}", f"instantaneous_diesel_production_consumption(t): {instantaneous_diesel_production_consumption(t)}", f"instantaneous_gasoline_production_consumption(t): {instantaneous_gasoline_production_consumption(t)}"])
  mean_simulation_output[t + 1] = diesel_reserves

# Monte Carlo uncertainty plot
simulations_output = []
for num_of_simulations in range(100):
  # print(time.time()-start_time)
  # Randomly sampling a value in the variable distribution. 
  unconverted_transport_diesel_consumption_per_hp = sample_gaussian(unconverted_transport_diesel_consumption_per_hp_mean, unconverted_transport_diesel_consumption_per_hp_uncertainty)
  diesel_transport_capacity_hp = sample_gaussian(0.75 * diesel_transport_capacity_hp_mean, 0.75 * diesel_transport_capacity_hp_uncertainty)
  initial_delay = sample_gaussian(initial_delay_mean, initial_delay_uncertainty)
  rate_of_gasification = sample_gaussian(rate_of_gasification_mean, rate_of_gasification_uncertainty)
  converted_transport_diesel_consumption_per_hp = sample_gaussian(converted_transport_diesel_consumption_per_hp_mean, converted_transport_diesel_consumption_per_hp_uncertainty)
  unconverted_production_diesel_consumption_per_hp = sample_gaussian(unconverted_production_diesel_consumption_per_hp_mean, unconverted_production_diesel_consumption_per_hp_uncertainty)
  diesel_production_capacity_hp = sample_gaussian(0.75 * diesel_production_capacity_hp_mean, 0.75 * diesel_production_capacity_hp_uncertainty)
  converted_production_diesel_consumption_per_hp = sample_gaussian(converted_production_diesel_consumption_per_hp_mean, converted_production_diesel_consumption_per_hp_uncertainty)
  initial_diesel_reserve = sample_gaussian(initial_diesel_reserve_mean, initial_diesel_reserve_uncertainty)

  # Resetting state variables
  is_initial_delay_over = False
  is_all_diesel_transport_gasified = False
  is_all_diesel_production_gasified = False
  is_all_gasoline_production_gasified = False
  t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
  t_when_all_diesel_production_gasified = False
  t_when_all_gasoline_production_gasified = False

  delta_t = 1 #plotting in one day increments
  simulation_output = [initial_diesel_reserve] + [0] * (last_day_of_simulation + 1)

  for t in range(last_day_of_simulation):
    diesel_reserves = \
      simulation_output[t] \
      - instantaneous_diesel_transport_consumption(t) * delta_t \
      - instantaneous_diesel_production_consumption(t) * delta_t
    # gasoline_reserves = \
    #   simulation_output[-1][2] \
    #   - instantaneous_gasoline_production_consumption(t) * delta_t
    # no_gasification_diesel_reserves = \
    #   simulation_output_no_gasification[t] \
    #   - unconverted_transport_diesel_consumption_per_hp * diesel_transport_capacity_hp\
    #   - unconverted_production_diesel_consumption_per_hp * diesel_production_capacity_hp
    # simulation_output.append([t, diesel_reserves, gasoline_reserves, no_gasification_diesel_reserves, complete_gasification_diesel_reserves, is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, f"instantaneous_diesel_transport_consumption(t): {instantaneous_diesel_transport_consumption(t)}", f"instantaneous_diesel_production_consumption(t): {instantaneous_diesel_production_consumption(t)}", f"instantaneous_gasoline_production_consumption(t): {instantaneous_gasoline_production_consumption(t)}"])
    simulation_output[t + 1] = diesel_reserves
  
  simulations_output.append(simulation_output)

# Monte Carlo uncertainty plot of no gasification scenario.
simulations_output_no_gasification = []
for num_of_simulations in range(100):
  # print(time.time()-start_time)
  # Randomly sampling a value in the variable distribution. 
  unconverted_transport_diesel_consumption_per_hp = sample_gaussian(unconverted_transport_diesel_consumption_per_hp_mean, unconverted_transport_diesel_consumption_per_hp_uncertainty)
  diesel_transport_capacity_hp = sample_gaussian(0.75 * diesel_transport_capacity_hp_mean, 0.75 * diesel_transport_capacity_hp_uncertainty)
  initial_delay = sample_gaussian(initial_delay_mean, initial_delay_uncertainty)
  rate_of_gasification = sample_gaussian(rate_of_gasification_mean, rate_of_gasification_uncertainty)
  converted_transport_diesel_consumption_per_hp = sample_gaussian(converted_transport_diesel_consumption_per_hp_mean, converted_transport_diesel_consumption_per_hp_uncertainty)
  unconverted_production_diesel_consumption_per_hp = sample_gaussian(unconverted_production_diesel_consumption_per_hp_mean, unconverted_production_diesel_consumption_per_hp_uncertainty)
  diesel_production_capacity_hp = sample_gaussian(0.75 * diesel_production_capacity_hp_mean, 0.75 * diesel_production_capacity_hp_uncertainty)
  converted_production_diesel_consumption_per_hp = sample_gaussian(converted_production_diesel_consumption_per_hp_mean, converted_production_diesel_consumption_per_hp_uncertainty)
  initial_diesel_reserve = sample_gaussian(initial_diesel_reserve_mean, initial_diesel_reserve_uncertainty)

  # Resetting state variables
  is_initial_delay_over = False
  is_all_diesel_transport_gasified = False
  is_all_diesel_production_gasified = False
  is_all_gasoline_production_gasified = False
  t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
  t_when_all_diesel_production_gasified = False
  t_when_all_gasoline_production_gasified = False

  delta_t = 1 #plotting in one day increments
  simulation_output_no_gasification = [initial_diesel_reserve] + [0] * (last_day_of_simulation + 1)

  for t in range(last_day_of_simulation):
    is_initial_delay_over = False
    # diesel_reserves = \
    #   simulation_output[t] \
    #   - instantaneous_diesel_transport_consumption(t) * delta_t \
    #   - instantaneous_diesel_production_consumption(t) * delta_t
    # gasoline_reserves = \
    #   simulation_output[-1][2] \
    #   - instantaneous_gasoline_production_consumption(t) * delta_t
    no_gasification_diesel_reserves = \
      simulation_output_no_gasification[t] \
      - instantaneous_diesel_transport_consumption(t) * delta_t \
      - instantaneous_diesel_production_consumption(t) * delta_t
    # simulation_output.append([t, diesel_reserves, gasoline_reserves, no_gasification_diesel_reserves, complete_gasification_diesel_reserves, is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, f"instantaneous_diesel_transport_consumption(t): {instantaneous_diesel_transport_consumption(t)}", f"instantaneous_diesel_production_consumption(t): {instantaneous_diesel_production_consumption(t)}", f"instantaneous_gasoline_production_consumption(t): {instantaneous_gasoline_production_consumption(t)}"])
    simulation_output_no_gasification[t + 1] = no_gasification_diesel_reserves
  
  simulations_output_no_gasification.append(simulation_output_no_gasification)

lower_bound_10_percent_plot_data = []
upper_bound_90_percent_plot_data = []
lower_bound_25_percent_plot_data = []
upper_bound_75_percent_plot_data = []

simulation_data_by_day = [list(row) for row in zip(*simulations_output)]
for day_number in range(len(simulation_data_by_day)):
  lower_bound_10_percent_plot_data.append(mean_simulation_output[day_number] - 1.282 * statistics.stdev(simulation_data_by_day[day_number]))
  upper_bound_90_percent_plot_data.append(mean_simulation_output[day_number] + 1.282 * statistics.stdev(simulation_data_by_day[day_number]))
  lower_bound_25_percent_plot_data.append(mean_simulation_output[day_number] - 0.674 * statistics.stdev(simulation_data_by_day[day_number]))
  upper_bound_75_percent_plot_data.append(mean_simulation_output[day_number] + 0.674 * statistics.stdev(simulation_data_by_day[day_number]))

# Plotting
# Define plotting colours
color_palette = {
    "green": "#77dd77",
    "blue": "#89cff0",
    "orange": "#ffb347",
    "red": "#ff6961",
    "pink": "#ffbfd3",
    "purple": "#B19CD9"
}

# print("time_axis_of_plot")
# print(time_axis_of_plot)
# print("lower_bound_10_percent_plot_data")
# print(lower_bound_10_percent_plot_data)
# print("upper_bound_90_percent_plot_data")
# print(upper_bound_90_percent_plot_data)
# print("upper_bound_75_percent_plot_data")
# print(upper_bound_75_percent_plot_data)
# print("lower_bound_25_percent_plot_data")
# print(lower_bound_25_percent_plot_data)

plt.figure(figsize=(15, 10))

# Shading
plt.fill_between(time_axis_of_plot, lower_bound_10_percent_plot_data, upper_bound_90_percent_plot_data, color='lightblue', edgecolor='none', alpha=0.5, label='10th to 90th percentile')
plt.fill_between(time_axis_of_plot, lower_bound_25_percent_plot_data, upper_bound_75_percent_plot_data, color='blue', edgecolor='none', alpha=0.5, label='25th to 75th percentile')

# Lines
plt.plot(time_axis_of_plot, mean_simulation_output, color='navy', label="Main Scenario", linewidth=3.0)
plt.plot(time_axis_of_plot, business_as_usual_simulation_output, color='orange', label = "No Gasification", linewidth=3.0)

plt.xlabel('Days Since Global Catastrophic Infrastructure Loss (days)', fontsize=24)
plt.ylabel('Global Diesel Reserves (kg of diesel)', fontsize=24)
plt.legend(fontsize=20)
plt.grid(True)
plt.tight_layout()
plt.xlim([0, 1500])
plt.ylim([0, 2*10**11])
plt.tick_params(axis='both', which='major', labelsize=16)

# Define a custom formatter function
def custom_formatter(x, pos):
  return r'${:.2f}\times10^{{11}}$'.format(x / 10**11)

# Apply the custom formatter to the y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(custom_formatter))

plt.savefig('plot_main_scenario.tiff', dpi=500, bbox_inches='tight')

plt.show()

# print(f"initial_delay: {initial_delay}")
# print(f"t_when_all_diesel_transport_gasified: {t_when_all_diesel_transport_gasified}")
# print(f"t_when_all_diesel_production_gasified: {t_when_all_diesel_production_gasified}")

# Function to find the day diesel reserves reach 0 for a given simulation output
def find_day_reserves_run_out(simulation_output):
    for day, reserves in enumerate(simulation_output):
        if reserves <= 0:
            return day
    return -1  # Returns -1 if reserves never run out

# Calculate the day diesel reserves run out for each Monte Carlo simulation
days_reserves_run_out_mc = [find_day_reserves_run_out(simulation) for simulation in simulations_output]
# Filter out any simulations where reserves never run out
days_reserves_run_out_mc_filtered = [day for day in days_reserves_run_out_mc if day != -1]

# Calculate the day diesel reserves run out for the no gasification scenario
day_reserves_run_out_no_gas = find_day_reserves_run_out(business_as_usual_simulation_output)

# Calculate percentiles for the Monte Carlo simulations
percentile_10_mc = np.percentile(days_reserves_run_out_mc_filtered, 10)
percentile_90_mc = np.percentile(days_reserves_run_out_mc_filtered, 90)

print(f"Main Scenario - 10th Percentile: Day {percentile_10_mc}")
print(f"Main Scenario - 90th Percentile: Day {percentile_90_mc}")

# Since the no gasification scenario has only one outcome, its 10th and 90th percentiles are the same
if day_reserves_run_out_no_gas != -1:  # Ensure reserves do run out
    print(f"No Gasification Scenario - Day reserves run out: {day_reserves_run_out_no_gas}")
else:
    print("In the No Gasification Scenario, diesel reserves do not run out within the simulation period.")

# Find the day when diesel reserves cross the x-axis (reach 0 kg) for the main scenario
crossing_day = None
for day, reserves in enumerate(mean_simulation_output):
    if reserves <= 0:
        crossing_day = day
        break  # Stop iteration when reserves become zero or negative

if crossing_day is not None:
    print(f"The mean of the main scenario crosses the x-axis on Day {crossing_day}.")
else:
    print("The mean of the main scenario does not cross the x-axis within the simulation period.")

# List to store the day when reserves reach 0 kg for each simulation
days_when_diesel_reserves_run_out = []

# Iterate over each simulation output
for simulation_output in simulations_output_no_gasification:
    # Find the day when reserves first reach or dip below 0 kg
    day_when_diesel_runs_out = np.argmax(np.array(simulation_output) <= 0)
    # Append the day number to the list
    days_when_diesel_reserves_run_out.append(day_when_diesel_runs_out)

# Calculate the 10th and 90th percentile values for the day when reserves reach 0 kg
tenth_percentile = np.percentile(days_when_diesel_reserves_run_out, 10)
ninetieth_percentile = np.percentile(days_when_diesel_reserves_run_out, 90)

print("10th percentile value for diesel reserves running out with no gasification scenario:", tenth_percentile)
print("90th percentile value for diesel reserves running out with no gasification scenario:", ninetieth_percentile)
