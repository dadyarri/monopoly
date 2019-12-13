import random


# Базовый класс, опиывающий игровую сессию
class Base:
    def __init__(self):
        self.players = []  # Список с объектами игроков
        self.current_player = 0  # Номер текущего игрока
        self.cells = 39  # Количество ячеек на поле
        self.number_of_players = 0   # Количество игроков


# Класс, описывающий игрока, его позицию на поле, баланс, нахождение в тюрьме
class Player:
    def __init__(self, name: str):
        self.base_coord = 0  # Начальная координата
        self.last_coord = 0  # Предыдущая координата
        self.cur_coord = 0  # Текущая координата
        self.base_balance = 1500  # Начальный баланс
        self.cur_balance = 1500  # Текущий баланс

        self.name = name  # Отображаемое имя

        self.start_score = throw_a_die(1)  # Начальный бросок кубика
        self.takes = 0  # Дублей выпало

        self.in_jail = False  # Игрок в тюрьме?
        self.left_in_jail = 0  # Ходов осталось провести в тюрьме


def start_new_game():
    # Начало новой игры
    print('*********\nMONOPOLY\n*********\n')
    game.number_of_players = int(input('Введите количество игроков:\n> '))
    for i in range(game.number_of_players):
        game.players.append(Player(name=input(f'Введите имя игрока {i+1}: ')))


def start_move():
    # Начало хода
    print(f'Сейчас ход игрока {game.players[game.current_player].name}.')
    if game.players[game.current_player].in_jail:
        # Если игрок в тюрьме
        print('Вы в тюрьме и не можете сделать ход.')
        game.players[game.current_player] -= 1  # Вычитаем один ход из его заключения
        if game.players[game.current_player].left_in_jail == 0:  # Если время заключения прошло
            print('Вы вышли из тюрьмы.')
            game.players[game.current_player].in_jail = False  # Освобождаем игрока
            start_move()  # И даем возможность сходиться
    else:
        bankrupt = False
        if game.players[game.current_player].cur_balance <= 0:  # Если баланс игрока меньше или равен нулю, тогда
            print('Вы банкрот, голубчик!')
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
        else:
            if move == 1 and not bankrupt:  # Бросить кубики
                make_move()
            elif move == 2:  # Начать управление недвижимостью
                property_management()
            elif move == 3:  # Сдаться
                recognize_bankruptcy()
            else:  # Неизвестная команда
                print('Введите число от 1 до 3!')
                start_move()


def throw_a_die(dies: int = 2):
    # Бросить кубики (по умолчанию бросается два кубика)
    if dies == 1:
        return random.randint(1, 6)
    return random.randint(1, 6), random.randint(1, 6)


def make_move():
    # Сделать шаг
    f_die, s_die = throw_a_die()
    print(f'На кубиках выпало {f_die} и {s_die}.')
    if f_die == s_die:   # Если выпал дубль
        print('Какая неожиданность! Дубль дает вам право ходить еще раз.')
        game.players[game.current_player].takes += 1  # Добавляем единицу в счетчик
    else:  # Если цепочка дублей нарушилась
        game.players[game.current_player].takes = 0  # Обнуляем счетчик дублей
    if game.players[game.current_player].takes == 3:  # Если количество дублей равно 3
        game.players[game.current_player].takes = 0  # Обнуляем счетчик дублей
        go_to_jail()  # Отправляем игрока в тюрьму
    if not game.players[game.current_player].in_jail:  # Если игрок не в тюрьме
        game.players[game.current_player].last_coord = game.players[game.current_player].cur_coord  # Сохраняем его
        # предыдущуюю координату
        game.players[game.current_player].cur_coord = f_die + s_die  # Перемещаем игрока на сумму, выпавшую на кубиках
        if game.players[game.current_player].cur_coord > game.cells:  # Если координата игрока больше количества ячеек
            game.players[game.current_player].cur_coord = game.players[game.current_player].cur_coord - game.cells
            # Начинаем новый круг
            if game.players[game.current_player].cur_coord == 0:  # Если игрок остановился на ячейке "Старт"
                pay_salary(400)  # Начисляем зарплату 400
            else:   # Иначе, зарплата 200
                pay_salary(200)
        pay_taxes()  # Заплатить налоги
    if f_die == s_die and not game.players[game.current_player].in_jail:
        make_move()


def pay_salary(value: int):
    # Зарплата за прохождение круга
    if game.players[game.current_player].last_coord > game.players[game.current_player].cur_coord:  # Если игрок
        # закончил круг (предыдущая координата больше текущей)
        print(f'Вы завершили круг. Получите зарплату в размере {value}₩')
        game.players[game.current_player].cur_balance += value


def pay_taxes():
    # Если игрок попал на клетку с налогами
    if game.players[game.current_player].cur_coord == 4 or game.players[game.current_player].cur_coord == 38:
        print('Вы попали на клетку с налогами.')
    if game.players[game.current_player].cur_coord == 4:  # Если игрок попал на ячейку "Подоходный налог"
        print('Подоходный налог. С вашего счета списано 200₩')
        game.players[game.current_player].cur_balance -= 200
    if game.players[game.current_player].cur_coord == 38:   # Если игрок попал на ячейку "Налог на роскошь"
        print('Налог на роскошь. С вашего счета списано 100₩')
        game.players[game.current_player].cur_balance -= 100


def property_management():
    pass


def recognize_bankruptcy():
    # Признать банкротство
    print('Вы действительно хотите сдаться? [Д/Н]')
    if input().lower() == 'д':  # Подтверждение
        print('Серьёзно? Ну хорошо, ваше право...')
        print(f'Удаление игрока {game.players[game.current_player].name}.chr')  # Отсылочка для знающих :)
        game.players.pop(game.current_player)


def go_to_jail():
    print('Вы попали в тюрьму и пропускаете три своих хода.')
    game.players[game.current_player].in_jail = True  # Поместить игрока в тюрьму (логически)
    game.players[game.current_player].last_coord = game.players[game.current_player].cur_coords
    game.players[game.current_player].cur_coord = 10   # Помесить игрока в тюрьму (практически)
    game.players[game.current_player].left_in_jail = 3  # Начислить три хода заключения


if __name__ == '__main__':
    game = Base()
    start_new_game()
    while len(game.players) > 1:
        start_move()
    print(f'Игрок {game.players[0].name} одержал победу. Поздравляем!')
