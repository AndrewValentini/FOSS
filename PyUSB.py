import usb.core
import usb.util
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class usbLivePlot: 
    def __init__(self):


        # finding the device
        self.usbDev = usb.core.find(idVendor=0x000, idProduct=0x0000)
        if self.usbDev is None:
            raise ValueError('Device not found')
            
        # With no arguments, the first configuration will be the active one
        self.usbDev.set_configuration()
        
        # find and assign IN endpoint
        self.epIn = self.findEndpoint(usb.util.ENDPOINT_IN)



        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot
        self.startTime = time.time()





        #Cretaing Buffers
        self.datasize = 43
        self.payloadsize_array = []
        self.TimeStamp_array = []
        self.PktCounter_array = []
        self.Type_array = []
        self.Version_array = []
        self.Sync_array = []
        self.SensorStatus_array = []
        self.DATA_array = []

    def bytesFromusb(self, usbData):
        payloadsize_bytes = usbData[ 0 : 3 ]
        TimeStamp_bytes = usbData[ 4 : 7 ]
        PktCounter_bytes = usbData[ 8 : 9 ]
        Type_bytes = usbData[ 10 : 10 ]
        Version_bytes = usbData[ 11 : 11 ]
        Sync_bytes = usbData[ 12 : 15 ]
        SensorStatus_bytes = usbData[ 17 : 19 ]
        DATA_bytes = usbData[ 20 : 43 ]

        
        payloadsize = []
        TimeStamp = []
        PktCounter = []
        Type = []
        Version = []
        Sync = []
        SensorStatus = []
        DATA = []

        
        # Converting Byte arrays to integers, time is uint16 (this is not needed)
        for i in range(self.datasize):
            payloadsize.append(self.accel_byte2g(payloadsize_bytes[i]))
            #TimeStamp.append(self.accel_byte2g(TimeStamp_bytes[i]))
            PktCounter.append(self.accel_byte2g(PktCounter_bytes[i]))
            Type.append(self.accel_byte2g(Type_bytes[i]))
            Version.append(self.accel_byte2g(Version_bytes[i]))
            Sync.append(self.accel_byte2g(Sync_bytes[i]))
            SensorStatus.append(self.accel_byte2g(SensorStatus_bytes[i]))
            DATA.append(self.accel_byte2g(DATA_bytes[i]))


            
            t_gator = int.from_bytes(TimeStamp_bytes[i], byteorder='little', signed=False)
            TimeStamp.append(t_gator/1000000) # converting microseconds to seconds because data from Gator is collected in the former
        
        return payloadsize, PktCounter, Type, Version, Sync, SensorStatus, DATA, TimeStamp # little endian (LSB) transmission



    def animate(self, i):
        
        # Reading the USB    
        timeout = 50
        try:
            usbData = self.usbDev.read(self.epIn.bEndpointAddress, 5*self.datasize, timeout)
        except usb.core.usbError as e:
            print('Data not read:', e)
            return
            
        payloadsize_buf,TimeStamp_buf,PktCounter_buf, Type_buf, Version_buf, Sync_buf, SensorStatus_buf, DATA_buf, tMcu = self.bytesFromUsb(usbData)


        #self.timear.extend(tMcu)
        self.payloadsize_array.extend(payloadsize_buf)
        self.TimeStamp_array.extend(TimeStamp_buf)
        self.PktCounter_array.extend(PktCounter_buf)
        self.Type_array.extend(Type_buf)
        self.Version_array.extend(Version_buf)
        self.Sync_array.extend(Sync_buf)
        self.SensorStatus_array.extend(SensorStatus_buf)
        self.DATA_array.extend(DATA_buf)


        self.ax1.clear()
        self.ax1.plot(self.TimeStamp_array, self.DATA_array, marker = '.', linestyle = None)
        self.ax1.set_title("Strain from Gator Versus Time")
        self.ax1.set_xlabel("Time [s]")
        self.ax1.set_ylabel("Strain from Gator [?]") 
        

    def findEndpoint(self, direction):
        cfg = self.usbDev.get_active_configuration()
        intf = cfg[(0,0)]

        ep = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                direction)

        assert ep is not None
        print(ep)
        return ep
    def main(): 

        usbLive = usbLivePlot()
        usbLive.filename = "strain.log"

        #Creating a self-animating plot
        ani = animation.FuncAnimation(usbLive.fig, usbLive.animate, interval = 30)
        plt.show()

    if __name__ == "__main__":
        main()

        