from django import forms
from django.contrib.auth.models import User
from .models import Associado


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=150, required=True)
    last_name = forms.CharField(label='Sobrenome', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    biografia = forms.CharField(label='Biografia', widget=forms.Textarea, required=False)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Seha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('As senhas não conferem.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            Associado.objects.create(
                usuario=user,
                biografia=self.cleaned_data.get('biografia', '')
            )
        return user
