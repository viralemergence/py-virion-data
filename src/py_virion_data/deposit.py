
import json
import requests
from py_virion_data import get_json
from py_virion_data import sanitize_id
import fs 
from fs.osfs import OSFS
import pandas as pd
from io import BytesIO

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
        # working files consist of key (file name) and url (url to file on zenodo) 
        self.working_files = dict()
    

    def set_working_version(self, zenodo_id: str):
        """set the working version of the data.
        Downloads and parses the desired zenodo deposit.
        Sets the the working_version, working_url, working_json,
        and working_files attributes.


        Parameters
        ----------
        zenodo_id : str
            zenodo id for the working version of the data.
        
        Examples
        --------
        virion = deposit()
        virion.set_working_version(virion.latest_version)

        """
        zenodo_id = sanitize_id.sanitize_id(zenodo_id)
        self.working_version = zenodo_id
        self.working_url = "https://zenodo.org/api/records/%s" % zenodo_id
        self.working_json = get_json.get_json(self.working_url)
        # add files in a dict
        dep_files =  self.working_json["files"]
        file_dict = dict()
        for item in dep_files:
            file_key = item["key"]
            file_url = item["links"]["self"]
            file_dict[file_key] = file_url
        self.working_files = file_dict
        # add attribution information
        # bibtex
        self.working_bibtex = self.export_metadata(format="bibtex")
        # citation
        self.working_citation = self.get_citation(style = "apa")


    def download_versioned_data(self, zenodo_id = "working", dir = "outputs", recreate = True):
        """Save a particular version of the deposit to disc. 

        Parameters
        ----------
        zenodo_id : str, optional
            Zenodo id for a particular version of the data, by default "working" but also accepts "latest".  
        dir : str, optional
            directory where you would like to save the data, by default "outputs"
        recreate : bool, optional
            Should the downloaded files be recreated (overwritten), by default True

        Returns
        -------
        str
            path to directory with files. Data are stored in `dir/zenodo_id` to preserve the data version.
        """
        
        zenodo_id = self.check_zenodo_id(zenodo_id)

        # setup zenodo items

        dep_url = "https://zenodo.org/api/records/%s" % zenodo_id
        dep_json = get_json.get_json(dep_url)
        # add files in a dict
        dep_files =  dep_json["files"]
        file_dict = dict()
        for item in dep_files:
            file_key = item["key"]
            file_url = item["links"]["self"]
            file_dict[file_key] = file_url
        dep_files = file_dict 

        # create directory with version
        home_fs = OSFS(".")

        download_dir = fs.path.join(dir,zenodo_id)
        
        # if the whole thing is there, and we don't want to re-download, return the directory
        if home_fs.exists(download_dir) & (not recreate):
            return download_dir

        # if dir is not there, make it 
        if not home_fs.exists(dir): 
            home_fs.makedir(dir, recreate = recreate)

        home_fs.makedir(download_dir, recreate = recreate)

        # download the files
        
        for file_key, file_url in dep_files.items():
            file_path = fs.path.join(download_dir,file_key)
            r = requests.get(file_url)
            open(file_path, 'wb').write(r.content)

        # return the file path
        return download_dir
    
    def load_remote_csv_file(self, file_key, compressed=True, encodings=['utf-8', 'windows-1252']):
        """
        Load a remote CSV file (optionally gzipped) from the working files.

        Parameters
        ----------
        file_key : str
            Filename to load from `self.working_files`.
        compressed : bool
            Whether the file is gzip-compressed.
        encodings : list of str
            Fallback encodings to try.

        Returns
        -------
        pandas.DataFrame
        """
        if not self.working_files:
            raise RuntimeError("No working files available. Call set_working_version() first.")
        
        if file_key not in self.working_files:
            raise ValueError(f"File key '{file_key}' not found in working files: {list(self.working_files.keys())}")
        
        url = self.working_files[file_key]
        response = requests.get(url)
        response.raise_for_status()

        for encoding in encodings:
            try:
                return pd.read_csv(
                    BytesIO(response.content),
                    compression='gzip' if compressed else None,
                    encoding=encoding
                )
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {url} with encodings: {encodings}")

    
    def get_latest_dataframe(self, file_key="virion", encodings=['utf-8', 'windows-1252']):
        """
        Load a CSV file (compressed or uncompressed) from the latest Zenodo deposit version.

        This method sets the working version to the latest deposit (if not already set),
        searches for a matching file, determines whether it is gzipped, and loads it.

        Parameters
        ----------
        file_key : str
            Base name of the file to load (e.g., "virion" instead of "virion.csv.gz").
            The method will match the first available file that starts with this prefix.
        encodings : list of str, optional
            List of encodings to try for decoding the file.

        Returns
        -------
        pandas.DataFrame
            The loaded data from the matched CSV file.

        Raises
        ------
        FileNotFoundError
            If no matching file is found.
        """
        self.set_working_version(self.latest_version)

        # Match file by prefix (e.g., "virion" → "virion.csv.gz")
        matches = [k for k in self.working_files if k.startswith(file_key)]
        if not matches:
            raise FileNotFoundError(
                f"No file starting with '{file_key}' found in working files: {list(self.working_files.keys())}"
            )

        matched_key = matches[0]
        is_gzipped = matched_key.endswith(".gz")

        if is_gzipped:
            return self.load_remote_csv_file(file_key=matched_key, encodings=encodings, compressed=True)
        else:
            return self.load_remote_csv_file(file_key=matched_key, encodings=encodings, compressed=False)
    
    def export_metadata(self, format: str, zenodo_id = "working"):
        """Export metadata for a version of the deposit.

        Parameters
        ----------
        format : str
            file format for the metadata. One of "json", "json-ld","csl","datacite-json","datacite-xml", "dublincore","marcxml","bibtex","geojson","dcat-ap","codemeta", "cff"
        zenodo_id : str, optional
            Zenodo id for the version of the data, by default "working". Also accepts "latest". Does not change working version!

        Returns
        -------
        str
            File contents as a text string.

        Raises
        ------
        ValueError
            Checks if format is one of the supported file types.
        
        Examples
        --------
        virion = deposit()
        virion.export_metadata(format = "json-ld", zenodo_id = "latest")
        """
        formats = ["json", "json-ld","csl","datacite-json","datacite-xml", "dublincore","marcxml","bibtex","geojson","dcat-ap","codemeta", "cff"]
        
        if format not in formats:
                raise ValueError(
                    f"format - '{format}' - must be one of '{formats}'"
                    )
        
        zenodo_id = self.check_zenodo_id(zenodo_id)
    
        export_url = f"https://zenodo.org/records/{zenodo_id}/export/{format}"
        resp = requests.get(export_url)
        return resp.text


    def get_citation(self, style: str, zenodo_id = "working"):
        """_summary_

        Parameters
        ----------
        style : str
            A citation style. Must be one of: 
              "havard-cite-them-right",
               "apa",
               "modern-language-association",
               "vancouver",
               "chicago-fullnote-bibliography",
               "ieee"
        zenodo_id : str, optional
            _description_, by default "working" also accepts "latest". Does not change working version!

        Returns
        -------
        str
            Citation in appropriate style

        Raises
        ------
        ValueError
            style must be one of the supported style types
        """

        styles =  ["havard-cite-them-right",
               "apa",
               "modern-language-association",
               "vancouver",
               "chicago-fullnote-bibliography",
               "ieee"]

        if style not in styles:
            raise ValueError(
                    f"style - '{style}' - must be one of '{styles}'"
                    )
        
        zenodo_id = self.check_zenodo_id(zenodo_id)
    
        citation_url = f"https://zenodo.org/api/records/{zenodo_id}?locale=en-US&style={style}"

        headers = {'Accept': 'text/x-bibliography',
                   'Content-type': 'text/x-bibliography'}
        resp = requests.get(url = citation_url, headers = headers)
        return resp.content
    
    def check_zenodo_id(self, zenodo_id:str):
        """Checks if Zenodo ID conforms to a pattern. Also allows a user to pass lastest or working as valid zenodo ids.

        Parameters
        ----------
        zenodo_id : str
            Zenodo id for a version of the data. Can also be "working" or "latest" to the get the working or latest version respectively.

        Returns
        -------
        str
            sanitized zenodo id.
        """
        if zenodo_id == "working":
            zenodo_id = self.working_version
        if zenodo_id == "latest":
            zenodo_id = self.latest_version
        if zenodo_id not in ["latest","working"]:
            zenodo_id = sanitize_id.sanitize_id(zenodo_id)
        return zenodo_id
        


# home_fs = OSFS(".")
# download_dir = fs.path.join("hello","you")
# home_fs.makedir(download_dir)

# print(home_fs.listdir(path = "/"))

# zenodo_dep = deposit()
# zenodo_dep.set_working_version(zenodo_dep.latest_version)
# # print(zenodo_dep.working_files)   
# zenodo_dep.download_versioned_data(recreate=False)
# zenodo_dep.download_versioned_data(zenodo_id=15677843)
# lates_virion  = zenodo_dep.load_remote_gzipped_csv("https://zenodo.org/api/records/15733485/files/virion.csv.gz/content")
# print(len(lates_virion))

#print(versions_json["hits"]["hits"][1].keys())

# virion = deposit()
# json_ld = virion.export_metadata(format = "json-ld", zenodo_id = "latest")
# print(json_ld)

# virion.set_working_version(zenodo_id="15733485")
# print(virion.working_citation)