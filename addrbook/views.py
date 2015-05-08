from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction

from addrbook.models import Entry
from addrbook.forms import RegistrationForm, CreateForm, EditForm

from datetime import datetime

import time # for adding sleep calls to demonstrate concurrency issues

@login_required
def search(request):
    if not 'last' in request.GET:
        return render(request, 'addrbook/search.html', {})

    last = request.GET['last']
    objects = Entry.objects.filter(last_name__istartswith=last)

    if objects.count() == 0:
        message = 'No entries with last name = "{0}"'.format(last)
        return render(request, 'addrbook/search.html', {'message': message})

    if objects.count() > 1:
        context = { 'entries': objects.all() }
        return render(request, 'addrbook/list.html', context)

    entry = objects.all()[0]
    form = EditForm(instance=entry)
    context = { 'entry': entry, 'form': form }
    return render(request, 'addrbook/edit.html', context)

@login_required
def create(request):
    if request.method == 'GET':
        context = { 'form': CreateForm() }
        return render(request, 'addrbook/create.html', context)

    entry = Entry(created_by=request.user, creation_time=datetime.now(),
                  updated_by=request.user, update_time=datetime.now())
    create_form = CreateForm(request.POST, instance=entry)
    if not create_form.is_valid():
        context = { 'form': create_form }
        return render(request, 'addrbook/create.html', context)
   
    # Save the new record
    create_form.save()

    message = 'Entry created'
    edit_form = EditForm(instance=entry)
    context = { 'message': message, 'entry': entry, 'form': edit_form }
    return render(request, 'addrbook/edit.html', context)

@login_required
def delete(request, id):
    if request.method != 'POST':
        message = 'Invalid request.  POST method must be used.'
        return render(request, 'addrbook/search.html', { 'message': message })

    entry = get_object_or_404(Entry, id=id)
    entry.delete()
    message = 'Entry for {0}, {1} has been deleted.'.format(entry.last_name, entry.first_name)
    return render(request, 'addrbook/search.html', { 'message': message })

@login_required
@transaction.atomic
def edit(request, id):
    try:
        if request.method == 'GET':
            entry = Entry.objects.get(id=id)
            form = EditForm(instance=entry)
            context = { 'entry': entry, 'form': form }
            return render(request, 'addrbook/edit.html', context)
    
        entry = Entry.objects.select_for_update().get(id=id)
        db_update_time = entry.update_time  # Copy timestamp to check after form is bound
        form = EditForm(request.POST, instance=entry)
        if not form.is_valid():
            context = { 'entry': entry, 'form': form }
            return render(request, 'addrbook/edit.html', context)

        # if update times do not match, someone else updated DB record while were editing
        if db_update_time != form.cleaned_data['update_time']:
            # refetch from DB and try again.
            entry = Entry.objects.get(id=id)
            form = EditForm(instance=entry)
            context = {
                'message': 'Another user has modified this record.  Re-enter your changes.',
                'entry':   entry,
                'form':    form,
            }
            return render(request, 'addrbook/edit.html', context)

        # Set update info to current time and user, and save it!
        entry.update_time = datetime.now()
        entry.updated_by  = request.user
        form.save()

        # form = EditForm(instance=entry)
        context = {
            'message': 'Entry updated.',
            'entry':   entry,
            'form':    form,
        }
        return render(request, 'addrbook/edit.html', context)
    except Entry.DoesNotExist:
        context = { 'message': 'Record with id={0} does not exist'.format(id) }
        return render(request, 'addrbook/search.html', context)

@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'addrbook/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'addrbook/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))
    

