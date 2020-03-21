#!/usr/bin/env python3.7

import sys, getopt
import csv

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
	
	# Smooth data
	# each displacement position has on average six data points
	force = movingAverage(force.copy(), 6).copy()

	# Find local minima or maxima
	print("Displ.\tForce")
	for i in range(2, len(force)):
		if force[i] < 0:
			continue # false positives in unstable region before test begins
		deriv1 = force[i]   -  force[i-1]
		deriv2 = force[i-1] -  force[i-2]
		if (deriv1 * deriv2) < 0:
			print(displacement[i], force[i])

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
