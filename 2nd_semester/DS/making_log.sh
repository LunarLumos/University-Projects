#!/bin/bash

# Generate test logs
cat > test_logs.txt << 'EOF'
192.168.1.100 - admin [01/Apr/2025:08:00:01] "GET /index.html HTTP/1.1" 200 512
10.0.2.15 - user [01/Apr/2025:08:00:02] "POST /login.php HTTP/1.1" 200 342
172.16.0.55 - attacker [01/Apr/2025:08:00:04] "GET /products.php?id=1 union select 1,2,3 from users-- HTTP/1.1" 200 1024
192.168.2.88 - xsser [01/Apr/2025:08:00:05] "GET /search?q=<script>alert(1)</script> HTTP/1.1" 200 654
10.1.1.77 - hacker [01/Apr/2025:08:00:06] "GET /user.php?id=convert(int,@@version) HTTP/1.1" 200 768
192.168.1.200 - bruteforcer [01/Apr/2025:08:00:07] "POST /login.php?username=admin&password=guess1 HTTP/1.1" 401 111
192.168.1.200 - bruteforcer [01/Apr/2025:08:00:08] "POST /login.php?username=admin&password=guess2 HTTP/1.1" 401 111
192.168.1.200 - bruteforcer [01/Apr/2025:08:00:09] "POST /login.php?username=admin&password=guess3 HTTP/1.1" 401 111
192.168.1.200 - bruteforcer [01/Apr/2025:08:00:10] "POST /login.php?username=admin&password=guess4 HTTP/1.1" 401 111
192.168.1.200 - bruteforcer [01/Apr/2025:08:00:11] "POST /login.php?username=admin&password=guess5 HTTP/1.1" 401 111
10.0.0.222 - lfi_attacker [01/Apr/2025:08:00:12] "GET /../../../../etc/passwd HTTP/1.1" 403 222
172.16.0.244 - cmd_hacker [01/Apr/2025:08:00:13] "GET /ping.php?ip=127.0.0.1;cat+/etc/passwd HTTP/1.1" 200 444
10.0.2.16 - user2 [01/Apr/2025:08:00:14] "GET /about.html HTTP/1.1" 200 612
EOF

# Run IDS
echo -e "\nRunning IDS Detection...\n"
perl stellarisys.pl < test_logs.txt
