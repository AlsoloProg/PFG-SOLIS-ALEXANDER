import machine
from machine import Pin
import utime
import sys
import select
import _thread

pin = Pin("LED", Pin.OUT)
poll_obj = select.poll()
poll_obj.register(sys.stdin,1)

# Encoder pins
clk_pin_ra = 21
dt_pin_ra = 20

clk_pin_dec = 3
dt_pin_dec = 2

# Configurar pines como entradas con resistencia pull-up
clk_pin_ra_pu = Pin(clk_pin_ra, Pin.IN, Pin.PULL_UP)
dt_pin_ra_pu = Pin(dt_pin_ra, Pin.IN, Pin.PULL_UP)

clk_pin_dec_pu = Pin(clk_pin_dec, Pin.IN, Pin.PULL_UP)
dt_pin_dec_pu = Pin(dt_pin_dec, Pin.IN, Pin.PULL_UP)

# Motor ra pins
pin_a = Pin(16, Pin.OUT)
pin_b = Pin(17, Pin.OUT)
pin_c = Pin(18, Pin.OUT)
pin_d = Pin(19, Pin.OUT)

# Motor dec pins
pin_e = Pin(4, Pin.OUT)
pin_f = Pin(5, Pin.OUT)
pin_g = Pin(6, Pin.OUT)
pin_h = Pin(7, Pin.OUT)

# Motor configuration for spin
rotate_steps_acw = [[0,0,1,1],[0,1,1,0],[1,1,0,0],[1,0,0,1]]
rotate_steps_cw = [[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]

# Funcion para encoder declinacion
last_clk_state_ra = 0
last_dt_state_ra = 0
last_clk_state_dec = 0
last_dt_state_dec = 0
dec_encoder_count = 0
ra_encoder_count = 0

def read_encoders():
    global last_clk_state_ra, last_dt_state_ra, ra_encoder_count
    global last_clk_state_dec, last_dt_state_dec, dec_encoder_count
    while True:
        print("DEC: ", dec_encoder_count/2, "| RA: ", ra_encoder_count/2)
        clk_state_dec= clk_pin_dec_pu.value()
        dt_state_dec = dt_pin_dec_pu.value()

        if clk_state_dec != last_clk_state_dec or dt_state_dec != last_dt_state_dec:
            if clk_state_dec != last_clk_state_dec:
                if dt_state_dec != clk_state_dec:
                    dec_encoder_count += 1
                else:
                    dec_encoder_count -= 1
            last_clk_state_dec = clk_state_dec
            last_dt_state_dec = dt_state_dec
            
        clk_state_ra= clk_pin_ra_pu.value()
        dt_state_ra = dt_pin_ra_pu.value()

        if clk_state_ra != last_clk_state_ra or dt_state_ra != last_dt_state_ra:
            if clk_state_ra != last_clk_state_ra:
                if dt_state_ra != clk_state_ra:
                    ra_encoder_count += 1
                else:
                    ra_encoder_count -= 1
            last_clk_state_ra = clk_state_ra
            last_dt_state_ra = dt_state_ra
        utime.sleep_ms(2)


# Blink LED on start
pin.value(1)
utime.sleep(0.5)
pin.value(0)
utime.sleep(0.5)
dec_count = 0
ra_count = 0
time_counter = 0
first_char = ''
thread_started = 0
while True:
    if poll_obj.poll(0):
        if thread_started == 0:
            _thread.start_new_thread(read_encoders, ())
            thread_started = 1
        read = sys.stdin.readline().strip()
        print("Input: ", read) 
        dec_count = int(float(read.split('b',2)[0])*2)
        ra_count = int(float(read.split('b',2)[1])*2)
        manual_move = int(float(read.split('b',2)[2]))
        
        while manual_move == 1:
            read = sys.stdin.readline().strip()
            manual_move = int(float(read.split('b',2)[2]))
            for step in rotate_steps_acw:
                    pin_a.value(step[0])
                    pin_b.value(step[1])
                    pin_c.value(step[2])
                    pin_d.value(step[3])
                    utime.sleep_ms(5)
        
        while manual_move == 2:
            read = sys.stdin.readline().strip()
            manual_move = int(float(read.split('b',2)[2]))
            for step in rotate_steps_acw:
                    pin_e.value(step[0])
                    pin_f.value(step[1])
                    pin_g.value(step[2])
                    pin_h.value(step[3])
                    utime.sleep_ms(5)
        
        while manual_move == 3:
            read = sys.stdin.readline().strip()
            manual_move = int(float(read.split('b',2)[2]))
            for step in rotate_steps_cw:
                    pin_a.value(step[0])
                    pin_b.value(step[1])
                    pin_c.value(step[2])
                    pin_d.value(step[3])
                    utime.sleep_ms(5)
                    
        while manual_move == 4:
            read = sys.stdin.readline().strip()
            manual_move = int(float(read.split('b',2)[2]))
            for step in rotate_steps_cw:
                    pin_e.value(step[0])
                    pin_f.value(step[1])
                    pin_g.value(step[2])
                    pin_h.value(step[3])
                    utime.sleep_ms(5)
        
        while manual_move == 5:
            read = sys.stdin.readline().strip()
            manual_move = int(float(read.split('b',2)[2]))
            dec_encoder_count = 0
            ra_encoder_count = 0
            pin_e.value(0)
            pin_f.value(0)
            pin_g.value(0)
            pin_h.value(0)
                
        initial_ra = ra_count
        initial_dec = dec_count

        if dec_encoder_count > 0:
            while dec_encoder_count != 0:
                print("Ajutando posicion inicial acw...", dec_encoder_count)
                for step in rotate_steps_acw:
                    pin_e.value(step[0])
                    pin_f.value(step[1])
                    pin_g.value(step[2])
                    pin_h.value(step[3])
                    utime.sleep_ms(5)
        elif dec_encoder_count < 0:
            while dec_encoder_count != 0:
                print("Ajutando posicion inicial cw...",dec_encoder_count)
                for step in rotate_steps_cw:
                    pin_e.value(step[0])
                    pin_f.value(step[1])
                    pin_g.value(step[2])
                    pin_h.value(step[3])
                    utime.sleep_ms(5)

        if ra_encoder_count < 0:
            while ra_encoder_count != 0:
                print("Ajutando posicion inicial acw...", ra_encoder_count)
                for step in rotate_steps_acw:
                    pin_a.value(step[0])
                    pin_b.value(step[1])
                    pin_c.value(step[2])
                    pin_d.value(step[3])
                    utime.sleep_ms(5)
        elif ra_encoder_count > 0:
            while ra_encoder_count != 0:
                print("Ajutando posicion inicial cw...", ra_encoder_count)
                for step in rotate_steps_cw:
                    pin_a.value(step[0])
                    pin_b.value(step[1])
                    pin_c.value(step[2])
                    pin_d.value(step[3])
                    utime.sleep_ms(5)

        pin_a.value(0)
        pin_b.value(0)
        pin_c.value(0)
        pin_d.value(0)
        pin_e.value(0)
        pin_f.value(0)
        pin_g.value(0)
        pin_h.value(0)
        
        if dec_count != 0 and ra_count != 0:
            while abs(dec_encoder_count) < abs(dec_count):
                if initial_dec < 0:
                    for step in rotate_steps_cw:
                        pin_e.value(step[0])
                        pin_f.value(step[1])
                        pin_g.value(step[2])
                        pin_h.value(step[3])
                        utime.sleep_ms(5)
                else:
                    for step in rotate_steps_acw:
                        pin_e.value(step[0])
                        pin_f.value(step[1])
                        pin_g.value(step[2])
                        pin_h.value(step[3])
                        utime.sleep_ms(5)
                        
            dec_count = dec_encoder_count

            while abs(ra_encoder_count) < abs(ra_count):
                if initial_ra < 0:
                    for step in rotate_steps_acw:
                        pin_a.value(step[0])
                        pin_b.value(step[1])
                        pin_c.value(step[2])
                        pin_d.value(step[3])
                        utime.sleep_ms(5)
                else:
                    for step in rotate_steps_cw:
                        pin_a.value(step[0])
                        pin_b.value(step[1])
                        pin_c.value(step[2])
                        pin_d.value(step[3])
                        utime.sleep_ms(5)
                            
            ra_count = ra_encoder_count            
            print("Finished")    
            stop_check = 0
            while True:
                time_counter += 1
                old_encoder = ra_encoder_count
                print(time_counter)
                if time_counter == 120:
                    while old_encoder == ra_encoder_count:
                        print("Old: ", old_encoder, "New: ", ra_encoder_count)
                        if initial_ra < 0:
                            for step in rotate_steps_acw:
                                if old_encoder == ra_encoder_count:
                                    pin_a.value(step[0])
                                    pin_b.value(step[1])
                                    pin_c.value(step[2])
                                    pin_d.value(step[3])
                                utime.sleep_ms(5)
                        else:
                            for step in rotate_steps_cw:
                                if old_encoder == ra_encoder_count:
                                    pin_a.value(step[0])
                                    pin_b.value(step[1])
                                    pin_c.value(step[2])
                                    pin_d.value(step[3])
                    time_counter = 0
                utime.sleep_ms(1000)



