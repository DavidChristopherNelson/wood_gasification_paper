import numpy as np

def sample_gaussian(mean, percentile_90):
  mean = float(mean)
  percentile_90 = float(percentile_90)

  # Convert 90th percentile deviation to standard deviation
  sigma = percentile_90 / 1.28

  if sigma < 0:
    print("Error: sigma < 0")
    print(f"mean: {mean}")
    print(f"percentile_90: {percentile_90}")
    print(f"sigma: {sigma}")

  # Draw a sample from the Gaussian distribution
  return np.random.normal(mean, sigma)

# Example usage
# mean = 50  # Replace with your mean
# percentile_90_deviation = 10  # Replace with your 90th percentile deviation
# sample = sample_gaussian(mean, percentile_90_deviation)
# #print(sample)
