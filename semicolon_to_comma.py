
filename = 'Logs/stoikov'
with open(filename + ".csv", 'r') as f:
    lines = f.readlines()

#change semicolon to comma
lines = [line.replace(';', ',') for line in lines]

#output to new file
with open(filename + "_fixed.csv", 'w') as f:
    f.writelines(lines)