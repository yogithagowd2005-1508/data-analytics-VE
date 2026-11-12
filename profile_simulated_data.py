"""
VELOOP REWARDS - SIMULATED DATA PROFILING ENGINE
================================================
Work Package J: J1 Dataset Profiling, J2 Relationship & Referential Integrity Testing,
J3 KPI Calculability Assessment.
"""

import os
import glob
import pandas as pd
import numpy as np

def run_profiling():
    data_dir = 'data'
    files = {
        'Users': 'Users.csv',
        'Task_Activity': 'Task_Activity.csv',
        'Rewards': 'Rewards.csv',
        'Wallet': 'Wallet.csv',
        'Withdrawals': 'Withdrawals.csv',
        'Referrals': 'Referrals.csv',
        'Feature_Events': 'Feature_Events.csv',
        'Messy_Data': 'Messy_Data.csv'
    }

    dfs = {}
    for name, f in files.items():
        dfs[name] = pd.read_csv(os.path.join(data_dir, f))

    print("=====================================================================")
    print("WORK PACKAGE J1: SIMULATED DATASET PROFILING REPORT")
    print("=====================================================================")
    
    profiling_summary = []

    for name, df in dfs.items():
        num_records = len(df)
        num_cols = len(df.columns)
        
        # Primary key candidate (first col ending with id or containing id)
        id_cols = [c for c in df.columns if 'id' in c.lower()]
        pk_col = id_cols[0] if id_cols else df.columns[0]
        unique_ids = df[pk_col].nunique()
        duplicate_pk_count = num_records - unique_ids
        
        # Missing values count across all columns
        missing_total = int(df.isna().sum().sum())
        missing_by_col = df.isna().sum()[df.isna().sum() > 0].to_dict()
        
        # Date columns
        date_cols = [c for c in df.columns if 'time' in c.lower() or 'at' in c.lower() or 'date' in c.lower()]
        date_ranges = {}
        for dc in date_cols:
            valid_dates = pd.to_datetime(df[dc], errors='coerce').dropna()
            if len(valid_dates) > 0:
                date_ranges[dc] = f"{valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}"
            else:
                date_ranges[dc] = "No valid dates parsed"
                
        # Status column distribution
        status_cols = [c for c in df.columns if 'status' in c.lower()]
        status_dist = {}
        for sc in status_cols:
            status_dist[sc] = df[sc].value_counts().to_dict()
            
        # Numeric ranges
        num_cols_list = df.select_dtypes(include=[np.number]).columns.tolist()
        num_ranges = {}
        for nc in num_cols_list:
            num_ranges[nc] = f"min: {df[nc].min()}, max: {df[nc].max()}, mean: {df[nc].mean():.2f}"

        profiling_summary.append({
            'dataset_name': name,
            'records_count': num_records,
            'columns_count': num_cols,
            'pk_candidate': pk_col,
            'unique_ids': unique_ids,
            'duplicate_pk_count': duplicate_pk_count,
            'total_missing_cells': missing_total,
            'missing_breakdown': str(missing_by_col),
            'date_range': str(date_ranges),
            'status_distribution': str(status_dist),
            'numeric_ranges': str(num_ranges)
        })
        
        print(f"\n--- Dataset: {name} ---")
        print(f"Records: {num_records:,} | Columns: {num_cols} | PK: {pk_col} (Unique: {unique_ids:,}, Dups: {duplicate_pk_count})")
        print(f"Missing Values: {missing_total:,}")
        print(f"Date Ranges: {date_ranges}")
        print(f"Status Distribution: {status_dist}")
        print(f"Numeric Ranges: {num_ranges}")

    df_summary = pd.DataFrame(profiling_summary)
    df_summary.to_csv('data/profiling_summary.csv', index=False)

    print("\n=====================================================================")
    print("WORK PACKAGE J2: REFERENTIAL INTEGRITY & RELATIONSHIP TESTING")
    print("=====================================================================")

    users_set = set(dfs['Users']['user_id'])
    
    relationships = [
        ('Task_Activity', 'user_id', 'Users', 'user_id'),
        ('Rewards', 'user_id', 'Users', 'user_id'),
        ('Wallet', 'user_id', 'Users', 'user_id'),
        ('Withdrawals', 'user_id', 'Users', 'user_id'),
        ('Referrals', 'referring_user_id', 'Users', 'user_id'),
        ('Referrals', 'referred_user_id', 'Users', 'user_id'),
        ('Feature_Events', 'user_id', 'Users', 'user_id'),
        ('Rewards', 'task_activity_id', 'Task_Activity', 'task_activity_id'),
        ('Messy_Data', 'user_id', 'Users', 'user_id')
    ]

    rel_results = []
    for child_tbl, child_fk, parent_tbl, parent_pk in relationships:
        child_vals = dfs[child_tbl][child_fk].dropna()
        # filter empty strings
        child_vals = child_vals[child_vals != '']
        parent_vals = set(dfs[parent_tbl][parent_pk].dropna())
        
        orphans = child_vals[~child_vals.isin(parent_vals)]
        orphan_count = len(orphans)
        unique_orphans = orphans.nunique()
        
        status = "PASSED (0 orphans)" if orphan_count == 0 else f"FAILED ({orphan_count} orphan references, {unique_orphans} unique keys)"
        rel_results.append({
            'child_table': child_tbl,
            'foreign_key': child_fk,
            'parent_table': parent_tbl,
            'primary_key': parent_pk,
            'total_tested': len(child_vals),
            'orphan_records': orphan_count,
            'unique_orphans': unique_orphans,
            'integrity_status': status
        })
        print(f"FK Test: {child_tbl}.{child_fk} -> {parent_tbl}.{parent_pk}: {status}")

    df_rel = pd.DataFrame(rel_results)
    df_rel.to_csv('data/referential_integrity_test_results.csv', index=False)

    print("\n=====================================================================")
    print("WORK PACKAGE J3: KPI CALCULABILITY ASSESSMENT")
    print("=====================================================================")
    
    kpi_tests = [
        {
            'kpi_id': 'KPI_USR_01',
            'name': 'Daily Active Users (DAU)',
            'formula': 'COUNT(DISTINCT user_id) per day with qualifying event',
            'calculable': 'YES',
            'tables_used': 'Feature_Events, Task_Activity',
            'notes': 'Can be calculated directly using timestamp and user_id across activity datasets.'
        },
        {
            'kpi_id': 'KPI_ENG_04',
            'name': 'Task Completion Rate',
            'formula': 'COUNT(completed tasks) / COUNT(started tasks)',
            'calculable': 'YES',
            'tables_used': 'Task_Activity',
            'notes': 'Can be calculated via status column in Task_Activity.'
        },
        {
            'kpi_id': 'KPI_WDR_06',
            'name': 'Average Withdrawal Processing Duration',
            'formula': 'AVG(final_timestamp - requested_timestamp)',
            'calculable': 'YES',
            'tables_used': 'Withdrawals',
            'notes': 'Directly computable on completed/rejected records with final_timestamp.'
        },
        {
            'kpi_id': 'KPI_REV_01',
            'name': 'Net Ad Revenue per User (ARPU)',
            'formula': 'SUM(gross_ad_revenue - reward_expense) / Total Users',
            'calculable': 'NO',
            'tables_used': 'Task_Activity (incomplete)',
            'missing_data': 'Gross third-party ad network payout / eCPM cost data is not captured in Task_Activity. Only internal user reward_amount is tracked.',
            'remedy': 'Ingest ad network provider settlement revenue feeds (e.g. AdMob/IronSource API gross earnings postback).'
        },
        {
            'kpi_id': 'KPI_RET_02',
            'name': 'D30 Rolling Retention Rate',
            'formula': 'COUNT(users active on Day 30) / COUNT(users registered on Day 0)',
            'calculable': 'PARTIAL',
            'tables_used': 'Users, Feature_Events',
            'missing_data': 'Calculable only for users whose registration was at least 30 days prior to dataset cutoff.',
            'remedy': 'Implement cohort survival modeling table with maturity window flags.'
        },
        {
            'kpi_id': 'KPI_FRD_01',
            'name': 'Multi-Account Collusion Rate',
            'formula': 'COUNT(users sharing device/IP/bank) / Total Users',
            'calculable': 'NO',
            'tables_used': 'None',
            'missing_data': 'Hardware device fingerprint (IDFV/GAID), IP address hash, and bank account hashes are not present in User or Withdrawal tables.',
            'remedy': 'Add security telemetry tracking payload (device_fingerprint_hash, ip_asn, payment_destination_hash) to Ingestion Gateway.'
        }
    ]
    
    df_kpi_test = pd.DataFrame(kpi_tests)
    df_kpi_test.to_csv('data/kpi_calculability_test.csv', index=False)
    for t in kpi_tests:
        print(f"KPI: {t['name']} | Calculable: {t['calculable']} | Remedy: {t.get('remedy', 'Fully supported')}")

if __name__ == '__main__':
    run_profiling()
