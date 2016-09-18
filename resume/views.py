from django.shortcuts import render

def resume(request):
    return render(request, "resume/index.html")
