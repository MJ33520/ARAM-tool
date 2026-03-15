$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\ARAM Assistant.lnk")
$Shortcut.TargetPath = "C:\Users\Administrator\.gemini\antigravity\scratch\aram-assistant\launch.bat"
$Shortcut.WorkingDirectory = "C:\Users\Administrator\.gemini\antigravity\scratch\aram-assistant"
$Shortcut.IconLocation = "C:\Users\Administrator\.gemini\antigravity\scratch\aram-assistant\launch.bat"
$Shortcut.Save()
Write-Host "Shortcut created at $DesktopPath\ARAM Assistant.lnk"
