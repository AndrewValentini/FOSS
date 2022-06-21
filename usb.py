import usb.core
import usb.util

class UsbPlot: 
    def __init__(self):
    
    
        # find our device - Vendor ST, Product STM32F4
        self.usbDev = usb.core.find(idVendor=0x0483, idProduct=0xF00D)
        if self.usbDev is None:
            raise ValueError('Device not found')
            
        # With no arguments, the first configuration will be the active one
        self.usbDev.set_configuration()
        
        # find and assign IN endpoint
        self.epIn = self.findEndpoint(usb.util.ENDPOINT_IN)


        self.datasize = 12
        self.timear = []
        self.xar = []
        self.yar = []
        self.zar = []

    def xyzFromUsb(self, usbData):
        xbytes = usbData[0              :self.datasize]
        ybytes = usbData[self.datasize  :2*self.datasize]
        zbytes = usbData[2*self.datasize:3*self.datasize]
        tbytes = usbData[3*self.datasize:(3+2)*self.datasize]
        
        payloadsize = []
        Time_Stamp = []
        Pkt_Counter = []
        Type = []
        Version = []
        Sync = []
        
        # Byte arrays to integers, time is uint16
        for i in range(self.datasize):
            x.append(self.accel_byte2g(xbytes[i]))
            y.append(self.accel_byte2g(ybytes[i]))
            z.append(self.accel_byte2g(zbytes[i]))
            
            t_tmp = int.from_bytes(tbytes[2*i:2*i+2], byteorder='little', signed=False)
            t.append(t_tmp/1000 + self.timeOverflow) # seconds
        
        return x,y,z,t # little endian transmission



    def animate(self, i):
        
        # Read USB    
        timeout = 50
        try:
            usbData = self.usbDev.read(self.epIn.bEndpointAddress, 5*self.datasize, timeout)
        except usb.core.USBError as e:
            print('Data not read:', e)
            return
            
        xbuf,ybuf,zbuf,tMcu = self.xyzFromUsb(usbData)





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