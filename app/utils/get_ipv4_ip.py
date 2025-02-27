import subprocess

def get_windows_ip():
    result = subprocess.run(
        ["powershell.exe", "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object InterfaceAlias -NotLike '*Loopback*' | Select-Object -ExpandProperty IPAddress)"],
        capture_output=True, text=True
    )
    ip_list = result.stdout.strip().splitlines()  # Chia kết quả thành từng dòng
    return ip_list[0] if ip_list else None  # Lấy dòng đầu tiên nếu có kết quả

#print(get_windows_ip())