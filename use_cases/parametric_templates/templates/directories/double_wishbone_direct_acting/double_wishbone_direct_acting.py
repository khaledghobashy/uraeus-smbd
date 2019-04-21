# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 08:18:17 2019

@author: khaled.ghobashy
"""

from source.interfaces.scripting_interfaces import topology

def create():
    global template    
    template = topology(__file__)
    
    # Adding System Bodies
    template.add_body('uca', mirrored=True)
    template.add_body('lca', mirrored=True)
    template.add_body('upright', mirrored=True)
    template.add_body('upper_strut', mirrored=True)
    template.add_body('lower_strut' ,mirrored=True)
    template.add_body('tie_rod', mirrored=True)
    template.add_body('hub', mirrored=True)
    template.add_body('steer', mirrored=True, virtual=True)
    template.add_body('chassis', virtual=True)
    
    # Adding System Joints
    template.add_joint.spherical('uca_upright', 'rbr_uca', 'rbr_upright', mirrored=True)
    template.add_joint.spherical('lca_upright', 'rbr_lca', 'rbr_upright', mirrored=True)
    template.add_joint.spherical('tie_upright', 'rbr_tie_rod', 'rbr_upright', mirrored=True)
    template.add_joint.revolute('uca_chassis', 'rbr_uca', 'vbs_chassis', mirrored=True)
    template.add_joint.revolute('lca_chassis', 'rbr_lca', 'vbs_chassis', mirrored=True)
    template.add_joint.revolute('hub_bearing', 'rbr_upright', 'rbr_hub', mirrored=True)
    template.add_joint.universal('strut_chassis', 'rbr_upper_strut', 'vbs_chassis', mirrored=True)
    template.add_joint.universal('strut_lca', 'rbr_lower_strut', 'rbr_lca', mirrored=True)
    template.add_joint.universal('tie_steering', 'rbr_tie_rod', 'vbr_steer', mirrored=True)
    template.add_joint.cylinderical('strut', 'rbr_upper_strut', 'rbr_lower_strut', mirrored=True)

    # Adding System Forces
    template.add_force.internal_force('strut', 'rbr_upper_strut', 'rbr_lower_strut', mirrored=True)
    
    template.assemble_model()
    template.save()
    template.write_python_code()
    
if __name__ == '__main__':
    create()
else:
    template = topology.reload(__file__)

