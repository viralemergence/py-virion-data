import tempfile
import fsspec
import pytest
from py_virion_data.deposit import deposit
from py_virion_data.sanitize_id import sanitize_id

def test_deposit():
    virion = deposit()

    # Download data to temp dir

    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = virion.download_versioned_data(
            zenodo_id="latest",  # now explicitly set
            dir=tmpdir,       # safe relative path
            recreate=False # data should not be there
        )
        
        fs = fsspec.filesystem('file') 
        
        assert len(fs.ls(data_path)) != 0
        
        # test re-downloading
        data_path_redownload = virion.download_versioned_data(
            zenodo_id="latest",  # now explicitly set
            dir=tmpdir,       # safe relative path
            recreate= False # data should NOT be overwritten
        )

        # test downloading version 17460940 to a new folder in tmpdir
        data_path_17460940 = virion.download_versioned_data(
            zenodo_id="17460940",  # now explicitly set
            dir=f"{tmpdir}/new_folder",       # safe relative path
            recreate= False # data should NOT be overwritten
        )

    # Load remote csv file - expect failure no working version set
    with pytest.raises(RuntimeError):
        virion.load_remote_csv_file("virion.csv.gz")
    
    # Load dataframe directly - automatically sets working version to latest
    df = virion.get_latest_dataframe("virion")  # will match 'virion.csv.gz'

    # check that the dataframe has content
    assert len(df) != 0

    # Load remote csv file - expect failure file does not exist
    with pytest.raises(ValueError):
        virion.load_remote_csv_file("birrian.csv.gz") # like virion but for birria

    # Load get_latest_dataframe - expect failure file_key not found
    with pytest.raises(FileNotFoundError):
        virion.get_latest_dataframe("birrian") # like virion but for birria

    # load non-compressed file
    virion.get_latest_dataframe("edgelist")

    # export metadata - expect failure not an acceptable value
    with pytest.raises(ValueError):
        ppt = virion.export_metadata(format = "ppt", zenodo_id = "latest")

    # citation - expect failure not an acceptable value
    with pytest.raises(ValueError):
        citation = virion.get_citation("yipyip")

    #  sanitize id - expect failure not an acceptable value
    with pytest.raises(ValueError):
        bad_id = sanitize_id("Benito")

if __name__ == "__main__":
    test_deposit()
    print("Test completed successfully.")