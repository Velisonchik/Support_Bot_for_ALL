
from ldap3 import Connection
from reqs import AD_SERVER, AD_SERVER_DN, username_ad_adm, passwd_ad_adm, member_of_for_ad_search


def get_ids_from_ad():
    ids = {}
    conn = Connection(AD_SERVER, user='sdsys\\' + username_ad_adm, password=passwd_ad_adm, auto_bind=True)
    conn.search(AD_SERVER_DN, f'(&(objectclass=person)(memberOf={member_of_for_ad_search}))',
                attributes=['sAMAccountName', 'telegramID'])
    for i in conn.response:
        try:
            ids[i['attributes']['telegramID'][0]] = i['attributes']['sAMAccountName']
        except (IndexError, KeyError):
            pass
    return ids


if __name__ == '__main__':
    get_ids_from_ad()
