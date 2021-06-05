import time
import xlrd
import argparse
import itertools
from anytree import Node, RenderTree

def max_ind(arr):
    maxi = 0
    for i in range(len(arr)):
        if arr[maxi] < arr[i]:
            maxi = i
    return maxi


def main():

    tmp = []
    parser = argparse.ArgumentParser(description='Программа расчет максимальной прибыли')
    parser.add_argument('--path', help='Путь к таблице объектов', default='5.xls')
    parser.add_argument('--var', help='Число вариантов', default=3, type=int)
    parser.add_argument('--obj', help='Число объектов', default=10, type=int)
    parser.add_argument('--greed', help='Процент объектов для жадного алгоритма, от 0 до 100', default=40, type=int)
    parser.add_argument('--brute', help='Запускать полный перебор', action="store_true")
    parser.add_argument('--mvg', help='Запускать метод ветвей и границ', action="store_true")
    parser.add_argument('--usegreed', help='Учитывать решения жадного алгоритма в МВГ', action="store_true")

    args = parser.parse_args()

    if not (0 <= args.greed <= 100):
        print('Процент объектов для жадного алгоритма должен быть от 0 до 100!')
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

    print()
    print("**** Жадный алгоритм ********")
    greedy_vars = find_best_variants(args, tmp, money, number_of_greedy_obj)


    if args.brute:
        print()
        print("**** Метод полного перебора ********")
        startTime = time.time()
        bf = brute_force(args, tmp, money)
        print("Затраты: ", bf[0], " - Доход: ", bf[1])
        print("Выбранные варианты: ", [x+1 if x < args.var else 0 for x in bf[2]])
        endTime = time.time()
        totalTime = endTime - startTime
        print("Время, потраченное на выполнение данного кода = ", totalTime*1000)

    if args.mvg:
        print()
        print("**** Метод ветвей и границ ********")
        startTime = time.time()
        greedy_obj = [n[3]+1 for n in greedy_vars]
        if args.usegreed:
            money_rest = money - sum([n[0][0] for n in greedy_vars])
            bf = mvg(args, tmp, money_rest, greedy_obj)
            if greedy_vars:
                greedy_var = [n[2]+1 for n in greedy_vars]
                zipped_greed = list(zip(greedy_obj, greedy_var))
                zipped_mvg = list(zip(bf[2][0], bf[2][1]))

                if zipped_mvg == [(0, 0)]:
                    total = zipped_greed
                else:
                    total = zipped_greed + zipped_mvg

                total.sort(key=lambda k: k[0])
                print("Затраты: ", bf[0] + sum([n[0][0] for n in greedy_vars]), " - Доход: ", bf[1] + sum([n[0][1] for n in greedy_vars]))
                print("Выбранные объекты: ", [n[0] for n in total])
                print("Их варианты: ", [n[1] for n in total])
            else:
                print("Затраты: ", bf[0], " - Доход: ", bf[1])
                print("Выбранные объекты: ", bf[2][0])
                print("Их варианты: ", bf[2][1])

        else:
            bf = mvg(args, tmp, money, greedy_obj)
            print("Затраты: ", bf[0], " - Доход: ", bf[1])
            print("Выбранные объекты: ", bf[2][0])
            print("Их варианты: ", bf[2][1])

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
    choose_obj = []
    while len(used_obj) < number_of_greedy_obj:

        best_variants = []  # np.zeros((args.obj, 5))
        for vs in table:  # Обойдем каждый объект в поиске лучшего варианта на оставшиеся деньги
            ind = table.index(vs)
            if ind in used_obj:
                continue
            vsn = [[s, s[1] / s[0] if s[0] > 0 else float("inf"), vs.index(s)] for s in vs if s[0] < money_rest]

            if not vsn:
                continue
            best_variant = max(vsn, key=lambda item: item[1])
            best_variants.append([*best_variant, ind])

        if not best_variants:
            break  # best_variants_ret  # Деньги закончились быстрее, чем объекты, и не смогли ничего найти на оставшуюся сумму
        best_variants.sort(key=lambda k: k[1], reverse=True)
        for el in best_variants:
            if el[0][0] <= money_rest:
                best_variants_ret.append(el)
                money_rest -= el[0][0]
                used_obj.append(el[3])

                expenses += el[0][0]
                proceeds += el[0][1]
                maxind.append(el[2] + 1)
                choose_obj.append(el[3] + 1)

                break

    print("Затраты: ", expenses, " - Доход: ", proceeds)
    print("Выбранные объекты: ", choose_obj)
    print("Выбранные варианты: ", maxind)

    endTime = time.time()
    totalTime = endTime - startTime
    print("Время, потраченное на выполнение данного кода = ", totalTime * 1000)
    return best_variants_ret

def find_cost_profit_mvg(args, table, subset, fl):
    cost = 0
    profit = 0
    for i in fl:
        cost += table[i-1][subset[fl.index(i)]][0]
        profit += table[i-1][subset[fl.index(i)]][1]
    return [cost, profit]

def check_cost(args, table, fl, money, best_variant):
    variants = [var for var in range(1, args.var + 1)]
    costs = [variants for _ in range(len(fl))]
    ok = False

    for subset in itertools.product(*costs):
        cost_profit = find_cost_profit_mvg(args, table, subset, fl)

        if cost_profit[0] <= money:
            ok = True
            if cost_profit[1] > best_variant[1]:
                best_variant[1] = cost_profit[1]
                best_variant[0] = cost_profit[0]
                best_variant[2] = [fl, subset]
    return ok

def add_children(args, table, knot, obj_num, money, best_variant, greedy_obj):  # Добавлять будем только в случае, если затраты еще не превышены
    # Сначал нужно проверить, не превысили ли мы уже для этого варианта наши затраты
    # Если превысили, этот узел нужно удалить, а не добавлять ему детей
    # А лучше организовать проверку перед добавлением, так должно быть быстрее

    for obj_num_loc in range(obj_num, args.obj+1):
        if args.usegreed and obj_num_loc in greedy_obj:  # Пропустим объекты, которые уже взяты жадным алгоритмом
            continue

        if obj_num_loc <= knot.name:
            continue
        fl = [n.name for n in knot.ancestors if n.name > 0]
        fl.append(knot.name)
        fl.append(obj_num_loc)
        no_overcost = check_cost(args, table, fl, money, best_variant)  # Тут нужно возвращать еще и лучший из проверенных вариантов, чтобы в случае успешного проходения проверки сравнить его с лучшим предыдущим и добавить.
        if not no_overcost:
            print("Данную ветвь отсекаем, т.к. превышаются затраты при любом варианте:", fl)
            continue

        kinder = Node(obj_num_loc, parent=knot)
        add_children(args, table, kinder, obj_num + 1, money, best_variant, greedy_obj)

def tree(args, table, money, greedy_obj):  # Формируем дерево объектов, которые нужно обойти.
    root = Node(0)
    best_variant = [0, 0, [[0], (0,)]]
    for obj_num in range(1, args.obj+1):
        if args.usegreed and obj_num in greedy_obj:  # Пропустим объекты, которые уже взяты жадным алгоритмом
            continue

        fl = [obj_num]
        no_overcost = check_cost(args, table, fl, money, best_variant)  # Тут нужно возвращать еще и лучший из проверенных вариантов, чтобы в случае успешного проходения проверки сравнить его с лучшим предыдущим и добавить.
        if not no_overcost:
            print("Данную ветвь отсекаем, т.к. превышаются затраты при любом варианте:", fl)
            continue

        knot = Node(obj_num, parent=root)
        add_children(args, table, knot, obj_num + 1, money, best_variant, greedy_obj)
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))
    return best_variant

def mvg(args, table, money, greedy_obj):
    for i in table:
        i.insert(0, [0, 0])  # Добавляем еще один вариант - пустой, чтобы перебрать варианты не со всеми объектами тоже

    best_variant = tree(args, table, money, greedy_obj)

    return best_variant


def brute_force(args, table, money):
    for i in table:
        i.append([0, 0])  # Добавляем еще один вариант - пустой, чтобы перебрать варианты не со всеми объектами тоже

    variants = [var for var in range(args.var + 1)]
    costs = [variants for _ in range(args.obj)]

    bf_profit = 0
    bf_cost = 0
    best_variant = ...
    for subset in itertools.product(*costs):
        cost_profit = find_cost_profit(args, table, subset)
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
