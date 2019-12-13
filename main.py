import random


class Player:
    def __init__(self, name: str):
        self.base_coord = 0  # Начальная координата
        self.last_coord = 0  # Предыдущая координата
        self.cur_coord = 0  # Текущая координата
        self.base_balance = 1500  # Начальный баланс
        self.cur_balance = 1500  # Текущий баланс

        self.name = name

        self.start_score = throw_a_die(1)
        self.takes = 0

        self.in_jail = False
        self.left_in_jail = 0


class Base:
    def __init__(self):
        self.players = []
        self.current_player = 0
        self.cells = 39


def start_new_game():
    print('*********\nMONOPOLY\n*********\n')
    number_of_players = int(input('Введите количество игроков:\n> '))
    for i in range(number_of_players):
        game.players.append(Player(name=input(f'Введите имя игрока {i+1}: ')))


def start_move():
    print(f'Сейчас ход игрока {game.players[game.current_player].name}.')
    if game.players[game.current_player].in_jail:
        print('Вы в тюрьме и не можете сделать ход.')
        game.players[game.current_player] -= 1
        if game.players[game.current_player].left_in_jail == 0:
            print('Вы вышли из тюрьмы.')
            game.players[game.current_player].in_jail = False
            start_move()
    else:
        bankrupt = False
        if game.players[game.current_player].cur_balance <= 0:
            print('Вы банкрот, голубчик!')
            bankrupt = True
        print(f'Выберите действие:\n')
        if not bankrupt:
            print('1 – Бросить кубик')
        print('2 – Управление недвижимостью')
        print('3 – Признать банкротство')
        move = input(input('> '))
        if move == 1 and not bankrupt:
            make_move()
        elif move == 2:
            property_management()
        elif move == 3:
            recognize_bankruptcy()
        else:
            print('Введите число от 1 до 3!')
            start_move()


def throw_a_die(dies: int = 2):
    if dies == 1:
        return random.randint(1, 6)
    return random.randint(1, 6), random.randint(1, 6)


def make_move():
    f_die, s_die = throw_a_die()
    if f_die == s_die:
        game.players[game.current_player].takes += 1
    else:
        game.players[game.current_player].takes = 0
    if game.players[game.current_player].takes == 3:
        go_to_jail()
        game.players[game.current_player].takes = 0
    if not game.players[game.current_player].in_jail:
        game.players[game.current_player].last_coord = game.players[game.current_player].cur_coord
        game.players[game.current_player].cur_coord = f_die + s_die
        if game.players[game.current_player].cur_coord > game.cells:
            game.players[game.current_player].cur_coord = game.players[game.current_player].cur_coord - game.cells
            if game.players[game.current_player].cur_coord == 0:
                pay_salary(400)
            else:
                pay_salary(200)
        pay_taxes()


def move_events():



def pay_salary(value: int):
    if game.players[game.current_player].last_coord > game.players[game.current_player].cur_coord:
        print(f'Вы завершили круг. Получите зарплату в размере {value}₩')
        game.players[game.current_player].cur_balance += value


def pay_taxes():
    print('Вы попали на клетку с налогами.')
    if game.players[game.current_player].cur_coord == 4:
        print('Подоходный налог. С вашего счета списано 200₩')
        game.players[game.current_player].cur_balance -= 200
    if game.players[game.current_player].cur_coord == 38:
        print('Налог на роскошь. С вашего счета списано 100₩')
        game.players[game.current_player].cur_balance -= 100


def property_management():
    pass


def recognize_bankruptcy():
    print('Вы действительно хотите сдаться? [Д/Н]')
    if input().lower() == 'д':
        print('Серьёзно? Ну хорошо, ваше право...')
        print(f'Удаление игрока {game.players[game.current_player].name}.chr')
        game.players.pop(game.current_player)


def go_to_jail():
    print('Вы попали в тюрьму и пропускаете три своих хода.')
    game.players[game.current_player].in_jail = True
    game.players[game.current_player].left_in_jail = 3


if __name__ == '__main__':
    game = Base()
    start_new_game()
    while len(game.players) > 1:
        start_move()
