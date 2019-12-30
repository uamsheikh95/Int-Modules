# -*- coding: utf-8 -*-

from . import models

class State(models.Model):

	_inherit = 'res.country.state'
    
    # _sql_constraints = [
        # ('state_code_unique', 'unique(code)', 'The code number must me unique'),
    # ]