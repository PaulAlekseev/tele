

class DeliverabilityChecker:
    @staticmethod
    def check_deliverability(content: dict):
        data = content.get('data')
        problem_result = {}
        try:
            result_dns = (DeliverabilityChecker._check_dns_data(data[0]))
            problem_result = DeliverabilityChecker._update_data(problem_result, DeliverabilityChecker._check_dkim_data(data[1]))
            problem_result = DeliverabilityChecker._update_data(problem_result, DeliverabilityChecker._check_spfs_data(data[2]))
            problem_result = DeliverabilityChecker._update_data(problem_result, DeliverabilityChecker._check_ptrs_data(data[3]))
            for domain, value in result_dns.items():
                problem_result[domain].update({
                    'local_authority': value['local_authority']
                })
        except Exception as e:
            return {}
        return problem_result

    @staticmethod
    def _clear_domainkey(domainkey: str):
        return domainkey.replace('default._domainkey.', '')

    @staticmethod
    def _check_dns_data(dns_data: dict) -> dict:
        return {
            DeliverabilityChecker._clear_domainkey(item.get('domain')): {'local_authority': item.get('local_authority')} for item in dns_data['data']
        }

    @staticmethod
    def _check_dkim_data(dkim_data: dict) -> dict:
        result = {}
        for item in dkim_data['data']:
            if item.get('state') == 'VALID':
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 1
            else :
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 0
        return result

    @staticmethod
    def _check_spfs_data(spfs_data: dict) -> dict:
        result = {}
        for item in spfs_data['data']:
            if item.get('state') == 'VALID':
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 1
            else :
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 0
        return result

    @staticmethod
    def _check_ptrs_data(ptrs_data: dict) -> dict:
        result = {}
        for item in ptrs_data['data']:
            if item.get('state') == 'VALID':
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 1
            else :
                result[DeliverabilityChecker._clear_domainkey(item.get('domain'))] = 0
        return result

    @staticmethod
    def _update_data(old_data: dict, new_data: dict):
        for key, value in new_data.items():
            if key in old_data:
                old_data[key]['result'] += value
            else:
                old_data[key] = {'result': value}
        return old_data
