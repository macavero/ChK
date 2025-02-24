import pg8000
import pandas as pd

# Connect database
conn = pg8000.connect(
    host="limsdb2",  
    port=5432,         
    user="limsreader",
    password="limsro",
    database="lims2"
)

try:
    name = input("Enter the name of the query (human, mouse, nhp to save file): ")
    human_query = """
        SELECT s.name, a.name as age, proj.code, err.workflow_state as ephys_QC,
        Err.failed_bad_rs, Err.failed_electrode_0, Err.failed_no_seal,
        Err.electrode_0_pa, Err.seal_gohm, Err.initial_access_resistance_mohm,
        Err.input_resistance_mohm, Err.input_access_resistance_ratio, s.id as donor_id, 
        s.patched_cell_container,
        ef.*
        FROM donors d
        JOIN ages a ON a.id=d.age_id
        JOIN specimens s ON s.donor_id = d.id
        JOIN ephys_roi_results err ON s.ephys_roi_result_id = err.id
        JOIN projects proj ON s.project_id = proj.id
        JOIN ephys_features ef on ef.specimen_id = s.id
        AND proj.code in ('hIVSCC-METc', 'hIVSCC-MET')
    """
    
    mouse_query = """
        SELECT s.name, a.name as age, proj.code, err.workflow_state as ephys_QC,
        Err.failed_bad_rs, Err.failed_electrode_0, Err.failed_no_seal,
        Err.electrode_0_pa, Err.seal_gohm, Err.initial_access_resistance_mohm,
        Err.input_resistance_mohm, Err.input_access_resistance_ratio, s.id as donor_id, 
        s.patched_cell_container,
        ef.*
        FROM donors d
        JOIN ages a ON a.id=d.age_id
        JOIN specimens s ON s.donor_id = d.id
        JOIN ephys_roi_results err ON s.ephys_roi_result_id = err.id
        JOIN projects proj ON s.project_id = proj.id
        JOIN ephys_features ef on ef.specimen_id = s.id
        AND proj.code in ('mIVSCC-MET-R01_LC', 'mIVSCC-MET')
    """

    test_query = """
        SELECT s.name, s.id as specimen_id, proj.code, s.patched_cell_container, err.recording_date,
        err.workflow_state as Ephys_QC, err.storage_directory, ra.failed as RNAamp_fail, ra.rna_amplification_set_id,
        ra.percent_cdna_longer_than_400bp, ra.amplified_quantity_ng, ra.cycles as PCR_cycles
        FROM donors d
        JOIN ages a ON a.id=d.age_id
        LEFT JOIN specimens s ON s.donor_id = d.id
        LEFT JOIN ephys_roi_results err ON s.ephys_roi_result_id = err.id
        LEFT JOIN rna_amplification_inputs rai ON rai.sample_id = s.id
        LEFT JOIN rna_amplifications ra ON ra.id = rai.rna_amplification_id
        LEFT JOIN cell_soma_locations csl ON  csl.specimen_id = s.id
        JOIN projects proj ON s.project_id = proj.id
        AND proj.code in ('mIVSCC-MET', 'mIVSCC-MET-R01_LC') 
    """

    # Execute query
    cursor = conn.cursor()
    cursor.execute(mouse_query)
    
    # Obtaining results
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)

    # Save data
    df.to_csv(f"../data/results_{name}_query.csv", index=False)
    print(f"Data saved to 'results_{name}_query.csv'")

except Exception as e:
    print(f"Error: {e}")

finally:
    cursor.close()
    conn.close()