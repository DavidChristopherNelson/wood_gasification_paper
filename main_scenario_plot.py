import os
import matplotlib.pyplot as plt
import pprint
from pprint import pformat
from numbers_utils import close_numbers_file
from numbers_utils import open_numbers_file
from numbers_utils import read_cell_value

# Clear the console
os.system('clear')

# Closes all other numbers files that may be open just to ensure data is read
# from the correct file. This is probably not necessary.
for _ in range(5):
    close_numbers_file

# Open spreadsheet and read the required parameters.
open_numbers_file ("Gasification Model V3")

def main_scenario(): 
  # State variables
  global is_initial_delay_over, is_all_diesel_transport_gasified, is_all_diesel_production_gasified, is_all_gasoline_production_gasified, t_when_all_diesel_transport_gasified, t_when_all_diesel_production_gasified, t_when_all_gasoline_production_gasified
  is_initial_delay_over = False
  is_all_diesel_transport_gasified = False
  is_all_diesel_production_gasified = False
  is_all_gasoline_production_gasified = False
  t_when_all_diesel_transport_gasified = False # Note that Python allows for dynamic type setting
  t_when_all_diesel_production_gasified = False
  t_when_all_gasoline_production_gasified = False

  global unconverted_transport_diesel_consumption_per_hp, diesel_transport_capacity_hp, initial_delay, rate_of_gasification, converted_transport_diesel_consumption_per_hp
  global unconverted_production_diesel_consumption_per_hp, diesel_production_capacity_hp, converted_production_diesel_consumption_per_hp

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
  diesel_transport_capacity_hp = float(read_cell_value(
      "Food Related Fuel Consumption",
      "Variables Required For Sensitivity Plots",
      "B6"
  ))
  diesel_production_capacity_hp = float(read_cell_value(
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
  for t in range(last_day_of_simulation + 1):
    simulation_output.append([t,0])

  for t in range(last_day_of_simulation):
    diesel_reserves = \
      simulation_output[t][1] \
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
    simulation_output[t + 1][1] = diesel_reserves
  
  return simulation_output

# Run the main_scenario function
simulation_output = main_scenario()

formatted_data = pformat(simulation_output)
with open('output.txt', 'w') as file:
  file.write(formatted_data)

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
diesel_reserves = []
for data_point in simulation_output:
  time.append(data_point[0])
  diesel_reserves.append(data_point[1])

# plt.plot(time, diesel_reserves)
# plt.plot(time, no_gasification_diesel_reserves)
# plt.plot(time, gasoline_reserves)
# plt.plot(time, complete_gasification_diesel_reserves)
plt.plot(time, diesel_reserves, label="Main Scenario")

plt.xlabel('Days since HEMP Event (days)')
plt.ylabel('Global Diesel Reserves (kg of diesel)')
plt.legend()
plt.title('Global Diesel Reserves Since HEMP Event')
plt.grid(True)
plt.xlim([0, 800])
plt.ylim([0, 2*10**11])
plt.show()

# print(f"t_when_all_diesel_transport_gasified: {t_when_all_diesel_transport_gasified}")
# print(f"t_when_all_diesel_production_gasified: {t_when_all_diesel_production_gasified}")
# print(f"t_when_all_gasoline_production_gasified: {t_when_all_gasoline_production_gasified}")
