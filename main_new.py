import random

import data
from classes import Base, Player


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
    return f'====\nХод игрока {game.cp.name}.\nСостояние счёта: {game.cp.cur_balance}{game.currency}.\n' \
           f'Позиция: {game.field[game.cp.cur_coord]["name"]}.\n===='


def start_move():
    bankrupt = False
    if game.cp.cur_balance <= 0:
        bankrupt = True
        print('Вы банкрот!')
    if game.cp.in_jail:
        print('Вы находитесь тюрьме и не можете ходится.')
        if game.cp.escape_card:
            print('Вы можете использовать карточки побега.')
            if prompt('Использовать?'):
                


if __name__ == '__main__':
    try:  # Пробуй
        game = Base()  # Создать экземпляр игры
        start_new_game()  # Начать новую игру
        while len(game.players) > 1:  # Пока количество игроков больше единицы
            print(player_info())  # Выведи информацию о текущем игроке
            start_move()  # Начинай новый ход
    except KeyboardInterrupt:  # Если игры принудительно завершена на ^C
        print('\nИгра завершена без сохранения прогресса.')
    else:  # Если игра завершилась без ошибки остановки
        try:  # Пробуй вывести
            print(f'Игрок {game.players[0].name} одержал победу. Поздравляем!')  # Поздравление
        except IndexError:  # Если возбудилось исключение IndexError (игрока с нулевым индексом не существует,
            # такое может быть, например, если игра была остановлена во время создания игроков)
            pass  # Ничего не выводи
