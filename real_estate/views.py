from django.shortcuts import redirect, render
from .models import Property_details, Agent, Property_rooms, CreateAdminUser
from .serializers import Property_detailsSerializer, Agent_Serializer, Property_rooms_Serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q, Avg, Sum
from django.core.paginator import Paginator
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Property_details



@api_view(['GET'])
def property_details_api(request):
    property = Property_details.objects.all()
    convert_api = Property_detailsSerializer(property, many=True)
    return Response(convert_api.data)


# Admin user registration and login views
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
 
# Admin login view
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

# page rendering views
def dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('login')

    return render(request, 'index.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def category(request):
    return render(request, 'categories.html')


# Agent page views
def Agentpage(request):
    agents = Agent.objects.all()

    total_agents = agents.count()

    
    active_agents = Agent.objects.filter(is_active=True).count()

    
    avg_rating = agents.aggregate(avg=Avg('rating'))['avg'] or 0

    total_properties = agents.aggregate(total=Sum('sold'))['total'] or 0

    context = {
        'agents': agents,
        'total_agents': total_agents,
        'active_agents': active_agents,
        'avg_rating': round(avg_rating, 1),
        'total_properties': total_properties
    }

    return render(request, 'agents.html', context)

# add agent
def add_agent(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            mail_id = request.POST.get('mail_id', '').strip()
            rating = request.POST.get('rating', '').strip()
            sold = request.POST.get('sold', '0').strip()
            reviews = request.POST.get('reviews', '0').strip()
            agent_image = request.FILES.get('agent_image')

            # Validation
            if not name:
                messages.error(request, "Agent name is required")
                return redirect('agents')
            
            if not mail_id:
                messages.error(request, "Email is required")
                return redirect('agents')
            
            if not rating:
                messages.error(request, "Rating is required")
                return redirect('agents')

            # Type conversion and validation
            try:
                rating_val = Decimal(rating)
                sold = int(sold) if sold else 0
                reviews = int(reviews) if reviews else 0
            except (ValueError, TypeError):
                messages.error(request, "Rating must be a valid number, Sold and Reviews must be integers")
                return redirect('agents')

            if rating_val > 5 or rating_val < 0:
                messages.error(request, "Rating must be between 0 and 5")
                return redirect('agents')

            # Create agent
            agent = Agent.objects.create(
                name=name,
                mail_id=mail_id,
                rating=rating_val,
                sold=sold,
                reviews=reviews,
                agent_image=agent_image if agent_image else None
            )

            messages.success(request, f"Agent '{name}' added successfully!")
            return redirect('agents')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('agents')

    return redirect('agents')

# edit agent
def edit_agent(request, agent_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        messages.error(request, "Agent not found")
        return redirect('agents')
    
    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            mail_id = request.POST.get('mail_id', '').strip()
            rating = request.POST.get('rating', '').strip()
            sold = request.POST.get('sold', '0').strip()
            reviews = request.POST.get('reviews', '0').strip()
            agent_image = request.FILES.get('agent_image')

            # Validation
            if not name:
                messages.error(request, "Agent name is required")
                return redirect(f'/edit-agent/{agent_id}/')
            
            if not mail_id:
                messages.error(request, "Email is required")
                return redirect(f'/edit-agent/{agent_id}/')
            
            if not rating:
                messages.error(request, "Rating is required")
                return redirect(f'/edit-agent/{agent_id}/')

            # Type conversion and validation
            try:
                rating_val = Decimal(rating)
                sold = int(sold) if sold else 0
                reviews = int(reviews) if reviews else 0
            except (ValueError, TypeError):
                messages.error(request, "Rating must be a valid number, Sold and Reviews must be integers")
                return redirect(f'/edit-agent/{agent_id}/')

            if rating_val > 5 or rating_val < 0:
                messages.error(request, "Rating must be between 0 and 5")
                return redirect(f'/edit-agent/{agent_id}/')

            # Update agent
            agent.name = name
            agent.mail_id = mail_id
            agent.rating = rating_val
            agent.sold = sold
            agent.reviews = reviews
            
            if agent_image:
                agent.agent_image = agent_image
            
            agent.save()

            messages.success(request, f"Agent '{name}' updated successfully!")
            return redirect('agents')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(f'/edit-agent/{agent_id}/')

    context = {'agent': agent}
    return render(request, 'edit_agent.html', context)

# delete agent
def delete_agent(request, agent_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        agent = Agent.objects.get(id=agent_id)
        agent_name = agent.name
        agent.delete()
        messages.success(request, f"Agent '{agent_name}' deleted successfully!")
    except Agent.DoesNotExist:
        messages.error(request, "Agent not found")
    except Exception as e:
        messages.error(request, f"Error deleting agent: {str(e)}")
    
    return redirect('agents')

# agent active/Inactive toggle
def toggle_agent_status(request, agent_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        agent = Agent.objects.get(id=agent_id)
        agent.is_active = not agent.is_active
        agent.save()
        
        status = "activated" if agent.is_active else "deactivated"
        messages.success(request, f"Agent '{agent.name}' {status} successfully!")
    except Agent.DoesNotExist:
        messages.error(request, "Agent not found")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('agents')

# agent details export to excel
def export_agents_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Agents"

    # Header Row
    ws.append([
        "Name", "Email", "Rating", "Properties Sold", "Reviews", "Status"
    ])

    # Data Rows
    agents = Agent.objects.all()

    for agent in agents:
        ws.append([
            agent.name,
            agent.mail_id,
            float(agent.rating),
            agent.sold,
            agent.reviews,
            "Active" if agent.is_active else "Inactive"
        ])

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=agents.xlsx'

    wb.save(response)
    return response


#property page business logic

# add property view
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
                if not agent.is_active:
                    messages.error(request, "Selected agent is not active")
                    return redirect('properties')
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

# delete property view
def delete_property(request, property_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        property_obj = Property_details.objects.get(id=property_id)
        property_title = property_obj.title
        
        
        if property_obj.property_rooms:
            property_obj.property_rooms.delete()
        
       
        property_obj.delete()
        
        messages.success(request, f"Property '{property_title}' deleted successfully!")
    except Property_details.DoesNotExist:
        messages.error(request, f" Property not found")
    except Exception as e:
        messages.error(request, f" Error deleting property: {str(e)}")
    
    return redirect('properties')

# edit property view
def edit_property(request, property_id):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    try:
        property_obj = Property_details.objects.get(id=property_id)
    except Property_details.DoesNotExist:
        messages.error(request, " Property not found")
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

           
            if not title:
                messages.error(request, " Title is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not price:
                messages.error(request, " Price is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not rating:
                messages.error(request, " Rating is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not property_type:
                messages.error(request, " Property Type is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not location:
                messages.error(request, " Location is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not cost_of_living:
                messages.error(request, " Cost of Living is required")
                return redirect(f'/edit-property/{property_id}/')
            
            if not agent_id:
                messages.error(request, " Please select an agent")
                return redirect(f'/edit-property/{property_id}/')

            # Numeric validation
            try:
                price = int(price)
                rating_val = Decimal(rating)
                cost_of_living = int(cost_of_living)
            except (ValueError, TypeError):
                messages.error(request, " Price, Rating, and Cost must be valid numbers")
                return redirect(f'/edit-property/{property_id}/')

            # Rating validation
            if rating_val > 5 or rating_val < 0:
                messages.error(request, " Rating must be between 0 and 5")
                return redirect(f'/edit-property/{property_id}/')

            # Room validation
            try:
                bedrooms = int(bedrooms) if bedrooms else 1
                bathroom = int(bathroom) if bathroom else 1
                kitchen = int(kitchen) if kitchen else 1
                store_room = int(store_room) if store_room else 1
                balcony = int(balcony) if balcony else 1
            except (ValueError, TypeError):
                messages.error(request, " Room numbers must be valid integers")
                return redirect(f'/edit-property/{property_id}/')

            
            try:
                agent = Agent.objects.get(id=agent_id)
                if not agent.is_active:
                    messages.error(request, " Selected agent is not active")
                    return redirect(f'/edit-property/{property_id}/')
            except Agent.DoesNotExist:
                messages.error(request, " Selected agent does not exist")
                return redirect(f'/edit-property/{property_id}/')

            
            if property_obj.property_rooms:
                property_obj.property_rooms.bedrooms = bedrooms
                property_obj.property_rooms.bathroom = bathroom
                property_obj.property_rooms.kitchen = kitchen
                property_obj.property_rooms.store_room = store_room
                property_obj.property_rooms.balcony = balcony
                property_obj.property_rooms.save()

          
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

            messages.success(request, f" Property '{title}' updated successfully!")
            return redirect('properties')

        except Exception as e:
            messages.error(request, f" Error: {str(e)}")
            return redirect(f'/edit-property/{property_id}/')

    agents = Agent.objects.filter(is_active=True)
    context = {
        'property': property_obj,
        'agents': agents,
        'property_types': ['House', 'Apartment', 'Villa', 'Condo', 'Townhouse', 'Store']
    }
    return render(request, 'edit_property.html', context)

# property search and Pagination
def properties(request):
    search_query = request.GET.get('search', '')

    properties = Property_details.objects.all().order_by('-id')

    
    if search_query:
        properties = properties.filter(
            title__icontains=search_query
        ) | properties.filter(
            location__icontains=search_query
        ) | properties.filter(
            property_type__icontains=search_query
        )

 
    paginator = Paginator(properties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    agents = Agent.objects.filter(is_active=True)

    return render(request, 'properties.html', {
        'properties': page_obj,
        'search_query': search_query,
        'agents': agents
    })

#export properties to excel file
def export_properties(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Properties"

    # Header Row
    ws.append([
        "Title", "Location", "Price", "Type",
        "Rating", "Cost of Living", "Agent"
    ])

    # Data Rows
    properties = Property_details.objects.all()

    for p in properties:
        ws.append([
            p.title,
            p.location,
            p.price,
            p.property_type,
            float(p.rating),
            p.cost_of_living,
            p.Agent.name if p.Agent else "N/A"
        ])

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=properties.xlsx'

    wb.save(response)
    return response