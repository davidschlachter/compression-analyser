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
	print("Displ.\tForce")
	firstDerivatives = [0, 0]
	secondDerivative = 0
	secondDerivatives = [[], []]
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
		if (deriv1 * deriv2) < 0:
			print(displacementSet[i-1], forceSet[i-1])
			minMaxPoints[0].append(displacementSet[i-1])
			minMaxPoints[1].append(forceSet[i-1])

	plt.plot(displacementSet, forceSet, label="force")
	plt.plot(displacementSet, firstDerivatives, label="first derivative")
	plt.plot(secondDerivatives[0], secondDerivatives[1], label="second derivative")
	plt.plot(minMaxPoints[0], minMaxPoints[1], "o", label="local minima and maxima")
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
