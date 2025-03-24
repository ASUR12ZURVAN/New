from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TravelRequest, User
from .serializer import TravelRequestSerializer, UserSerializer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

# Initialize the ChatGroq instance for generating itineraries
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",  # Replace with your Groq API key
    model_name="llama-3.3-70b-versatile"
)

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests: {interests}. Provide a brief, bulleted itinerary."),
    ("human", "Create an itinerary for my day trip.")
])

# Create User API View
class UserCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        # Fetch all users from the User model
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# TravelRequest Create API View
class TravelRequestCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Retrieve the user ID from the request data
        user_id = request.data.get('user_id')
        
        # Ensure the user exists before proceeding
        

        # Get city, interests, travel date, and time from the request data
        city = request.data.get('city')
        interests = request.data.get('interests')
        travel_date = request.data.get('travel_date')
        travel_time = request.data.get('travel_time')

        if not city or not interests or not travel_date or not travel_time:
            return Response({"error": "City, interests, travel date, and travel time are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate itinerary using Groq AI
        state = {
            "messages": [HumanMessage(content=f"Create an itinerary for a day trip to {city} based on the following interests: {', '.join(interests)}")],
            "city": city,
            "interests": interests,
            "itinerary": ""
        }

        # Call the AI model to generate itinerary
        response = llm.invoke(itinerary_prompt.format_messages(city=city, interests=','.join(interests)))
        itinerary = response.content  # Get the AI-generated itinerary

        # Create the TravelRequest instance with AI-generated itinerary
        travel_request = TravelRequest.objects.create(
            user=user_id,  # Associate the travel request with the user object
            city=city,
            interests=interests,
            travel_date=travel_date,
            travel_time=travel_time,
            itinerary=itinerary  # Save the AI-generated itinerary
        )

        # Serialize the TravelRequest instance
        serializer = TravelRequestSerializer(travel_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])   
def get_itinerary_by_user(request):
        user_id = request.GET.get('user_id')
        # Fetch all TravelRequests for the given user ID
        travel_requests = TravelRequest.objects.filter(user=user_id)
        
        # Check if there are any travel requests
        if not travel_requests:
            return Response({"error": "No travel requests found for the given user."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the travel requests
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API view to get a user's travel requests
@api_view(['GET'])
def get_user_travel_requests(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        travel_requests = TravelRequest.objects.filter(user=user)
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
# API view to get all users (No need for get_users method inside TravelRequestCreateAPIView)
@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# API view to create a user
@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API view to delete a user by pk
@api_view(['DELETE'])
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# API view to update a user
@api_view(['PUT'])
def put_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
