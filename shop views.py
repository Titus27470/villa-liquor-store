from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, Product, Order
from .serializers import UserSerializer, ProductSerializer, OrderSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

# User registration
class RegisterUser(generics.CreateAPIView):
    serializer_class = UserSerializer

# User login
class LoginUser(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=400)

# List products
class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Manage individual product
class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Place order
class PlaceOrder(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = Product.objects.get(id=self.request.data['product'])
        quantity = int(self.request.data['quantity'])
        total_price = product.price * quantity
        serializer.save(
            user=self.request.user,
            total_price=total_price,
            payment_status='Pending'
        )
        # reduce stock
        product.stock -= quantity
        product.save()

# User's orders
class UserOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)