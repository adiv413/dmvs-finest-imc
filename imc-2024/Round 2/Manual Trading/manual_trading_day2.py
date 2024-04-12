conversion = [[1, 0.48, 1.52, 0.71], [2.05, 1, 3.26, 1.56], [0.64
,0.3, 1, 0.46], [1.41, 0.61, 2.08, 1]]

starting_seashells = 2_000_000

def recur(stock, quantity, depth = 0):
    if depth == 4:
        return quantity * conversion[stock][3]
    else:
        return max([recur(i, quantity * conversion[stock][i], depth + 1) for i in range(4)])


def recur_with_path(stock, quantity, path = [3], depth = 0):
    if depth == 4:
        return quantity * conversion[stock][3], path + [3]
    else:
        results = [recur_with_path(i, quantity * conversion[stock][i], path + [i], depth + 1) for i in range(4)]
        return max(results, key = lambda x: x[0])
print(recur_with_path(3, starting_seashells))
#double check
print(starting_seashells * conversion[3][0] * conversion[0][1] * conversion[1][3] * conversion[3][0] * conversion[0][3])

