import json
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import Todo
from django.core.paginator import Paginator

 
##------READ ops-------
def index(request):
    """"
    Renders the main page with the list of Todos
    """
    todos = Todo.objects.all().order_by('-created_at')

    ## Pagination - Showing 5 todos per page
    paginator = Paginator(todos,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'todos/index.html', {'page_obj': page_obj},status=200)

#--------HELPER--------
def get_request_data(request):
    """
    Retrieves form data from request.POST (for POST)
    or parses raw body data (for PUT/PATCH)
    """
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}
    

# ---------READ HISTORY-------
@require_http_methods(['GET'])
def todo_history(request, pk):
    todo = Todo.objects.get(pk=pk)
    # Order by newest first
    history_qs = todo.history.all().order_by('-timestamp') 
    
    # 1. Paginate (5 items per 'page')
    paginator = Paginator(history_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'todo': todo,
        'history': page_obj, # Pass the page object, not the raw list
    }

    # 2. Logic: If HTMX is asking, send ONLY the list items (the partial).
    #    Otherwise, send the full modal.
    if request.htmx and 'page' in request.GET:
        return render(request, 'todos/partials/history_list_items.html', context)
    
    return render(request, 'todos/partials/history_list.html', context)

#------CREATE-----
@require_http_methods(['POST'])
def add_todo(request):
    """
    Creates a new todo
    Returns the new list item HTML to be appended to the list
    """
    data = get_request_data(request)
    title = data.get('title')
    description = data.get('description') ###Capture the description
    print(title,description)
    if title:
        # 1.Creating the todo
        Todo.objects.create(title=title,description=description)

        # 2.Re-fetching the list
        todos = Todo.objects.all().order_by('-created_at')

        # 3. Paginating it
        paginator = Paginator(todos,5)
        page_obj = paginator.get_page(1)
        # Render the new list again
        return render(request,'todos/partials/todo_list.html',{'page_obj':page_obj},status=201)
    
   # Return 400 if title is missing
    return HttpResponse("Title is required",status=400)              


#----UPDATE(Edit Content)------

@require_http_methods(['GET', 'PUT'])  
def update_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'PUT':
        # 1. Parse JSON data from the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}  # Handle empty or invalid JSON

        # 2. Update fields
        # Note: We use .get() on the dictionary 'data', not request.POST
        todo.title = data.get('title')
        todo.description = data.get('description')
        
        # 3. Validation and Save
        if todo.title:
            todo.save()
            return render(request, 'todos/partials/todo_item.html', {'todo': todo})
        else:
            # Handle validation error (optional but good practice)
            return HttpResponse("Title is required", status=400)
    
    # GET request: Return the form populated with existing data
    return render(request, 'todos/partials/todo_form.html', {'todo': todo})
 
@require_http_methods(['PATCH'])
def toggle_todo(request, pk):
    """
    API to toggle the 'is_completed' status
    Returns the updated list item in HTML
    """
    todo = get_object_or_404(Todo,pk=pk)
    todo.is_completed = not todo.is_completed
    todo.save()

    return render(request,'todos/partials/todo_item.html',{'todo':todo},status=200)
 

#--------------------------DELETE
@require_http_methods(['DELETE'])
def delete_todo(request,pk):
    """
    Deletes a todo and returns the updated list(refilled from next page)
    """
    
    # 1.Delete the item
    todo = get_object_or_404(Todo,pk=pk)
    todo.delete()

    # 2. Get the current page number from the request(so we stay on same page)
    # Default to 1 if not provided
    page_number = request.GET.get('page',1)

    # 3.Refetch the list
    todos = Todo.objects.all().order_by('-created_at')
    paginator = Paginator(todos,5)
    
    # 3.Get current page object
    page_obj = paginator.get_page(page_number)

    # 4. Return the List Component
    return render(request,'todos/partials/todo_list.html',{'page_obj':page_obj},status=200)
