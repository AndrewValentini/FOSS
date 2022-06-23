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
            #DATA.append(int.from_bytes(DATA_bytes[i]))

            global DATA_g
            data_gator = int.from_bytes(TimeStamp_bytes[i], byteorder ='little', signed = False)
            DATA_g = TimeStamp.append(data_gator)
            t_gator = int.from_bytes(TimeStamp_bytes[i], byteorder='little', signed=False)
            # converting microseconds to seconds because data from Gator is collected in the former
            global TIME
            TIME = TimeStamp.append(t_gator/1000000)
        
        return payloadsize, PktCounter, Type, Version, Sync, SensorStatus, DATA, TimeStamp # little endian (LSB) transmission

     

    #-----------------What should go in place of DATA? I would like this to be where the FBGs pick up the changes over time--------Enter FBG_1, FBG_2, etc here
    with open("FOSS.data", 'w', newline = '', sep = ',') as file:

        writer_object = csv.writer(file)
        writer_object.writerow(['FBG_sensor1', 'FBG_sensor2', 'FBG_sensor3', 'FBG_sensor4'])
        
        for i in range(int(TIME),int(TIME)+5): 
            writer_object.writerow([DATA_g, DATA_g, DATA_g, DATA_g])

    
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



#-----------I feel like this part is important..You're adding the buffer data to the array set created. Isn't this needed regardless of if you create an animation?-
        #self.payloadsize_array.extend(payloadsize_buf)
        #self.TimeStamp_array.extend(TimeStamp_buf)
        #self.PktCounter_array.extend(PktCounter_buf)
        #self.Type_array.extend(Type_buf)
        #self.Version_array.extend(Version_buf)
        #self.Sync_array.extend(Sync_buf)
        #self.SensorStatus_array.extend(SensorStatus_buf)
        #self.DATA_array.extend(DATA_buf)

    