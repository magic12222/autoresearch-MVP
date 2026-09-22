"""用于验证失败状态和错误捕获。"""

import sys

print("失败样例已启动")
print("预期的示例错误", file=sys.stderr)
raise RuntimeError("受控失败")
