# todos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main Page
    path('', views.index, name='index'),
    
    # GET /todos/1/history -> Sub resource
    path('todos/<int:pk>/history', views.todo_history, name='todo_history'),

    # POST/todos/-> Creating a new task
    path('todos/', views.add_todo, name='add_todo'),

    #PUT /todos/1 -> Update task (title/description)
    path('todos/<int:pk>/', views.update_todo, name='update_todo'),

    #PATCH /todos/1/toggle -> Toggle status (Partial update)
    path('todos/<int:pk>/toggle', views.toggle_todo, name='toggle_todo'),

    #DELETE /todos/1 -> Delete task
    path('todos/<int:pk>/delete', views.delete_todo, name='delete_todo'),
]