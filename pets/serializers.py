from rest_framework import serializers
from .models import SexPet

from groups.serializers import GroupSerializer
from traits.serializers import TraitsSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(choices=SexPet.choices, default=SexPet.NOTINFORMED)

    group = GroupSerializer()
    traits = TraitsSerializer(many=True)
