import requests
import json

def get_json( zenodo_url: str):
    """_summary_

    Parameters
    ----------
    zenodo_id : string
        Zenodo id for a deposit
    zenodo_url : string
        Zenodo url pointing to json object

    Returns
    -------
    dict
        json response
    """

    resp = requests.get(zenodo_url)
    out = resp.json()

    return out 
 
parent_json = get_json("https://zenodo.org/api/records/15643003")

print(parent_json["id"])

#versions_json = get_json("https://zenodo.org/api/records/15733485/versions")

# print(json.dumps(versions_json["hits"],sort_keys=True, indent=4))
#print(versions_json["hits"]["hits"][1].keys())
