from django_fsm import has_transition_perm
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.utils import timezone

import hmac, hashlib, base64, json

from new_hsmt import settings
from users.models import User
from xfiles.models import XFile

def get_users_can_view(xfile):
    users = list(xfile.editors.all())
    users.append(User.objects.get(department=xfile.department, position__slug='truongphong'))
    users.append(User.objects.get(position__slug='giamdoc'))
    return users

def get_xfiles_can_view(user):
    if user.position.slug == 'giamdoc':
        return XFile.objects.all()
    elif user.position.slug == 'truongphong':
        return XFile.objects.filter(department=user.department)
    else:
        return user.xfiles_can_edit.all()

def can_edit_xfile(user, xfile):
    return has_transition_perm(xfile.submit_change, user) and user in xfile.editors.all()

def can_submit_xfile(user, xfile):
    return has_transition_perm(xfile.submit_change, user) and user in xfile.editors.all()

def can_approve_xfile(user, xfile):
    return has_transition_perm(xfile.approve_change, user) and user.department == xfile.department and user.position.slug == 'truongphong'
    
def can_reject_xfile(user, xfile):
    return has_transition_perm(xfile.reject_change, user) and user.department == xfile.department and user.position.slug == 'truongphong'

def can_reject_done(user, xfile):
    return has_transition_perm(xfile.create_change, user) and user in xfile.editors.all()

class BaseXFilePermission(BasePermission):
    def has_permission(self, request, view):
        xfile_id = request.resolver_match.kwargs.get('pk')
        self.xfile = get_object_or_404(XFile, pk=xfile_id)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

class CanViewXFile(BaseXFilePermission):
    message = 'Người dùng không đủ quyền để xem hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user in get_users_can_view(self.xfile)

class CanEditXFile(BaseXFilePermission):
    message = 'Người dùng hiện không thể chỉnh sửa hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.method in SAFE_METHODS or can_edit_xfile(request.user, self.xfile)

class CanSubmitXFile(BaseXFilePermission):
    message = 'Người dùng hiện không thể gửi hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.method in SAFE_METHODS or can_submit_xfile(request.user, self.xfile)

class CanApproveXFile(BaseXFilePermission):
    message = 'Người dùng hiện không thể phê duyệt hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.method in SAFE_METHODS or can_approve_xfile(request.user, self.xfile)

class CanRejectXFile(BaseXFilePermission):
    message = 'Người dùng hiện không thể yêu cầu sửa lại hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.method in SAFE_METHODS or can_reject_xfile(request.user, self.xfile)

class CanRejectDoneXFile(BaseXFilePermission):
    message = 'Người dùng hiện không thể hủy bỏ trạng thái hoàn thành của hồ sơ'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.method in SAFE_METHODS or can_reject_done(request.user, self.xfile)

class TargetIsNotInUse(BasePermission):
    message = 'Không thể sửa, xóa hướng/nhóm/địa bàn đang được sử dụng'

    def has_object_permission(self, request, view, obj):
        return obj.xfiles.count() == 0

class IsDepartmentAuthenticated(BaseXFilePermission):
    message = 'Người dùng chưa đăng nhập vào phòng/ban'

    def has_permission(self, request, view):
        super().has_permission(request, view)
        token = request.META.get('HTTP_DAUTHORIZATION')
        if not token:
            return False
        # giải mã token
        token_data = base64.urlsafe_b64decode(token)
        token_data = json.loads(token_data)
        expiration_time = token_data['exp']
        # Nếu hết tgian hiệu lực => false
        if expiration_time < timezone.now().timestamp():
            return False

        department_id = token_data['department_id']
        # Nếu không đúng phòng của xfile thì không được sửa
        if department_id != self.xfile.department.id:
            return False

        # Kiểm tra chữ kí
        signature_msg = f'{str(expiration_time)}{str(department_id)}{str(self.xfile.department.password)}'
        signature = hmac.new(
            bytes(settings.SECRET_KEY, 'latin-1'),
            msg=bytes(signature_msg, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        if signature != token_data['signature']:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)