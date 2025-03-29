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

# Groq help me out
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",  
    model_name="llama-3.3-70b-versatile"
)

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a {travel_duration} day trip itinerary along with daily weather without any introduction statement for {city} based on the user's interests: {interests} average budget {avg_budget} and food prefference {food_prefference}."
    "Provide a brief, bulleted itinerary." "Also suggest local restaurants and delicacies."),
    ("human", "Create an itinerary for my multiple days trip.")
])

# I need to create users obviously
class UserCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        # A general fetch call
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# TravelRequest Create API View
class TravelRequestCreateAPIView(APIView):
    def post(self, request, *args,**kwargs):
        user_id = request.data.get('user_id')
        

        city = request.data.get('city')
        interests = request.data.get('interests')
        travel_date = request.data.get('travel_date')
        travel_duration = request.data.get('travel_duration')
        avg_budget = request.data.get('avg_budget')
        food_prefference = request.data.get('food_prefference')

        if not city or not interests or not travel_date or not travel_duration:
            return Response({"error": "City, interests, travel date, and travel duration are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Groq AI is cool 
        state = {
            "messages": [HumanMessage(content=f"Create an itinerary for  {travel_duration} day trip without any introduction statement suggesting one or two places per day to {city} based on the following interests: {', '.join(interests)} and providing food options and budget accordingly.The food options should be the famous delicacies of that place and mention the restaurant too.")],
            "city": city,
            "interests": interests,
            "avg_budget":avg_budget,
            "food_prefference":food_prefference,
            "itinerary": "",
            "weather":""
        }

        response = llm.invoke(itinerary_prompt.format_messages(city=city, interests=','.join(interests), travel_duration=travel_duration,avg_budget=avg_budget,food_prefference=food_prefference))

        itinerary = response.content  


        travel_request = TravelRequest.objects.create(
            user=user_id,  
            city=city,
            interests=interests,
            travel_date=travel_date,
            travel_duration=travel_duration,
            avg_budget = avg_budget,
            food_prefference = food_prefference,
            itinerary=itinerary  # Need to save in database
        )

        serializer = TravelRequestSerializer(travel_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])   
def get_itinerary_by_user(request):
        user_id = request.GET.get('user_id')
        travel_requests = TravelRequest.objects.filter(user=user_id)
        if not travel_requests:
            return Response({"error": "No travel requests found for the given user."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialization is important
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# this one would give travel requests
@api_view(['GET'])
def get_user_travel_requests(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        travel_requests = TravelRequest.objects.filter(user=user)
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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
