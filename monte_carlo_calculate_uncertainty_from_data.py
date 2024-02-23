import os
import matplotlib.pyplot as plt
import pprint
import statistics
import time
import json
from pprint import pprint
from numbers_utils import close_numbers_file
from numbers_utils import open_numbers_file
from numbers_utils import read_cell_value
from numbers_utils import write_to_cell_in_numbers
from sample_gaussian import sample_gaussian

# Clear the console
os.system('clear')
start_time = time.time()
print(time.time() - start_time)

# Closes all other numbers files that may be open just to ensure data is read
# from the correct file. This is probably not necessary.
for _ in range(5):
  close_numbers_file

# Open spreadsheet and read the required parameters.
open_numbers_file ("Gasification Model V3")

with open('monte_carlo_samples.txt', 'r') as file:
  file_content = file.read()

file_data_blocks = file_content.split('\n\n')
output_cell_data = json.loads(file_data_blocks[0])
if len(file_data_blocks) > 1:
  samples = []
  for block in file_data_blocks[1:]:
    if not block.strip(): continue
    samples.append([float(num) for num in json.loads(block)])
else:
  print("No sample data in text file")

# Transpose read_simulation_outputs
samples_organised_by_output = [list(row) for row in zip(*samples)]

# Calculate the output's uncertainty 
if len(samples_organised_by_output) != len(output_cell_data):
  print("Some sample number data is not allocated to output cells. This is unexpected and an error.")

for output_cell_number in range(len(samples_organised_by_output)):
  write_to_cell_in_numbers(
    output_cell_data[output_cell_number]["sheet"], 
    output_cell_data[output_cell_number]["table"], 
    output_cell_data[output_cell_number]["uncertainty_cell_location"],
    1.282 * statistics.stdev(samples_organised_by_output[output_cell_number])
  )
