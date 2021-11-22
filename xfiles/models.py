from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import transition, GET_STATE, FSMIntegerField

from users.models import Department, User

# Choices
class STATUS(models.IntegerChoices):
    '''
    Những trạng thái của XFile
    '''
    INIT = 0, _('khởi tạo')
    EDITING = 1, _('đang sửa đổi')
    APPROVING = 2, _('đang phê duyệt')
    DONE = 3, _('đã hoàn thiện')
    
class TARGET_TYPES(models.IntegerChoices):
    '''
    Những loại của Target
    '''
    DIRECTION = 1, _('hướng')
    GROUP = 2, _('nhóm mục tiêu')
    AREA = 3, _('địa bàn')

class XFILE_ACTION(models.IntegerChoices):
    '''
    Những hành động có thể làm với XFile
    '''
    CREATE = 0, _('tạo mới')
    EDIT = 1, _('sửa đổi')
    SUBMIT = 2, _('gửi phê duyệt')
    APPROVE = 3, _('phê duyệt')
    REJECT = 4, _('yêu cầu sửa lại')
    REJECT_DONE =   5, _('hủy bỏ trạng thái hoàn thiện để tiếp tục sửa đổi')

class ROW_ACTION(models.IntegerChoices):
    '''
    Những hành động có thể làm với 1 trường dữ liệu
    '''
    ADD = 0, _('thêm trường dữ liệu')
    REMOVE = 1, _('xóa trường dữ liệu')
    EDIT = 2, _('sửa trường dữ liệu')

# Create your models here.
class XFileType(models.Model):
    '''
    Biểu diễn loại hồ sơ
    '''
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Target(models.Model):
    '''
    Biểu diễn hướng-nhóm-địa bàn
    '''
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    type = models.PositiveIntegerField(choices=TARGET_TYPES.choices)

    def __str__(self):
        return f'{self.get_type_display()} {self.name}'
        
class Detail(models.Model):
    '''
    Biểu diễn nội dung của trường dữ liệu
    '''
    timestamp = models.DateTimeField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    content = models.ForeignKey('Content', on_delete=models.CASCADE, related_name='details', null=True)

class ExContent(models.Model):
    '''
    Biểu diễn bản mẫu 1 trường dữ liệu của hồ sơ
    '''
    name = models.TextField()
    xfile_type = models.ForeignKey('XFileType', on_delete=models.CASCADE, related_name='ex_contents')

    def __str__(self):
        return self.name

class Content(models.Model):
    '''
    Biểu diễn 1 trường dữ liệu của hồ sơ
    '''
    name = models.TextField()
    xfile = models.ForeignKey('XFile', on_delete=models.CASCADE, related_name='contents')

    def __str__(self):
        return self.name    

class AttackLog(models.Model):
    '''
    Biểu diễn bảng IV: theo dõi quá trình theo dõi/tấn công
    '''
    timestamp = models.DateTimeField()
    process = models.TextField(blank=True)
    result = models.TextField(blank=True)
    attacker = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    xfile = models.ForeignKey('XFile', on_delete=models.CASCADE, related_name='attack_logs')

    def __str__(self):
        return f'quá trình {self.process}'

class XFileLog(models.Model):
    '''
    Biểu diễn những thay đổi của XFile
    '''
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.PositiveIntegerField(choices=XFILE_ACTION.choices, default=XFILE_ACTION.EDIT)
    performer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfile_logs')
    xfile = models.ForeignKey('XFile', on_delete=models.CASCADE, related_name='xfile_logs')

    contents = models.TextField(null=True, blank=True)
    attack_logs = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'những thay đổi của hồ sơ {self.xfile.code}'

class XFile(models.Model):
    '''
    Biểu diễn hồ sơ mục tiêu
    '''
    code = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    type = models.ForeignKey(XFileType, on_delete=models.PROTECT, related_name='xfiles')
    targets = models.ManyToManyField(Target, related_name='xfiles')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='xfiles')

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfiles_created')
    editors = models.ManyToManyField(User, related_name='xfiles_can_edit')
    date_created = models.DateTimeField(auto_now_add=True)

    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfiles_submitted', null=True)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfiles_approved', null=True)
    date_submitted = models.DateTimeField(null=True)
    date_approved = models.DateTimeField(null=True)

    status = FSMIntegerField(
        choices = STATUS.choices,
        default = STATUS.INIT,
        protected = True
    )

    def __str__(self):
        return self.code

    # Finite-state machine
    @transition(
        field=status,
        source= STATUS.INIT,
        target= STATUS.EDITING
    )
    def init_content(self, by=None):
        '''
        - Change status to EDITING
        - Khởi tạo các trường dữ liệu cho xfile dựa vào loại hồ sơ
        '''
        ex_contents = self.type.ex_contents.all()
        for ex_content in ex_contents:
            Content.objects.create(name = ex_content.name, xfile=self)
        XFileLog.objects.create(action=XFILE_ACTION.CREATE, performer=by, xfile=self)

    @transition(
        field=status,
        source= STATUS.EDITING,
        target= STATUS.APPROVING
    )
    def submit_change(self, by=None):
        '''
        - Change status to APPROVING
        - Save XFile.submitted_by, XFile.date_submitted
        '''
        self.submitted_by = by
        self.date_submitted = timezone.now()
        XFileLog.objects.create(action=XFILE_ACTION.SUBMIT, performer=by, xfile=self)

    @transition(
        field=status,
        source= STATUS.APPROVING,
        target= STATUS.DONE
    )
    def approve_change(self, by=None):
        '''
        - Change status to DONE
        - Save XFile.approved_by, XFile.date_approved
        '''
        self.approved_by = by
        self.date_approved = timezone.now()
        XFileLog.objects.create(action=XFILE_ACTION.APPROVE, performer=by, xfile=self)
        self.save()

    @transition(
        field=status,
        source= STATUS.DONE,
        target= STATUS.EDITING,
    )
    def create_change(self, by=None):
        '''
        - Change status to EDITING
        '''
        XFileLog.objects.create(action=XFILE_ACTION.REJECT_DONE, performer=by, xfile=self)

    @transition(
        field=status,
        source= STATUS.APPROVING,
        target= STATUS.EDITING
    )
    def reject_change(self, by=None):
        '''
        - Change status to EDITING
        '''
        XFileLog.objects.create(action=XFILE_ACTION.REJECT, performer=by, xfile=self)