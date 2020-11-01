
import time
import pigpio

# sipeed 6+1 mic array MSM261S4030H0 driver

class ClockGen(object):

    # Use Hardware PWM to generate clock for MIC_BCK pin
    def __init__(self, pi, clk_pin):
        self.pi = pi
        self.clk_pin = clk_pin

    def set_mode(self, hz, duty):
        # Set clk pin as Hardware PWM
        self.pi.set_mode(self.clk_pin, pigpio.OUTPUT)
        # Set clk pin with given clock and duty ratio based 1MHz(=1000000)
        self.pi.hardware_PWM(self.clk_pin, hz, int(duty*1000000))
### end ###

class MSMmic(object):

    # MSM261S4030H0 driver

    def __init__(self, pi, ch):
        self.pi = pi
        self.channel = ch
        self.read_size = 24 # 24bits per 32clk?
        self.baud = 16000*16#(16000*16/24)*64
        self.flags = 256 # Choose set auxiliary SPI
        self.handler = self.pi.spi_open(self.channel, self.baud, self.flags)

    def read(self):
        # Specify read byte
        c, d = self.pi.spi_read(self.handler, self.read_size//8)
        return c, d

    def cleanup(self):
        self.pi.spi_close(self.handler)


### main ###

if __name__ == "__main__":

    pi = pigpio.pi()

    if not pi.connected:
        print('exit')
        exit(0)

    # Causion!! You need to specify pins as BCM-provided-pin assignment, not a header
    # Use GPIO18(header12) for HardwarePWM
    MIC_BCK = ClockGen(pi, clk_pin=18)
    # Use GPIO19(header35) for MIC_WS word select signal
    MIC_WS = ClockGen(pi, clk_pin=13)

    MIC_BCK.set_mode(hz=64*24*16000, duty=0.5)
    MIC_WS.set_mode(hz=24*16000, duty=0.5)

    MSM1 = MSMmic(pi, 0)
    MSM2 = MSMmic(pi, 1)
    MSM3 = MSMmic(pi, 2)
    mic_array = [MSM1, MSM2, MSM3]

    try:
        while True:
            for i, mic in enumerate(mic_array):
                c, d = mic.read()
                print("mic{}, c:{}, d:{}".format(i, c,d))

    except KeyboardInterrupt:
        print("\nCtr+c")
    
    except Exception as e:
        print(str(e))
    
    finally:
        for mic in mic_array:
            mic.cleanup()

        print("Cleanup")

###end###
