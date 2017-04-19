$de_config_dir/config.d/channels/

Sources = [
  {
    # Class name to import
    "name":    "HTCondorJobQ",
    # pass the entire params dictionary as the parameter to __init__
    "params":  {
      "schedd_name":   "cmsosgce.fnal.gov",
      "constraint":    "(VO_Name =?= 'CMS')",
      "desired_attrs": ["ProcId", "ClusterId", "VO_Name"],
    }
    # I don't know how to express schedule
    "schedule": "5 minute",
  }, {
    "name": "LocalCapacity",
    "params": {
      "collector_name": "cmscollector.fnal.gov",
      "constraint": "(Slot_Type =!= 'Partitionable')",
    }
    "schedule": "5 minute"
  }, {
    "name": "CloudBudget",
    "params": {
      "budget_file": "some path",
    }
    "schedule": "5 minute"
  }, {
    "name": "ProvisionerResourceList",
    "params": {}
    "schedule": "5 minute"
  }, {
    "name": "HPCAllocation",
    "params": {}
    "schedule": "5 minute"
  }, {
    "name": "AWSSpotPrice",
    "params": {}
    "schedule": "5 minute"
  }]

# These are the parameters that must be copied from the parameter store into the DataBlock
Parameters = ["p_overflow", "p_overflow_threshold", "p_overflow_cloud", "p_overflow_hpc", "p_overflow_osg", "p_target_burn_rate"]

Transforms: [ {
    # Class name to import
    "name": "osg_requests",
    # pass the entire params dictionary as the parameter to __init__
    "params": {}
  },{
    "name": "hpc_requests",
    "params": {}
  },{
    "name": "CloudRequests",
    "params": {}
  },

Publishers: [ {
    "name": "ProvisionerRequests",
    "params": {}
  }, {
    "name": "PublishMonitoring",
    "params": {}
  }
]

common_facts = {
    "jobs_present":              "(len(jobs.index) > 0)",
    "overflow_condition":        "((len(jobs.index) - local_slots) > params['threshold'])",
    "overflow_permitted":        "(params['overflow_permitted'])",
    "overflow_hpc_permitted":    "(params['overflow_hpc_permitted'])",
    "overflow_cloud_permitted":  "(params['overflow_cloud_permitted'])",
    "hpc_sufficient_allocation": "(available_hpc_allocation > jobs['time'].sum())",
    "cloud_sufficient_budget":   "(available_cloud_budget > sum(['jobs']['estimated_cost']))"
}

common_rules = {
    "allow_overflow": {
        "expression": "(jobs_present && overflow_permitted && overflow_condition)",
        "actions": ["use_osg"],
        "facts": ["handle_overflow"],
    },
    "disallow_overflow": {
        "expression": "!handle_overflow",
        "actions": ["use_local"],
        "facts": [],
    },
    "handle_hpc": {
        "expression": "(handle_overflow && overflow_hpc_permitted && hpc_sufficient_allocation)",
        "actions": [""],
        "facts": ["use_hpc"],
    }
    "handle_cloud": {
        "expression": "(handle_overflow && !use_hpc && overflow_cloud_permitted && cloud_sufficient_budget)",
        "actions": [""],
        "facts": ["use_cloud"],
    }
}


cloud_facts = {
    "good_total_estimated_budget" : "available_cloud_budget - ( jobs['estimated_cost'].sum()) > 0",
    "good_total_burn_rate" : "p_target_burn_rate >= (jobs['burn_rate'].sum())"
}

cloud_rules = {
    "publish_cloud": {
        "expression": "use_cloud",
        "actions": ["publish_cloud"],
        "facts": [],
    }
}

LogicEngine = {
    'facts' : [common_facts, cloud_facts]
    "rules" : [common_rules, cloud_rules]
}
