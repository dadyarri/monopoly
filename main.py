import random

import data


# Базовый класс, описывающий игровую сессию
class Base:
    def __init__(self):
        self.field = data.field
        self.players = []  # Список с объектами игроков
        self.current_player = 0  # Номер текущего игрока
        self.cells = 39  # Количество ячеек на поле
        self.number_of_players = 0  # Количество игроков
        self.currency = '₩'

        self.cp = None


# Класс, описывающий игрока, его позицию на поле, баланс, нахождение в тюрьме
class Player:
    def __init__(self, name: str):
        self.base_coord = 0  # Начальная координата
        self.last_coord = self.base_coord  # Предыдущая координата
        self.cur_coord = self.base_coord  # Текущая координата
        self.base_balance = 1500  # Начальный баланс
        self.cur_balance = self.base_balance  # Текущий баланс

        self.name = name  # Отображаемое имя
        f_die, s_die = throw_a_die()
        self.start_score = f_die + s_die  # Начальный бросок кубика
        self.takes = 0  # Дублей выпало

        self.in_jail = False  # Игрок в тюрьме?
        self.left_in_jail = 0  # Ходов осталось провести в тюрьме
        self.escape_card = 0  # Карточки освобождения из тюрьмы ("Казна" или "Шанс")


def start_new_game():
    # Начало новой игры
    print('*********\nMONOPOLY\n*********\n')
    game.number_of_players = int(input('Введите количество игроков:\n> '))
    for i in range(game.number_of_players):
        game.players.append(Player(name=input(f'Введите имя игрока {i + 1}: ')))
    # Сортировка игроков по возрастанию стартовых очков
    for i in range(len(game.players)):
        # Исходно считаем наименьшим первый элемент
        lowest_value_index = i
        # Этот цикл перебирает несортированные элементы
        for j in range(i + 1, len(game.players)):
            if game.players[j].start_score < game.players[lowest_value_index].start_score:
                lowest_value_index = j
        # Самый маленький элемент меняем с первым в списке
        game.players[i], game.players[lowest_value_index] = game.players[lowest_value_index], game.players[i]
    game.players.reverse()  # Переворот списка игроков, чтобы сортировать игроков по убыванию
    # Вывод порядка хода
    print('Порядок хода игроков: ', end='')
    for i in range(len(game.players)):
        if i != len(game.players) - 1:  # Разделитель между игроками
            end = ', '  # Если сейчас выводится не последний игрок, тогда выведи после него запятую
        else:
            end = '\n'  # Иначе – новую строку
        print(f'{game.players[i].name}', end=end)
    game.cp = game.players[game.current_player]


def print_info():
    print('===')
    print(f'Сейчас ход игрока {game.cp.name}.')
    print(f'У вас на счету: {game.cp.cur_balance}{game.currency}')
    print(f'Вы находитесь на ячейке {game.field[game.cp.cur_coord]["name"]}.')
    print('===')


def escape_from_jail():
    # Пытаемся освободить игрока
    f_die, s_die = throw_a_die()
    print('Бросаю кубики...', end=' ')
    print(f'На кубиках выпало {f_die} и {s_die}.')
    if f_die == s_die:  # Если выпадает дубль, то освобождаем
        print(f'У вас получилось сбежать. Ваш ход, {game.cp.name}.')
        game.cp.in_jail = False
        game.cp.left_in_jail = 0
        start_move()  # И даем право сходиться еще раз
    else:  # Иначе, добавляем к заключению штрафные ходы (рандом от 1 до 3)
        moves = random.randint(1, 3)
        print(f'Не повезло... Вас поймали и дали дополнительный срок в {moves} ходов.')
        game.cp.left_in_jail += moves


def start_move():
    # Начало хода
    print_info()
    if game.cp.in_jail:  # Если игрок в тюрьме
        print('Вы в тюрьме и не можете сделать ход но можете попытаться сбежать, если у вас выпадет дубль.')
        if prompt('Пробуем?'):
            escape_from_jail()
        else:
            game.cp.left_in_jail -= 1  # Вычитаем один ход из его заключения
        if game.cp.left_in_jail != 0:
            print(f'Вам осталось провести в тюрьме {game.cp.left_in_jail} ходов.')
        else:  # Если время заключения прошло
            print('Вы вышли из тюрьмы.')
            game.cp.in_jail = False  # Освобождаем игрока
            start_move()  # И даем возможность сходиться
    else:
        bankrupt = False
        if game.cp.cur_balance <= 0:  # Если баланс игрока меньше или равен нулю, тогда
            print('Вы банкрот, голубчик!')
            game.cp.cur_balance = 0
            bankrupt = True  # Признаем его банкротом
        print(f'Выберите действие:\n')
        if not bankrupt:  # И ограничиваем действия
            print('1 – Бросить кубик')
        print('2 – Управление недвижимостью')
        print('3 – Признать банкротство')
        try:
            move = int(input('> '))
        except ValueError:
            print('Ожидается ввод числа')
            start_move()
        else:
            if not bankrupt:
                if move in [1, 2, 3]:
                    if move == 1:  # Бросить кубики и завершить ход
                        print('бросаем кубики и делаем ход.')
                        make_move()  # Сделать ход
                        print('выполняем действия карточки.')
                        move_actions()
                        print('завершаем ход.')
                        complete_move()
                    elif move == 2:  # Начать управление недвижимостью
                        property_management()
                        start_move()
                    elif move == 3:  # Сдаться
                        recognize_bankruptcy()
                else:  # Неизвестная команда
                    print('Введите число от 1 до 3!')
                    start_move()
            else:
                if move in [2, 3]:
                    if move == 2:  # Начать управление недвижимостью
                        property_management()
                        start_move()
                    elif move == 3:  # Сдаться
                        recognize_bankruptcy()
                else:  # Неизвестная команда
                    print('Введите число от 2 до 3!')
                    start_move()


def move_actions():
    print(f'Вы находитесь на ячейке {game.field[game.cp.cur_coord]["name"]}')
    if game.field[game.cp.cur_coord]["owned_by"] is None and game.cp.cur_coord not in [0, 2, 4, 7, 10, 17, 20, 29, 34,
                                                                                       36]:
        # Если ячейка никому не принадлежит и если ячейка не служебная (т. е. её можно купить)
        if game.field[game.cp.cur_coord]["price"] < game.cp.cur_balance:  # Если у игрока достаточно денег
            if prompt(f'Предприятие никому не принадлежит. Хотите купить?\n'
                      f'Её стоимость: {game.field[game.cp.cur_coord]["price"]}\n'
                      f'У вас есть: {game.cp.cur_balance}'):  # Предлагаем игроку купить эту карточку
                game.field[game.cp.cur_coord]["owned_by"] = game.current_player  # Покупаем
                game.cp.cur_balance -= game.field[game.players[
                    game.current_player].cur_coord]["price"]
                print(f'Успех! Предприятие {game.field[game.cp.cur_coord]["name"]} теперь ваше!')
            else:
                auction()
        else:
            print('У вас недостаточно средств для покупки этой карточки.')
            auction()
    else:
        if game.field[game.cp.cur_coord]["owned_by"] is not None:  # Если ячейка принадлежит какому-то игроку
            print(f'Предприятие {game.field[game.cp.cur_coord]["name"]} принадлежит '
                  f'игроку '
                  f'{game.players[game.field[game.cp.cur_coord]["owned_by"]].name}')
            # Вычисляем ренту
            if game.field[game.cp.cur_coord]["houses"] is None and game.field[game.cp.cur_coord]["hotel"] is None:
                value = game.field[game.cp.cur_coord]["renta"]
            elif game.field[game.cp.cur_coord]["houses"] == 1 and game.field[game.cp.cur_coord]["hotel"] is None:
                value = game.field[game.cp.cur_coord]["one_house_renta"]
            elif game.field[game.cp.cur_coord]["houses"] == 2 and game.field[game.cp.cur_coord]["hotel"] is None:
                value = game.field[game.cp.cur_coord]["two_house_renta"]
            elif game.field[game.cp.cur_coord]["houses"] == 3 and game.field[game.cp.cur_coord]["hotel"] is None:
                value = game.field[game.cp.cur_coord]["three_house_renta"]
            elif game.field[game.cp.cur_coord]["houses"] == 4 and game.field[game.cp.cur_coord]["hotel"] is None:
                value = game.field[game.cp.cur_coord]["four_house_renta"]
            elif game.field[game.cp.cur_coord]["houses"] is None and game.field[game.cp.cur_coord]["hotel"] == 1:
                value = game.field[game.cp.cur_coord]["hotel_renta"]
            else:
                value = 0
            print(f'Вы должны заплатить ему ренту в размере {value}{game.currency}.')  # И переводим ее на счет хозяина
            game.cp.cur_balance -= value
            game.players[game.field[game.cp.cur_coord]["owned_by"]].cur_balance += value
    if game.cp.cur_coord in [2, 17]:
        print('chest.')
        get_event_card('chest')
    if game.cp.cur_coord in [7, 34]:
        print('chance.')
        get_event_card('chance')
    pay_taxes()  # Заплотить нологе


def auction():
    print('аукцион.')


def throw_a_die():
    # Бросить кубики
    return random.randint(1, 6), random.randint(1, 6)


def move_player(dies: int = 0):
    game.cp.last_coord = game.cp.cur_coord  # Сохраняем его предыдущуюю координату
    game.cp.cur_coord += dies  # Перемещаем игрока на сумму, выпавшую на кубиках


def new_lap():
    game.cp.cur_coord = game.cp.cur_coord - game.cells
    # Начинаем новый круг
    if game.cp.cur_coord == 0:  # Если игрок остановился на ячейке "Старт"
        pay_salary(400)  # Начисляем зарплату 400
    else:  # Иначе, зарплата 200
        pay_salary(200)


def make_move():
    # Сделать шаг
    f_die, s_die = throw_a_die()
    print('Бросаю кубики...', end=' ')
    print(f'На кубиках выпало {f_die} и {s_die}.')
    if f_die == s_die:  # Если выпал дубль
        print('Какая неожиданность! Дубль дает вам право ходить еще раз.')
        game.cp.takes += 1  # Добавляем единицу в счетчик
        print(f'{game.cp.takes=}')
        print(f'{game.cp.cur_coord=}')
        move_player(f_die + s_die)
        print(f'{game.cp.cur_coord=}')
        move_actions()
    else:  # Если цепочка дублей нарушилась
        game.cp.takes = 0  # Обнуляем счетчик дублей
    if game.cp.takes == 3:  # Если количество дублей равно 3
        go_to_jail()  # Отправляем игрока в тюрьму
    if not game.cp.in_jail:  # Если игрок не в тюрьме
        move_player(f_die + s_die)
        if game.cp.cur_coord == 30:  # Если игрок попал на ячейку "Отправляйся в тюрьму"
            go_to_jail()  # Отправляем его в тюрьму
        if game.cp.cur_coord > game.cells:  # Если координата игрока больше количества ячеек
            new_lap()


def complete_move():
    print(f'Ход игрока {game.cp.name} завершен.')
    print('---')
    game.current_player += 1
    if game.current_player == game.number_of_players:
        game.current_player = 0
    game.cp = game.players[game.current_player]


def pay_salary(value: int):
    # Зарплата за прохождение круга
    if game.cp.last_coord > game.cp.cur_coord:  # Если игрок
        # закончил круг (предыдущая координата больше текущей)
        print(f'Вы завершили круг. Получите зарплату в размере {value}{game.currency}')
        game.cp.cur_balance += value


def pay_taxes():
    if game.cp.cur_coord == 4:  # Если игрок попал на ячейку "Подоходный налог"
        print('Вы попали на клетку с налогами.')
        print(f'Подоходный налог. С вашего счета списано 200{game.currency}')
        game.cp.cur_balance -= 200
    if game.cp.cur_coord == 38:  # Если игрок попал на ячейку "Налог на роскошь"
        print('Вы попали на клетку с налогами.')
        print(f'Налог на роскошь. С вашего счета списано 100{game.currency}')
        game.cp.cur_balance -= 100


def property_management():
    pass


def get_event_card(_type: str):
    pass


def prompt(msg: str):
    resp = input(f'{msg} [Д/Н]:\n> ').lower()
    if resp == 'д':
        return True
    return False


def recognize_bankruptcy():
    # Признать банкротство
    if prompt('Вы действительно хотите сдаться?'):  # Подтверждение
        print('Серьёзно? Ну хорошо, ваше право...')
        print(f'Удаление игрока {game.cp.name}.chr')  # Отсылочка для знающих :)
        game.players.pop(game.current_player)
    else:
        print('Не пугайте меня так!')


def go_to_jail():
    print('Вы попали в тюрьму и пропускаете три своих хода.')
    game.cp.takes = 0  # Обнуляем счетчик дублей
    game.cp.in_jail = True  # Поместить игрока в тюрьму (логически)
    game.cp.last_coord = game.cp.cur_coord
    game.cp.cur_coord = 10  # Помесить игрока в тюрьму (практически)
    game.cp.left_in_jail = 3  # Начислить три хода заключения


if __name__ == '__main__':
    try:
        game = Base()
        start_new_game()
        while len(game.players) > 1:
            start_move()
    except KeyboardInterrupt:
        print('Игра завершена без сохранения прогресса.')
    else:
        try:
            print(f'Игрок {game.players[0].name} одержал победу. Поздравляем!')
        except IndexError:
            pass
else:
    print('Игра требует запуска как отдельный файл.')
    game = None
