conversion = [[1, 0.5, 1.45, 0.75], [1.95, 1, 3.1, 1.49], [0.67, 0.31, 1, 0.48], [1.34, 0.64, 1.98, 1]]

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
print(starting_seashells * conversion[3][0] * conversion[0][1] * conversion[1][2] * conversion[2][0] * conversion[0][3])

