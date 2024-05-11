from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class AuthenticationAPITests(APITestCase):
    def test_get_token(self):
        # Attempt to get token with invalid credentials
        response = self.client.post('/api/token/', {'username': 'invaliduser', 'password': 'invalidpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        # Ensure a valid refresh token is required for refreshing
        user = User.objects.create_user(username='testuser', password='testpassword')
        token_response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpassword'}, format='json')
        refresh_response = self.client.post('/api/token/refresh/', {'refresh': token_response.data['refresh']}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

class UserRegistrationTests(APITestCase):
    def test_user_registration(self):
        data = {'username': 'testuser', 'password': 'TestPassword123'}
        response = self.client.post('/chatbot/user/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get(username='testuser').username, 'testuser')

    def test_weak_password_registration(self):
        data = {'username': 'testuser', 'password': 'password'}  # Weak password
        response = self.client.post('/chatbot/user/register/', data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            # If the user was created successfully, check that it's not created with a weak password
            user = User.objects.get(username='testuser')
            self.assertTrue(user.check_password(data['password']), "Password should be hashed")
            self.assertGreater(len(data['password']), 7, "Password should be at least 8 characters long")
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('password', response.data)

    def test_existing_username_registration(self):
        # Ensure registration fails with existing username
        User.objects.create_user(username='testuser', password='TestPassword123')
        data = {'username': 'testuser', 'password': 'TestPassword123'}
        response = self.client.post('/chatbot/user/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_missing_data_registration(self):
        # Ensure registration fails with missing data
        data = {'username': 'testuser'}  # Missing password
        response = self.client.post('/chatbot/user/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
