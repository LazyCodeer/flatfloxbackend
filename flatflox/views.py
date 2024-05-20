# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth
from rest_framework.decorators import api_view
from flatflox.models import User, PGModel, Location, Rating, WorkingCities
from flatflox.serializers import UserSerializer, PGModelSerializer, LocationSerializer, RatingSerializer, WorkingCitiesSerializer
import logging
from django.core.paginator import Paginator
from django.db import transaction

logger = logging.getLogger(__name__)

@api_view(['POST'])
def login_user(request):
    idToken = request.data.get('idToken')

    try:
        decodedToken = auth.verify_id_token(idToken)
        uid = decodedToken['uid']

        user = User.objects.filter(username=uid).first()
        if user is None:
            return Response({'error': 'Account do not exist', 'status': 'not_exists'})
        if user is not None and user.isVerified == False:
            user.isVerified = True
            user.save()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)
    except auth.ExpiredIdTokenError:
        return Response({'error': 'Token has expired', 'status': 'expired'}, status=401)
    except auth.InvalidIdTokenError:
        return Response({'error': 'Invalid token', 'status': 'invalid'}, status=401)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST', 'PATCH'])
def signup_user(request):
    try:
        idToken = request.data.get('idToken')
        name = request.data.get('name','')
        email = request.data.get('email','')
        contact = request.data.get('contact','')
        profileImage = request.FILES.get('profileImage','')

        # decoding firebase auth token
        decodedToken = auth.verify_id_token(idToken)
        uid = decodedToken['uid']

        # fetching user from database
        user = User.objects.filter(username=uid).first()

        if request.method == 'POST':
            if user is not None and user.isVerified:
                return Response({'error': 'Account already exists. Try to login', 'status' : 'exists'})
                
            if user is None:
                user = User.objects.create(username=uid, name=name, contact=contact, email=email)
                user_serializer = UserSerializer(user)
                return Response({'user_data': user_serializer.data, 'status':'created'})

        elif request.method == 'PATCH':
            if user is not None and user.isVerified:
                if name != '':
                    user.name = name
                if email != '':
                    user.email = email
                if profileImage != '':
                    user.profileImage = profileImage
                user.save()
                return Response({'status': 'Updated'})
            else:
                return Response({'error': 'Error While updating your info. please try in sometime'})

        return Response({'error': 'Invalid request method'}, status=400)

    except auth.ExpiredIdTokenError:
        logger.error('Token has expired')
        return Response({'error': 'Token has expired', 'status': 'expired'}, status=401)
    except auth.InvalidIdTokenError:
        logger.error('Invalid token')
        return Response({'error': 'Invalid token', 'status': 'invalid'}, status=401)
    except Exception as e:
        logger.error(e)
        return Response({'error': str(e)}, status=500)
        

'''
Adding new PG
'''
# adding new pg
@api_view(['POST', 'GET'])
def paid_guest(request):
    if request.method == 'POST':
        serializer = PGModelSerializer(data=request.data)
        if serializer.is_valid():
            location_serializer = LocationSerializer(data=request.data.get('location'))
            if location_serializer.is_valid():
                location = location_serializer.save()
                pg = serializer.save(location=location)
                return Response({'success': 'PG added successfully', 'data': PGModelSerializer(pg).data}, status=status.HTTP_201_CREATED)
            else:
                return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        page_number = request.query_params.get('page_number', 1)
        no_of_pg = request.query_params.get('no_of_pg', 10)

        pgs = PGModel.objects.all()
        paginator = Paginator(pgs, no_of_pg)
        page_obj = paginator.get_page(page_number)

        serializer = PGModelSerializer(page_obj, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@transaction.atomic
def create_pg(request):
    if request.method == 'POST':
        serializer = PGModelSerializer(data=request.data)
        if serializer.is_valid():
            # Check if a similar PG already exists
            name = serializer.validated_data.get('name')
            location_data = serializer.validated_data.get('location')
            existing_pgs = PGModel.objects.filter(name=name, location__address=location_data['address'])
            if existing_pgs.exists():
                return Response({'error': 'A similar PG already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# adding rating
@api_view(['POST'])
def add_rating(request):
    if request.method == 'POST':
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            pg_id = request.data.get('pg_id')
            user_rating = request.data.get('rating')
            user_id = request.data.get('user_id')

            try:
                pg = PGModel.objects.get(id=pg_id)
            except PGModel.DoesNotExist:
                return Response({'error': 'PG not found'}, status=status.HTTP_404_NOT_FOUND)

            # Calculate new rating
            num_ratings = Rating.objects.filter(pg=pg).count()
            new_rating = (pg.rating * num_ratings + user_rating) / (num_ratings + 1)
            pg.rating = new_rating
            pg.save()

            serializer.save()
            return Response({'success': 'Rating added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# get all working cities
@api_view(['GET'])
def get_working_cities(request):
    try:
        cities = WorkingCities.objects.all()
        serializer = WorkingCitiesSerializer(cities, many=True)
    except Exception as e:
        return Response({'error': e.message})
    
    return Response(serializer.data, status=status.HTTP_200_OK)