from data import field

from main import throw_a_die


# Базовый класс, описывающий игровую сессию
class Base:
    def __init__(self):
        self.field = field  # Берет разметку игрового поля из файла data.py
        self.players = []  # Список с объектами игроков
        self.current_player = 0  # Номер текущего игрока
        self.cells = 39  # Количество ячеек на поле
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

        self.name = name  # Отображаемое имя

        self.start_score = sum(throw_a_die())  # Начальный бросок кубика
        self.takes = 0  # Дублей выпало

        self.in_jail = False  # Игрок в тюрьме?
        self.left_in_jail = 0  # Ходов осталось провести в тюрьме
        self.escape_card = 0  # Карточки освобождения из тюрьмы ("Казна" или "Шанс")
