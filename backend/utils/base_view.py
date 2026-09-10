from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import generics, mixins, views
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class BaseCreateModelViewSet(mixins.CreateModelMixin, GenericViewSet):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_delete=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class BaseModelViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['create_time', 'update_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_delete=False)

    # def perform_destroy(self, instance):
    #     instance.is_delete = True
    #     instance.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    # def perform_create(self, serializer):
    #     serializer.save(create_by=self.request.user)
    #
    # def perform_update(self, serializer):
    #     return super().perform_update(serializer)