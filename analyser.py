#!/usr/bin/env python3.7

import sys, getopt
import csv
from matplotlib import pyplot as plt

def main(argv):
	# get the filename of the data file to process
	inputfile = ''
	try:
		opts, args = getopt.getopt(argv,"hi:",["ifile="])
	except getopt.GetoptError:
		print ('analyser.py -i <inputfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('analyser.py -i <inputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg.strip()

	# empty list to store the data
	data = []
	# empty lists to store data
	time = []
	displacement = []
	force = []

	# read in the data file
	with open(inputfile, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in reader:
			# check if this is a row of numbers (i.e. not of comments of headers)
			allNumbers = True
			if not row:
				continue # if there are no entries in the row, skip
			for item in row:
				try:
					float(item)
				except ValueError:
					allNumbers = False
			if allNumbers is True: # only add rows to 'data' if all entries are numeric
				data.append(row)
				time.append(float(row[0]))
				displacement.append(float(row[1]))
				force.append(float(row[2]))
	
	# Smooth data: just one (average) force measurement per displacement
	displacementSet = []
	forceSet = []
	for i in sorted(set(displacement)): # for each unique displacement value
		nValues  = 0.
		forceSum = 0.
		for j in range(0, len(force)): # gather and average all the forces at each displacement
			if displacement[j] == i:
				forceSum += force[j]
				nValues += 1
		displacementSet.append(i)
		forceSet.append(forceSum / nValues)
	
	# Can apply a moving average for further smoothing
	#forceSet = movingAverage(forceSet.copy(), 4).copy()

	# Find local minima or maxima
	print("# Local minima and maxima")
	print("Displ.\tForce")
	firstDerivatives = [0, 0]
	secondDerivative = 0
	secondDerivatives = [[], [], [], []] # displacement, second derivative, average displacement, average force
	minMaxPoints = [[], []]
	for i in range(2, len(forceSet)):
		if forceSet[i] < 0.5: # false positives in unstable region before test begins
			firstDerivatives.append(0)
			continue 
		deriv1 = forceSet[i]   -  forceSet[i-1]
		deriv2 = forceSet[i-1] -  forceSet[i-2]
		secondDerivative = deriv1 - deriv2
		firstDerivatives.append(deriv2)
		secondDerivatives[0].append(displacementSet[i-1])
		secondDerivatives[1].append(secondDerivative)
		secondDerivatives[2].append( (displacementSet[i-2] + displacementSet[i])/2 )
		secondDerivatives[3].append( (forceSet[i-2] + forceSet[i])/2 )
		if (deriv1 * deriv2) < 0:
			print(displacementSet[i-1], forceSet[i-1])
			minMaxPoints[0].append(displacementSet[i-1])
			minMaxPoints[1].append(forceSet[i-1])

	# Find linear regions (i.e. find regions where the second derivative is within
	# some threshold range from zero)
	threshold = 1.5
	linearPortion = []
	for i in range(0, len(secondDerivatives[0])):
		if abs(secondDerivatives[1][i]) < threshold:
			linearPortion.append([ secondDerivatives[2][i], secondDerivatives[3][i] ])
	
	# Find the global maximum
	global_max_y = max(forceSet)
	global_max_x = displacementSet[forceSet.index(global_max_y)]
	print("\n# Global max:\n" + str(global_max_x) + "\t" + str(global_max_y))

	# Merge together the linear regions (currently stored as individual points)
	lossyLinearRegion = []
	stepSize = 2 * abs(displacementSet[1] - displacementSet[0])
	print("stepSize: ", stepSize)
	x1, y1, x2, y2 = linearPortion[0][0], linearPortion[0][1], 0, 0
	for i in range(1, len(linearPortion)):
		if abs(linearPortion[i][0] - linearPortion[i-1][0]) > (stepSize + 0.000001): # add small value to overcome float precision problems
			x2 = linearPortion[i-1][0]
			y2 = linearPortion[i-1][1]
			lossyLinearRegion.append([ [x1, x2], [y1, y2] ])
			x1 = linearPortion[i][0]
			y1 = linearPortion[i][1]

	# Identify the longest linear region before the global maximum
	longestRange, longestRangeSet, longestRangeIndex = 0, [], 0
	for i in range(0, len(lossyLinearRegion)):
		if lossyLinearRegion[i][1][1] < global_max_y:
			if (lossyLinearRegion[i][0][1] - lossyLinearRegion[i][0][0]) > longestRange:
				longestRange = lossyLinearRegion[i][0][1] - lossyLinearRegion[i][0][0]
				longestRangeSet = lossyLinearRegion[i].copy()
				longestRangeIndex = i
	del lossyLinearRegion[longestRangeIndex]

	# Calculate the slope of the longest linear region
	print("\nMaximum yield stress:")
	x1, y1, x2, y2 = longestRangeSet[0][0], longestRangeSet[1][0], longestRangeSet[0][1], longestRangeSet[1][1]
	print(y2)
	slope = (y2 - y1)/(x2 - x1)
	print("Modulus:")
	print(slope)

	# Plot the results
	plt.plot(displacementSet, forceSet, label="force")
	plt.plot(displacementSet, firstDerivatives, label="first derivative")
	plt.plot(secondDerivatives[0], secondDerivatives[1], label="second derivative")
	plt.plot(minMaxPoints[0], minMaxPoints[1], "o", label="local minima and maxima")
	for i in range(0, len(lossyLinearRegion)):
		if i == 0:
			thisLabel = "linear regions"
		else:
			thisLabel = ""
		plt.plot(lossyLinearRegion[i][0], lossyLinearRegion[i][1], "o-", color="purple", label=thisLabel)
	plt.plot(longestRangeSet[0], longestRangeSet[1], "o-", color="magenta", label="Modulus: "+str(round(slope,2)))
	plt.legend(loc=0)
	plt.show()

# Simple moving average, https://www.quora.com/How-do-I-perform-moving-average-in-Python
def movingAverage(l, N):
	sum = 0
	result = list( 0 for x in l)

	for i in range( 0, N ):
		sum = sum + l[i]
		result[i] = sum / (i+1)

	for i in range( N, len(l) ):
		sum = sum - l[i-N] + l[i]
		result[i] = sum / N

	return result


if __name__ == "__main__":
	main(sys.argv[1:])
