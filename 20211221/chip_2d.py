from sympy import Symbol
import numpy as np
import tensorflow as tf

from simnet.solver import Solver
from simnet.dataset import TrainDomain, ValidationDomain
from simnet.data import Validation
from simnet.sympy_utils.geometry_2d import Rectangle, Line, Channel2D
from simnet.sympy_utils.functions import parabola
from simnet.csv_utils.csv_rw import csv_to_dict
from simnet.PDES.navier_stokes import IntegralContinuity, NavierStokes
from simnet.controller import SimNetController
from simnet.architecture import FourierNetArch

# simulation params
channel_length = (-2.5, 2.5)
channel_width = (-0.5, 0.5)
chip_pos = -1.0
chip_height = 0.6
chip_width = 1.0
inlet_vel = 1.5

# define geometry
channel = Channel2D((channel_length[0], channel_width[0]),
                    (channel_length[1], channel_width[1]))
inlet = Line((channel_length[0], channel_width[0]),
             (channel_length[0], channel_width[1]),
             normal=1)
outlet = Line((channel_length[1], channel_width[0]),
              (channel_length[1], channel_width[1]),
              normal=1)
rec = Rectangle((chip_pos, channel_width[0]),
                (chip_pos+chip_width, channel_width[0]+chip_height))
flow_rec = Rectangle((chip_pos-0.25, channel_width[0]),
                     (chip_pos+chip_width+0.25, channel_width[1]))
geo = channel - rec
geo_hr = geo & flow_rec
geo_lr = geo - flow_rec
x_pos = Symbol('x_pos')
integral_line = Line((x_pos, channel_width[0]),
                     (x_pos, channel_width[1]),
                     1)
x_pos_range = {x_pos: lambda batch_size: np.full((batch_size, 1), np.random.uniform(channel_length[0], channel_length[1]))}

# define sympy variables to parametrize domain curves
x, y = Symbol('x'), Symbol('y')

# validation data
mapping = {'Points:0': 'x', 'Points:1': 'y',
           'U:0': 'u', 'U:1': 'v', 'p': 'p'}
openfoam_var = csv_to_dict('openfoam/2D_chip_fluid0.csv', mapping)
openfoam_var['x'] -= 2.5 # normalize pos
openfoam_var['y'] -= 0.5
openfoam_invar_numpy = {key: value for key, value in openfoam_var.items() if key in ['x', 'y']}
openfoam_outvar_numpy = {key: value for key, value in openfoam_var.items() if key in ['u', 'v', 'p']}

class Chip2DTrain(TrainDomain):
  def __init__(self, **config):
    super(Chip2DTrain, self).__init__()

    # inlet
    inlet_parabola = parabola(y, channel_width[0], channel_width[1], inlet_vel)
    inlet_bc = inlet.boundary_bc(outvar_sympy={'u': inlet_parabola, 'v': 0},
                                 batch_size_per_area=64)
    self.add(inlet_bc, name="Inlet")

    # outlet
    outlet_bc = outlet.boundary_bc(outvar_sympy={'p': 0},
                                   batch_size_per_area=64)
    self.add(outlet_bc, name="Outlet")

    # noslip
    noslip = geo.boundary_bc(outvar_sympy={'u': 0, 'v': 0},
                             batch_size_per_area=256)
    self.add(noslip, name="ChipNS")

    # interior lr
    interior_lr = geo_lr.interior_bc(outvar_sympy={'continuity': 0, 'momentum_x': 0, 'momentum_y': 0},
                                     bounds={x: channel_length, y: channel_width},
                                     lambda_sympy={'lambda_continuity': 2*geo.sdf,
                                                   'lambda_momentum_x': 2*geo.sdf,
                                                   'lambda_momentum_y': 2*geo.sdf},
                                     batch_size_per_area=256)
    self.add(interior_lr, name="InteriorLR")

    # interior hr
    interior_hr = geo_hr.interior_bc(outvar_sympy={'continuity': 0, 'momentum_x': 0, 'momentum_y': 0},
                                     bounds={x: channel_length, y: channel_width},
                                     lambda_sympy={'lambda_continuity': 2*geo.sdf,
                                                   'lambda_momentum_x': 2*geo.sdf,
                                                   'lambda_momentum_y': 2*geo.sdf},
                                     batch_size_per_area=1024)
    self.add(interior_hr, name="InteriorHR")


    # integral continuity
    for i in range(4):
      IC = integral_line.boundary_bc(outvar_sympy={'integral_continuity': 1.0},
                                     batch_size_per_area=512,
                                     lambda_sympy={'lambda_integral_continuity': 1.0},
                                     criteria=geo.sdf>0,
                                     param_ranges=x_pos_range,
                                     fixed_var=False)
      self.add(IC, name="IntegralContinuity_"+str(i))

class Chip2DVal(ValidationDomain):
  def __init__(self, **config):
    super(Chip2DVal, self).__init__()
    val = Validation.from_numpy(openfoam_invar_numpy, openfoam_outvar_numpy)
    self.add(val, name='Val')

class ChipSolver(Solver):
  train_domain = Chip2DTrain
  val_domain = Chip2DVal
  arch = FourierNetArch

  def __init__(self, **config):
    super(ChipSolver, self).__init__(**config)

    self.frequencies = ('axis,diagonal', [i/5. for i in range(25)]) 
    
    self.equations = (NavierStokes(nu=0.02, rho=1, dim=2, time=False).make_node()
                      + IntegralContinuity(dim=2).make_node())
    flow_net = self.arch.make_node(name='flow_net',
                                   inputs=['x', 'y'],
                                   outputs=['u', 'v', 'p'])
    self.nets = [flow_net]

  @classmethod
  def update_defaults(cls, defaults):
    defaults.update({
        'network_dir': './network_checkpoint_chip_2d',
        'rec_results': True,
        'rec_results_freq': 5000,
        'max_steps': 10000,
        'decay_steps': 100,
        'xla': True
        })
if __name__ == '__main__':
  ctr = SimNetController(ChipSolver)
  ctr.run()
