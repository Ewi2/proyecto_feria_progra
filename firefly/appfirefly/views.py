from django.shortcuts import render
from .models import Dato


def lista1(request):
    listas1 = Dato.objects.all()
    return render(request,"dato.html",{"Dato":listas1})

def lista_raiz(request):
    # Lógica para la vista de la URL raíz
    return render(request, 'inicio.html')
