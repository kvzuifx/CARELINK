from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated: #cannot go to login page if im already logged in
                 return redirect('main1')
            else:
                return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            print('working',allowed_roles)
            group = None
            user = User.objects.get(username='cureus')
            groups = user.groups.all()
            for group in groups:
                 print(group.name)
            if request.user.groups.exists():
                group = None
                for group in request.user.groups.all():
                   if group.name == 'admin':
                    group = group.name
                    break
                else:
        # 'else' block executes when the loop completes without a 'break'
        # Assign the name of the first group to admin_group
                    group = request.user.groups.all()[0].name #its 1 not 0 
            if group in allowed_roles:
                    return  view_func(request, *args, **kwargs)
            else:
                # return  HttpResponse(f'you are not authorized ro view this page, because you belong to {group}')
                return redirect('user-page')
        return wrapper_func
    return decorator 

def mainsd(request):
    def wrapper_func(request, *args, **kwargs):
          print("follow",request.user.groups.all())
    return wrapper_func

# def admin_only(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             print('working',allowed_roles)
#             group = None
#             user = User.objects.get(username='kvzui1')
#             groups = user.groups.all()
#             for group in groups:
#                  print(group.name)
#             if request.user.groups.exists():
#                 group = None
#                 for group in request.user.groups.all():
#                    if group.name == 'admin':
#                     group = group.name
#                     break
#                 else:
#         # 'else' block executes when the loop completes without a 'break'
#         # Assign the name of the first group to admin_group
#                     group = request.user.groups.all()[0].name #its 1 not 0 
#             if group in allowed_roles:
#                     return  view_func(request, *args, **kwargs)
#             else:
#                 return  HttpResponse(f'you are not authorized ro view this page, because you belong to {group}')
#         return wrapper_func

def mainsd(request):
    def wrapper_func(request, *args, **kwargs):
          print("follow",request.user.groups.all())
    return wrapper_func
