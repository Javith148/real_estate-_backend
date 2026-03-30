from django.shortcuts import redirect, render
from .models import Property_details, Agent, Property_rooms, CreateAdminUser
from .serializers import Property_detailsSerializer, Agent_Serializer, Property_rooms_Serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q



@api_view(['GET'])
def property_details_api(request):
    property = Property_details.objects.all()
    convert_api = Property_detailsSerializer(property, many=True)
    return Response(convert_api.data)


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       

        try:
            user = CreateAdminUser.objects.get(username=username)

            if check_password(password, user.password):
                request.session['admin_id'] = user.id
                return redirect('dashboard')
            else:
                return render(request, 'login.html', {'error': 'Wrong password'})

        except CreateAdminUser.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})

    return render(request, 'login.html')

def dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('login')

    return render(request, 'index.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def category(request):
    return render(request, 'categories.html')

def properties(request):
    properties = Property_details.objects.all()
    agents = Agent.objects.all()
    return render(request, 'properties.html', {'properties': properties, 'agents': agents})

def create_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        CreateAdminUser.objects.create(
            username=username,
            password=make_password(password)
        )

        return redirect('login')  

    return render(request, 'createadmin.html')





def add_property(request):
    if request.method == "POST":
        try:
           
            title = request.POST.get('title', '').strip()
            price = request.POST.get('price', '').strip()
            rating = request.POST.get('rating', '').strip()
            property_type = request.POST.get('property_type', '').strip()
            location = request.POST.get('location', '').strip()
            cost_of_living = request.POST.get('cost_of_living', '').strip()
            agent_id = request.POST.get('agent', '').strip()
            image = request.FILES.get('image')

           
            bedrooms = request.POST.get('bedrooms', '1').strip()
            bathroom = request.POST.get('bathroom', '1').strip()
            kitchen = request.POST.get('kitchen', '1').strip()
            store_room = request.POST.get('store_room', '1').strip()
            balcony = request.POST.get('balcony', '1').strip()

         
            if not title:
                messages.error(request, "Title is required")
                return redirect('properties')
            
            if not price:
                messages.error(request, "Price is required")
                return redirect('properties')
            
            if not rating:
                messages.error(request, "Rating is required")
                return redirect('properties')
            
            if not property_type:
                messages.error(request, "Property Type is required")
                return redirect('properties')
            
            if not location:
                messages.error(request, "Location is required")
                return redirect('properties')
            
            if not cost_of_living:
                messages.error(request, "Cost of Living is required")
                return redirect('properties')
            
            if not agent_id:
                messages.error(request, "Please select an agent")
                return redirect('properties')
            
            if not image:
                messages.error(request, "Property image is required")
                return redirect('properties')

            try:
                price = int(price)
                rating_val = Decimal(rating)
                cost_of_living = int(cost_of_living)
            except (ValueError, TypeError):
                messages.error(request, "Price, Rating, and Cost must be valid numbers")
                return redirect('properties')

            
            if rating_val > 5 or rating_val < 0:
                messages.error(request, "Rating must be between 0 and 5")
                return redirect('properties')

           
            try:
                bedrooms = int(bedrooms) if bedrooms else 1
                bathroom = int(bathroom) if bathroom else 1
                kitchen = int(kitchen) if kitchen else 1
                store_room = int(store_room) if store_room else 1
                balcony = int(balcony) if balcony else 1
            except (ValueError, TypeError):
                messages.error(request, "Room numbers must be valid integers")
                return redirect('properties')

          
            try:
                agent = Agent.objects.get(id=agent_id)
            except Agent.DoesNotExist:
                messages.error(request, "Selected agent does not exist")
                return redirect('properties')

          
            rooms = Property_rooms.objects.create(
                bedrooms=bedrooms,
                bathroom=bathroom,
                kitchen=kitchen,
                store_room=store_room,
                balcony=balcony
            )

          
            property_obj = Property_details.objects.create(
                title=title,
                price=price,
                rating=rating_val,
                property_type=property_type,
                location=location,
                cost_of_living=cost_of_living,
                image=image,
                Agent=agent,
                property_rooms=rooms
            )

            messages.success(request, f"Property '{title}' added successfully!")
            return redirect('properties')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('properties')

    return redirect('properties')


def delete_property(request, property_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        property_obj = Property_details.objects.get(id=property_id)
        property_title = property_obj.title
        
        # Delete associated rooms first
        if property_obj.property_rooms:
            property_obj.property_rooms.delete()
        
        # Delete the property
        property_obj.delete()
        
        messages.success(request, f"✅ Property '{property_title}' deleted successfully!")
    except Property_details.DoesNotExist:
        messages.error(request, f"❌ Property not found")
    except Exception as e:
        messages.error(request, f"❌ Error deleting property: {str(e)}")
    
    return redirect('properties')


def edit_property(request, property_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        property_obj = Property_details.objects.get(id=property_id)
    except Property_details.DoesNotExist:
        messages.error(request, "❌ Property not found")
        return redirect('properties')
    
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get('title', '').strip()
            price = request.POST.get('price', '').strip()
            rating = request.POST.get('rating', '').strip()
            property_type = request.POST.get('property_type', '').strip()
            location = request.POST.get('location', '').strip()
            cost_of_living = request.POST.get('cost_of_living', '').strip()
            agent_id = request.POST.get('agent', '').strip()
            image = request.FILES.get('image')

            # Room details
            bedrooms = request.POST.get('bedrooms', '1').strip()
            bathroom = request.POST.get('bathroom', '1').strip()
            kitchen = request.POST.get('kitchen', '1').strip()
            store_room = request.POST.get('store_room', '1').strip()
            balcony = request.POST.get('balcony', '1').strip()

            # ========== VALIDATION ==========
            if not title:
                messages.error(request, "❌ Title is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not price:
                messages.error(request, "❌ Price is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not rating:
                messages.error(request, "❌ Rating is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not property_type:
                messages.error(request, "❌ Property Type is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not location:
                messages.error(request, "❌ Location is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not cost_of_living:
                messages.error(request, "❌ Cost of Living is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not agent_id:
                messages.error(request, "❌ Please select an agent")
                return redirect(f'/edit-property/{property_id}/')

            # Numeric validation
            try:
                price = int(price)
                rating_val = Decimal(rating)
                cost_of_living = int(cost_of_living)
            except (ValueError, TypeError):
                messages.error(request, "❌ Price, Rating, and Cost must be valid numbers")
                return redirect(f'/edit-property/{property_id}/')

            # Rating validation
            if rating_val > 5 or rating_val < 0:
                messages.error(request, "❌ Rating must be between 0 and 5")
                return redirect(f'/edit-property/{property_id}/')

            # Room validation
            try:
                bedrooms = int(bedrooms) if bedrooms else 1
                bathroom = int(bathroom) if bathroom else 1
                kitchen = int(kitchen) if kitchen else 1
                store_room = int(store_room) if store_room else 1
                balcony = int(balcony) if balcony else 1
            except (ValueError, TypeError):
                messages.error(request, "❌ Room numbers must be valid integers")
                return redirect(f'/edit-property/{property_id}/')

            # Agent exists check
            try:
                agent = Agent.objects.get(id=agent_id)
            except Agent.DoesNotExist:
                messages.error(request, "❌ Selected agent does not exist")
                return redirect(f'/edit-property/{property_id}/')

            # ========== UPDATE PROPERTY_ROOMS ==========
            if property_obj.property_rooms:
                property_obj.property_rooms.bedrooms = bedrooms
                property_obj.property_rooms.bathroom = bathroom
                property_obj.property_rooms.kitchen = kitchen
                property_obj.property_rooms.store_room = store_room
                property_obj.property_rooms.balcony = balcony
                property_obj.property_rooms.save()

            # ========== UPDATE PROPERTY_DETAILS ==========
            property_obj.title = title
            property_obj.price = price
            property_obj.rating = rating_val
            property_obj.property_type = property_type
            property_obj.location = location
            property_obj.cost_of_living = cost_of_living
            property_obj.Agent = agent
            
            if image:
                property_obj.image = image
            
            property_obj.save()

            messages.success(request, f"✅ Property '{title}' updated successfully!")
            return redirect('properties')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
            return redirect(f'/edit-property/{property_id}/')

    # GET request - load edit form with current data
    agents = Agent.objects.all()
    context = {
        'property': property_obj,
        'agents': agents,
        'property_types': ['House', 'Apartment', 'Villa', 'Condo', 'Townhouse', 'Store']
    }
    return render(request, 'edit_property.html', context)