from telebot.types import User as TUser

users = {}


class TelegramUser:
    languages = [
        'en',
        'fa',
    ]
    flows = []
    errors = 0

    def __init__(self, data: TUser):
        self.id = data.id
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.full_name = data.full_name
        self.username = data.username

        if data.language_code in self.languages:
            self.language_code = data.language_code
        else:
            self.language_code = 'en'

        self.can_start_flow = True
        users[self.id] = self
        self.db = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'language_code': self.language_code,
        }

    def set_language(self, language_code):
        self.language_code = language_code
        users[self.id] = self

    def allow_flow(self, flow):
        self.flows.remove(flow)
        users[self.id] = self

    def allow_flows(self):
        self.flows = []
        users[self.id] = self

    def stop_flow(self, flow):
        self.flows.append(flow)
        users[self.id] = self

    def add_error(self):
        self.errors += 1
        users[self.id] = self

    def __str__(self):
        return f'[User {self.id} - {self.first_name} - {self.can_start_flow}]'
