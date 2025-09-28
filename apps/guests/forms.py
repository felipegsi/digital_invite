from django import forms
from apps.guests.models import Guest
from apps.core.services.appwrite_service import AppwriteService


class GuestForm(forms.ModelForm):
    avatar = forms.ImageField(required=True)

    # Removendo a definição do campo com widget múltiplo que causa o erro

    class Meta:
        model = Guest
        fields = [
            "first_name",
            "last_name",
            "nickname",
            "gender",
            "emoji",
        ]

    def save(self, commit=True):
        guest = super().save(commit=False)

        # Processamento do avatar
        pic = self.cleaned_data.get("avatar")
        if pic:
            guest.avatar_id = AppwriteService.upload_file(pic, resize_to=(500, 500))

        # Processamento das memórias (múltiplas imagens)
        # Busca diretamente da requisição
        memory_files = self.files.getlist('memories_upload')
        if memory_files:
            # Inicializa a lista de memórias se não existir
            if not guest.memories:
                guest.memories = []

            # Processa cada arquivo e adiciona o ID à lista de memórias
            for memory_file in memory_files:
                memory_id = AppwriteService.upload_file(memory_file, resize_to=(800, 800))
                guest.memories.append(memory_id)

        if commit:
            guest.save()
        return guest
