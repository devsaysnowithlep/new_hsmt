from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator


# Create your models here.

class Position(models.Model):
    '''
    Biểu diễn chức vụ trong tổ chức
    '''
    name = models.TextField()
    alias = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'

    # Thông tin chi tiết về User
    first_name = models.CharField(max_length=150)
    # image = models.ImageField(default="default.jpg", upload_to=get_user_dir_path)
    address = models.TextField(blank=True)
    skill = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)
    self_introduction = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    layout_config = models.TextField(blank=True)

    # department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.username