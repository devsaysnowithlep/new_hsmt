from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import get_object_or_404, HttpResponse

from django_fsm import has_transition_perm

from xfiles.serializers import *
from xfiles.permissions import *
from users.permissions import *

def test(request, pk):
    xfile = get_object_or_404(XFile, pk=pk)
    users = get_users_can_view(xfile)
    xfiles = get_xfiles_can_view(request.user)
    print('users: ', users)
    print('xfiles: ', xfiles)
    return HttpResponse('ok')

# REST API
class XFileTypeListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới loại hồ sơ'''
    permission_classes = [IsAuthenticated, IsGiamdoc]
    serializer_class = XFileTypeSerializer
    queryset = XFileType.objects.all()

class XFileTypeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa loại hồ sơ'''
    permission_classes = [IsAuthenticated, IsGiamdoc]
    serializer_class = XFileTypeSerializer
    queryset = XFileType.objects.all()

class TargetListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới hướng-nhóm-địa bàn'''
    permission_classes = [IsAuthenticated]
    serializer_class = TargetSerializer
    queryset = Target.objects.all()

class TargetRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa hướng-nhóm-địa bàn'''
    permission_classes = [IsAuthenticated, TargetIsNotInUse]
    serializer_class = TargetSerializer
    queryset = Target.objects.all()

class XFileListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới'''
    permission_classes = [IsAuthenticated]
    serializer_class = XFileSerializer
    
    def get_queryset(self):
        return get_xfiles_can_view(self.request.user)

    # Ghi đè funtion perform_create để khởi tạo giá trị mặc định cho XFile
    def perform_create(self, serializer):
        xfile = serializer.save()
        xfile.init_content(by=self.request.user)
        xfile.creator = self.request.user
        xfile.save()

class XFileRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanEditXFile]
    serializer_class = XFileSerializer
    
    def get_queryset(self):
        return get_xfiles_can_view(self.request.user)

class XFileAttackLogListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới quá trình theo dõi/tấn công của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = AttackLogSerializer

    def get_queryset(self):
        self.xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        return self.xfile.attack_logs.all()

    # Ghi đè funtion perform_create để khởi tạo giá trị cho attacklog
    def perform_create(self, serializer):
        serializer.save(xfile=self.xfile)

class XFileAttackRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Liệt kê và tạo mới quá trình theo dõi/tấn công của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = AttackLogSerializer
    lookup_url_kwarg = 'attacklog_pk'

    def get_queryset(self):
        self.xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        return self.xfile.attack_logs.all()

class XFileContentList(generics.ListAPIView):
    '''Liệt kê content của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = ContentSerializer

    def get_queryset(self):
        xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        return xfile.contents.all()

class XFileDetailListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới detail của 1 trường dữ liệu của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = DetailSerializer

    def get_queryset(self):
        xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        self.content = get_object_or_404(xfile.contents.all(), id=self.kwargs['content_pk'])
        return self.content.details.all()

    # Ghi đè funtion perform_create để khởi tạo giá trị cho detail
    def perform_create(self, serializer):
        serializer.save(content=self.content)

class XFileDetailRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    '''Xem Sửa Xóa detail của 1 trường dữ liệu của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = DetailSerializer
    lookup_url_kwarg = 'detail_pk'

    def get_queryset(self):
        self.xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        content = get_object_or_404(self.xfile.contents.all(), id=self.kwargs['content_pk'])
        return content.details.all()

    def update(self, request, *args, **kwargs):
        self.get_object().editor = request.user
        return super().update(request, *args, **kwargs)
    
class XFileLogListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới bản log của hồ sơ mục tiêu'''
    permission_classes = [IsAuthenticated, CanViewXFile, CanEditXFile, IsDepartmentAuthenticated]
    serializer_class = XFileLogSerializer

    def get_queryset(self):
        self.xfile = get_object_or_404(XFile, id=self.kwargs['pk'])
        return self.xfile.xfile_logs.all()

    # Ghi đè funtion perform_create để khởi tạo giá trị cho XFileLog
    def perform_create(self, serializer):
        serializer.save(xfile=self.xfile, performer=self.request.user)

class XFilePermView(APIView):
    '''Liệt kê những hành động người dùng có thể làm với hồ sơ'''
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request, pk, format=None):
        user = request.user
        xfile = get_object_or_404(XFile, id=pk)
        data = {
            'view': user in get_users_can_view(xfile),
            'rejectDone': can_reject_done(user, xfile),
            'edit': can_edit_xfile(user, xfile),
            'submit': can_submit_xfile(user, xfile),
            'reject': can_reject_xfile(user, xfile),
            'approve': can_approve_xfile(user, xfile),
        }
        return Response(data, status.HTTP_200_OK)

class XFileSubmitView(APIView):
    permission_classes = [IsAuthenticated, CanSubmitXFile]
    http_method_names = ['put']
    
    def get_object(self, pk):
        return get_object_or_404(XFile, id=pk)

    def put(self, request, pk):
        xfile = self.get_object(pk)
        user = request.user
        self.check_object_permissions(request, xfile)
        xfile.submit_change(by=user)
        xfile.save()
        # notify(actor=user, target=xfile, verb=VERB.SEND.label, notify_to=list(xfile.checkers.all()))
        return Response({'detail': 'Gửi kiểm định thành công'}, status.HTTP_200_OK)

class XFileApproveView(APIView):
    permission_classes = [IsAuthenticated, CanApproveXFile]
    http_method_names = ['put']
    
    def get_object(self, pk):
        return get_object_or_404(XFile, id=pk)

    def put(self, request, pk):
        xfile = self.get_object(pk)
        user = request.user
        self.check_object_permissions(request, xfile)
        xfile.approve_change(by=user)
        xfile.save()
        # notify(actor=user, target=xfile, verb=VERB.SEND.label, notify_to=list(xfile.checkers.all()))
        return Response({'detail': 'Phê duyệt thành công'}, status.HTTP_200_OK)

class XFileRejectView(APIView):
    permission_classes = [IsAuthenticated, CanRejectXFile]
    http_method_names = ['put']
    
    def get_object(self, pk):
        return get_object_or_404(XFile, id=pk)

    def put(self, request, pk):
        xfile = self.get_object(pk)
        user = request.user
        self.check_object_permissions(request, xfile)
        xfile.reject_change(by=user)
        xfile.save()
        # notify(actor=user, target=xfile, verb=VERB.SEND.label, notify_to=list(xfile.checkers.all()))
        return Response({'detail': 'Đã yêu cầu sửa lại'}, status.HTTP_200_OK)
   
class XFileCreateChangeView(APIView):
    permission_classes = [IsAuthenticated, CanRejectDoneXFile]
    http_method_names = ['put']
    
    def get_object(self, pk):
        return get_object_or_404(XFile, id=pk)

    def put(self, request, pk):
        xfile = self.get_object(pk)
        user = request.user
        self.check_object_permissions(request, xfile)
        xfile.create_change(by=user)
        xfile.save()
        # notify(actor=user, target=xfile, verb=VERB.SEND.label, notify_to=list(xfile.checkers.all()))
        return Response({'detail': 'Yêu cầu sửa thêm thành công'}, status.HTTP_200_OK)
   
