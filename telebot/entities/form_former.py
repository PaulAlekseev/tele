import urllib.parse


class FormFormer:

    @staticmethod
    def _domains_former(domains: list) -> dict:
        return {
            f'domain-{i}': domains[i]
            for i in range(len(domains))
        }

    @staticmethod
    def dns_former(domains: list) -> dict:
        return {'command': [
            'DNS', 'has_local_authority', FormFormer._domains_former(domains)
        ]}

    @staticmethod
    def dkims_former(domains: list) -> dict:
        return {'command-0': [
            'EmailAuth', 'validate_current_dkims', FormFormer._domains_former(domains)
        ]}

    @staticmethod
    def spfs_former(domains: list) -> dict:
        return {'command-1': [
            'EmailAuth', 'validate_current_spfs', FormFormer._domains_former(domains)
        ]}

    @staticmethod
    def prts_former(domains: list) -> dict:
        return {'command-2': [
            'EmailAuth', 'validate_current_ptrs', FormFormer._domains_former(domains)
        ]}

    @staticmethod
    def return_full_source(domains: list) -> str:
        result = {}
        result.update(FormFormer.dns_former(domains))
        result.update(FormFormer.dkims_former(domains))
        result.update(FormFormer.spfs_former(domains))
        result.update(FormFormer.prts_former(domains))
        return urllib.parse.urlencode(result).replace('%27', '%22')