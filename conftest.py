# conftest.py — pytest 公共配置
# DeepSeek API（OpenAI 兼容格式）
#
# 密钥来源优先级（统一读取环境变量 OPENAI_API_KEY）：
#   1. 系统环境变量（CI 中由 GitHub Secrets 注入，最优先）
#   2. 项目根目录下的 .env 文件（本地开发用，已被 .gitignore 排除，不会上传）
#
# 任何情况下都不要把真实 Key 硬编码写进代码。

import os

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not DEEPSEEK_API_KEY:
    raise RuntimeError(
        "未检测到 OPENAI_API_KEY。\n"
        "本地：复制 .env.example 为 .env 并填入 DeepSeek Key；\n"
        "CI：在 GitHub 仓库 Settings -> Secrets 中添加 OPENAI_API_KEY。"
    )

os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
