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
    ("system", 
        "You are a structured travel assistant. Always generate a {travel_duration}-day travel itinerary for {city}, ensuring the output is formatted as follows:"
        "\n\n---"
        "\n*Day 1:*"
        "\n- **Weather:** (Weather condition, Temperature in °C)"
        "\n- **Visit:** (List 1-2 attractions)"
        "\n- **Food:**"
        "\n  - *Breakfast:* (Dish) at (Restaurant) (₹Price)"
        "\n  - *Lunch:* (Dish) at (Restaurant) (₹Price)"
        "\n  - *Dinner:* (Dish) at (Restaurant) (₹Price)"
        "\n- **Stay:** (Hotel Name or similar) (₹Price per night)"
        "\n\n*Day 2:*"
        "\n- Repeat the same format for each day..."
        "\n\n---"
        "\nAt the end, always include:"
        "\n- **Total estimated cost for the {travel_duration}-day trip:** ₹ (Breakdown of stay, food, and transport)"
        "\n- **Local delicacies to try as per the food prefference:** (List famous dishes of {city})"
        "\n\n---"
        "\n**Maintain this format consistently, regardless of the inputs provided.**"
        "\n- **User Interests:** {interests}"
        "\n- **Average Budget:** ₹{avg_budget}"
        "\n- **Food Preference:** {food_prefference}"
    ),
    ("human", "Generate a structured itinerary for my trip.")
])

hotel_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a structured accommodation assistant. Identify all places in the {itinerary_entered} and provide a list of hotels along with booking link for each place. "
     "For each location, list all hotels along with their prices (sorted from cheapest to most expensive) and reviews."),
    ("human",
     "Generate a structured list of hotels for each place in the itinerary. "
     "Format the response as follows:\n"
     "- **Place Name**\n"
     "  - Hotel Name: Price, Review, Official Website Link\n"
     "  - Hotel Name: Price, Review, Official Website Link\n"
     "Ensure the hotels are grouped under their respective places and sorted by price in ascending order.")
])

restaurant_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a skilled restaurant finder. You need to find restaurants for user having {food_prefferences} in visiting places given in {itinerary_entered}"
    ),
    (
        "human",
        "Generate and list all the restaurants of my food preference present in visiting places mentioned in the itinerary"
        "Format the response as follows:\n"
        "- **Place Name**\n"
        "  - Restaurant Name: Price, Review\n"
        "  - Restaurant Name: Price, Review\n"
        "Ensure the restaurants are grouped under their respective places and sorted by price in ascending order."
    )
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
    "messages": [HumanMessage(content=(
        f"Generate a structured {travel_duration}-day travel itinerary for {city}."
        f"\n\nThe response **must always** follow this exact format:"
        f"\n---"
        f"\n*Day 1:*"
        f"\n- **Weather:** (e.g., Partly Cloudy, 25°C)"
        f"\n- **Visit:** (1-2 attractions per day)"
        f"\n- **Food:**"
        f"\n  - *Breakfast:* (Dish) at (Restaurant) (₹Price)"
        f"\n  - *Lunch:* (Dish) at (Restaurant) (₹Price)"
        f"\n  - *Dinner:* (Dish) at (Restaurant) (₹Price)"
        f"\n- **Stay:** (Hotel Name or similar) (₹Price per night)"
        f"\n\n*Day 2:*"
        f"\n- **Weather:** (e.g., Sunny, 28°C)"
        f"\n- **Visit:** (1-2 attractions per day)"
        f"\n- **Food:**"
        f"\n  - *Breakfast:* (Dish) at (Restaurant) (₹Price)"
        f"\n  - *Lunch:* (Dish) at (Restaurant) (₹Price)"
        f"\n  - *Dinner:* (Dish) at (Restaurant) (₹Price)"
        f"\n- **Stay:** (Hotel Name or similar) (₹Price per night)"
        f"\n\n(Repeat this format for all days...)"
        f"\n---"
        f"\nAt the end, **always include:**"
        f"\n- **Total Estimated Cost for {travel_duration} days:** ₹ (Breakdown of stay, food, transport)"
        f"\n- **Local Delicacies to Try:** (List of traditional dishes from {city})"
        f"\n\n---"
        f"\nEnsure that **every response strictly follows this format**, without any introduction or summary."
        f"\n- **User Interests:** {', '.join(interests)}"
        f"\n- **Food Preference:** {food_prefference}"
        f"\n- **Average Budget:** ₹{avg_budget}"
        f"\n- **Travel Duration:** {travel_duration} days"
    ))],
    "city": city,
    "interests": interests,
    "avg_budget": avg_budget,
    "food_prefference": food_prefference,
    "itinerary": "",
    "weather": ""
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
    
###############################################
    
@api_view(['DELETE'])
def delete_itinerary(request, user, itinerary_id):
    try:
        itinerary = TravelRequest.objects.get(id=itinerary_id, user=user)
    except TravelRequest.DoesNotExist:
        return Response({"error": "Itinerary not found for this user"}, status=status.HTTP_404_NOT_FOUND)

    itinerary.delete()
    return Response({"message": "Itinerary deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

###############################################

@api_view(['POST'])
def get_hotels_by_itinerary(request):
    itinerary_entered = request.data.get("itinerary")
    user_id = request.data.get("user_id")
    itinerary_id = request.data.get("itinerary_id")

    if not itinerary_entered:
        return Response({"error": "Itinerary is required"}, status=400)

    state = {
        "messages": [
            HumanMessage(
                content=(
                    f"List all the hotels present in the places given in {itinerary_entered} along with their booking link, "
                    "including their reviews and prices, sorted in ascending order of price."
                )
            )
        ]
    }

    response = llm.invoke(hotel_prompt.format_messages(itinerary_entered = itinerary_entered))  # Ensure this works correctly
    hotels = response.content if response else "No hotels found."

    return Response({"hotels": hotels})

#########################################################


@api_view(['POST'])
def get_restaurants(request):
    food_prefferences = request.data.get('food_prefferences')
    itinerary_entered = request.data.get('itinerary')

    if not food_prefferences or not itinerary_entered:
        return Response({"error":"Food preferences or itinerary not entered"},status = status.HTTP_404_NOT_FOUND)
    state = {
        "messages": [
            HumanMessage(
                content=(
                    f"List all the restaurants present in the places given in {itinerary_entered} according to {food_prefferences}, "
                    "including their reviews and prices, sorted in ascending order of price."
                )
            )
        ]
    }
    response = llm.invoke(restaurant_prompt.format_messages(itinerary_entered = itinerary_entered,food_prefferences = food_prefferences))
    restaurants = response.content if response else "No restaurants found"

    return Response({"restaurnats":restaurants})

############################################################

@api_view(['GET'])   
def get_itinerary_by_user(request):
        user_id = request.GET.get('user_id')
        travel_requests = TravelRequest.objects.filter(user=user_id)
        if not travel_requests:
            return Response({"error": "No travel requests found for the given user."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialization is important
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#######################################################

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


######################################################

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

#####################################################

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

####################################################

@api_view(['DELETE'])
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

####################################################

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

