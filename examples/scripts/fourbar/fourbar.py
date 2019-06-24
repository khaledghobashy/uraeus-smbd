# -*- coding: utf-8 -*-
"""
Created on Sun May  5 10:07:05 2019

@author: khaled.ghobashy
"""

import smbd.systems as systems

from smbd.numenv.python.codegen import projects as py_proj
from smbd.numenv.cpp_eigen.codegen import projects as cpp_proj

project = systems.standalone_project('')
project.create()

model_name = 'fourbar'

# Creating sym_model Instance
# ===========================
sym_model = systems.standalone_topology(model_name)

# Adding Bodies
sym_model.add_body('l1')
sym_model.add_body('l2')
sym_model.add_body('l3')

# Adding Joints
sym_model.add_joint.revolute('a', 'ground', 'rbs_l1')
sym_model.add_joint.spherical('b', 'rbs_l1', 'rbs_l2')
sym_model.add_joint.universal('c', 'rbs_l2', 'rbs_l3')
sym_model.add_joint.revolute('d', 'rbs_l3', 'ground')

# Adding Actuators
sym_model.add_actuator.rotational_actuator('act', 'jcs_a')

# Assembling the Model
sym_model.assemble()


# Creating Configuration Instance
config = systems.configuration('%s_cfg'%model_name, sym_model)

# Adding UserInputs
# =================
config.add_point.UserInput('a')
config.add_point.UserInput('b')
config.add_point.UserInput('c')
config.add_point.UserInput('d')

config.add_vector.UserInput('x')
config.add_vector.UserInput('y')
config.add_vector.UserInput('z')

# Defining Relations
# ==================
config.add_relation.Equal_to('pt1_jcs_a', ('hps_a',))
config.add_relation.Equal_to('pt1_jcs_b', ('hps_b',))
config.add_relation.Equal_to('pt1_jcs_c', ('hps_c',))
config.add_relation.Equal_to('pt1_jcs_d', ('hps_d',))

config.add_relation.Oriented('ax1_jcs_c', ('hps_b', 'hps_c'))
config.add_relation.Oriented('ax2_jcs_c', ('hps_c', 'hps_b'))

config.add_relation.Equal_to('ax1_jcs_a', ('vcs_x',))
config.add_relation.Equal_to('ax1_jcs_b', ('vcs_z',))
config.add_relation.Equal_to('ax1_jcs_d', ('vcs_y',))

# Creating Geometries
# ===================
config.add_scalar.UserInput('links_ro')

config.add_geometry.Cylinder_Geometry('l1', ('hps_a','hps_b','s_links_ro'))
config.assign_geometry_to_body('rbs_l1', 'gms_l1')

config.add_geometry.Cylinder_Geometry('l2', ('hps_b','hps_c','s_links_ro'))
config.assign_geometry_to_body('rbs_l2', 'gms_l2')

config.add_geometry.Cylinder_Geometry('l3', ('hps_c','hps_d','s_links_ro'))
config.assign_geometry_to_body('rbs_l3', 'gms_l3')

# Assembling the Configuration
# ============================
config.assemble()
config.extract_inputs_to_csv('config_inputs')


# Writing Python Project
# ======================
py_project = py_proj.standalone_project(parent_dir='')
py_project.create_dirs()
py_project.write_topology_code(sym_model.topology)
py_project.write_configuration_code(config.config)
py_project.write_mainfile()


# Writing C++ Project
# ===================
cpp_project = cpp_proj.standalone_project(parent_dir='')
cpp_project.create_dirs()
cpp_project.write_topology_code(sym_model.topology)
cpp_project.write_configuration_code(config.config)
cpp_project.write_mainfile()
cpp_project.write_makefile()


