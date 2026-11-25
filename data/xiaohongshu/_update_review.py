import importlib.util
from pathlib import Path

directory = Path(__file__).parent
spec = importlib.util.spec_from_file_location('records', directory / 'records.py')
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)
records = store.read_records(store.DEFAULT_FILE)
record = records['6ada267b000000002c00fd0e']
record['review_status'] = 'Expanded 点点 AI/commenter reply reviewed; video partially reviewed, not a full transcript; original media not archived.'
record['notes'] = 'Initially captured from a listing; title may be truncated. Subsequent review: ' + record['review_status']
record.setdefault('review_observations', []).extend([
    'An existing commenter lists five shops; the expanded AI response supplies these unverified leads, not authoritative addresses or a full video transcript:',
    '大口食堂: AI claims 江岸区西马路63-85号百帝苑雅云1单元1层4号, near 苗栗路/马祖路.',
    '三间张Hokkien: AI claims 江岸区芦沟桥路68号武汉天地12号楼.',
    '三回野饭铺: AI claims 汉口万象城对面宝岛公园西北门斜对面.',
    '迪迪寿喜烧食堂: AI claims 3号线菱角湖站A出口旁.',
    'Ouioui又又制甜: AI claims 武汉新天地附近武汉二中旁.',
    'The AI says all are in 汉口; locations and all AI claims remain unverified.',
])
record['status'] = 'partial'
store.write_records(store.DEFAULT_FILE, records)
print('Updated 1 record')
