from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    # Personalize os métodos do adaptador conforme necessário
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False  # Por exemplo, desative o usuário até a ativação
        user.save()
        return user
