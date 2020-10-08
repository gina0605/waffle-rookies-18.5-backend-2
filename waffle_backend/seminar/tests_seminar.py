from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
import datetime

from user.models import InstructorProfile, ParticipantProfile
from seminar.models import Seminar, UserSeminar

class PostSeminar(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_token = 'Token ' + Token.objects.create(user=part).key

        ParticipantProfile.objects.create(
            user=part,
        )

        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'Token ' + Token.objects.create(user=partinst).key

        ParticipantProfile.objects.create(
            user=partinst,
        )

        InstructorProfile.objects.create(
            user=partinst,
        )

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'Token ' + Token.objects.create(user=inst).key

        InstructorProfile.objects.create(
            user=inst,
        )

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
        )

        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            role="participant",
        )

        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role="instructor",
        )

    def test_post_seminar_unauthorized(self):
        response = self.client.post(         # Unauthorized
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_noninstructor(self):
        response = self.client.post(         # Not instructor
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.part_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_already_instructor(self):
        response = self.client.post(         # Already instructing another seminar
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_incomplete_request(self):
        response = self.client.post(         # Name blank
            '/api/v1/seminar/',
            json.dumps({
                "name": "",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No capacity
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No count
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No time
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_wrong_request(self):
        response = self.client.post(         # capacity not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": "a",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # capacity < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": -1,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": "a",
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": -1,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # time format wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




