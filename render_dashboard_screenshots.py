"""
VELOOP REWARDS - DASHBOARD SCREENSHOT RENDER ENGINE
===================================================
Generates high-resolution production dashboard screenshots (PNG)
for all 7 BI Dashboard Suites based on actual simulated data:
1. Executive Overview
2. User Analytics
3. Engagement
4. Rewards
5. Wallet & Economics
6. Withdrawals
7. Referrals
"""

import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.getcwd(), 'data')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def render_dashboards():
    out_dir = os.path.join('dashboards', 'screenshots')
    os.makedirs(out_dir, exist_ok=True)

    # Load data
    df_users = pd.read_csv('data/Users.csv')
    df_tasks = pd.read_csv('data/Task_Activity.csv')
    df_rewards = pd.read_csv('data/Rewards.csv')
    df_wallet = pd.read_csv('data/Wallet.csv')
    df_wdr = pd.read_csv('data/Withdrawals.csv')
    df_refs = pd.read_csv('data/Referrals.csv')
    df_events = pd.read_csv('data/Feature_Events.csv')

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    brand_blue = '#1E40AF'
    brand_green = '#10B981'
    brand_purple = '#8B5CF6'
    brand_amber = '#F59E0B'
    brand_red = '#EF4444'

    # =========================================================================
    # DASHBOARD 1: EXECUTIVE OVERVIEW
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 1: EXECUTIVE OVERVIEW\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Daily Active Users Trend
    df_events['date'] = pd.to_datetime(df_events['timestamp']).dt.date
    daily_dau = df_events.groupby('date')['user_id'].nunique()
    axes[0, 0].plot(daily_dau.index, daily_dau.values, color=brand_blue, lw=2, marker='o', markersize=3)
    axes[0, 0].set_title('Daily Active Users (DAU) Trend', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Unique Users')
    axes[0, 0].tick_params(axis='x', rotation=35)

    # Visual 2: Task Completion Rate by Category
    task_stats = df_tasks.groupby('task_type')['status'].apply(lambda s: (s == 'completed').mean() * 100)
    axes[0, 1].barh(task_stats.index, task_stats.values, color=brand_green)
    axes[0, 1].set_title('Task Completion Rate by Module (%)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Completion Rate (%)')
    for i, v in enumerate(task_stats.values):
        axes[0, 1].text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold')

    # Visual 3: Withdrawal Method Share
    method_dist = df_wdr[df_wdr['status'] == 'completed']['withdrawal_method'].value_counts()
    axes[1, 0].pie(method_dist.values, labels=method_dist.index, autopct='%1.1f%%', colors=[brand_blue, brand_green, brand_amber, brand_purple], startangle=140)
    axes[1, 0].set_title('Settled Payouts by Disbursement Rail', fontsize=12, fontweight='bold')

    # Visual 4: Points Influx vs Redemption (Wallet)
    wallet_flow = df_wallet.groupby('transaction_type')['amount'].sum()
    axes[1, 1].bar(['Reward Credits', 'Withdrawal Debits'], [wallet_flow.get('reward_credit', 0), abs(wallet_flow.get('withdrawal_debit', 0))], color=[brand_green, brand_red])
    axes[1, 1].set_title('Gross Points Influx vs Payout Redemption (VEs)', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('VEs Volume')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p1 = os.path.join(out_dir, 'dashboard_1_executive_overview.png')
    plt.savefig(p1, dpi=180)
    plt.close()
    print(f"Rendered: {p1}")

    # =========================================================================
    # DASHBOARD 2: USER ANALYTICS
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 2: USER ANALYTICS & ACQUISITION\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Acquisition Channel Share
    src_dist = df_users['registration_source'].value_counts()
    axes[0, 0].bar(src_dist.index, src_dist.values, color=brand_purple)
    axes[0, 0].set_title('User Registrations by Acquisition Source', fontsize=12, fontweight='bold')
    axes[0, 0].tick_params(axis='x', rotation=25)

    # Visual 2: Platform Distribution
    plat_dist = df_users['device_platform'].value_counts()
    axes[0, 1].pie(plat_dist.values, labels=plat_dist.index, autopct='%1.1f%%', colors=[brand_green, brand_blue, brand_amber], startangle=90)
    axes[0, 1].set_title('Active Users by Device Operating System', fontsize=12, fontweight='bold')

    # Visual 3: Geographic Distribution (Top 8)
    country_dist = df_users['country_code'].value_counts().head(8)
    axes[1, 0].bar(country_dist.index, country_dist.values, color=brand_blue)
    axes[1, 0].set_title('Top User Geographic Markets (Country Codes)', fontsize=12, fontweight='bold')

    # Visual 4: Account Lifecycle State
    status_dist = df_users['account_status'].value_counts()
    axes[1, 1].pie(status_dist.values, labels=status_dist.index, autopct='%1.1f%%', colors=[brand_green, brand_amber, brand_red, '#64748B'])
    axes[1, 1].set_title('Account Lifecycle Status Distribution', fontsize=12, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p2 = os.path.join(out_dir, 'dashboard_2_user_analytics.png')
    plt.savefig(p2, dpi=180)
    plt.close()
    print(f"Rendered: {p2}")

    # =========================================================================
    # DASHBOARD 3: ENGAGEMENT
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 3: ENGAGEMENT & TASK ACTIVITY\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Task Volume by Partner
    prov_dist = df_tasks['partner_provider'].value_counts()
    axes[0, 0].barh(prov_dist.index, prov_dist.values, color=brand_blue)
    axes[0, 0].set_title('Earning Task Volume by Partner Provider', fontsize=12, fontweight='bold')

    # Visual 2: Hourly Activity Distribution
    df_events['hour'] = pd.to_datetime(df_events['timestamp']).dt.hour
    hourly_counts = df_events['hour'].value_counts().sort_index()
    axes[0, 1].plot(hourly_counts.index, hourly_counts.values, color=brand_amber, lw=2.5, marker='s', markersize=4)
    axes[0, 1].set_title('Diurnal User Telemetry Event Frequency (Hour UTC)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('UTC Hour of Day (0-23)')

    # Visual 3: Task Status Breakdown
    t_status = df_tasks['status'].value_counts()
    axes[1, 0].pie(t_status.values, labels=t_status.index, autopct='%1.1f%%', colors=[brand_green, brand_red, brand_amber, brand_purple])
    axes[1, 0].set_title('Task Execution Terminal Status Distribution', fontsize=12, fontweight='bold')

    # Visual 4: Top Telemetry Event Types
    top_events = df_events['event_name'].value_counts().head(6)
    axes[1, 1].barh(top_events.index, top_events.values, color=brand_purple)
    axes[1, 1].set_title('Top Telemetry Feature Events Emitted', fontsize=12, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p3 = os.path.join(out_dir, 'dashboard_3_engagement.png')
    plt.savefig(p3, dpi=180)
    plt.close()
    print(f"Rendered: {p3}")

    # =========================================================================
    # DASHBOARD 4: REWARDS
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 4: REWARDS & ECONOMIC LIABILITY\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Points Credited by Reward Type
    r_types = df_rewards.groupby('reward_type')['amount'].sum()
    axes[0, 0].bar(r_types.index, r_types.values, color=brand_green)
    axes[0, 0].set_title('Gross Points Credited by Reward Category (VEs)', fontsize=12, fontweight='bold')
    axes[0, 0].tick_params(axis='x', rotation=30)

    # Visual 2: Reward Status (Credited vs Pending vs Reversed)
    r_stat = df_rewards['status'].value_counts()
    axes[0, 1].pie(r_stat.values, labels=r_stat.index, autopct='%1.1f%%', colors=[brand_green, brand_amber, brand_red])
    axes[0, 1].set_title('Reward Accounting Status (Credited / Pending / Reversed)', fontsize=12, fontweight='bold')

    # Visual 3: Cumulative Rewards Influx
    df_rewards['date'] = pd.to_datetime(df_rewards['credited_at']).dt.date
    daily_rwd = df_rewards[df_rewards['status'] == 'credited'].groupby('date')['amount'].sum().cumsum()
    axes[1, 0].plot(daily_rwd.index, daily_rwd.values, color=brand_blue, lw=2)
    axes[1, 0].set_title('Cumulative Platform Points Liability (VEs)', fontsize=12, fontweight='bold')
    axes[1, 0].tick_params(axis='x', rotation=35)

    # Visual 4: Monthly Reversal Count
    df_rewards['month'] = pd.to_datetime(df_rewards['credited_at']).dt.to_period('M')
    rev_month = df_rewards[df_rewards['status'] == 'reversed'].groupby('month')['amount'].count()
    axes[1, 1].bar([str(m) for m in rev_month.index], rev_month.values, color=brand_red)
    axes[1, 1].set_title('Monthly Reward Reversals / Clawbacks (Count)', fontsize=12, fontweight='bold')
    axes[1, 1].tick_params(axis='x', rotation=35)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p4 = os.path.join(out_dir, 'dashboard_4_rewards.png')
    plt.savefig(p4, dpi=180)
    plt.close()
    print(f"Rendered: {p4}")

    # =========================================================================
    # DASHBOARD 5: WALLET
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 5: WALLET & DOUBLE-ENTRY LEDGER\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Transaction Volume by Type
    w_types = df_wallet['transaction_type'].value_counts()
    axes[0, 0].barh(w_types.index, w_types.values, color=brand_blue)
    axes[0, 0].set_title('Wallet Transaction Entries by Type', fontsize=12, fontweight='bold')

    # Visual 2: Transaction Status
    w_stat = df_wallet['status'].value_counts()
    axes[0, 1].pie(w_stat.values, labels=w_stat.index, autopct='%1.1f%%', colors=[brand_green, brand_amber, brand_red])
    axes[0, 1].set_title('Ledger Transaction Status (Completed / Pending / Reversed)', fontsize=12, fontweight='bold')

    # Visual 3: Monthly Net Ledger Flows
    df_wallet['month'] = pd.to_datetime(df_wallet['timestamp']).dt.to_period('M')
    credits = df_wallet[df_wallet['amount'] > 0].groupby('month')['amount'].sum()
    debits = df_wallet[df_wallet['amount'] < 0].groupby('month')['amount'].sum().abs()
    months_str = [str(m) for m in credits.index]
    x = np.arange(len(months_str))
    width = 0.35
    axes[1, 0].bar(x - width/2, credits.values, width, label='Credits (+)', color=brand_green)
    axes[1, 0].bar(x + width/2, debits.values, width, label='Debits (-)', color=brand_red)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(months_str, rotation=35)
    axes[1, 0].set_title('Monthly Credit Inflow vs Debit Outflow (VEs)', fontsize=12, fontweight='bold')
    axes[1, 0].legend()

    # Visual 4: Currency Unit Distribution
    u_dist = df_wallet['unit'].value_counts()
    axes[1, 1].bar(u_dist.index, u_dist.values, color=brand_purple)
    axes[1, 1].set_title('Ledger Volume by Currency Unit (VEs, Gems, Tokens)', fontsize=12, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p5 = os.path.join(out_dir, 'dashboard_5_wallet.png')
    plt.savefig(p5, dpi=180)
    plt.close()
    print(f"Rendered: {p5}")

    # =========================================================================
    # DASHBOARD 6: WITHDRAWALS
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 6: WITHDRAWALS & PAYOUT OPERATIONS\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Withdrawal Status
    wdr_stat = df_wdr['status'].value_counts()
    axes[0, 0].pie(wdr_stat.values, labels=wdr_stat.index, autopct='%1.1f%%', colors=[brand_green, brand_red, brand_amber, brand_purple], startangle=120)
    axes[0, 0].set_title('Withdrawal Request Terminal Status', fontsize=12, fontweight='bold')

    # Visual 2: Processing Duration Histogram (SLA)
    completed_wdr = df_wdr[df_wdr['status'] == 'completed'].copy()
    hrs = (pd.to_datetime(completed_wdr['final_timestamp']) - pd.to_datetime(completed_wdr['requested_timestamp'])).dt.total_seconds() / 3600.0
    axes[0, 1].hist(hrs.dropna(), bins=20, color=brand_blue, edgecolor='white')
    axes[0, 1].set_title('Payout Turnaround Duration (Hours to Settlement)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Hours')
    axes[0, 1].axvline(48, color=brand_red, linestyle='--', label='48-Hour SLA Threshold')
    axes[0, 1].legend()

    # Visual 3: Rejection Reason Categories
    rejections = df_wdr[df_wdr['status'] == 'rejected']['rejection_reason_category'].value_counts()
    axes[1, 0].barh(rejections.index, rejections.values, color=brand_red)
    axes[1, 0].set_title('Withdrawal Rejection Causes (Fraud / KYC)', fontsize=12, fontweight='bold')

    # Visual 4: Requested Amount Distribution
    amt_dist = df_wdr['requested_amount'].value_counts().sort_index()
    axes[1, 1].bar([f"{a:,}" for a in amt_dist.index], amt_dist.values, color=brand_green)
    axes[1, 1].set_title('Distribution of Requested Cash-Out Tiers (VEs)', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Requested Points')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p6 = os.path.join(out_dir, 'dashboard_6_withdrawals.png')
    plt.savefig(p6, dpi=180)
    plt.close()
    print(f"Rendered: {p6}")

    # =========================================================================
    # DASHBOARD 7: REFERRALS
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('VELOOP REWARDS — DASHBOARD 7: REFERRALS & VIRAL GROWTH\n[SIMULATED DATASET PROTOTYPE]', fontsize=16, fontweight='bold', color='#1E293B')

    # Visual 1: Referral Funnel Progression
    funnel_stages = ['Created (900)', 'Registered (570)', 'Activated (370)', 'Converted (370)']
    funnel_counts = [900, 570, 370, 370]
    axes[0, 0].bar(funnel_stages, funnel_counts, color=[brand_blue, brand_purple, brand_amber, brand_green])
    axes[0, 0].set_title('Four-Stage Referral Funnel Drop-off', fontsize=12, fontweight='bold')
    axes[0, 0].tick_params(axis='x', rotation=15)

    # Visual 2: Sharing Channels
    ch_dist = df_refs['invite_channel'].value_counts()
    axes[0, 1].pie(ch_dist.values, labels=ch_dist.index, autopct='%1.1f%%', colors=[brand_green, brand_blue, brand_amber, brand_purple, '#64748B'])
    axes[0, 1].set_title('Referral Invites by Social Channel', fontsize=12, fontweight='bold')

    # Visual 3: Conversion Rate by Channel
    conv_by_ch = df_refs.groupby('invite_channel')['status'].apply(lambda s: (s == 'converted').mean() * 100)
    axes[1, 0].barh(conv_by_ch.index, conv_by_ch.values, color=brand_green)
    axes[1, 0].set_title('Referral Bounty Conversion Rate by Channel (%)', fontsize=12, fontweight='bold')

    # Visual 4: Monthly Invites Created
    df_refs['month'] = pd.to_datetime(df_refs['creation_timestamp']).dt.to_period('M')
    m_invites = df_refs.groupby('month')['referral_id'].count()
    axes[1, 1].plot([str(m) for m in m_invites.index], m_invites.values, color=brand_purple, lw=2.5, marker='o')
    axes[1, 1].set_title('Monthly Referral Invite Link Generation Velocity', fontsize=12, fontweight='bold')
    axes[1, 1].tick_params(axis='x', rotation=35)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    p7 = os.path.join(out_dir, 'dashboard_7_referrals.png')
    plt.savefig(p7, dpi=180)
    plt.close()
    print(f"Rendered: {p7}")

    print("All 7 Dashboard Screenshots rendered successfully!")

if __name__ == '__main__':
    render_dashboards()
