from rest_framework import  generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password

import hmac, hashlib, base64, json

from new_hsmt import settings
from xfiles.utils import change_pwd_for_xfile_department
from users.serializers import *
from users.permissions import *

# REST API
class DepartmentListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới phòng ban'''
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Department.objects.all()

class DepartmentLogin(APIView):
    '''Đăng nhập vào phòng'''
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, format=None):
        '''fields=('department_id', 'password')'''
        department_id = request.data.get('department')
        password = request.data.get('password')
        department = get_object_or_404(Department, id=department_id)
        if check_password(password, department.password):
            expiration_time = (timezone.now() + timezone.timedelta(minutes=60)).timestamp()
            signature_msg = f'{str(expiration_time)}{str(department_id)}{str(department.password)}'
            signature = hmac.new(
                bytes(settings.SECRET_KEY, 'latin-1'),
                msg=bytes(signature_msg, 'latin-1'),
                digestmod=hashlib.sha256
            ).hexdigest().upper()
            token_data = {
                'exp': expiration_time,
                'department_id': department_id,
                'signature': signature
            }
            token = base64.urlsafe_b64encode(bytes(json.dumps(token_data), 'latin-1'))
            return Response({'access': token}, status=status.HTTP_200_OK)
        return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_400_BAD_REQUEST)

class DepartmentChangePwd(APIView):
    '''Thay đổi mật khẩu của phòng'''
    ermission_classes = [IsAuthenticated, IsTruongphong]
    http_method_names = ['post']

    def post(self, request, format=None):
        '''fields=('department', 'old_password', 'new_password')'''
        department_id = request.data.get('department')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        department = get_object_or_404(Department, id=department_id)

        # chỉ trưởng phòng của phòng tương ứng được đổi
        if request.user.department != department:
            return Response({'detail': 'Không thể đổi mật khẩu của phòng khác'}, status=status.HTTP_403_FORBIDDEN)
        if check_password(old_password, department.password):
            department.password = make_password(new_password)
            department.save()
            change_pwd_for_xfile_department(department_id, old_password, new_password)
            return Response({'detail': 'Đổi mật khẩu thành công'}, status= status.HTTP_200_OK)
        return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_400_BAD_REQUEST)

class PositionListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới chức vụ'''
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Position.objects.all()

class UserListCreate(generics.ListCreateAPIView):
    '''Liệt kê và tạo mới người dùng'''
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()

    def post(self, request, *args, **kwargs):
        if request.user.position.id < int(request.data.get('position')):
            return Response({'detail': 'Không thể tạo tài khoản có chức vụ cao hơn mình'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.department.id != int(request.data.get('department')):
            return Response({'detail': 'Không thể tạo tài khoản khác phòng/ban với mình'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

class UserRetrieve(generics.RetrieveAPIView):
    '''Thông tin chi tiết về 1 user'''
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

class UserMeView(APIView):
    '''Hiển thị thông tin chi tiết về người dùng hiện tại'''
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request, format=None):
        data = UserDetailSerializer(request.user).data
        return Response(data, status.HTTP_200_OK)

class UserChangePwd(APIView):
    '''Thay đổi mật khẩu người dùng hiện tại'''
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, format=None):
        oldPwd = request.data.get('oldPwd', '')
        newPwd = request.data.get('newPwd', '')
        if not (newPwd and oldPwd):
            return Response({'detail': 'Thiếu dữ liệu'}, status.HTTP_400_BAD_REQUEST)
        if not check_password(oldPwd,request.user.password):  
            return Response({'detail': 'Mật khẩu cũ không chính xác'}, status.HTTP_400_BAD_REQUEST)
        if len(newPwd) <8:
            return Response({'detail': 'Mật khẩu mới phải lớn hơn 8 ký tự'}, status.HTTP_400_BAD_REQUEST)
        request.user.set_password(newPwd)
        request.user.save()
        return Response({'detail' : 'Đổi mật khẩu thành công'}, status.HTTP_200_OK)

class UserUpdate(generics.UpdateAPIView):
    '''Update thông tin chi tiết của người dùng'''
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserManager(generics.UpdateAPIView):
    '''Quản lí trạng thái, phòng ban, chức vụ của người dùng'''
    serializer_class = UserManagerSerializer
    permission_classes = [IsAuthenticated, (IsTruongphong & InSameDepartment) | IsGiamdoc]

    def get_queryset(self):
        return User.objects.all()

    def put(self, request, *args, **kwargs):
        if request.user.position.id < int(request.data.get('position')):
            return Response({'detail': 'Không thể tạo tài khoản có chức vụ cao hơn mình'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if request.user.position.id < int(request.data.get('position')):
            return Response({'detail': 'Không thể tạo tài khoản có chức vụ cao hơn mình'}, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)