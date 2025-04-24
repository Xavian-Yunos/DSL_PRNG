import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns
from sklearn.preprocessing import PowerTransformer

# ---- Serial Configuration ----
PORT = 'COM9'  # Change to your serial port
BAUDRATE = 9600

# ---- Open Serial Port ----
ser = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# ---- Data Collection ----
timeset = 30    # change timeset to collect data in seconds
print(f"Collecting serial data for {timeset/60} min...")
data = []
start_time = time.time()

while time.time() - start_time < timeset:
    if ser.in_waiting >= 2:
        raw_bytes = ser.read(2)
        if len(raw_bytes) == 2:
            high_byte = raw_bytes[0]
            low_byte = raw_bytes[1]
            value = (high_byte << 8) | low_byte
            data.append(value)

ser.close()
# Convert to numpy array
data = np.array(data).reshape(-1, 1)
data = np.array(data).flatten()  # Flatten reshaped data
window_size = 50

# ---- Apply Central Limit Theorem (Rolling Average of Uniform Data) ----
window_size = 50  # Using higher values approximates closer to Gaussian
rolling_avg = np.convolve(data, np.ones(window_size)/window_size, mode='valid') # mean of window size values
transformed_data = rolling_avg  # Use this for analysis

# ---- Histogram with Normal Curve Overlay ----
plt.figure(figsize=(10, 6))
sns.histplot(data, bins=100, kde=True, stat="density", color="skyblue", label="Data")

# Fit a normal distribution and overlay
mu, std = np.mean(data), np.std(data)
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = stats.norm.pdf(x, mu, std)
plt.plot(x, p, 'r', label='Normal Distribution Fit')
plt.title("Histogram with Normal Distribution Fit")
plt.xlabel("16-bit Value")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.show()

# ---- Q-Q Plot ----
plt.figure(figsize=(6, 6))
stats.probplot(data, dist="norm", plot=plt)
plt.title("Q-Q Plot")
plt.grid(True)
plt.show()

# ---- Histogram ----
plt.figure(figsize=(10, 6))
sns.histplot(transformed_data, bins=100, kde=True, stat="density", color="skyblue", label="CLT Smoothed Data")

mu, std = np.mean(transformed_data), np.std(transformed_data)
x = np.linspace(mu - 4*std, mu + 4*std, 100)
p = stats.norm.pdf(x, mu, std)
plt.plot(x, p, 'r', label='Gaussian Fit')
plt.title("Histogram of CLT-Transformed Data")
plt.xlabel("Value")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.show()

# ---- Q-Q Plot ----
plt.figure(figsize=(6, 6))
stats.probplot(transformed_data, dist="norm", plot=plt)
plt.title("Q-Q Plot (CLT Transformed)")
plt.grid(True)
plt.show()