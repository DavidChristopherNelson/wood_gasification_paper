import os
import time
import threading
import json
from pprint import pformat
from numbers_utils import close_numbers_file
from numbers_utils import open_numbers_file
from numbers_utils import read_cell_value
from numbers_utils import write_to_cell_in_numbers
from sample_gaussian import sample_gaussian

# Clear the console and set the timer
os.system('clear')
start_time = time.time()
print(time.time() - start_time)

# Closes all other numbers files that may be open just to ensure data is read
# from the correct file. This is probably not necessary.
for _ in range(5):
    close_numbers_file

# Open spreadsheet and read the required parameters.
open_numbers_file ("Gasification Model V3")

# Identify the cells that contain parameters
parameter_cell_groups = [
    {
        "sheet": "Parameters",
        "table": "Parameters", 
        "cell_start_column": "C",
        "cell_end_column": "C",
        "cell_start_row": 2,
        "cell_end_row": 77
    },
    {
        "sheet": "Parameters",
        "table": "WW2 Gasifier Ramp Up", 
        "cell_start_column": "D",
        "cell_end_column": "D",
        "cell_start_row": 2,
        "cell_end_row": 12
    },
    {
        "sheet": "Parameters",
        "table": "WW2 Gasifier Ramp Up",
        "cell_start_column": "F",
        "cell_end_column": "F",
        "cell_start_row": 2,
        "cell_end_row": 12
    },
    {
        "sheet": "Parameters",
        "table": "WW2 Gasifier Ramp Up",
        "cell_start_column": "H",
        "cell_end_column": "H",
        "cell_start_row": 2,
        "cell_end_row": 12
    }
  ]

# Create an array of parameter cells and populate it with data
parameter_cells = []
for cell_group in parameter_cell_groups:
  sheet = cell_group["sheet"]
  table = cell_group["table"]
  cell_start_column = cell_group["cell_start_column"]
  cell_end_column = cell_group["cell_end_column"]
  cell_start_row = cell_group["cell_start_row"]
  cell_end_row = cell_group["cell_end_row"]
  for column in range(ord(cell_start_column), ord(cell_end_column) + 1):
    for row in range(cell_start_row, cell_end_row + 1):
      parameter_cells.append({
        "sheet":sheet,
        "table":table, 
        "value_cell_location": f"{chr(column)}{row}",
        "uncertainty_cell_location": f"{chr(column + 1)}{row}", # This assumes the uncertainty is always located in the cell to the right of where the value is stored. 
        "name_cell_location": f"{chr(column - 2)}{row}"
      })
      parameter_cells[-1]["name"] = read_cell_value(
        parameter_cells[-1]["sheet"], 
        parameter_cells[-1]["table"], 
        parameter_cells[-1]["name_cell_location"]
      )
      parameter_cells[-1]["value"] = read_cell_value(
        parameter_cells[-1]["sheet"], 
        parameter_cells[-1]["table"], 
        parameter_cells[-1]["value_cell_location"]
      )
      uncertainty = read_cell_value(
        parameter_cells[-1]["sheet"], 
        parameter_cells[-1]["table"], 
        parameter_cells[-1]["uncertainty_cell_location"]
      )
      if uncertainty == "missing value":
          uncertainty = 0
      parameter_cells[-1]["uncertainty"] = uncertainty

# Identify the cells that contain the model outputs
output_cell_groups = [
  {
    "sheet": "WW2 Gasifier Ramp Up",
    "table": "WW2 Gasifier Ramp Up Scaled by Horsepower", 
    "cell_start_column": "C",
    "cell_end_column": "C",
    "cell_start_row": 2,
    "cell_end_row": 12
  },
  {
    "sheet": "WW2 Gasifier Ramp Up",
    "table": "Linear Regression Variables", 
    "cell_start_column": "B",
    "cell_end_column": "B",
    "cell_start_row": 2,
    "cell_end_row": 3
  },
  {
    "sheet": "Food Related Fuel Consumption",
    "table": "Food Production Fuel Consumption Calculations", 
    "cell_start_column": "B",
    "cell_end_column": "B",
    "cell_start_row": 2,
    "cell_end_row": 12
  },
  {
    "sheet": "Food Related Fuel Consumption",
    "table": "Food Transportation Fuel Consumption Calculations", 
    "cell_start_column": "B",
    "cell_end_column": "B",
    "cell_start_row": 2,
    "cell_end_row": 14
  },
  {
    "sheet": "Food Related Fuel Consumption",
    "table": "Initial Liquid Fuel Stockpiles", 
    "cell_start_column": "B",
    "cell_end_column": "B",
    "cell_start_row": 2,
    "cell_end_row": 7
  },
  {
    "sheet": "Food Related Fuel Consumption",
    "table": "Variables Required For Sensitivity Plots", 
    "cell_start_column": "B",
    "cell_end_column": "B",
    "cell_start_row": 2,
    "cell_end_row": 14
  }
]

output_cells = []
for cell_group in output_cell_groups:
  sheet = cell_group["sheet"]
  table = cell_group["table"]
  cell_start_column = cell_group["cell_start_column"]
  cell_end_column = cell_group["cell_end_column"]
  cell_start_row = cell_group["cell_start_row"]
  cell_end_row = cell_group["cell_end_row"]
  for column in range(ord(cell_start_column), ord(cell_end_column) + 1):
    for row in range(cell_start_row, cell_end_row + 1):
      output_cells.append({
        "sheet":sheet,
        "table":table,
        "value_cell_location": f"{chr(column)}{row}",
        "uncertainty_cell_location": f"{chr(column + 1)}{row}",
        "name_cell_location": f"{chr(column - 1)}{row}",
        "sample_data_points": []
      })

# Multi-threading code
exit_flag = False

def check_exit():
  global exit_flag
  input("Press Enter to stop the loop. The current loop iteration needs to finish (approx 40s) before ending the cycle so please be patient.\n")
  exit_flag = True

# Monte Carlo Error Propagation
with open('monte_carlo_samples.txt', 'a') as file:
  # This writes data about the output cells. This only needs to be done once at the top of the text file. 
  # data_string = json.dumps(output_cells)
  # file.write(data_string)
  # file.write("\n\n")

  threading.Thread(target=check_exit).start()
  
  iteration_number = 0
  while not exit_flag:
    iteration_number += 1
    print("------------ Processing iteration number " + str(iteration_number) + " now ------------")
    print(time.time() - start_time)
    for parameter_cell in parameter_cells:
      mean = parameter_cell["value"]
      percentile_90 = parameter_cell["uncertainty"]
      write_to_cell_in_numbers(
        parameter_cell["sheet"], 
        parameter_cell["table"], 
        parameter_cell["value_cell_location"],
        sample_gaussian(mean, percentile_90)
      )
    time.sleep(0.5)
    simulation_output = []
    for output_cell in output_cells:
      simulation_output.append(read_cell_value(
        output_cell["sheet"], 
        output_cell["table"], 
        output_cell["value_cell_location"]
      ))
    formatted_data = json.dumps(simulation_output)
    file.write(formatted_data)
    file.write("\n\n")  # Writing two newlines to separate each entry
    file.flush()

# Write original parameter values in the spreadsheet
print("Writing original parameter values back into the spreadsheet.")
print("This typically takes about 70 seconds. Please do not force close the program.")
for parameter_cell in parameter_cells:
  write_to_cell_in_numbers(
    parameter_cell["sheet"], 
    parameter_cell["table"], 
    parameter_cell["value_cell_location"], 
    parameter_cell["value"]
  )

print("Program is complete.")
print(time.time() - start_time)
