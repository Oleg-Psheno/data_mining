import re
import base64
with open('text.txt','r') as f:
    str = f.read()

out = re.findall(r'phone%22%2C%22([a-zA-Z|\d]+)%3D%3D%22', str)[0]
print(f'Строка длиной {len(str)} символов')

code = 'S3pjZ0tEa3lOU2tnTlRrM0xURTVMVFkwXw'

# sb = s.encode('ascii')
code2 = base64.b64decode(out + "========")
result = base64.b64decode(code2 + b"========").decode()
print(result)

# f = base64.b64decode(d)
# print(f)
