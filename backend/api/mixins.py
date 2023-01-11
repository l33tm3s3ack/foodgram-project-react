from rest_framework import mixins, viewsets


class ListCreateRetrieveViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    """Mixin for UserViewset"""
    pass
