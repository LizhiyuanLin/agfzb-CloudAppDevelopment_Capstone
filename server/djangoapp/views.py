from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # <HINT> Get user information from request.POST
        # <HINT> username, first_name, last_name, password
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['psw']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            # <HINT> Login the user and 
            # redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://0a24c5d2.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        return render(request, 'djangoapp/index.html', {"dealership_list": dealerships})


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://0a24c5d2.us-south.apigw.appdomain.cloud/api/review"
        # Get reviews from the URL
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)
        return render(request, 'djangoapp/dealer_details.html', {"reviews_list":dealer_reviews, "dealer_id": dealer_id})
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.user.is_authenticated:
        if request.method == "GET":
            models = CarModel.objects.all().filter(dealer_id=dealer_id)
            context["cars"] = models
            context["dealer_id"] = dealer_id
            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == 'POST':
            car = CarModel.objects.get(id=request.POST['car'])
            review = {
                "review":{
                "name":request.user.first_name+" "+request.user.last_name,
                "dealership":dealer_id,
                "review":request.POST['content'],
                "purchase":request.POST['purchase'],
                "purchase_date":request.POST['purchase_date'],
                "car_make":car.make.name,
                "car_model":car.name,
                "car_year":car.year.strftime("%Y")
                }
            }
            json_payload = {"review": review}
            post_request("https://0a24c5d2.us-south.apigw.appdomain.cloud/api/review", json_payload)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
