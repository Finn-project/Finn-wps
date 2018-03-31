from django.http import HttpResponse


def view_index(request):
    return HttpResponse('101')
