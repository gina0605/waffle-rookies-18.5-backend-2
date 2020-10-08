from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
import datetime

from user.models import InstructorProfile, ParticipantProfile
from seminar.models import Seminar, UserSeminar

class PostSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_token = 'Token ' + Token.objects.create(user=part).key
        ParticipantProfile.objects.create(user=part)

        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'Token ' + Token.objects.create(user=partinst).key
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'Token ' + Token.objects.create(user=inst).key
        InstructorProfile.objects.create(user=inst)

        inst2 = User.objects.create_user(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_token = 'Token ' + Token.objects.create(user=inst2).key
        self.inst2_id = inst2.id
        InstructorProfile.objects.create(user=inst2)

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

        response = self.client.post(         # online wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
                "online": "dd"
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar(self):
        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertTrue(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.partinst_id)
        self.assertEqual(instructor["username"], "partinst")
        self.assertEqual(instructor["email"], "partinst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)

        seminar = Seminar.objects.get(id=data["id"])
        self.assertEqual(seminar.name, "seminar2")
        self.assertEqual(seminar.capacity, 9)
        self.assertEqual(seminar.count, 4)
        self.assertTrue(hasattr(seminar, "time"))
        self.assertTrue(seminar.online)
        userseminar = seminar.user_seminars.get()
        self.assertEqual(userseminar.user.username, "partinst")
        self.assertEqual(userseminar.role, "instructor")
        self.assertIsNone(userseminar.dropped_at)

        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
                "online": "F",
            }),
            HTTP_AUTHORIZATION=self.inst2_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertFalse(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst2_id)
        self.assertEqual(instructor["username"], "inst2")
        self.assertEqual(instructor["email"], "inst2@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)

        seminar = Seminar.objects.get(id=data["id"])
        self.assertEqual(seminar.name, "seminar2")
        self.assertEqual(seminar.capacity, 9)
        self.assertEqual(seminar.count, 4)
        self.assertTrue(hasattr(seminar, "time"))
        self.assertFalse(seminar.online)
        userseminar = seminar.user_seminars.get()
        self.assertEqual(userseminar.user.username, "inst2")
        self.assertEqual(userseminar.role, "instructor")
        self.assertIsNone(userseminar.dropped_at)

        self.assertEqual(Seminar.objects.count(), 3)
        self.assertEqual(UserSeminar.objects.count(), 4)


class PutSeminarSeminaridTestCase(TestCase):
    client = Client()

    def setUp(self):
        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'Token ' + Token.objects.create(user=partinst).key
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'Token ' + Token.objects.create(user=inst).key
        self.inst_id = inst.id
        InstructorProfile.objects.create(user=inst)

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
            online=False,
        )
        self.seminar_id = seminar.id
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            role="participant",
            dropped_at=timezone.localtime(),
        )
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role="instructor",
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=11,
            count=6,
            time=datetime.time(hour=15, minute=40),
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar2,
            role="instructor",
        )

    def test_put_seminar_seminarid_unauthorized(self):
        response = self.client.put(         # Unauthorized
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_not_instructor(self):
        response = self.client.put(         # Not instructor of the seminar
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_wrong_id(self):
        response = self.client.put(         # wrong id
            '/api/v1/seminar/3/',
            json.dumps({
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_wrong_request(self):
        response = self.client.put(         # Capacity smaller than number of participants
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "capacity": 0,
                "name": "Seminar1",
                "online": "T",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.capacity, 10)
        self.assertEqual(seminar.name, "seminar1")
        self.assertFalse(seminar.online)

        response = self.client.put(         # Capacity not number
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "capacity": "a",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.capacity, 10)

        response = self.client.put(         # count < 0
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "count": -1,
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)
        self.assertEqual(seminar.name, "seminar1")

        response = self.client.put(         # count not number
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "count": "z",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)

        response = self.client.put(         # time wrong format
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "time": "12",
                "count": 7,
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)

        response = self.client.put(         # wrong online
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "online": "d"
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertFalse(seminar.online)

    def test_put_seminar_seminarid(self):
        response = self.client.put(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
                "capacity": 1,
                "count": 20,
                "time": "10:10",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar_id)
        self.assertEqual(data["name"], "Seminar1")
        self.assertEqual(data["capacity"], 1)
        self.assertEqual(data["count"], 20)
        self.assertEqual(data["time"], "10:10")
        self.assertFalse(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst_id)
        self.assertEqual(instructor["username"], "inst")
        self.assertEqual(instructor["email"], "inst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertIn("participants", data)
        self.assertEqual(len(data["participants"]), 1)
        participant = data["participants"][0]
        self.assertEqual(participant["id"], self.partinst_id)
        self.assertEqual(participant["username"], "partinst")
        self.assertEqual(participant["email"], "partinst@mail.com")
        self.assertEqual(participant["first_name"], "")
        self.assertEqual(participant["last_name"], "")
        self.assertIn("joined_at", participant)
        self.assertFalse(participant["is_active"])
        self.assertIsNotNone(participant["dropped_at"])

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "Seminar1")
        self.assertEqual(seminar.capacity, 1)
        self.assertEqual(seminar.count, 20)
        self.assertFalse(seminar.online)


class GetSeminarSeminaridTestCase(TestCase):
    client = Client()

    def setUp(self):
        inst = User.objects.create(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_id = inst.id
        InstructorProfile.objects.create(user=inst)

        inst2 = User.objects.create(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_id = inst2.id
        InstructorProfile.objects.create(user=inst2)

        part = User.objects.create(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_id = part.id
        ParticipantProfile.objects.create(user=part)

        partinst = User.objects.create(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        seminar = Seminar.objects.create(
            name="seminar",
            capacity=10,
            count=5,
            time=timezone.localtime(),
        )
        self.seminar_id = seminar.id
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role="instructor"
        )
        UserSeminar.objects.create(
            user=inst2,
            seminar=seminar,
            role="instructor"
        )
        UserSeminar.objects.create(
            user=part,
            seminar=seminar,
            role="participant",
            dropped_at=timezone.localtime(),
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            role="participant"
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=11,
            count=6,
            time=timezone.localtime(),
            online=False,
        )
        self.seminar2_id = seminar2.id
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar2,
            role="instructor"
        )

    def test_get_seminar_seminarid_wrong_id(self):
        response = self.client.get(         # wrong id
            '/api/v1/seminar/10/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_seminar(self):
        response = self.client.get(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar_id)
        self.assertEqual(data["name"], "seminar")
        self.assertEqual(data["capacity"], 10)
        self.assertEqual(data["count"], 5)
        self.assertIn("time", data)
        self.assertTrue(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 2)

        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst_id)
        self.assertEqual(instructor["username"], "inst")
        self.assertEqual(instructor["email"], "inst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)

        instructor2 = data["instructors"][1]
        self.assertEqual(instructor2["id"], self.inst2_id)
        self.assertEqual(instructor2["username"], "inst2")
        self.assertEqual(instructor2["email"], "inst2@mail.com")
        self.assertEqual(instructor2["first_name"], "")
        self.assertEqual(instructor2["last_name"], "")
        self.assertIn("joined_at", instructor2)
        self.assertIn("participants", data)
        self.assertEqual(len(data["participants"]), 2)

        participant = data["participants"][0]
        self.assertEqual(participant["id"], self.part_id)
        self.assertEqual(participant["username"], "part")
        self.assertEqual(participant["email"], "part@mail.com")
        self.assertEqual(participant["first_name"], "")
        self.assertEqual(participant["last_name"], "")
        self.assertIn("joined_at", participant)
        self.assertFalse(participant["is_active"])
        self.assertIsNotNone(participant["dropped_at"])

        participant2 = data["participants"][1]
        self.assertEqual(participant2["id"], self.partinst_id)
        self.assertEqual(participant2["username"], "partinst")
        self.assertEqual(participant2["email"], "partinst@mail.com")
        self.assertEqual(participant2["first_name"], "")
        self.assertEqual(participant2["last_name"], "")
        self.assertIn("joined_at", participant2)
        self.assertTrue(participant2["is_active"])
        self.assertIsNone(participant2["dropped_at"])

        response = self.client.get(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar2_id),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 11)
        self.assertEqual(data["count"], 6)
        self.assertIn("time", data)
        self.assertFalse(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 1)

        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.partinst_id)
        self.assertEqual(instructor["username"], "partinst")
        self.assertEqual(instructor["email"], "partinst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)

        self.assertEqual(len(data["participants"]), 0)

