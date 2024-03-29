from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import ParticipantProfile, InstructorProfile
from seminar.serializers import ParticipantSeminarSerializer, InstructorSeminarSerializer
from seminar.models import UserSeminar


class UserSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = ('participant', 'instructor')
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    participant = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    role = serializers.ChoiceField(choices=ROLE_CHOICES, write_only=True)
    university = serializers.CharField(allow_blank=True, write_only=True, required=False)
    accepted = serializers.NullBooleanField(write_only=True, required=False)
    company = serializers.CharField(allow_blank=True, write_only=True, required=False)
    year = serializers.IntegerField(allow_null=True, write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'date_joined',
            'participant',
            'instructor',
            'role',
            'university',
            'accepted',
            'company',
            'year',
        )

    def get_participant(self, user):
        if hasattr(user, 'participant'):
            return ParticipantProfileSerializer(user.participant, context=self.context).data
        return None

    def get_instructor(self, user):
        if hasattr(user, 'instructor'):
            return InstructorProfileSerializer(user.instructor, context=self.context).data
        return None

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if bool(first_name) ^ bool(last_name):
            raise serializers.ValidationError("First name and last name should appear together.")
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            raise serializers.ValidationError("First name or last name should not have number.")

        role = data.get('role')
        serializer = None
        data_copied = data.copy()
        if not role:
            if hasattr(self.instance, 'participant'):
                data_copied.pop('accepted', None)
                serializer = ParticipantProfileSerializer(self.instance.participant, data=data_copied, partial=True)
                serializer.is_valid(raise_exception=True)
            if hasattr(self.instance, 'instructor'):
                serializer = InstructorProfileSerializer(self.instance.participant, data=data_copied, partial=True)
                serializer.is_valid(raise_exception=True)
        else:
            data_copied.update(user=None)
            if role == 'participant':
                serializer = ParticipantProfileSerializer(data=data_copied)
            elif role == 'instructor':
                serializer = InstructorProfileSerializer(data=data_copied)
            serializer.is_valid(raise_exception=True)

        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        university = validated_data.pop('university', '')
        accepted = validated_data.pop('accepted', None)
        company = validated_data.pop('company', '')
        year = validated_data.pop('year', None)
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        if role == 'participant':
            ParticipantProfile.objects.create(
                user=user,
                university=university,
                accepted=accepted,
            )
        elif role == 'instructor':
            InstructorProfile.objects.create(
                user=user,
                company=company,
                year=year,
            )
        return user

    def update(self, instance, validated_data):
        if hasattr(instance, 'participant'):
            participant = instance.participant
            participant.university = validated_data.pop('university', participant.university)
            participant.save()
        if hasattr(instance, 'instructor'):
            instructor = instance.instructor
            instructor.company = validated_data.pop('company', instructor.company)
            instructor.year = validated_data.pop('year', instructor.year)
            instructor.save()
        super(UserSerializer, self).update(instance, validated_data)


class ParticipantProfileSerializer(serializers.ModelSerializer):
    seminars = serializers.SerializerMethodField(read_only=True)
    accepted = serializers.NullBooleanField(required=True)

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'user',
            'university',
            'accepted',
            'seminars',
        )
        extra_kwargs = {'user': {'write_only': True, 'allow_null': True}}

    def get_seminars(self, participant):
        user = participant.user
        queryset = UserSeminar.objects.filter(user=user, role='participant')
        return ParticipantSeminarSerializer(queryset, many=True).data


class InstructorProfileSerializer(serializers.ModelSerializer):
    charge = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = (
            'id',
            'company',
            'year',
            'charge',
        )

    def get_charge(self, participant):
        user = participant.user
        try:
            queryset = UserSeminar.objects.get(user=user, role='instructor')
        except ObjectDoesNotExist:
            return None
        return InstructorSeminarSerializer(queryset).data
