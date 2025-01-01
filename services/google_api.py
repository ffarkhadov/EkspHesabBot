# services/google_api.py

import gspread
from datetime import datetime

class GoogleSheetsService:
    def __init__(self, creds_file: str, spreadsheet_id: str):
        self.creds_file = creds_file
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None

        # Кэш пользователей
        self.users_cache = {}

    def authorize(self):
        print(">>> [GoogleSheetsService] Авторизация...")
        self.client = gspread.service_account(filename=self.creds_file)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        print(">>> [GoogleSheetsService] Авторизация успешна!")

    def load_users(self):
        """
        Считываем вкладку 'Users' и кладём данные в self.users_cache:
         { user_id_int: {
              'username': ...,
              'role': ...,
              'store_name': ...,
              'region': ...,
              'phone': ...,
              'location': ...,
              'is_active': True/False,
              'date_added': ...
           },
           ...
         }
        """
        print(">>> [GoogleSheetsService] Загрузка пользователей из 'Users'...")
        ws = self.spreadsheet.worksheet("Users")
        data = ws.get_all_records()
        temp_dict = {}
        for row in data:
            user_id = row.get("user_id")
            if user_id:
                try:
                    user_id_int = int(user_id)
                    temp_dict[user_id_int] = row
                except ValueError:
                    print(f"!!! [GoogleSheetsService] Некорректный user_id: {user_id}")
        self.users_cache = temp_dict
        print(f">>> [GoogleSheetsService] Загружено пользователей: {len(self.users_cache)}")

    def add_buyer(self, user_id: int, username: str, store_name: str, region: str, phone: str):
        """
        Записываем новую строку в Google Sheets для buyer:
         user_id | username | role    | store_name | region | phone | location | is_active | date_added
        """
        ws = self.spreadsheet.worksheet("Users")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            user_id,
            username,
            "buyer",     # роль
            store_name,
            region,
            phone,
            "",          # location пока пустая
            True,        # is_active
            now_str      # date_added
        ]
        ws.append_row(row)
        # Обновляем кэш
        self.load_users()

    def set_inactive(self, user_id: int):
        """Пример: меняем is_active=False для указанного user_id, если нужно."""
        # Не обязательно, но можно показать, как редактировать
        pass
