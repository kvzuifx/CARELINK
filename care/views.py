from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from .forms import SupplyForm
from .models import Supply
from .models import *
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404
from django.db import transaction
from .forms import CreateFormUser, BenefactorRegistrationForm, RequestForm
from django.forms import formset_factory
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user , allowed_users, mainsd
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.db.models import Sum
from datetime import date, timedelta
from .models import Supply, Donation, Request, SupplyShipment
from django.conf import settings
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.urls import reverse
from . import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Supply
from .forms import SupplyForm
from django.shortcuts import render
from django.http import JsonResponse
from llama_index.core import PromptTemplate
from ollama import Client
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
import io
import base64
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from .models import Supply, Donation
from django.db.models import Count
# Create your views here.
from .forms import *


client = Client(host='http://localhost:11434')

def home12(request):
    return render(request, 'care/home.html')

class Index(TemplateView):
    template_name= 'care/ind.html'

# Define the low quantity threshold

@login_required(login_url='login')
def dash(request, user_id):
    LOW_QUANTITY = 10  # Adjust as needed
    user = get_object_or_404(User, pk=user_id)

    # Handle POST actions
    if request.method == 'POST':
        action = request.POST.get('action')
        supply_id = request.POST.get('supply_id')
        item = get_object_or_404(Supply, pk=supply_id, user=user)

        if action == 'edit':
            # Handle edit action
            # You can load a separate form here to edit the item and save the changes.
            form = SupplyForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, 'Item updated successfully.')
            else:
                messages.error(request, 'Error updating item.')

        elif action == 'delete':
            # Handle delete action
            item.delete()
            messages.success(request, 'Item deleted successfully.')

        return redirect('dash', user_id=user_id)

    # Handle GET request to display items
    items = Supply.objects.filter(user_id=user_id).order_by('supply_id')
    low_inventory = items.annotate(
        supply_quantity_int=Cast('supply_quantity', IntegerField())
    ).filter(supply_quantity_int__lte=LOW_QUANTITY)

    low_inventory_count = low_inventory.count()
    if low_inventory_count > 0:
        messages.error(request, f'{low_inventory_count} item{"s" if low_inventory_count > 1 else ""} has low inventory')

    low_inventory_ids = low_inventory.values_list('supply_id', flat=True)
    
    context = {
        'items': items,
        'low_inventory_ids': low_inventory_ids,
        'user_id': user_id
    }
    return render(request, 'care/dashboard.html', context)


def AddItem(request, user_id):
    if request.method == 'POST':
        if 'addSupply' in request.POST:
            supply_form = SupplyForm(request.POST, request.FILES)
            if supply_form.is_valid():
                supply_instance = supply_form.save(commit=False)
                # Explicitly set the user_id to the user field
                supply_instance.user_id = user_id
                supply_instance.save()
                messages.success(request, 'Supply item added successfully!')
                return redirect(reverse('dash', kwargs={'user_id': user_id}))
    else:
        supply_form = SupplyForm()
    
    context = {'supply_form': supply_form}
    return render(request, 'care/item_form.html', context)

def EditItem(request, user_id, item_id):
    # Retrieve the supply item based on user_id and item_id
    item = get_object_or_404(Supply, pk=item_id, user_id=user_id)
    supply_form = SupplyForm(instance=item)

    if request.method == 'POST':
        # Initialize the form with POST data and files, and bind it to the existing item instance
        supply_form = SupplyForm(request.POST, request.FILES, instance=item)
        if supply_form.is_valid():
            # Save the updated item
            supply_form.save()
            messages.success(request, 'Supply item updated successfully!')
            return redirect('dash', user_id=user_id)
        else:
            messages.error(request, 'Error updating item.')

    context = {
        'supply_form': supply_form,
        'item': item
    }
    return render(request, 'care/item_form.html', context)


@unauthenticated_user 
def registerPage(request):
    user_form = CreateFormUser()
    benefactor_form = BenefactorRegistrationForm()

    if request.method == "POST":
        user_form = CreateFormUser(request.POST)
        benefactor_form = BenefactorRegistrationForm(request.POST)

        if user_form.is_valid() and benefactor_form.is_valid():
            try:
                with transaction.atomic():
                    # Save user and patient details
                    user = user_form.save()

                    benef = benefactor_form.save(commit=False)
                    benef.user = user  # Link the patient to the user
                    benef.save()

                    # Add user to the 'patient' group
                    benefactor_group = Group.objects.get(name='benefactor')
                    benefactor_group.user_set.add(user)

                    messages.success(request, 'Account created for ' + user.username)
                    return redirect('login')

            except Exception as e:
                messages.error(request, f'Error: {e}')
    print(user_form) 
    context = {'user_form': user_form, 'benefactor_form': benefactor_form}
    return render(request, 'care/register.html', context)


# @csrf_exempt
@unauthenticated_user
def loginPage(request):
    # Initialize forms
    user_form = CreateFormUser()
    benefactor_form = BenefactorRegistrationForm()

    if request.method == "POST":
        # Handle login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user_id = user.id
            # Redirect to the user's page
            return redirect(f'/{user_id}/user/')
        
        else:
            messages.info(request, 'Username or password is incorrect')
        print(user_id)
        # Handle registration
        user_form = CreateFormUser(request.POST)
        benefactor_form = BenefactorRegistrationForm(request.POST)

        if user_form.is_valid() and benefactor_form.is_valid():
            try:
                with transaction.atomic():
                    # Save user and benefactor details
                    user = user_form.save()

                    benefactor = benefactor_form.save(commit=False)
                    benefactor.user = user  # Link the benefactor to the user
                    benefactor.save()

                    # Add user to the 'benefactor' group
                    benefactor_group = Group.objects.get(name='benefactor')
                    benefactor_group.user_set.add(user)

                    messages.success(request, 'Account created for ' + user.username)
                    return redirect('login')

            except Exception as e:
                messages.error(request, f'Error: {e}')

    # Always include forms in context
    context = {
        'user_form': user_form,
        'benefactor_form': benefactor_form
    }
    return render(request, 'care/login.html', context)

def logOutUser(request):
    logout(request)
    return redirect('login') 

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
# @mainsd()
def main(request):
    context = {}
    # Use a different variable name for the queryset
    return render(request, 'care/main.html',context)


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from geopy.geocoders import Nominatim


def location_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = Organisation.objects.filter(org_loc__icontains=query)[:10]
        data = [{'address': org.org_loc} for org in suggestions]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

# def index1(request):
#     # Fetch data from Django models
#     supply_data = Supply.objects.values('supply_category', 'supply_quantity')
#     donation_data = Donation.objects.values('donor__ben_name', 'quantity_donated')

#     # Convert to DataFrame
#     supply_df = pd.DataFrame(supply_data)
#     donation_df = pd.DataFrame(donation_data)
    
#     # Convert quantity columns to numeric
#     supply_df['supply_quantity'] = pd.to_numeric(supply_df['supply_quantity'], errors='coerce')
#     donation_df['quantity_donated'] = pd.to_numeric(donation_df['quantity_donated'], errors='coerce')

#     # Pie Chart for Supply Categories
#     pie_img = io.BytesIO()
#     plt.figure(figsize=(10, 5))
#     supply_category_totals = supply_df.groupby('supply_category')['supply_quantity'].sum().reset_index()
#     plt.pie(supply_category_totals['supply_quantity'], labels=supply_category_totals['supply_category'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
#     plt.title('Supply Categories Distribution')
#     plt.savefig(pie_img, format='png')
#     plt.close()
#     pie_img.seek(0)
#     pie_img_base64 = base64.b64encode(pie_img.getvalue()).decode('utf-8')

#     # Bar Graph for Donations by Donor
#     bar_img = io.BytesIO()
#     plt.figure(figsize=(12, 6))
#     plt.bar(donation_df['donor__ben_name'], donation_df['quantity_donated'], color=sns.color_palette('viridis', len(donation_df)))
#     plt.xlabel('Donor Name')
#     plt.ylabel('Quantity Donated')
#     plt.title('Total Donations by Donor')
#     plt.xticks(rotation=90)
#     plt.savefig(bar_img, format='png')
#     plt.close()
#     bar_img.seek(0)
#     bar_img_base64 = base64.b64encode(bar_img.getvalue()).decode('utf-8')

#     # Pass images to template
#     context = {
#         'pie_img_base64': pie_img_base64,
#         'bar_img_base64': bar_img_base64,
#     }
#     return render(request, 'care/index.html', context)

@login_required(login_url='login')
def Analytics(request):
   
    # Query to get the count of each supply category
    supply_data = Supply.objects.values('supply_category').annotate(count=Count('supply_id'))
    
    # Convert the data to a list of dictionaries
    supply_categories = list(supply_data)
    
    return render(request, 'care/analytics.html', {'supply_categories': supply_categories})

from django.shortcuts import get_object_or_404, render
from .models import Benefactor, Request
from .routing import haversine, geocode_location

from django.utils import timezone
from math import radians, cos, sin, sqrt, atan2

# Define the threshold in kilometers
SOME_THRESHOLD = 10
@login_required(login_url='login')
def userPage(request, user_id):
    # Retrieve the benefactor associated with the logged-in user
    user_benefactor = get_object_or_404(Benefactor, user_id=user_id)
    print(user_benefactor)
    # Retrieve notifications associated with this benefactor
    notifications = Notification.objects.filter(ben=user_benefactor).order_by('-timestamp')
    print("they dont exist")
    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.rec = user_benefactor
            new_request.status = 'pending'
            new_request.save()

            # Notify nearby benefactors
            notification_created = False
            if user_benefactor.latitude and user_benefactor.longitude:
                nearby_benefactors = Benefactor.objects.exclude(pk=user_benefactor.pk).filter(
                    latitude__isnull=False, longitude__isnull=False
                )
                distances = [
                    (benefactor, haversine(user_benefactor.latitude, user_benefactor.longitude, benefactor.latitude, benefactor.longitude))
                    for benefactor in nearby_benefactors
                ]
                distances.sort(key=lambda x: x[1])

                for benefactor, distance in distances:
                    if distance < SOME_THRESHOLD:
                        Notification.objects.create(
                            ben=benefactor,
                            notif_type='Request',
                            message=f'New request submitted for {new_request.supply} at {new_request.dest_loc}.',
                            timestamp=timezone.now(),
                            is_read='No'
                        )
                        notification_created = True

            return JsonResponse({
                'success': True,
                'notification_created': notification_created,
                'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    else:
        form = RequestForm()
    
    context = {
        'request_form': form,
        'user_benefactor': user_benefactor,
        'user_id': user_id,
        'notifications': notifications  # All notifications for this benefactor
    }
    return render(request, 'care/user1.html', context)


def distance_info(request, user_id):
    user_benefactor = get_object_or_404(Benefactor, user_id=user_id)
    print(f"User ID: {user_id}")
    print(f"User Benefactor Coordinates: {user_benefactor.latitude}, {user_benefactor.longitude}")
    
    if user_benefactor.latitude is not None and user_benefactor.longitude is not None:
        all_benefactors = Benefactor.objects.exclude(pk=user_benefactor.pk).filter(latitude__isnull=False, longitude__isnull=False)
        print(f"Number of other benefactors found: {all_benefactors.count()}")

        distances = []
        for benefactor in all_benefactors:
            distance = haversine(user_benefactor.latitude, user_benefactor.longitude, benefactor.latitude, benefactor.longitude)
            distances.append((benefactor, distance))
            print(f"Benefactor ID: {benefactor.pk}, Name: {benefactor.ben_name}, Coordinates: {benefactor.latitude}, {benefactor.longitude}, Distance: {distance} km")

        distances.sort(key=lambda x: x[1])  # Sort by distance
        
        # Prepare data for the map
        map_data = {
            'user_coords': [user_benefactor.latitude, user_benefactor.longitude],
            'nearest_benefactors': [
                {'name': benefactor.ben_name, 'coords': [benefactor.latitude, benefactor.longitude], 'distance': distance}
                for benefactor, distance in distances
            ]
        }
        
        context = {
            'distances': distances,
            'map_data': map_data
        }
        return render(request, 'care/distance.html', context)
    else:
        context = {
            'error_message': 'User benefactor does not have valid coordinates.'
        }

    return render(request, 'care/distance.html', context)



    

def dashboards(request):
    # Supply Quantities
    supplies = Supply.objects.all()
    labels_supply = [supply.supply_type for supply in supplies]
    data_supply = [supply.supply_quantity for supply in supplies]

    # Expiration Overview
    expired_count = Supply.objects.filter(expiration_date__lt=date.today()).count()
    expiring_soon_count = Supply.objects.filter(expiration_date__lt=date.today() + timedelta(days=30)).count()
    long_shelf_life_count = Supply.objects.filter(expiration_date__gte=date.today() + timedelta(days=30)).count()
    labels_expiration = ['Expired', 'Expiring Soon', 'Long Shelf Life']
    data_expiration = [expired_count, expiring_soon_count, long_shelf_life_count]

    # Donations Trend
    donations = Donation.objects.values('donation_date').annotate(total_donated=Sum('quantity_donated'))
    labels_donations = [donation['donation_date'].strftime('%Y-%m-%d') for donation in donations]
    data_donations = [donation['total_donated'] for donation in donations]

    # Requests vs Shipments
    dates = Request.objects.values('req_date').distinct().order_by('req_date')
    labels_requests_vs_shipments = [date['req_date'].strftime('%Y-%m-%d') for date in dates]
    requests_data = [Request.objects.filter(req_date=date).count() for date in dates]
    shipments_data = [SupplyShipment.objects.filter(shipment_date=date).count() for date in dates]

    return render(request, 'care/dashboard.html', {
        'labels_supply': labels_supply,
        'data_supply': data_supply,
        'labels_expiration': labels_expiration,
        'data_expiration': data_expiration,
        'labels_donations': labels_donations,
        'data_donations': data_donations,
        'labels_requests_vs_shipments': labels_requests_vs_shipments,
        'requests_data': requests_data,
        'shipments_data': shipments_data,
    })


@login_required(login_url='login')
def notifications(request, user_id):
    # Get the Benefactor instance for the given user_id
    user_benefactor = get_object_or_404(Benefactor, user_id=user_id)
    
    # Filter notifications based on the benefactor
    notifications = Notification.objects.filter(ben=user_benefactor).order_by('-timestamp')

    context = {
        'notifications': notifications,
        'user_id': user_id  # Attach user_id to context
    }
    return render(request, 'care/notifications.html', context)

@login_required(login_url='login')
def mark_as_read(request, notif_id):
    notification = get_object_or_404(Notification, notif_id=notif_id)
    notification.is_read = 'Yes'
    notification.save()
    return redirect('notifications')


def requests_for_benefactor(request, user_id):
    # Retrieve the benefactor and their organisation
    benefactor = get_object_or_404(Benefactor, pk=user_id)
    organisation = get_object_or_404(Organisation, pk=benefactor.org.pk)
    
    # Fetch requests based on destination location
    requests = Request.objects.filter(dest_loc=organisation.org_loc).order_by('-req_date')


    request_id_proofs = {}
    for req in requests:
        # Retrieve the ID proof associated with the benefactor or request
        # Adjust the filter if needed
        id_proof = IDProof.objects.filter(benefactor=req.rec).first()  
        
        # Map the request ID to its ID proof
        request_id_proofs[req.req_id] = id_proof
    
    # Handle POST request to update the status
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('status')
        req = get_object_or_404(Request, pk=request_id)
        req.status = new_status
        req.save()
        messages.success(request, 'Request status updated successfully!')
        # return redirect('care/benefactor_req.html', user_id=user_id)
    
    context = {
        'requests': requests,
        'benefactor': benefactor,
        'request_id_proofs': request_id_proofs
    }
    return render(request, 'care/benefactor_req.html', context)

def supply_detail(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    requests = Request.objects.filter(supply=supply)
    context = {
        'supply': supply,
        'requests': requests
    }
    return render(request, 'care/supply_detail.html', context) 

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

def extract_fields_from_ocr(ocr_text, question):
    carelink_context = (
        "CARELINK is a robust supply chain management system designed to streamline the process of connecting donors with recipients in need of health-related supplies. "
        "The platform facilitates efficient tracking and distribution of donations, ensuring that supplies reach those who need them most. Donors can easily list the supplies they wish to contribute, while recipients can apply for requests based on their specific needs."
        "To maintain security and ensure authenticity, CARELINK requires that all recipients attach a valid ID proof when submitting a request. "
        "This verification process helps protect both parties and ensures that supplies are distributed fairly and responsibly. The ID proof must be uploaded to the system before any request is processed, ensuring that all necessary information is in place for a smooth transaction."
    )


    query = (
        "Below is a description of CARELINK. "
        "Based on this description, please provide detailed answers to the following questions:\n"
        "{question}\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Provide detailed responses for each question based on the information in the context."
    )

    prompt = query.format(context_str=carelink_context, question=question)
    print(f"Formatted Prompt: {prompt}")  # Debugging line
  # Debugging line

    try:
        response = client.chat(model='llama3', messages=[
            {'role': 'user', 'content': prompt},
        ])
        print("Raw Response:", response)  # Debugging line
        
        if isinstance(response, dict):
            resp_text = response.get('message', {}).get('content', 'No content found in the response.')
        else:
            resp_text = 'Unexpected response format.'
        
        return resp_text
    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while processing the request."




from django.http import JsonResponse

def chat_view(request):
    if request.method == 'POST':
        ocr_text = request.POST.get('ocr_text', '')
        question = request.POST.get('question', '')
        
        prompt = extract_fields_from_ocr(ocr_text, question)
        print(f"OCR Text: {ocr_text}")  # Debugging line
        print(f"Question: {question}")  # Debugging line
        print(f"Prompt: {prompt}")  # Debugging line

        # Call the LLaMA model
        try:
            response = client.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt},
            ])
            print("Raw Response:", response)  # Debugging line

            if isinstance(response, dict):
                resp_text = response.get('message', {}).get('content', 'No content found in the response.')
            else:
                resp_text = 'Unexpected response format.'
                
            return JsonResponse({'response': resp_text, 'prompt': prompt})
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({'response': "An error occurred while processing the request.", 'prompt': prompt})
    return render(request, 'care/chat.html')




@login_required
def upload_id_proof(request, user_id):
    # Get the Benefactor instance for the given user_id
    user_benefactor = get_object_or_404(Benefactor, user_id=user_id)

    if request.method == 'POST':
        form = IDProofForm(request.POST, request.FILES)
        if form.is_valid():
            id_proof = form.save(commit=False)
            # Automatically set the benefactor field
            id_proof.benefactor = user_benefactor
            id_proof.save()
            return redirect('view_id_proof', user_id=user_id)  # Redirect to view ID proof page
    else:
        form = IDProofForm()

    return render(request, 'care/upload_id_proof.html', {'form': form, 'user_id': user_id})


@login_required
def view_id_proof(request, user_id):
    # Get the Benefactor instance for the given user_id
    user_benefactor = get_object_or_404(Benefactor, user_id=user_id)

    try:
        id_proof = IDProof.objects.filter(benefactor=user_benefactor).first() 
    except IDProof.DoesNotExist:
        id_proof = None

    return render(request, 'care/view_id_proof.html', {'id_proof': id_proof, 'user_id': user_id})