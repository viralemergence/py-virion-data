import requests
import json

def get_json(zenodo_url: str):
    """Fetch a Zenodo API endpoint and return the parsed JSON response.

    Parameters
    ----------
    zenodo_url : str
        Zenodo URL pointing to a JSON object.

    Returns
    -------
    dict
        Parsed JSON response.
    """

    resp = requests.get(zenodo_url)
    out = resp.json()

    return out 
 
# parent_json = get_json("https://zenodo.org/api/records/15643003")

# print(parent_json["id"])

#versions_json = get_json("https://zenodo.org/api/records/15733485/versions")

# print(json.dumps(versions_json["hits"],sort_keys=True, indent=4))
#print(versions_json["hits"]["hits"][1].keys())
