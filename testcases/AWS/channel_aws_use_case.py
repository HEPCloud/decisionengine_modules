$de_config_dir/config.d/channels/

Sources = [
  {
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

LogicEngine = {
  "ResourceSelection": {
    "Facts": {
      "jobs_present":              "(len(jobs) > 0)",
      "overflow_condition":        "((len(jobs) - local$slots) > params$threshold)",
      "overflow_permitted":        "(params$overflow_permitted)",
      "overflow_hpc_permitted":    "(params$overflow_hpc_permitted)",
      "overflow_cloud_permitted":  "(params$overflow_cloud_permitted)",
      "hpc_sufficient_allocation": "(hpcinfo$hours_available > SUM(jobs$time))",
      "cloud_sufficient_budget":   "(cloudinfo$available_budget > SUM(jobs$estimated_cost))"
    }
    "Rules": [
      "(jobs_present & overflow_permitted &  overflow_condition) -> [use_osg, handle_overflow]",
      "(jobs_present & !(overflow_permitted & overflow_condition)) -> [use_local]",
      "(overflow_hpc_permitted & handle_overflow & hpc_sufficient_allocation) -> use_hpc"
    ]
