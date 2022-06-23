import usb.core
import usb.util
import csv

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

        #defining an array
        payloadsize = []
        TimeStamp = []
        PktCounter = []
        Type = []
        Version = []
        Sync = []
        SensorStatus = []
        DATA = []

        
        # Converting Byte arrays to integers, time is uint16 (this is not needed)
        #convert the gators data into something usable (as seen in the TimeStamp) <--- I think this has been completed (had to get rid of self. though; ask Caleb if this will work)
        for i in range(self.datasize):
            payloadsize.append(int.from_bytes(payloadsize_bytes[i]))
            #TimeStamp.append(self.accel_byte2g(TimeStamp_bytes[i]))
            PktCounter.append(int.from_bytes(PktCounter_bytes[i]))
            Type.append(int.from_bytes(Type_bytes[i]))
            Version.append(int.from_bytes(Version_bytes[i]))
            Sync.append(int.from_bytes(Sync_bytes[i]))
            SensorStatus.append(int.from_bytes(SensorStatus_bytes[i]))
            DATA.append(int.from_bytes(DATA_bytes[i]))

#----------------------------Is the TIME = TimeStamp.... allowed? Can I declare a varibale which is under a for i in range? ------------------------------------
            
            t_gator = int.from_bytes(TimeStamp_bytes[i], byteorder='little', signed=False)
            # converting microseconds to seconds because data from Gator is collected in the former
            TIME = TimeStamp.append(t_gator/1000000)
        
        return payloadsize, PktCounter, Type, Version, Sync, SensorStatus, DATA, TimeStamp # little endian (LSB) transmission

     

    #---------------------------What should go in place of DATA? I would like this to be where the FBGs pick up the changes over time
    with open("FOSS.data", 'w', newline = '', sep = ',') as file:

        writer_object = csv.writer(file)
        writer_object.writerow(['FBG_sensor1', 'FBG_sensor2', 'FBG_sensor3', 'FBG_sensor4'])
        
#----------------------------------------Why isn't TIME defined? I defined it above, didn't I?
        for i in range(int(TIME),int(TIME)+5): 
            writer_object.writerow(['DATA', 'DATA' 'DATA', 'DATA'])







    
#---------QUESTION--------->Is it a problem that therer exists no 'i' in  this def line? I can just get rid of it...---------
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
    