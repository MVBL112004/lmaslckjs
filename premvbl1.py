import requests, re, os, json, base64, uuid, sys, time, traceback
from time import sleep
from datetime import datetime, timedelta
listCookie = []
proxy_list = []
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
trang = "\033[1;37m"
tim = "\033[1;35m"
xanh = "\033[1;36m"
thanh = f'{do}[{trang}</>{do}] {trang}=> '
class ProxyRotator:
    def __init__(self, proxies: list[str]):
        self.proxies = proxies[:] if proxies else []
        self.i = 0

    def has_proxy(self):
        return bool(self.proxies)

    def current(self) -> str | None:
        if not self.proxies:
            return None
        return self.proxies[self.i % len(self.proxies)]

    def rotate(self) -> str | None:
        if not self.proxies:
            return None
        self.i = (self.i + 1) % len(self.proxies)
        return self.current()

def to_requests_proxies(proxy_str: str | None) -> dict | None:
    if not proxy_str:
        return None
    p = proxy_str.strip().split(':')
    # Hỗ trợ cả 2 dạng: user:pass:host:port hoặc host:port:user:pass
    if len(p) == 4:
        try:
            host, port, user, past = p
            int(port)
        except ValueError:
            user, past, host, port = p
        return {
            'http':  f'http://{user}:{past}@{host}:{port}',
            'https': f'http://{user}:{past}@{host}:{port}',
        }
    # Dạng host:port
    if len(p) == 2:
        host, port = p
        return {
            'http':  f'http://{host}:{port}',
            'https': f'http://{host}:{port}',
        }
    return None

def check_proxy_fast(proxy_str: str) -> bool:
    # Đơn giản: gọi 1 URL nhẹ với timeout ngắn
    try:
        _sess = requests.Session()
        r = _sess.get(
            'http://www.google.com/generate_204',
            proxies=to_requests_proxies(proxy_str),
            timeout=6
        )
        return r.status_code in (204, 200)
    except Exception:
        return False
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(fr'''           {luc}© Bản Quyền MVBL ! Tool VIPPRO !!!
        
{do} _____ ______       ___      ___  ________      ___          
{trang}|\   _ \  _   \    |\  \    /  /||\   __  \    |\  \         
{do}\ \  \\\__\ \  \   \ \  \  /  / /\ \  \|\ /_   \ \  \        
{trang} \ \  \\|__| \  \   \ \  \/  / /  \ \   __  \   \ \  \       
{do}  \ \  \    \ \  \   \ \    / /    \ \  \|\  \   \ \  \____  
{trang}   \ \__\    \ \__\   \ \__/ /      \ \_______\   \ \_______\ 
{do}    \|__|     \|__|    \|__|/        \|_______|    \|_______|''')
    thanhngang(65)
    print(f'''{thanh} {luc}Admin{trang}: {vang}Mai Vũ Bảo Long
{thanh} {luc}Box Zalo{trang}: {do}https://zalo.me/g/qioudg138
{thanh} {luc}Web Bán Proxy ipv6 chạy tool{trang}: {do} long2k4.id.vn
{thanh} {luc}Web DVMXH{trang}: {do}
{thanh} {luc}Web Thu Xu{trang}: {do}https://thucoin.com/
{thanh} {luc}Bạn Đang Sử Dụng Tool{trang}: {vang}Trao Đổi Sub Facebook VIP''')
    thanhngang(65)

def thanhngang(so):
    for i in range(so):
        print(trang+'-',end ='')
    print('')

def Delay(value):
    while not(value <= 1):
        value -= 0.123
        print(f'''{trang}[{xanh}MVBL1104{trang}] [{xanh}DELAY{trang}] [{xanh}{str(value)[0:5]}{trang}] [{vang}X    {trang}]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''{trang}[{xanh}MVBL1104{trang}] [{xanh}DELAY{trang}] [{xanh}{str(value)[0:5]}{trang}] [ {vang}X   {trang}]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''{trang}[{xanh}MVBL1104{trang}] [{xanh}DELAY{trang}] [{xanh}{str(value)[0:5]}{trang}] [  {vang}X  {trang}]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''{trang}[{xanh}MVBL1104{trang}] [{xanh}DELAY{trang}] [{xanh}{str(value)[0:5]}{trang}] [   {vang}X {trang}]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''{trang}[{xanh}MVBL1104{trang}] [{xanh}DELAY{trang}] [{xanh}{str(value)[0:5]}{trang}] [    {vang}X{trang}]''', '               ', end = '\r')
        sleep(0.02)

def load_settings():
    if os.path.exists("setting.json"):
        with open("setting.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_settings(settings):
    with open("setting.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)

def decode_base64(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str

def encode_to_base64(_data):
    byte_representation = _data.encode('utf-8')
    base64_bytes = base64.b64encode(byte_representation)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

# ================== KEY VIP ==================
# Nguồn key trên GitHub (đọc trực tiếp, không tải file về)
KEY_SOURCE_URL = 'https://raw.githubusercontent.com/MVBL112004/lmaslckjs/main/key.txt'
KEY_VTH_URL = 'https://raw.githubusercontent.com/MVBL112004/lmaslckjs/main/keyvth.txt'

def _parse_expiry_to_datetime(exp_str: str) -> datetime | None:
    exp_str = exp_str.strip()
    # Ưu tiên: epoch giây
    if exp_str.isdigit():
        try:
            return datetime.fromtimestamp(int(exp_str))
        except Exception:
            pass
    # ISO-like
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]:
        try:
            return datetime.strptime(exp_str, fmt)
        except Exception:
            continue
    return None

def _fetch_key_map(timeout_sec: int = 15) -> dict[str, datetime]:
    try:
        resp = requests.get(KEY_SOURCE_URL, timeout=timeout_sec)
        text = resp.text
    except Exception:
        return {}
    key_map: dict[str, datetime] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '|' not in line:
            continue
        k, exp = line.split('|', 1)
        k = k.strip()
        exp_dt = _parse_expiry_to_datetime(exp)
        if k and exp_dt:
            key_map[k] = exp_dt
    return key_map

def verify_vip_key():
    while True:
        print(f"{luc}Vui lòng nhập key VIP để tiếp tục.")
        print(f"{luc}Bạn có thể nhận keyvip bằng cách mua proxy tại {do}long2k4.id.vn{luc} hoặc liên hệ Zalo {do}0816042268{luc} để mua.")
        user_key = input(f"{thanh}{luc}Nhập key VIP{trang}: {vang}").strip()
        if not user_key:
            continue
        key_map = _fetch_key_map()
        if not key_map:
            print(f"{do}Không thể truy cập nguồn key. Kiểm tra kết nối mạng rồi thử lại!")
            continue
        if user_key not in key_map:
            print(f"{do}Key không hợp lệ. Vui lòng nhập lại!")
            print(f"{luc}Bạn có thể nhận keyvip bằng cách mua proxy tại {do}long2k4.id.vn{luc} hoặc liên hệ Zalo {do}0816042268{luc} để mua.")
            continue
        expiry = key_map[user_key]
        # Chuyển sang giờ VN (UTC+7) để hiển thị
        now_sys = datetime.now()
        now_vn = now_sys + timedelta(hours=7)
        expiry_vn = expiry + timedelta(hours=7)
        if expiry <= now_sys:
            print(f"{do}Key đã hết hạn vào {vang}{expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7){do}. Dừng tool.")
            raise SystemExit(0)
        else:
            print(f"{luc}Key hợp lệ. Hạn dùng tới {vang}{expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7){trang}.")
            # Lưu expiry toàn cục để hiển thị đếm ngược trong vòng lặp chính
            globals()['VIP_KEY_EXPIRY_SYS'] = expiry
            break

def main_menu():
    banner()
    print(f"{thanh}{luc}Nhập {do}[{vang}1{do}] {luc}Chạy Job TDS FB VIP")
    print(f"{thanh}{luc}Nhập {do}[{vang}2{do}] {luc}Check Live Proxy")
    print(f"{thanh}{luc}Nhập {do}[{vang}3{do}] {luc}Chạy Game VTH VIP")
    thanhngang(65)
    choice = input(f"{thanh}{luc}Nhập lựa chọn{trang}: {vang}").strip()
    return choice

def _parse_proxy_line(raw: str) -> tuple[str, dict]:
    raw = raw.strip()
    if not raw or raw.startswith('#'):
        return '', {}
    parts = raw.split(':')
    if len(parts) == 2:
        host, port = parts
        auth = ''
    elif len(parts) == 4:
        host, port, user, pwd = parts
        auth = f"{user}:{pwd}@"
    else:
        return raw, {}
    proxy_uri = f"http://{auth}{host}:{port}"
    return raw, { 'http': proxy_uri, 'https': proxy_uri }

def _try_request_fast(url: str, proxies: dict, timeout: float):
    try:
        r = requests.get(url, proxies=proxies, timeout=timeout)
        return r.status_code == 200 and bool(r.text.strip()), r.text.strip()
    except Exception as e:
        return False, str(e)

def _check_one_fast(raw: str, timeout: float = 8.0) -> tuple[bool, str]:
    raw, proxies = _parse_proxy_line(raw)
    if raw == '' or not proxies:
        return False, ''
    urls = [
        'https://api64.ipify.org?format=text',
        'http://api64.ipify.org?format=text',
        'https://api.ipify.org?format=text',
        'http://api.ipify.org?format=text',
    ]
    for _ in range(2):
        for url in urls:
            ok, note = _try_request_fast(url, proxies, timeout)
            if ok:
                return True, note
        sleep(0.5)
    return False, ''

def run_check_proxy(proxies: list[str] | None = None):
    banner()
    print(f"{luc}Bắt đầu kiểm tra proxy...{trang}")
    if proxies is None:
        if not os.path.exists("proxy-vip.json"):
            print(f"{do}Không tìm thấy file proxy-vip.json, vui lòng nhập proxy mới!")
            proxies = add_proxy()
        else:
            with open("proxy-vip.json", "r") as f:
                proxies = json.load(f)

    live = []
    die = []
    for pr in proxies:
        ok, iptxt = _check_one_fast(pr, timeout=8.0)
        if ok:
            ip = iptxt if iptxt else 'Unknown'
            print(f"{luc}[LIVE]{trang} {pr} {vang}→ {ip}")
            live.append(pr)
        else:
            print(f"{do}[DIE]{trang} {pr}")
            die.append(pr)

    # Lưu proxy sống
    try:
        with open('proxylive.txt', 'w', encoding='utf-8') as f:
            for pr in live:
                f.write(pr + "\n")
        print(f"{luc}Đã lưu proxy live vào file {vang}proxylive.txt{trang}")
    except Exception:
        pass

    print(f"{luc}Tổng proxy sống: {vang}{len(live)}{trang}, chết: {do}{len(die)}")

def proxy_menu_choice2():
    banner()
    print(f"{thanh}{luc}Nhập {do}[{vang}1{do}] {luc}Check live proxy cũ")
    print(f"{thanh}{luc}Nhập {do}[{vang}2{do}] {luc}Nhập proxy mới")
    print(f"{thanh}{luc}Nếu không có proxy cũ, hệ thống sẽ chuyển sang nhập proxy mới.")
    thanhngang(65)
    chon = input(f"{thanh}{luc}Nhập lựa chọn{trang}: {vang}").strip()
    thanhngang(65)

    def _save_and_info(proxies):
        with open("proxy-vip.json", "w") as f:
            json.dump(proxies, f)
        print(f"{luc}Đã lưu {vang}{len(proxies)}{luc} proxy vào file proxy-vip.json{trang}")

    if chon == "1":
        # Check live proxy cũ
        if not os.path.exists("proxy-vip.json"):
            print(f"{do}Không có proxy cũ! Chuyển sang nhập proxy mới...")
            proxies = add_proxy_no_check()
            _save_and_info(proxies)
            run_check_proxy()
            return
        try:
            with open("proxy-vip.json", "r") as f:
                proxies = json.load(f)
        except Exception:
            proxies = []

        if not proxies:
            print(f"{do}Không có proxy cũ! Chuyển sang nhập proxy mới...")
            proxies = add_proxy_no_check()
            _save_and_info(proxies)
        # Dù là cũ hay vừa nhập, giờ chạy check
        run_check_proxy()
        return

    elif chon == "2":
        # Nhập proxy mới
        proxies = add_proxy_no_check()
        _save_and_info(proxies)
        # Sau khi nhập xong mới kiểm tra
        run_check_proxy(proxies)
        return

    else:
        print(f"{do}Lựa chọn không hợp lệ!")
        return

def _fetch_vth_key_map(timeout_sec: int = 15) -> dict[str, datetime]:
    """Tải danh sách key VTH từ GitHub"""
    try:
        resp = requests.get(KEY_VTH_URL, timeout=timeout_sec, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/plain,*/*'
        })
        resp.raise_for_status()
        text = resp.text
    except Exception:
        return {}
    
    key_map = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '|' not in line:
            continue
        k, exp = line.split('|', 1)
        k = k.strip()
        exp_dt = _parse_expiry_to_datetime(exp)
        if k and exp_dt:
            key_map[k] = exp_dt
    return key_map

def verify_vth_key():
    """Kiểm tra key VIP cho Game VTH"""
    while True:
        print(f"{luc}Vui lòng nhập key VIP để tiếp tục.")
        print(f"{luc}Bạn có thể nhận keyvip bằng cách mua proxy tại {do}long2k4.id.vn{luc} hoặc liên hệ Zalo {do}0816042268{luc} để mua.")
        try:
            user_key = input(f"{thanh}{luc}Nhập key VIP{trang}: {vang}").strip()
            if not user_key:
                continue
            key_map = _fetch_vth_key_map()
            if not key_map:
                print(f"{do}Không thể truy cập nguồn key. Kiểm tra kết nối mạng rồi thử lại!")
                continue
            if user_key not in key_map:
                print(f"{do}Key không hợp lệ. Vui lòng nhập lại!")
                print(f"{luc}Bạn có thể nhận keyvip bằng cách mua proxy tại {do}long2k4.id.vn{luc} hoặc liên hệ Zalo {do}0816042268{luc} để mua.")
                continue
            
            expiry = key_map[user_key]
            now_sys = datetime.now()
            now_vn = now_sys + timedelta(hours=7)
            expiry_vn = expiry + timedelta(hours=7)
            
            if expiry <= now_sys:
                print(f"{do}Key đã hết hạn vào {vang}{expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7){do}. Dừng tool.")
                raise SystemExit(0)
            else:
                print(f"{luc}Key hợp lệ. Hạn dùng tới {vang}{expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7){trang}.")
                globals()['VTH_KEY_EXPIRY'] = expiry
                break
        except KeyboardInterrupt:
            print(f"\n{do}Đã hủy. Thoát game.")
            raise SystemExit(0)

def run_vth_game():
    """Chạy Game VTH VIP - tải và thực thi từ GitHub raw link"""
    banner()
    print(f"{luc}Đang tải Game VTH VIP từ server...{trang}")
    
    # Kiểm tra key VTH trước
    verify_vth_key()
    
    # Ẩn URL thật, chỉ hiện tên file giả trong traceback
    GAME_FILE = "vthgame.py"
    URL_VTH = "https://raw.githubusercontent.com/MVBL112004/lmaslckjs/main/anoasnkj.py"
    
    # Thêm headers để tránh lỗi 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/plain,application/octet-stream,*/*',
        'Cache-Control': 'no-cache',
        'Referer': 'https://github.com/'
    }
    
    try:
        # Tải code từ GitHub
        print(f"{luc}Đang kết nối tới server...{trang}")
        response = requests.get(URL_VTH, timeout=20, headers=headers)
        response.raise_for_status()
        
        # Kiểm tra response có phải JSON không
        try:
            response.json()
            print(f"{do}Server trả về dữ liệu không hợp lệ!")
            input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
            return
        except:
            # Không phải JSON là đúng, vì chúng ta cần code Python
            pass
            
        code = response.content.decode("utf-8", errors="replace")
        if not code.strip():
            print(f"{do}Không thể tải code từ server hoặc nội dung rỗng!")
            input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
            return
        
        print(f"{luc}Tải thành công! Đang khởi động Game VTH VIP...{trang}")
        sleep(2)
        
        # Clear màn hình trước khi chạy game
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Thực thi code từ RAM với sys.excepthook tùy chỉnh để ẩn URL
        def custom_excepthook(type_, value, traceback_):
            if type_ == KeyboardInterrupt:
                print(f"\n{do}Đã dừng Game VTH VIP!")
            elif type_ == SystemExit:
                pass  # Không hiện gì khi thoát bình thường
            else:
                import traceback
                # Thay thế URL trong traceback bằng tên file giả
                formatted = '\n'.join(line.replace(URL_VTH, GAME_FILE) 
                                    for line in traceback.format_exception(type_, value, traceback_))
                print(f"\n{do}Lỗi khi chạy Game VTH VIP!")
                print(formatted)
            
        old_excepthook = sys.excepthook
        sys.excepthook = custom_excepthook
        
        try:
            # Tạo namespace với các biến cần thiết
            ns = {
                "__name__": "__main__",
                "__file__": GAME_FILE,
                "os": os,
                "sys": sys,
                "time": time,
                "sleep": sleep,
                "requests": requests,
                "json": json,
                "datetime": datetime,
                "thanh": thanh,
                "luc": luc,
                "vang": vang,
                "do": do,
                "trang": trang,
            }
            # Compile và thực thi code trong namespace riêng
            exec(compile(code, GAME_FILE, "exec"), ns, ns)
        finally:
            # Khôi phục excepthook gốc
            sys.excepthook = old_excepthook
        
        # Sau khi game kết thúc (thoát bình thường hoặc hết key)
        print(f"\n{luc}Game VTH VIP đã kết thúc.{trang}")
        input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
        
    except requests.RequestException as e:
        print(f"{do}Không thể kết nối tới server!")
        print(f"{do}Kiểm tra kết nối mạng và thử lại.")
        input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
    except ImportError as e:
        print(f"\n{do}Thiếu thư viện cần thiết cho Game VTH VIP!")
        print(f"{luc}Vui lòng cài đặt: {vang}pip install rich websocket-client pytz")
        input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
    except (SystemExit, KeyboardInterrupt):
        # Xử lý cả SystemExit và KeyboardInterrupt cùng một chỗ
        # Không hiện traceback để tránh lộ URL
        print(f"\n{luc}Game đã kết thúc.{trang}")
        input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")
    except Exception as e:
        # In traceback nhưng thay URL thật bằng tên file giả
        formatted = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        formatted = formatted.replace(URL_VTH, GAME_FILE)
        print(f"\n{do}Lỗi khi chạy Game VTH VIP!")
        print(formatted)
        input(f"{thanh}{luc}Nhấn Enter để quay lại menu chính...{trang}")

# Nên đặt gần chỗ main loop để truy cập sẵn các biến
def rotate_and_reinit(rotator: ProxyRotator):
    """
    Xoay sang proxy kế tiếp, kiểm tra sống, rồi re-init lại các session (fb + tds).
    Trả về (proxy_str, fb, tds) nếu thành công, hoặc (None, None, None) nếu hết proxy.
    """
    if not rotator.has_proxy():
        return (None, None, None)

    tried = 0
    while tried < len(rotator.proxies):
        new_proxy = rotator.rotate()
        if check_proxy_fast(new_proxy):
            # Re-init Facebook & TDS với proxy mới
            fb_new = Facebook(cookie, new_proxy)
            tds_new = TraoDoiSub(username, password, new_proxy)
            return (new_proxy, fb_new, tds_new)
        tried += 1

    # Không còn proxy sống
    return (None, None, None)

class Facebook:
    def __init__(self, cookie: str, proxy=None):
        try:
            self.lsd = ''
            self.fb_dtsg = ''
            self.jazoest = ''
            self.cookie = cookie
            self.proxies = None
            self.session = requests.Session()
            self.id = self.cookie.split('c_user=')[1].split(';')[0]
            self.headers = {'authority': 'www.facebook.com', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-language': 'vi', 'sec-ch-prefers-color-scheme': 'light', 'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'viewport-width': '1366', 'Cookie': self.cookie}
            if proxy:
                proxy = proxy.strip()
                parts = proxy.split(':')
                if len(parts) == 4:
                    try:
                        host, port, user, past = parts
                        int(port)
                    except ValueError:
                        user, past, host, port = parts
                    self.proxies = {
                        'http': f'http://{user}:{past}@{host}:{port}',
                        'https': f'http://{user}:{past}@{host}:{port}'
                    }
            url = self.session.get(f'https://www.facebook.com/{self.id}', headers=self.headers, proxies=self.proxies).url
            response = self.session.get(url, headers=self.headers, proxies=self.proxies).text
            matches = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
            if len(matches) > 0:
                self.fb_dtsg += matches[0]
                self.jazoest += re.findall(r'jazoest=(.*?)\"', response)[0]
                self.lsd += re.findall(r'\["LSD",\[\],\{"token":"(.*?)"\}', response)[0]
        except:
            pass
    def set_proxy(self, proxy_str: str | None):
        """Cập nhật proxies cho session hiện tại."""
        if proxy_str:
            self.proxies = to_requests_proxies(proxy_str)
        else:
            self.proxies = None        
    def info(self):
        get = self.session.get('https://www.facebook.com/me',headers=self.headers, proxies=self.proxies).text
        try:
            name = get.split('<title>')[1].split('</title>')[0]
            return {'success': 200, 'id': self.id, 'name': name}
        except:
            return {'error': 200}
        
    def likepage(self, id: str):
        try:
            data = {
                'av': self.id,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometProfilePlusLikeMutation',
                'variables': '{"input":{"is_tracking_encrypted":false,"page_id":"'+str(id)+'","source":null,"tracking":null,"actor_id":"'+str(self.id)+'","client_mutation_id":"1"},"scale":1}',
                'server_timestamps': 'true',
                'doc_id': '6716077648448761',
            }
            response = self.session.post('https://www.facebook.com/api/graphql/',data=data,headers=self.headers, proxies=self.proxies)
            if '"subscribe_status":"IS_SUBSCRIBED"' in response.text:
                return True
            else:
                return False
        except:
            pass

    def follow(self, id: str):
        try:
            data = {
                'av': self.id,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometUserFollowMutation',
                'variables': '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,unexpected,1719765181042,489343,250100865708545,,;SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,unexpected,1719765155735,648442,391724414624676,,;SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,tap_search_bar,1719765153341,865155,391724414624676,,","is_tracking_encrypted":false,"subscribe_location":"PROFILE","subscribee_id":"'+str(id)+'","tracking":null,"actor_id":"'+str(self.id)+'","client_mutation_id":"5"},"scale":1}',
                'server_timestamps': 'true',
                'doc_id': '25581663504782089',
            }
            response = self.session.post('https://www.facebook.com/api/graphql/',data=data,headers=self.headers, proxies=self.proxies)
            if '"subscribe_status":"IS_SUBSCRIBED"' in response.text:
                return True
            else:
                return False
        except:
            pass

    def reaction(self, id: str, type: str):
        try:
            reac = {
                "LIKE": "1635855486666999",
                "LOVE": "1678524932434102",
                "CARE": "613557422527858",
                "HAHA": "115940658764963",
                "WOW": "478547315650144",
                "SAD": "908563459236466",
                "ANGRY": "444813342392137"
            }
            idreac = reac.get(type)
            data = {
                'av': self.id,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                'variables': fr'{{"input":{{"attribution_id_v2":"CometHomeRoot.react,comet.home,tap_tabbar,1719027162723,322693,4748854339,,","feedback_id":"{encode_to_base64("feedback:"+str(id))}","feedback_reaction_id":"{idreac}","feedback_source":"NEWS_FEED","is_tracking_encrypted":true,"tracking":["AZWUDdylhKB7Q-Esd2HQq9i7j4CmKRfjJP03XBxVNfpztKO0WSnXmh5gtIcplhFxZdk33kQBTHSXLNH-zJaEXFlMxQOu_JG98LVXCvCqk1XLyQqGKuL_dCYK7qSwJmt89TDw1KPpL-BPxB9qLIil1D_4Thuoa4XMgovMVLAXncnXCsoQvAnchMg6ksQOIEX3CqRCqIIKd47O7F7PYR1TkMNbeeSccW83SEUmtuyO5Jc_wiY0ZrrPejfiJeLgtk3snxyTd-JXW1nvjBRjfbLySxmh69u-N_cuDwvqp7A1QwK5pgV49vJlHP63g4do1q6D6kQmTWtBY7iA-beU44knFS7aCLNiq1aGN9Hhg0QTIYJ9rXXEeHbUuAPSK419ieoaj4rb_4lA-Wdaz3oWiWwH0EIzGs0Zj3srHRqfR94oe4PbJ6gz5f64k0kQ2QRWReCO5kpQeiAd1f25oP9yiH_MbpTcfxMr-z83luvUWMF6K0-A-NXEuF5AiCLkWDapNyRwpuGMs8FIdUJmPXF9TGe3wslF5sZRVTKAWRdFMVAsUn-lFT8tVAZVvd4UtScTnmxc1YOArpHD-_Lzt7NDdbuPQWQohqkGVlQVLMoJNZnF_oRLL8je6-ra17lJ8inQPICnw7GP-ne_3A03eT4zA6YsxCC3eIhQK-xyodjfm1j0cMvydXhB89fjTcuz0Uoy0oPyfstl7Sm-AUoGugNch3Mz2jQAXo0E_FX4mbkMYX2WUBW2XSNxssYZYaRXC4FUIrQoVhAJbxU6lomRQIPY8aCS0Ge9iUk8nHq4YZzJgmB7VnFRUd8Oe1sSSiIUWpMNVBONuCIT9Wjipt1lxWEs4KjlHk-SRaEZc_eX4mLwS0RcycI8eXg6kzw2WOlPvGDWalTaMryy6QdJLjoqwidHO21JSbAWPqrBzQAEcoSau_UHC6soSO9UgcBQqdAKBfJbdMhBkmxSwVoxJR_puqsTfuCT6Aa_gFixolGrbgxx5h2-XAARx4SbGplK5kWMw27FpMvgpctU248HpEQ7zGJRTJylE84EWcVHMlVm0pGZb8tlrZSQQme6zxPWbzoQv3xY8CsH4UDu1gBhmWe_wL6KwZJxj3wRrlle54cqhzStoGL5JQwMGaxdwITRusdKgmwwEQJxxH63GvPwqL9oRMvIaHyGfKegOVyG2HMyxmiQmtb5EtaFd6n3JjMCBF74Kcn33TJhQ1yjHoltdO_tKqnj0nPVgRGfN-kdJA7G6HZFvz6j82WfKmzi1lgpUcoZ5T8Fwpx-yyBHV0J4sGF0qR4uBYNcTGkFtbD0tZnUxfy_POfmf8E3phVJrS__XIvnlB5c6yvyGGdYvafQkszlRrTAzDu9pH6TZo1K3Jc1a-wfPWZJ3uBJ_cku-YeTj8piEmR-cMeyWTJR7InVB2IFZx2AoyElAFbMuPVZVp64RgC3ugiyC1nY7HycH2T3POGARB6wP4RFXybScGN4OGwM8e3W2p-Za1BTR09lHRlzeukops0DSBUkhr9GrgMZaw7eAsztGlIXZ_4"],"session_id":"{uuid.uuid4()}","actor_id":"{self.id}","client_mutation_id":"3"}},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}}',
                'server_timestamps': 'true',
                'doc_id': '7047198228715224',
            }
            self.session.post('https://www.facebook.com/api/graphql/',headers=self.headers, data=data, proxies=self.proxies)
        except:
            pass

    def reactioncmt(self, id: str, type: str):
        try:
            reac = {
                "LIKE": "1635855486666999",
                "LOVE": "1678524932434102",
                "CARE": "613557422527858",
                "HAHA": "115940658764963",
                "WOW": "478547315650144",
                "SAD": "908563459236466",
                "ANGRY": "444813342392137"
            }
            g_now = datetime.now()
            d = g_now.strftime("%Y-%m-%d %H:%M:%S.%f")
            datetime_object = datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f")
            timestamp = str(datetime_object.timestamp())
            starttime = timestamp.replace('.', '')
            id_reac = reac.get(type)
            data = {
                'av': self.id,  
                'fb_dtsg': self.fb_dtsg, 
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern', 
                'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation', 
                'variables': '{"input":{"attribution_id_v2":"CometVideoHomeNewPermalinkRoot.react,comet.watch.injection,via_cold_start,1719930662698,975645,2392950137,,","feedback_id":"'+encode_to_base64("feedback:"+str(id))+'","feedback_reaction_id":"'+id_reac+'","feedback_source":"TAHOE","is_tracking_encrypted":true,"tracking":[],"session_id":"'+str(uuid.uuid4())+'","downstream_share_session_id":"'+str(uuid.uuid4())+'","downstream_share_session_origin_uri":"https://fb.watch/t3OatrTuqv/?mibextid=Nif5oz","downstream_share_session_start_time":"'+starttime+'","actor_id":"'+self.id+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}', 
                'server_timestamps': 'true', 
                'doc_id': '7616998081714004',
            }
            self.session.post('https://www.facebook.com/api/graphql/',headers=self.headers, data=data, proxies=self.proxies)
        except:
            pass
    
    def share(self, id: str):
        try:
            data = {
                'av': self.id,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'ComposerStoryCreateMutation',
                'variables': '{"input":{"composer_entry_point":"share_modal","composer_source_surface":"feed_story","composer_type":"share","idempotence_token":"'+str(uuid.uuid4())+'_FEED","source":"WWW","attachments":[{"link":{"share_scrape_data":"{\\"share_type\\":22,\\"share_params\\":['+id+']}"}}],"reshare_original_post":"RESHARE_ORIGINAL_POST","audience":{"privacy":{"allow":[],"base_state":"EVERYONE","deny":[],"tag_expansion_state":"UNSPECIFIED"}},"is_tracking_encrypted":true,"tracking":["AZWWGipYJ1gf83pZebtJYQQ-iWKc5VZxS4JuOcGWLeB-goMh2k74R1JxqgvUTbDVNs-xTyTpCI4vQw_Y9mFCaX-tIEMg2TfN_GKk-PnqI4xMhaignTkV5113HU-3PLFG27m-EEseUfuGXrNitybNZF1fKNtPcboF6IvxizZa5CUGXNVqLISUtAWXNS9Lq-G2ECnfWPtmKGebm2-YKyfMUH1p8xKNDxOcnMmMJcBBZkUEpjVzqvUTSt52Xyp0NETTPTVW4zHpkByOboAqZj12UuYSsG3GEhafpt91ThFhs7UTtqN7F29UsSW2ikIjTgFPy8cOddclinOtUwaoMaFk2OspLF3J9cwr7wPsZ9CpQxU21mcFHxqpz7vZuGrjWqepKQhWX_ZzmHv0LR8K07ZJLu8yl51iv-Ram7er9lKfWDtQsuNeLqbzEOQo0UlRNexaV0V2m8fYke8ubw3kNeR5XsRYiyr958OFwNgZ3RNfy-mNnO9P-4TFEF12NmNNEm4N6h0_DRZ-g74n-X2nGwx9emPv4wuy9kvQGeoCqc636BfKRE-51w2GFSrHAsOUJJ1dDryxZsxQOEGep3HGrVp_rTsVv7Vk3JxKxlzqt3hnBGDgi6suTZnJw69poVOIz6TPCTthRhj7XUu4heyKBSIeHsjBRC2_s3NwuZ4kKNCQ2JkVuBXz_hsRhDmbAnBi6WUFIJhLHO_bGgKbEASuU4vtj4FNKo_G8p-J1kYmCo0Pi72Csi3EikuocfjHFwfSD3cCbetr3V8Yp6OmSGkqX63FkSqzBoAcHFeD-iyCAkn0UJGqU-0o670ZoR-twkUDcSJPXDN2NYQfqiyb9ZknZ7j04w1ZfAyaE7NCiCc-lDt1ic79XyHunjOyLStgXIW30J4OEw_hAn86LlRHbYVhi-zBBTZWWnEl9piuUz0qtnN-qEd002DjNYaMy0aDAbL9oOYDdN8mHvnXq1aKove9I4Jy0WtlxeN8279ayz7NdDZZ9LrajY_YxIJJqdZtJIuRYTunEeDsFrORpu3RYRbFwpGnQbHeSLH1YvwOyOJRXhYYmVLJEGD2N9r5wkPbgbx2HoWsGjWj_DpkEAyg59eBJy4RYPJHvOsetBQABEWmGI7nhUDYTPdhrzVxqB_g4fQ9JkPzIbEhcoEZjmspGZcR4z4JxUDJCNdAz2aK4lR4P5WTkLtj2uXMDD_nzbl8r_DMcj23bjPiSe0Fubu-VIzjwr7JgPNyQ1FYhp5u4lpqkkBkGtfyAaUjCgFhg4FW-H3d3vPVMO--GxbhK9kN0QAcOE3ZqQR2dRz6NbhcvTyNfDxy0dFTRw-f-vxn04gjJB5ZEG3WfSzQv0VbqDYm6-NFYAzIxbDLoiCu34WAa2lckx5qxncXBhQj6Fro2gXGPXo4d32DvqQg7_RHQ-SF_WLqdxRCXF91NIqxYmFZsOJAuQ5m6TafzuNnQoJB3OQFoknv8Uy5O4FKuwazh1rvLrsj-1QEMi3sTrr9KxJkZy9EKXs92ndlb3edgfycLOffTil-gW2BvxeNiMQzqF1xJqFBKHDyatgwpXDX81HDwxkuMEaGPREIeQLuOlBJrL_20RD1e4Gu4tjQD8vRsb29UNG60DqpDvc-H4Z2oxeppm0KIwQNaCTtGUxxmvT807fXMnuVEf5QI5qTx9YRJh56GiWLoHC_zPMhoikMbAybIVWh9HtVgZGgImDmz0l9P4LgtpKNnKbQj_2ZKn2ZhOYKZLdt1P2Jq2Z2z76MtbRQTrpZpFb14zWVnh1LFCSFPAB7sqC1-u-KQOf2_SjEecztPccso8xZB2nkhLetyPn9aFuO-J_LCZydQeiroXx4Z8NxhDpbLoOpw2MbRCVB_TxfnLGNn1QD0To9TTChxK5AHNRRLDaj3xK1e0jd37uSmHTkT6QJVHFHEYMVLBcuV1MQcoy0wsvc1sRb",null],"logging":{"composer_session_id":"'+str(uuid.uuid4())+'"},"navigation_data":{"attribution_id_v2":"FeedsCometRoot.react,comet.most_recent_feed,tap_bookmark,1719641912186,189404,608920319153834,,"},"event_share_metadata":{"surface":"newsfeed"},"actor_id":"'+self.id+'","client_mutation_id":"3"},"feedLocation":"NEWSFEED","feedbackSource":1,"focusCommentID":null,"gridMediaWidth":null,"groupID":null,"scale":1,"privacySelectorRenderLocation":"COMET_STREAM","checkPhotosToReelsUpsellEligibility":false,"renderLocation":"homepage_stream","useDefaultActor":false,"inviteShortLinkKey":null,"isFeed":true,"isFundraiser":false,"isFunFactPost":false,"isGroup":false,"isEvent":false,"isTimeline":false,"isSocialLearning":false,"isPageNewsFeed":false,"isProfileReviews":false,"isWorkSharedDraft":false,"hashtag":null,"canUserManageOffers":false,"__relay_internal__pv__CometIsAdaptiveUFIEnabledrelayprovider":true,"__relay_internal__pv__CometUFIShareActionMigrationrelayprovider":true,"__relay_internal__pv__IncludeCommentWithAttachmentrelayprovider":true,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false,"__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider":false,"__relay_internal__pv__IsWorkUserrelayprovider":false,"__relay_internal__pv__IsMergQAPollsrelayprovider":false,"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":true,"__relay_internal__pv__StoriesRingrelayprovider":false,"__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider":false}',
                'server_timestamps': 'true',
                'doc_id': '8167261726632010'
            }
            self.session.post("https://www.facebook.com/api/graphql/",headers=self.headers, data=data, proxies=self.proxies)
        except:
            pass

    def group(self, id: str):
        try:
            data = {
                'av':self.id,
                'fb_dtsg':self.fb_dtsg,
                'jazoest':self.jazoest,
                'fb_api_caller_class':'RelayModern',
                'fb_api_req_friendly_name':'GroupCometJoinForumMutation',
                'variables':'{"feedType":"DISCUSSION","groupID":"'+id+'","imageMediaType":"image/x-auto","input":{"action_source":"GROUP_MALL","attribution_id_v2":"CometGroupDiscussionRoot.react,comet.group,via_cold_start,1673041528761,114928,2361831622,","group_id":"'+id+'","group_share_tracking_params":{"app_id":"2220391788200892","exp_id":"null","is_from_share":false},"actor_id":"'+self.id+'","client_mutation_id":"1"},"inviteShortLinkKey":null,"isChainingRecommendationUnit":false,"isEntityMenu":true,"scale":2,"source":"GROUP_MALL","renderLocation":"group_mall","__relay_internal__pv__GroupsCometEntityMenuEmbeddedrelayprovider":true,"__relay_internal__pv__GlobalPanelEnabledrelayprovider":false}',
                'server_timestamps':'true',
                'doc_id':'5853134681430324',
                'fb_api_analytics_tags':'["qpl_active_flow_ids=431626709"]',
            }
            self.session.post('https://www.facebook.com/api/graphql/',headers=self.headers, data=data, proxies=self.proxies)
        except:
            pass
    
    def checkDissmiss(self):
        try:
            response = self.session.get('https://www.facebook.com/', headers=self.headers, timeout=30)
            if '601051028565049' in response.text:
                return 'Dissmiss'
            if '1501092823525282' in response.text:
                return 'Checkpoint282'
            if '828281030927956' in response.text:
                return 'Checkpoint956'
            if 'title="Log in to Facebook">' in response.text:
                return 'CookieOut'
            else:
                return 'Biblock'
        except:
            pass
        
    def clickDissMiss(self):
        try:
            data = {
                "av": self.id,
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest,
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "FBScrapingWarningMutation",
                "variables": "{}",
                "server_timestamps": "true",
                "doc_id": "6339492849481770"
            }
            self.session.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, timeout=30)
        except:
            pass

class NextCaptcha:
    def __init__(self, apikey):
        self.apikey = apikey
        self.session = requests.Session()

    def recaptchav2(self, sitekey, siteurl):
        try:
            data = {
                "clientKey": self.apikey,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": siteurl,
                    "websiteKey": sitekey
                }
            }
            response = self.session.post('https://api.3xcaptcha.com/createTask', json=data).json()
            if response.get('errorId', 0) != 0:
                return {'error': response.get('errorId', 200), 'message': response.get('errorDescription', 'Unknown error')}
            return {'status': "success", 'task_id': response.get('taskId')}
        except requests.RequestException as e:
            return {'error': 500, 'message': str(e)}
        except Exception as e:
            return {'error': 200, 'message': str(e)}

    def get_result(self, task_id, max_attempts=10):
        data = {
            "clientKey": self.apikey,
            "taskId": task_id
        }
        wait_time = 3
        for x in range(max_attempts):
            try:
                response = self.session.post('https://api.3xcaptcha.com/getTaskResult', json=data).json()
                if response.get('errorId', 0) != 0:
                    return {'error': response.get('errorId', 200), 'message': response.get('errorDescription', 'Unknown error')}
                if response.get('status') == 'ready':
                    return {'status': "success", 'token': response['solution']['gRecaptchaResponse']}
                
                sleep(wait_time)
                wait_time = min(wait_time + 2, 10)

            except requests.RequestException as e:
                return {'error': 500, 'message': str(e)}
            except Exception as e:
                return {'error': 200, 'message': str(e)}
        return {'error': 408, 'message': 'Timeout: CAPTCHA not ready after multiple attempts'}

class TraoDoiSub(object):
    def __init__ (self, username: str, password: str, proxy=None):
        try:
            self.username = username
            self.password = password
            self.proxies = None
            self.session = requests.Session()
            session = self.session.post(
                'https://traodoisub.com/scr/login.php',
                data={'username': self.username, 'password': self.password},
                timeout=10
            )
            self.cookie = session.headers['Set-cookie'].split(';')[0]
            self.headers = {
                'authority': 'traodoisub.com', 
                'accept': 'application/json, text/javascript, */*; q=0.01', 
                'cache-control': 'max-age=0', 
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 
                'origin': 'https://traodoisub.com', 
                'referer': 'https://traodoisub.com/', 
                'x-requested-with': 'XMLHttpRequest', 
                'cookie': self.cookie
            }
            if proxy:
                proxy = proxy.strip()
                parts = proxy.split(':')
                if len(parts) == 4:
                    try:
                        host, port, user, past = parts
                        int(port)
                    except ValueError:
                        user, past, host, port = parts
                    self.proxies = {
                        'http': f'http://{user}:{past}@{host}:{port}',
                        'https': f'http://{user}:{past}@{host}:{port}'
                    }
            response = self.session.get(
                'https://traodoisub.com/view/setting/load.php',
                headers=self.headers,
                proxies=self.proxies,
                timeout=10
            ).json()
            self.token = response['tokentds']
            self.user = response['user']
            self.xu = response['xu']
        except:
            pass
    def set_proxy(self, proxy_str: str | None):
        self.proxies = to_requests_proxies(proxy_str)        
    def info(self):
        try:
            return {'status': "success", 'user': self.user, 'xu': self.xu, 'token': self.token}
        except:
            return {'error': 200}
        
    def datnick(self, id: str):
        response = self.session.post('https://traodoisub.com/scr/datnick.php',headers=self.headers, data={'iddat': id}, proxies=self.proxies).text
        if response == '1':
            return True
        else:
            return False
    
    def themnick(self, id, capcha):
        response = self.session.post('https://traodoisub.com/scr/add_uid.php',headers=self.headers, data={'idfb': id, 'g-recaptcha-response': capcha}, proxies=self.proxies).text
        if '{"success":true}' in response:
            return True
        else:
            return json.loads(response)
    
    def get_g_recaptcha_response(self, apikey):
        try:
            response = self.session.get('https://traodoisub.com/view/cauhinh/', headers=self.headers, proxies=self.proxies)
            sitekey = response.text.split('data-sitekey="')[1].split('"')[0]
            captcha_solver = NextCaptcha(apikey)
            recaptchav2 = captcha_solver.recaptchav2(sitekey, response.url)
            if recaptchav2.get('status') != 'success':
                return {'error': 200, 'message': 'Không thể tạo task CAPTCHA'}
            task_id = recaptchav2.get('task_id')
            g_recaptcha_response = captcha_solver.get_result(task_id)
            if g_recaptcha_response.get('status') == 'success':
                return {'status': 'success', 'token': g_recaptcha_response['token']}
            else:
                return {'error': 200, 'message': 'Không thể lấy token CAPTCHA'}
        except Exception as e:
            return {'error': 500, 'message': str(e)}
    
    def getjob(self, type: str):
        try:
            getjob = self.session.get(
                f'https://traodoisub.com/api/?fields={type}&access_token={self.token}&type=ALL',
                proxies=self.proxies,
                timeout=60
            )
            return getjob
        except Exception:
            class _EmptyResp:
                text = ''
                def json(self):
                    return {}
            return _EmptyResp()
    
    def nhanxu(self, type: str, id: str) -> dict:
        try:
            nhanxu = self.session.get(
                f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}',
                proxies=self.proxies,
                timeout=20
            ).json()
            return nhanxu if isinstance(nhanxu, dict) else {}
        except Exception:
            return {}
    
    def cache_jobs(self, type: str, id: str) -> bool:
        try:
            caches = self.session.get(
                f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}',
                proxies=self.proxies,
                timeout=60
            ).json()
            # Một số phản hồi không có khóa 'cache' (khi lỗi hoặc chưa ghi nhận). Trả về 0 để tránh KeyError.
            return int(caches.get('cache', 0) or 0)
        except Exception:
            # Lỗi mạng/parse → coi như chưa cache nhiệm vụ nào
            return 0

def check_proxy(proxy):
    session = requests.Session()
    response = session.post('https://kiemtraip.vn/check-proxy',data={'option': 'checkCountry', 'changeTimeout': '5000', 'changeUrl': 'http://www.google.com', 'proxies': str(proxy)}).text
    if '<span class="text-success copy">' in response:
        ip = response.split('<span class="text-success copy">')[1].split()[0].split('</span>')[0]
        return {'status': "success", 'ip': ip}
    else:
        return {'status': "error", 'ip': None}

def add_proxy():
    i = 1
    proxy_list = []
    print(f"{luc}Nhập Proxy Theo Dạng{trang}: {vang}username:password:host:port hoặc host:port:username:password")
    print(f"{luc}Nhấn Enter để bỏ qua và tiếp tục không dùng proxy.")
    while True:
        proxy = input(f'{luc}Nhập Proxy Số {vang}{i}{trang}: {vang}').strip()
        if proxy == '':
            if i == 1:
                return []
            break
        try:
            check = check_proxy(proxy)
            if check['status'] == "success":
                i += 1
                print(f'{luc}Proxy Hoạt Động: {vang}{check["ip"]}')
                proxy_list.append(proxy)
            else:
                print(f'{do}Proxy Die! Vui Lòng Nhập Lại !!!')
        except Exception as e:
            print(f'{do}Lỗi Kiểm Tra Proxy: {str(e)}')
    return proxy_list

def add_proxy_no_check():
    i = 1
    proxy_list_local = []
    print(f"{luc}Nhập Proxy Theo Dạng{trang}: {vang}username:password:host:port hoặc host:port:username:password")
    print(f"{luc}Nhấn Enter để kết thúc nhập và lưu.")
    while True:
        proxy = input(f'{luc}Nhập Proxy Số {vang}{i}{trang}: {vang}').strip()
        if proxy == '':
            if i == 1:
                return []
            break
        proxy_list_local.append(proxy)
        i += 1
    return proxy_list_local
    
def addcookie():
    i = 0
    while True:
        i += 1
        cookie = input(f'{thanh}{luc}Nhập Cookie Facebook Số{vang} {i}{luc}: {vang}')
        if cookie == '' and i != 1:
            break 
        proxy = proxy_list[0] if proxy_list else None
        fb = Facebook(cookie, proxy)
        info = fb.info()
        if 'success' in info:
            name = info['name']
            print(f'{thanh}{luc}Tên Facebook: {vang}{name}')
            thanhngang(65)
            listCookie.append(cookie)
        else:
            print(f'{do}Cookie Facebook Die ! Vui Lòng Nhập Lại !!!')
            i -= 1
            thanhngang(65)

if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "2":
            proxy_menu_choice2()
            # Sau khi kiểm tra xong, quay lại menu chính
            continue
        elif choice == "3":
            run_vth_game()
            # Sau khi chạy game xong, quay lại menu chính
            continue
        elif choice == "1":
            break
        else:
            print(f"{do}Lựa chọn không hợp lệ!")
            # Quay lại menu để chọn lại
            continue

    banner()
    verify_vip_key()
    if not os.path.exists('proxy-vip.json'):
        proxy_list = add_proxy()
        with open('proxy-vip.json', 'w') as f:
            json.dump(proxy_list, f)
    else:
        print(f'{thanh}{luc}Nhập {do}[{vang}1{do}] {luc}Sử Dụng Proxy Đã Lưu')
        print(f'{thanh}{luc}Nhập {do}[{vang}2{do}] {luc}Nhập Proxy Mới')
        thanhngang(65)
        chon = input(f'{thanh}{luc}Nhập{trang}: {vang}')
        thanhngang(65)
        while True:
            if chon == '1':
                print(f'{luc}Đang Lấy Dữ Liệu Đã Lưu ','          ',end='\r')
                sleep(1)
                with open('proxy-vip.json', 'r') as f:
                    proxy_list = json.load(f)
                break
            elif chon == '2':
                proxy_list = add_proxy()
                with open('proxy-vip.json', 'w') as f:
                    json.dump(proxy_list, f)
                break
            else:
                print(f'{do}Vui Lòng Nhập Đúng !!!')
banner()
if not os.path.exists('tkmktds.json'):
    while True:
        username = input(f'{thanh}{luc}Nhập Tài Khoản TĐS{trang}: {vang}')
        password = input(f'{thanh}{luc}Nhập Mật Khẩu TĐS{trang}: {vang}')
        print('\033[1;32mĐang Xử Lý...', end='\r')
        proxy = proxy_list[0] if proxy_list else None
        tds = TraoDoiSub(username, password, proxy)
        checklogin = tds.info()
        if checklogin['status'] == 'success':
            users, xu = checklogin['user'], checklogin['xu']
            print(f'{luc}Đăng Nhập Thành Công')
            with open('tkmktds.json', 'w') as f:
                json.dump([f'{username}|{password}|{users}'], f)
            break
        else:
            print(f'{do}Đăng Nhập Thất Bại')
else:
    token_json = json.loads(open('tkmktds.json', 'r').read())
    stt_token = 0
    for tokens in token_json:
        if len(tokens) > 5:
            stt_token += 1
            print(f'{thanh}{luc}Account {do}[{vang}{stt_token}{do}] {luc}Để Chạy Tài Khoản: {vang}{tokens.split("|")[2]}')
    thanhngang(65)
    print(f'{thanh}{luc}Nhập {do}[{vang}1{do}] {luc}Chọn Acc Trao Đổi Sub Để Chạy Tool')
    print(f'{thanh}{luc}Nhập {do}[{vang}2{do}] {luc}Nhập Tài Khoản & Mật Khẩu Mới')
    thanhngang(65)
    while True:
        chon = input(F'{thanh}{luc}Nhập: {vang}')
        thanhngang(65)
        if chon == '1':
            while True:
                try:
                    tokentds = int(input(f'{thanh}{luc}Nhập Số Acc: {vang}'))
                    thanhngang(65)
                    username, password = token_json[tokentds - 1].split("|")[:2]
                    proxy = proxy_list[0] if proxy_list else None
                    if proxy and not check_proxy_fast(proxy):
                        proxy = None
                    tds = TraoDoiSub(username, password, proxy)
                    checklogin = tds.info()
                    if checklogin['status'] == 'success':
                        users, xu = checklogin['user'], checklogin['xu']
                        print(f"{luc}Đăng Nhập Thành Công")
                        break
                    else:
                        print(f'{do}Đăng Nhập Thất Bại')
                except:
                    print(f'{do}Số Acc Không Tồn Tại')
            break
        elif chon == '2':
            while True:
                username = input(f'{thanh}{luc}Nhập Tài Khoản TĐS{trang}: {vang}')
                password = input(f'{thanh}{luc}Nhập Mật Khẩu TĐS{trang}: {vang}')
                print('\033[1;32mĐang Xử Lý...', end='\r')
                proxy = proxy_list[0] if proxy_list else None
                if proxy and not check_proxy_fast(proxy):
                    proxy = None
                tds = TraoDoiSub(username, password, proxy)
                checklogin = tds.info()
                if checklogin['status'] == 'success':
                    users, xu = checklogin['user'], checklogin['xu']
                    print(f'{luc}Đăng Nhập Thành Công')
                    token_json.append(f'{username}|{password}|{users}')
                    with open('tkmktds.json', 'w') as f:
                        json.dump(token_json, f)
                    break
                else:
                    print(f'{do}Đăng Nhập Thất Bại')
            break
        else:
            print(f'{do}Vui Lòng Nhập Chính Xác')
banner()
if os.path.exists(f'cookiefb-vip-tds.json') == False:
    addcookie()
    with open('cookiefb-vip-tds.json','w') as f:
        json.dump(listCookie, f)
else:
    print(f'{thanh}{luc}Nhập {do}[{vang}1{do}] {luc}Sử Dụng Cookie Facebook Đã Lưu')
    print(f'{thanh}{luc}Nhập {do}[{vang}2{do}] {luc}Nhập Cookie Facebook Mới')
    thanhngang(65)
    chon = input(f'{thanh}{luc}Nhập{trang}: {vang}')
    thanhngang(65)
    while True:
        if chon == '1':
            print(f'{luc}Đang Lấy Dữ Liệu Đã Lưu ','          ',end='\r')
            sleep(1)
            listCookie = json.loads(open('cookiefb-vip-tds.json', 'r').read())
            break
        elif chon == '2':
            addcookie()
            with open('cookiefb-vip-tds.json','w') as f:
                json.dump(listCookie, f)
            break
        else:
            print(f'{do}Vui Lòng Nhập Đúng !!!')
banner()
print(f'{thanh}{luc}Tên Tài Khoản{trang}: {vang}{users}')
print(f'{thanh}{luc}Xu Hiện Tại{trang}: {vang}{str(format(int(checklogin['xu']),","))}')
print(f'{thanh}{luc}Số Cookie Facebook{trang}: {vang}{len(listCookie)}')
print(f'{thanh}{luc}Số Proxy Live{trang}: {vang}{len(proxy_list)}')
thanhngang(65)
list_nv = []
print(f'{thanh}{luc}Nhập {do}[{vang}1{do}]{luc} Để Chạy Nhiệm Vụ Like')
print(f'{thanh}{luc}Nhập {do}[{vang}2{do}]{luc} Để Chạy Nhiệm Vụ Cảm Xúc')
print(f'{thanh}{luc}Nhập {do}[{vang}3{do}]{luc} Để Chạy Nhiệm Vụ Cảm Xúc Cmt')
print(f'{thanh}{luc}Nhập {do}[{vang}4{do}]{luc} Để Chạy Nhiệm Vụ Cảm Xúc Vip')
print(f'{thanh}{luc}Nhập {do}[{vang}5{do}]{luc} Để Chạy Nhiệm Vụ Share')
print(f'{thanh}{luc}Nhập {do}[{vang}6{do}]{luc} Để Chạy Nhiệm Vụ Share Vip')
print(f'{thanh}{luc}Nhập {do}[{vang}7{do}]{luc} Để Chạy Nhiệm Vụ Follow')
print(f'{thanh}{luc}Nhập {do}[{vang}8{do}]{luc} Để Chạy Nhiệm Vụ Like Page')
print(f'{thanh}{luc}Nhập {do}[{vang}9{do}]{luc} Để Chạy Nhiệm Vụ Like Page Vip')
print(f'{thanh}{luc}Nhập {do}[{vang}0{do}]{luc} Để Chạy Nhiệm Vụ Group')
print(f'{thanh}{luc}Có Thể Chọn Nhiều Nhiệm Vụ {do}({vang}VD: 123...{do})')
thanhngang(65)
if os.path.exists("setting.json"):
    with open("setting.json", "r", encoding="utf-8") as file:
        settings = json.load(file)
else:
    settings = {}

if "runidfb" not in settings:
    settings["runidfb"] = "n"  # hoặc "y"
    with open("setting.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

use_saved_config = input(f'{thanh}{luc}Bạn Có Muốn Sử Dụng Cấu Hình Cũ Không? {do}({vang}y/n{do}){luc}: {vang}')

if use_saved_config.lower() == "y":
    print(f'{thanh}{luc}Sử dụng cấu hình đã lưu')
elif use_saved_config.lower() == "n":
    settings.clear()
    settings["nhiemvu"] = input(f'{thanh}{luc}Nhập Số Để Chọn Nhiệm Vụ{trang}: {vang}')
    while True:
        try:
            settings["delay"] = int(input(f'{thanh}{luc}Nhập Delay Job{trang}: {vang}'))
            break
        except:
            print(f"{do}Vui Lòng Nhập Số")
    while(True):
        try:
            settings["delay_getjob"] = int(input(f'{thanh}{luc}Nhập Delay Get Job {do}({vang}VD: 30{do}){trang}: {vang}'))
            break
        except:
            print(f'{do}Vui Lòng Nhập Số')
    while True:
        try:
            settings["JobbBlock"] = int(input(f'{thanh}{luc}Sau Bao Nhiêu Nhiệm Vụ Chống Block{trang}: {vang}'))
            if settings["JobbBlock"] <= 1:
                print(f"{do}Vui Lòng Nhập Lớn Hơn 1")
                continue
            break
        except:
            print(f"{do}Vui Lòng Nhập Số")
    while True:
        try:
            settings["DelayBlock"] = int(input(f"{thanh}{luc}Sau {vang}{settings['JobbBlock']} {luc}Nhiệm Vụ Nghỉ Bao Nhiêu Giây{trang}: {vang}"))
            break
        except:
            print(f"{do}Vui Lòng Nhập Số")
    while True:
        try:
            settings["JobBreak"] = int(input(f'{thanh}{luc}Sau Bao Nhiêu Nhiệm Vụ Chuyển Acc{trang}: {vang}'))
            if settings["JobBreak"] <= 1:
                print(f"{do}Vui Lòng Nhập Lớn Hơn 1")
                continue
            break
        except:
            print(f"{do}Vui Lòng Nhập Số")
    settings["autoch"] = input(f'{thanh}{luc}Bạn Có Muốn Auto Cấu Hình Không? {do}({vang}y/n{do}){luc}: {vang}')
    if settings["autoch"] == "y":
        settings["apikey"] = input(f'{thanh}{luc}Nhập Api Key 3xcaptcha.com{trang}: {vang}')
    else:
        settings["apikey"] = ""
    settings["runidfb"] = input(f'{thanh}{luc}Bạn Có Muốn Ẩn Id Facebook Không? {do}({vang}y/n{do}){luc}: {vang}')
    settings["configured"] = "y"
    with open("setting.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)
thanhngang(65)
stt = 0
totalxu = 0
xuthem = 0
# Khởi tạo bộ xoay proxy toàn cục
rotator_global = ProxyRotator(proxy_list)

while True:
    # Hiển thị đếm ngược thời gian sử dụng key (UTC+7)
    try:
        if 'VIP_KEY_EXPIRY_SYS' in globals():
            now_sys = datetime.now()
            if now_sys >= VIP_KEY_EXPIRY_SYS:
                print(f"{do}Key đã hết hạn. Dừng tool.")
                raise SystemExit(0)
            remaining = VIP_KEY_EXPIRY_SYS - now_sys
            # Chuyển đổi hiển thị theo UTC+7
            expiry_vn = (VIP_KEY_EXPIRY_SYS + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            hrs, rem = divmod(int(remaining.total_seconds()), 3600)
            mins, secs = divmod(rem, 60)
            # Dọn dòng hiện tại để không dính vào các print dùng end='\r'
            print(' ' * 120, end='\r')
            print(f"{trang}[{xanh}KEY VIP{trang}] Còn lại: {vang}{hrs:02d}:{mins:02d}:{secs:02d}{trang} | Hết hạn: {vang}{expiry_vn} (UTC+7){trang}", end='\r')
    except Exception:
        pass
    if len(listCookie) == 0:
        print(f'{do}Đã Xóa Tất Cả Cookie, Vui Lòng Nhập Lại !!!')
        addcookie()
        with open('cookiefb-vip-tds.json','w') as f: 
            json.dump(listCookie, f)
    if len(proxy_list) == 0:
        print(f'{do}Không có Proxy! Tiếp tục chạy mà không dùng Proxy', '            ', end="\r")
    for index, cookie in enumerate(listCookie):
        # Lấy proxy hiện tại từ rotator
        proxy = rotator_global.current()
        myip = None
        if proxy:
            if check_proxy_fast(proxy):
                try:
                    ipcheck = check_proxy(proxy)
                    myip = ipcheck['ip'] if ipcheck['status'] == 'success' else None
                except Exception:
                    myip = None
            else:
                # Proxy hiện tại chết → xoay sang proxy khác và re-init nhanh
                new_proxy, fb_tmp, tds_tmp = rotate_and_reinit(rotator_global)
                if not new_proxy:
                    print(f'{do}Hết proxy sống. Tiếp tục chạy không proxy.')
                    proxy = None
                else:
                    proxy = new_proxy
                    try:
                        ipcheck = check_proxy(proxy)
                        myip = ipcheck['ip'] if ipcheck['status'] == 'success' else None
                    except Exception:
                        myip = None
        JobError, JobSuccess, JobFail = 0, 0, 0
        fb = Facebook(cookie, proxy)
        # Đồng bộ proxy cho TĐS (giữ phiên đăng nhập hiện tại)
        try:
            tds.set_proxy(proxy)
        except Exception:
            pass
        info = fb.info()
        if 'success' in info:
            namefb = info['name']
            idfb = str(info['id'])
            idrun = idfb[0]+idfb[1]+idfb[2]+"#"*(int(len(idfb)-3)) if settings.get("runidfb","n").upper() =='Y' else idfb
        else:
            print(f'{do}Cookie Facebook Die ! Đã Xóa Ra Khỏi List !!!')
            listCookie.remove(cookie)
            break
        datnick = tds.datnick(idfb)
        if datnick == True:
            print(f'{luc}Id Facebook{trang}: {vang}{idrun}{do} | {luc}Tên Tài Khoản{trang}: {vang}{namefb}{do} | {luc}Proxy{trang}: {vang}{myip}')
        else:
            if settings["apikey"]:
                print(f'{luc}Đang Thêm Id Facebook{trang}: {vang}{idfb}{do} | {luc}Tên Tài Khoản{trang}: {vang}{namefb}','            ',end="\r")
                gaicapcha = tds.get_g_recaptcha_response(settings["apikey"])
                if gaicapcha.get('status') == 'success':
                    add_uid = tds.themnick(idfb, gaicapcha.get('token'))
                    if add_uid == True:
                        datnick = tds.datnick(idfb)
                        if datnick == True:
                            print(f'{luc}Id Facebook{trang}: {vang}{idrun}{do} | {luc}Tên Tài Khoản{trang}: {vang}{namefb}{do} | {luc}Proxy{trang}: {vang}{myip}')
                        else:
                            print(f'{luc}Chưa Cấu Hình Id Facebook{trang}: {vang}{idfb}{do} | {luc}Tên Tài Khoản{trang}: {vang}{namefb}')
                            listCookie.remove(cookie)
                            break
                    else:
                        print(f'{luc}{add_uid}')
                        listCookie.remove(cookie)
                        break
                else:
                    print(f'{luc}Không Thể Giải Lỗi Rồi Hì Hì !!!!')
                    sleep(10)
                    continue
            else:
                print(f'{luc}Chưa Cấu Hình Id Facebook{trang}: {vang}{idfb}{do} | {luc}Tên Tài Khoản{trang}: {vang}{namefb}')
                listCookie.remove(cookie)
                break

        while True:
            chuyen = False
            nextDelay = False
            if settings["nhiemvu"] == '':
                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Tất Cả Tương Tác')
                listCookie.remove(cookie)
                chuyen = True
                break

            if '1' in settings["nhiemvu"]:
                try:
                    getjob = tds.getjob('like')
                except requests.RequestException:
                    new_proxy, fb_new, tds_new = rotate_and_reinit(rotator_global)
                    if new_proxy:
                        proxy = new_proxy
                        fb = fb_new
                        tds = tds_new
                        print(f'{vang}Đã chuyển sang proxy khác để tiếp tục job LIKE.')
                        try:
                            getjob = tds.getjob('like')
                        except Exception as e:
                            print(f'{do}Lỗi getjob LIKE sau khi xoay proxy: {e}')
                            getjob = None
                    else:
                        print(f'{do}Không còn proxy khác, tiếp tục không proxy.')
                        tds.set_proxy(None)
                        fb.set_proxy(None)
                        try:
                            getjob = tds.getjob('like')
                        except Exception as e:
                            print(f'{do}Lỗi getjob LIKE khi không proxy: {e}')
                            getjob = None

                if not getjob:
                    chuyen = True
                else:
                    if "id" in getjob.text:
                        print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Like        ",end = "\r")
                    for x in getjob.json():
                        nextDelay = False
                        id = x['id']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.reaction(id_, 'LIKE')
                        nhanxu = tds.nhanxu('like', id)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}LIKE{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Like')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('1','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                if getjob and 'error' in getjob.text:
                    if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                        print(f'{do}Tiến Hành Get Job Like, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                        sleep(1)
                        Delay(settings["delay_getjob"])
                    elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                        print(do+getjob.json()['error']+'          ')
                        listCookie.remove(cookie)
                        break
                    else:
                        print(do+getjob.json()['error']+'          ',end="\r")

            if '2' in settings["nhiemvu"]:
                getjob = tds.getjob('reaction')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Cảm Xúc        ",end = "\r")
                    for x in getjob.json():
                        nextDelay = False
                        id = x['id']
                        type = x['type']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.reaction(id_, type)
                        nhanxu = tds.nhanxu(type, id)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}{type}{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Cảm Xúc')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('2','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Cảm Xúc, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")

            if '3' in settings["nhiemvu"]:
                getjob = tds.getjob('facebook_reactioncmt')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Cảm Xúc        ",end = "\r")
                    for x in getjob.json()['data']:
                        nextDelay = False
                        id = x['id']
                        type = x['type']
                        code = x['code']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.reactioncmt(id_, type)
                        nhanxu = tds.nhanxu('facebook_reactioncmt', code)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}{type}{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Cảm Xúc Cmt')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('3','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Cảm Xúc, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")

            if '4' in settings["nhiemvu"]:
                getjob = tds.getjob('facebook_reaction')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Cảm Xúc        ",end = "\r")
                    for x in getjob.json()['data']:
                        nextDelay = False
                        id = x['id']
                        type = x['type']
                        code = x['code']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.reaction(id_, type)
                        nhanxu = tds.nhanxu('facebook_reaction', code)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}{type}{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Cảm Xúc')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('4','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Cảm Xúc, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")
            
            if '5' in settings["nhiemvu"]:
                getjob = tds.getjob('share')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Share        ",end = "\r")
                    for x in getjob.json():
                        nextDelay = False
                        id = x['id']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.share(id_)
                        nhanxu = tds.nhanxu('SHARE', id)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}SHARE{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Share')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('5','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Share, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")

            if '6' in settings["nhiemvu"]:
                getjob = tds.getjob('facebook_share')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Share        ",end = "\r")
                    for x in getjob.json()['data']:
                        nextDelay = False
                        id = x['id']
                        code = x['code']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.share(id_)
                        nhanxu = tds.nhanxu('facebook_share', code)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}SHARE{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Share')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('6','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Share, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")

            if '7' in settings["nhiemvu"]:
                getjob = tds.getjob('facebook_follow')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Follow        ",end = "\r")
                    for x in getjob.json()['data']:
                        nextDelay = False
                        id = x['id']
                        code = x['code']
                        id_ = id.split('_')[1] if '_' in id else id
                        fl = fb.follow(id_)
                        if fl == False:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")
                        else:
                            nextDelay = True
                            JobSuccess += 1
                            timejob = datetime.now().strftime('%H:%M:%S')
                            stt+=1
                            JobFail = 0
                            caches = tds.cache_jobs('facebook_follow_cache', code)
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}FOLLOW{do} | {trang}{id_}{do} | {xanh}{caches}/5{do}')
                            if caches >= 5:
                                sleep(3)
                                for _ in range(5):
                                    nhanxu = tds.nhanxu('facebook_follow', 'facebook_api')
                                    if 'success' in nhanxu:
                                        job_success = nhanxu['data']['job_success']
                                        msg = nhanxu['data']['msg']
                                        xu = nhanxu['data']['xu']
                                        xutotal = msg.replace(' Xu','')
                                        totalxu += int(xutotal)
                                        stt+=1
                                        timejob = datetime.now().strftime('%H:%M:%S')
                                        print(f'{do}| {vang}X{do} | {xanh}{timejob}{do} | {vang}FOLLOW{do} | {trang}{id_}{do} | {xanh}{job_success}/{caches}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))} Xu')
                                        break
                                    sleep(2)
                                if stt % 5 == 0:
                                    print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                                break

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Follow')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('7','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Follow, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")
                            tds.nhanxu('facebook_follow', 'facebook_api')

            if '8' in settings["nhiemvu"]:
                getjob = tds.getjob('page')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Like Page        ",end = "\r")
                    for x in getjob.json():
                        nextDelay = False
                        id = x['id']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.likepage(id_)
                        nhanxu = tds.nhanxu('PAGE', id)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}LIKEPAGE{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Page')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('8','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Like Page, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")

            if '9' in settings["nhiemvu"]:
                getjob = tds.getjob('facebook_page')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Like Page        ",end = "\r")
                    for x in getjob.json()['data']:
                        nextDelay = False
                        id = x['id']
                        code = x['code']
                        id_ = id.split('_')[1] if '_' in id else id
                        fl = fb.likepage(id_)
                        if fl == False:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")
                        else:
                            nextDelay = True
                            JobSuccess += 1
                            timejob = datetime.now().strftime('%H:%M:%S')
                            stt+=1
                            JobFail = 0
                            caches = tds.cache_jobs('facebook_page_cache', code)
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}LIKEPAGE{do} | {trang}{id_}{do} | {xanh}{caches}/5{do}')
                            if caches >= 5:
                                sleep(3)
                                for _ in range(5):
                                    nhanxu = tds.nhanxu('facebook_page', 'facebook_api')
                                    if 'success' in nhanxu:
                                        job_success = nhanxu['data']['job_success']
                                        msg = nhanxu['data']['msg']
                                        xu = nhanxu['data']['xu']
                                        xutotal = msg.replace(' Xu','')
                                        totalxu += int(xutotal)
                                        stt+=1
                                        timejob = datetime.now().strftime('%H:%M:%S')
                                        print(f'{do}| {vang}X{do} | {xanh}{timejob}{do} | {vang}LIKEPAGE{do} | {trang}{id_}{do} | {xanh}{job_success}/{caches}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))} Xu')
                                        break
                                    sleep(2)
                                if stt % 5 == 0:
                                    print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                                break

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Page')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('9','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Like Page, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")
                            tds.nhanxu('facebook_follow', 'facebook_api')

            if '0' in settings["nhiemvu"]:
                getjob = tds.getjob('group')
                if "id" in getjob.text:
                    print(luc+f" Đã Tìm Thấy {len(getjob.json())} Nhiệm Vụ Group        ",end = "\r")
                    for x in getjob.json():
                        nextDelay = False
                        id = x['id']
                        id_ = id.split('_')[1] if '_' in id else id
                        fb.group(id_)
                        nhanxu = tds.nhanxu('GROUP', id)
                        if 'success' in nhanxu:
                            nextDelay, msg, xu, JobFail, timejob = True, nhanxu['data']['msg'], nhanxu['data']['xu'], 0, datetime.now().strftime('%H:%M:%S')
                            xutotal = msg.replace(' Xu','')
                            totalxu += int(xutotal)
                            stt+=1
                            JobSuccess += 1
                            print(f'{do}| {vang}{stt}{do} | {xanh}{timejob}{do} | {vang}GROUP{do} | {trang}{id_}{do} | {vang}{msg}{do} | {luc}{str(format(int(xu),","))}')
                            if stt % 10 == 0:
                                print(f'{trang}[{luc}Total Cookie Facebook: {vang}{len(listCookie)}{trang}] [{luc}Total Coin: {vang}{str(format(int(totalxu),","))}{trang}] [{luc}Tổng Xu: {vang}{str(format(int(xu),","))}{trang}]')
                        else:
                            JobFail += 1
                            print(f'{trang}[{do}{JobFail}{trang}] {trang}[{do}ERROR{trang}] {trang}{id_}','            ',end="\r")

                        if JobFail >= 10:
                            check = fb.checkDissmiss()
                            if '601051028565049' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Spam')
                                fb.clickDissMiss()
                            if 'Checkpoint282' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint282')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'Checkpoint956' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Checkpoint956')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            if 'CookieOut' in check:
                                print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out')
                                listCookie.remove(cookie)
                                chuyen = True
                                break
                            else:
                                checklive = fb.info()
                                if 'error' in checklive:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Out, Đã Xoá Khỏi List')
                                    listCookie.remove(cookie)
                                    chuyen = True
                                    break
                                else:
                                    print(f'{do}Tài Khoản {vang}{namefb} {do}Đã Bị Block Group')
                                    settings["nhiemvu"] = settings["nhiemvu"].replace('0','')
                                    break

                        if JobSuccess != 0 and JobSuccess % int(settings["JobBreak"]) == 0:
                            chuyen = True
                            break

                        if nextDelay == True:
                            if stt % int(settings["JobbBlock"])==0:
                                Delay(settings["DelayBlock"])
                            else:
                                Delay(settings["delay"])

                    if chuyen == True:
                        break
                else:
                    if 'error' in getjob.text:
                        if getjob.json()['error'] == "Thao tác quá nhanh vui lòng chậm lại":
                            print(f'{do}Tiến Hành Get Job Group, COUNTDOWN: {str(round(getjob.json()["countdown"], 3))}'   ,end="\r")
                            sleep(1)
                            Delay(settings["delay_getjob"])
                        elif getjob.json()['error']=="Đã đạt giới hạn nhiệm vụ trong ngày hôm nay":
                            print(do+getjob.json()['error']+'          ')
                            listCookie.remove(cookie)
                            break
                        else:
                            print(do+getjob.json()['error']+'          ',end="\r")
