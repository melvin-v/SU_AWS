from django.shortcuts import render

# Create your views here.
def store(request):
    context = {}
    return render(request,'generales /store.html')

def cart(request):
    context = {}
    return render(request,'generales /cart.html')

def checkout(request):
    context = {}
    return render(request,'generales /checkout.html')