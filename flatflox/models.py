from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
# Create your models here.

class User(AbstractUser):
    contact = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120)
    profileImage = models.ImageField(upload_to='profile/',null=True, blank=True)
    isVerified = models.BooleanField(default=False)

    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

# Model for pgs
class PGModel(models.Model):
    name = models.CharField(max_length=255)
    PG_ROOMS = 'pg rooms'
    CO_LIVING = 'co-living'
    TYPE_CHOICES = [
        (PG_ROOMS, 'PG Rooms'),
        (CO_LIVING, 'Co-Living')
    ]
    pg_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    location = models.OneToOneField('Location', on_delete=models.CASCADE)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    MALE = 'male'
    FEMALE = 'female'
    UNISEX = 'unisex'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNISEX, 'Unisex')
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    sharing_type = models.CharField(max_length=50)
    amenities = models.JSONField()
    available_rooms = models.IntegerField()
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    state = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    pictures = models.ManyToManyField('PGPicture')

    def __str__(self):
        return self.name

# creating location model to store location of pgs and user
class Location(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.address
    

# pg picture
class PGPicture(models.Model):
    image = models.ImageField(upload_to='pg_images/', null=True, blank=True)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pg = models.ForeignKey(PGModel, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.pg.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update PG rating after saving a review
        self.pg.update_rating()
    
class WorkingCities(models.Model):
    city = models.CharField(max_length=120, blank=True, null=True)
    image = models.ImageField(upload_to='working_cities/', null=True, blank=True)