from django.db import models

class User(models.Model):
    # Choices for food preferences (you can expand this based on your needs)
    FOOD_PREFERENCES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('VEGAN', 'Vegan'),
        ('ANY', 'Any'),
    ]
    
    age = models.IntegerField()
    name = models.CharField(max_length=100)
    travel_destination = models.CharField(max_length=200)
    avg_budget = models.IntegerField()
    food_preference = models.CharField(
        max_length=10,
        choices=FOOD_PREFERENCES,
        default='ANY'
    )
    travel_duration = models.IntegerField()

    def __str__(self):
        return self.name


class TravelInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggested_accommodation = models.CharField(max_length=255)
    suggested_transportation = models.CharField(max_length=255)
    suggested_activities = models.TextField()
    recommended_budget = models.IntegerField()

    def __str__(self):
        return f"Travel Information for {self.user.name}"

class TravelRequest(models.Model):
    FOOD_PREFERENCES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('VEGAN', 'Vegan'),
        ('ANY', 'Any'),
    ]
    
    user = models.CharField(max_length=100)
    city = models.CharField(max_length=200)
    avg_budget = models.IntegerField()
    food_prefference = models.CharField(
        max_length=10,
        choices=FOOD_PREFERENCES,
        default='ANY'
    )
    interests = models.TextField()
    travel_date = models.DateField()
    travel_duration = models.IntegerField()
    weather = models.TextField(blank=True,null=True)
    itinerary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"TravelRequest for {self.user.name} to {self.city} on {self.travel_date} at {self.travel_duration}"
