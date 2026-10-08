import json
import re
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE.parent.parent / 'outputs'
events = json.loads((BASE / 'dom-observations.json').read_text())
initial = json.loads((BASE / 'working-structure.json').read_text())
initial_questions = [q for q in initial['questions'] if q['id'].startswith('q') and '.' not in q['id']]
ids = [q['observed_container_id'] for q in initial_questions]
ids += ['ychig3', 'tizh0y', 't2ph2d', 'kmi976', 'nz89s9', 'tmzx5x', '7k22ws', 'ks3t1x', 'i5q0vu', 'e6birw', '8zu0b6', 'obqonq', 'ri2f8n', 'mz5lmb', 'rf5wk3']
record_ids = {dom: f'q{i:02d}' for i, dom in enumerate(ids, 1)}
first = {}
for event in events:
    for question in event['questions']:
        first.setdefault(question['id'], question)
unknown = set(first) - set(ids)
if unknown:
    raise ValueError(f'Unmapped new question IDs: {sorted(unknown)}')

dropdowns = {
    'xihnqc': '神经内科|心血管内科|呼吸与危重症医学科|消化内科|内分泌科|血液肿瘤科|肾内科|干部医疗科|儿科|康复医学科|普外科|骨外科|胸外科|心脏大血管外科|泌尿外科|妇产科|重症医学科|血管外科|肛肠科|医疗美容科|麻醉科|耳鼻喉头颈外科|眼科|口腔科|急诊科|感染科|中医科|皮肤科|综合门诊|神经外科|其他'.split('|'),
    '286ubz': '张敏|张娟|高丽君|杜宇|周金伟|关颖卓|崔思然|庞尚一|其他'.split('|'),
    '49wxul': ['1', '2', '3', '4', '5'],
}
parents = {
    'ychig3': ('5wm9h4', '是'), 'tizh0y': ('i3hu6i', '是'), 't2ph2d': ('8xl3ga', '是'),
    'kmi976': ('u1s7xw', '是'), 'nz89s9': ('n1t1ym', '是'), 'tmzx5x': ('ybqms9', '是'),
    '7k22ws': ('9fb0fe', '是'), 'ks3t1x': ('gw80sx', '是'), 'i5q0vu': ('i6mqlx', '是'),
    'e6birw': ('lsjcnl', '是'), '8zu0b6': ('nz3udo', '否'), 'obqonq': ('nz3udo', '否'),
    'ri2f8n': ('nz3udo', '否'), 'mz5lmb': ('nz3udo', '否'), 'rf5wk3': ('nz3udo', '否'),
}
composite_labels = {
    'ychig3': ['抗菌药物的品规数', '金额总数', '是否合理'],
    'tizh0y': ['抗肿瘤药物的品规数', '金额总数', '是否合理'],
    't2ph2d': ['激素药物的品规数', '金额总数', '是否合理'],
    'kmi976': ['注射剂的品规数', '金额总数', '是否合理'],
    'nz89s9': ['中成药的品规数', '金额总数', '是否合理'],
    'tmzx5x': ['中药注射剂的品规数', '金额总数', '是否合理'],
    '7k22ws': ['第二类精神的品规数', '金额总数', '是否合理'],
    'ks3t1x': ['国家基本药品的品规数', '金额总数'],
    'e6birw': ['长处方药品的品规数', '金额总数', '用药疗程', '是否合理'],
}

questions = []
for dom in ids:
    source = first[dom]
    controls = source['controls']
    types = {c['type'] for c in controls}
    raw = re.sub(r'^\d+\.', '', source['text'])
    q = {
        'id': record_ids[dom], 'observed_container_id': dom,
        'title': source['title'], 'description': source['note'], 'required': source['required'],
        'raw_observed_text': raw, 'visibility': 'initial',
        'evidence_state_indices': [i for i, e in enumerate(events) if any(z['id'] == dom for z in e['questions'])],
    }
    if dom in parents:
        parent, value = parents[dom]
        q['visibility'] = {'question': record_ids[parent], 'equals': value}
    if dom in dropdowns:
        q['control_type'] = 'searchable_combobox'
        q['options'] = dropdowns[dom]
    elif 'radio' in types:
        q['control_type'] = 'radio'
        if dom == 'i5q0vu':
            q['options'] = ['是', '否（请写明药品名称）']
        else:
            q['options'] = ['是', '否'] if dom == 'nz3udo' else ['否', '是']
    elif 'checkbox' in types:
        q['control_type'] = 'checkbox_group'
        q['options'] = [line for line in source['text'].split('\n') if re.match(r'^1-\d+ ', line)]
        q['observed_option_values'] = [c['value'] for c in controls if c['type'] == 'checkbox']
        assert len(q['options']) == len(q['observed_option_values']), dom
    elif dom in composite_labels:
        q['control_type'] = 'multiple_inline_textareas'
        q['subfields'] = [{'id':f"{q['id']}.{i}", 'label': label, 'control_type':'textarea', 'placeholder':'Please enter', 'required_individually_verified':False} for i, label in enumerate(composite_labels[dom],1)]
    elif dom == '9pekb6':
        q['control_type'] = 'datetime_picker'
        q['html_input_type'] = 'text'
        q['picker_components_observed'] = ['year','month','day','hour 00-23','minute 00-59','OK']
        q['observed_value_behavior'] = '打开日期时间弹层即带入当前时间；未按OK，收起后仍有值；结束时使用clear清空并回读value为空。'
        q['readonly_input'] = True
    else:
        q['control_type'] = 'textarea' if 'textarea' in types else 'text'
    base_controls = [c for c in controls if c['type'] != 'textarea'] if dom in dropdowns else controls
    q['base_dom_controls'] = [{k:v for k,v in c.items() if k not in ['checked','value']} for c in base_controls]
    questions.append(q)

supplementary = [
    {'id':'q02.other','parent_question':'q02','when_option':'其他'},
    {'id':'q04.other','parent_question':'q04','when_option':'其他'},
    {'id':'q27.no_drug_names','parent_question':'q27','when_option':'否（请写明药品名称）'},
]
for s in supplementary:
    s.update(control_type='textarea',placeholder='Please enter additional content(Optional)',required_by_visible_ui=False,counted_as_separate_question=False)
    if s['parent_question'] in ('q02','q04'):
        s.update(location='expanded_dropdown_menu',additional_visibility_condition='下拉菜单展开时可见；收起后隐藏，但过渡动画期间可能暂时仍有布局尺寸',observed_class='ksapc-select-write-other-config')

byid = {q['observed_container_id']:q for q in questions}
coverage = []
for i, event in enumerate(events):
    actual_choices = {}
    supplementary_visible = []
    for q in event['questions']:
        record = byid[q['id']]
        kind = record['control_type']
        if kind in ('radio','checkbox_group'):
            checked = [c.get('checked',False) for c in q['controls'] if c['type'] in ('radio','checkbox')]
            actual_choices[record['id']] = [value for value, selected in zip(record['options'], checked) if selected]
        if q['id'] in ('xihnqc','286ubz','i5q0vu') and any(c['type']=='textarea' for c in q['controls']):
            supplementary_visible.append(record['id'])
    coverage.append({'state_index':i,'recorded_action':event['action'],'visible_question_count':len(event['questions']),'visible_question_ids':[record_ids[q['id']] for q in event['questions']],'actual_radio_checkbox_selections':actual_choices,'parents_with_dom_supplementary_textarea':supplementary_visible,'supplementary_visibility_caveat':'本项只反映DOM中存在补充textarea；下拉菜单收起时控件可隐藏，不代表当前可见。'})

result = {k:v for k,v in initial.items() if k not in ('questions','conditions','coverage','remaining','observations')}
result['questions'] = questions
result['supplementary_controls'] = supplementary
result['conditions'] = [{'if':{'question':record_ids[parent],'equals':value},'shows':[record_ids[dom]]} for dom,(parent,value) in parents.items()]
result['coverage'] = coverage
result['summary'] = {'initial_questions':18,'unique_numbered_questions_observed':len(questions),'conditional_numbered_questions_observed':15,'supplementary_textareas_observed':len(supplementary),'composite_questions':9,'composite_textarea_count':sum(len(q.get('subfields',[])) for q in questions),'checkbox_options':sum(len(q.get('options',[])) for q in questions if q['control_type']=='checkbox_group')}
result['open_checks'] = ['后续事件尚在采集，报告不是最终完成判定']
result['source_artifacts'] = ['work/form-exploration/dom-observations.json']
if (BASE/'visible-multiselect-coverage.json').exists():
    visible_evidence = json.loads((BASE/'visible-multiselect-coverage.json').read_text())
    assert len(visible_evidence['singles']) == 28
    assert visible_evidence['all'] == visible_evidence['none']
    assert all(s['signature'] == visible_evidence['none'] for s in visible_evidence['singles'])
    result['visible_checkbox_coverage'] = {'method':'按getClientRects过滤实际可见控件，比较题容器和控件类型/placeholder签名','all_selected_matches_none':True,'single_option_cases_checked':28,'all_single_option_signatures_match_none':True,'does_not_prove_all_subsets_equivalent':True}
    result['source_artifacts'].append('work/form-exploration/visible-multiselect-coverage.json')
if (BASE/'dropdown-coverage.json').exists():
    dropdown_evidence = json.loads((BASE/'dropdown-coverage.json').read_text())
    assert {x['value'] for x in dropdown_evidence['departments']} == set(dropdowns['xihnqc'])
    assert len(dropdown_evidence['departments']) == 31
    assert len(dropdown_evidence['verified']) == 14
    assert all(x['value'] == x['result']['selected'] for x in dropdown_evidence['verified'])
    result['dropdown_coverage'] = {'department_choices_tested':[x['value'] for x in dropdown_evidence['departments']], 'explicit_selection_readback':[{'question':record_ids[x['id']],'choice':x['value'],'selected':x['result']['selected'],'expanded':x['result']['expanded'],'visible_textareas':x['result']['visibleTexts'],'question_count':x['questionCount']} for x in dropdown_evidence['verified']]}
    result['source_artifacts'].append('work/form-exploration/dropdown-coverage.json')
if (BASE/'final-blank-state.json').exists():
    final_state = json.loads((BASE/'final-blank-state.json').read_text())
    assert final_state['outline'] == ['Fill in outline (0/18 questions)']
    assert len(final_state['questions']) == 18
    assert all(q['selected'] is None and all(not c['checked'] and c['value']=='' for c in q['controls']) for q in final_state['questions'])
    result['final_ui_state'] = final_state
    result['source_artifacts'].append('work/form-exploration/final-blank-state.json')
if (BASE/'multiselect-coverage.json').exists():
    checkbox_evidence = json.loads((BASE/'multiselect-coverage.json').read_text())
    expected = {(q['observed_container_id'], option) for q in questions if q['control_type']=='checkbox_group' for option in q['options']}
    actual = {(x['id'], x['option']) for x in checkbox_evidence['results']}
    assert expected == actual, {'missing':sorted(expected-actual),'unexpected':sorted(actual-expected)}
    result['checkbox_coverage'] = [{'question':record_ids[x['id']],'option':x['option'],'numbered_question_count':x['totalQuestions'],'dom_control_counts':{record_ids[dom]:n for dom,n in x['controlCounts']}} for x in checkbox_evidence['results']]
    result['source_artifacts'].append('work/form-exploration/multiselect-coverage.json')
result['ui_text_caveats'] = [
    '不规范类选项1-3的DOM label.textContent终止于“无审核”，1-12终止于“慢性病、老年病”；title属性为空，没有发现更完整的标签文本。按表单原文记录，不从法规补全。',
    '表单原文含“剂里”“数里”“用里”“修改口期”“开县”等疑似错字；本报告保留原文，未修改表单。',
    '“抗肿瘤物相关项”“第二类精神的品规数”为表单原文；本报告未自行改写。',
    '三组多选选项的编号都从1-1开始；必须按父题和选项全文区分，不能只用编号定位。',
    '医保子题的否选项要求写明药品名称，但出现的补充框提示Optional。此处分别记录业务文案与UI要求，未通过提交测试实际校验。'
    ,'处方中药物品规总数只提供1至5，但不规范项又包含“单张门急诊处方超过五种药品”。超过5种如何记录、品规如何计数需要业务方确认；不得自动压成5或擅自按通用名去重。'
]
result['adapter_implications'] = [
    '初始18题不能当作完整题目清单；每次选择触发项后重新获取可见题，并按可观察容器ID和题目标题定位。',
    '界面题号随条件题出现而变化；q01等记录ID固定，页面数字题号不固定。',
    '9个相关项是一个题容器内的2至4个textarea，共27个独立填空；其中“是否合理”仍是textarea，并非radio。',
    '科室、药师、品规总数是搜索式combobox，读取search输入的value不能替代读取已选项目。',
    '科室/药师的其他补充textarea位于展开的下拉菜单内，收起菜单后不显示；DOM节点存在不等于控件当前可见。',
    '其他选中后菜单可保持展开；进入下一下拉前应核验旧菜单收起、目标aria-expanded和目标选项可见，选择后回读选中值，不能假定连续click已成功。科室其他在补充文本为空时也可保持选中。',
    '复合填空容器观察到class=ksapc-qmultiStepInput-write；每个textarea外层前一span是子字段文案，可结合容器ID、子标签与位置映射。',
    '同一页面反复出现是/否和Please enter；定位必须限定题容器与子字段序号。',
    '观察到已选radio再次click会取消选择；设置前应先读checked状态，避免重试反向清空。',
    '不合理事项全部勾选后，合理选是可收起5个条件题；再改否时28个历史勾选仍在。隐藏不等于清空，变更父答案和开始新处方前须处理残留。',
    '日期input为readonly；只打开日期时间弹层、未按OK也观察到带入当前时间并在关闭弹层后保留。应通过明确日期选择和回读核对，不能把打开控件当作无副作用。',
    '三组多选均非必填；有的选项原文不完整，必须保留配置原文并将含义确认留给业务对齐。',
    '本次没有调用现有wps-mcp；这里只记录所需表单控件能力，不声称当前MCP已通过适配验证。',
    '页面没有iframe，题目位于当前文档；最终提交按钮可见但本次未点击。'
]
OUT.mkdir(exist_ok=True)
(BASE/'compiled-structure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary'],ensure_ascii=False))
print(f"Compiled {len(events)} observed states; no final artifact published yet")
