import serial as ser
import time 
import numpy as np
import matplotlib.pyplot as plt
import sysid_pem_toolbox as sid


def signal_to_mag_and_dir(signal_to_convert):
    N = signal_to_convert.shape[0]
    signal_magnitude = np.empty(N,dtype='B')
    signal_direction = np.empty(N,dtype='B')
    for ii in range(N):
        if np.abs(signal_to_convert[ii]) > 255:
            signal_magnitude[ii] = 255
        else:
            signal_magnitude[ii] = np.round(np.abs(signal_to_convert[ii]))
    
        if signal_to_convert[ii] >= 0:
            signal_direction[ii] = 1
        else:
            signal_direction[ii] = 0
    return signal_magnitude, signal_direction

def run_cart_pendulum(reference_magnitude,reference_direction,com_port):
    num_tries_setup_comms = 100
    N = 1000
    #reference_magnitude = np.concatenate( (np.zeros(250,dtype='B'), 50*np.ones(250,dtype='B')) )
    #reference_direction = np.zeros(N,dtype='B')

    cart_position = np.empty(N,dtype=int)
    pendulum_position = np.empty(N,dtype=int)
    tt = np.empty(N,dtype=int)



    arduino = ser.Serial(port=com_port, baudrate=9600, timeout=0.1)
    arduino.reset_input_buffer()
    arduino.reset_output_buffer() 
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    time.sleep(1)
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    msg = [[0]]
    for ii in range(num_tries_setup_comms):
        m1 = arduino.readline()
        #print('Received message:', m1)
        if m1 == b'Completed Setup.\r\n':
            arduino.write(bytes('c', 'utf-8')) 
            print('Arduino completed setup.')
            time.sleep(0.1)
            msg = arduino.readlines()
            break
    if chr(msg[-1][0]) == 'c':
        print('Computer and Arduino communicating and ready.')
    else:
        print('Computer and Arduino not communicating properly.')
        print('Exiting.')
        arduino.close()
        return -1


    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    print('Sending data to Arduino.')
    for ii in range(N):
        arduino.write(reference_magnitude[ii].tobytes()) 
        check = arduino.read()
        #print(check)
        if len(check) == 0:
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1
        #print('sent: ', reference_magnitude[ii], 'received: ', check, ' (', check[0], ')')
        if reference_magnitude[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1

    for ii in range(N):
        arduino.write(reference_direction[ii].tobytes()) 
        check = arduino.read()
        if len(check) == 0:    
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1   
        #print('sent: ', reference_direction[ii], 'received: ', check, ' (', check[0], ')')
        if reference_direction[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1




    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    data_received_flag = False
    while not data_received_flag:
        msg = arduino.readline()
        #print('message: ', msg)
        if isinstance(msg, bytes):
            if msg == b'Sending data.\r\n':
                data_received_flag = True
        time.sleep(0.1)   


    tt1 = time.time()
    print('Receiving Data from Arduino.')
    for ii in range(N):
        msg = arduino.read(2)
        tt2 = time.time()
        dt = tt2-tt1
        tt1 = tt2 
        #print(dt, ' ', msg, ' (', int.from_bytes(msg,'little',signed=True), ')') 
        cart_position[ii] = int.from_bytes(msg,'little',signed=True)

    for ii in range(N):
        msg = arduino.read(2)
        tt2 = time.time()
        dt = tt2-tt1
        tt1 = tt2 
        #print(dt, ' ', msg, ' (', int.from_bytes(msg,'little',signed=True), ')') 
        pendulum_position[ii] = int.from_bytes(msg,'little',signed=True)

    for ii in range(N):
        msg = arduino.read(2)
        tt2 = time.time()
        dt = tt2-tt1
        tt1 = tt2 
        #print(dt, ' ', msg, ' (', int.from_bytes(msg,'little',signed=True), ')') 
        tt[ii] = int.from_bytes(msg,'little',signed=True)


    arduino.close()
    return cart_position, pendulum_position, tt


def run_motor_and_disk(reference_magnitude,reference_direction,com_port):
    num_tries_setup_comms = 100
    N = 1000
    #reference_magnitude = np.concatenate( (np.zeros(250,dtype='B'), 50*np.ones(250,dtype='B')) )
    #reference_direction = np.zeros(N,dtype='B')

    disk_position = np.empty(N,dtype=int)
    tt = np.empty(N,dtype=int)

    print('Setting up Python and Arduino.')


    arduino = ser.Serial(port=com_port, baudrate=9600, timeout=0.1)
    arduino.reset_input_buffer()
    arduino.reset_output_buffer() 
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    time.sleep(1)
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    msg = [[0]]
    for ii in range(num_tries_setup_comms):
        m1 = arduino.readline()
        #print('Received message:', m1)
        if m1 == b'Completed Setup.\r\n':
            arduino.write(bytes('c', 'utf-8')) 
            print('Arduino completed setup.')
            time.sleep(0.1)
            msg = arduino.readlines()
            break
    if chr(msg[-1][0]) == 'c':
        print('Computer and Arduino communicating and ready.')
    else:
        print('Computer and Arduino not communicating properly.')
        print('Exiting.')
        arduino.close()
        return -1


    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    print('Sending data to Arduino.')
    for ii in range(N):
        arduino.write(reference_magnitude[ii].tobytes()) 
        check = arduino.read()
        #print(check)
        if len(check) == 0:
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1
        #print('sent: ', reference_magnitude[ii], 'received: ', check, ' (', check[0], ')')
        if reference_magnitude[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1

    for ii in range(N):
        arduino.write(reference_direction[ii].tobytes()) 
        check = arduino.read()
        if len(check) == 0:    
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1   
        #print('sent: ', reference_direction[ii], 'received: ', check, ' (', check[0], ')')
        if reference_direction[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1

    print('Simulation is running.')


    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    data_received_flag = False
    while not data_received_flag:
        msg = arduino.readline()
        #print('message: ', msg)
        if isinstance(msg, bytes):
            if msg == b'Sending data.\r\n':
                data_received_flag = True
        time.sleep(0.1)   

    print('Simulation has ended. Retrieving data.')

    tt1 = time.time()
    print('Receiving Data from Arduino.')
    for ii in range(N):
        msg = arduino.read(2)
        tt2 = time.time()
        dt = tt2-tt1
        tt1 = tt2 
        #print(dt, ' ', msg, ' (', int.from_bytes(msg,'little',signed=True), ')') 
        disk_position[ii] = int.from_bytes(msg,'little',signed=True)

    for ii in range(N):
        msg = arduino.read(2)
        tt2 = time.time()
        dt = tt2-tt1
        tt1 = tt2 
        #print(dt, ' ', msg, ' (', int.from_bytes(msg,'little',signed=True), ')') 
        tt[ii] = int.from_bytes(msg,'little',signed=True)


    arduino.close()

    print('Completed.')
    
    return disk_position, tt


def run_motor_and_disk_open_loop_streaming(reference_magnitude,reference_direction,com_port,num_bytes_per_int=2):

    # To run this function, "one_encoder_motor_coms_v2.ino" needs to be loaded onto the Arduino.

    num_tries_setup_comms = 100
    N = 1000
    #reference_magnitude = np.concatenate( (np.zeros(250,dtype='B'), 50*np.ones(250,dtype='B')) )
    #reference_direction = np.zeros(N,dtype='B')

    disk_position1 = np.empty(N,dtype=int)   
    tt = np.empty(N,dtype=int)

    arduino = ser.Serial(port=com_port, baudrate=115200, timeout=0.1)
    arduino.reset_input_buffer()
    arduino.reset_output_buffer() 
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    time.sleep(1)
    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    msg = [[0]]
    for ii in range(num_tries_setup_comms):
        m1 = arduino.readline()
        #print('Received message:', m1)
        if m1 == b'Completed Setup.\r\n':
            arduino.write(bytes('c', 'utf-8')) 
            print('Arduino completed setup.')
            time.sleep(0.1)
            msg = arduino.readlines()
            break
    if chr(msg[-1][0]) == 'c':
        print('Computer and Arduino communicating and ready.')
    else:
        print('Computer and Arduino not communicating properly.')
        print('Exiting.')
        arduino.close()
        return -1


    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    print('Sending data to Arduino.')
    for ii in range(N):
        arduino.write(reference_magnitude[ii].tobytes()) 
        check = arduino.read()
        #print(check)
        if len(check) == 0:
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1
        #print('sent: ', reference_magnitude[ii], 'received: ', check, ' (', check[0], ')')
        if reference_magnitude[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1

    for ii in range(N):
        arduino.write(reference_direction[ii].tobytes()) 
        check = arduino.read()
        if len(check) == 0:    
            print('No reply received. Most likely array size mismatch in Arduino and Python.')
            arduino.close()
            return -1   
        #print('sent: ', reference_direction[ii], 'received: ', check, ' (', check[0], ')')
        if reference_direction[ii] != check[0]:
            print('Error sending data to Arduino. Exiting.')
            arduino.close()
            return -1

    print('Simulation is running.')


    #print('Input Buffer length:', arduino.in_waiting)
    #print('Output buffer length:', arduino.out_waiting)

    num_data_received = 0
    while num_data_received < N:
        if arduino.in_waiting >= 2*num_bytes_per_int:
            msg = arduino.read(num_bytes_per_int)
            disk_position1[num_data_received] = int.from_bytes(msg,'little',signed=True)          
            msg = arduino.read(num_bytes_per_int)                        
            tt[num_data_received] = int.from_bytes(msg,'little',signed=True)

            #print(num_data_received, ':', disk_position1[num_data_received], ',', tt[num_data_received])
            num_data_received += 1

    print('Simulation has ended.')

    arduino.close()
    return disk_position1, tt




def fit_transfer_function_to_frequency_response(n,G,omega):

    na = n[0]
    nb = n[1]
    nf = omega.shape[0]

    # Construct regression matrix
    phi = np.zeros((nf,na+nb), dtype = complex)
    for ii in range(nb):
        for jj in range(nf):
            phi[jj,ii] = (1j * omega[jj])**(ii)

    for ii in range(na):
        for jj in range(nf):
            phi[jj,ii+nb] = - (1j * omega[jj])**(ii) * G[jj]

    # Construct to be predicted output
    b = np.zeros((nf,1), dtype = complex)
    for ii in range(nf):
        b[ii] = G[ii] * (1j * omega[ii])**(na)

    # split between real and imaginary parts to force only real theta
    phi_stack = np.concatenate((np.real(phi), np.imag(phi)))
    b_stack = np.concatenate((np.real(b), np.imag(b)))

    # do linear regression
    theta = np.linalg.inv(phi_stack.T @ phi_stack) @ (phi_stack.T @ b_stack)

    return theta




    

