$dest = "C:\Users\OM\OneDrive\Desktop\MediKal\temp_sdk"
New-Item -ItemType Directory -Force -Path $dest

Write-Host "1. Downloading Adoptium Temurin JDK 17 from GitHub..."
$jdkUrl = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.8.1%2B1/OpenJDK17U-jdk_x64_windows_hotspot_17.0.8.1_1.zip"
$jdkZip = "$dest\jdk.zip"
& curl.exe -L -o $jdkZip $jdkUrl

Write-Host "2. Extracting JDK 17..."
$jdkExtract = "$dest\jdk"
New-Item -ItemType Directory -Force -Path $jdkExtract
Expand-Archive -Path $jdkZip -DestinationPath $jdkExtract
Remove-Item $jdkZip

Write-Host "3. Discovering JDK home..."
$jdkHome = (Get-ChildItem -Path $jdkExtract -Directory)[0].FullName
Write-Host "JDK Home is: $jdkHome"

Write-Host "4. Downloading Android cmdline-tools with curl..."
$sdkUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$sdkZip = "$dest\sdk.zip"
& curl.exe -L -o $sdkZip $sdkUrl

Write-Host "5. Extracting cmdline-tools..."
$sdkPath = "$dest\android-sdk"
$cmdlineTemp = "$dest\cmdline-temp"
New-Item -ItemType Directory -Force -Path $cmdlineTemp
Expand-Archive -Path $sdkZip -DestinationPath $cmdlineTemp
Remove-Item $sdkZip

# Move files to latest folder
$latestPath = "$sdkPath\cmdline-tools\latest"
New-Item -ItemType Directory -Force -Path $latestPath
Copy-Item -Path "$cmdlineTemp\cmdline-tools\*" -Destination $latestPath -Recurse -Force
Remove-Item -Path $cmdlineTemp -Recurse -Force

# Set environment variables for the process
$env:JAVA_HOME = $jdkHome
$env:ANDROID_HOME = $sdkPath
$env:PATH = "$jdkHome\bin;$sdkPath\cmdline-tools\latest\bin;$env:PATH"

Write-Host "6. Accepting licenses..."
$sdkManager = "$sdkPath\cmdline-tools\latest\bin\sdkmanager.bat"
$yes = , "y" * 100
$yes | & $sdkManager --licenses

Write-Host "7. Installing platforms and build tools..."
& $sdkManager "platform-tools" "build-tools;34.0.0" "platforms;android-34"

Write-Host "8. Configuration done!"
