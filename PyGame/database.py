import sqlite3


class Database:  # Класс для базы данных.
    def __init__(self):  # Инициализирует подключение к базе данных и создает таблицы, если они не существуют.
        self.conn = sqlite3.connect('game_stats.db')
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):  # Создает таблицы для хранения статистики игровых сессий и общей статистики.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                врагов_убито INTEGER,
                потерянно_жизней INTEGER,
                смертей_от_врага INTEGER,
                смертей_от_воды INTEGER,
                результат_игры TEXT,
                причина_поражения TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS overall_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                всего_врагов_убито INTEGER DEFAULT 0,
                всего_побед INTEGER DEFAULT 0,
                всего_поражений INTEGER DEFAULT 0,
                всего_поражений_из_за_жизний INTEGER DEFAULT 0,
                всего_поражений_из_за_потери_эмблемы INTEGER DEFAULT 0,
                всего_очков INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('SELECT COUNT(*) FROM overall_stats')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO overall_stats DEFAULT VALUES')

        self.conn.commit()

    def load_total_points(self):  # Загружает общее количество очков из базы данных.
        self.cursor.execute('SELECT всего_очков FROM overall_stats')
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def save_game_session(self, enemies_killed, lives_lost, lost_due_to_enemy, lost_due_to_water, game_result,
                          lose_reason):  # Сохраняет данные текущей игровой сессии в базу данных.
        self.cursor.execute('''
            INSERT INTO game_sessions (врагов_убито, потерянно_жизней, смертей_от_врага, смертей_от_воды, результат_игры, причина_поражения)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (enemies_killed, lives_lost, lost_due_to_enemy, lost_due_to_water, game_result, lose_reason))

        if game_result == "win":
            self.cursor.execute('UPDATE overall_stats SET всего_побед = всего_побед + 1')
        else:
            self.cursor.execute('UPDATE overall_stats SET всего_поражений = всего_поражений + 1')
            if lose_reason == "no_lives":
                self.cursor.execute(
                    'UPDATE overall_stats SET всего_поражений_из_за_жизний = всего_поражений_из_за_жизний + 1')
            elif lose_reason == "base_destroyed":
                self.cursor.execute(
                    'UPDATE overall_stats SET всего_поражений_из_за_потери_эмблемы = всего_поражений_из_за_потери_эмблемы + 1')

        self.cursor.execute('UPDATE overall_stats SET всего_врагов_убито = всего_врагов_убито + ?', (enemies_killed,))
        self.conn.commit()

    def update_total_points(self, total_points):  # Обновляет общее количество очков в базе данных.
        self.cursor.execute('UPDATE overall_stats SET всего_очков = ?', (total_points,))
        self.conn.commit()

    def close(self):  # Закрывает соединение с базой данных.
        self.conn.close()
