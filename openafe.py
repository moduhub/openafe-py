import serial

class OpenAFE:

	def __init__(self, comPort, onPointCallback=None, onEndCallback=None):
		"""
		NOTE: This method can raise an Exception.

		The above code defines a Python class with an initialization method that establishes a serial
		connection and sets optional callback functions.
		
		:param comPort: The comPort parameter is the serial port to which the OpenAFE device is connected.
		It is used to establish a connection with the device
		:param onPointCallback: The onPointCallback parameter is a function that will be called whenever a
		data point is received from the OpenAFE device. This function can be used to process or display the
		received data point
		:param onEndCallback: The `onEndCallback` parameter is a callback function that will be called when
		the communication with the OpenAFE device ends. It is an optional parameter, so if you don't provide
		a callback function, it will default to `None`
		"""
		try:
			self.onPointCallback = onPointCallback
			self.onEndCallback = onEndCallback
			
			self.ser = serial.Serial(comPort, 115200)

			messageReceived = self.waitForMessage()

			if messageReceived != "MSG,RDY" or self.isValidMessage(messageReceived):
				raise Exception("OpenAFE is not ready!")

		except serial.serialutil.SerialException:
			raise Exception("Failed to stablish connection with the OpenAFE device. CHECK IF IT IS CONNECTED!")
		except Exception as e:
			raise Exception("Could not initiate communication with the OpenAFE device. Reason: ", e)


	def waitForMessage(self):
		"""
		NOTE: This method can raise an Exception.

		The `waitForMessage` function reads a message from a serial port, checks its checksum, and returns
		the message if the checksum is valid, otherwise it returns -1.
		:return: The function `waitForMessage` returns either the message received from OpenAFE if the
		checksum is valid, or -1 if the checksum is not valid.
		"""
		try:
			rawMessage=str(self.ser.readline())
		except serial.serialutil.SerialException:
			raise Exception("Failed to read from the OpenAFE device. CHECK IF IT IS CONNECTED!")

		messageReceived = rawMessage[2:][:-3]

		checksum = messageReceived[-2:]

		# check the message's checksum ...
		calculatedChecksum = self._calculateChecksumOfString(messageReceived[1:][:-3])
		checksumInMessage = self._getChecksumIntegerFromString(checksum)

		if (calculatedChecksum - checksumInMessage) == 0:
			# checksum is valid
			message = messageReceived[1:][:-3] 
			return message
		else :
			# checksum is not valid
			raise Exception("Message from the MCU got corrupted.")


	def isValidMessage(self, message):
		"""
		NOTE: This functions does not check if the message is an error message, it checks if the message 
		received is valid, in other words, if it was not corrupted during its transmission.

		The function `isValidMessage` checks if a given message is valid by comparing it to -1.
		
		:param message: The parameter "message" is a variable that represents the message being checked for
		validity
		:return: True if the message is equal to -1, and False otherwise.
		"""
		if message == -1:
			return True
		else:
			return False


	def isErrorMessage(self, message):
		"""
		NOTE: This function only checks if the message is an error message, but not if the message received
		is valid. Invalid messages have a value of -1. 

		The function checks if a given message is an error message by checking if it begins with "ERR".
		
		:param message: The parameter "message" is a string that represents a message
		:return: a boolean value. If the message begins with "ERR", it will return True. Otherwise, it will
		return False.
		"""
		if message[:-4] == "ERR":
			return True
		else:
			return False


	def _calculateChecksumOfString(self, string):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_calculateChecksumOfString` calculates the checksum of a given string by performing a
		bitwise XOR operation on the ASCII values of its characters.
		
		:param string: The parameter "string" is a string of characters for which we want to calculate the
		checksum, e.g.: "CVW,500,-500,250,2,1".
		:return: the checksum of the given string, e.g.: 119 (0x77).
		"""
		checksum = 0
		for char in string:
			checksum = (checksum ^ ord(char))
		return checksum


	def _getChecksumIntegerFromString(self, checksumString):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_getChecksumIntegerFromString` converts a string representation of a checksum into an
		integer value.
		
		:param checksumString: The `checksumString` parameter is a string that represents a checksum, e.g.: "32".
		:return: an integer checksum value e.g.: 50 (0x32).
		"""
		integerChecksum = 0
		index = 1

		for char in checksumString:
			if ord(char) < 0x41:
				integerChecksum |= (ord(char) - 0x30) << (index * 4)
			else:
				integerChecksum |= (ord(char) - 0x37) << (index * 4)
			index -= 1

		return integerChecksum


	def sendCommandToMCU(self, command):
		"""
		NOTE: This method can raise an Exception.

		The `sendCommandToMCU` function sends a command to a microcontroller unit (MCU) by calculating a
		checksum, constructing a full command string, and writing it to a serial port.
		
		:param command: The `command` parameter is a string that represents the command to be sent to the
		MCU (Microcontroller Unit). It can be any valid command that the MCU understands. For example,
		"CVW,500,-500,250,2,1" is a command that instructs the MCU to
		"""
		try:
			checksum = self._calculateChecksumOfString(command)
			checksumString = format(checksum, '02X')
			fullCommand = "$" + command + "*" + checksumString
			# print("full command: ", fullCommand)
			self.ser.write(fullCommand.encode("utf-8"))

			commandResponse = self.waitForMessage()

			if self.isErrorMessage(commandResponse):
				raise Exception("MCU declined CV command")

		except serial.serialutil.SerialException:
			raise Exception("Failed send command to the OpenAFE device. CHECK IF IT IS CONNECTED!")
		except Exception as e:
			raise("Failed send command to the OpenAFE device. Reason: ", e)


	def setCurrentRange(self, currentRange):
		"""
		NOTE: This method can raise an Exception.

		The function sets the current range of an OpenAFE device and returns True if successful, or False if
		there was an error.
		
		:param currentRange: The currentRange parameter is the desired range of current that the OpenAFE
		device should use. It is a numerical value that represents the range in amperes
		:return: a boolean value. If the current range was set successfully, it returns True. If there was
		an error and the current range was not set, it returns False.
		"""
		try:
			self.sendCommandToMCU("CMD,CUR," + str(currentRange))
		except Exception as e:
			raise Exception("Could not chanhge the current range setting in the OpenAFE device. Reason: ", e)



	def makeCyclicVoltammetry(self, settlingTime, startingPotential, endingPotential, scanRate, stepSize, numberOfCycles):
		"""
		NOTE: This method can raise an Exception.

		The function "makeCyclicVoltammetry" sends a command string to a microcontroller unit (MCU) to
		perform cyclic voltammetry with specified parameters.
		
		:param settlingTime: The settlingTime parameter refers to the time in seconds that the system should
		wait before starting the cyclic voltammetry measurement. This allows the system to stabilize and
		reach a steady state before the measurement begins, in milliseconds (ms)
		:param endingPotential: The ending potential is the final voltage value at which the cyclic
		voltammetry will stop. It is a floating-point number representing the voltage in volts, in millivolts (mV)
		:param startingPotential: The starting potential is the initial voltage at which the cyclic
		voltammetry experiment begins, in millivolts (mV)
		:param scanRate: The scan rate is the rate at which the potential is swept during the cyclic
		voltammetry experiment. It is usually expressed in millivolts per second (mV/s)
		:param stepSize: The step size is the increment or decrement in potential applied during each step
		of the cyclic voltammetry experiment. It determines the resolution of the measurement and can be
		positive or negative, in millivolts (mV)
		:param numberOfCycles: The numberOfCycles parameter specifies the number of cycles to perform in the
		cyclic voltammetry experiment
		"""
		CVCommandString = "CVW," + str(settlingTime) + "," + str(startingPotential) + "," + str(endingPotential) + \
		"," + str(scanRate) + "," + str(stepSize) + "," + str(numberOfCycles)
		try:
			self.sendCommandToMCU(CVCommandString) # send the CV command
		except Exception as e:
			raise Exception("Could not send the Cyclic Voltammetry to the OpenAFE device. Reason: ", e)


	def makeDifferentialPulseVoltammetry(self, settlingTime, startingPotential, endingPotential, pulsePotential, 
				      stepPotential, pulseWidth, baseWidth, samplePeriodPulse, samplePeriodBase):
		"""
		The function `makeDifferentialPulseVoltammetry` sends a command string to an OpenAFE device to
		perform a Differential Pulse Voltammetry measurement.
		
		:param settlingTime: The settling time is the duration in seconds for the system to stabilize before
		starting the measurement. It allows any transient effects to settle down and ensures accurate
		measurements
		:param startingPotential: The starting potential is the initial voltage at which the experiment
		begins. It is the potential at the beginning of the scan range
		:param endingPotential: The endingPotential parameter is the final potential value at which the
		differential pulse voltammetry will stop
		:param pulsePotential: The pulsePotential parameter refers to the potential at which the pulse is
		applied during the Differential Pulse Voltammetry (DPV) experiment
		:param stepPotential: The stepPotential parameter refers to the potential difference between each
		step in the voltage scan during the Differential Pulse Voltammetry (DPV) experiment. It determines
		the size of the voltage steps that the system will take during the scan
		:param pulseWidth: The pulseWidth parameter refers to the duration of the voltage pulse applied
		during the differential pulse voltammetry experiment. It is the time interval for which the
		potential is held at the pulsePotential value
		:param baseWidth: The baseWidth parameter refers to the width of the base potential in the
		Differential Pulse Voltammetry (DPV) technique. It represents the duration of the potential applied
		during the baseline period before the pulse potential is applied
		:param samplePeriodPulse: The samplePeriodPulse parameter refers to the time interval between each
		sample taken during the pulse phase of the Differential Pulse Voltammetry (DPV) experiment
		:param samplePeriodBase: The samplePeriodBase parameter refers to the time interval between each
		data point during the base phase of the differential pulse voltammetry experiment
		"""
		DPVCommandString = "DPV," + str(settlingTime) + "," + str(startingPotential) + "," + \
			str(endingPotential) + "," + str(pulsePotential) + "," + str(stepPotential) + "," + \
			str(pulseWidth) + "," + str(baseWidth) + "," + str(samplePeriodPulse) + "," + str(samplePeriodBase)
		try:
			self.sendCommandToMCU(DPVCommandString)
		except Exception as e:
			raise Exception("Could not send the Differential Pulse Voltammetry to the OpenAFE device. Reason: ", e)


	def makeSquareWaveVoltammetry(self, settlingTime, startingPotential, endingPotential, scanRate, pulsePotential, 
							   pulseFrequency, samplePeriodPulse):
		"""
		The function `makeSquareWaveVoltammetry` sends a command string to an OpenAFE device to perform
		Square Wave Voltammetry with specified parameters.
		
		:param settlingTime: The settling time is the duration in seconds for the system to stabilize before
		starting the measurement, in milliseconds
		:param startingPotential: The startingPotential parameter represents the initial potential at the
		beginning of the square wave voltammetry experiment, in millivolts
		:param endingPotential: The endingPotential parameter is the final potential value in the square
		wave voltammetry waveform, in millivolts
		:param scanRate: The scan rate is the rate at which the potential is swept during the voltammetry
		experiment. It is expressed in millivolts per second (mV/s)
		:param pulsePotential: The pulsePotential parameter represents the potential at which the pulse is
		applied during the Square Wave Voltammetry experiment, in millivolts
		:param pulseFrequency: The pulseFrequency parameter refers to the frequency at which the pulse
		potential is applied during the Square Wave Voltammetry experiment. It is the number of pulses per
		unit of time, in Hertz (Hz)
		:param samplePeriodPulse: When to sample the pulse, amount of ms before the pulse end, in milliseconds.
		"""

		SWVCommandString = "SWV," + str(settlingTime) + "," + str(startingPotential) + "," + \
			str(endingPotential) + "," + str(scanRate) + "," + str(pulsePotential) + "," + \
			str(pulseFrequency) + "," + str(samplePeriodPulse)
		try:
			self.sendCommandToMCU(SWVCommandString)
		except Exception as e:
			raise Exception("Could not send the Square Wave Voltammetry to the OpenAFE device. Reason: ", e)


	def receiveVoltammetryPoints(self):
		"""
		The function `receiveVoltammetryPoints` receives messages from OpenAFE, processes the received
		points, and calls the appropriate callbacks.
		"""
		while True:
			messageReceived = self.waitForMessage()
			point = messageReceived[4:]

			if messageReceived == "MSG,END":
				self._onVoltammetryEnd()
				break
			
			if messageReceived[:-4] == "ERR":
				raise Exception("An error ocurred during the voltammetry.")

			elif messageReceived != -1: # if message is valid
				pointObjs = point.split(',')

				voltage = float(pointObjs[0])
				current = float(pointObjs[1])

				self._onVoltammetryPoint(voltage, current)


	def _onVoltammetryPoint(self, voltage, current):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The `_onVoltammetryPoint` function takes in a voltage and current value and calls a callback function
		if it exists.
		
		:param voltage: The voltage value at a specific point in a voltammetry experiment
		:param current: The current parameter represents the measured electric current in the voltammetry
		experiment
		"""
		if self.onPointCallback and callable(self.onPointCallback):
			self.onPointCallback(voltage, current)


	def _onVoltammetryEnd(self):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_onVoltammetryEnd` checks if a callback function `onEndCallback` is defined and
		callable, and if so, it calls the callback function.
		"""
		if self.onEndCallback and callable(self.onEndCallback):
			self.onEndCallback()