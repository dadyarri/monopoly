import random

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
    if game.cp.in_jail and game.cp.cur_coord == 10:
        state = ' (как заключенный)'
    elif not game.cp.in_jail and game.cp.cur_coord == 10:
        state = ' (как посетитель)'
    else:
        state = ''
    print('====')
    print(f'Ход игрока {game.cp.name}.')
    print(f'Состояние счёта: {game.cp.cur_balance}{game.currency}.')
    print(f'Позиция: {game.field[game.cp.cur_coord]["name"]}{state}.')
    print(f'====')


def start_move():
    bankrupt = False
    if game.cp.cur_balance <= 0:
        bankrupt = True
        print('Вы банкрот!')
    if game.cp.in_jail:
        print('Вы находитесь в тюрьме и не можете ходиться.')
        if game.cp.escape_card:  # Если карточек нет (то есть это свойство равно 0), то условие не сработает
            print('Вы можете использовать карточки побега.')  # Можно получить среди карточек "Казна" или "Шанс"
            if prompt('Использовать?'):
                game.cp.escape_card -= 1
                game.cp.in_jail = False
                game.cp.left_in_jail = 0
                start_move()
        print('Вы можете попробовать сбежать из тюрьмы, если на кубиках выпадет дубль.')
        if prompt('Пробуем?'):
            f_die, s_die = throw_a_die()
            if f_die == s_die:
                print('У вас получилось сбежать!')
                game.cp.in_jail = False
                game.cp.left_in_jail = 0
                start_move()
            else:
                add = random.randint(1, 3)
                print(f'К сожалению вас поймали и дали дополнительный срок в {add} хода/ов.')
                game.cp.left_in_jail += add
        else:
            game.cp.left_in_jail -= 1  # Вычитаем один ход из его заключения
        if game.cp.left_in_jail != 0:  # Если заключение еще не прошло
            print(f'Вам осталось провести в тюрьме {game.cp.left_in_jail} хода/ов.')
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


def complete_move():
    pass


def make_move():
    # Бросаем кубики
    f_die, s_die = throw_a_die()
    # Смещаем фишку игрока
    print(f'На кубиках выпало {f_die} и {s_die}.')
    # Выполняем действия карточки
    move_actions()
    if f_die == s_die:
        # Выпал дубль, делаем еще один ход
        game.cp.takes += 1
        if game.cp.takes == 3:
            go_to_jail()
        else:
            make_move()
    else:
        game.cp.takes = 0
    # Завершаем ход
    complete_move()


def manage_property():
    pass


def recognize_bankruptcy():
    # Признать банкротство
    if prompt('Вы действительно хотите сдаться?'):  # Подтверждение
        print('Серьёзно? Ну хорошо, ваше право...')
        print(f'Удаление игрока {game.cp.name}.chr')  # Отсылочка для знающих :)
        game.players.pop(game.current_player)
    else:
        print('Не пугайте меня так!')


def go_to_jail():
    # Отправляем игрока в тюрьму
    game.cp.takes = 0  # Сбрасываем счетчик дублей
    game.cp.in_jail = True  # Логически отправляем игрока в тюрьму
    game.cp.left_in_jail = 3  # Начисляем ходы в заключении
    game.cp.cur_coord = 10  # Физически отправляем игрока в тюрьму


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
    pass


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
    except KeyboardInterrupt:  # Если игры принудительно завершена на ^C
        print('\nИгра завершена без сохранения прогресса.')
    else:  # Если игра завершилась без ошибки остановки
        print(f'Игрок {game.players[0].name} одержал победу. Поздравляем!')  # Поздравление
