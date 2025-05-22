# Create necessary directories
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\app"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\app\routes"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\app\services"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\app\utils"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\logs"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\static"
New-Item -ItemType Directory -Force -Path "youtube_transcript_app_deployment\templates"

# Copy main application files
Copy-Item -Path ".\app\*.py" -Destination ".\youtube_transcript_app_deployment\app\" -Recurse -Force
Copy-Item -Path ".\app\routes\*.py" -Destination ".\youtube_transcript_app_deployment\app\routes\" -Force
Copy-Item -Path ".\app\services\*.py" -Destination ".\youtube_transcript_app_deployment\app\services\" -Force
Copy-Item -Path ".\app\utils\*.py" -Destination ".\youtube_transcript_app_deployment\app\utils\" -Force

# Copy configuration files
Copy-Item -Path ".\.env.example" -Destination ".\youtube_transcript_app_deployment\.env" -Force
Copy-Item -Path ".\requirements.txt" -Destination ".\youtube_transcript_app_deployment\" -Force
Copy-Item -Path ".\README.md" -Destination ".\youtube_transcript_app_deployment\" -Force
Copy-Item -Path ".\run.py" -Destination ".\youtube_transcript_app_deployment\" -Force

# Create a requirements file with exact versions
pip freeze > ".\youtube_transcript_app_deployment\requirements_frozen.txt"

Write-Host "Deployment package created at: .\youtube_transcript_app_deployment"
