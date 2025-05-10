from .forms import ProfileUpdateForm

def profile_update_form(request):
    if request.user.is_authenticated:
        return {'profile_update_form': ProfileUpdateForm(instance=request.user.profile)}
    return {}
