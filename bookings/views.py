from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking ,RoomImage
from .forms import BookingForm, CustomUserCreationForm, RoomForm 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from .decoration import unauthenticated_user
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User


@login_required
def room_list(request):
    """Display all rooms with their availability."""
    rooms = Room.objects.all()
    for room in rooms:
        room.update_availability()  # Use the model's update method
    return render(request, 'bookings/room_list.html', {'rooms': rooms})
@login_required
def book_room(request):
    """Handle room booking."""
    room_id = request.GET.get('room_id')  # Get room ID from query parameters
    room = get_object_or_404(Room, id=room_id)

    # Validate if room is available
    if room.quantity_available <= 0:
        messages.error(request, "This room is fully booked.")
        return redirect('room_list')

    if request.method == 'POST':
        # Retrieve form data
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        rooms_to_book = int(request.POST.get('rooms_to_book', 1))

        # Validate dates
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect(f'/book?room_id={room_id}')

        if check_out_date <= check_in_date:
            messages.error(request, "Check-out date must be after the check-in date.")
            return redirect(f'/book?room_id={room_id}')

        # Validate room availability
        if rooms_to_book > room.quantity_available:
            messages.error(request, f"Only {room.quantity_available} rooms are available.")
            return redirect(f'/book?room_id={room_id}')

        # Redirect to booking confirmation page
        url = reverse('booking_confirm', args=[room.id])
        query_string = f"?check_in={check_in}&check_out={check_out}&rooms_to_book={rooms_to_book}"
        return HttpResponseRedirect(url + query_string)

    # Render the booking form for GET requests
    return render(request, 'bookings/book_room.html', {'room': room})

@login_required
def booking_confirm(request, room_id):
    """Confirm the booking details and process user actions."""
    room = get_object_or_404(Room, id=room_id)
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')
    rooms_to_book = int(request.GET.get('rooms_to_book',1))
    # Validate check-in and check-out dates
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        messages.error(request, "Invalid check-in or check-out date.")
        return redirect('room_list')

    if check_out <= check_in:
        messages.error(request, "Check-out date must be after the check-in date.")
        return redirect('room_list')
    
    if rooms_to_book > room.quantity_available:
        messages.error(request, f"Only {room.quantity_available} rooms are available.")
        return redirect('room_list')
    # Calculate total cost
    num_days = (check_out - check_in).days
    total_cost = num_days * room.price_per_night*rooms_to_book

    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Create booking
            Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out,
                rooms_booked=rooms_to_book
            )

            # Update room quantity and availability
            room.quantity_available -= rooms_to_book
            room.update_availability()
            messages.success(request, "Booking confirmed successfully!")
            return redirect('booking_success')
        elif 'cancel' in request.POST:
            messages.info(request, "Booking canceled.")
            return redirect('room_list')

    return render(request, 'bookings/booking_confirm.html', {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'rooms_to_book': rooms_to_book,
        'total_cost': total_cost,
    })
@login_required
def booking_success(request):
    """Display the booking success page."""
    return render(request, 'bookings/booking_success.html')

@login_required
def my_bookings(request):
    """Display logged-in user's bookings."""
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def admin_booking_list(request):
    """List all bookings for admin."""
    bookings = Booking.objects.select_related('room', 'user').all()

    return render(request, 'bookings/admin_booking_list.html', {'bookings': bookings})


@login_required
def delete_booking_admin(request, booking_id):
    """Delete a booking as admin and restore room availability."""
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room

    if request.method == 'POST':
        room.quantity_available += booking.rooms_booked
        room.update_availability()
        booking.delete()
        messages.success(request, "Booking deleted successfully!")
        return redirect('admin_booking_list')

    return render(request, 'bookings/delete_booking_admin.html', {'booking': booking})

@login_required
def update_booking_admin(request, booking_id):
    """Update booking details as admin."""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            booking.room.update_availability()
            messages.success(request, "Booking updated successfully!")
            return redirect('admin_booking_list')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/update_booking_admin.html', {'form': form, 'booking': booking})


@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    return render(request, 'bookings/admin_dashboard.html')
@login_required
def admin_room_list(request):
    """List all rooms for admin."""
    rooms = Room.objects.all()
    for room in rooms:
        room.update_availability()
    return render(request, 'bookings/admin_room_list.html', {'rooms': rooms})


@login_required
def delete_room_admin(request, room_id):
    """Delete a room as admin."""
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room deleted successfully!")
        return redirect('admin_room_list')

    return render(request, 'bookings/delete_room.html', {'room': room})

@login_required
def update_room_admin(request, room_id):
    """Update room details."""
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully!")
            return redirect('admin_room_list')
    else:
        form = RoomForm(instance=room)

    return render(request, 'bookings/update_room.html', {'form': form})

@login_required

def view_room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room_images = RoomImage.objects.filter(room=room)  # Fetch all images related to the room
    return render(request, 'bookings/room_detail.html', {
        'room': room,
        'room_images': room_images,
    })

def about_us(request):
    """Display the 'About Us' page."""
    return render(request, 'bookings/about.html')

def contact_us(request):
    """Display the 'Contact Us' page."""
    return render(request, 'bookings/contact.html')

def dashboard(request):
    """Display the dashboard."""
    rooms=Room.objects.all()
    return render(request, 'bookings/dashboard.html',{'rooms':rooms})
@unauthenticated_user
def registerPage(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'bookings/register.html', {'form': form})

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'bookings/login.html')

def logoutUser(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')
