from django.urls import path
from .views import *

urlpatterns = [
    path('users/',get_users,name = "get-users"),
    path('users/create',create_user,name = "create-user"),
    path('users/delete',delete_user,name = "delete-user"),
    path('api/users/', UserCreateAPIView.as_view(), name='user-create'),
    path('api/travel_requests/', TravelRequestCreateAPIView.as_view(), name='travel-request-create'), 
    path('get_itinerary_by_user/', get_itinerary_by_user, name='get_itinerary_by_user'),
    path('user/put',put_user,name = "put-user"),
    path('delete_itinerary',delete_itinerary,name = 'delete_itinerary'),
    path('get_hotel_by_itinerary/<int:itinerary_id>',get_hotels_by_itinerary,name = 'Get_Hotels')
]