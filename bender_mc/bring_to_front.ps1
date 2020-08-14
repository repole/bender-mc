function Show-Process($Process, [Switch]$Maximize)
{
    $sig = '
        [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
        [DllImport("user32.dll")] public static extern int SetForegroundWindow(IntPtr hwnd);
    '

    if ($Maximize) { $Mode = 3 } else { $Mode = 4 }
    $type = Add-Type -MemberDefinition $sig -Name WindowAPI -PassThru
    $hwnd = $process.MainWindowHandle
    $null = $type::ShowWindowAsync($hwnd, $Mode)
    $null = $type::SetForegroundWindow($hwnd)
}
try {
    $kodi = Get-Process -Name kodi -ErrorAction Stop
}
catch [Microsoft.PowerShell.Commands.ProcessCommandException]{
    $kodi = Start-Process 'C:\Program Files\Kodi\kodi.exe' -PassThru
}
Show-Process($kodi)
