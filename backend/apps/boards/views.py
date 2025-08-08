from rest_framework import generics
from .models import Board
from .serializers import BoardSerializer

class BoardListView(generics.ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
