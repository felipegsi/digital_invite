# Script de limpeza de cache e recompilação do projeto Django
Write-Host "Iniciando limpeza de cache e recompilação do projeto..." -ForegroundColor Green

# 1. Remover arquivos Python compilados
Write-Host "1. Removendo arquivos Python compilados (.pyc)..." -ForegroundColor Cyan
Get-ChildItem -Path . -Include *.pyc,__pycache__ -Recurse | Remove-Item -Recurse -Force

# 2. Limpar cache do Django
Write-Host "2. Limpando cache do Django..." -ForegroundColor Cyan
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# 3. Limpar arquivos estáticos compilados
Write-Host "3. Limpando arquivos Tailwind compilados..." -ForegroundColor Cyan
if (Test-Path ".\static\css\tailwind.css") {
    Remove-Item ".\static\css\tailwind.css" -Force
}

# 4. Recompilar Tailwind CSS
Write-Host "4. Recompilando Tailwind CSS..." -ForegroundColor Cyan
npm run build:css

# 5. Reiniciar o servidor Django
Write-Host "5. Script de limpeza concluído!" -ForegroundColor Green
Write-Host "`nAgora você pode reiniciar seu servidor Django com:" -ForegroundColor Yellow
Write-Host "python manage.py runserver" -ForegroundColor Yellow

Write-Host "`nLimpeza de cache concluída com sucesso!" -ForegroundColor Green
