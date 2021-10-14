import logging
import json
import datetime
from collections.abc import Mapping
import requests

import dimod
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


class QPUAccessAccumComposite(dimod.ComposedSampler):
    children = None
    _properties = {}
    _parameters = {}
    _scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    _ip_fetch_urls = ['https://inet-ip.info/ip', 'https://api.ipify.org/',
                      'https://ident.me', 'https://icanhazip.com',
                      'https://www.trackip.net/ip', 'https://myip.dnsomatic.com']
    _timestamp_format = '%Y-%m-%d %H:%M:%S:%f'

    def __init__(self, child_sampler, username, keyfile_path, spreadsheet_key, worksheet_index=0):
        self.children = [child_sampler]
        self.username = username
        self.keyfile_path = keyfile_path
        self.spreadsheet_key = spreadsheet_key
        self.worksheet_index = worksheet_index

        self._authorize()

    @property
    def properties(self):
        return self._properties

    @property
    def parameters(self):
        return self._parameters

    def _authorize(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.keyfile_path, self._scope)
        gc = gspread.authorize(credentials)
        workbook = gc.open_by_key(self.spreadsheet_key)
        self.worksheet = workbook.get_worksheet(self.worksheet_index)

    def _post_access_info(self, sampleset, **parameters):
        child = self.child
        for _ in range(10):  # max depth of children
            if hasattr(child, 'child'):
                child = child.child
            elif hasattr(child, 'client'):
                break
        else:
            raise Exception(f'Invalid child sampler: {self.child}')

        client = child.client
        timestamp = datetime.datetime.now().strftime(self._timestamp_format)
        access_info = parameters.copy()
        access_info.update(dict(timestamp=timestamp, name=self.username,
                                token=client.token.split('-')[0],
                                solver=client.get_solver().name,
                                endpoint=client.endpoint,
                                num_variables=len(sampleset.variables)))

        def flatten_dict(dic):
            for k, v in dic.items():
                if isinstance(v, Mapping):
                    flatten_dict(v)
                else:
                    access_info[k] = v

        if hasattr(sampleset, 'info'):
            flatten_dict(sampleset.info)

        for url in self._ip_fetch_urls:
            try:
                response = requests.get(url)
            except:
                continue
            access_info['ip_address'] = str(response.text).strip('\n')
            break

        column_numbers = {name: number for number, name in enumerate(self.worksheet.row_values(1))}
        insert_values = {}
        for name, value in access_info.items():
            number = column_numbers.get(name, None)
            if number is not None:
                insert_values[number] = value

        target_row = len(self.worksheet.col_values(1)) + 1
        insert_cells = self.worksheet.range(target_row, 1, target_row, len(column_numbers))
        for number, value in insert_values.items():
            insert_cells[number].value = value
        self.worksheet.update_cells(insert_cells)

    def sample(self, bqm, **parameters):
        sampleset = self.child.sample(bqm, **parameters)
        self._post_access_info(sampleset, **parameters)
        return sampleset

    def sample_ising(self, h, J, **parameters):
        sampleset = self.child.sample_ising(h, J, **parameters)
        self._post_access_info(sampleset, **parameters)
        return sampleset

    def sample_qubo(self, Q, **parameters):
        sampleset = self.child.sample_qubo(Q, **parameters)
        self._post_access_info(sampleset, **parameters)
        return sampleset

    def sample_cqm(self, cqm, **parameters):
        sampleset = self.child.sample_cqm(cqm, **parameters)
        self._post_access_info(sampleset, **parameters)
        return sampleset

    def sample_dqm(self, dqm, **parameters):
        sampleset = self.child.sample_dqm(dqm, **parameters)
        self._post_access_info(sampleset, **parameters)
        return sampleset
