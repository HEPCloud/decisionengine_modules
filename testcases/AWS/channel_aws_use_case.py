$de_config_dir/config.d/channels/

Sources = [
  {
    # Do we put the python module name here (i.e. filename.py) or do we put the classname here?
    "name":    "HTCondor_Job_Q",
    "params":  {
      "schedd_name":   "cmsosgce.fnal.gov",
      "constraint":    "(VO_Name =?= 'CMS')",
      "desired_attrs": ["ProcId", "ClusterId", "VO_Name"],
    }
    "schedule": "5 minute",
  }, {
    "name": "HTCondor_Local_Capacity",
    "params": {
      "collector_name": "cmscollector.fnal.gov",
      "constraint": "(Slot_Type =!= 'Partitionable')",
    "schedule": "5 minute"
  }]

Parameters = ["p_overflow", "p_overflow_threshold", "p_overflow_cloud", "p_overflow_hpc", "p_overflow_osg"]

Transforms: ["osg_requests", "hpc_requests", "CloudRequests"]

common_facts = {
      "jobs_present":              "(len(jobs.index) > 0)",
      "overflow_condition":        "((len(jobs.index) - local['slots']) > params['threshold'])",
      "overflow_permitted":        "(params['overflow_permitted'])",

      "overflow_hpc_permitted":    "(params['overflow_hpc_permitted'])",
      "overflow_cloud_permitted":  "(params['overflow_cloud_permitted'])",
      "hpc_sufficient_allocation": "(hpcinfo['hours_available'] > jobs['time'].sum())",
      "cloud_sufficient_budget":   "(cloudinfo['available_budget'] > sum(['jobs']['estimated_cost']))"

    }

common_rules = {
    [
      "(jobs_present & overflow_permitted &  overflow_condition) -> [use_osg, handle_overflow]",
      "(jobs_present & !(overflow_permitted & overflow_condition)) -> [use_local]",
      "(overflow_hpc_permitted & handle_overflow & hpc_sufficient_allocation) -> use_hpc"
    ]
}

cloud_facts = {
    "good_total_estimated_budget" : "ds['budget'] - ( (match_table[still_good == True]).assign(req_cost=number_to_request * burn_rate)['req_cost'].sum()) > 0",
    "good_total_burn_rate" : "ds['targetburn'] <= (match_table[still_good == True]['burn_rate'].sum())"
}

cloud_rules = {
    [
    ]
}

LogicEngine =
{
    'facts' : common_facts
    "rules" : common_rules
}
