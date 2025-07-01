import re

def sanitize_id(zenodo_id):
    """Check that the zenodo is interger like and do some light cleaning.

    Parameters
    ----------
    zenodo_id : str or int
        zenodo id to clean

    Returns
    -------
    str
        cleaned zenodo id

    Raises
    ------
    ValueError
        raises error for zenodo ids that contain non-digit characters
    """
        
    # force string
    zenodo_id_str = str(zenodo_id)
    # trim whitespace
    zenodo_id_nows = zenodo_id_str.strip()
        
    # check for non-numeric in string
    verify_int =  bool(re.search("^[0-9]+$", zenodo_id_nows))

    if verify_int:
        return zenodo_id_nows
        
    raise ValueError(f"zenodo id - '{zenodo_id}' - must only contain digits")