from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.core.exceptions import ValidationError

class Room(models.Model):
    room_type = models.CharField(max_length=50)
    price_per_night = models.IntegerField()
    is_available = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField()
    size = models.IntegerField()
    quantity_available = models.PositiveIntegerField(default=1)
    default_image = models.ImageField(upload_to='upload/media/', blank=True, null=True)
    def update_availability(self):
        """Update the availability of a room based on quantity available."""
        self.is_available = self.quantity_available > 0
        self.save()
    def __str__(self):
        return f"Room ({self.room_type})"
class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='upload/media/')

    def __str__(self):
        return f"Image for {self.room.room_type}"
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    rooms_booked = models.PositiveIntegerField(default=1)
    def clean(self):
        # Ensure check-out is after check-in
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")
        # Ensure room is available

    def __str__(self):
        return f"Booking: {self.user.username} - ({self.check_in} to {self.check_out})"