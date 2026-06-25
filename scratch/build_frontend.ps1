$ErrorActionPreference = "Stop"

$workspace = "C:\Users\OM\OneDrive\Desktop\MediKal"
$flutterDir = "$workspace\flutter_sdk"
$zipPath = "$workspace\flutter.zip"
$flutterBin = "$flutterDir\flutter\bin"

# 1. Download Flutter SDK
if (-not (Test-Path "$flutterBin\flutter.bat")) {
    Write-Host "Downloading Flutter SDK... This is a one-time download."
    $url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.22.2-stable.zip"
    Invoke-WebRequest -Uri $url -OutFile $zipPath
    
    Write-Host "Extracting Flutter SDK (this may take a couple of minutes)..."
    if (-not (Test-Path $flutterDir)) {
        New-Item -ItemType Directory -Path $flutterDir
    }
    # Using tar is much faster than Expand-Archive on Windows
    tar -xf $zipPath -C $flutterDir
    
    Write-Host "Cleaning up zip file..."
    Remove-Item $zipPath
} else {
    Write-Host "Flutter SDK is already downloaded."
}

# 2. Add to PATH for this script session
$env:Path = "$flutterBin;$env:Path"

# 3. Configure Flutter
Write-Host "Configuring Flutter..."
& flutter config --enable-web --no-analytics

# 4. Generate Web Files
Write-Host "Creating Web platform files..."
cd "$workspace\frontend"
& flutter create --platforms=web .

# 5. Build Web Release
Write-Host "Building Web Release (compiling Dart files to optimized JavaScript)..."
& flutter build web --release

Write-Host "Frontend build completed successfully!"
