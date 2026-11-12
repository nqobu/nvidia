import numpy as np
from sympy import Symbol, Eq

import modulus
from modulus.hydra import to_absolute_path, to_yaml, instantiate_arch
from modulus.hydra.config import ModulusConfig
from modulus.csv_utils.csv_rw import csv_to_dict
from modulus.continuous.solvers.solver import Solver
from modulus.continuous.domain.domain import Domain
from modulus.geometry.csg.csg_2d import Rectangle, Line, Channel2D
from modulus.sympy_utils.functions import parabola
from modulus.PDES.navier_stokes import NavierStokes
from modulus.PDES.basic import NormalDotVec
from modulus.continuous.constraints.constraint import (
    PointwiseBoundaryConstraint,
    PointwiseInteriorConstraint,
    IntegralBoundaryConstraint,
)

from modulus.continuous.validator.validator import PointwiseValidator
from modulus.key import Key
from modulus.node import Node


@modulus.main(config_path="conf", config_name="config_param")
def run(cfg: ModulusConfig) -> None:
    print(to_yaml(cfg))

    # make list of nodes to unroll graph on
    ns = NavierStokes(nu=0.02, rho=1.0, dim=2, time=False)
    normal_dot_vel = NormalDotVec(["u", "v"])
    flow_net = instantiate_arch(
        input_keys=[Key("x"), Key("y"), Key("chip_height"), Key("chip_width")],
        output_keys=[Key("u"), Key("v"), Key("p")],
        cfg=cfg.arch.fourier_net,
    )
    nodes = (
        ns.make_nodes()
        + normal_dot_vel.make_nodes()
        + [flow_net.make_node(name="flow_network", jit=cfg.jit)]
    )

    # add constraints to solver
    # simulation params
    channel_length = (-2.5, 2.5)
    channel_width = (-0.5, 0.5)
    chip_pos = -1.0
    inlet_vel = 1.5

    # paramteric variables
    chip_height = Symbol("chip_height")
    chip_width = Symbol("chip_width")
    chip_height_range = (0.4, 0.8)
    chip_width_range = (0.6, 1.4)
    param_ranges = {chip_height: chip_height_range, chip_width: chip_width_range}

    # define sympy variables to parametrize domain curves
    x, y = Symbol("x"), Symbol("y")

    # define geometry
    channel = Channel2D(
        (channel_length[0], channel_width[0]), (channel_length[1], channel_width[1])
    )
    inlet = Line(
        (channel_length[0], channel_width[0]),
        (channel_length[0], channel_width[1]),
        normal=1,
    )
    outlet = Line(
        (channel_length[1], channel_width[0]),
        (channel_length[1], channel_width[1]),
        normal=1,
    )
    rec = Rectangle(
        (chip_pos, channel_width[0]),
        (chip_pos + chip_width, channel_width[0] + chip_height),
    )
    flow_rec = Rectangle(
        (chip_pos - 0.25, channel_width[0]),
        (chip_pos + chip_width + 0.25, channel_width[1]),
    )
    geo = channel - rec
    geo_hr = geo & flow_rec
    geo_lr = geo - flow_rec
    x_pos = Symbol("x_pos")
    integral_line = Line((x_pos, channel_width[0]), (x_pos, channel_width[1]), 1)
    x_pos_range = {
        x_pos: lambda batch_size: np.full(
            (batch_size, 1), np.random.uniform(channel_length[0], channel_length[1])
        )
    }

    # make domain
    domain = Domain()

    # inlet
    inlet_parabola = parabola(y, channel_width[0], channel_width[1], inlet_vel)
    inlet = PointwiseBoundaryConstraint(
        nodes=nodes,
        geometry=inlet,
        outvar={"u": inlet_parabola, "v": 0},
        batch_size=cfg.batch_size.inlet,
        param_ranges=param_ranges,
    )
    domain.add_constraint(inlet, "inlet")

    # outlet
    outlet = PointwiseBoundaryConstraint(
        nodes=nodes,
        geometry=outlet,
        outvar={"p": 0},
        batch_size=cfg.batch_size.outlet,
        criteria=Eq(x, channel_length[1]),
        param_ranges=param_ranges,
    )
    domain.add_constraint(outlet, "outlet")

    # no slip
    no_slip = PointwiseBoundaryConstraint(
        nodes=nodes,
        geometry=geo,
        outvar={"u": 0, "v": 0},
        batch_size=cfg.batch_size.no_slip,
        param_ranges=param_ranges,
    )
    domain.add_constraint(no_slip, "no_slip")

    # interior lr
    interior_lr = PointwiseInteriorConstraint(
        nodes=nodes,
        geometry=geo_lr,
        outvar={"continuity": 0, "momentum_x": 0, "momentum_y": 0},
        batch_size=cfg.batch_size.interior_lr,
        bounds={x: channel_length, y: channel_width},
        lambda_weighting={
            "continuity": 2 * geo.sdf,
            "momentum_x": 2 * geo.sdf,
            "momentum_y": 2 * geo.sdf,
        },
        param_ranges=param_ranges,
    )
    domain.add_constraint(interior_lr, "interior_lr")

    # interior hr
    interior_hr = PointwiseInteriorConstraint(
        nodes=nodes,
        geometry=geo_hr,
        outvar={"continuity": 0, "momentum_x": 0, "momentum_y": 0},
        batch_size=cfg.batch_size.interior_hr,
        bounds={x: channel_length, y: channel_width},
        lambda_weighting={
            "continuity": 2 * geo.sdf,
            "momentum_x": 2 * geo.sdf,
            "momentum_y": 2 * geo.sdf,
        },
        param_ranges=param_ranges,
    )
    domain.add_constraint(interior_hr, "interior_hr")

    # integral continuity
    integral_continuity = IntegralBoundaryConstraint(
        nodes=nodes,
        geometry=integral_line,
        outvar={"normal_dot_vel": 1},
        batch_size=cfg.batch_size.num_integral_continuity,
        integral_batch_size=cfg.batch_size.integral_continuity,
        lambda_weighting={"normal_dot_vel": 1},
        criteria=geo.sdf > 0,
        param_ranges={**x_pos_range, **param_ranges},
    )
    domain.add_constraint(integral_continuity, "integral_continuity")

    # add validation data
    mapping = {"Points:0": "x", "Points:1": "y", "U:0": "u", "U:1": "v", "p": "p"}
    openfoam_var = csv_to_dict(to_absolute_path("openfoam/2D_chip_fluid0.csv"), mapping)
    openfoam_var["x"] -= 2.5  # normalize pos
    openfoam_var["y"] -= 0.5
    openfoam_var.update({"chip_height": np.full_like(openfoam_var["x"], 0.6)})
    openfoam_var.update({"chip_width": np.full_like(openfoam_var["x"], 1.0)})

    openfoam_invar_numpy = {
        key: value
        for key, value in openfoam_var.items()
        if key in ["x", "y", "chip_height", "chip_width"]
    }
    openfoam_outvar_numpy = {
        key: value for key, value in openfoam_var.items() if key in ["u", "v", "p"]
    }
    openfoam_validator = PointwiseValidator(
        openfoam_invar_numpy, openfoam_outvar_numpy, nodes
    )
    domain.add_validator(openfoam_validator)

    # make solver
    slv = Solver(cfg, domain)

    # start solver
    slv.solve()


if __name__ == "__main__":
    run()
