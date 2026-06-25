$ErrorActionPreference = "Stop"

$workspace = "C:\Users\OM\OneDrive\Desktop\MediKal"
$flutterBin = "$workspace\flutter_sdk\flutter\bin"

# Add to PATH for this script session
$env:Path = "$flutterBin;$env:Path"

# 1. Configure Flutter
Write-Host "Configuring Flutter for web..."
& flutter config --enable-web --no-analytics

# 2. Generate Web Files
Write-Host "Creating Web platform files..."
cd "$workspace\frontend"
& flutter create --platforms=web .

# 3. Build Web Release
Write-Host "Building Web Release (compiling Dart files to optimized JavaScript)..."
& flutter build web --release

Write-Host "Frontend build completed successfully!"
