from django.shortcuts import render

# Create your views here.

def index_view(request):
    return render(request, "index.html", {"search": True})

def bot_view(request):
    return render(request, "bots.html")