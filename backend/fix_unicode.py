# Fix Unicode encoding issues in simple_backend.py
import sys
import io

# Ensure UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read the file
with open('simple_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements
replacements = [
    ('\u2705', '[OK]'),           # ✅
    ('\u274C', '[ERROR]'),        # ❌
    ('\u26A0\uFE0F', '[WARNING]'), # ⚠️
    ('\u26A0', '[WARNING]'),      # ⚠
    ('\U0001F680', '[INFO]'),     # 🚀
    ('\U0001F4B0', '[PRICE]'),    # 💰
    ('\U0001F4C8', '[UP]'),       # 📈
    ('\U0001F4C9', '[DOWN]'),     # 📉
    ('\U0001F50D', '[DEBUG]'),    # 🔍
    ('\U0001F504', '[REFRESH]'),  # 🔄
    ('\U0001F91D', ''),           # 🤝
    ('\U0001F6E1\uFE0F', ''),     # 🛡️
    ('\U0001F6E1', ''),           # 🛡
    ('\U0001F4A1', ''),           # 💡
    ('\U0001F393', ''),           # 🎓
    ('\U0001F4CA', ''),           # 📊
    ('\u23F0', ''),               # ⏰
    ('\U0001F3AF', ''),           # 🎯
    ('\U0001F527', ''),           # 🔧
    ('\u2753', ''),               # ❓
    ('\U0001F4DA', ''),           # 📚
    ('\U0001F52E', ''),           # 🔮
    ('\U0001F916', ''),           # 🤖
    ('\U0001F4AC', ''),           # 💬
    ('\u2022', '-'),              # •
    ('\u2B06\uFE0F', '[UP]'),     # ⬆️
    ('\u2B07\uFE0F', '[DOWN]'),   # ⬇️
]

# Apply replacements
for old, new in replacements:
    content = content.replace(old, new)

# Write back
with open('simple_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {len(replacements)} emoji types")
print("File updated successfully!")
