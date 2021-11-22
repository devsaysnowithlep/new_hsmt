from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

def is_troly(user):
    return user.position.slug == 'troly'

def is_truongphong(user):
    return user.position.slug == 'truongphong'

def is_giamdoc(user):
    return user.position.slug == 'giamdoc'

class IsTroly(BasePermission):
    message = 'Người dùng phải là trợ lý'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return is_troly(request.user)

    def has_permission(self, request, view):
        return self.has_object_permission(request, view, None)

class IsTruongphong(BasePermission):
    message = 'Người dùng phải là trợ lý'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return is_truongphong(request.user)

    def has_permission(self, request, view):
        return self.has_object_permission(request, view, None)

class IsGiamdoc(BasePermission):
    message = 'Người dùng phải là trợ lý'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return is_giamdoc(request.user)

    def has_permission(self, request, view):
        return self.has_object_permission(request, view, None)

class IsAdmin(BasePermission):
    message = 'Người dùng phải là trợ lý'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_staff

    def has_permission(self, request, view):
        return self.has_object_permission(request, view, None)

class IsOwner(BasePermission):
    message = 'Chủ sở hữu mới có thể sửa đổi'
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.id == obj.id

class IsNotOwner(BasePermission):
    message = 'Chủ sở hữu không được tự sửa đổi'
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.id != obj.id

class InSameDepartment(BasePermission):
    message = 'Người dùng phải thuộc đúng phòng/ban'
    def has_object_permission(self, request, view, obj):
        return request.user.department.id == obj.department.id