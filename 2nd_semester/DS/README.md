# 🛡️ Stellarisys – Intelligent Intrusion Detection System  
**Author**: Aadil  
**Instructor**: [Mr. Faruk Hosen](https://mdfarukhosenict.github.io/)  
**University**: Daffodil International University  
**Course**: Data Structures & Lab  
**Semester**: Spring 2025  
**Email**: aadil025@yahoo.com  
**GitHub**: [LunarLumos](https://github.com/LunarLumos)  
**Project**: Stellarisys – Perl-based IDS  

---

## 📦 Project Description  
Stellarisys is an advanced, terminal-based Intrusion Detection System (IDS) developed in Perl. The system analyzes system logs in real-time to detect security threats using pattern matching and implements core data structures for efficient processing.

### Key Features:
- **Multi-attack detection** (SQLi, XSS, brute force, etc.)
- **Real-time Telegram alerts** for immediate threat notifications
- **Data structure implementations** (BST, Graph, Linked List, etc.)
- **Color-coded terminal output** for visual threat classification
- **Log analysis** from both static files and live streams

This project demonstrates the application of algorithmic thinking to security problems, implementation of complex data structures in Perl, and the design of systems for real-world cybersecurity applications.

---

## 🌐 Live Execution  
```bash
# Run with sample logs
./making_log.sh | ./stellarisys.pl
```

---

## 📦 Prerequisites  
```bash
bash install.sh
```

---

## 📁 Project Structure  
```
├── stellarisys.pl        # Main detection engine (Perl)  
├── making_log.sh         # Test log generator  
├── test_logs.txt         # Sample attack logs  
├── install.sh            # Dependency installer  
├── README.md             # Project documentation  
```

---

## 🛠️ Technologies Used  
- **Perl 5+** (Core detection logic)  
- **LWP::UserAgent** (Telegram API integration)  
- **Regular Expressions** (Pattern matching)  
- **Data Structures**:  
  - **Binary Search Tree (BST)**: IP sorting  
  - **Graph**: IP relationship mapping  
  - **Queue**: Brute-force detection  
  - **Stack**: Event tracking  

---

## ✅ Detection Capabilities  
- **SQL Injection**: `union select`, `@@version`  
- **XSS**: `<script>`, `alert()`, `document.cookie`  
- **Path Traversal**: `../../../etc/passwd`  
- **Command Injection**: `; cat /etc/passwd`  
- **Brute Force**: 5+ failed login attempts  
- **Real-time Alerts**: Terminal and Telegram notifications  

---

## ⚙️ Configuration  
**Current Config:**
```bash
TELEGRAM:
  BOT_TOKEN = #Your Bot Token
  CHAT_ID = #Your Chat ID

COLOR_SCHEME: Enabled

THRESHOLDS:
  BRUTE_FORCE = 5 attempts
```

---

## 📝 Log Files Example  
```
192.168.1.100 - admin [01/Apr/2025:08:00:01] "GET /index.html HTTP/1.1" 200 512
10.0.2.15 - user [01/Apr/2025:08:00:02] "POST /login.php HTTP/1.1" 200 342
172.16.0.55 - attacker [01/Apr/2025:08:00:04] "GET /products.php?id=1 union select..."
```

---

## 📊 Output Example  
```
🟢 SAFE: 192.168.1.100 - GET /index.html  
🔴 ALERT: SQL_INJECTION from 172.16.0.55  
🟣 ALERT: XSS detected from 192.168.2.88  
🟡 ALERT: BRUTE_FORCE from 192.168.1.200 (5 attempts)  
📡 Telegram alert sent successfully  
```

---

## 🎯 Learning Outcomes  
- Implemented core data structures in a security context  
- Developed pattern-matching algorithms for threat detection  
- Created a modular system with separate detection components  
- Integrated external APIs (Telegram) for alerting  
- Optimized log processing for better performance  

---

## 📈 Future Enhancements  
- [ ] JSON configuration support  
- [ ] Enhanced attack pattern database  
- [ ] Machine learning integration for anomaly detection  
- [ ] Web dashboard for visualization  
- [ ] Docker containerization  

---

## 🧠 Conclusion  
Stellarisys represents my journey of combining data structures with cybersecurity applications. This project not only fulfilled academic requirements but also provided practical experience in building security tools. The system demonstrates how fundamental computer science concepts can be applied to solve real-world security challenges.
