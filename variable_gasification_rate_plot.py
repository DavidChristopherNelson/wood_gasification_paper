import os
import matplotlib.pyplot as plt
import pprint
from pprint import pformat
from numbers_utils import close_numbers_file
from numbers_utils import open_numbers_file
from numbers_utils import read_cell_value
from matplotlib.ticker import FuncFormatter

# Clear the console
os.system('clear')

# Closes all other numbers files that may be open just to ensure data is read
# from the correct file. This is probably not necessary.
for _ in range(5):
    close_numbers_file

# Open spreadsheet and read the required parameters.
open_numbers_file ("Gasification Model V3")

initial_delay = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B2"
))
initial_diesel_reserve = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B3"
))
initial_gasoline_reserve = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B4"
))
rate_of_gasification = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B5"
))
diesel_transport_capacity_hp = 0.75 * float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B6"
))
diesel_production_capacity_hp = 0.75 * float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B7"
))
gasoline_production_capacity_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B8"
))
unconverted_transport_diesel_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B9"
))
converted_transport_diesel_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B10"
))
unconverted_production_diesel_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B11"
))
converted_production_diesel_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B12"
))
unconverted_production_gasoline_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B13"
))
converted_production_gasoline_consumption_per_hp = float(read_cell_value(
    "Food Related Fuel Consumption",
    "Variables Required For Sensitivity Plots",
    "B14"
))

# print(f"initial_delay: {initial_delay}")
# print(f"initial_diesel_reserve: {initial_diesel_reserve}")
# print(f"initial_gasoline_reserve: {initial_gasoline_reserve}")
# print(f"rate_of_gasification: {rate_of_gasification}")
# print(f"diesel_transport_capacity_hp: {diesel_transport_capacity_hp}")
# print(f"diesel_production_capacity_hp: {diesel_production_capacity_hp}")
# print(f"gasoline_production_capacity_hp: {gasoline_production_capacity_hp}")
# print(f"unconverted_transport_diesel_consumption_per_hp: {unconverted_transport_diesel_consumption_per_hp}")
# print(f"converted_transport_diesel_consumption_per_hp: {converted_transport_diesel_consumption_per_hp}")
# print(f"unconverted_production_diesel_consumption_per_hp: {unconverted_production_diesel_consumption_per_hp}")
# print(f"converted_production_diesel_consumption_per_hp: {converted_production_diesel_consumption_per_hp}")
# print(f"unconverted_production_gasoline_consumption_per_hp: {unconverted_production_gasoline_consumption_per_hp}")
# print(f"converted_production_gasoline_consumption_per_hp: {converted_production_gasoline_consumption_per_hp}")

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
    is_initial_delay_over = True if initial_delay < t else False
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


simulation_output = [[0, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve, initial_diesel_reserve]]
delta_t = 1 #plotting in one day increments
last_day_of_simulation = 1000
sensitivity_variable_array = [
  0, 
  0.25 * rate_of_gasification, 
  0.5 * rate_of_gasification, 
  0.75 * rate_of_gasification, 
  rate_of_gasification, 
  1.25 * rate_of_gasification,
  1.5 * rate_of_gasification,
  1.75 * rate_of_gasification,
  2 * rate_of_gasification]

for t in range(last_day_of_simulation + 1):
  simulation_output.append([t,0,0,0,0,0,0,0,0,0])
for index in range(len(sensitivity_variable_array)):
  rate_of_gasification = sensitivity_variable_array[index]
  # State variables
  is_initial_delay_over = False
  is_all_diesel_transport_gasified = False
  is_all_diesel_production_gasified = False
  is_all_gasoline_production_gasified = False
  t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
  t_when_all_diesel_production_gasified = False
  t_when_all_gasoline_production_gasified = False
  for t in range(last_day_of_simulation):
    diesel_reserves = \
      simulation_output[t][index + 1] \
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
    simulation_output[t + 1][index + 1] = diesel_reserves


formatted_data = pformat(simulation_output)
with open('output.txt', 'w') as file:
    file.write(formatted_data)

# Define plotting colours
color_palette = {
    "green": "#77dd77",
    "blue": "#89cff0",
    "orange": "#ffb347",
    "red": "#ff6961",
    "pink": "#ffbfd3",
    "purple": "#B19CD9"
}

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

# time = []
# diesel_reserves = []
# gasoline_reserves = []
# no_gasification_diesel_reserves = []
# complete_gasification_diesel_reserves = []
# for data_point in simulation_output:
#   time.append(data_point[0])
#   diesel_reserves.append(data_point[1])
#   gasoline_reserves.append(data_point[2])
#   no_gasification_diesel_reserves.append(data_point[3])
#   complete_gasification_diesel_reserves.append(data_point[4])

time = []
diesel_reserves_delay_1 = []
diesel_reserves_delay_2 = []
diesel_reserves_delay_3 = []
diesel_reserves_delay_4 = []
diesel_reserves_delay_5 = []
diesel_reserves_delay_6 = []
diesel_reserves_delay_7 = []
diesel_reserves_delay_8 = []
diesel_reserves_delay_9 = []
for data_point in simulation_output:
  time.append(data_point[0])
  diesel_reserves_delay_1.append(data_point[1])
  diesel_reserves_delay_2.append(data_point[2])
  diesel_reserves_delay_3.append(data_point[3])
  diesel_reserves_delay_4.append(data_point[4])
  diesel_reserves_delay_5.append(data_point[5])
  diesel_reserves_delay_6.append(data_point[6])
  diesel_reserves_delay_7.append(data_point[7])
  diesel_reserves_delay_8.append(data_point[8])
  diesel_reserves_delay_9.append(data_point[9])

plt.figure(figsize=(15, 10))
# plt.plot(time, diesel_reserves)
# plt.plot(time, no_gasification_diesel_reserves)
# plt.plot(time, gasoline_reserves)
# plt.plot(time, complete_gasification_diesel_reserves)
plt.plot(time, diesel_reserves_delay_1, label="No Gasifiers Installed", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_2, label="25% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_3, label="50% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_4, label="75% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_5, label="Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_6, label="125% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_7, label="150% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_8, label="175% of Swedish Gasification Rate", linewidth=3.0)
plt.plot(time, diesel_reserves_delay_9, label="200% of Swedish Gasification Rate", linewidth=3.0)

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

plt.savefig('plot_variable_gasification_rate.tiff', dpi=500, bbox_inches='tight')

plt.show()

# print(f"t_when_all_diesel_transport_gasified: {t_when_all_diesel_transport_gasified}")
# print(f"t_when_all_diesel_production_gasified: {t_when_all_diesel_production_gasified}")
# print(f"t_when_all_gasoline_production_gasified: {t_when_all_gasoline_production_gasified}")
