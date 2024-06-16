from HardwareMonitor.Hardware import *  # equivalent to 'using LibreHardwareMonitor.Hardware;'
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import datetime
import matplotlib.dates as mdates

# namespace LibreHardwareMonitor.Hardware.Storage;
computer = Computer()  # settings can not be passed as constructor argument (following below)
computer.IsMotherboardEnabled = False
computer.IsControllerEnabled = False
computer.IsCpuEnabled = True
computer.IsGpuEnabled = True
computer.IsBatteryEnabled = False
computer.IsMemoryEnabled = False
computer.IsNetworkEnabled = False
computer.IsStorageEnabled = False
computer.Open()

class UpdateVisitor(IVisitor):
    __namespace__ = "TestHardwareMonitor"  # must be unique among implementations of the IVisitor interface
    def VisitComputer(self, computer: IComputer):
        computer.Traverse(self)

    def VisitHardware(self, hardware: IHardware):
        hardware.Update()
        for subHardware in hardware.SubHardware:
            subHardware.Update()

    def VisitParameter(self, parameter: IParameter): pass

    def VisitSensor(self, sensor: ISensor): pass


def get_temp() -> list[int]:    #[cpu_max_tmp, cpu_average_tmp, gpu_max_temp, gpu_average_temp]
    computer.Accept(UpdateVisitor())

    time.sleep(1)
    #                           for cpu:↓          ↓for max cpu temp <-sensor
    cpu_max_tmp = int(computer.Hardware[0].Sensors[83].Value)
    #                               for cpu:↓          ↓for average cpu temp <-sensor
    cpu_average_tmp = int(computer.Hardware[0].Sensors[84].Value)
    #                            for gpu:↓          ↓for max gpu temp <-sensor
    gpu_max_temp = int(computer.Hardware[1].Sensors[19].Value)
    #                        for gpu:↓          ↓for gpu temp <-sensor
    gpu_average_temp = int(computer.Hardware[1].Sensors[0].Value)

    returnList = [cpu_max_tmp, cpu_average_tmp, gpu_max_temp, gpu_average_temp]

    return returnList



# Example queue length
queue_len = 30

# Initialize the queues
time_queue = deque(maxlen=queue_len)
temp_queue = deque(maxlen=queue_len)
pwm_queue = deque(maxlen=queue_len)

temps = None


# Convert Unix time to datetime objects for better plotting
def convert_times(unix_times):
    return [datetime.datetime.fromtimestamp(ts) for ts in unix_times]

# Create the figure and axis
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

# Format the axes
ax1.set_xlabel('Time')
ax1.set_ylabel('CPU Temperature (°C)', color='red')
ax2.set_ylabel('GPU Temperature (°C)', color='orange')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
ax1.xaxis.set_major_locator(mdates.SecondLocator(interval=10))

# Create the data curves
temp_line, = ax1.plot([], [], color="red", label='CPU Temperature')
pwm_line, = ax2.plot([], [], color="orange", label='GPU Temperature')

def init():
    temp_line.set_data([], [])
    pwm_line.set_data([], [])
    return temp_line, pwm_line

def update(frame):
    current_time = time.time()
    temps = get_temp()
    new_temp = temps[1]
    new_pwm = temps[3]

    time_queue.append(current_time)
    temp_queue.append(new_temp)
    pwm_queue.append(new_pwm)

    times = convert_times(time_queue)
    times_num = mdates.date2num(times)

    temp_line.set_data(times_num, list(temp_queue))
    pwm_line.set_data(times_num, list(pwm_queue))

    ax1.set_xlim(times_num[0], times_num[-1])
    ax1.set_ylim(min(temp_queue) - 5, max(temp_queue) + 5)
    ax2.set_ylim(min(pwm_queue) - 20, max(pwm_queue) + 20)
    fig.autofmt_xdate()
    return temp_line, pwm_line

ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, interval=5000, cache_frame_data=False)

plt.show()