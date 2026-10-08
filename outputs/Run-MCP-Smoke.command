#!/bin/zsh
# User-run local smoke test. No WPS network page, login, or submission.
set -u
task_root="${0:A:h:h}"
task_python="$task_root/work/mcp-validation/venv/bin/python"
task_repo="$task_root/work/wps-mcp-test"
task_log="$task_root/work/mcp-validation/manual-browser-smoke.log"

print 'WPS MCP 本地浏览器测试'
print '将打开本地合成表单，自动填入演示内容并回读，然后关闭浏览器。'
print '本次测试不访问医院表单。结果会保存到当前任务目录。'

if [[ ! -x "$task_python" || ! -f "$task_repo/server.py" ]]; then
  print '测试环境文件缺失，请回到聊天报告此提示。'
  read '?按回车关闭。'
  exit 1
fi

cd "$task_repo" || exit 1
export PLAYWRIGHT_BROWSERS_PATH="$task_root/work/mcp-validation/browsers"
unset WPS_MCP_BROWSER_PATH
"$task_python" server.py --smoke-test --headed > "$task_log" 2>&1
task_status=$?
cat "$task_log"
print ''
print "退出码：$task_status"
print "结果文件：$task_log"
print '运行完成后回到聊天发送“测试器运行完了”，我会读取结果继续。'
read '?按回车关闭窗口。'
exit "$task_status"
