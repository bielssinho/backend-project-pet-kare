from rest_framework.views import APIView, Request, Response, status
from rest_framework.pagination import PageNumberPagination
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from django.shortcuts import get_object_or_404


class PetsView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        req_params = request.query_params.get("trait", None)

        if req_params:
            pets = Pet.objects.filter(traits__name__icontains=req_params)

            result_page = self.paginate_queryset(pets, request, view=self)
            serializer = PetSerializer(result_page, many=True)

            return self.get_paginated_response(serializer.data)
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:

        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits")

        group_obj = Group.objects.filter(
            scientific_name__iexact=group["scientific_name"]
        ).first()

        if not group_obj:
            group_obj = Group.objects.create(**group)

        pet_obj = Pet.objects.create(**serializer.validated_data, group_id=group_obj.id)

        for trait_dict in traits:
            trait_obj = Trait.objects.filter(
                name__iexact=trait_dict["name"]
            ).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet_obj.traits.add(trait_obj)

        serializer = PetSerializer(pet_obj)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PetsDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        seralizer = PetSerializer(pet)

        return Response(seralizer.data, status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group_data: dict = serializer.validated_data.pop("group", None)

        if group_data:
            try:
                group_obj = Group.objects.get(scientific_name=group_data["scientific_name"])

            except Group.DoesNotExist:
                group_obj = Group.objects.create(**group_data)

            pet.group = group_obj

        traits_data = serializer.validated_data.pop("traits", None)
        if traits_data:
            try:
                for trait in traits_data:
                    trait_dict: dict = trait
                    trait_obj = pet.traits.filter(name__iexact=trait_dict["name"]).first()

            except Trait.DoesNotExist:
                trait_obj = Trait.objects.create(**traits_data)

            pet.traits.add(trait_obj)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
