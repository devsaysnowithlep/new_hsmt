from django.db import models

from users.models import User

# Create your models here.
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

class XFileType(models.Model):
    '''
    Biểu diễn loại hồ sơ
    '''
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class XFile(models.Model):
    '''
    Biểu diễn hồ sơ mục tiêu
    '''
    code = models.CharField(max_length=150, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    type = models.ForeignKey(XFileType, on_delete=models.PROTECT, related_name='xfiles')
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfiles_created', null=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='xfiles_edited', null=True)

    def __str__(self):
        return self.code

    def init_content(self):
        ex_contents = self.type.ex_contents.all()
        for ex_content in ex_contents:
            Content.objects.create(name = ex_content.name, xfile=self)