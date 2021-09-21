"""
Compare slots on Nersc and startd
"""
import pandas

from decisionengine.framework.modules import Transform
from decisionengine.framework.modules.Transform import Parameter


@Transform.supports_config(Parameter("entry_nersc_map", type=dict, comment="Maps jobs on NERSC to entry name"))
@Transform.consumes(
    startd_manifests=pandas.DataFrame, Factory_Entries_LCF=pandas.DataFrame, Nersc_Job_Info=pandas.DataFrame
)
@Transform.produces(nersc_userpool_slots_comparison=dict)
class CompareNerscUserpoolSlots(Transform.Transform):
    """
    Transform that consumes nersc slots and userpool slots as input,
    and produces the comparison between them
    """

    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.entry_nersc_map = param_dict["entry_nersc_map"]

    def transform(self, data_block):
        """
        Count the number of slots on startd, calculate the running slots on Nersc, and
        compare the two metrics. Also calculate the relative difference between them.
        """

        self.logger.debug("in CompareNerscUserpoolSlots transform")
        nersc_df = data_block["Nersc_Job_Info"]
        userpool_slots_df = data_block["startd_manifests"]
        factory_entry_df = data_block["Factory_Entries_LCF"]

        # constrain userpool slots with only batch slurm
        userpool_slots_df = userpool_slots_df[userpool_slots_df["GLIDEIN_GridType"] == "batch slurm"]
        userpool_slots_df = userpool_slots_df[(userpool_slots_df["SlotType"] == "Partitionable")]

        results = {}

        # construct mapping of entry_name: #cores per node
        cores_dict = {}

        for _index, row in factory_entry_df.iterrows():
            cores_dict[row["EntryName"]] = int(row["GLIDEIN_CPUS"])

        total_slots_nersc = 0

        for _index, row in nersc_df.iterrows():
            if row["status"] == "R":
                key = row["hostname"] + row["queue"] + row["user"]
                entry_name = self.entry_nersc_map[key]
                if entry_name not in cores_dict:
                    self.logger.info(f"error: entry {entry_name} does NOT exist!")
                else:
                    result_key = "nersc" + "." + row["hostname"] + "." + row["queue"] + "." + row["user"] + ".count"
                    if result_key in results:
                        results[result_key] += cores_dict[entry_name] * int(row["nodes"])
                    else:
                        results[result_key] = cores_dict[entry_name] * int(row["nodes"])
                    total_slots_nersc += cores_dict[entry_name] * int(row["nodes"])

        self.logger.info(f"total number of slots on Nersc = {total_slots_nersc}")

        # pull slot info from User pool ########

        total_slots_userpool = 0
        for _index, row in userpool_slots_df.iterrows():
            total_slots_userpool += int(row["TotalCpus"])

        self.logger.info(f"total number of slots on userpool = {total_slots_userpool}")

        # compute the relative difference between the two metrics ###
        rel_diff = 0.0
        diff = abs(total_slots_userpool - total_slots_nersc)
        if diff != 0:
            more = max(total_slots_nersc, total_slots_userpool)
            rel_diff = diff / more

        self.logger.info(f"diff = {diff:f}, rel diff = {rel_diff:f}")

        # construct the result namespace ############################
        results["nersc.count"] = total_slots_nersc
        results["userpool.count"] = total_slots_userpool
        results["relative_diff"] = rel_diff

        return {"nersc_userpool_slots_comparison": results}


Transform.describe(CompareNerscUserpoolSlots)
