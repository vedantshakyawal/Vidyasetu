from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

# --- FIREBASE & SERIALIZERS ---
from firebase_admin import firestore
from .serializers import UserSerializer

# Initialize Firestore client
db = firestore.client(database_id="vidyasetu")

# Secret code for Faculty/Admin registration
INSTITUTION_CODE = "SAIBALAJI_2026"

# ==========================================
# 1. LOGIN VIEW (With Device Enforcement)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username') # Note: Can be email if configured in Django
    password = request.data.get('password')
    role = request.data.get('role')
    device_id = request.data.get('device_id')

# testgit s
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # 1. Validate Role (Prevent a student from logging into the faculty portal)
        if role and user.role != role:
            return Response({'error': 'Role mismatch. Please select your correct role.'}, status=403)
            
        # 2. Single-Session Enforcement
        if device_id and user.device_id != device_id:
            # Delete any existing tokens for this user (logs them out of the old device)
            Token.objects.filter(user=user).delete()
            # Update and save the new device ID
            user.device_id = device_id
            user.save()
            
            # (Optional) Sync the new device_id to Firestore if you rely on it there
            try:
                db.collection('users').document(str(user.id)).update({'device_id': device_id})
            except Exception:
                pass # Fail silently if Firestore doc doesn't exist yet

        # 3. Issue Token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'role': user.role,
            'uid': user.id,
            'name': user.get_full_name() or user.username,
            'message': 'Login successful'
        }, status=200)
        
    return Response({'error': 'Invalid credentials'}, status=400)


# ==========================================
# 2. REGISTRATION VIEW (Replaces add_user)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_user(request):
    """
    Endpoint for Registration: POST /api/register/
    Handles both Student and Faculty/Admin registration.
    """
    data = request.data
    role = data.get('role', 'student')
    
    # 1. Institution Code Check for Faculty/Admin
    if role in ['faculty', 'admin']:
        provided_code = data.get('institution_code')
        if provided_code != INSTITUTION_CODE:
            return Response(
                {"error": "Invalid Institution Code. Registration denied."}, 
                status=403
            )

    serializer = UserSerializer(data=data)
    
    if serializer.is_valid():
        # 2. Save user in Django (handles password hashing)
        user = serializer.save()

        # 3. Sync user data to Firestore matching your exact PRD structure
        try:
            doc_ref = db.collection('users').document(str(user.id))
            doc_ref.set({
                'uid': user.id,
                'name': user.first_name or user.username,
                'email': user.email,
                'role': user.role,
                'roll_no': user.roll_no or "",
                'class': user.student_class or "",  # 11th / 12th
                'course': user.course or "",        # PCMB / PCMC
                'department': user.department or "",
                'device_id': user.device_id or "",
                'subjects': [] # Default empty array for faculty
            })
        except Exception as e:
            # If Firebase fails, delete the Django user to prevent ghost accounts
            user.delete()
            return Response({'error': f'Failed to sync with Firebase: {str(e)}'}, status=500)

        return Response({
            'message': 'Account successfully created!',
            'uid': user.id,
            'role': user.role
        }, status=201)
        
    return Response(serializer.errors, status=400)