
import json
import requests
import get_json
import sanitize_id
import fs 
from fs.osfs import OSFS

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
        self.parent_id = sanitize_id.sanitize_id(parent_id)
        self.parent_url = "https://zenodo.org/api/records/%s" % parent_id
        
        ## get parent json : dict
        parent_json = get_json.get_json(self.parent_url)

        self.parent_json = parent_json

        # get all versions : list
        # get link to all versions of the deposit
        versions_url = parent_json["links"]["versions"]
        versions_json = get_json.get_json(versions_url)

        all_versions = []
        for item in versions_json["hits"]["hits"]:
            all_versions.append(item["id"])
        print(all_versions)

        self.all_versions = all_versions
        # get latest version : str
        latest_version = parent_json["id"]
        self.latest_version = sanitize_id.sanitize_id(latest_version)

      # self.working_verion
        self.working_version = ""
        self.working_url = ""
      # self.working_json
        self.working_json = dict()
    

    def set_working_version(self, zenodo_id: str):
        """set the working version of the data

        Parameters
        ----------
        zenodo_id : str
            zenodo id for the working version of the data.

        virion = deposit()
        virion.set_working_version(virion.latest)

        """
        zenodo_id = sanitize_id.sanitize_id(zenodo_id)
        self.working_version = zenodo_id
        self.working_url = "https://zenodo.org/api/records/%s" % zenodo_id
        self.working_json = get_json.get_json(self.working_url)

    def download_versioned_data(self, zenodo_id = "working", dir = "outputs", recreate = True):
        
        if zenodo_id == "working":
            zenodo_id = self.working_version
            sanitize_id.sanitize_id(zenodo_id) # will throw an error if is empty
        if zenodo_id == "latest":
            ### inform user that the working version is changing?
            zenodo_id = self.latest_version
            self.set_working_version(zenodo_id=zenodo_id)
            sanitize_id.sanitize_id(zenodo_id) # will throw an error if is empty - should be impossible
        
        # create directory with version
        home_fs = OSFS(".")
        home_fs.makedir(dir)    
        download_dir = fs.path.join(dir,zenodo_id)
        home_fs.makedir(download_dir, recreate = recreate)
        # download the files
        dep_files =  self.working_json["files"]
        for item in dep_files:
            file_key = item["key"]
            file_url = item["links"]["self"]
            file_path = fs.path.join(download_dir,file_key)
            r = requests.get(file_url)
            open(file_path, 'wb').write(r.content)

        # return the file path
        return download_dir

        

    
    def load_remote_gzipped_csv(url, encodings=['utf-8', 'windows-1252']):
        response = requests.get(url)
        response.raise_for_status()
        for encoding in encodings:
            try:
                return pd.read_csv(BytesIO(response.content), compression='gzip', encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {url} with encodings: {encodings}")


# home_fs = OSFS(".")
# download_dir = fs.path.join("hello","you")
# home_fs.makedir(download_dir)

# print(home_fs.listdir(path = "/"))

zenodo_dep = deposit()
zenodo_dep.set_working_version(zenodo_dep.latest_version)   
zenodo_dep.download_versioned_data()

#print(versions_json["hits"]["hits"][1].keys())

