#!/bin/zsh
# User-started, bounded local tests plus real WPS synthetic draft validation. Never submits.
set -u
task_root="${0:A:h:h}"
task_python="$task_root/work/mcp-validation/venv/bin/python"
task_runner="$task_root/work/mcp-validation/live_test.py"
print 'WPS MCP 真实填表验证器（合成数据，不提交）'
print '先跑本地候选测试；通过后打开医院表单，您在独立浏览器手工登录并回到空表。'
print '只验证一次25题填写、两次重复调用及多选替换；不会自动恢复空表。'
print '完整合成payload与每步结果保存到 work/mcp-validation/live-results。'
if [[ ! -x "$task_python" || ! -f "$task_runner" ]]; then
  print '测试环境文件缺失，请回到聊天报告。'
  read '?按回车关闭。'
  exit 1
fi
cd "$task_root" || exit 1
export PLAYWRIGHT_BROWSERS_PATH="$task_root/work/mcp-validation/browsers"
unset WPS_MCP_BROWSER_PATH
"$task_python" "$task_runner"
task_status=$?
print ''
print "验证器退出码：$task_status"
print '测试后请勿提交合成草稿。回到聊天发送“验证器运行完了”，我会读取实际结果。'
read '?按回车关闭窗口。'
exit "$task_status"
