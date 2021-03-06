from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category
from rango.models import Page
from rango.models import User, UserProfile

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from datetime import datetime
from django.views.generic.edit import FormView
from .bing_search import run_query, read_bing_key
from registration.backends.simple.views import RegistrationView
from django.urls import reverse


class MyRegistrationView(RegistrationView):

    def get_success_url(self, user=None):
        return reverse('register_profile/')


def get_server_side_cookie(request, cookie, default_val = None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visits_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visits_time = datetime.strptime(last_visits_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visits_time).seconds > 10:
        visits +=1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] =  last_visits_cookie
    request.session['visits'] =  visits


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupkake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']
    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Yauheni',
                    'last_visit':request.session['last_visit']}
    return render(request, 'rango/about.html', context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    query=''
    result_list =[]
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    context_dict.update({'result_list':result_list, 'query':query})
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)[:5]
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
    return render(request, 'rango/category.html', context_dict)


@login_required()
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required()
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

"""
def register(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('You Rango account is disabled')
        else:
            print(f'Invalid login details: {username} {password}')
            return render(request, 'rango/login.html',
                          {'error_message': 'Invalid username and/or password entered. Try again'})
    else:
        return render(request, 'rango/login.html', {})


@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
"""

@login_required()
def restricted(request):
    return HttpResponse('Since you are logged in, you can see that text !')

def goto_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id = page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)

"""
def search(request):
    query=''
    result_list =[]
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list':result_list, 'query':query})
"""

@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('index')
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)

@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)
    return render(request, 'rango/profile.html', {'userprofile':userprofile, 'user':user, 'form':form})

def profile_list(request):
    profiles = User.objects.all()
    profile_name = [profile.username for profile in profiles]
    print(profile_name)
    return render(request, 'rango/profile_list.html', {'profile_name':profile_name})

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

def get_category_list(max_results = 0, starts_with = ''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(cat_list)>max_results:
            cat_list = cat_list[:max_results]
    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    if len(cat_list) == 0:
        cat_list = Category.objects.order_by('-likes')
    return render(request, 'rango/cats.html', {'cats': cat_list})

@login_required
def auto_add_page(request):
    cat_id = None
    title = None
    url = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category,
                                       title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
        # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)