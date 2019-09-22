# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:49:16 2019

@author: khaled.ghobashy
"""
# Standard library imports
import os
import pickle

# 3rd party library imports
import numpy as np

# Local applicataion imports
from .solvers import kds_solver, dds_solver

###############################################################################

def load_pickled_data(file):
    with open(file, 'rb') as f:
        instance = pickle.load(f)
    return instance

###############################################################################
###############################################################################

class multibody_system(object):
    
    def __init__(self, system):
        self.topology = system.topology()
        try:
            self.Subsystems = system.subsystems
        except AttributeError:
            pass
        
###############################################################################
###############################################################################

class simulation(object):
    
    def __init__(self, name, model, typ='kds'):
        self.name = name
        self.assembly = model.topology
        if typ == 'kds':
            self.soln = kds_solver(self.assembly)
        elif typ == 'dds':
            self.soln = dds_solver(self.assembly)
        else:
            raise ValueError('Bad simulation type argument : %r'%typ)
    
    def set_time_array(self, duration, spacing):
        self.soln.set_time_array(duration, spacing)
        
    def solve(self, run_id=None):
        run_id = '%s_temp'%self.name if run_id is None else run_id
        self.soln.solve(run_id)
    
    def save_results(self, path, filename):
        path = os.path.abspath(path)
        filepath = os.path.join(path, filename)
        self.soln.pos_dataframe.to_csv('%s.csv'%filepath, index=True)
        print('results saved as %s.csv at %s'%(filename, path))
        
    def eval_reactions(self):
        self.soln.eval_reactions()
    
