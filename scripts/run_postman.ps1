param(
  [string]$EnvFile = ".env"
)

Write-Output "Activating virtualenv and running migrations..."
.\futurex\Scripts\Activate.ps1
python manage.py migrate --noinput

Write-Output "Starting Django dev server in background"
Start-Process -NoNewWindow -FilePath python -ArgumentList 'manage.py','runserver','0.0.0.0:8000'
Start-Sleep -Seconds 3

Write-Output "Running Newman collection..."
Push-Location postman
npm install
npm run run-postman
Pop-Location
