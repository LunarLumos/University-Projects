
```
============================================
🛡️ **Stellarisys** – Terminal-based Intrusion Detection Tool
============================================

$ cat /proc/stellarisys/meta
AUTHOR:    Aadil
COURSE:    Cyber Security Systems
SEMESTER:  Spring 2025
EMAIL:     aadil025@yahoo.com
GITHUB:    github.com/LunarLumos
VERSION:   v1.0
LICENSE:   MIT

$ ./stellarisys.pl --about
[ℹ] Stellarisys is a lightweight terminal-based IDS developed in Perl
[ℹ] Designed for educational use and log analysis
[ℹ] Features: Attack detection, Telegram alerts, Data structure implementation

$ ls -l --classify
stellarisys.pl*  # Main detection engine (executable)
making_log.sh*   # Log generator script (executable) 
test_logs.txt    # Sample attack logs
README.md        # This documentation

$ ./stellarisys.pl --tech
[🛠] TECHNOLOGIES:
- Perl 5+ (Core engine)
- LWP::UserAgent (Telegram API)
- Regular Expressions (Pattern matching)
- Terminal/CLI (Interface)

$ ./stellarisys.pl --features
[🔍] DETECTION CAPABILITIES:
[✓] SQLi      (union select, @@version)
[✓] XSS       (<script>, onerror=)
[✓] Path Traversal (../../../etc/passwd)
[✓] Command Injection (; rm -rf)
[✓] Brute Force (5+ login attempts)

[📡] OUTPUT FEATURES:
[✓] Color-coded terminal alerts
[✓] Telegram notifications
[✓] Data structure visualization

$ ./stellarisys.pl --structures
[🧠] DATA STRUCTURES IMPLEMENTED:
├─ LinkedList (Alert storage)
├─ Stack (Event tracking)
├─ Queue (Brute-force detection)
├─ Graph (IP relationships)
└─ BST (IP sorting)

$ cat install_guide
# PREREQUISITES
sudo apt-get install perl
sudo cpan install LWP::UserAgent

# SETUP
chmod +x stellarisys.pl making_log.sh
nano stellarisys.pl  # Edit BOT_TOKEN and CHAT_ID

# USAGE
./making_log.sh | ./stellarisys.pl  # Test with sample attacks
tail -f live.log | ./stellarisys.pl # Real-time monitoring

$ ./making_log.sh | head -3
192.168.1.100 - admin [01/Apr/2025:08:00:01] "GET /index.html HTTP/1.1" 200 512
10.0.2.15 - user [01/Apr/2025:08:00:02] "POST /login.php HTTP/1.1" 200 342 
172.16.0.55 - attacker [01/Apr/2025:08:00:04] "GET /products.php?id=1 union select..."

$ ./stellarisys.pl < test_logs.txt
[🟢] SAFE: 192.168.1.100 - GET /index.html
[🔴] ALERT: SQL_INJECTION from 172.16.0.55
[🟣] ALERT: XSS detected from 192.168.2.88
[🟡] ALERT: BRUTE_FORCE from 192.168.1.200 (5 attempts)
[📡] Telegram alert sent successfully

$ ./stellarisys.pl --config
[⚙] CURRENT CONFIG:
TELEGRAM:
  BOT_TOKEN = #Your Bot Token
  CHAT_ID = #Your chat ID
COLOR_SCHEME: Enabled
THRESHOLDS:
  BRUTE_FORCE = 5 attempts

============================================
[✔] SYSTEM READY | CTRL+C to exit
============================================
```
