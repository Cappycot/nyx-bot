# fuck this

from re import match


data = open("EventsDST.dat")

output = open("EventsUTC.dat", "w")

def day(num):
	if num % 10000 > 2400:
		num += 7600
	return num

for line in data:
	line = line.strip("\n ")
	if not line:
		pass
	elif match("^[0-9]", line) is None:
		output.write(line)
	else:
		things = line.split("-")
		# 400 for EDT, 500 for EST (non DST)
		num1 = day(int(things[0]) + 400)
		num2 = day(int(things[1]) + 400)
		if num1 >= 80000:
			num1 -= 70000
			num2 -= 70000
		output.write("{}-{}".format(num1, num2))
	output.write("\n")
	
output.flush()
output.close()
data.close()

