from django.db import models
 
'''
class User(models.Model):
    #用户表
 
    gender = (
        ('male','男'),
        ('female','女'),
    )
 
    name = models.CharField(max_length=128, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=256, verbose_name="密码")
    mobile = models.CharField(max_length=11, verbose_name="手机号", default="")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    sex = models.CharField(max_length=32, choices=gender, default='男')
    #image = models.ImageField(verbose_name="用户头像", upload_to="users/%Y/%m", default="")
    c_time = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField("Role")
 
    def __str__(self):
        return self.name
 
    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'
'''

