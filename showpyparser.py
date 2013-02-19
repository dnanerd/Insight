import sys

count=0
for line in sys.stdin:
	linear = line.split()
	try:
		if float(linear[2])>=0.3:
			sys.stdout.write(line)
	except:
		count +=1
#		if float(linear[-1])>=0.4:

sys.stderr.write(str(count) + " error thrown\n")