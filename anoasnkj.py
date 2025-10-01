import json
import sys
import time
import threading
import random
import logging
import math
import re
from collections import defaultdict, deque
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Tuple, Optional
from statistics import pstdev
import os
import pytz
import requests
import websocket
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.rule import Rule
from rich.text import Text
from rich import box

TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID   = None

# ================== KEY VIP VTH GAME ==================
KEY_VTH_URL = 'https://raw.githubusercontent.com/MVBL112004/lmaslckjs/main/keyvth.txt'

def _parse_expiry_datetime(exp_str: str):
    """Parse chuỗi thời gian thành datetime"""
    exp_str = exp_str.strip()
    # Epoch giây
    if exp_str.isdigit():
        try:
            return datetime.fromtimestamp(int(exp_str))
        except Exception:
            pass
    # ISO-like formats
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

def _fetch_vth_key_map(timeout_sec: int = 15):
    """Tải danh sách key từ GitHub"""
    try:
        resp = requests.get(KEY_VTH_URL, timeout=timeout_sec)
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
        exp_dt = _parse_expiry_datetime(exp)
        if k and exp_dt:
            key_map[k] = exp_dt
    return key_map

def verify_vth_key():
    """Kiểm tra key VIP cho Game VTH"""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/]")
    console.print("[bold cyan]XÁC THỰC KEY VIP - GAME VTH[/]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/]")
    console.print("[green]Vui lòng nhập key VIP để tiếp tục.[/]")
    console.print("[green]Liên hệ Zalo [bold yellow]0816042268[/] hoặc [bold yellow]long2k4.id.vn[/] để mua key.[/]\n")
    
    while True:
        try:
            user_key = input("Nhập key VIP: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[red]Đã hủy. Thoát game.[/]")
            sys.exit(0)
        
        if not user_key:
            continue
        
        console.print("[cyan]Đang kiểm tra key....[/]")
        key_map = _fetch_vth_key_map()
        
        if not key_map:
            console.print("[red]❌ Không thể truy cập server key. Kiểm tra kết nối mạng![/]")
            retry = input("Thử lại? (y/n): ").strip().lower()
            if retry != 'y':
                sys.exit(0)
            continue
        
        if user_key not in key_map:
            console.print("[red]❌ Key không hợp lệ. Vui lòng nhập lại![/]")
            console.print("[yellow]Liên hệ Zalo 0816042268 hoặc long2k4.id.vn để mua key.[/]\n")
            continue
        
        expiry = key_map[user_key]
        now_sys = datetime.now()
        
        # Chuyển sang UTC+7 để hiển thị
        from datetime import timedelta
        expiry_vn = expiry + timedelta(hours=7)
        
        if expiry <= now_sys:
            console.print(f"[red]❌ Key đã hết hạn vào {expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7). Dừng tool.[/]")
            sys.exit(0)
        else:
            console.print(f"[green]✅ Key hợp lệ! Hạn dùng tới: [bold yellow]{expiry_vn.strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)[/][/]")
            # Lưu vào global để đếm ngược
            globals()['VTH_KEY_EXPIRY'] = expiry
            break


def load_telegram_config():
    """Tải cấu hình Telegram từ file setting.json"""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    if os.path.exists("setting.json"):
        try:
            with open("setting.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                TELEGRAM_BOT_TOKEN = settings.get("telegram_bot_token")
                TELEGRAM_CHAT_ID = settings.get("telegram_chat_id")
                if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                    return True
        except Exception:
            pass
    return False


def prompt_telegram_config():
    """Yêu cầu người dùng nhập cấu hình Telegram"""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/]")
    console.print("[bold cyan]CẤU HÌNH TELEGRAM THÔNG BÁO[/]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/]")
    console.print("[yellow]Nhấn Enter để bỏ qua nếu không muốn nhận thông báo qua Telegram[/]\n")
    
    try:
        bot_token = input("Nhập Telegram Bot Token: ").strip()
        if not bot_token:
            console.print("[yellow]Đã bỏ qua cấu hình Telegram. Tool sẽ chạy không có thông báo.[/]")
            return False
        
        chat_id = input("Nhập Telegram Chat ID: ").strip()
        if not chat_id:
            console.print("[yellow]Đã bỏ qua cấu hình Telegram. Tool sẽ chạy không có thông báo.[/]")
            return False
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Đã bỏ qua cấu hình Telegram.[/]")
        return False
    
    TELEGRAM_BOT_TOKEN = bot_token
    TELEGRAM_CHAT_ID = chat_id
    
    # Lưu vào setting.json
    try:
        if os.path.exists("setting.json"):
            with open("setting.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}
        
        settings["telegram_bot_token"] = TELEGRAM_BOT_TOKEN
        settings["telegram_chat_id"] = TELEGRAM_CHAT_ID
        
        with open("setting.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        
        console.print("[green]✅ Đã lưu cấu hình Telegram vào setting.json[/]")
        return True
    except Exception as e:
        console.print(f"[red]Không thể lưu cấu hình: {e}[/]")
        return False


def tg_send(text: str, silent: bool = False):
    """Gửi tin nhắn Telegram đơn giản."""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            # "parse_mode": "HTML",  # mở nếu muốn format
            "disable_notification": bool(silent),
        }
        HTTP.post(url, json=payload, timeout=4)
    except Exception as e:
        log_debug(f"tg_send err: {e}")
# -------------------- CONFIG & GLOBALS --------------------
console = Console()
tz = pytz.timezone("Asia/Ho_Chi_Minh")

logger = logging.getLogger("escape_vip_ai_rebuild")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler("escape_vip_ai_rebuild.log", encoding="utf-8"))

# Endpoints (config)
BET_API_URL = "https://api.escapemaster.net/escape_game/bet"
WS_URL = "wss://api.escapemaster.net/escape_master/ws"
WALLET_API_URL = "https://wallet.3games.io/api/wallet/user_asset"

HTTP = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    adapter = HTTPAdapter(
        pool_connections=20, pool_maxsize=50,
        max_retries=Retry(total=3, backoff_factor=0.2,
                          status_forcelist=(500, 502, 503, 504))
    )
    HTTP.mount("https://", adapter)
    HTTP.mount("http://", adapter)
except Exception:
    pass

ROOM_NAMES = {
    1: "📦 Nhà kho", 2: "🪑 Phòng họp", 3: "👔 Phòng giám đốc", 4: "💬 Phòng trò chuyện",
    5: "🎥 Phòng giám sát", 6: "🏢 Văn phòng", 7: "💰 Phòng tài vụ", 8: "👥 Phòng nhân sự"
}
def room_label(room_id: int, include_id: bool = True) -> str:
    try:
        rid = int(room_id)
    except Exception:
        rid = room_id
    name = ROOM_NAMES.get(rid, f"Phòng {rid}")
    return f"PHÒNG_{rid} — {name}" if include_id else name
ROOM_ORDER = [1, 2, 3, 4, 5, 6, 7, 8]

# runtime state
USER_ID: Optional[int] = None
SECRET_KEY: Optional[str] = None
issue_id: Optional[int] = None
issue_start_ts: Optional[float] = None
count_down: Optional[int] = None
killed_room: Optional[int] = None
round_index: int = 0
_skip_active_issue: Optional[int] = None  # ván hiện tại đang nghỉ

room_state: Dict[int, Dict[str, Any]] = {r: {"players": 0, "bet": 0} for r in ROOM_ORDER}
room_stats: Dict[int, Dict[str, Any]] = {r: {"kills": 0, "survives": 0, "last_kill_round": None, "last_players": 0, "last_bet": 0} for r in ROOM_ORDER}

predicted_room: Optional[int] = None
last_killed_room: Optional[int] = None
prediction_locked: bool = False

# balances & pnl
current_build: Optional[float] = None
current_usdt: Optional[float] = None
current_world: Optional[float] = None
last_balance_ts: Optional[float] = None
last_balance_val: Optional[float] = None
starting_balance: Optional[float] = None
cumulative_profit: float = 0.0

# streaks
win_streak: int = 0
lose_streak: int = 0
max_win_streak: int = 0
max_lose_streak: int = 0

# betting
base_bet: float = 1.0
multiplier: float = 2.0
current_bet: Optional[float] = None
run_mode: str = "AUTO"
# Thêm vào sau dòng 123
betting_mode: str = "DEMO"  # "DEMO" hoặc "REAL"
# AUTO or STAT
bet_rounds_before_skip: int = 0
_rounds_placed_since_skip: int = 0
skip_next_round_flag: bool = False

bet_history: deque = deque(maxlen=500)
# store bet records; display last 5
bet_sent_for_issue: set = set()

# new controls
pause_after_losses: int = 0  # khi thua thì nghỉ bao nhiêu tay
_skip_rounds_remaining: int = 0
profit_target: Optional[float] = None  # take profit (BUILD)
stop_when_profit_reached: bool = False
stop_loss_target: Optional[float] = None  # stop loss (BUILD)
stop_when_loss_reached: bool = False
stop_flag: bool = False

# UI / timing
ui_state: str = "IDLE"
# analysis window timestamps
analysis_start_ts: Optional[float] = None
# when True, show a "lòa/blur" analysis visual between 45s -> 10s
analysis_blur: bool = False
# ws/poll
last_msg_ts: float = time.time()
last_balance_fetch_ts: float = 0.0
BALANCE_POLL_INTERVAL: float = 4.0
_ws: Dict[str, Any] = {"ws": None}

# selection config (used by algorithms)
SELECTION_CONFIG = {
    "max_bet_allowed": float("inf"),
    "max_players_allowed": 9999,
    "avoid_last_kill": True,
}

# REPLACED: use single VIP mode (50 formulas ensemble)
SELECTION_MODES = {
    "VIP": "Công thức SIU VIP",
    "PRO":   "PRO (SMI+Trend)",
    "META":  "META (VIP ∩ PRO)"
}
# Tăng cược tối đa +30% khi META đồng thuận (0..1 → 0..+30%).
# Nếu không muốn tăng, đặt = 0.0
# META_BET_BOOST_MAX giờ sẽ được tính random mỗi lần đặt cược
def get_meta_boost() -> float:
    """Trả về giá trị boost ngẫu nhiên từ 0.01-0.06"""
    import random
    return random.uniform(0.01, 0.06)
settings = {"algo": "META"}

# NEW: lưu lịch sử ngắn hạn cho từng phòng (để tính trend/stability)
HIST_K = 8
room_hist = {r: deque(maxlen=HIST_K) for r in ROOM_ORDER}

_spinner = ["📦", "🪑", "👔", "💬", "🎥", "🏢", "💰", "👥"]

_num_re = re.compile(r"-?\d+[\d,]*\.?\d*")

RAINBOW_COLORS = ["red", "orange1", "yellow1", "green", "cyan", "blue", "magenta"]

# -------------------- UTILITIES --------------------

def log_debug(msg: str):
    try:
        logger.debug(msg)
    except Exception:
        pass


def _parse_number(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    m = _num_re.search(s)
    if not m:
        return None
    token = m.group(0).replace(",", "")
    try:
        return float(token)
    except Exception:
        return None


def human_ts() -> str:
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def safe_input(prompt: str, default=None, cast=None):
    try:
        s = input(prompt).strip()
    except EOFError:
        return default
    if s == "":
        return default
    if cast:
        try:
            return cast(s)
        except Exception:
            return default
    return s

# -------------------- BALANCE PARSING & FETCH --------------------

def _parse_balance_from_json(j: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if not isinstance(j, dict):
        return None, None, None
    build = None
    world = None
    usdt = None

    data = j.get("data") if isinstance(j.get("data"), dict) else j
    if isinstance(data, dict):
        cwallet = data.get("cwallet") if isinstance(data.get("cwallet"), dict) else None
        if cwallet:
            for key in ("ctoken_contribute", "ctoken", "build", "balance", "amount"):
                if key in cwallet and build is None:
                    build = _parse_number(cwallet.get(key))
        for k in ("build", "ctoken", "ctoken_contribute"):
            if build is None and k in data:
                build = _parse_number(data.get(k))
        for k in ("usdt", "kusdt", "usdt_balance"):
            if usdt is None and k in data:
                usdt = _parse_number(data.get(k))
        for k in ("world", "xworld"):
            if world is None and k in data:
                world = _parse_number(data.get(k))

    found = []

    def walk(o: Any, path=""):
        if isinstance(o, dict):
            for kk, vv in o.items():
                nk = (path + "." + str(kk)).strip(".")
                if isinstance(vv, (dict, list)):
                    walk(vv, nk)
                else:
                    n = _parse_number(vv)
                    if n is not None:
                        found.append((nk.lower(), n))
        elif isinstance(o, list):
            for idx, it in enumerate(o):
                walk(it, f"{path}[{idx}]")

    walk(j)

    for k, n in found:
        if build is None and any(x in k for x in ("ctoken", "build", "contribute", "balance")):
            build = n
        if usdt is None and "usdt" in k:
            usdt = n
        if world is None and any(x in k for x in ("world", "xworld")):
            world = n

    return build, world, usdt


def balance_headers_for(uid: Optional[int] = None, secret: Optional[str] = None) -> Dict[str, str]:
    h = {
        "accept": "*/*",
        "accept-language": "vi,en;q=0.9",
        "cache-control": "no-cache",
        "country-code": "vn",
        "origin": "https://xworld.info",
        "pragma": "no-cache",
        "referer": "https://xworld.info/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "user-login": "login_v2",
        "xb-language": "vi-VN",
    }
    if uid is not None:
        h["user-id"] = str(uid)
    if secret:
        h["user-secret-key"] = str(secret)
    return h


def fetch_balances_3games(retries=2, timeout=6, params=None, uid=None, secret=None):
    """
    Non-blocking friendly: call from background threads if you don't want UI block.
    """
    global current_build, current_usdt, current_world, last_balance_ts
    global starting_balance, last_balance_val, cumulative_profit

    uid = uid or USER_ID
    secret = secret or SECRET_KEY
    payload = {"user_id": int(uid) if uid is not None else None, "source": "home"}

    attempt = 0
    while attempt <= retries:
        attempt += 1
        try:
            r = HTTP.post(
                WALLET_API_URL,
                json=payload,
                headers=balance_headers_for(uid, secret),
                timeout=timeout,
            )
            r.raise_for_status()
            j = r.json()

            build = None
            world = None
            usdt = None
            # custom parsing
            build, world, usdt = _parse_balance_from_json(j)

            if build is not None:
                if last_balance_val is None:
                    starting_balance = build
                    last_balance_val = build
                else:
                    delta = float(build) - float(last_balance_val)
                    if abs(delta) > 0:
                        cumulative_profit += delta
                        last_balance_val = build
                current_build = build
            if usdt is not None:
                current_usdt = usdt
            if world is not None:
                current_world = world

            last_balance_ts = time.time()
            return current_build, current_world, current_usdt

        except Exception as e:
            log_debug(f"wallet fetch attempt {attempt} error: {e}")
            time.sleep(min(0.6 * attempt, 2))

    return current_build, current_world, current_usdt

# -------------------- VIP ENSEMBLE SELECTION --------------------

def _room_features(rid: int):
    st = room_state.get(rid, {})
    stats = room_stats.get(rid, {})
    players = float(st.get("players", 0))
    bet = float(st.get("bet", 0))
    bet_per_player = (bet / players) if players > 0 else bet
    kill_count = float(stats.get("kills", 0))
    survive_count = float(stats.get("survives", 0))
    kill_rate = (kill_count + 0.5) / (kill_count + survive_count + 1.0)
    survive_score = 1.0 - kill_rate
    recent_history = list(bet_history)[-8:]
    recent_pen = 0.0
    for i, rec in enumerate(reversed(recent_history)):
        if rec.get("room") == rid:
            recent_pen += 0.12 * (1.0 / (i + 1))
    last_pen = 0.0
    if last_killed_room == rid:
        last_pen = 0.35 if SELECTION_CONFIG.get("avoid_last_kill", True) else 0.0
    # normalized players (0..1 roughly)
    players_norm = min(1.0, players / 50.0)
    bet_norm = 1.0 / (1.0 + bet / 2000.0)
    bpp_norm = 1.0 / (1.0 + bet_per_player / 1200.0)
    return {
        "players": players,
        "players_norm": players_norm,
        "bet": bet,
        "bet_norm": bet_norm,
        "bet_per_player": bet_per_player,
        "bpp_norm": bpp_norm,
        "kill_rate": kill_rate,
        "survive_score": survive_score,
        "recent_pen": recent_pen,
        "last_pen": last_pen
    }


def choose_room_VIP() -> Tuple[int, str]:
    """
    Build 50 deterministic formula weights, score each room and aggregate.
    Deterministic by using a fixed seed for weight generation so results are repeatable.
    """
    cand = [r for r in ROOM_ORDER]
    # deterministic weights via seeded RNG
    seed = 1234567
    rng = random.Random(seed)
    # pre-generate 50 weight sets
    formulas = []
    for i in range(50):
        # vary weights around some sensible defaults
        w_players = rng.uniform(0.2, 0.8)
        w_bet = rng.uniform(0.1, 0.6)
        w_bpp = rng.uniform(0.05, 0.6)
        w_survive = rng.uniform(0.05, 0.4)
        w_recent = rng.uniform(0.05, 0.3)
        w_last = rng.uniform(0.1, 0.6)
        noise_scale = rng.uniform(0.0, 0.08)
        formulas.append((w_players, w_bet, w_bpp, w_survive, w_recent, w_last, noise_scale))

    agg_scores = {r: 0.0 for r in cand}
    # compute per-formula scores
    for idx, wset in enumerate(formulas):
        for r in cand:
            f = _room_features(r)
            score = 0.0
            score += wset[0] * f["players_norm"]
            score += wset[1] * f["bet_norm"]
            score += wset[2] * f["bpp_norm"]
            score += wset[3] * f["survive_score"]
            score -= wset[4] * f["recent_pen"]
            score -= wset[5] * f["last_pen"]
            # small deterministic noise per formula/room
            noise = (math.sin((idx + 1) * (r + 1) * 12.9898) * 43758.5453) % 1.0
            noise = (noise - 0.5) * (wset[6] * 2.0)
            score += noise
            agg_scores[r] += score

    # normalize by number of formulas
    for r in agg_scores:
        agg_scores[r] /= len(formulas)

    ranked = sorted(agg_scores.items(), key=lambda kv: (-kv[1], kv[0]))
    best_room = ranked[0][0]
    return best_room, "LOGICVIP"

def _shares():
    tot_p = sum((room_state[r]["players"] for r in ROOM_ORDER), 0)
    tot_b = sum((room_state[r]["bet"]     for r in ROOM_ORDER), 0)
    return max(tot_p,1), max(tot_b,1)

def _room_extra_features(rid: int) -> Dict[str, float]:
    players = float(room_state[rid]["players"])
    bet     = float(room_state[rid]["bet"])
    tot_p, tot_b = _shares()
    player_share = players / tot_p
    bet_share    = bet / tot_b
    smi          = bet_share - player_share
    bpp          = bet/players if players>0 else bet

    hist = list(room_hist[rid])
    if len(hist) >= 2:
        dp = hist[-1]["players"] - hist[-2]["players"]
        db = hist[-1]["bet"]     - hist[-2]["bet"]
        vel_p = dp / max(hist[-2]["players"], 1)
        vel_b = db / max(hist[-2]["bet"], 1)
    else:
        vel_p = vel_b = 0.0

    # stability: phương sai nhỏ => ổn định cao
    if len(hist) >= 3:
        p_vals = [h["players"] for h in hist]
        b_vals = [h["bet"] for h in hist]
        p_std  = pstdev(p_vals) if len(p_vals)>=2 else 0.0
        b_std  = pstdev(b_vals) if len(b_vals)>=2 else 0.0
        p_mean = sum(p_vals)/len(p_vals)
        b_mean = sum(b_vals)/len(b_vals)
        stability = 1.0 - 0.5*( (p_std/max(p_mean,1)) + (b_std/max(b_mean,1)) )
        stability = max(0.0, min(1.0, stability))
    else:
        stability = 0.5

    # late surge flag nếu người/bet tăng nhanh khi còn ít giây
    late_surge = 1.0 if (vel_p > 0.35 or vel_b > 0.35) and (isinstance(count_down,int) and count_down<=10) else 0.0

    # crowd trap: top người nhưng bpp thấp hơn median bpp
    bpps = []
    for r in ROOM_ORDER:
        pl = float(room_state[r]["players"])
        bt = float(room_state[r]["bet"])
        bpps.append(bt/pl if pl>0 else bt)
    bpps_sorted = sorted(bpps)
    median_bpp = bpps_sorted[len(bpps_sorted)//2]
    is_top_people = all(players >= room_state[r]["players"] for r in ROOM_ORDER)
    crowd_trap = 1.0 if (is_top_people and bpp < median_bpp) else 0.0

    # recent kill spacing (2 ván gần nhất)
    last_kill_round = room_stats[rid]["last_kill_round"]
    recent_kill_penalty = 0.0
    if last_kill_round is not None and round_index - int(last_kill_round) <= 2:
        recent_kill_penalty = 1.0

    return {
        "player_share": player_share,
        "bet_share": bet_share,
        "smi": smi,
        "bpp": bpp,
        "stability": stability,
        "late_surge": late_surge,
        "crowd_trap": crowd_trap,
        "recent_kill_penalty": recent_kill_penalty
    }

def choose_room_pro() -> Tuple[int, str, float]:
    # trọng số khởi tạo (tinh chỉnh dần) - tăng độ phân biệt
    a1,a2,a3,a4,a5,a6,a7,a8 = 1.2,0.6,0.7,0.4,0.35,0.8,0.5,0.2

    scores = {}
    for r in ROOM_ORDER:
        f0 = _room_features(r)
        f1 = _room_extra_features(r)

        # chuẩn hóa bpp (càng cao càng tốt, clamp 0..1)
        bpp_norm = 1.0 - 1.0/(1.0 + f1["bpp"]/1200.0)
        # tránh lặp phòng vừa pick 2 ván liên tiếp
        recent_pick_penalty = 0.0
        recent = list(bet_history)[-2:]
        if any(b.get("room")==r for b in recent):
            recent_pick_penalty = 1.0

        score = 0.0
        score += a1 * f1["smi"]
        score += a2 * f1["bet_share"]
        score -= a3 * f1["player_share"]
        score += a4 * bpp_norm
        score += a5 * f1["stability"]
        score -= a6 * max(f1["late_surge"], f1["crowd_trap"])
        score -= a7 * f1["recent_kill_penalty"]
        score -= a8 * recent_pick_penalty

        # giữ lại "survive_score" từ stats dài hạn
        score += 0.15 * f0["survive_score"]
        
        # thêm noise nhỏ để tăng độ phân biệt
        import random
        noise = random.uniform(-0.05, 0.05)
        score += noise

        scores[r] = score

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    (r1,s1), (r2,s2) = ranked[0], ranked[1]
    conf = (s1 - s2) / (abs(s1)+abs(s2)+1e-6)
    return r1, "PRO(SMI+Trend)", max(0.0, conf)

def choose_room_meta() -> Tuple[Optional[int], str, float]:
    """
    META Algorithm - Enhanced Voting System v2:
    - Kết hợp VIP, PRO và phân tích rủi ro bổ sung
    - Áp dụng nhiều lớp lọc để tăng tỷ lệ thắng
    """
    vip_room, vip_algo = choose_room_VIP()
    pro_room, pro_algo, pro_conf = choose_room_pro()
    
    # Tạo điểm số cho tất cả các phòng
    room_scores = {r: 0.0 for r in ROOM_ORDER}
    
    # Layer 1: VIP vote (trọng số 40%)
    room_scores[vip_room] += 0.4
    
    # Layer 2: PRO vote (trọng số 40%)
    pro_weight = 0.4 * max(0.3, float(pro_conf or 0.5))
    room_scores[pro_room] += pro_weight
    
    # Layer 3: Risk Analysis (trọng số 20%)
    for r in ROOM_ORDER:
        risk_score = _calculate_room_risk(r)
        room_scores[r] += 0.2 * (1.0 - risk_score)  # điểm cao khi rủi ro thấp
    
    # Tìm phòng có điểm cao nhất
    sorted_rooms = sorted(room_scores.items(), key=lambda x: -x[1])
    chosen_room, total_score = sorted_rooms[0]
    second_score = sorted_rooms[1][1] if len(sorted_rooms) > 1 else 0
    
    # Tính confidence dựa trên độ phân biệt
    score_gap = total_score - second_score
    base_conf = min(0.95, total_score * 0.8)
    gap_bonus = min(0.15, score_gap * 2.0)
    
    if vip_room == pro_room:
        # Đồng thuận: bonus confidence
        consensus_bonus = 0.1 + 0.1 * float(pro_conf or 0.5)
        meta_conf = base_conf + gap_bonus + consensus_bonus
        algo_desc = f"META-CONSENSUS({vip_algo}+{pro_algo})"
    else:
        # Bất đồng: phụ thuộc vào risk analysis
        meta_conf = base_conf + gap_bonus
        algo_desc = f"META-ENHANCED({vip_algo}={vip_room},PRO={pro_room})"
    
    # Áp dụng penalty cho các trường hợp rủi ro cao
    chosen_risk = _calculate_room_risk(chosen_room)
    if chosen_risk > 0.7:  # rủi ro quá cao
        meta_conf *= 0.6  # giảm confidence 40%
        algo_desc += "-HIGH_RISK"
    elif chosen_risk > 0.5:  # rủi ro trung bình
        meta_conf *= 0.8  # giảm confidence 20%
        algo_desc += "-MED_RISK"
    
    # Skip nếu confidence quá thấp
    min_threshold = 0.35  # tăng ngưỡng từ 0.25 lên 0.35
    if meta_conf < min_threshold:
        return None, f"META-LOW-CONF({algo_desc},conf={meta_conf:.3f})", meta_conf
    
    return chosen_room, algo_desc, max(0.0, min(1.0, meta_conf))

def _calculate_room_risk(room_id: int) -> float:
    """
    Tính toán rủi ro của một phòng (0.0 = an toàn, 1.0 = rủi ro cao)
    """
    try:
        st = room_state.get(room_id, {})
        stats = room_stats.get(room_id, {})
        
        # Factor 1: Tỷ lệ bị giết gần đây
        kills = float(stats.get("kills", 0))
        survives = float(stats.get("survives", 0))
        total_games = kills + survives
        kill_rate = kills / max(total_games, 1)
        
        # Factor 2: Phòng vừa bị giết gần đây
        last_kill_penalty = 0.0
        if last_killed_room == room_id:
            last_kill_penalty = 0.4  # penalty cao cho phòng vừa bị giết
        
        # Factor 3: Số người quá ít hoặc quá nhiều
        players = float(st.get("players", 0))
        player_risk = 0.0
        if players < 5:  # quá ít người
            player_risk = 0.3
        elif players > 50:  # quá nhiều người
            player_risk = 0.2
        
        # Factor 4: Tỷ lệ cược/người bất thường
        bet = float(st.get("bet", 0))
        bet_per_player = bet / max(players, 1)
        bpp_risk = 0.0
        if bet_per_player > 2000:  # cược quá cao/người
            bpp_risk = 0.2
        elif bet_per_player < 50:  # cược quá thấp/người
            bpp_risk = 0.15
        
        # Factor 5: Lịch sử đặt cược gần đây
        recent_bet_penalty = 0.0
        recent_bets = list(bet_history)[-3:]
        for bet_rec in recent_bets:
            if bet_rec.get("room") == room_id and bet_rec.get("result") == "Thua":
                recent_bet_penalty += 0.1
        
        # Tổng hợp rủi ro
        total_risk = min(1.0, kill_rate + last_kill_penalty + player_risk + bpp_risk + recent_bet_penalty)
        return total_risk
        
    except Exception:
        return 0.5  # rủi ro trung bình nếu có lỗi

# -------------------- BETTING HELPERS --------------------

def api_headers() -> Dict[str, str]:
    return {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "user-id": str(USER_ID) if USER_ID else "",
        "user-secret-key": SECRET_KEY if SECRET_KEY else ""
    }


def place_bet_http(issue: int, room_id: int, amount: float) -> dict:
    """Đặt cược theo chế độ DEMO hoặc REAL"""
    global betting_mode
    
    if betting_mode == "DEMO":
        # DEMO MODE: Giả lập đặt cược thành công mà không gọi API thật
        import time
        import random
        
        # Giả lập delay API
        time.sleep(random.uniform(0.1, 0.3))
        
        # Luôn trả về kết quả thành công trong demo mode
        return {
            "msg": "ok",
            "code": 0,
            "status": "success",
            "demo": True,
            "data": {
                "issue": issue,
                "room_id": room_id,
                "amount": amount,
                "timestamp": time.time()
            }
        }
    else:
        # REAL MODE: Đặt cược thật qua API
        payload = {"asset_type": "BUILD", "user_id": USER_ID, "room_id": int(room_id), "bet_amount": float(amount)}
        try:
            r = HTTP.post(BET_API_URL, headers=api_headers(), json=payload, timeout=6)
            try:
                return r.json()
            except Exception:
                return {"raw": r.text, "http_status": r.status_code}
        except Exception as e:
            return {"error": str(e)}


def record_bet(issue: int, room_id: int, amount: float, resp: dict, algo_used: Optional[str] = None) -> dict:
    now = datetime.now(tz).strftime("%H:%M:%S")
    rec = {"issue": issue, "room": room_id, "amount": float(amount), "time": now, "resp": resp, "result": "Đang", "algo": algo_used, "delta": 0.0, "win_streak": win_streak, "lose_streak": lose_streak}
    bet_history.append(rec)
    return rec


def place_bet_async(issue: int, room_id: int, amount: float, algo_used: Optional[str] = None):
    def worker():
        room_text = room_label(room_id)
        mode_icon = "🎮" if betting_mode == "💰" else "💰"
        console.print(f"[cyan]{mode_icon} {betting_mode} - Đang đặt {amount} BUILD -> {room_text} (v{issue}) — Thuật toán: {algo_used}[/]")
        time.sleep(random.uniform(0.02, 0.25))
        res = place_bet_http(issue, room_id, amount)
        rec = record_bet(issue, room_id, amount, res, algo_used=algo_used)
        if isinstance(res, dict) and (res.get("msg") == "ok" or res.get("code") == 0 or res.get("status") in ("ok", 1)):
            bet_sent_for_issue.add(issue)
            mode_icon = "🎮" if betting_mode == "💰" else "💰"
            console.print(f"[green]✅ {betting_mode} - Đặt thành công {amount} BUILD vào {room_text} (v{issue}).[/]")
            mode_icon = "🎮" if betting_mode == "💰" else "💰"
            tg_send(f"{mode_icon} - Đặt {float(amount):.4f} BUILD → {room_text} (v{issue})", silent=True)
        else:
            mode_icon = "🎮" if betting_mode == "💰" else "💰"
            console.print(f"[red]❌ {betting_mode} - Đặt lỗi v{issue}: {res}[/]")
    threading.Thread(target=worker, daemon=True).start()

# -------------------- LOCK & AUTO-BET --------------------

def lock_prediction_if_needed(force: bool = False):
    global prediction_locked, predicted_room, ui_state, current_bet, _rounds_placed_since_skip, skip_next_round_flag, _skip_rounds_remaining, _skip_active_issue
    if stop_flag:
        return
    if prediction_locked and not force:
        return
    if issue_id is None:
        return
    
    # --- ĐANG NGHỈ SAU KHI THUA ---
    if _skip_rounds_remaining > 0:
        # chỉ trừ 1 lần khi sang ván mới
        if _skip_active_issue != issue_id:
            console.print(f"[yellow]⏸️ Đang nghỉ {_skip_rounds_remaining} ván theo cấu hình sau khi thua.[/]")
            _skip_rounds_remaining -= 1         # tiêu thụ 1 ván nghỉ
            _skip_active_issue = issue_id       # nhớ là ván này đã nghỉ

        # khóa đến hết ván hiện tại để không bị các tick countdown đặt lại
        prediction_locked = True
        ui_state = "ANALYZING"                  # hoặc "PREDICTED" tuỳ UI
        return
    
    # Chọn phòng chỉ khi KHÔNG skip
    algo_sel = settings.get("algo")

    if algo_sel == "META":
        chosen, algo_used, conf = choose_room_meta()
        if chosen is None:
            # Confidence quá thấp → SKIP ván
            console.print(f"[yellow]⏸️ META: Confidence quá thấp → SKIP ván này. ({algo_used})[/]")
            tg_send(f"🧠 SKIP ván này vì không đủ tin tưởng v#{issue_id or '?'}", silent=True)
            prediction_locked = True
            ui_state = "ANALYZING"
            return
    elif algo_sel == "PRO":
        chosen, algo_used, conf = choose_room_pro()
    else:
        chosen, algo_used = choose_room_VIP()
        conf = 0.12  # conf giả lập cho VIP
    
    # --- NGƯỠNG CONFIDENCE để SKIP bẻ chuỗi thua ---
    # Điều chỉnh ngưỡng theo thuật toán
    if algo_sel == "META":
        min_conf = 0.40  # META Enhanced cần confidence cao hơn để đảm bảo chất lượng
        if lose_streak == 2:
            min_conf = 0.50  # nghiêm ngặt hơn khi thua 2 ván
        elif lose_streak >= 3:
            min_conf = 0.60  # rất nghiêm ngặt khi thua 3+ ván
    else:
        min_conf = 0.02  # VIP/PRO giữ ngưỡng thấp
        if lose_streak == 2:
            min_conf = 0.05
        elif lose_streak >= 3:
            min_conf = 0.07
    if conf < min_conf:
        console.print(f"[yellow]⏸️ BỎ QUA ván này (Mức độ tin cậy={conf:.3f} < {min_conf:.2f}).[/]")
        tg_send(
            f"🎮 ⏸️ SKIP ván #{issue_id or '?'}\n"
            f"Mức độ tin cậy: {conf:.3f} < {min_conf:.2f}\n"
            f"Chuỗi thua: {lose_streak}\n",
            silent=True
        )
        prediction_locked = True
        ui_state = "ANALYZING"
        return
    
    # --- STREAK PROTECTION: Tránh chuỗi thua dài ---
    if lose_streak >= 2 and algo_sel == "META":
        # Kiểm tra xem phòng được chọn có an toàn không
        chosen_risk = _calculate_room_risk(chosen)
        if chosen_risk > 0.3:  # rủi ro > 30%
            console.print(f"[yellow]⏸️ STREAK PROTECTION: Phòng {chosen} có rủi ro cao ({chosen_risk:.3f}) khi đang thua {lose_streak} ván liên tiếp.[/]")
            tg_send(f"🛡️ STREAK PROTECTION v#{issue_id or '?'}: Risk={chosen_risk:.3f}, Streak={lose_streak}", silent=True)
            prediction_locked = True
            ui_state = "ANALYZING"
            return
    
    predicted_room = chosen
    prediction_locked = True
    ui_state = "PREDICTED"
    
    # place bet if AUTO
    if run_mode == "AUTO" and not skip_next_round_flag:
        # get balance quickly (non-blocking - allow poller to update if needed)
        bld, _, _ = fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
        if bld is None:
            console.print("[yellow]⚠️ Không lấy được số dư trước khi đặt — bỏ qua đặt ván này.[/]")
            prediction_locked = False
            return
        global current_bet
        
        # Debug: Kiểm tra current_bet trước khi đặt cược
        console.print(f"[blue]🔍 DEBUG: Trước khi đặt cược - current_bet={current_bet}, base_bet={base_bet}, multiplier={multiplier}[/blue]")
        if current_bet is None:
            current_bet = base_bet
            console.print(f"[yellow]⚠️ current_bet is None, reset to base_bet: {current_bet}[/yellow]")
        else:
            console.print(f"[green]✅ current_bet không None: {current_bet}[/green]")
        amt = float(current_bet)
        
        # META đồng thuận → tăng size theo độ tin cậy (random 1-6%)
        if str(algo_used).startswith("META") and conf is not None:
            meta_boost_rate = get_meta_boost()  # random 0.01-0.06
            boost = 1.0 + meta_boost_rate * float(conf)   # ví dụ conf=0.8, boost=0.03 → +2.4%
            amt *= boost
            # chặn trên bởi cấu hình nếu có
            amt = min(amt, SELECTION_CONFIG.get("max_bet_allowed", float("inf")))
            # làm đẹp số thập phân
            amt = float(f"{amt:.4f}")
            console.print(f"[magenta]🧠 META BOOST: {conf:.3f} confidence → +{meta_boost_rate*100:.1f}% = {amt:.4f} BUILD[/magenta]")
        
        console.print(f"[cyan]💰 Đặt cược: {amt} BUILD (base={current_bet}, multiplier={multiplier})[/cyan]")
        if amt <= 0:
            console.print("[yellow]⚠️ Số tiền đặt không hợp lệ (<=0). Bỏ qua.[/]")
            prediction_locked = False
            return
            
        # Thông báo rõ ràng khi META đồng thuận
        
            
        place_bet_async(issue_id, predicted_room, amt, algo_used=algo_used)
        _rounds_placed_since_skip += 1
        if bet_rounds_before_skip > 0 and _rounds_placed_since_skip >= bet_rounds_before_skip:
            skip_next_round_flag = True
            _rounds_placed_since_skip = 0
    elif skip_next_round_flag:
        console.print("[yellow]⏸️ TẠM DỪNG THEO DÕI SÁT THỦ[/]")
        skip_next_round_flag = False

# -------------------- WEBSOCKET HANDLERS --------------------

def safe_send_enter_game(ws):
    if not ws:
        log_debug("safe_send_enter_game: ws None")
        return
    try:
        payload = {"msg_type": "handle_enter_game", "asset_type": "BUILD", "user_id": USER_ID, "user_secret_key": SECRET_KEY}
        ws.send(json.dumps(payload))
        log_debug("Sent enter_game")
    except Exception as e:
        log_debug(f"safe_send_enter_game err: {e}")


def _extract_issue_id(d: Dict[str, Any]) -> Optional[int]:
    if not isinstance(d, dict):
        return None
    possible = []
    for key in ("issue_id", "issueId", "issue", "id"):
        v = d.get(key)
        if v is not None:
            possible.append(v)
    if isinstance(d.get("data"), dict):
        for key in ("issue_id", "issueId", "issue", "id"):
            v = d["data"].get(key)
            if v is not None:
                possible.append(v)
    for p in possible:
        try:
            return int(p)
        except Exception:
            try:
                return int(str(p))
            except Exception:
                continue
    return None


def on_open(ws):
    _ws["ws"] = ws
    console.print("[green]ĐANG TRUY CẬP DỮ LIỆU GAME[/]")
    safe_send_enter_game(ws)


def _background_fetch_balance_after_result():
    # fetch in background to update cumulative etc
    try:
        fetch_balances_3games()
    except Exception:
        pass


def _mark_bet_result_from_issue(res_issue: Optional[int], krid: int):
    """
    Update kết quả CHỈ KHI có đặt cược ở issue đó.
    Tránh reset current_bet sai khi skip round.
    """
    global current_bet, win_streak, lose_streak, max_win_streak, max_lose_streak
    global _skip_rounds_remaining, stop_flag, _skip_active_issue

    if res_issue is None:
        return

    # ✅ Quan trọng: chỉ xử lý nếu THỰC SỰ đã đặt cược ở issue này
    if res_issue not in bet_sent_for_issue:
        # Không có cược cho ván này (ví dụ đang nghỉ) -> bỏ qua hoàn toàn
        log_debug(f"_mark_bet_result_from_issue: skip issue {res_issue} (no bet placed)")
        return

    # Tìm đúng bản ghi của issue này (KHÔNG fallback)
    rec = next((b for b in reversed(bet_history) if b.get("issue") == res_issue), None)
    if rec is None:
        log_debug(f"_mark_bet_result_from_issue: no record found for issue {res_issue}, skip")
        return

    # Tránh xử lý lặp
    if rec.get("settled"):
        log_debug(f"_mark_bet_result_from_issue: issue {res_issue} already settled, skip")
        return

    try:
        placed_room = int(rec.get("room"))
        # Nếu phòng bị kill khác phòng đã đặt => THẮNG
        if placed_room != int(krid):
            rec["result"] = "Thắng"
            rec["settled"] = True
            current_bet = base_bet              # reset martingale về base
            win_streak += 1
            lose_streak = 0
            if win_streak > max_win_streak:
                max_win_streak = win_streak
            # --- TELEGRAM: THẮNG ---
            try:
                amt = float(rec.get("amount") or 0)
            except Exception:
                amt = 0.0
            tg_send(
                f"🎮  ✅ THẮNG v{res_issue}\n"
                f"Đặt: {amt:.4f} BUILD → PHÒNG_{placed_room}\n"
                f"Sát thủ vào: {ROOM_NAMES.get(krid, krid)}\n"
                f"Chuỗi thắng: {win_streak}"
               
            )
        else:
            # THUA -> nhân tiền cho ván kế tiếp
            rec["result"] = "Thua"
            rec["settled"] = True
            try:
                old_bet = current_bet
                current_bet = float(rec.get("amount")) * float(multiplier)
                console.print(f"[red]🔴 THUA! Số cũ: {rec.get('amount')} × {multiplier} = {current_bet} BUILD[/red]")
                console.print(f"[red]🔴 DEBUG: current_bet đã được cập nhật từ {old_bet} thành {current_bet}[/red]")
            except Exception as e:
                current_bet = base_bet
                console.print(f"[red]🔴 THUA! Lỗi tính toán: {e}, reset về: {current_bet} BUILD[/red]")
            lose_streak += 1
            win_streak = 0
            if lose_streak > max_lose_streak:
                max_lose_streak = lose_streak
            if pause_after_losses > 0:
                _skip_rounds_remaining = pause_after_losses
                _skip_active_issue = None        # để ván kế tiếp mới trừ 1 lần
            # --- TELEGRAM: THUA ---
            try:
                amt = float(rec.get("amount") or 0)
            except Exception:
                amt = 0.0
            tg_send(
                f"🎮 🔴 THUA v{res_issue}\n"
                f"Đặt: {amt:.4f} BUILD → PHÒNG_{placed_room}\n"
                f"Sát thủ vào: {ROOM_NAMES.get(krid, krid)}\n"
                f"Cược kế tiếp: {float(current_bet or 0):.4f} (×{multiplier})\n"
                f"Chuỗi thua: {lose_streak}"
            )
    except Exception as e:
        log_debug(f"_mark_bet_result_from_issue err: {e}")
    finally:
        # dọn whitelist cho issue đã xử lý xong (optional)
        try:
            bet_sent_for_issue.discard(res_issue)
        except Exception:
            pass


def on_message(ws, message):
    global issue_id, count_down, killed_room, round_index, ui_state, analysis_start_ts, issue_start_ts
    global prediction_locked, predicted_room, last_killed_room, last_msg_ts, current_bet
    global win_streak, lose_streak, max_win_streak, max_lose_streak, cumulative_profit, _skip_rounds_remaining, stop_flag, analysis_blur
    last_msg_ts = time.time()
    try:
        if isinstance(message, bytes):
            try:
                message = message.decode("utf-8", errors="replace")
            except Exception:
                message = str(message)
        data = None
        try:
            data = json.loads(message)
        except Exception:
            try:
                data = json.loads(message.replace("'", '"'))
            except Exception:
                log_debug(f"on_message non-json: {str(message)[:200]}")
                return

        # sometimes payload wraps JSON string in data field
        if isinstance(data, dict) and isinstance(data.get("data"), str):
            try:
                inner = json.loads(data.get("data"))
                merged = dict(data)
                merged.update(inner)
                data = merged
            except Exception:
                pass

        msg_type = data.get("msg_type") or data.get("type") or ""
        msg_type = str(msg_type)
        new_issue = _extract_issue_id(data)

        # issue stat / rooms update
        if msg_type == "notify_issue_stat" or "issue_stat" in msg_type:
            rooms = data.get("rooms") or []
            if not rooms and isinstance(data.get("data"), dict):
                rooms = data["data"].get("rooms", [])
            for rm in (rooms or []):
                try:
                    rid = int(rm.get("room_id") or rm.get("roomId") or rm.get("id"))
                except Exception:
                    continue
                players = int(rm.get("user_cnt") or rm.get("userCount") or 0) or 0
                bet = int(rm.get("total_bet_amount") or rm.get("totalBet") or rm.get("bet") or 0) or 0
                room_state[rid] = {"players": players, "bet": bet}
                room_stats[rid]["last_players"] = players
                room_stats[rid]["last_bet"] = bet
                # sau khi set room_state[rid] = {"players": ..., "bet": ...}
                ts = time.time()
                room_hist[rid].append({
                    "ts": ts,
                    "players": players,
                    "bet": bet
                })
            if new_issue is not None and new_issue != issue_id:
                # New issue arrived -> prepare
                log_debug(f"New issue: {issue_id} -> {new_issue}")
                issue_id = new_issue
                issue_start_ts = time.time()
                round_index += 1
                killed_room = None
                prediction_locked = False
                predicted_room = None
                ui_state = "ANALYZING"
                analysis_start_ts = time.time()
                # NOTE: Do NOT lock prediction immediately here so ANALYZING UI shows.

        # countdown
        elif msg_type == "notify_count_down" or "count_down" in msg_type:
            count_down = data.get("count_down") or data.get("countDown") or data.get("count") or count_down
            try:
                count_val = int(count_down)
            except Exception:
                count_val = None
            # enter analysis blur window when <=45s; place bet when <=10s
            if count_val is not None:
                try:
                    # when <=10s, lock and place (if not already locked)
                    if count_val <= 8 and not prediction_locked:
                        # stop blur animation right before placing
                        analysis_blur = False
                        lock_prediction_if_needed()
                    elif count_val <= 45:
                        # start blur-analysis (45s -> 10s)
                        ui_state = "ANALYZING"
                        analysis_start_ts = time.time()
                        analysis_blur = True
                except Exception:
                    pass

        # result
        elif msg_type == "notify_result" or "result" in msg_type:
            # get killed room
            kr = data.get("killed_room") if data.get("killed_room") is not None else data.get("killed_room_id")
            if kr is None and isinstance(data.get("data"), dict):
                kr = data["data"].get("killed_room") or data["data"].get("killed_room_id")
            if kr is not None:
                try:
                    krid = int(kr)
                except Exception:
                    krid = kr
                killed_room = krid
                last_killed_room = krid
                for rid in ROOM_ORDER:
                    if rid == krid:
                        room_stats[rid]["kills"] += 1
                        room_stats[rid]["last_kill_round"] = round_index
                    else:
                        room_stats[rid]["survives"] += 1

                # Immediately mark bet result locally (fast) without waiting for balance
                res_issue = new_issue if new_issue is not None else issue_id
                _mark_bet_result_from_issue(res_issue, krid)
                # Fire background balance refresh to compute actual deltas & cumulative profit
                threading.Thread(target=_background_fetch_balance_after_result, daemon=True).start()

            ui_state = "RESULT"

            # check profit target or stop-loss after we fetched balances (balance fetch may set current_build)
            def _check_stop_conditions():
                global stop_flag
                try:
                    if stop_when_profit_reached and profit_target is not None and isinstance(current_build, (int, float)) and current_build >= profit_target:
                        console.print(f"[bold green]🎉 MỤC TIÊU LÃI ĐẠT: {current_build} >= {profit_target}. Dừng tool.[/]")
                        stop_flag = True
                        try:
                            wsobj = _ws.get("ws")
                            if wsobj:
                                wsobj.close()
                        except Exception:
                            pass
                    if stop_when_loss_reached and stop_loss_target is not None and isinstance(current_build, (int, float)) and current_build <= stop_loss_target:
                        console.print(f"[bold red]⚠️ STOP-LOSS TRIGGED: {current_build} <= {stop_loss_target}. Dừng tool.[/]")
                        stop_flag = True
                        try:
                            wsobj = _ws.get("ws")
                            if wsobj:
                                wsobj.close()
                        except Exception:
                            pass
                except Exception:
                    pass
            # run check slightly delayed to allow balance refresh thread update
            threading.Timer(1.2, _check_stop_conditions).start()

    except Exception as e:
        log_debug(f"on_message err: {e}")


def on_close(ws, code, reason):
    log_debug(f"WS closed: {code} {reason}")


def on_error(ws, err):
    log_debug(f"WS error: {err}")


def start_ws():
    backoff = 0.6
    while not stop_flag:
        try:
            ws_app = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
            _ws["ws"] = ws_app
            ws_app.run_forever(ping_interval=12, ping_timeout=6)
        except Exception as e:
            log_debug(f"start_ws exception: {e}")
        t = min(backoff + random.random() * 0.5, 30)
        log_debug(f"Reconnect WS after {t}s")
        time.sleep(t)
        backoff = min(backoff * 1.5, 30)

# -------------------- BALANCE POLLER THREAD --------------------

class BalancePoller(threading.Thread):
    def __init__(self, uid: Optional[int], secret: Optional[str], poll_seconds: int = 2, on_balance=None, on_error=None, on_status=None):
        super().__init__(daemon=True)
        self.uid = uid
        self.secret = secret
        self.poll_seconds = max(1, int(poll_seconds))
        self._running = True
        self._last_balance_local: Optional[float] = None
        self.on_balance = on_balance
        self.on_error = on_error
        self.on_status = on_status

    def stop(self):
        self._running = False

    def run(self):
        if self.on_status:
            self.on_status("Kết nối...")
        while self._running and not stop_flag:
            try:
                build, world, usdt = fetch_balances_3games(params={"userId": str(self.uid)} if self.uid else None, uid=self.uid, secret=self.secret)
                if build is None:
                    raise RuntimeError("Không đọc được balance từ response")
                delta = 0.0 if self._last_balance_local is None else (build - self._last_balance_local)
                first_time = (self._last_balance_local is None)
                if first_time or abs(delta) > 0:
                    self._last_balance_local = build
                    if self.on_balance:
                        self.on_balance(float(build), float(delta), {"ts": human_ts()})
                    if self.on_status:
                        self.on_status("Đang theo dõi")
                else:
                    if self.on_status:
                        self.on_status("Đang theo dõi (không đổi)")
            except Exception as e:
                if self.on_error:
                    self.on_error(str(e))
                if self.on_status:
                    self.on_status("Lỗi kết nối (thử lại...)")
            for _ in range(max(1, int(self.poll_seconds * 5))):
                if not self._running or stop_flag:
                    break
                time.sleep(0.2)
        if self.on_status:
            self.on_status("Đã dừng")

# -------------------- MONITOR --------------------

def monitor_loop():
    global last_balance_fetch_ts, last_msg_ts, stop_flag
    while not stop_flag:
        now = time.time()
        
        # Kiểm tra key VIP hết hạn
        if 'VTH_KEY_EXPIRY' in globals():
            try:
                if datetime.now() >= VTH_KEY_EXPIRY:
                    console.print("[red bold]⚠️ KEY VIP ĐÃ HẾT HẠN! Dừng tool.[/]")
                    stop_flag = True
                    try:
                        wsobj = _ws.get("ws")
                        if wsobj:
                            wsobj.close()
                    except Exception:
                        pass
                    break
            except Exception:
                pass
        
        if now - last_balance_fetch_ts >= BALANCE_POLL_INTERVAL:
            last_balance_fetch_ts = now
            try:
                fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
            except Exception as e:
                log_debug(f"monitor fetch err: {e}")
        if now - last_msg_ts > 8:
            log_debug("No ws msg >8s, send enter_game")
            try:
                safe_send_enter_game(_ws.get("ws"))
            except Exception as e:
                log_debug(f"monitor send err: {e}")
        if now - last_msg_ts > 30:
            log_debug("No ws msg >30s, force reconnect")
            try:
                wsobj = _ws.get("ws")
                if wsobj:
                    try:
                        wsobj.close()
                    except Exception:
                        pass
            except Exception:
                pass
        # Removed analysis_duration-based auto-lock. Now locking is driven solely by countdown messages (<=10s).
        time.sleep(0.6)

# -------------------- UI (RICH) --------------------

def _spinner_char():
    return _spinner[int(time.time() * 4) % len(_spinner)]

def _rainbow_border_style() -> str:
    idx = int(time.time() * 2) % len(RAINBOW_COLORS)
    return RAINBOW_COLORS[idx]

def build_header(border_color: Optional[str] = None):
    tbl = Table.grid(expand=True)
    tbl.add_column(ratio=2)
    tbl.add_column(ratio=1)

    mode_icon = "🎮" if betting_mode == "💰" else "💰"
    left = Text(f"{mode_icon} {betting_mode} - VUA THOÁT HIỂM VIP BY LONG", style="bold cyan")

    b = f"{current_build:,.4f}" if isinstance(current_build, (int, float)) else (str(current_build) if current_build is not None else "-")
    u = f"{current_usdt:,.4f}" if isinstance(current_usdt, (int, float)) else (str(current_usdt) if current_usdt is not None else "-")
    x = f"{current_world:,.4f}" if isinstance(current_world, (int, float)) else (str(current_world) if current_world is not None else "-")

    pnl_val = cumulative_profit if cumulative_profit is not None else 0.0
    pnl_str = f"{pnl_val:+,.4f}"
    pnl_style = "green bold" if pnl_val > 0 else ("red bold" if pnl_val < 0 else "yellow")

    bal = Text.assemble((f"USDT: {u}", "bold"), ("   "), (f"XWORLD: {x}", "bold"), ("   "), (f"BUILD: {b}", "bold"))

    algo_label = SELECTION_MODES.get(settings.get('algo'), settings.get('algo'))

    right_lines = []
    right_lines.append(f"Thuật toán: {algo_label}")
    right_lines.append(f"Lãi/lỗ: [{pnl_style}] {pnl_str} [/{pnl_style}]")
    right_lines.append(f"Phiên: {issue_id or '-'}")
    right_lines.append(f"chuỗi: thắng={max_win_streak} / thua={max_lose_streak}")
    
    # Hiển thị đếm ngược key VIP
    if 'VTH_KEY_EXPIRY' in globals():
        try:
            from datetime import timedelta
            now_sys = datetime.now()
            if now_sys >= VTH_KEY_EXPIRY:
                right_lines.append("[red bold]⚠️ KEY HẾT HẠN[/]")
            else:
                remaining = VTH_KEY_EXPIRY - now_sys
                hrs, rem = divmod(int(remaining.total_seconds()), 3600)
                mins, secs = divmod(rem, 60)
                expiry_vn = (VTH_KEY_EXPIRY + timedelta(hours=7)).strftime('%d/%m %H:%M')
                right_lines.append(f"[cyan]KEY: {hrs:02d}:{mins:02d}:{secs:02d} → {expiry_vn}[/]")
        except Exception:
            pass
    
    if stop_when_profit_reached and profit_target is not None:
        right_lines.append(f"[green]TakeProfit@{profit_target}[/]")
    if stop_when_loss_reached and stop_loss_target is not None:
        right_lines.append(f"[red]StopLoss@{stop_loss_target}[/]")

    right = Text.from_markup("\n".join(right_lines))

    tbl.add_row(left, right)
    tbl.add_row(bal, Text(f"{datetime.now(tz).strftime('%H:%M:%S')}  •  {_spinner_char()}", style="dim"))
    panel = Panel(tbl, box=box.ROUNDED, padding=(0,1), border_style=(border_color or _rainbow_border_style()))
    return panel

def build_rooms_table(border_color: Optional[str] = None):
    t = Table(box=box.MINIMAL, expand=True)
    t.add_column("ID", justify="center", width=3)
    t.add_column("Phòng", width=16)
    t.add_column("Ng", justify="right")
    t.add_column("Cược", justify="right")
    t.add_column("TT", justify="center")
    for r in ROOM_ORDER:
        st = room_state.get(r, {})
        status = ""
        try:
            if killed_room is not None and int(r) == int(killed_room):
                status = "[red]☠ Kill[/]"
        except Exception:
            pass
        try:
            if predicted_room is not None and int(r) == int(predicted_room):
                status = (status + " [dim]|[/] [green]✓ Dự đoán[/]") if status else "[green]✓ Dự đoán[/]"
        except Exception:
            pass
        players = str(st.get("players", 0))
        bet_val = st.get('bet', 0) or 0
        bet_fmt = f"{int(bet_val):,}"
        t.add_row(str(r), ROOM_NAMES.get(r, f"Phòng {r}"), players, bet_fmt, status)
    return Panel(t, title="PHÒNG", border_style=(border_color or _rainbow_border_style()))

def build_mid(border_color: Optional[str] = None):
    global analysis_start_ts, analysis_blur
    # ANALYZING: show a blur / loading visual from 45s down to 10s
    if ui_state == "ANALYZING":
        lines = []
        lines.append(f"ĐANG PHÂN TÍCH PHÒNG AN TOÀN NHẤT  {_spinner_char()}")
        # show countdown if available (do not show explicit 'will place at Xs' note)
        if count_down is not None:
            try:
                cd = int(count_down)
                lines.append(f"Đếm ngược tới kết quả: {cd}s")
            except Exception:
                pass
        else:
            lines.append("Chưa nhận được dữ liệu đếm ngược...")

        # blur visual: animated blocks with varying fill to give a 'loading/blur' impression
        if analysis_blur:
            bar_len = 36
            blocks = []
            tbase = int(time.time() * 5)
            for i in range(bar_len):
                # pseudo-random flicker deterministic-ish by tbase + i
                val = (tbase + i) % 7
                ch = "█" if val in (0, 1, 2) else ("▓" if val in (3, 4) else "░")
                color = RAINBOW_COLORS[(i + tbase) % len(RAINBOW_COLORS)]
                blocks.append(f"[{color}]{ch}[/{color}]")
            lines.append("".join(blocks))
            lines.append("")
            lines.append("AI ĐANG TÍNH TOÁN 8S CUỐI VÀO BUID")
        else:
            # fallback compact progress bar (no percent text)
            bar_len = 24
            filled = int((time.time() * 2) % (bar_len + 1))
            bars = []
            for i in range(bar_len):
                if i < filled:
                    color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
                    bars.append(f"[{color}]█[/{color}]")
                else:
                    bars.append("·")
            lines.append("".join(bars))

        lines.append("")
        lines.append(f"Phòng sát thủ vào ván trước: {ROOM_NAMES.get(last_killed_room, '-')}")
        txt = "\n".join(lines)
        return Panel(Align.center(Text.from_markup(txt), vertical="middle"), title="PHÂN TÍCH", border_style=(border_color or _rainbow_border_style()))

    elif ui_state == "PREDICTED":
        name = ROOM_NAMES.get(predicted_room, f"Phòng {predicted_room}") if predicted_room else '-'
        last_bet_amt = current_bet if current_bet is not None else '-'
        lines = []
        lines.append(f"AI chọn: {name}  — [green]KẾT QUẢ DỰ ĐOÁN[/]")
        lines.append(f"Số đặt: {last_bet_amt} BUILD")
        lines.append(f"Phòng sát thủ vào ván trước: {ROOM_NAMES.get(last_killed_room, '-')}")
        lines.append(f"Chuỗi thắng: {win_streak}  |  Chuỗi thua: {lose_streak}")
        lines.append("")
        if count_down is not None:
            try:
                cd = int(count_down)
                lines.append(f"Đếm ngược tới kết quả: {cd}s")
            except Exception:
                pass
        lines.append("")
        lines.append(f"đang học hỏi dữ liệu {_spinner_char()}")
        txt = "\n".join(lines)
        return Panel(Align.center(Text.from_markup(txt)), title="DỰ ĐOÁN", border_style=(border_color or _rainbow_border_style()))

    elif ui_state == "RESULT":
        k = ROOM_NAMES.get(killed_room, "-") if killed_room else "-"
        last_success = next((str(b.get('amount')) for b in reversed(bet_history) if b.get('result') in ('Thắng', 'Win')), '-')
        lines = []
        lines.append(f"Sát thủ đã vào: {k}")
        lines.append(f"Lãi/lỗ: {cumulative_profit:+.4f} BUILD")
        lines.append(f"Đặt cược thành công (last): {last_success}")
        lines.append(f"Max Chuỗi: W={max_win_streak} / L={max_lose_streak}")
        txt = "\n".join(lines)
        # border color to reflect last result
        border = None
        last = None
        if bet_history:
            last = bet_history[-1].get('result')
        if last == 'Thắng':
            border = 'green'
        elif last == 'Thua':
            border = 'red'
        return Panel(Align.center(Text.from_markup(txt)), title="KẾT QUẢ", border_style=(border or (border_color or _rainbow_border_style())))
    else:
        lines = []
        lines.append("Chờ ván mới...")
        lines.append(f"Phòng sát thủ vào ván trước: {ROOM_NAMES.get(last_killed_room, '-')}")
        lines.append(f"AI chọn: {ROOM_NAMES.get(predicted_room, '-') if predicted_room else '-'}")
        lines.append(f"Lãi/lỗ: {cumulative_profit:+.4f} BUILD")
        txt = "\n".join(lines)
        return Panel(Align.center(Text.from_markup(txt)), title="TRẠNG THÁI", border_style=(border_color or _rainbow_border_style()))

def build_bet_table(border_color: Optional[str] = None):
    t = Table(title="Lịch sử cược (5 ván gần nhất)", box=box.SIMPLE, expand=True)
    t.add_column("Ván", no_wrap=True)
    t.add_column("Phòng", no_wrap=True)
    t.add_column("Tiền", justify="right", no_wrap=True)
    t.add_column("KQ", no_wrap=True)
    t.add_column("Thuật toán", no_wrap=True)
    last5 = list(bet_history)[-5:]
    for b in reversed(last5):
        amt = b.get('amount') or 0
        amt_fmt = f"{float(amt):,.4f}"
        res = str(b.get('result') or '-')
        algo = str(b.get('algo') or '-')
        # color rows: thắng green, thua red, pending yellow
        if res.lower().startswith('thắng') or res.lower().startswith('win'):
            res_text = Text(res, style="green")
            row_style = ""
        elif res.lower().startswith('thua') or res.lower().startswith('lose'):
            res_text = Text(res, style="red")
            row_style = ""
        else:
            res_text = Text(res, style="yellow")
            row_style = ""
        t.add_row(str(b.get('issue') or '-'), str(b.get('room') or '-'), amt_fmt, res_text, algo)
    return Panel(t, border_style=(border_color or _rainbow_border_style()))

# -------------------- SETTINGS & START --------------------

def prompt_settings():
    global base_bet, multiplier, run_mode, bet_rounds_before_skip, current_bet, pause_after_losses, profit_target, stop_when_profit_reached, stop_loss_target, stop_when_loss_reached, settings
    console.print(Rule("[bold cyan]CẤU HÌNH NHANH[/]"))
    base = safe_input("Số BUILD đặt mỗi ván: ", default="1")
    try:
        base_bet = float(base)
    except Exception:
        base_bet = 1.0
    m = safe_input("Nhập 1 số nhân sau khi thua (ổn định thì 2): ", default="2")
    try:
        multiplier = float(m)
    except Exception:
        multiplier = 2.0
    current_bet = base_bet
    # Thêm vào prompt_settings() sau dòng 1349 (sau current_bet = base_bet)
# Chọn chế độ cược
    console.print("\n[bold]Chọn chế độ cược:[/]")
    console.print("1) DEMO - Giả lập đặt cược (không mất tiền thật)")
    console.print("2) REAL - Đặt cược thật (mất tiền thật)")
    mode = safe_input("Chọn (1/2): ", default="1")
    global betting_mode
    betting_mode = "REAL" if str(mode).strip() == "2" else "DEMO"
    console.print(f"[bold green]Chế độ: {betting_mode}[/bold green]")
    # Algorithm selection (simple chooser for now)
    console.print("\n[bold]Chọn thuật toán:[/]")
    console.print("1) VIP công thức tính phòng an toàn nhất (AI + RANDOM + toán học)")
    console.print("2) PRO (SMI+Trend: anti-crowd + trend + stability)")
    console.print("3) META (VIP ∩ PRO: chỉ cược khi đồng thuận)")
    alg = safe_input("Chọn (1/2/3): ", default="3")
    settings["algo"] = {"1": "VIP", "2": "PRO", "3": "META"}.get(str(alg).strip(), "META")

    s = safe_input("Chống soi: sau bao nhiêu ván đặt thì nghỉ 1 ván: ", default="0")
    try:
        bet_rounds_before_skip = int(s)
    except Exception:
        bet_rounds_before_skip = 0
    # pause after losses
    pl = safe_input("Nếu thua thì nghỉ bao nhiêu tay trước khi cược lại (ví dụ 2): ", default="0")
    try:
        pause_after_losses = int(pl)
    except Exception:
        pause_after_losses = 0
    # profit target
    pt = safe_input("lãi bao nhiêu thì chốt( không dùng enter): ", default="")
    try:
        if pt and pt.strip() != "":
            profit_target = float(pt)
            stop_when_profit_reached = True
        else:
            profit_target = None
            stop_when_profit_reached = False
    except Exception:
        profit_target = None
        stop_when_profit_reached = False
    # stop-loss
    sl = safe_input("lỗ bao nhiêu thì chốt( không dùng enter): ", default="")
    try:
        if sl and sl.strip() != "":
            stop_loss_target = float(sl)
            stop_when_loss_reached = True
        else:
            stop_loss_target = None
            stop_when_loss_reached = False
    except Exception:
        stop_loss_target = None
        stop_when_loss_reached = False

    # Note: analysis duration selection removed. Tool now auto-places when countdown <= 10s.
    runm = safe_input("💯bạn đã sẵn sàng hãy nhấn enter để bắt đầu💯: ", default="AUTO")
    run_mode = str(runm).upper()

def start_threads():
    threading.Thread(target=start_ws, daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()

def parse_login():
    global USER_ID, SECRET_KEY
    console.print(Rule("[bold cyan]ĐĂNG NHẬP[/]"))
    link = safe_input("Dán link trò chơi (từ xworld.info) tại đây (ví dụ chứa userId & secretKey) > ", default=None)
    if not link:
        console.print("[red]Không nhập link. Thoát.[/]")
        sys.exit(1)
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        if 'userId' in params:
            USER_ID = int(params.get('userId')[0])
        SECRET_KEY = params.get('secretKey', [None])[0]
        console.print(f"[green]✅ Đã đọc: userId={USER_ID}[/]")
    except Exception as e:
        console.print("[red]Link không hợp lệ. Thoát.[/]")
        log_debug(f"parse_login err: {e}")
        sys.exit(1)

def main():
    # Kiểm tra key VIP trước khi chạy
    verify_vth_key()
    
    # Tải cấu hình Telegram từ setting.json hoặc yêu cầu nhập mới
    if not load_telegram_config():
        prompt_telegram_config()
    
    parse_login()
    console.print("[bold magenta]Loading...[/]")
    prompt_settings()
    console.print("[bold green]Bắt đầu kết nối dữ liệu...[/]")

    def on_balance_changed(bal, delta, info):
        console.print(f"[green]⤴️ cập nhật số dư: {bal:.4f} (Δ {delta:+.4f}) — {info.get('ts')}[/]")

    def on_error(msg):
        console.print(f"[red]Balance poll lỗi: {msg}[/]")

    poller = BalancePoller(USER_ID, SECRET_KEY, poll_seconds=max(1, int(BALANCE_POLL_INTERVAL)), on_balance=on_balance_changed, on_error=on_error, on_status=None)
    poller.start()
    start_threads()

    with Live(Group(build_header(), build_mid(), build_rooms_table(), build_bet_table()), refresh_per_second=8, console=console, screen=False) as live:
        try:
            while not stop_flag:
                live.update(Group(build_header(), build_mid(), build_rooms_table(), build_bet_table()))
                time.sleep(0.12)
            console.print("[bold yellow]Tool đã dừng theo yêu cầu hoặc đạt mục tiêu.[/]")
        except KeyboardInterrupt:
            console.print("[yellow]Thoát bằng người dùng.[/]")
            poller.stop()

if __name__ == "__main__":
    main()
