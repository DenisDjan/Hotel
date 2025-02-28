from django.contrib import admin
from .models import Room, Booking,RoomImage  # Import models from models.py, not redefining them

class RoomImageInline(admin.TabularInline):  # Or admin.StackedInline for a different layout
    model = RoomImage
    extra = 3  # Number of additional image upload forms to show by default
    fields = ['image']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
     list_display = ['room_type', 'price_per_night', 'capacity', 'quantity_available']
     inlines = [RoomImageInline]  # Attach the inline to the Room admin panel
     fields = ['room_type', 'price_per_night', 'capacity', 'size', 'quantity_available', 'default_image']
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out')
