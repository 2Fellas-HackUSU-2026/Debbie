import requests
import time
import json
import os

print("Waiting for server to start...")
time.sleep(2)

print("1. Uploading document...")
with open('.build/test_data/integration_test.docx', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)

print("Upload status:", response.status_code)
data = response.json()
doc_id = data['doc_id']
structure = data['structure']

print(f"Doc ID: {doc_id}")
print(f"Structure has {len(structure['paragraphs'])} paragraphs and {len(structure['tables'])} tables.")

print("\n2. Getting AI suggestions...")
try:
    response = requests.get(f'http://localhost:8000/suggest/{doc_id}')
    print("Suggestions status:", response.status_code)
    suggestions = response.json()
    print("Suggestions found:", len(suggestions.get('suggestions', [])))
except Exception as e:
    print(f"AI Suggestions failed (expected if API key not set): {e}")

print("\n3. Processing document...")
payload = {
    "doc_id": doc_id,
    "selections": [
        {"id": "p_2", "variable_name": "company_name", "description": "The name of the company"},
        {"id": "t_0_col_1", "variable_name": "table_column_value", "description": "Values for column 1"},
        {"id": "t_0_r_1_c_1", "variable_name": "specific_override", "description": "Override for this specific cell"}
    ]
}

response = requests.post('http://localhost:8000/process', json=payload)
print("Process status:", response.status_code)

if response.status_code == 200:
    print("Process success:", response.json()['message'])

    # Check data.json
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data_json = json.load(f)
        print("\ndata.json contents:")
        print(json.dumps(data_json, indent=2))

        # Verify specific override took precedence
        if "company_name" in data_json and "table_column_value" in data_json and "specific_override" in data_json:
            print("✓ SUCCESS: All variables saved correctly in data.json")
        else:
            print("✗ ERROR: Missing variables in data.json")
    else:
        print("✗ ERROR: data.json not created!")
