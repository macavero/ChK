import pandas as pd
import numpy as np

def load_dataset(merge_metadata=False, update=False):
    densities_path = "../data/channel_data_densities.xlsx"
    df_densities = pd.read_excel(densities_path, sheet_name = 'peak_current_densities')

    metadata_path = "../data/jem_lims_metadata_250421.xlsx"
    df_metadata = pd.read_excel(metadata_path)

    # Human (sorting with Regex)
    pattern_H = r'^H[0-9]\d'
    df_pattern_H = df_densities.copy()
    df_reg_H = df_pattern_H[df_pattern_H['cell'].str.contains(pattern_H, regex=True)]
    df_H= df_reg_H.reset_index(drop=True)

    # NHP (sorting with Regex)
    pattern_QN = r'^QN[0-9]\d'
    df_pattern_QN = df_densities.copy()
    df_reg_QN = df_pattern_QN[df_pattern_QN['cell'].str.contains(pattern_QN, regex=True)]
    df_QN= df_reg_QN.reset_index(drop=True)

    #Mouse
    pattern_m = r'^(H[0-9]\d|QN[0-9]\d)' #exclude all human and NHP
    df_m = df_densities[~df_densities['cell'].str.contains(pattern_m, regex=True)].reset_index(drop=True)


    # Counts per species
    df_m.shape[0] + df_H.shape[0] + df_QN.shape[0] == df_densities.shape[0]
    df_m.shape[0], df_H.shape[0], df_QN.shape[0]

    if update:
        try:
            
            ########################################################################################################
            ###                                             Human                                                ###
            ########################################################################################################
            
            # Human - Use tree_subclass	and tree_cluster for ttype
            h_ttypes_path = '//allen/programs/celltypes/workgroups/rnaseqanalysis/shiny/patch_seq/star/human/human_patchseq_MTG_current/mapping.df.lastmap.csv'
            df_human_ttypes = pd.read_csv(h_ttypes_path) 
            df_human_ttypes_reduced = df_human_ttypes[['cell_name_label', 'tree_subclass', 'tree_cluster', 'tree_class']]

            df_human_ch_tt = pd.merge(left = df_H, left_on = 'cell',
                        right = df_human_ttypes_reduced, right_on = 'cell_name_label', how = 'inner')


            # Merge with ephys data (query from LIMS)
            df_hum_ephys = pd.read_csv('../data/results_human_query.csv')
            df_human_ch_tt_ephys = pd.merge(left = df_human_ch_tt, left_on = 'cell',
                                            right = df_hum_ephys, right_on = 'name', how = 'inner')
            
            if merge_metadata:
                # Merge with metadata
                df_human_ch_tt_ephys_meta = pd.merge(left = df_human_ch_tt_ephys, left_on = 'cell',
                                                right = df_metadata, right_on = 'jem-id_cell_specimen', how = 'inner')
            else:
                df_human_ch_tt_ephys_meta = df_human_ch_tt_ephys.copy() 
                
            # Merge with homology dictionary
            df_dict_hom = pd.read_excel('../data/hodge_MvH_homology_mapping.xlsx')
            df_human = pd.merge(left = df_human_ch_tt_ephys_meta, left_on = 'tree_cluster',
                                right = df_dict_hom, right_on = 'cluster_name', how = 'inner')

            # New col for current ratios
            df_human['nonfast_tot_70_ratio'] = df_human['nonfast_70'] / df_human['tot_70']
            df_human['fast_tot_70_ratio'] = df_human['fast_70'] / df_human['tot_70']


            ########################################################################################################
            ###                                            Mouse WB                                              ###
            ########################################################################################################

            m_ttypes_path = '//allen/programs/celltypes/workgroups/rnaseqanalysis/shiny/patch_seq/star/mouse/mouse_patchseq_WB_current/mapping.df.lastmap.csv'
            df_mouse_tt_WB = pd.read_csv(m_ttypes_path)
            df_mouse_ch_tt_WB = pd.merge(left = df_m, left_on = 'cell',
                                    right = df_mouse_tt_WB, right_on='cell_name', how='inner')

            if merge_metadata:
                # Merge WB with metadata
                df_mouse_ch_tt_WB_meta = pd.merge(left = df_mouse_ch_tt_WB, left_on = 'cell',
                                                right = df_metadata, right_on = 'jem-id_cell_specimen', how = 'inner')
            else:
                df_mouse_ch_tt_WB_meta = df_mouse_ch_tt_WB.copy()

            # Merge WB mouse with ephys data (query from LIMS)
            df_mouse_ephys = pd.read_csv('../data/results_mouse_query.csv')
            df_mouse_WB = pd.merge(left = df_mouse_ch_tt_WB_meta, left_on = 'cell',
                                right = df_mouse_ephys, right_on = 'name', how = 'inner')
            # New col for class
            df_mouse_WB['class'] = df_mouse_WB['best.class_label'].apply(
                lambda x: 'Glutamatergic' if 'Glut' in x else ('GABAergic' if 'GABA' in x else 'Unknown'))
        
            # New col for current ratios WB
            df_mouse_WB['nonfast_tot_70_ratio'] = df_mouse_WB['nonfast_70'] / df_mouse_WB['tot_70']
            df_mouse_WB['fast_tot_70_ratio'] = df_mouse_WB['fast_70'] / df_mouse_WB['tot_70']
            
            
            ########################################################################################################
            ###                                            Mouse VISp                                            ###
            ########################################################################################################
            
        
            df_mouse_tt_VISp = pd.read_csv('../data/mouse_VISp_tax_rsc384.csv')
            df_mouse_tt_VISp['tree_cluster'] = df_mouse_tt_VISp['tree_cluster'].apply(lambda x: x.replace("_", " "))
            
            df_mouse_ch_tt_VISp = pd.merge(left = df_m, left_on = 'cell',
                                        right = df_mouse_tt_VISp, right_on='cell_name_label', how='inner')

            if merge_metadata:
                # Merge VISp with metadata
                df_mouse_ch_tt_VISp_meta = pd.merge(left = df_mouse_ch_tt_VISp, left_on = 'cell',
                                                right = df_metadata, right_on = 'jem-id_cell_specimen', how = 'inner')
            else:
                df_mouse_ch_tt_VISp_meta = df_mouse_ch_tt_VISp.copy()

            # Merge VISp mouse with ephys data (query from LIMS)
            df_mouse_VISp = pd.merge(left = df_mouse_ch_tt_VISp_meta, left_on = 'cell',
                                right = df_mouse_ephys, right_on = 'name', how = 'inner')
            
            # New col for current ratios VISp
            df_mouse_VISp['nonfast_tot_70_ratio'] = df_mouse_VISp['nonfast_70'] / df_mouse_VISp['tot_70']
            df_mouse_VISp['fast_tot_70_ratio'] = df_mouse_VISp['fast_70'] / df_mouse_VISp['tot_70']
            
            
    

            if merge_metadata == False:
                # Create excel file from dataframes - for remote use.
                df_mouse_WB.to_excel(f'../data/mouse_tt_WB_ch_ephys.xlsx', index=False)
                df_mouse_VISp.to_excel(f'../data/mouse_tt_VISp_ch_ephys.xlsx', index=False)
                df_human.to_excel(f'../data/human_tt_ch_ephys.xlsx', index=False)
                print('Data loaded and saved to local files.')
                
                df_human_ch_tt.to_excel(f'../data/human_tt_ch_for_IPFX.xlsx', index=False)
                df_mouse_ch_tt_WB.to_excel(f'../data/mouse_tt_ch_for_IPFX.xlsx', index=False)
            
        except:
            print('Data directory not available. Loading from local files.')
            df_mouse_WB = pd.read_excel('../data/mouse_tt_WB_ch_ephys.xlsx')
            df_mouse_VISp = pd.read_excel('../data/mouse_tt_VISp_ch_ephys.xlsx')
            df_human = pd.read_excel('../data/human_tt_ch_ephys.xlsx')
        
    else:
            print('Files not updated. Loading from local files.')
            df_mouse_WB = pd.read_excel('../data/mouse_tt_WB_ch_ephys.xlsx')
            df_mouse_VISp = pd.read_excel('../data/mouse_tt_VISp_ch_ephys.xlsx')
            df_human = pd.read_excel('../data/human_tt_ch_ephys.xlsx')

    return df_human, df_mouse_WB, df_mouse_VISp, df_m, df_H, df_QN