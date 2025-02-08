# Adjust the parameters below according to your needs:
# 
# NOTE: Keep in mind that some voltammetry waves may not be 
# generated by the AFE, those will return an error.
# 
# Comment or de-comment the voltammetry type as needed.

# COM port:
COM_PORT = "COM14" # The COM port to which the Arduino is connected

# Parameters:
voltammetryType = "CV" # Cyclic Voltammetry
# voltammetryType = "DPV" # Differential Pulse Voltammetry
# voltammetryType = "SW" # Square Wave

startingPotential_millivolts = -500
endingPotential_millivolts = 500
scanRate_millivoltsPerSecond = 200
stepSize_millivolts = 5
numberOfCycles = 2
settlingTime_milliseconds = 1000

pulsePotential_millivolts = 100
pulseWidth_milliseconds = 2
baseWidth_milliseconds = 20
samplePeriodPulse_milliseconds = 1
samplePeriodBase_milliseconds = 2

pulseFrequency_hertz = 10

currentRange_microamps = 200	

# Graph Options:
graphTitle = "H2O + NaCl Cyclic Voltammetry" # the graph title to be displayed, can be left in blank
graphSubTitle = "" # the graph sub title, can be left blank
gridVisible = True # Change to True or False, to make the grid visible or hidden, respectively


import matplotlib.pyplot as plt
from collections import deque
from openafe import OpenAFE

def plotPoints(queVoltage, queCurrent):
    """
    Plots the voltammetry points, changing color based on the cycle and whether the voltage is increasing or decreasing.
    
    :param queVoltage: List of voltage values to plot on the x-axis.
    :param queCurrent: List of current values to plot on the y-axis.
    """

    plt.clf()
    plt.suptitle(graphTitle)
    plt.title(graphSubTitle)
    plt.xlabel('Voltage (mV)')
    plt.ylabel('Current (uA)')
    plt.grid(visible=gridVisible)

    # Define colors for each cycle
    cycle_colors = [
        ("blue", "red"),    # Cycle 1: (ascending, descending)
        ("green", "purple"),  # Cycle 2: (ascending, descending)
        ("orange", "cyan"),  # Cycle 3: (ascending, descending)
        ("black", "magenta")  # Cycle 4: (ascending, descending)
    ]

    # Identificar os pontos onde os ciclos começam
    cycleBoundaries = [0]  # O primeiro ciclo sempre começa no índice 0
    for i in range(1, len(queVoltage) - 1):
        # Detecta o início de um novo ciclo (quando a tensão retorna ao ponto inicial)
        if queVoltage[i - 1] > queVoltage[i] and queVoltage[i] <= startingPotential_millivolts:
            cycleBoundaries.append(i)

    numCycles = len(cycleBoundaries)

    if numCycles > len(cycle_colors):
        print(f"Warning: More cycles detected ({numCycles}) than colors available. Colors will repeat.")

    # Criar lista para a legenda
    legend_handles = []  # Lista para armazenar os identificadores das linhas na legenda
    legend_labels = []   # Lista para armazenar os nomes dos ciclos na legenda

    # Plotando os segmentos com cores de acordo com o ciclo correto
    cycleIndex = 0
    for i in range(1, len(queVoltage)):
        # Verifica se entramos em um novo ciclo
        if cycleIndex < len(cycleBoundaries) - 1 and i >= cycleBoundaries[cycleIndex + 1]:
            cycleIndex += 1  # Avança para o próximo ciclo

        # Seleciona as cores corretas do ciclo atual
        ascending_color, descending_color = cycle_colors[cycleIndex % len(cycle_colors)]

        # Determina a cor com base na variação de tensão
        color = ascending_color if queVoltage[i] > queVoltage[i - 1] else descending_color

        # Plota o segmento e adiciona à legenda apenas uma vez por ciclo
        line, = plt.plot([queVoltage[i - 1], queVoltage[i]], [queCurrent[i - 1], queCurrent[i]], color=color)

        if color == ascending_color and f"Ciclo {cycleIndex+1} - Subida" not in legend_labels:
            legend_handles.append(line)
            legend_labels.append(f"Ciclo {cycleIndex+1} - Subida")

        elif color == descending_color and f"Ciclo {cycleIndex+1} - Descida" not in legend_labels:
            legend_handles.append(line)
            legend_labels.append(f"Ciclo {cycleIndex+1} - Descida")

    # Configuração dos limites do eixo X
    plt.xlim(startingPotential_millivolts - 100, endingPotential_millivolts + 100)

    # Adicionar legenda ao gráfico
    plt.legend(legend_handles, legend_labels, loc="upper right")

    # Atualiza o gráfico
    plt.draw()
    plt.pause(0.05)
    
# ***** ***** ***** Callbacks ***** ***** *****
def onVoltammetryPoint(voltage, current):
	"""
	The function `onVoltammetryPoint` appends voltage and current values to two queues and plots the
	points every 20 data points.
	
	:param voltage: The voltage value at a specific point in the voltammetry experiment
	:param current: The current parameter represents the current value measured during a voltammetry
	experiment
	"""
	queVoltage.append(voltage)
	queCurrent.append(current)

	if len(queVoltage) % 5 == 0: 
		plotPoints(queVoltage, queCurrent)


def onVoltammetryEnd():
	"""
	The function `onVoltammetryEnd` plots the voltage and current points and displays a message indicating
	that the voltammetry is finished.
	"""
	plotPoints(queVoltage, queCurrent)
	print("INFO: Voltammetry finished!") 
	plt.show()


# ***** ***** ***** MAIN ***** ***** *****:

# MAX NO. OF POINTS TO STORE
queVoltage = deque(maxlen = 10000)
queCurrent = deque(maxlen = 10000)

try:
	openAFE_device = OpenAFE(COM_PORT, onVoltammetryPoint, onVoltammetryEnd)

	openAFE_device.setCurrentRange(currentRange_microamps)

	if voltammetryType == "CV":
		openAFE_device.makeCyclicVoltammetry(settlingTime_milliseconds, startingPotential_millivolts, endingPotential_millivolts, \
			scanRate_millivoltsPerSecond, stepSize_millivolts, numberOfCycles)

	elif voltammetryType == "DPV":
		openAFE_device.makeDifferentialPulseVoltammetry(settlingTime_milliseconds, startingPotential_millivolts, 
							endingPotential_millivolts, pulsePotential_millivolts, stepSize_millivolts,
							pulseWidth_milliseconds, baseWidth_milliseconds, samplePeriodPulse_milliseconds, 
							samplePeriodBase_milliseconds)

	elif voltammetryType == "SW":
		openAFE_device.makeSquareWaveVoltammetry(settlingTime_milliseconds, startingPotential_millivolts, 
										   endingPotential_millivolts, scanRate_millivoltsPerSecond, 
										   pulsePotential_millivolts, pulseFrequency_hertz, samplePeriodPulse_milliseconds)

	openAFE_device.receiveVoltammetryPoints()

except Exception as exception:
	print(exception)