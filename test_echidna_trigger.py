from analyzers.echidna_runner_docker import _static_echidna_proxy, simplify_echidna_issues

result = _static_echidna_proxy('contracts/EchidnaTriggerDemo.sol')
print('=== STATIC PROXY RESULTS ===')
for k, v in result.items():
    print(f'  {k}: {v}')

print()
print('=== SIMPLIFIED ISSUES ===')
issues = simplify_echidna_issues(result, 'EchidnaTriggerDemo')
for i in issues:
    print(f'  Tool: {i["tool"]}, Title: {i["title"]}, Severity: {i["severity"]}')
    print(f'    Desc: {i["description"]}')
