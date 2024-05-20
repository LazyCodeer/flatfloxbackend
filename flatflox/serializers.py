from rest_framework.serializers import ModelSerializer
from flatflox.models import User, PGModel, Location, Rating, WorkingCities

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','name', 'email', 'contact', 'isVerified')

class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'address', 'latitude', 'longitude']

class PGModelSerializer(ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = PGModel
        fields = [
            'id', 'name', 'pg_type', 'location', 'starting_price',
            'gender', 'sharing_type', 'amenities', 'available_rooms', 'rating'
        ]
        extra_kwargs = {
            'rating': {'required': False}
        }

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location = Location.objects.create(**location_data)
        pg = PGModel.objects.create(location=location, **validated_data)
        return pg
    

class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'rating_value', 'pg', 'user', 'date_created']
        read_only_fields = ['id', 'date_created'] 

class WorkingCitiesSerializer(ModelSerializer):
    class Meta:
        model = WorkingCities
        fields = '__all__'