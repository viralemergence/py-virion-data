
import json
import get_json

class deposit:
    """deposit class object holds deposit attributes
    """
    def __init__(self, parent_id="15643003"):
        """initialize the deposit with a parent id

        Parameters
        ----------
        parent_id : character
             Default value is the parent id for the virion zenodo deposit.
             To find the parent ID, download a JSON representation of the
             deposit (export to json on the webpage or use `export_deposit_metadata`),
             there will be an attribute called parent that looks like
             "https://zenodo.org/api/records/15020049".
             The 8 digit string at the end of the url is the parent id.
        """
        self.parent_id = parent_id
        self.parent_url = "https://zenodo.org/api/records/%s" % parent_id
        
        ## get parent json : dict
        parent_json = get_json(self.parent_url)

        self.parent_json = parent_json

        # get all versions : list
        # get link to all versions of the deposit
        versions_url = parent_json["links"]["versions"]
        versions_json = get_json(versions_url)

        all_versions = []
        for item in versions_json["hits"]["hits"]:
            all_versions.append(item["id"])
        print(all_versions)

        self.all_versions = all_versions
        # get latest version : string
        latest_version = parent_json["id"]
        self.latest_version = latest_version

      # self.working_verion
        self.working_version = ""
        self.working_url = ""
      # self.working_json
        self.working_json = dict()
    

    def set_working_version(self, zenodo_id: string):
        """set the working version of the data

        Parameters
        ----------
        zenodo_id : string
            zenodo id for the working version of the data.

        virion = new deposit()
        virion.set_working_version(virion.latest)

        """
        self.working_version = zenodo_id
        self.working_url = "https://zenodo.org/api/records/%s" % zenodo_id

