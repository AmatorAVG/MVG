import time
import xlrd
import argparse
import itertools

def max_ind(arr):
    maxi = 0
    for i in range(len(arr)):
        if arr[maxi] < arr[i]:
            maxi = i
    return maxi


def main():


    tmp = []

    parser = argparse.ArgumentParser(description='Программа расчет максимальной прибыли')
    parser.add_argument('--path', help='Путь к таблице объектов', default='3.xls')
    parser.add_argument('--var', help='Число вариантов', default=5)
    parser.add_argument('--obj', help='Число объектов', default=9)

    args = parser.parse_args()

    book = xlrd.open_workbook(args.path)
    sheet = book.sheet_by_index(0)
    money = float(sheet.cell_value(0, 1))
    data1 = [[sheet.cell_value(r, c) for r in range(4, 4+args.var)] for c in range(0, args.obj+1)]
    data2 = [[sheet.cell_value(r, c) for r in range(4, 4+args.var)] for c in range(args.obj+3, 2*args.obj+4)]

    startTime = time.time()  # Время на чтение данных из файла не будем учитывать, оно постоянно для всех алгоритмов


    for i in range(1, args.obj+1):
        data = list(map(list, zip(data1[i], data2[i])))
        tmp.append(data)
    print(tmp)

    items = tmp

    exp = [0]*args.obj
    tops = [1000 for x in range(len(items))]  # ,1000,1000,1000,1000,1000,1000,1000,1000,1000]
    bottoms = [0 for x in range(len(items))]
    maxind = [0]*args.obj

    expenses = 0
    proceeds = 0
    for i in range(len(tops)):
        item = items[i]
        maxi = 0
        for j in range(len(item)):
            if item[j][1] > item[maxi][1]:
                maxi = j
        tops[i] = item[maxi][0]
        exp[i] = item[maxi][1]
        bottoms[i] = min([el[0] for el in item])

        expenses += tops[i]
        proceeds += exp[i]
        maxind[i] = maxi

    while expenses > money:
        maxi = max_ind(tops)
        expenses -= tops[maxi]
        proceeds -= exp[maxi]

        maxj = -1
        for i in range(len(items[maxi])):
            if items[maxi][i][0] < tops[maxi]:
                if maxj < 0 or items[maxi][maxj][1] < items[maxi][i][1]:
                    maxj = i

        tops[maxi] = items[maxi][maxj][0]
        exp[maxi] = items[maxi][maxj][1]
        expenses += tops[maxi]
        proceeds += exp[maxi]
        maxind[maxi] = maxj

    for i in range(len(maxind)):
        maxind[i] += 1

    print("Затраты: ", expenses, " - Доход: ", proceeds)
    print("Выбраные варианты: ", maxind)
    print("Их затраты: ", tops)
    print("Их выручки: ", exp)

    endTime = time.time()
    totalTime = endTime - startTime
    print("Время, потраченное на выполнение данного кода = ", totalTime)

    print()
    print("**** Метод полного перебора ********")
    startTime = time.time()
    bf = brute_force(args, tmp, money)
    print("Затраты: ", bf[0], " - Доход: ", bf[1])
    # print("Выбраные варианты: ", maxind)
    # print("Их затраты: ", tops)
    # print("Их выручки: ", exp)
    endTime = time.time()
    totalTime = endTime - startTime
    print("Время, потраченное на выполнение данного кода = ", totalTime)

def brute_force(args, table, money):
    for i in table:
        i.append([0, 0])  # Добавляем еще один вариант - пустой, чтобы перебрать варианты не со всеми объектами тоже

    variants = [var for var in range(args.var + 1)]
    costs = [variants for _ in range(args.obj)]

    bf_profit = 0
    bf_cost = 0
    for subset in itertools.product(*costs):
        # print(subset)
        cost_profit = find_cost_profit(args, table, subset)
        # print(cost_profit)
        if cost_profit[0] <= money and cost_profit[1] > bf_profit:
            bf_profit = cost_profit[1]
            bf_cost = cost_profit[0]
    return [bf_cost, bf_profit]

def find_cost_profit(args, table, subset):
    cost = 0
    profit = 0
    for i in range(len(subset)):
        cost += table[i][subset[i]][0]
        profit += table[i][subset[i]][1]
    return [cost, profit]




if __name__ == '__main__':
    main()
