from rest_framework import serializers
from .models import User, EWasteItem, CollectionRequest

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with name and phone validation."""

    name = serializers.CharField(
        min_length=3,
        error_messages={"min_length": "Name must be at least 3 characters long."}
    )
    phone = serializers.CharField(
        min_length=10, max_length=10,
        error_messages={
            "min_length": "Phone number must be exactly 10 digits.",
            "max_length": "Phone number must be exactly 10 digits."
        }
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'address', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Ensure name is at least 3 characters long after trimming spaces."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value

    def validate_phone(self, value):
        """Ensure phone number contains exactly 10 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value

    def validate(self, data):
        """Cross-field validation: Ensure address is not empty."""
        if not data.get('address'):
            raise serializers.ValidationError({"address": "This field is required."})
        return data


class EWasteItemSerializer(serializers.ModelSerializer):
    """Serializer for e-waste items with file handling and validation."""

    image = serializers.ImageField(required=False, allow_null=True)
    document = serializers.FileField(required=False, allow_null=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = EWasteItem
        fields = ['id', 'name', 'category', 'condition', 'owner', 'owner_name', 
                  'image', 'document', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_image(self, value):
        """Validate image file size and type."""
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("Image file size cannot exceed 5MB.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("File must be an image.")
        return value

    def validate_document(self, value):
        """Validate document file size and type."""
        if value:
            if value.size > 10 * 1024 * 1024:  # 10MB limit
                raise serializers.ValidationError("Document file size cannot exceed 10MB.")
            allowed_types = ['application/pdf', 'application/msword', 
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("File must be a PDF or Word document.")
        return value


class CollectionRequestSerializer(serializers.ModelSerializer):
    """Serializer for CollectionRequest with improved validation."""

    user_name = serializers.CharField(source='user.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = CollectionRequest
        fields = ['id', 'user', 'user_name', 'item', 'item_name', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Ensure status is valid."""
        valid_statuses = ['pending', 'in_progress', 'completed']
        if 'status' in data and data['status'] not in valid_statuses:
            raise serializers.ValidationError({"status": "Invalid status value."})
        return data
