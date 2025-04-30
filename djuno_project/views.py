from django.shortcuts import render
from djuno.registry import registry


def index(request):
    context = {
        'button': registry['button'](text='Click Me'),
        'icon': registry['icon'](name='star')
    }
    return render(request, 'index.html', context)
