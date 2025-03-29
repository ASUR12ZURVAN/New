from django.urls import path
from .views import *
from .views import delete_itinerary

urlpatterns = [
    path('users/',get_users,name = "get-users"),
    path('users/create',create_user,name = "create-user"),
    path('users/delete',delete_user,name = "delete-user"),
    path('api/delete_itinerary/<int:id>/', delete_itinerary, name='delete-itinerary'),
    path('api/users/', UserCreateAPIView.as_view(), name='user-create'),
    path('api/travel_requests/', TravelRequestCreateAPIView.as_view(), name='travel-request-create'), 
    path('get_itinerary_by_user/', get_itinerary_by_user, name='get_itinerary_by_user'),
    path('user/put',put_user,name = "put-user")
]