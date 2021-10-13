import numpy as np
import dimod
from dwave.system import DWaveCliqueSampler

from qpu_access_accum import QPUAccessAccumComposite


def main():
    N = 15
    bqm = dimod.BQM(np.random.normal(size=(N, N)), 'BINARY')

    sampler_config = dict(token='TOKEN', solver='SOLVER')
    child_sampler = DWaveCliqueSampler(**sampler_config)

    accum_conifg = dict(username='NAME',
                        keyfile_path='API_KEY.json',
                        spreadsheet_key='SPREADSHEET_KEY')
    sampler = QPUAccessAccumComposite(child_sampler, **accum_conifg)

    sampleset = sampler.sample(bqm, num_reads=1000, annealing_time=1)
    print(sampleset.aggregate())


if __name__ == '__main__':
    main()