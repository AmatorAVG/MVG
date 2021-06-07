import main
import PySimpleGUI as sg


layout = [
    [sg.T('Путь к таблице объектов:'),
     sg.In(default_text='5.xls', size=(35, 1), key='path'), sg.FileBrowse(size=(15, 1))],
    [sg.Text('Число вариантов:', size=(35, 1)), sg.Text('Число объектов:')],
    [sg.Slider(range=(1, 50), default_value=3, orientation="h", size=(30, 10), key='var'),
     sg.Slider(range=(1, 100), default_value=10, orientation="h", size=(30, 10), key='obj')],
    [sg.Text('Процент объектов для жадного алгоритма (при 0 объектов не запускается):')],
    [sg.Slider(range=(0, 100), default_value=40, orientation="h", size=(65, 10), key='greed')],
    [sg.Checkbox('Учитывать решения жадного алгоритма в МВГ', key='usegreed')],
    [sg.Checkbox('Запускать полный перебор', key='brute')],
    [sg.Checkbox('Запускать метод ветвей и границ', key='mvg')],
    [sg.Button("Поехали!", size=(50, 2)), sg.Cancel(size=(15, 2))],
]


window = sg.Window('Метод ветвей и границ', layout, size=(640, 320))
while True:                             # The Event Loop
    event, values = window.read()
    if event in (None, 'Exit', 'Cancel'):
        break

    if event == 'Поехали!':
        main.r_print._gui = True
        res = main.main(values)
        sg.popup(res, title="Результат")
