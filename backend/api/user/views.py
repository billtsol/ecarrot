"""
Views for the user API
"""

from rest_framework import ( # type: ignore
  generics,
  authentication,
  permissions
)
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.settings import api_settings # type: ignore
from user.serializers import (
  UserSerializer,
  AuthTokenSerializer,
)

class CreateUserView(generics.CreateAPIView):
  """Create a new user in the system"""
  serializer_class = UserSerializer

'''
ObtainAuthToken is a class-based view in Django REST Framework (DRF) 
that provides an endpoint for obtaining an authentication token. 
It allows users to authenticate via their credentials (usually 
username and password) and receive a token, 
which can then be used for subsequent authenticated requests'''
class CreateTokenView(ObtainAuthToken):
  """Create a new auth token for user"""
  serializer_class = AuthTokenSerializer
  renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

'''
The generics.RetrieveUpdateAPIView is a class in Django REST Framework
that provides functionality for retrieving and updating an object, 
handling GET and PUT or PATCH requests automatically.
'''
class ManageUserView(generics.RetrieveUpdateAPIView):
  """Manage the authenticated user"""
  serializer_class = UserSerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]

  def get_object(self):
    """Retrieve and return authenticated user"""
    return self.request.user