from rest_framework import generics

from api.models import Program
from api.serializers import ProgramSerializer


class ProgramList(generics.ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class ProgramDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
