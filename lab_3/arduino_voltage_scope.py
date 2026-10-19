import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import serial as ser
import sys
import time


# Some constants that you need to change
com_port = 'COM9'  # Enter your com port number here
Kp = 300  # proportional gain
Ki = 5 # Integral gain
open_or_closed_loop = 1 # enter 0 for open loop, 1 for closed loop
u = 170 # for open loop, specify input step magnitude number between 0 to 255. 


def read_voltage_sensor(arduino,num_bytes_per_int=2,num_bytes_per_float=4):
    num_data_received = 0
    while num_data_received < 1:
        #tt1 = time.time()
        num_bytes_in_buffer= arduino.in_waiting
        #print('buffer length:', num_bytes_in_buffer)
        if num_bytes_in_buffer >= 2*num_bytes_per_int:
            jj = 0
            n = int(num_bytes_in_buffer/num_bytes_per_int/2)
            voltage_reading = np.empty(n)
            dt_reading = np.empty(n)
            while num_bytes_in_buffer >= 2*num_bytes_per_int:
                msg = arduino.read(2)  
                #arr = np.array(msg) 
                #voltage_reading = arr.view(dtype=np.float32)    
            
                #msg = arduino.read(num_bytes_per_int)
                voltage_reading_int = int.from_bytes(msg,'little',signed=True)
                voltage_reading[n-1-jj] = voltage_reading_int/100
                
                msg = arduino.read(2)  
                dt_reading[n-1-jj] = int.from_bytes(msg,'little',signed=True)
                #print('msg:', msg, 'jj:', jj, 'voltage:', voltage_reading[n-1-jj], 'dt:', dt_reading[n-1-jj])
                num_data_received += 1
                jj+=1
                num_bytes_in_buffer -= 4
    return voltage_reading, dt_reading

def retrieve_voltage_samples(ii, arduino, voltage, N, line):

    # Read temperature (Celsius) from TMP102
    new_voltage_samples, new_time_samples = read_voltage_sensor(arduino)
    #print(new_samples)
    #print(new_sample)
    # Add y to list
    num_new_samples = new_voltage_samples.shape[0]
    voltage[0:N-num_new_samples] = voltage[num_new_samples:N]
    voltage[N-num_new_samples:N] = new_voltage_samples

    # Update line with new Y values
    line.set_ydata(voltage)

    return line,



def write_float(arduino,F):
    F_32 = np.array([F],dtype='float32')
    arduino.write(F_32.tobytes()) 
    check1 = arduino.read(4)
    check2 = arduino.readline()
    arr = np.array(check1)
    check1_float = arr.view(dtype=np.float32)
    #print('Sent:', F_32, ' as ', F_32.tobytes(), '. Received: ', check1, ' which equals ', check1_float, ', and ', check2)
    if len(check2) == 0:
        print('No reply received. Most likely array size mismatch in Arduino and Python.')
        arduino.close()
        return -1    
    #if F_32 != np.float32(check2.decode("utf-8")):
    if F_32 != check1_float:
        print('Error sending data to Arduino. Exiting.')
        arduino.close()
        return -1
    
    return 0


def write_int(arduino,I):
    I_16 = np.array([I],dtype='int16')
    arduino.write(I_16.tobytes()) 
    check1 = arduino.read(2)
    arr = np.array(check1)
    check1_int = arr.view(dtype=np.int16)
    #print('Sent:', I_16[0], ' as ', I_16.tobytes(), '. Received: ', check1, 'which equals', check1_int) 
    if I_16[0] != check1_int:
        print('Error sending int to Arduino. Exiting.')
        arduino.close()
        return -1
    
    return 0






num_tries_setup_comms = 100
N = 1000
    #reference_magnitude = np.concatenate( (np.zeros(250,dtype='B'), 50*np.ones(250,dtype='B')) )
    #reference_direction = np.zeros(N,dtype='B')


voltage = np.zeros((N),dtype='float32')
tt = np.empty(N,dtype=int)


y_range = [0, 25]  # Range of possible Y values to display

    # Create figure for plotting
fig,ax = plt.subplots()

t = np.linspace(0,10,N)

ax.set_ylim(y_range)
ax.set_xlim([0,10])


    # Create a blank line. We will update the line in animate
line, = ax.plot(t, voltage)

    # Add labels
plt.title('Output Voltage of Boost Converter')
plt.xlabel('Samples')
plt.ylabel('Voltage (V)')

arduino = ser.Serial(port=com_port, baudrate=115200, timeout=0.1)
arduino.reset_input_buffer()
arduino.reset_output_buffer() 
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)
mm = arduino.readlines()
#time.sleep(5)
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)
#print(mm)
msg = ''
for ii in range(num_tries_setup_comms):
    m1 = arduino.readline()
    #print('m1:', m1)
        #print('Received message:', m1)
    if m1 == b'Completed Setup.\r\n':
        arduino.write(bytes('c', 'utf-8')) 
        print('Arduino completed setup.')
        #time.sleep(0.1)
        msg = arduino.readline()
        print('message:', msg)
        break

if msg == b'c\r\n':
    print('Computer and Arduino communicating and ready.')
else:
    print('Computer and Arduino not communicating properly.')
    print('Exiting.')
    arduino.close()
    sys.exit(-1)
    #time.sleep(5)
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

flag = write_float(arduino,Kp)
if flag == -1:
    arduino.close()
    sys.exit(-1)

flag = write_float(arduino,Ki)
if flag == -1:
    arduino.close()
    sys.exit(-1)

flag = write_int(arduino,open_or_closed_loop)
if flag == -1:
    arduino.close()
    sys.exit(-1)

if open_or_closed_loop == 0:
    flag = write_float(arduino,u)
    if flag == -1:
        arduino.close()
        sys.exit(-1)


ani = animation.FuncAnimation(fig,
retrieve_voltage_samples,
fargs=(arduino,voltage,N,line),
interval=10,
blit=True)
plt.show()

arduino.write(bytes('x', 'utf-8')) 
print('Exiting.')      
arduino.close()
