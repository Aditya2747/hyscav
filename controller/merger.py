def merge_issues(all_issues):
    """
    Merge and deduplicate issues from all analyzers
    """
    seen = set()
    merged = []

    for issue in all_issues:
        key = (
            issue.get("tool"),
            issue.get("type"),
            issue.get("description"),
            issue.get("contract")
        )

        if key not in seen:
            seen.add(key)
            merged.append(issue)

    return merged
