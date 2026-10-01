import os

# 必须在任何 src.* 导入前指定内存库
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
