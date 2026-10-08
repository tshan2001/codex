import json
from pathlib import Path

base = Path(__file__).parent
out = base.parent.parent / 'outputs'
data = json.loads((base/'compiled-structure.json').read_text())
final = json.loads((base/'final-notes.json').read_text())
data.update(final)
byid = {q['id']: q for q in data['questions']}
lines = [
    data['title'] + ' — 动态结构探索报告',
    '观察日期：2026-10-08（America/Los_Angeles）',
    '来源：' + data['url'],
    '',
    '结果与边界',
    data['completion_verdict'],
    '已观察到18个初始题、15个条件题，共33个独立编号题；9个复合填空题共27个独立textarea；另有3处同题可选补充文本。',
    '三组不合理事项共28个复选选项，组本身均不标必填；另外30个编号题在出现时标必填。',
    'q01–q33以及带点后缀的ID由本报告自定义，不是WPS官方字段ID。WPS容器标识来自DOM观察，未验证为后端字段ID。',
    '页面数字题号会随展开分支改变，不能用显示题号作为稳定定位键。',
    '',
    '初始状态与操作边界',
    '在用户已登录Chrome中观察到0/18，全部答案为空；单选控件可操作。页面为单页滚动，底部有Submit，没有观察到Next。',
    '未输入处方号、医生、患者、金额、药名、点评原因等业务文本；未点击最终提交。选择题切换仅用于用户授权的结构探索。',
    data['persistence_and_final_state'],
    '',
    '完整题目清单',
]

names = {'textarea':'多行文本框','text':'文本input（界面可有数值提示）','radio':'单选','checkbox_group':'多选','searchable_combobox':'可搜索下拉框','datetime_picker':'日期时间选择器','multiple_inline_textareas':'一句提示内多个独立文本框'}
for q in data['questions']:
    visibility = q['visibility']
    condition = '初始常显' if visibility == 'initial' else f"{visibility['question']}「{byid[visibility['question']]['title']}」=「{visibility['equals']}」"
    lines.extend(['', f"{q['id']} | {q['title']}", f"  DOM容器：{q['observed_container_id']}；类型：{names[q['control_type']]}；必填：{'是（出现时）' if q['required'] else '否'}；出现条件：{condition}"])
    if q['description']:
        lines.append('  说明原文：' + q['description'])
    if q.get('options'):
        lines.append('  选项原文（按页面顺序）：')
        for option in q['options']:
            lines.append('    ' + option)
    if q.get('subfields'):
        lines.append('  子填空（按从左到右/DOM顺序；每个均为textarea）：')
        for field in q['subfields']:
            lines.append(f"    {field['id']} {field['label']}")
        lines.append('  必填标记属于整个题；各空单独的提交校验未测试。')
    if q['control_type'] == 'datetime_picker':
        lines.append('  实际弹层：年/月/日 + 小时00–23 + 分钟00–59 + OK。input为readonly；打开即自动带入当前时间，未按OK、收起后仍有值；最终通过clear恢复空值。')
    if q['id'] == 'q07':
        lines.append('  placeholder原文：Enter a number (decimals allowed)；实际HTML类型=text，未测试数值边界。')

lines.extend(['', '同题补充输入（不增加独立编号题）'])
for s in data['supplementary_controls']:
    lines.append(f"  {s['id']}：{s['parent_question']}选择「{s['when_option']}」时追加textarea；界面提示Optional。")
    if s.get('additional_visibility_condition'):
        lines.append('    ' + s['additional_visibility_condition'] + '。补充框在下拉菜单内。')
    else:
        lines.append('    由q16=是先展开q27，再由q27的否选项展开；选回是收起。')

lines.extend(['', '分支覆盖与返回切换'])
lines.extend('  '+x for x in data['coverage_summary'])
lines.extend(['', '全部交互观察索引（动作名可能记录意图，actual selections才是观察到的状态）'])
for s in data['coverage']:
    lines.append(f"  state {s['state_index']:02d} | {s['recorded_action']} | {s['visible_question_count']}个编号题")
lines.extend(['', 'MCP适配影响（不是当前MCP已通过验证的结论）'])
lines.extend('  '+x for x in data['adapter_implications'])
lines.extend(['', '表单原文中的需确认事项'])
lines.extend('  '+x for x in data['ui_text_caveats'])
lines.extend(['', '未检查或不能据本次探索断言的事项'])
lines.extend('  '+x for x in data['not_checked'])
lines.extend(['', '证据与协作方式', '根代理负责唯一Chrome交互；结构子代理读取实际DOM快照、比对字段/选项/覆盖集合并整理此报告。'])
for evidence in data.get('evidence_files',[]):
    lines.append('  '+evidence)
lines.append('机器可读详细记录见同目录wps-form-structure.json；原始逐状态DOM证据保存在本任务work/form-exploration/。')
lines.append('本报告只描述表单结构，不作任何处方临床合理性判断。')

out.mkdir(exist_ok=True)
(out/'wps-form-structure.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(out/'wps-form-structure.txt').write_text('\n'.join(lines)+'\n')
print(f"Saved {len(data['questions'])} questions, {len(lines)} report lines, {len(data['coverage'])} states")
