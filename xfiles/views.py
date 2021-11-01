from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from .serializers import *

# REST API
class XFileTypeListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới loại hồ sơ'''
    serializer_class = XFileTypeSerializer
    queryset = XFileType.objects.all()

class XFileTypeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa loại hồ sơ'''
    serializer_class = XFileTypeSerializer
    queryset = XFileType.objects.all()

class XFileListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới'''
    serializer_class = XFileSerializer
    queryset = XFile.objects.all()

    # Ghi đè funtion perform_create để khởi tạo giá trị mặc định cho XFile
    def perform_create(self, serializer):
        xfile = serializer.save()
        xfile.init_content()
        xfile.creator = self.request.user

class XFileRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa hồ sơ mục tiêu'''
    serializer_class = XFileSerializer
    queryset = XFile.objects.all()

class XFileContentList(generics.ListAPIView):
    '''Liệt kê content của hồ sơ mục tiêu'''
    serializer_class = ContentSerializer

    def get_queryset(self):
        xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        return xfile.contents.all()

class XFileDetailListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới detail của 1 trường dữ liệu của hồ sơ mục tiêu'''
    serializer_class = DetailSerializer

    def get_queryset(self):
        xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        self.content = get_object_or_404(xfile.contents.all(), id=self.kwargs['content_pk'])
        return self.content.details.all()

    # Ghi đè funtion perform_create để khởi tạo giá trị cho detail
    def perform_create(self, serializer):
        detail = serializer.save()
        detail.content = self.content
        detail.save()

class XFileDetailRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa detail của 1 trường dữ liệu của hồ sơ mục tiêu'''
    serializer_class = DetailSerializer
    lookup_url_kwarg = 'detail_pk'

    def get_queryset(self):
        self.xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        content = get_object_or_404(self.xfile.contents.all(), id=self.kwargs['content_pk'])
        return content.details.all()

    def update(self, request, *args, **kwargs):
        self.get_object().editor = request.user
        return super().update(request, *args, **kwargs)
    