from django.urls import path
from . import views

urlpatterns = [
    # Common routes
    path('', views.dashboard, name='dashboard'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('about-us/', views.about_us, name='about'),
    path('contact-us/', views.contact_us, name='contact'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),

    # User-specific routes
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:room_id>/', views.view_room_detail, name='room_detail'),
    path('book/', views.book_room, name='book_room'),
    path('booking_confirm/<int:room_id>/', views.booking_confirm, name='booking_confirm'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Admin-specific routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin-bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('delete_room/<int:room_id>', views.delete_room_admin, name='delete_room'),
    path('update_room/<int:room_id>', views.update_room_admin, name='update_room'),
    # Corrected the following two routes:
    path('update_booking_admin/<int:booking_id>/', views.update_booking_admin, name='update_booking_admin'),
    path('delete_booking_admin/<int:booking_id>/', views.delete_booking_admin, name='delete_booking_admin'),
]
