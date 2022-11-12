from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.forms import ProfileUpdateForm, UserUpdateForm
from users.models import Profile as Pro
from users.models import Requests
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from memberships.models import Membership, UserMembership, Subscription
from django.core.mail import send_mail
from django.core.mail import EmailMessage


# Create your views here.

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None


def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


@login_required
def Profile(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_membership': user_membership,
        'user_subscription': user_subscription
    }
    return render(request, 'profile/profile.html', context)


def kerkesa(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('e-mail')
        phone_number = request.POST.get('phone')
        prof = request.user.profile
        request_mod = Requests(profile=prof, name=name, email=email, phone_number=phone_number)
        request_mod.save()
        prof_id = prof.id
        Pro.objects.filter(id=prof_id).update(is_teacher=True)

        message = 'Your request for a teacher account has been accepted! Now you can go back to MesoOn and upload courses and lectures, job done!'
        send_mail(
            'MesoOn, request accepted.',
            message,
            'mesoon@no-reply.com',
            [email],
            fail_silently=False,
        )
        send_mail(
            'MesoOn',
            'Someone made a request for the teachers account. Me info: ' + name + ' , ' + email + ' , ' + phone_number + ' , ' + str(
                prof) + '.',
            'mesoon@no-reply.com',
            ['redian1marku@gmail.com'],
            fail_silently=False,
        )
        messages.info(request, f'The request was sent successfully, you will be notified by email.')
        return redirect('courses:home')

