import time
import xlrd
import argparse
import itertools
import pprint
# import numpy as np
from anytree import Node, RenderTree
from anytree.exporter import DictExporter

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
    parser.add_argument('--var', help='Число вариантов', default=2)
    parser.add_argument('--obj', help='Число объектов', default=4)
    parser.add_argument('--greed', help='Процент объектов для жадного алгоритма, от 0 до 50%', default=100)
    parser.add_argument('--brute', help='Запускать полный перебор', default=False)
    parser.add_argument('--mvg', help='Запускать метод ветвей и границ', default=True)

    args = parser.parse_args()

    if not (0 <= args.greed <= 100):
        print('Процент объектов для жадного алгоритма должен быть от 0 до 50!')
        return

    number_of_greedy_obj = int(args.obj * args.greed / 100)
    print(f'Число объектов для жадного алгоритма: {number_of_greedy_obj} из {args.obj}')

    book = xlrd.open_workbook(args.path)
    sheet = book.sheet_by_index(0)
    money = float(sheet.cell_value(0, 1))
    data1 = [[sheet.cell_value(r, c) for r in range(4, 4+args.var)] for c in range(0, args.obj+1)]
    data2 = [[sheet.cell_value(r, c) for r in range(4, 4+args.var)] for c in range(args.obj+3, 2*args.obj+4)]

    for i in range(1, args.obj+1):
        data = list(map(list, zip(data1[i], data2[i])))
        tmp.append(data)
    # pprint.pprint(tmp)

    print()
    print("**** Жадный алгоритм ********")
    find_best_variants(args, tmp, money, number_of_greedy_obj)


    print()
    print("**** Метод ветвей и границ (исходный, неправильный) ********")

    startTime = time.time()  # Время на чтение данных из файла не будем учитывать, оно постоянно для всех алгоритмов

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
    print("Время, потраченное на выполнение данного кода = ", totalTime*1000)

    if args.brute:
        print()
        print("**** Метод полного перебора ********")
        startTime = time.time()
        bf = brute_force(args, tmp, money)
        print("Затраты: ", bf[0], " - Доход: ", bf[1])
        print("Выбраные варианты: ", [x+1 for x in bf[2]])
        # print("Их затраты: ", tops)
        # print("Их выручки: ", exp)
        endTime = time.time()
        totalTime = endTime - startTime
        print("Время, потраченное на выполнение данного кода = ", totalTime*1000)

    if args.mvg:
        print()
        print("**** Метод ветвей и границ новый ********")
        startTime = time.time()
        bf = mvg(args, tmp, money)
        print("Затраты: ", bf[0], " - Доход: ", bf[1])
        print("Выбраные варианты: ", [x+1 for x in bf[2]])
        # print("Их затраты: ", tops)
        # print("Их выручки: ", exp)
        endTime = time.time()
        totalTime = endTime - startTime
        print("Время, потраченное на выполнение данного кода = ", totalTime*1000)


def find_best_variants(args, table, money_rest, number_of_greedy_obj):
    startTime = time.time()
    if number_of_greedy_obj == 0:
        return []
    best_variants_ret = []
    used_obj = []  # Список объектов, которые уже попали в выборку, чтобы не искать среди них снова
    expenses = 0
    proceeds = 0
    maxind = []
    while len(used_obj) < number_of_greedy_obj:
        # startTimeC = time.time()

        best_variants = []  # np.zeros((args.obj, 5))
        # print(best_variants)
        for vs in table:  # Обойдем каждый объект в поиске лучшего варианта на оставшиеся деньги
            # startTimeT = time.time()
            ind = table.index(vs)
            if ind in used_obj:
                continue
            vsn = [[s, s[1] / s[0] if s[0] > 0 else float("inf"), vs.index(s)] for s in vs if s[0] < money_rest]
            # print(vsn)

            if not vsn:
                continue
            # print("Время, потраченное на выполнение 1 цикла 4= ", (time.time() - startTimeT) * 1000)
            best_variant = max(vsn, key=lambda item: item[1])

            # best_variant = vsn[0]
            # for j in vsn:
            #     if j[1] > best_variant[1]:
            #         best_variant = j

            #best_cost, best_profit = max(vsn, key=lambda item: item[1])
            #print(best_variant)
            # print("Время, потраченное на выполнение 1 цикла 5= ", (time.time() - startTimeT) * 1000)
            best_variants.append([*best_variant, ind])

            #best_variants[ind][0] = best_variant[0][0] #  ([best_variant[0][0], best_variant[0][1], best_variant[1], best_variant[2], ind])

            # print("Время, потраченное на выполнение 1 цикла 6= ", (time.time() - startTimeT) * 1000)
        # print("Время, потраченное на выполнение 1 цикла 3= ", (time.time() - startTimeC) * 1000)
        if not best_variants:
            print('No money, need chiper variant')
            break  # best_variants_ret  # Деньги закончились быстрее, чем объекты, и не смогли ничего найти на оставшуюся сумму
        best_variants.sort(key=lambda k: k[1], reverse=True)
        # print("Время, потраченное на выполнение 1 цикла 1= ", (time.time() - startTimeC) * 1000)
        # pprint.pprint(best_variants)
        # print()
        for el in best_variants:
            #print(money_rest)
            if el[0][0] <= money_rest:
                best_variants_ret.append(el)
                money_rest -= el[0][0]
                used_obj.append(el[3])

                expenses += el[0][0]
                proceeds += el[0][1]
                maxind.append(el[2] + 1)
                break
        # print("Время, потраченное на выполнение 1 цикла 2= ", (time.time() - startTimeC) * 1000)


    # pprint.pprint(best_variants_ret)
    # expenses = 0
    # proceeds = 0
    # maxind = []
    # for n in best_variants_ret:
    #     expenses += n[0][0]
    #     proceeds += n[0][1]
    #     maxind.append(n[2] + 1)

    # expenses = sum([n[0][0] for n in best_variants_ret])
    # proceeds = sum([n[0][1] for n in best_variants_ret])
    # maxind = [n[2] + 1 for n in best_variants_ret]
    print("Затраты: ", expenses, " - Доход: ", proceeds)
    print("Выбраные варианты: ", maxind)

    endTime = time.time()
    totalTime = endTime - startTime
    print("Время, потраченное на выполнение данного кода = ", totalTime * 1000)
    return best_variants_ret

def find_cost_profit_mvg(args, table, fl):
    vars = range(1, args.var+1)
    print()
    cost = 0
    profit = 0

    for (obj, var) in itertools.product(fl, vars):
        print(f"obj: {obj}, var: {var}")
        cost += table[obj][var][0]
        profit += table[obj][var][1]

    print()
    return [cost, profit]

def check_cost(args, table, fl):
    #vars = range(1, args.var + 1)
    #vars = ['v1', 'v2']
    print()
    cost = 0
    profit = 0
    variants = [var for var in range(1, args.var + 1)]
    costs = [variants for _ in range(len(fl))]

    #for subset in itertools.product(fl, repeat=2):
    for subset in itertools.product(*costs):
        print(subset)  # Тут все варианты, которые нужно проверить
        #print(f"obj: {obj}, var: {var}")
        # cost += table[obj][var][0]
        # profit += table[obj][var][1]

        # print(subset)
    print()
    return [False, cost, profit]

def add_children(args, table, knot, obj_num):  # Добавлять будем только в случае, если затраты еще не превышены
    # Сначал нужно проверить, не превысили ли мы уже для этого варианта наши затраты
    # Если превысили, этот узел нужно удалить, а не добавлять ему детей
    # А лучше организовать проверку перед добавлением, так должно быть быстрее

    for obj_num_loc in range(obj_num, args.obj+1):
        if obj_num_loc <= knot.name:
            continue
        fl = [n.name for n in knot.ancestors if n.name > 0]
        fl.append(knot.name)
        fl.append(obj_num_loc)
        print(fl)  # Вот для этого списка объектов нужно сделать проверку стоимости
        overcost = check_cost(args, table, fl)  # Тут нужно возвращать еще и лучший из проверенных вариантов, чтобы в случае успешного проходения проверки сравнить его с лучшим предыдущим и добавить.
        if overcost[0]:
            continue

        # cost_profit = find_cost_profit_mvg(args, table, fl)
        # # print(cost_profit)
        # if cost_profit[0] >= money:
        #     print("Пропускаем ")
        #     continue
        # if cost_profit[0] <= money and cost_profit[1] > bf_profit:
        #     bf_profit = cost_profit[1]
        #     bf_cost = cost_profit[0]
        #     best_variant = subset
        # return [bf_cost, bf_profit, best_variant]



        kinder = Node(obj_num_loc, parent=knot)
        add_children(args, table, kinder, obj_num + 1)
        #print('added')

def tree(args, table):  # Формируем дерево объектов, которые нужно обойти.
    root = Node(0)
    for obj_num in range(1, args.obj+1):
        knot = Node(obj_num, parent=root)
        add_children(args, table, knot, obj_num + 1)
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))


def mvg(args, table, money):
    for i in table:
        i.insert(0, [0, 0])  # Добавляем еще один вариант - пустой, чтобы перебрать варианты не со всеми объектами тоже

    variants = [var for var in range(args.var + 1)]
    costs = [variants for _ in range(args.obj)]
    #costs = [variants for _ in range(2)]
    # arr = [0]*args.obj
    # for i in range(args.obj + 1):
    tree(args, table)
    #     # for j in range(args.var + 1):
    #     #     for k in range(args.var + 1):
    #     #         print(i, j, k)

    bf_profit = 0
    bf_cost = 0
    best_variant = ...
    pprint.pprint(costs)
    it = itertools.product(*costs)
    for subset in it:
        # l = list(subset)
        #print(l)
        #continue

        cost_profit = find_cost_profit(args, table, subset)
        #print(cost_profit)
        if cost_profit[0] <= money and cost_profit[1] > bf_profit:
            bf_profit = cost_profit[1]
            bf_cost = cost_profit[0]
            best_variant = subset
    return [bf_cost, bf_profit, best_variant]


def brute_force(args, table, money):
    for i in table:
        i.append([0, 0])  # Добавляем еще один вариант - пустой, чтобы перебрать варианты не со всеми объектами тоже

    variants = [var for var in range(args.var + 1)]
    costs = [variants for _ in range(args.obj)]

    bf_profit = 0
    bf_cost = 0
    best_variant = ...
    for subset in itertools.product(*costs):
        # print(subset)
        cost_profit = find_cost_profit(args, table, subset)
        # print(cost_profit)
        if cost_profit[0] <= money and cost_profit[1] > bf_profit:
            bf_profit = cost_profit[1]
            bf_cost = cost_profit[0]
            best_variant = subset
    return [bf_cost, bf_profit, best_variant]


def find_cost_profit(args, table, subset):
    cost = 0
    profit = 0
    for i in range(len(subset)):
        cost += table[i][subset[i]][0]
        profit += table[i][subset[i]][1]
    return [cost, profit]




if __name__ == '__main__':
    main()
