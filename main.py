# TODO: Дописать правила игры в README
# TODO: Написать аукцион (вызывается, если игрок не хочет или не может выкупить Собственность)
# TODO: Написать управление собственностью (аукцион; строительство; залог)

import random

from termcolor import colored

from data import field


# Базовый класс, описывающий игровую сессию
class Base:
    def __init__(self):
        self.field = field  # Берет разметку игрового поля из файла data.py
        self.players = []  # Список с объектами игроков
        self.current_player = 0  # Номер текущего игрока
        self.cells = 36  # Количество ячеек на поле
        self.number_of_players = 0  # Количество игроков
        self.currency = '₩'  # Символ валюты

        self.cp = None


# Класс, описывающий игрока, его позицию на поле, баланс, нахождение в тюрьме
class Player:
    def __init__(self, name: str):
        self.base_coord = 0  # Начальная координата
        self.last_coord = self.base_coord  # Предыдущая координата
        self.cur_coord = self.base_coord  # Текущая координата
        self.base_balance = 1500  # Начальный баланс
        self.cur_balance = self.base_balance  # Текущий баланс

        self.property = {}

        self.name = name  # Отображаемое имя

        self.start_score = sum(throw_a_die())  # Начальный бросок кубика
        self.takes = 0  # Дублей выпало

        self.in_jail = False  # Игрок в тюрьме?
        self.left_in_jail = 0  # Ходов осталось провести в тюрьме
        self.escape_card = 0  # Карточки освобождения из тюрьмы ("Казна" или "Шанс")


def start_new_game():
    # Начало новой игры
    print('*********\nMONOPOLY\n*********\n')
    try:
        game.number_of_players = int(input('Введите количество игроков:\n> '))  # Спрашиваем количество игроков (ожидая
    # при этом целое число)
    except ValueError:
        print('Ожидается целое число')
        start_new_game()
    else:
        for i in range(game.number_of_players):  # Создание профилей игроков в указанном количестве
            game.players.append(Player(name=input(f'Введите имя игрока {i + 1}: ')))
        # Сортировка игроков по убыванию стартовых очков (определение порядка хода, как в классической Монополии)
        for i in range(len(game.players)):
            # Исходно считаем наибольшим первый элемент
            index = i
            # Этот цикл перебирает несортированные элементы
            for j in range(i + 1, len(game.players)):
                if game.players[j].start_score > game.players[index].start_score:
                    index = j
            # Самый большой элемент меняем с первым в списке
            game.players[i], game.players[index] = game.players[index], game.players[i]
        # Вывод порядка хода
        print('Порядок хода игроков: ', end='')
        for i in range(len(game.players)):
            if i != len(game.players) - 1:  # Разделитель между игроками
                end = ', '  # Если сейчас выводится не последний игрок, тогда выведи после него запятую
            else:
                end = '\n'  # Иначе – новую строку
            print(f'{game.players[i].name}', end=end)
        # Создание алиаса для текущего игрока (зд.: первого, с индексом 0)
        game.cp = game.players[game.current_player]


def player_info():
    if game.cp.in_jail and game.cp.cur_coord == 10:
        state = ' (как заключенный)'
    elif not game.cp.in_jail and game.cp.cur_coord == 10:
        state = ' (как посетитель)'
    else:
        state = ''
    print('====')
    print(f'{colored("Ход игрока", attrs=["bold"])} {colored(game.cp.name, "magenta")}.')
    print(f'{colored("Состояние счёта:", attrs=["bold"])} {colored(game.cp.cur_balance, "magenta")}'
          f'{colored(game.currency, "magenta")}.')
    print(f'{colored("Позиция:", attrs=["bold"])} {colored(game.field[game.cp.cur_coord]["name"], "magenta")}'
          f'{colored(state, "magenta")}.')
    print(f'====')


def start_move():
    bankrupt = False
    if game.cp.cur_balance <= 0:  # Если баланс игрока меньше или равен нулю
        bankrupt = True  # Тогда признаем его банкротом
        print(colored('Вы банкрот!', 'red', attrs=['bold', 'blink']))
    if game.cp.in_jail:
        print('Вы находитесь в тюрьме и не можете ходиться.')
        if game.cp.escape_card:  # Если карточек нет (то есть это свойство равно 0), то условие не сработает
            print('Вы можете использовать карточки побега.')  # Можно получить среди карточек "Казна" или "Шанс"
            if prompt('Использовать?'):
                game.cp.escape_card -= 1
                game.cp.in_jail = False
                game.cp.left_in_jail = 0
                start_move()
        else:
            game.cp.left_in_jail -= 1  # Вычитаем один ход из его заключения
            if game.cp.left_in_jail != 0:  # Если заключение еще не прошло
                print(f'Вам осталось провести в тюрьме {game.cp.left_in_jail} хода/ов.')
                complete_move()
            else:  # Если время заключения прошло
                print('Вы вышли из тюрьмы.')
                game.cp.in_jail = False  # Освобождаем игрока
                game.cp.left_in_jail = 0
                start_move()  # И даем возможность сходиться
    else:
        print('Выберите действие:')
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
                        make_move()
                        complete_move()
                    elif move == 2:  # Начать управление недвижимостью
                        manage_property()
                        start_move()
                    elif move == 3:  # Сдаться
                        # Сдаёмся и удаляем профайл игрока
                        recognize_bankruptcy()
                else:  # Неизвестная команда
                    print('Введите число от 1 до 3!')
                    start_move()
            else:
                if move in [2, 3]:
                    if move == 2:  # Начать управление недвижимостью
                        manage_property()
                        start_move()
                    elif move == 3:  # Сдаться
                        pass
                else:  # Неизвестная команда
                    print('Введите число от 2 до 3!')
                    start_move()


def move_actions():
    print(f'Вы находитесь на ячейке {game.field[game.cp.cur_coord]["name"]} ('
          f'{game.field[game.cp.cur_coord]["category"]})')
    if game.field[game.cp.cur_coord]["owned_by"] is None and game.cp.cur_coord not in [0, 2, 4, 7, 10, 17, 20, 29, 34,
                                                                                       36]:
        # Если ячейка никому не принадлежит и если ячейка не служебная (т. е. её можно купить)
        if prompt(f'Предприятие никому не принадлежит. Хотите купить?\n'
                  f'Её стоимость: {game.field[game.cp.cur_coord]["price"]}{game.currency}\n'
                  f'У вас есть: {game.cp.cur_balance}{game.currency}'):  # Предлагаем игроку купить эту карточку
            if game.field[game.cp.cur_coord]["price"] < game.cp.cur_balance:  # Если у игрока достаточно денег
                game.field[game.cp.cur_coord]["owned_by"] = game.current_player  # Покупаем
                game.cp.cur_balance -= game.field[game.players[
                    game.current_player].cur_coord]["price"]
                game.cp.property.setdefault(game.field[game.cp.cur_coord]['category'])
                try:
                    _f = bool(len(game.cp.property.setdefault(game.field[game.cp.cur_coord]['category'])))
                except TypeError:
                    game.cp.property[game.field[game.cp.cur_coord]['category']] = list()
                finally:
                    game.cp.property[game.field[game.cp.cur_coord]['category']].append(game.field[game.cp.cur_coord])
                print(f'Успех! Предприятие {game.field[game.cp.cur_coord]["name"]} теперь ваше!')
            else:
                print('У вас недостаточно средств для покупки этой карточки.')
                auction()
        else:
            auction()
    else:
        if game.field[game.cp.cur_coord]["owned_by"] is not None and game.field[game.cp.cur_coord]["owned_by"] != \
                game.current_player:  # Если ячейка принадлежит какому-то игроку
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
    if game.cp.cur_coord == 29:
        go_to_jail()
    pay_taxes()  # Заплотить нологе


def complete_move():
    print(f'Ход игрока {game.cp.name} завершен.')
    game.current_player += 1
    if game.current_player == game.number_of_players:
        game.current_player = 0
    game.cp = game.players[game.current_player]


def make_move():
    # Бросаем кубики
    f_die, s_die = throw_a_die()
    print(f'На кубиках выпало {f_die} и {s_die}.')
    # Смещаем фишку игрока
    game.cp.last_coord = game.cp.cur_coord
    game.cp.cur_coord += f_die + s_die
    if game.cp.cur_coord > game.cells:
        game.cp.cur_coord -= game.cells
        print(f'{game.cp.cur_coord}')
        if game.cp.cur_coord == 0:
            pay_salary(400)
        else:
            pay_salary(200)
    # Выполняем действия карточки
    move_actions()
    if f_die == s_die:
        # Выпал дубль, делаем еще один ход
        print(f'Какая неожиданность! У вас выпал {colored("дубль", attrs=["bold"])}. Дубль дает право на еще один ход.')
        game.cp.takes += 1  # Добавляем единицу к счетчику
        if game.cp.takes >= 3:  # Если количество дублей подряд достигло трех, то
            go_to_jail()  # Отправляем игрока в тюрьму
        else:  # Иначе
            make_move()  # Даем сходится еще раз
    else:  # Если цепчока дублей нарушилась, тогда обнуляем счетчик дублей
        game.cp.takes = 0


def manage_property():
    if not game.cp.property:
        print('У вас нет предприятий в собственности!')
    else:
        for k, v in game.cp.property.items():
            for i in range(len(v)):
                t = v[i]['name']
                print(f'{k}: {t}')


def recognize_bankruptcy():
    # Признать банкротство
    if prompt('Вы действительно хотите сдаться?'):  # Подтверждение
        print('Серьёзно? Ну хорошо, ваше право...')
        print(f'Удаление игрока {game.cp.name}.chr')  # Отсылочка для знающих :)
        game.players.pop(game.current_player)
        for i in range(len(game.field)):
            if game.field[i]['owned_by'] == game.current_player:
                game.field[i]['owned_by'] = None
        print('Собственность ушедшего игрока теперь принадлежит Банку.')
        complete_move()
    else:
        print('Не пугайте меня так!')


def go_to_jail():
    # Отправляем игрока в тюрьму
    print('Вы попали в тюрьму и должны пропустить три своих хода.')
    game.cp.takes = 0  # Сбрасываем счетчик дублей
    game.cp.in_jail = True  # Логически отправляем игрока в тюрьму
    game.cp.left_in_jail = 3  # Начисляем ходы в заключении
    game.cp.cur_coord = 10  # Физически отправляем игрока в тюрьму
    complete_move()


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


def get_event_card(_type: str):
    pass


def auction():
    print(colored('Аукцион!', 'yellow', attrs=['blink']))


def prompt(msg: str):
    resp = input(f'{msg} [Д/Н]:\n> ').lower()
    if resp == 'д':
        return True
    return False


def throw_a_die():
    # Бросить кубики
    return random.randint(1, 6), random.randint(1, 6)


if __name__ == '__main__':
    try:  # Пробуй
        game = Base()  # Создать экземпляр игры
        start_new_game()  # Начать новую игру
        while len(game.players) > 1:  # Пока количество игроков больше единицы
            player_info()  # Выведи информацию о текущем игроке
            start_move()  # Начинай новый ход
    except KeyboardInterrupt:  # Если игра принудительно завершена на ^C
        print('\nИгра завершена без сохранения прогресса.')
    else:  # Если игра завершилась без ручной остановки
        print(f'Игрок {game.players[0].name} одержал победу. Поздравляем!')  # Поздравление
