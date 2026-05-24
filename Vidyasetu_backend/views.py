from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

# --- NEW IMPORTS FOR REGISTRATION & FIREBASE ---
from firebase_admin import firestore
from .serializers import UserSerializer

# Initialize Firestore client
db = firestore.client()

# Create your views here

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username , password=password)
    if user is not None:
        token, _= Token.objects.get_or_create(user=user)
        return Response({
            'token':token.key,
            'role':user.role,
            'uid': user.id,
            'name': user.get_full_name() or user.username
        })
    return Response({'error': 'Invalid credentials'}, status=400)

# --- NEW ADD USER VIEW ---
@api_view(['POST'])
@permission_classes([AllowAny]) # We'll lock this down to Admins later
def add_user(request):
    """
    Endpoint for Admins to register a new Student or Faculty.
    POST /api/users/add/
    """
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        # 1. Save user in Django (handles password hashing & local auth)
        user = serializer.save()

        # 2. Sync user data to Firestore matching your PRD structure
        try:
            doc_ref = db.collection('users').document(str(user.id))
            doc_ref.set({
                'uid': user.id,
                'name': user.first_name or user.username,
                'email': user.email,
                'role': user.role,
                'department': user.department,
                'roll_no': user.roll_no,
                'subjects': [] # Default empty array, assigned later
            })
        except Exception as e:
            # If Firebase fails, delete the Django user to prevent ghost accounts
            user.delete()
            return Response({'error': f'Failed to sync with Firebase: {str(e)}'}, status=500)

        return Response({
            'message': 'User successfully created!',
            'uid': user.id,
            'role': user.role
        }, status=201)
        
    return Response(serializer.errors, status=400)

            