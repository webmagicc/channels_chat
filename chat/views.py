from django.shortcuts import render


def home(request):
    user = request.user
    # request.session['message'] = 'Work with session'
    session_message = request.session.get('message', None)
    return render(
        request, "index.html", {
            'user': user,
            'session_message': session_message
        }
    )
