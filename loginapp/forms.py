from django import forms
from captcha.fields import CaptchaField


class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=128, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # captcha = CaptchaField(label='验证码')


class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    #widget=widgets.Textarea(attrs={"class":"c1","placeholder":"请输入一段话"}),error_messages={"required":"手机号不能为空"})
    username = forms.CharField(label="用户名", max_length=128,
                               widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入用户名"}), required=True)
    password1 = forms.CharField(label="密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "请输入密码"}), required=True)
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "请再次输入密码"}), required=True)
    mobile = forms.CharField(label="手机号", max_length=11,
                             widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入手机号"}), required=True)

    email = forms.EmailField(label="邮箱地址",
                             widget=forms.EmailInput(attrs={'class': 'form-control', "placeholder":"请输入邮箱"}), required=True)
    sex = forms.ChoiceField(label='性别', choices=gender)
    #image = forms.ImageField(label="用户头像")
    # captcha = CaptchaField(label='验证码')

