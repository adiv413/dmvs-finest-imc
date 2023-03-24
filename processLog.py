import pandas as pd
import matplotlib as plt

#read log.txt into a dataframe. The format is as follows:
# [timestamp]: ...
# Pina Price: xxx
# Coco Price: xxx
# Pina Position: xxx
# Coco Position: xxx


# open the file without using pandas
with open("log.txt", "r") as f:
    # read line by line
    lines = [line.strip() for line in f.readlines()]
# separate into 1st line + 4*nth line
#separate into 2nd line + 4*nth line
#separate into 3rd line + 4*nth line
#separate into 4th line + 4*nth line

pinaPrices = [lines[i] for i in range(1, len(lines), 4)]
cocoPrices = [lines[i] for i in range(2, len(lines), 4)]
pinaPositions = [lines[i] for i in range(3, len(lines), 4)]
cocoPositions = [lines[i] for i in range(4, len(lines), 4)]

# convert these into a dataframe
# df = pd.DataFrame({"pinaPrices": pinaPrices, "cocoPrices": cocoPrices, "pinaPositions": pinaPositions, "cocoPositions": cocoPositions})
# df.head()

print(pinaPrices)