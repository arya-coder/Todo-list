from django.apps import AppConfig


class TodosConfig(AppConfig):
    name = 'todos'


    def ready(self):
        import todos.signals