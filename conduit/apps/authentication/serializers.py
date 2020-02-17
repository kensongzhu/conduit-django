from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # The client should not able to send a token along with a registration request.
    # Making `token` read only handles for us
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # List all of fields that could possibly be included in a request
        # or a response, including fields specified explicitly above
        fields = ['username', 'email', 'password', 'token']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(min_length=8, max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating t hat they've provided an email
        # and password and that this combination matches one of the users in our database.
        email = attrs.get('email', None)
        password = attrs.get('password', None)

        # Raise an exception if an email is not provided
        if not email:
            raise serializers.ValidationError('An email address is required to login.')

        if not password:
            raise serializers.ValidationError('A password is required to login.')

        # The `authenticate` method is provided by Django and handlers checking
        # for a user that matches this email/password combination. Notice how
        # pass `email` as the `username` value since in our `USERNAME_FIELD` as `email`
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if not user:
            raise serializers.ValidationError('A user with this email and password was not found.')

        # Django provides a flag on our `User` model called `is_active`, The purpose
        # of this flag to tell us whether the user has been banned
        # or deactivated. This will almost never be the case, but
        # it is worth checking. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data
        # This is t he data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    # Password must be at least 8 characters, but no more than 128 characters
    # These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so lets just stick with the defaults
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'token']

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only = True`, like we did for password
        # above. The reason we want to use `read_only_fields` here is that
        # we don't need to specify anything else about the field. The
        # password field needed the `min_length` and `max_length`
        # but that isn't the case for the token field
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User"""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # Django provides a function that handles hashing and salting password
        # This means we need to remove the password field from the
        # `validated-data` dictionary before iterating over it
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            # For the keys remaining in `validated_data`, we will set then on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password:
            # `set_password` handles all of security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out the `set_password` does not save the model.
        instance.save()

        return instance
