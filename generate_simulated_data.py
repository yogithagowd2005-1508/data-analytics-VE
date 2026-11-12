"""
VELOOP REWARDS - SIMULATED DATA GENERATION ENGINE
=================================================
MANDATORY COMPLIANCE HEADER:
SIMULATED DATA — CREATED FOR ANALYTICAL TESTING
This dataset is synthetic/simulated for product analytics readiness, data modelling,
data profiling, and quality testing. It does NOT represent actual VELOOP company statistics,
actual earnings, actual withdrawals, or live production performance.

Methodology:
- Deterministic pseudo-random generation with fixed seed (seed=42) for full reproducibility.
- Models 7 interconnected operational entities plus 1 intentionally corrupted "Messy Data" audit sheet.
- Emulates realistic product behavior: drop-offs, pending queues, failed tasks, reversals, and user churn.
"""

import os
import random
import datetime
import pandas as pd
import numpy as np

def generate_datasets():
    random.seed(42)
    np.random.seed(42)

    base_date = datetime.datetime(2026, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(2026, 10, 31, 23, 59, 59)
    total_seconds = int((end_date - base_date).total_seconds())

    def random_timestamp():
        offset = random.randint(0, total_seconds)
        return base_date + datetime.timedelta(seconds=offset)

    # 1. USERS (~1,000 records)
    print("Generating Users (1,000 records)...")
    user_ids = [f"USR_{i:05d}" for i in range(1, 1001)]
    reg_sources = ['organic', 'referral', 'paid_ad', 'partner_promo', 'influencer']
    reg_source_weights = [0.35, 0.25, 0.20, 0.12, 0.08]
    campaigns = ['spring_launch_2026', 'summer_boost', 'refer_a_friend_v1', 'creator_code_special', None]
    campaign_weights = [0.25, 0.20, 0.20, 0.15, 0.20]
    platforms = ['Android', 'iOS', 'Web']
    platform_weights = [0.65, 0.28, 0.07]
    countries = ['US', 'GB', 'IN', 'CA', 'DE', 'PH', 'NG', 'BR', 'ID', 'FR']
    country_weights = [0.30, 0.15, 0.18, 0.08, 0.06, 0.08, 0.05, 0.04, 0.04, 0.02]
    statuses = ['active', 'dormant', 'suspended', 'closed']
    status_weights = [0.68, 0.24, 0.05, 0.03]

    users_data = []
    for uid in user_ids:
        reg_ts = random_timestamp()
        source = random.choices(reg_sources, weights=reg_source_weights)[0]
        camp = random.choices(campaigns, weights=campaign_weights)[0] if source != 'organic' else None
        plat = random.choices(platforms, weights=platform_weights)[0]
        cntry = random.choices(countries, weights=country_weights)[0]
        status = random.choices(statuses, weights=status_weights)[0]
        
        onboarding_done = random.random() < 0.82
        if onboarding_done:
            onb_ts = reg_ts + datetime.timedelta(minutes=random.randint(2, 120))
        else:
            onb_ts = None
            
        last_login_offset = random.randint(0, int((end_date - reg_ts).total_seconds()))
        last_login = reg_ts + datetime.timedelta(seconds=last_login_offset)

        users_data.append({
            'user_id': uid,
            'registration_timestamp': reg_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'registration_source': source,
            'acquisition_campaign': camp if camp else '',
            'device_platform': plat,
            'country_code': cntry,
            'account_status': status,
            'is_onboarding_completed': onboarding_done,
            'onboarding_completed_timestamp': onb_ts.strftime('%Y-%m-%d %H:%M:%S') if onb_ts else '',
            'last_login_timestamp': last_login.strftime('%Y-%m-%d %H:%M:%S')
        })
    df_users = pd.DataFrame(users_data)

    # 2. TASK ACTIVITY (~6,000 records)
    print("Generating Task Activity (6,000 records)...")
    task_types = ['watch_ad', 'survey', 'tap_earn', 'mining', 'offerwall', 'app_install']
    task_type_weights = [0.40, 0.18, 0.20, 0.10, 0.07, 0.05]
    task_catalog = {
        'watch_ad': ('TK_AD_101', 'AdMob Short Video', 15, 'VEs', 'GoogleAdMob'),
        'survey': ('TK_SURV_201', 'Consumer Opinion Survey', 120, 'VEs', 'Pollfish'),
        'tap_earn': ('TK_TAP_301', 'Daily Energy Tap Session', 25, 'VEs', 'InternalEngine'),
        'mining': ('TK_MINE_401', '6-Hour Cloud Hash Claim', 80, 'VEs', 'InternalEngine'),
        'offerwall': ('TK_OFF_501', 'Reach Level 10 in Castle Quest', 450, 'VEs', 'Tapjoy'),
        'app_install': ('TK_APP_601', 'Download & Open FinApp', 250, 'VEs', 'IronSource')
    }
    task_statuses = ['completed', 'failed', 'abandoned', 'pending_validation']
    task_status_weights = [0.72, 0.12, 0.11, 0.05]
    validation_statuses = ['validated', 'rejected', 'pending']

    task_activity_data = []
    active_user_pool = df_users[df_users['account_status'].isin(['active', 'dormant'])]['user_id'].tolist()
    user_reg_map = dict(zip(df_users['user_id'], pd.to_datetime(df_users['registration_timestamp'])))

    for i in range(1, 6001):
        uid = random.choice(active_user_pool)
        user_reg = user_reg_map[uid]
        sec_avail = max(1, int((end_date - user_reg).total_seconds()))
        start_ts = user_reg + datetime.timedelta(seconds=random.randint(0, sec_avail))
        
        ttype = random.choices(task_types, weights=task_type_weights)[0]
        cat_info = task_catalog[ttype]
        status = random.choices(task_statuses, weights=task_status_weights)[0]
        
        duration = random.randint(15, 900)
        completed_ts = start_ts + datetime.timedelta(seconds=duration) if status in ['completed', 'failed', 'pending_validation'] else None
        
        if status == 'completed':
            val_status = 'validated'
            error_reason = ''
        elif status == 'failed':
            val_status = 'rejected'
            error_reason = random.choice(['tracking_timeout', 'anti_bot_check_failed', 'postback_missing', 'user_closed_window'])
        elif status == 'pending_validation':
            val_status = 'pending'
            error_reason = ''
        else: # abandoned
            val_status = 'rejected'
            error_reason = 'user_abandoned'

        task_activity_data.append({
            'task_activity_id': f"TSK_{i:06d}",
            'task_id': cat_info[0],
            'task_type': ttype,
            'feature_category': 'Earning',
            'user_id': uid,
            'started_at': start_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': completed_ts.strftime('%Y-%m-%d %H:%M:%S') if completed_ts else '',
            'status': status,
            'reward_amount': cat_info[2],
            'reward_unit': cat_info[3],
            'validation_status': val_status,
            'partner_provider': cat_info[4],
            'error_reason': error_reason
        })
    df_task_activity = pd.DataFrame(task_activity_data)

    # 3. REWARDS (~5,000 records)
    print("Generating Rewards (5,000 records)...")
    reward_types = ['task_completion', 'daily_login', 'streak_bonus', 'referral_bonus', 'spin_wheel', 'badge_milestone']
    reward_weights = [0.60, 0.15, 0.08, 0.07, 0.06, 0.04]
    reward_statuses = ['credited', 'pending', 'reversed']
    reward_status_weights = [0.93, 0.04, 0.03]

    completed_tasks = df_task_activity[df_task_activity['validation_status'] == 'validated'].to_dict('records')
    random.shuffle(completed_tasks)
    task_idx = 0

    rewards_data = []
    for i in range(1, 5001):
        rtype = random.choices(reward_types, weights=reward_weights)[0]
        r_status = random.choices(reward_statuses, weights=reward_status_weights)[0]
        
        if rtype == 'task_completion' and task_idx < len(completed_tasks):
            t_row = completed_tasks[task_idx]
            task_idx += 1
            uid = t_row['user_id']
            task_ref = t_row['task_activity_id']
            amt = t_row['reward_amount']
            unit = t_row['reward_unit']
            base_ts = datetime.datetime.strptime(t_row['completed_at'], '%Y-%m-%d %H:%M:%S')
            credit_ts = base_ts + datetime.timedelta(seconds=random.randint(1, 30))
        else:
            uid = random.choice(active_user_pool)
            task_ref = ''
            user_reg = user_reg_map[uid]
            sec_avail = max(1, int((end_date - user_reg).total_seconds()))
            credit_ts = user_reg + datetime.timedelta(seconds=random.randint(0, sec_avail))
            if rtype == 'daily_login':
                amt, unit = 20, 'VEs'
            elif rtype == 'streak_bonus':
                amt, unit = 100, 'VEs'
            elif rtype == 'referral_bonus':
                amt, unit = 250, 'VEs'
            elif rtype == 'spin_wheel':
                amt, unit = random.choice([10, 50, 150, 300]), 'VEs'
            else: # badge_milestone
                amt, unit = 500, 'XP'

        correction_id = ''
        if r_status == 'reversed':
            correction_id = f"RWD_{random.randint(1, max(1, i-1)):05d}"

        rewards_data.append({
            'reward_id': f"RWD_{i:05d}",
            'user_id': uid,
            'task_activity_id': task_ref,
            'reward_type': rtype,
            'amount': amt,
            'reward_unit': unit,
            'status': r_status,
            'credited_at': credit_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'ledger_status': 'posted' if r_status == 'credited' else ('reversed' if r_status == 'reversed' else 'pending'),
            'correction_reference_id': correction_id
        })
    df_rewards = pd.DataFrame(rewards_data)

    # 4. WALLET TRANSACTIONS (~3,500 records)
    print("Generating Wallet Transactions (3,500 records)...")
    wallet_types = ['reward_credit', 'withdrawal_debit', 'token_exchange', 'admin_adjustment', 'withdrawal_refund']
    wallet_type_weights = [0.65, 0.22, 0.08, 0.03, 0.02]

    wallet_data = []
    # Use credited rewards as baseline
    credited_rewards = df_rewards[df_rewards['status'] == 'credited'].to_dict('records')
    random.shuffle(credited_rewards)
    rwd_ptr = 0

    for i in range(1, 3501):
        wtype = random.choices(wallet_types, weights=wallet_type_weights)[0]
        
        if wtype == 'reward_credit' and rwd_ptr < len(credited_rewards):
            r_item = credited_rewards[rwd_ptr]
            rwd_ptr += 1
            uid = r_item['user_id']
            amt = float(r_item['amount'])
            unit = r_item['reward_unit']
            ts = r_item['credited_at']
            status = 'completed'
            src = 'reward_engine'
            ref_id = r_item['reward_id']
        elif wtype == 'withdrawal_debit':
            uid = random.choice(active_user_pool)
            amt = -float(random.choice([500, 1000, 2000, 5000]))
            unit = 'VEs'
            u_ts = user_reg_map[uid] + datetime.timedelta(days=random.randint(5, 60))
            ts = min(u_ts, end_date).strftime('%Y-%m-%d %H:%M:%S')
            status = random.choices(['completed', 'pending', 'reversed'], weights=[0.88, 0.08, 0.04])[0]
            src = 'withdrawal_engine'
            ref_id = f"WDR_{random.randint(1, 1200):04d}"
        elif wtype == 'token_exchange':
            uid = random.choice(active_user_pool)
            amt = -float(random.choice([200, 500, 1000]))
            unit = 'VEs'
            u_ts = user_reg_map[uid] + datetime.timedelta(days=random.randint(3, 40))
            ts = min(u_ts, end_date).strftime('%Y-%m-%d %H:%M:%S')
            status = 'completed'
            src = 'exchange_service'
            ref_id = f"EXC_{i:05d}"
        elif wtype == 'admin_adjustment':
            uid = random.choice(active_user_pool)
            amt = float(random.choice([50, -50, 100, -100]))
            unit = 'VEs'
            u_ts = user_reg_map[uid] + datetime.timedelta(days=random.randint(10, 50))
            ts = min(u_ts, end_date).strftime('%Y-%m-%d %H:%M:%S')
            status = 'completed'
            src = 'manual_ops'
            ref_id = f"ADJ_{i:04d}"
        else: # withdrawal_refund
            uid = random.choice(active_user_pool)
            amt = float(random.choice([500, 1000, 2000]))
            unit = 'VEs'
            u_ts = user_reg_map[uid] + datetime.timedelta(days=random.randint(15, 70))
            ts = min(u_ts, end_date).strftime('%Y-%m-%d %H:%M:%S')
            status = 'completed'
            src = 'withdrawal_engine'
            ref_id = f"WDR_{random.randint(1, 1200):04d}"

        wallet_data.append({
            'transaction_id': f"TXN_{i:06d}",
            'user_id': uid,
            'timestamp': ts,
            'transaction_type': wtype,
            'amount': amt,
            'unit': unit,
            'status': status,
            'source': src,
            'reference_id': ref_id,
            'reversal_relationship_id': f"TXN_{random.randint(1, max(1, i-1)):06d}" if status == 'reversed' else ''
        })
    df_wallet = pd.DataFrame(wallet_data)

    # 5. WITHDRAWALS (~1,200 records)
    print("Generating Withdrawals (1,200 records)...")
    wdr_methods = ['PayPal', 'Crypto_USDT', 'GiftCard_Amazon', 'BankTransfer']
    wdr_method_weights = [0.45, 0.28, 0.18, 0.09]
    wdr_statuses = ['completed', 'rejected', 'processing', 'reversed']
    wdr_status_weights = [0.74, 0.14, 0.09, 0.03]
    rejection_reasons = ['KYC_incomplete', 'minimum_threshold_not_met', 'suspected_fraud', 'third_party_provider_error', 'account_mismatch']

    withdrawals_data = []
    for i in range(1, 1201):
        uid = random.choice(active_user_pool)
        user_reg = user_reg_map[uid]
        sec_avail = max(1, int((end_date - user_reg).total_seconds()))
        req_ts = user_reg + datetime.timedelta(seconds=random.randint(0, sec_avail))
        
        method = random.choices(wdr_methods, weights=wdr_method_weights)[0]
        amt = random.choice([500, 1000, 1500, 2000, 3000, 5000, 10000])
        status = random.choices(wdr_statuses, weights=wdr_status_weights)[0]
        
        proc_ts = req_ts + datetime.timedelta(hours=random.randint(1, 24))
        if status == 'completed':
            final_ts = proc_ts + datetime.timedelta(hours=random.randint(2, 48))
            rej_reason = ''
            tx_hash = f"HASH_{random.randint(10000000, 99999999):X}"
        elif status == 'rejected':
            final_ts = proc_ts + datetime.timedelta(hours=random.randint(1, 12))
            rej_reason = random.choice(rejection_reasons)
            tx_hash = ''
        elif status == 'reversed':
            final_ts = proc_ts + datetime.timedelta(hours=random.randint(24, 96))
            rej_reason = 'provider_payout_failed_reversed'
            tx_hash = ''
        else: # processing
            final_ts = None
            rej_reason = ''
            tx_hash = ''

        withdrawals_data.append({
            'withdrawal_id': f"WDR_{i:04d}",
            'user_id': uid,
            'requested_amount': amt,
            'currency_unit': 'VEs',
            'withdrawal_method': method,
            'requested_timestamp': req_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'processing_timestamp': proc_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'final_timestamp': final_ts.strftime('%Y-%m-%d %H:%M:%S') if final_ts else '',
            'status': status,
            'rejection_reason_category': rej_reason,
            'payout_reference_hash': tx_hash,
            'fee_amount': round(amt * 0.02, 2)
        })
    df_withdrawals = pd.DataFrame(withdrawals_data)

    # 6. REFERRALS (~900 records)
    print("Generating Referrals (900 records)...")
    channels = ['WhatsApp', 'Telegram', 'Twitter', 'DirectLink', 'SMS']
    channel_weights = [0.38, 0.28, 0.16, 0.12, 0.06]
    ref_statuses = ['converted', 'activated', 'registered', 'link_created']
    ref_status_weights = [0.42, 0.20, 0.22, 0.16]

    referrals_data = []
    registered_referrals = df_users[df_users['registration_source'] == 'referral']['user_id'].tolist()
    reg_ref_idx = 0

    for i in range(1, 901):
        ref_by = random.choice(active_user_pool)
        create_ts = random_timestamp()
        channel = random.choices(channels, weights=channel_weights)[0]
        r_stat = random.choices(ref_statuses, weights=ref_status_weights)[0]
        
        if r_stat in ['registered', 'activated', 'converted']:
            if reg_ref_idx < len(registered_referrals):
                ref_user = registered_referrals[reg_ref_idx]
                reg_ref_idx += 1
            else:
                ref_user = random.choice(active_user_pool)
            reg_ts = create_ts + datetime.timedelta(hours=random.randint(1, 72))
        else:
            ref_user = ''
            reg_ts = None
            
        if r_stat in ['activated', 'converted'] and reg_ts:
            act_ts = reg_ts + datetime.timedelta(hours=random.randint(1, 48))
        else:
            act_ts = None
            
        conv_flag = (r_stat == 'converted')

        referrals_data.append({
            'referral_id': f"REF_{i:04d}",
            'referring_user_id': ref_by,
            'referred_user_id': ref_user,
            'invite_channel': channel,
            'creation_timestamp': create_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'registration_timestamp': reg_ts.strftime('%Y-%m-%d %H:%M:%S') if reg_ts else '',
            'activation_timestamp': act_ts.strftime('%Y-%m-%d %H:%M:%S') if act_ts else '',
            'status': r_stat,
            'reward_credited_to_referrer': conv_flag,
            'attribution_source': 'campaign_share_sheet'
        })
    df_referrals = pd.DataFrame(referrals_data)

    # 7. FEATURE EVENTS (~12,000 records)
    print("Generating Feature Events (12,000 records)...")
    event_names = [
        'daily_reward_claimed', 'streak_updated', 'spin_started', 'spin_completed',
        'mission_started', 'mission_completed', 'badge_earned', 'wallet_viewed',
        'help_article_viewed', 'onboarding_milestone'
    ]
    event_weights = [0.22, 0.18, 0.14, 0.13, 0.10, 0.08, 0.05, 0.04, 0.03, 0.03]

    feature_events_data = []
    for i in range(1, 12001):
        uid = random.choice(active_user_pool)
        user_reg = user_reg_map[uid]
        sec_avail = max(1, int((end_date - user_reg).total_seconds()))
        ts = user_reg + datetime.timedelta(seconds=random.randint(0, sec_avail))
        
        ename = random.choices(event_names, weights=event_weights)[0]
        session_id = f"SES_{random.randint(100000, 999999)}"
        platform = random.choices(platforms, weights=platform_weights)[0]
        
        feature_events_data.append({
            'event_id': f"EVT_{i:06d}",
            'user_id': uid,
            'session_id': session_id,
            'event_name': ename,
            'feature_domain': 'engagement' if 'streak' in ename or 'daily' in ename or 'spin' in ename else ('gamification' if 'badge' in ename or 'mission' in ename else 'support'),
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'device_platform': platform,
            'status': 'success'
        })
    df_feature_events = pd.DataFrame(feature_events_data)

    # 8. MESSY DATA (~550 records)
    print("Generating Messy Data (550 records with deliberate data quality anomalies)...")
    messy_records = []

    # Issue 1: Duplicate IDs (30 records)
    for i in range(1, 31):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': 'USR_00100',  # duplicate ID reuse
            'timestamp': '2026-05-10 14:22:10',
            'event_name': 'task_completed',
            'amount': 50,
            'status': 'completed',
            'platform': 'Android',
            'category': 'Earning',
            'issue_tag': 'duplicate_id'
        })

    # Issue 2: Missing IDs (null user_id) (25 records)
    for i in range(31, 56):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': None,  # Missing ID
            'timestamp': '2026-05-11 09:12:00',
            'event_name': 'daily_reward_claimed',
            'amount': 20,
            'status': 'completed',
            'platform': 'iOS',
            'category': 'Daily',
            'issue_tag': 'missing_id'
        })

    # Issue 3: Missing Timestamps (25 records)
    for i in range(56, 81):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': None,  # Missing timestamp
            'event_name': 'watch_ad_completed',
            'amount': 15,
            'status': 'completed',
            'platform': 'Android',
            'category': 'Earning',
            'issue_tag': 'missing_timestamp'
        })

    # Issue 4: Malformed Dates (35 records)
    malformed_date_examples = ['2026/31/02', 'INVALID_DATE', '12-11-2026 99:99', '2026-00-15', 'N/A', '9999-99-99']
    for i in range(81, 116):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': random.choice(malformed_date_examples),
            'event_name': 'spin_completed',
            'amount': 100,
            'status': 'completed',
            'platform': 'Android',
            'category': 'Daily',
            'issue_tag': 'malformed_date'
        })

    # Issue 5: Invalid Statuses (30 records)
    invalid_statuses = ['COMPLETEDDDD', 'UNKNOWN_STATUS', 'finished_ok', 'pending_maybe', 'NULL_STATUS']
    for i in range(116, 146):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-06-01 10:00:00',
            'event_name': 'withdrawal_processed',
            'amount': 500,
            'status': random.choice(invalid_statuses),
            'platform': 'Web',
            'category': 'Wallet',
            'issue_tag': 'invalid_status'
        })

    # Issue 6: Inconsistent Capitalization (35 records)
    mixed_caps = ['cOmPLeTeD', 'pEnDiNg', 'ReVeRsEd', 'FAILED_error', 'Success']
    for i in range(146, 181):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-06-05 12:30:00',
            'event_name': 'mission_completed',
            'amount': 50,
            'status': random.choice(mixed_caps),
            'platform': 'iOS',
            'category': 'Missions',
            'issue_tag': 'inconsistent_capitalization'
        })

    # Issue 7: Trailing / Leading Spaces (35 records)
    for i in range(181, 216):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"  USR_{i:05d}  ",  # spaces around ID
            'timestamp': '2026-06-10 15:45:00',
            'event_name': '  watch_ad   ',  # spaces around event name
            'amount': 15,
            'status': ' completed ',
            'platform': ' Android ',
            'category': ' Earning ',
            'issue_tag': 'trailing_spaces'
        })

    # Issue 8: Invalid Numeric Values (string instead of float/int) (30 records)
    invalid_nums = ['one_hundred', 'NaN', '###', 'NULL_NUM', '10.5.2']
    for i in range(216, 246):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-06-15 18:20:00',
            'event_name': 'reward_credited',
            'amount': random.choice(invalid_nums),
            'status': 'completed',
            'platform': 'Android',
            'category': 'Rewards',
            'issue_tag': 'invalid_numeric_value'
        })

    # Issue 9: Negative Values where inappropriate (30 records)
    for i in range(246, 276):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-06-20 08:10:00',
            'event_name': 'withdrawal_requested',
            'amount': -random.randint(100, 5000),  # Negative requested amount
            'status': 'requested',
            'platform': 'Android',
            'category': 'Withdrawals',
            'issue_tag': 'negative_numeric_value'
        })

    # Issue 10: Unexpected Nulls in critical columns (30 records)
    for i in range(276, 306):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-07-01 11:15:00',
            'event_name': None,  # Unexpected null event_name
            'amount': 25,
            'status': 'completed',
            'platform': None,  # Unexpected null platform
            'category': None,
            'issue_tag': 'unexpected_null'
        })

    # Issue 11: Orphan Records (Referencing Non-Existent Users) (45 records)
    for i in range(306, 351):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_999{i%10:02d}",  # non-existent user ID
            'timestamp': '2026-07-05 14:00:00',
            'event_name': 'task_completed',
            'amount': 80,
            'status': 'completed',
            'platform': 'iOS',
            'category': 'Earning',
            'issue_tag': 'orphan_record'
        })

    # Issue 12: Duplicate Events (Same event sent twice within 0-1s) (40 records / 20 pairs)
    for i in range(351, 391, 2):
        ts_dup = f"2026-07-10 16:30:{i%59:02d}"
        for step in [0, 1]:
            messy_records.append({
                'record_id': f"REC_{i+step:04d}",
                'user_id': f"USR_{(i%50)+1:05d}",
                'timestamp': ts_dup,
                'event_name': 'streak_bonus_claimed',
                'amount': 100,
                'status': 'completed',
                'platform': 'Android',
                'category': 'Daily',
                'issue_tag': 'duplicate_event'
            })

    # Issue 13: Inconsistent Naming Standards (40 records)
    variations = ['watch-ad', 'WATCH_ADS', 'WatchAd', 'ad_watch_view', 'watch_video_ad']
    for i in range(391, 431):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-07-15 19:40:00',
            'event_name': random.choice(variations),
            'amount': 15,
            'status': 'completed',
            'platform': 'Android',
            'category': 'Earning',
            'issue_tag': 'inconsistent_naming'
        })

    # Issue 14: Impossible State Transitions / Chronology Violations (40 records)
    for i in range(431, 471):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{i:05d}",
            'timestamp': '2026-08-01 10:00:00',
            'event_name': 'withdrawal_completed_before_request',
            'amount': 1500,
            'status': 'completed_prior_to_request',
            'platform': 'Android',
            'category': 'Withdrawals',
            'issue_tag': 'impossible_state_transition'
        })

    # Additional standard records to round to ~550 (80 clean control records)
    for i in range(471, 551):
        messy_records.append({
            'record_id': f"REC_{i:04d}",
            'user_id': f"USR_{(i%100)+1:05d}",
            'timestamp': '2026-08-05 12:00:00',
            'event_name': 'daily_reward_claimed',
            'amount': 20,
            'status': 'completed',
            'platform': 'Android',
            'category': 'Daily',
            'issue_tag': 'control_clean_record'
        })

    df_messy = pd.DataFrame(messy_records)

    # Save to CSVs
    print("Writing CSV files to data/ ...")
    csv_files = {
        'Users.csv': df_users,
        'Task_Activity.csv': df_task_activity,
        'Rewards.csv': df_rewards,
        'Wallet.csv': df_wallet,
        'Withdrawals.csv': df_withdrawals,
        'Referrals.csv': df_referrals,
        'Feature_Events.csv': df_feature_events,
        'Messy_Data.csv': df_messy
    }
    
    for filename, df in csv_files.items():
        filepath = os.path.join('data', filename)
        df.to_csv(filepath, index=False)
        print(f"Saved {filepath} ({len(df)} records)")

    # Save to master Excel workbook
    excel_path = os.path.join('data', 'VELOOP_Simulated_Datasets.xlsx')
    print(f"Writing master Excel workbook to {excel_path}...")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_users.to_excel(writer, sheet_name='Users', index=False)
        df_task_activity.to_excel(writer, sheet_name='Task Activity', index=False)
        df_rewards.to_excel(writer, sheet_name='Rewards', index=False)
        df_wallet.to_excel(writer, sheet_name='Wallet', index=False)
        df_withdrawals.to_excel(writer, sheet_name='Withdrawals', index=False)
        df_referrals.to_excel(writer, sheet_name='Referrals', index=False)
        df_feature_events.to_excel(writer, sheet_name='Feature Events', index=False)
        df_messy.to_excel(writer, sheet_name='Messy Data', index=False)
    print("Master Excel workbook generated successfully!")

if __name__ == '__main__':
    generate_datasets()
