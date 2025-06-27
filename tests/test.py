from py_virion_data.deposit import deposit

def test_deposit():
    virion = deposit()

    # # Download data
    # virion.download_versioned_data(
    #     zenodo_id="latest",  # now explicitly set
    #     dir="outputs",       # safe relative path
    #     recreate=True
    # )

    # Load dataframe directly
    df = virion.get_latest_dataframe("taxonomy_virus")  # will match 'detection.csv.gz'
    print(df.head())


if __name__ == "__main__":
    test_deposit()
    print("Test completed successfully.")