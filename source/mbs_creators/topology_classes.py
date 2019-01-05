# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 11:31:35 2019

@author: khale
"""

import sympy as sm
import matplotlib.pyplot as plt
import networkx as nx

from source.symbolic_classes.bodies import body, ground
from source.symbolic_classes.spatial_joints import absolute_locator
from source.symbolic_classes.algebraic_constraints import joint_actuator


class abstract_topology(object):
    
    def __init__(self,name):
        self.graph = nx.MultiGraph(name=name)
        self.name = name
        self._edges_map = {}
        
        # adding ground node
        attr_dict = self._attr_gen(ground)
        self.graph.add_node('ground',**attr_dict)
    
    @property
    def selected_variant(self):
        return self.graph
    @property
    def nodes(self):
        return self.selected_variant.nodes
    @property
    def edges(self):
        return self.selected_variant.edges
        
    @property
    def n(self):
        n = sum([node[-1] for node in self.nodes(data='n')])
        return n
    @property
    def nc(self):
        nc_nodes = sum([node[-1] for node in self.nodes(data='nc')])
        nc_edges = sum([edge[-1] for edge in self.edges(data='nc')])
        return nc_nodes + nc_edges
    @property
    def nve(self):
        nve_nodes = sum([node[-1] for node in self.nodes(data='nve')])
        nve_edges = sum([edge[-1] for edge in self.edges(data='nve')])
        return nve_nodes + nve_edges
    
    def _attr_gen(self,obj):
        attr_dict ={'n':obj.n,'nc':obj.nc,'nve':obj.nve,'class':obj}
        return attr_dict
    
    def draw_topology(self):
        plt.figure(figsize=(6,6))
        nx.draw_spring(self.selected_variant,with_labels=True)
        plt.show()

###############################################################################
###############################################################################

class topology(abstract_topology):
    
    def add_body(self,name):
        variant = self.selected_variant
        if name not in variant.nodes():
            attr_dict = self._attr_gen(body)
            variant.add_node(name,**attr_dict)
        
    
    def add_joint(self,typ,name,body_i,body_j):
        variant = self.selected_variant
        edge  = (body_i,body_j,name)
        if edge not in variant.edges:
            attr_dict = self._attr_gen(typ)
            variant.add_edge(*edge,**attr_dict)
            self._edges_map[name] = edge
            
    def add_joint_actuator(self,typ,name,joint_name):
        variant = self.selected_variant
        joint_edge = self._edges_map[joint_name]
        act_edge = (*joint_edge[:2],name)
        if act_edge not in variant.edges:
            attr_dict = self._attr_gen(typ)
            variant.add_edge(*act_edge,**attr_dict,joint_name=joint_name)
            self._edges_map[name] = act_edge
    
    def add_absolute_actuator(self,name,body,coordinate):
        variant = self.selected_variant
        edge  = (body,'ground',name)
        if edge not in variant.edges:
            attr_dict = self._attr_gen(absolute_locator)
            variant.add_edge(*edge,**attr_dict,coordinate=coordinate)
            self._edges_map[name] = edge
    
    def remove_body(self,name):
        self.selected_variant.remove_node(name)
    
    def remove_joint(self,name):
        edge = self._edges_map[name]
        self.selected_variant.remove_edge(*edge)
    
###############################################################################
###############################################################################

class template_based_topology(topology):
    
    def __init__(self,name):
        super().__init__(name)
        self.selected_variant.nodes['ground']['mirr']='ground'
        
    @property
    def virtual_bodies(self):
        condition = lambda n: n.startswith('vbs_') or n.startswith('vbr_')
        virtuals  = filter(condition,self.selected_variant.nodes)
        return set(virtuals)
    
    
    def add_body(self,name,mirrored=False):
        variant = self.selected_variant
        if mirrored:
            node1 = 'rbr_%s'%name
            node2 = 'rbl_%s'%name
            super().add_body(node1)
            super().add_body(node2)
            variant.nodes[node1]['mirr'] = node2
            variant.nodes[node2]['mirr'] = node1 
        else:
            node1 = node2 = 'rbs_%s'%name
            super().add_body(node1)
            variant.nodes[node1]['mirr'] = node2
    
    def add_virtual_body(self,name,mirrored=False):
        variant = self.selected_variant
        if mirrored:
            node1 = 'vbr_%s'%name
            node2 = 'vbl_%s'%name
            super().add_body(node1)
            super().add_body(node2)
            variant.nodes[node1]['mirr'] = node2
            variant.nodes[node2]['mirr'] = node1 
        else:
            node1 = node2 = 'vbs_%s'%name
            super().add_body(node1)
            variant.nodes[node1]['mirr'] = node2
    
    def add_joint(self,typ,name,body_i,body_j,mirrored=False):
        variant = self.selected_variant
        if mirrored:
            body_i_mirr = variant.nodes[body_i]['mirr']
            body_j_mirr = variant.nodes[body_j]['mirr']
            key1 = 'jcr_%s'%name
            key2 = 'jcl_%s'%name
            super().add_joint(typ,key1,body_i,body_j)
            super().add_joint(typ,key2,body_i_mirr,body_j_mirr)
            joint_edge1 = self._edges_map[key1]
            joint_edge2 = self._edges_map[key2]
            variant.edges[joint_edge1]['mirr'] = key2
            variant.edges[joint_edge2]['mirr'] = key1
        else:
            key = 'jcs_%s'%name
            super().add_joint(typ,key,body_i,body_j)
            joint_edge = self._edges_map[key]
            variant.edges[joint_edge]['mirr'] = key
    
    def add_joint_actuator(self,typ,name,joint_name,mirrored=False):
        variant = self.selected_variant
        if mirrored:
            joint_edge1 = self._edges_map[joint_name]
            joint_name2 = variant.edges[joint_edge1]['mirr']
            key1 = 'mcr_%s'%name
            key2 = 'mcl_%s'%name
            super().add_joint_actuator(typ,key1,joint_name)
            super().add_joint_actuator(typ,key2,joint_name2)
        else:
            key = 'mcs_%s'%name
            super().add_joint_actuator(typ,key,joint_name)
    
    def add_absolute_actuator(self,name,body_i,coordinate,mirrored=False):
        variant = self.selected_variant
        if mirrored:
            body_i_mirr = variant.nodes[body_i]['mirr']
            key1 = 'mcr_%s'%name
            key2 = 'mcl_%s'%name
            super().add_absolute_actuator(key1,body_i,coordinate)
            super().add_absolute_actuator(key2,body_i_mirr,coordinate)
        else:
            key = 'mcs_%s'%name
            super().add_absolute_actuator(key,body_i,coordinate)

###############################################################################
###############################################################################

class subsystem(abstract_topology):
    
    def __init__(self,name,topology):
        self.name = name+'_'
        self.topology = topology
        def label(x):
            name = (x if x=='ground' else self.name + x)
            return name
        self.graph = nx.relabel_nodes(topology.graph,label)
        self._virtual_bodies = []
    
    @property
    def virtual_bodies(self):
        virtual_bodies = [self.name+i for i in self.topology.virtual_bodies]
        return set(virtual_bodies)
    
    def _assemble_nodes(self):
        for n in self.nodes:
            if n.startswith(self.name+'vb'):
                pass
            else:
                body_type = self.nodes[n]['class']
                self.nodes[n]['obj'] = body_type(n)
            self.nodes[n]['mirr']=self.name+self.nodes[n]['mirr']
    
    def _assemble_edge(self,e):
        edge_class = self.edges[e]['class']
        b1, b2, name = e
        if issubclass(edge_class,joint_actuator):
            joint_name = self.edges[e]['joint_name']
            joint_object = self.edges[(b1,b2,joint_name)]['obj']
            self.edges[e]['obj'] = edge_class(name,joint_object)
        elif issubclass(edge_class,absolute_locator):
            coordinate = self.edges[e]['coordinate']
            self.edges[e]['obj'] = edge_class(name,self.nodes[b1]['obj'],coordinate)
        else:
            self.edges[e]['obj'] = edge_class(name,self.nodes[b1]['obj'],self.nodes[b2]['obj'])
    

    def _assemble_edges(self):
        for e in self.edges:
            b1, b2, name = e
            if b1.startswith(self.name+'vb') or b2.startswith(self.name+'vb'):
                pass
            else:
                self._assemble_edge(e)
            
    def assemble_model(self):
        self._assemble_nodes()
        self._assemble_edges()
    
###############################################################################
###############################################################################

class assembly(subsystem):
    
    def __init__(self,name):
        self.name = name
        self.ground = ground()
        self.graph = nx.MultiGraph(name=name)
        self.graph.add_node('ground',obj=self.ground,mirr='ground')
        self.subsystems = {}
        self._virtual_bodies_map = {}
    
    @property
    def nve(self):
        return super().nve +2
    @property
    def virtual_bodies_map(self):
        return self._virtual_bodies_map
    
    def _update_virtual_bodies_map(self,subsystem):
        new_virtuals = subsystem.virtual_bodies
        new_virtuals = zip(new_virtuals,len(new_virtuals)*['ground'])
        self._virtual_bodies_map.update(new_virtuals)
    
    def _replace_nodes(self,v,u):
        nx.relabel_nodes(self.graph,{v:u},copy=False)
        
    def add_subsystem(self,subsystem):
        self.subsystems[subsystem.name] = subsystem
        subsystem_graph = subsystem.selected_variant
        self.graph.add_nodes_from(subsystem_graph.nodes(data=True))
        self.graph.add_edges_from(subsystem_graph.edges(data=True,keys=True))
        self._update_virtual_bodies_map(subsystem)
    
    def assign_virtual_body(self,virtual_node,actual_node):
        virtual_node_1 = virtual_node
        virtual_node_2 = self.nodes[virtual_node]['mirr']
        actual_node_1 = actual_node
        actual_node_2 = self.nodes[actual_node]['mirr']
        self.virtual_bodies_map[virtual_node_1] = actual_node_1
        self.virtual_bodies_map[virtual_node_2] = actual_node_2
    
    def assemble_model(self):
        for v,u in self.virtual_bodies_map.items():
            self._replace_nodes(v,u)
    
    @property
    def configuration_constants(self):
        cons = []
        for e in self.edges(data='obj'):
            cons += e[-1].configuration_constants()
        return cons
    @property
    def numerical_arguments(self):
        args = []
        for e in self.edges(data='obj'):
            args += e[-1].numerical_arguments()
        for n in self.nodes(data='obj'):
            args += n[-1].numerical_arguments()
        return args
    @property
    def q(self):
        return sm.MatrixSymbol('q',self.n,1)
    @property
    def qd(self):
        return sm.MatrixSymbol('qd',self.n,1)
    def map_coordinates(self):
        q = []
        qd = []
        i = 0
        for n in self.nodes(data='obj'):
            q.append(sm.Eq(n[-1].R,self.q[i:i+3,0]))
            q.append(sm.Eq(n[-1].P,self.q[i+3:i+3+4,0]))
            
            qd.append(sm.Eq(n[-1].Rd,self.qd[i:i+3,0]))
            qd.append(sm.Eq(n[-1].Pd,self.qd[i+3:i+3+4,0]))
            
            i+=7
        self.q_maped = q
        self.qd_maped = qd

    
        
    def generate_equations(self):
        
        edgelist = self.edges
        nodelist = self.nodes
        node_index = dict([(n,i) for i,n in enumerate(nodelist)])

        n_nodes = len(nodelist)
        cols = 2*n_nodes
        
        nve = self.nve  # number of constraint vector equations
        
        jacobian = sm.MutableSparseMatrix(nve,cols,None)
        
        equations = sm.MutableSparseMatrix(nve,1,None)
        vel_rhs   = sm.MutableSparseMatrix(nve,1,None)
        acc_rhs   = sm.MutableSparseMatrix(nve,1,None)
        
        row_ind = 0
        for e in edgelist:
            u,v = e[:2]
            try:
                eo  = self.edges[e]['obj'] # joint object
            except KeyError:
                self._assemble_edge(e)
                eo  = self.edges[e]['obj'] # joint object
            
            # tracker of row index based on the current joint type and the history
            # of the loop
            eo_nve = eo.nve+row_ind 
            
            ui = node_index[u]
            vi = node_index[v]
            
            # assigning the joint jacobians to the propper index in the system jacobian
            # on the "constraint vector equations" level.
            jacobian[row_ind:eo_nve,ui*2:ui*2+2] = eo.jacobian_i.blocks
            jacobian[row_ind:eo_nve,vi*2:vi*2+2] = eo.jacobian_j.blocks
            
            equations[row_ind:eo_nve,0] = eo.pos_level_equations.blocks
            vel_rhs[row_ind:eo_nve,0] = eo.vel_level_equations.blocks
            acc_rhs[row_ind:eo_nve,0] = eo.acc_level_equations.blocks
           
            row_ind += eo.nve
        
        
        for i,n in enumerate(nodelist):
            b = self.nodes[n]['obj']
            if isinstance(b,ground):
                jacobian[row_ind:row_ind+2,i*2:i*2+2]    = b.normalized_jacobian.blocks
                equations[row_ind:row_ind+2,0] = b.normalized_pos_equation.blocks
                vel_rhs[row_ind:row_ind+2,0]   = b.normalized_vel_equation.blocks
                acc_rhs[row_ind:row_ind+2,0]   = b.normalized_acc_equation.blocks
            else:
                jacobian[row_ind,i*2+1] = b.normalized_jacobian[1]
                equations[row_ind,0] = b.normalized_pos_equation
                vel_rhs[row_ind,0]   = b.normalized_vel_equation
                acc_rhs[row_ind,0]   = b.normalized_acc_equation
                
            row_ind += b.nve
        
        self.pos_level_equations = equations
        self.vel_level_equations = vel_rhs
        self.acc_level_equations = acc_rhs
        self.jacobian = jacobian
    
    

