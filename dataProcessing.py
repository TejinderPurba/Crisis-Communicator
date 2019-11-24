

# Forked and modified from: https://github.com/tutRPi/Raspberry-Pi-Heartbeat-Pulse-Sensor/blob/master/pulsesensor.py

import serial, time, datetime, sys
from xbee import XBee, ZigBee
import threading, queue

class DataProcessing:
    def __init__(self, serialPort = "/dev/ttyAMA0", baudRate = 9600):
        self.BPM = 0
        self.temp = -100
        self.motion = False
        self.pulseVoltage = 0
        self.ser = serial.Serial(serialPort, baudRate)
        self.xbee = ZigBee(serial.Serial(serialPort, baudRate), escaped=False)
        self.bpmQueue
        self.tempQueue
        self.alarm

    def getXBeeValuesLoop(self):
        while not self.threadXBee.stopped:
            response = self.xbee.wait_read_frame()
            bpmVal = response.get('samples')[0].get('adc-0')
            tempVal = response.get('samples')[0].get('adc-1')
            motionVal = response.get('samples')[0].get('dio-2')         # May be wrong, have to double check

            self.bpmQueue.put(bpmVal)
            self.tempQueue.put(tempVal)
            self.motion = motionVal

    def getBPMLoop(self):
        # init variables
        rate = [0] * 10         # array to hold last 10 IBI values
        sampleCounter = 0       # used to determine pulse timing
        lastBeatTime = 0        # used to find IBI
        P = 512                 # used to find peak in pulse wave, seeded
        T = 512                 # used to find trough in pulse wave, seeded
        thresh = 525            # used to find instant moment of heart beat, seeded
        amp = 100               # used to hold amplitude of pulse waveform, seeded
        firstBeat = True        # used to seed rate array so we startup with reasonable BPM
        secondBeat = False      # used to seed rate array so we startup with reasonable BPM

        IBI = 600               # int that holds the time interval between beats! Must be seeded!
        Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat". 
        lastTime = int(time.time()*1000)
        
        while not self.threadBPM.stopped:
            Signal = self.bpmQueue.get(block=True, timeout=None)
            currentTime = int(time.time()*1000)
            self.pulseVoltage = Signal
            
            sampleCounter += currentTime - lastTime
            lastTime = currentTime
            
            N = sampleCounter - lastBeatTime

            # find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3:     # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T:                          # T is the trough
                    T = Signal                          # keep track of lowest point in pulse wave 

            if Signal > thresh and Signal > P:
                P = Signal

            # signal surges up in value every time there is a pulse
            if N > 250:                                 # avoid high frequency noise
                if Signal > thresh and Pulse == False and N > (IBI/5.0)*3:       
                    Pulse = True                        # set the Pulse flag when we think there is a pulse
                    IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
                    lastBeatTime = sampleCounter        # keep track of time for next pulse

                    if secondBeat:                      # if this is the second beat, if secondBeat == TRUE
                        secondBeat = False;             # clear secondBeat flag
                        for i in range(len(rate)):      # seed the running total to get a realisitic BPM at startup
                          rate[i] = IBI

                    if firstBeat:                       # if it's the first time we found a beat, if firstBeat == TRUE
                        firstBeat = False;              # clear firstBeat flag
                        secondBeat = True;              # set the second beat flag
                        continue

                    # keep a running total of the last 10 IBI values  
                    rate[:-1] = rate[1:]                # shift data in the rate array
                    rate[-1] = IBI                      # add the latest IBI to the rate array
                    runningTotal = sum(rate)            # add upp oldest IBI values

                    runningTotal /= len(rate)           # average the IBI values 
                    self.BPM = 60000/runningTotal       # how many beats can fit into a minute? that's BPM!

            if Signal < thresh and Pulse == True:       # when the values are going down, the beat is over
                Pulse = False                           # reset the Pulse flag so we can do it again
                amp = P - T                             # get amplitude of the pulse wave
                thresh = amp/2 + T                      # set thresh at 50% of the amplitude
                P = thresh                              # reset these for next time
                T = thresh

            if N > 4000:                                # if 4 seconds go by without a beat
                thresh = 512                            # set thresh default
                P = 512                                 # set P default
                T = 512                                 # set T default
                lastBeatTime = sampleCounter            # bring the lastBeatTime up to date        
                firstBeat = True                        # set these to avoid noise
                secondBeat = False                      # when we get the heartbeat back
                self.BPM = 0

            time.sleep(0.005)

    def getTempLoop(self):
        while not self.threadTemp.stopped:
            Signal = self.tempQueue.get(block=True, timeout=None)
            # put in code for analog to celsius formula if using TMP35
            # else put in code for one-wire DS18B20 (see if SunFounder does the library stuff automatically)

    # Not currently in use. Overtaken by pin 13 on XBee (nOn_Sleep)
    def soundAlarm(self):
        self.xbee.remote_at(dest_addr=b'\x1d\x14', command='D3', parameter=b'\x05')
        self.xbee.remote_at(dest_addr=b'\x1d\x14', command='WR')

    # Not currently in use. Overtaken by pin 13 on XBee (nOn_Sleep)
    def silenceAlarm(self):
        self.xbee.remote_at(dest_addr=b'\x1d\x14', command='D3', parameter=b'\x04')
        self.xbee.remote_at(dest_addr=b'\x1d\x14', command='WR')

    # Start getXBeeValuesLoop routine which saves the XBee values in their variables
    def startAsyncXBee(self):
        self.threadXBee = threading.Thread(target=self.getXBeeValuesLoop)
        self.threadXBee.stopped = False
        self.threadXBee.start()
        return
        
    # Stop the BPM routine
    def stopAsyncXBee(self):
        self.threadXBee.stopped = True
        self.bpmQueue.clear()
        self.tempQueue.clear()
        self.alarm = False
        self.ser.close()
        return

    # Start getBPMLoop routine which saves the BPM in its variable
    def startAsyncBPM(self):
        self.threadBPM = threading.Thread(target=self.getBPMLoop)
        self.threadBPM.stopped = False
        self.threadBPM.start()
        return
        
    # Stop the BPM routine
    def stopAsyncBPM(self):
        self.threadBPM.stopped = True
        self.BPM = 0
        self.voltage = 0
        return

    # Start getTempLoop routine which saves the temp in its variable
    def startAsyncTemp(self):
        self.threadTemp = threading.Thread(target=self.getTempLoop)
        self.threadTemp.stopped = False
        self.threadTemp.start()
        return
        
    # Stop the temp routine
    def stopAsyncTemp(self):
        self.threadTemp.stopped = True
        self.temp = -100
        return
    
