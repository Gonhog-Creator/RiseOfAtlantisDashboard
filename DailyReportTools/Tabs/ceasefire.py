import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def format_number(num):
    """Format numbers with abbreviations"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{int(num):,}"

def create_ceasefire_tab(filtered_df):
    """Create the Protected Resources tab with player and resource analysis"""
    
    if not filtered_df.empty:
        st.markdown("### Protected Resources Analysis")
        
        # Look for any report with raw_player_data (comprehensive CSV format)
        comprehensive_data = None
        comprehensive_index = -1
        
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            if 'raw_player_data' in row and row['raw_player_data'] is not None:
                comprehensive_data = row
                comprehensive_index = i
                break
        
        if comprehensive_data is None:
            st.warning("No comprehensive CSV data found. This feature requires comprehensive CSV format.")
            return
        
        latest_data = comprehensive_data
        
        player_data = latest_data['raw_player_data']
        
        # Check for active effects column
        if 'active_effects' not in player_data.columns:
            st.warning("Active effects data not available in current report format.")
            return
        
        # Identify players with any attack prevention effects
        attack_prevention_effects = ['prevent_attacks:1']
        player_data['has_protection'] = player_data['active_effects'].fillna('').astype(str).apply(
            lambda x: any(effect in x for effect in attack_prevention_effects)
        )
        
        protected_players = player_data[player_data['has_protection']].copy()
        
        if protected_players.empty:
            st.info("No players currently have attack prevention effects.")
            return
        
        # Summary statistics
        total_players = len(player_data)
        protected_count = len(protected_players)
        protected_percentage = (protected_count / total_players * 100) if total_players > 0 else 0
        
        # Calculate total protected resources
        resource_columns = ['resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food']
        total_protected = 0
        for col in resource_columns:
            if col in protected_players.columns:
                total_protected += protected_players[col].fillna(0).sum()
        
        # Calculate total resources across all players
        total_resources = 0
        for col in resource_columns:
            if col in player_data.columns:
                total_resources += player_data[col].fillna(0).sum()
        
        # Calculate percentage of protected resources
        protected_resource_percentage = (total_protected / total_resources * 100) if total_resources > 0 else 0
        
        # Display summary metrics (simplified like skins section)
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Players with Protection",
                f"{protected_count:,} ({protected_percentage:.1f}%)" if total_players > 0 else f"{protected_count:,}"
            )
        
        with col2:
            st.metric(
                "Total Protected Resources",
                f"{format_number(total_protected)} ({protected_resource_percentage:.1f}%)"
            )
        
        st.markdown("---")
        
        # Player details table (simplified)
        st.markdown("#### Players with Attack Prevention")
        
        # Prepare player data for display
        display_columns = ['username', 'power']
        available_columns = [col for col in display_columns if col in protected_players.columns]
        
        if available_columns:
            player_table = protected_players[available_columns].copy()
            
            # Sort by power (descending)
            player_table = player_table.sort_values('power', ascending=False)
            
            # Rename columns for better display
            column_rename_map = {
                'username': 'Player Name',
                'power': 'Power'
            }
            
            player_table = player_table.rename(columns=column_rename_map)
            
            # Format power column
            if 'Power' in player_table.columns:
                player_table['Power'] = player_table['Power'].apply(lambda x: f"{x:,}" if pd.notna(x) else '0')
            
            st.dataframe(player_table, use_container_width=True, hide_index=True)
    
    else:
        st.info("No data available for protected resources analysis.")
