#!/usr/bin/env python3
"""Validate draft handover locally; no Dataverse/Azure access."""
from pathlib import Path
import json
import yaml

root = Path(__file__).parent
spec = yaml.safe_load((root / 'spec/data-model.yaml').read_text(encoding='utf-8'))
tables = spec['tables']
assert len(tables) == 19, len(tables)
names = [t['name'] for t in tables]
assert len(names) == len(set(names)), 'duplicate tables'
assert len(set(t['logicalName'] for t in tables)) == len(tables)
for table in tables:
    fields = table['fields']
    f_names = [f['name'] for f in fields]
    assert 'Name' in f_names, table['name']
    assert len(f_names) == len(set(f_names)), f'duplicate column on {table["name"]}'
    for field in fields:
        if field['type'] == 'lookup':
            assert field['target'] in names, (table['name'], field['name'], field['target'])
        if field['type'] == 'choice':
            assert field.get('options'), (table['name'], field['name'])
    for key in table.get('alternateKeys', []):
        assert all(k in f_names for k in key), (table['name'], key)
examples = [
    ('processing-step-callback', 'processing-step-callback'),
    ('processing-step-request', 'processing-step-request'),
    ('document-received-event', 'document-received-event'),
    ('document-register-request', 'document-register-request'),
    ('event-listener-request', 'event-listener-request')
]
try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print('NOTE jsonschema unavailable; syntax-only contract check')
    Draft202012Validator = None
for filename, schema_name in examples:
    example = json.loads((root / f'examples/{filename}.json').read_text(encoding='utf-8'))
    schema = json.loads((root / f'contracts/{schema_name}.schema.json').read_text(encoding='utf-8'))
    if Draft202012Validator:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(example)
print(f'OK: {len(tables)} tables, {sum(len(t["fields"]) for t in tables)} fields, {len(examples)} example contracts')
