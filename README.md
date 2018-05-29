## Login dean.vatuu.com with selenium

**Usage**

```python3
from login_swjtu import Browser

browser = Browser('<chromedriver path>')
data = {
    'username': '<your student id>',
    'password': '<your password>'
}
res = browser.login(data)

"""
res = {
    'status': int,  # 1 or 0 (for sucess / fail),
    'JSESSIONID': str,  # JSESSIONID for dean,
    'reason': str  # reason when failed
}
"""
```