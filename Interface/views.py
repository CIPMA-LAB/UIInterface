import os
import re
import cv2
import joblib
import imghdr
import shutil
import urllib3
import validators
import numpy as np
from pathlib import Path
from keras.engine import Model
from keras_vggface import utils
from keras.preprocessing import image
from keras_vggface.vggface import VGGFace
from django.shortcuts import render, redirect
from Interface.forms import RegistrationForm
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
import keras.backend.tensorflow_backend as tb
media = 'Interface/media/'

def home(request):
    context = {}
    clear_folder()
    if request.method == 'POST':
        fs = FileSystemStorage()
        if(request.FILES):
            uploaded_file = request.FILES['photo']
            if (request.user.is_authenticated):
                name_original = fs.save('user/' + request.user.username + '/' + uploaded_file.name, uploaded_file)
            else:
                name_original = fs.save('saved/' + uploaded_file.name, uploaded_file)
        elif(request.POST.get('url')):
            url = request.POST.get('url')
            if not validators.url(url):
                context['error'] = 'Invalid URL'
                return render(request, 'mysite/home.html', context)
            name = re.sub('[^\w\.!@#$^+=-]', '_', url.split('/')[-1]);
            http = urllib3.PoolManager()
            if (request.user.is_authenticated):
                name_original = ('user/' + request.user.username + '/' + name)
            else:
                name_original = ('saved/' + name)
            with http.request('GET', url, preload_content=False) as resp, open(media + name_original.split('/')[0] + '/' + request.user.username + '/' + name, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
            resp.release_conn()
        else:
            context['error'] = 'Please Input File or URL'
            return render(request, 'mysite/home.html', context)
        if (imghdr.what(media + name_original) == None):
            context['error'] = 'Invalid File Format'
            return render(request, 'mysite/home.html', context)
        image_size = fs.size(name_original)/1024
        context['url'] = fs.url(name_original)
        context['image_url'] = '/media/processed/'
        context['image_detected'] = '/media/processed/temp_detected.jpg'
        context['image_size'] = str(round(image_size, 2)) + ' KB'
        context['image_name'] = name_original.split('/')[-1]
        return render(request, 'mysite/home.html', context)
    else:
        return render(request, 'mysite/home.html')

def history(request):
    fs = FileSystemStorage()
    if request.method == 'POST':
        for file in fs.listdir('user/' + request.user.username + '/')[1]:
            fs.delete('user/' + request.user.username + '/' + file)
    context = {}
    path = media + 'user/' + request.user.username + '/'
    Path(path).mkdir(parents=True, exist_ok=True)
    img_list = os.listdir(path)
    images = [[0 for x in range(6)] for y in range(len(img_list))]
    for idx,image in enumerate(img_list):
        images[idx][0] = fs.url('user/' + request.user.username + '/' + image)
        images[idx][1] = image.split('/')[-1]
        images[idx][2] = str(round(fs.size('user/' + request.user.username + '/' + image)/1024, 2)) + ' KB'
        images[idx][3] = fs.get_created_time('user/' + request.user.username + '/' + image)
        images[idx][4] = fs.get_accessed_time('user/' + request.user.username + '/' + image)
        images[idx][5] = fs.get_modified_time('user/' + request.user.username + '/' + image)
    context['image_detail'] = images
    return render(request, 'mysite/history.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/login')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)

def profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile')
    else:
        form = UserChangeForm(instance=request.user)
        args = {'form': form, 'user': request.user.username}
        return render(request, 'mysite/Profile.html', args)

def password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/profile')
    else:
        form = PasswordChangeForm(user=request.user)
    context = {'form': form}
    return render(request, 'registration/password.html', context)

def clear_folder():
    fs_object = FileSystemStorage()
    for file in fs_object.listdir('processed/')[1]:
        fs_object.delete('processed/' + file)
    for file in fs_object.listdir('saved/')[1]:
        fs_object.delete('saved/' + file)

