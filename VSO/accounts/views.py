import os, cv2
from django.conf import settings
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, StreamForm, EditProfileForm, ResetPasswordForm,EditUserInfoForm
from .models import Stream, Record, Userinfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from datetime import  date

def home(request):
    # Check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")

            return render('home')

        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        today = date.today().strftime('%Y-%m-%d')
        records = Record.objects.filter(created_at__startswith=today, userid=request.user)
        path = " \\ \\ \\"
        if records:
            path = str(records[0].path).split('\\')[1:4]

        context = {

            'recent_records': records,
            'home': True,
            'path': f"{path[0]}\\{path[1]}\\{path[2]}"
        }
        return render(request, 'base.html', context)


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


def date_list(request):
    # Get the available dates from the records of the current user
    available_dates = Record.objects.filter(userid=request.user).dates('created_at', 'day', order='DESC')
    return render(request, 'date_list.html', {'available_dates': available_dates})


def streams_list(request, chosen_date):
    # Get streams for the current user that have records on the chosen date
    streams = Stream.objects.filter(record__created_at__date=chosen_date, userid=request.user).distinct()
    return render(request, 'stream_list.html', {'streams': streams, 'chosen_date': chosen_date})



def record_list(request, chosen_date, stream_id):
    # Get records for the current user, the chosen date, and the selected stream
    records = Record.objects.filter(streamid_id=stream_id, created_at__date=chosen_date, userid=request.user)
    user = request.user
    stream = Stream.objects.get(pk=stream_id)
    path = f"user_{user.id}_{user.first_name}\\{stream.label}\\{str(chosen_date).strip(' ')[:10]}\\"
    #
    return render(request, 'record_list.html', {'records': records, 'path': path})


def stream_list(request):
    streams = Stream.objects.filter(userid=request.user)
    return render(request, 'streams.html', {'streams': streams})


def add_stream(request):
    if request.method == 'POST':
        add_form = StreamForm(request.POST)
        if add_form.is_valid():
            new_stream = add_form.save(commit=False)
            new_stream.userid = request.user
            new_stream.save()
            return redirect('stream_list')
    else:
        add_form = StreamForm()

    return render(request, 'streams.html', {'add_form': add_form, 'show_add_form': True})


def stream_details(request, stream_id):
    current_stream = get_object_or_404(Stream, id=stream_id, userid=request.user)
    return render(request, 'streams.html', {'current_stream': current_stream, 'details': True})


def edit_stream(request, stream_id):
    current_stream = get_object_or_404(Stream, id=stream_id, userid=request.user)

    if request.method == 'POST':
        edit_form = StreamForm(request.POST, instance=current_stream)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('stream_details', stream_id=stream_id)
    else:
        edit_form = StreamForm(instance=current_stream)

    return render(request, 'streams.html',
                  {'edit_form': edit_form, 'current_stream': current_stream, 'show_edit_form': True})


@login_required
def user_profile(request):
    user_form = EditProfileForm(instance=request.user)
    user_info_form = EditUserInfoForm(instance=request.user.userinfo)

    FormSet = modelformset_factory(Userinfo, form=EditUserInfoForm, fields=('phone_number',), extra=0)

    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            user_form = EditProfileForm(request.POST, instance=request.user)
            user_info_form = EditUserInfoForm(request.POST, instance=request.user.Userinfo)
            if user_form.is_valid() and user_info_form.is_valid():
                user_form.save()
                user_info_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('user_profile')
        elif 'reset_password' in request.POST:
            reset_password_form = ResetPasswordForm(request.user, request.POST)
            if reset_password_form.is_valid():
                user = reset_password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed.')
                return redirect('user_profile')
        elif 'delete_account' in request.POST:
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('login')  # Redirect to login page after account deletion

    user_info_formset = FormSet(queryset=Userinfo.objects.filter(userid=request.user))
    reset_password_form = ResetPasswordForm(request.user)

    context = {
        'user_form': user_form,
        'user_info_formset': user_info_formset,
        'reset_password_form': reset_password_form,
    }

    return render(request, 'settings.html', context)
def serve_video(request, path, video_filename):
    p = str(path).split('\\')
    # Construct the path to the video file
    video_path = os.path.join(settings.MEDIA_ROOT, p[0], p[1], p[2], video_filename)

    # Open the video file in binary mode
    with open(video_path, 'rb') as video_file:
        response = HttpResponse(video_file.read(), content_type='video/mp4')  # Adjust content type if needed
        response['Content-Disposition'] = f'inline; filename="{video_filename}"'
        return response

# def serve_video(request, path, video_filename):
#     p = str(path).split('\\')
#     # Construct the path to the video file
#     video_path = os.path.join(settings.MEDIA_ROOT, p[0], p[1], p[2], video_filename)
#
#     # Reencode the video using ffmpeg-python
#     output_options = {'c:v': 'libvpx-vp9', 'b:v': '2M', 'c:a': 'libopus'}
#     reencoded_video = ffmpeg.input(video_path).output('pipe:', **output_options).run(capture_stdout=True,
#                                                                                      capture_stderr=True)
#
#     # Create an HttpResponse with the reencoded video content
#     response = HttpResponse(reencoded_video, content_type='video/webm')
#     response['Content-Disposition'] = f'inline; filename="{video_filename}"'
#     return response