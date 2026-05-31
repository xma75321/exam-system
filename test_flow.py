"""测试完整注册登录流程"""

import sys
sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from sqlalchemy import text

client = TestClient(app)

print("=" * 50)
print("测试完整注册登录流程")
print("=" * 50)

# 1. 清理测试数据
print("\n[1] 清理测试数据...")
with SessionLocal() as db:
    db.execute(text("DELETE FROM users WHERE username LIKE 'flowtest%'"))
    db.commit()

# 2. 测试注册
print("\n[2] 测试注册...")
r = client.post("/api/auth/register", json={
    "username": "flowtest1",
    "email": "flowtest1@example.com",
    "password": "Test123456"
})
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.json()}")

# 3. 检查数据库
print("\n[3] 检查数据库...")
with SessionLocal() as db:
    result = db.execute(text("SELECT id, username, email FROM users WHERE username = 'flowtest1'"))
    user = result.fetchone()
    if user:
        print(f"    用户已保存: ID={user[0]}, 用户名={user[1]}, 邮箱={user[2]}")
    else:
        print("    错误: 用户未保存到数据库!")

# 4. 测试登录
print("\n[4] 测试登录...")
r = client.post("/api/auth/login", json={
    "username": "flowtest1",
    "password": "Test123456"
})
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.json()}")

# 5. 测试重复注册
print("\n[5] 测试重复注册...")
r = client.post("/api/auth/register", json={
    "username": "flowtest1",
    "email": "flowtest1@example.com",
    "password": "Test123456"
})
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.json()}")

# 6. 测试错误密码登录
print("\n[6] 测试错误密码登录...")
r = client.post("/api/auth/login", json={
    "username": "flowtest1",
    "password": "WrongPassword"
})
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.json()}")

# 7. 测试不存在的用户登录
print("\n[7] 测试不存在的用户登录...")
r = client.post("/api/auth/login", json={
    "username": "nonexistent",
    "password": "Test123456"
})
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.json()}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
