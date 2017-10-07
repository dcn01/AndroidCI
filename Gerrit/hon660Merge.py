import hsm_common as hsmcommon
all_results = {'test_results': []}
if __name__ == "__main__":
    changes = hsmcommon.gerritChanges(status="merged")
    for item in changes:
        project = item['project']
        if project != None:
            need_append_result = True
            for element in all_results['test_results']:
                if project == element['project']:
                    element['patch_num'] += 1
                    need_append_result = False
                    break
            result = {'project': project, 'patch_num': 1}
            if need_append_result:
                all_results['test_results'].append(result)
    for item in all_results['test_results']:
        print(item)