import os

from reqs import SUPPORT_SITE, SUPPORT_API_KEY, SUPPORT_VERSION, PROJECT_ID_FOR_NEW_ISSUE
from redminelib import Redmine

tracker_ids = {'i': 2, 'c': 3, 'e': 1}


def create_new_issue(subject: str, description: str, username: int, tracker_id_in_str: str = 'c',
                     author_issue='', comment=None, file_path=None):
    print('Result of create_new_issue: ')

    redmine_adm = Redmine(SUPPORT_SITE, key=SUPPORT_API_KEY, version=SUPPORT_VERSION)
    assigned_to_id = username

    try:
        author_issue_id = int(list(redmine_adm.user.filter(name=author_issue).values('id'))[0]['id'])
    except IndexError:
        return f'Такого пользователя {author_issue} не нашел в саппорте'

    redmine_for_author_issue = Redmine(SUPPORT_SITE, key=redmine_adm.user.get(author_issue_id).api_key,
                                       version=SUPPORT_VERSION)
    issue = redmine_for_author_issue.issue.new()
    issue.project_id = PROJECT_ID_FOR_NEW_ISSUE
    issue.subject = subject
    issue.tracker_id = tracker_ids[tracker_id_in_str]
    issue.description = description
    issue.status_id = 1
    issue.priority_id = 4
    issue.category_id = 186
    issue.fixed_version_id = 4
    issue.assigned_to_id = assigned_to_id
    issue.done_ratio = 40
    issue.save()
    # if file_path:
    # issue.uploads = [{'path': f'{file_path}', 'filename': f'{file_path}'}]
    # issue.save()
    # os.remove(file_path)
    # else:
    # issue.save()

    print(issue.url)
    return issue.url


def check_user_role(mas):
    for i in mas:
        if i['id'] == 4:
            return True


def get_project_managers():
    redmine_adm = Redmine(SUPPORT_SITE, key=SUPPORT_API_KEY, version=SUPPORT_VERSION)
    res = redmine_adm.project.get(PROJECT_ID_FOR_NEW_ISSUE)
    project_managers = {}
    for i in res.memberships.values():
        try:
            if check_user_role(i['roles']):
                project_managers[i['user']['name']] = i['user']['id']
        except KeyError:
            pass
    return project_managers

    # return list(res.memberships)


if __name__ == '__main__':
    # print(create_new_issue(subject='Test SuppBot', description='Description', username='kashanyan.v', elapsed_time=0.8,
    # tracker_id_in_str='c', comment='Тестовый коммент'))
    get_project_managers()
