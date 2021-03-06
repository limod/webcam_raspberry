#!/usr/bin/env python
import time
import os
import RPIO
import RPIO.PWM



PWM_FREQUENCY = 50    # Hz
PWM_SUBCYLCLE_TIME_US = 1000/PWM_FREQUENCY * 1000
PWM_PULSE_INCREMENT_US = 10
PWM_DMA_CHANNEL = 0



ABSOLUTE_MIN_PULSE_WIDTH_US = 500
ABSOLUTE_MAX_PULSE_WIDTH_US = 2500

EXPLORE_PAN_START_ANGLE = 45.0;
EXPLORE_PAN_END_ANGLE = 135.0;
EXPLORE_TILT_START_ANGLE = 130.0;
EXPLORE_TILT_END_ANGLE = 50.0;

EXPLORE_ABS_PAN_STEP = 1;
EXPLORE_ABS_TILT_STEP = 5;

#-------------------------------------------------------------------------------
class ServoPWM:
    
    #---------------------------------------------------------------------------
    def __init__( self, pwmPin, minAnglePulseWidthPair, 
        midAnglePulseWidthPair, maxAnglePulseWidthPair ):
        
        # Check that the given angles are valid
        assert( minAnglePulseWidthPair[ 0 ] >= 0 )
        assert( midAnglePulseWidthPair[ 0 ] > minAnglePulseWidthPair[ 0 ] )
        assert( midAnglePulseWidthPair[ 0 ] < maxAnglePulseWidthPair[ 0 ] )
        assert( maxAnglePulseWidthPair[ 0 ] <= 180 )
        
        self.pwmPin = pwmPin
        self.minAnglePulseWidthPair = minAnglePulseWidthPair
        self.midAnglePulseWidthPair = midAnglePulseWidthPair
        self.maxAnglePulseWidthPair = maxAnglePulseWidthPair
        self.lastPulseWidthSet = None
    
    #---------------------------------------------------------------------------
    def setCommand( self, command ):
        
        # Work out whether the command is an angle, or a pulse width
        if command >= ABSOLUTE_MIN_PULSE_WIDTH_US:
            self.setPulseWidth( command )
        else:
            self.setAngle( command )
    
    #---------------------------------------------------------------------------
    def setPulseWidth( self, pulseWidth ):
        
        # Constrain the pulse width
        if pulseWidth < ABSOLUTE_MIN_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MIN_PULSE_WIDTH_US
        if pulseWidth > ABSOLUTE_MAX_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MAX_PULSE_WIDTH_US
        
        # Ensure that the pulse width is an integer multiple of the smallest 
        # possible pulse increment
        pulseIncrementUS = RPIO.PWM.get_pulse_incr_us()
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS
    
        if pulseWidth != self.lastPulseWidthSet:
            RPIO.PWM.add_channel_pulse( PWM_DMA_CHANNEL, self.pwmPin, 0, numPulsesNeeded)
            self.lastPulseWidthSet = pulseWidth
    
    #---------------------------------------------------------------------------
    def setAngle( self, angle ):
        
        # Constrain the angle
        if angle < self.minAnglePulseWidthPair[ 0 ]:
            angle = self.minAnglePulseWidthPair[ 0 ]
        if angle > self.maxAnglePulseWidthPair[ 0 ]:
            angle = self.maxAnglePulseWidthPair[ 0 ]
            
        # Convert the angle to a pulse width using linear interpolation
        if angle < self.midAnglePulseWidthPair[ 0 ]:
            
            angleDiff = self.midAnglePulseWidthPair[ 0 ] - self.minAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.minAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.midAnglePulseWidthPair[ 1 ] - self.minAnglePulseWidthPair[ 1 ]
            
            interpolation = float( angle - self.minAnglePulseWidthPair[ 0 ] ) / angleDiff
            
            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff
            
        else:
            
            angleDiff = self.maxAnglePulseWidthPair[ 0 ] - self.midAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.midAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.maxAnglePulseWidthPair[ 1 ] - self.midAnglePulseWidthPair[ 1 ]
            
            interpolation = float( angle - self.midAnglePulseWidthPair[ 0 ] ) / angleDiff
            
            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff
        
        print "Converted angle {0} to pulse width {1}".format( angle, pulseWidth )
        
        # Now set the pulse width
        self.setPulseWidth( pulseWidth )

