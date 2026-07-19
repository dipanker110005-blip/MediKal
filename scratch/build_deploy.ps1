Write-Host "Starting build process..."
Set-Location "c:\Users\OM\OneDrive\Desktop\MediKal\frontend"

# 1. Run Flutter build web
& "..\flutter_sdk\flutter\bin\flutter.bat" build web --release
if ($LASTEXITCODE -ne 0) {
    Write-Error "Flutter build failed!"
    exit 1
}

Write-Host "Flutter build completed successfully. Copying Vercel config files..."

# 2. Re-create and copy .vercel folder
New-Item -ItemType Directory -Force -Path "build\web\.vercel"
Copy-Item -Force ".vercel\project.json" "build\web\.vercel\project.json"

# 3. Create vercel.json in build/web
$vercelJson = @'
{
  "outputDirectory": ".",
  "cleanUrls": true,
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://medikal-backend-production-d7ad.up.railway.app/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
'@
Set-Content -Path "build\web\vercel.json" -Value $vercelJson

Write-Host "Deploying to Vercel..."
# 4. Deploy to Vercel
Set-Location "build\web"
npx --yes vercel deploy --prod
if ($LASTEXITCODE -ne 0) {
    Write-Error "Vercel deployment failed!"
    exit 1
}

Write-Host "Deployment completed successfully!"
