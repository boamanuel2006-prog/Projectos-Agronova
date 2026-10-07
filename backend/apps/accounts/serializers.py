from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Profile, Farm

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'is_verified', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'is_verified', 'is_staff', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(write_only=True, max_length=160)
    role = serializers.ChoiceField(choices=Profile.Role.choices, default=Profile.Role.FARMER, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'full_name', 'role']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        role = validated_data.pop('role', Profile.Role.FARMER)
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, full_name=full_name, role=role)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['user', 'full_name', 'role', 'bio', 'photo', 'verification_status', 'city', 'province']
        read_only_fields = ['role', 'verification_status']

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        user = authenticate(email=attrs['email'].lower(), password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Credenciais inválidas.')
        if not user.is_active:
            raise serializers.ValidationError('Conta desativada.')
        attrs['user'] = user
        return attrs
