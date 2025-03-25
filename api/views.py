from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, EWasteItem, CollectionRequest
from .serializers import UserSerializer, EWasteItemSerializer, CollectionRequestSerializer
from rest_framework.pagination import PageNumberPagination
import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.db.models import Count
from .exceptions import CustomAPIException, NotFoundError, ValidationError as CustomValidationError

@api_view(['GET'])
def analytics_view(request):
    """Returns analytics data for dashboard."""
    
    total_users = User.objects.count()
    total_e_waste_items = EWasteItem.objects.count()
    
    # Count of e-waste items by category
    e_waste_by_category = EWasteItem.objects.values('category').annotate(count=Count('id'))
    
    # Count of collection requests by status
    collection_status_counts = CollectionRequest.objects.values('status').annotate(count=Count('id'))
    
    # User contributions (how many items each user has contributed)
    user_contributions = User.objects.annotate(total_items=Count('ewaste_items')).values('name', 'total_items')

    return Response({
        "total_users": total_users,
        "total_e_waste_items": total_e_waste_items,
        "e_waste_by_category": list(e_waste_by_category),
        "collection_status_counts": list(collection_status_counts),
        "user_contributions": list(user_contributions),
    })
# Configure logger
logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Creating new user with data: {request.data}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"User created successfully with ID: {response.data['id']}")
            return response
        except ValidationError as e:
            logger.error(f"Validation error while creating user: {str(e)}")
            raise CustomValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error while creating user: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while creating the user.")

    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Updating user {kwargs.get('pk')} with data: {request.data}")
            response = super().update(request, *args, **kwargs)
            logger.info(f"User {kwargs.get('pk')} updated successfully")
            return response
        except ObjectDoesNotExist:
            logger.error(f"User with ID {kwargs.get('pk')} not found")
            raise NotFoundError(f"User with ID {kwargs.get('pk')} not found")
        except Exception as e:
            logger.error(f"Unexpected error while updating user: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while updating the user.")

class EWasteItemViewSet(viewsets.ModelViewSet):
    queryset = EWasteItem.objects.all()
    serializer_class = EWasteItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Enable filtering by category and owner
    filterset_fields = ['category', 'owner']
    
    # Enable search by name and condition
    search_fields = ['name', 'category', 'condition']
    
    # Enable ordering by created_at or updated_at
    ordering_fields = ['created_at', 'updated_at', 'name'] 
    ordering = ['-created_at']  # Default ordering (newest first)
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Creating new e-waste item with data: {request.data}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"E-waste item created successfully with ID: {response.data['id']}")
            return response
        except ValidationError as e:
            logger.error(f"Validation error while creating e-waste item: {str(e)}")
            raise CustomValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error while creating e-waste item: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while creating the e-waste item.")

    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Updating e-waste item {kwargs.get('pk')} with data: {request.data}")
            response = super().update(request, *args, **kwargs)
            logger.info(f"E-waste item {kwargs.get('pk')} updated successfully")
            return response
        except ObjectDoesNotExist:
            logger.error(f"E-waste item with ID {kwargs.get('pk')} not found")
            raise NotFoundError(f"E-waste item with ID {kwargs.get('pk')} not found")
        except Exception as e:
            logger.error(f"Unexpected error while updating e-waste item: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while updating the e-waste item.")

class CollectionRequestViewSet(viewsets.ModelViewSet):
    queryset = CollectionRequest.objects.all()
    serializer_class = CollectionRequestSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Creating new collection request with data: {request.data}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"Collection request created successfully with ID: {response.data['id']}")
            return response
        except ValidationError as e:
            logger.error(f"Validation error while creating collection request: {str(e)}")
            raise CustomValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error while creating collection request: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while creating the collection request.")

    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Updating collection request {kwargs.get('pk')} with data: {request.data}")
            response = super().update(request, *args, **kwargs)
            logger.info(f"Collection request {kwargs.get('pk')} updated successfully")
            return response
        except ObjectDoesNotExist:
            logger.error(f"Collection request with ID {kwargs.get('pk')} not found")
            raise NotFoundError(f"Collection request with ID {kwargs.get('pk')} not found")
        except Exception as e:
            logger.error(f"Unexpected error while updating collection request: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while updating the collection request.")
    
class CollectionRequestAPI(APIView):
    def post(self, request):
        try:
            logger.info(f"Processing new collection request: {request.data}")
            request_data = request.data.copy()
            request_data['user'] = request.user.id if hasattr(request, 'user') else 1
            
            # Check if the e-waste item exists
            e_waste_item_id = request_data.get("e_waste_item")
            if not EWasteItem.objects.filter(id=e_waste_item_id).exists():
                logger.error(f"E-Waste item with ID {e_waste_item_id} not found")
                raise NotFoundError(f"E-Waste item with ID {e_waste_item_id} not found")

            serializer = CollectionRequestSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Collection request created successfully with ID: {serializer.data['id']}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.error(f"Validation error in collection request: {serializer.errors}")
            raise CustomValidationError(str(serializer.errors))
            
        except CustomAPIException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in collection request: {str(e)}")
            raise CustomAPIException("An unexpected error occurred while processing the collection request.")
