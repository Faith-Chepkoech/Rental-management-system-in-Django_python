from django.shortcuts import render, redirect
from django.views.generic import CreateView,TemplateView
from .models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from .decorators import customer_required, owner_required
from .forms import CustomerSignUpForm, OwnerSignUpForm, LoginForm
from django.contrib import messages, auth
from django.contrib.auth.models import User
from clients.models import Clients,PropertyInquiry
from .models import Owner
from property.models import Property
from property.choice import price_choices, bedroom_choices, county_choices
from django.http import HttpResponse
from reportlab.pdfgen import canvas



 




class SignUpView(TemplateView):
    template_name = 'accounts/type.html'

class CustomerSignUpForm(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'accounts/customerreg.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        kwargs['form'] = self.form_class()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        password = form.cleaned_data.get('password1')
        user = authenticate(username=user.username, password=password)
        login(self.request, user)
        return redirect('login')

    
    
class OwnerSignUpView(CreateView):
    model = User
    form_class = OwnerSignUpForm
    template_name = 'accounts/ownerreg.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'owner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        password = form.cleaned_data.get('password1')
        user = authenticate(username=user.username, password=password)
        login(self.request, user)
        return redirect('login')



class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_customer:
                return reverse('index')
            elif user.is_owner:
                return reverse('dashboard')
        else:
            return reverse('login')







def index(request):
    propertys = Property.objects.order_by('-list_date')

    context = {
        'propertys': propertys,
        'county_choices': county_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices
    }

    return render(request, 'pages/index.html', context)

@login_required
def dashboard(request):
    if request.user.is_owner:
        owner = Owner.objects.get(user=request.user)
        owned_properties = Property.objects.filter(owner=owner)
        print(owned_properties)  # Print owned properties
        inquiries = PropertyInquiry.objects.filter(property__in=owned_properties)
        print(inquiries)  # Print inquiries

        return render(request, 'accounts/dashboard.html', {'owner': owner,'inquiries': inquiries,'owned_properties':owned_properties})
    elif request.user.is_customer:
        # Do something for customers
        return render(request, 'pages/index.html')
    else:
        # User is not an owner or a customer
        return render(request, 'accounts/type.html')



# Create your views here.
