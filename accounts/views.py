from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CustomUserRegistrationForm


def register(request):
    """
    Public registration view for Reader, Journalist, and Editor accounts.
    All roles are registered immediately with no admin approval required.
    """
    if request.user.is_authenticated:
        return redirect("article_list")

    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save(update_fields=["is_active"])

            login(request, user)
            messages.success(
                request,
                "Account created successfully. You are now logged in."
            )
            return redirect("article_list")
    else:
        form = CustomUserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})
