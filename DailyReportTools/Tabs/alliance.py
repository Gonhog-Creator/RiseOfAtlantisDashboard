import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

def format_number(num):
    """Format numbers with abbreviations"""
    if pd.isna(num):
        return "N/A"
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{int(num):,}"

def format_change(change):
    """Format daily change with sign"""
    if pd.isna(change):
        return "N/A"
    sign = "+" if change >= 0 else ""
    return f"{sign}{format_number(change)}"

def load_favorite_alliances():
    """Load favorite alliances from file"""
    favorites_file = "favorite_alliances.json"
    if os.path.exists(favorites_file):
        try:
            with open(favorites_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorite_alliances(favorites):
    """Save favorite alliances to file"""
    favorites_file = "favorite_alliances.json"
    try:
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f)
    except:
        pass

def calculate_alliance_stats(player_df):
    """Calculate alliance statistics from player data"""
    if 'alliance_name' not in player_df.columns:
        return None
    
    alliance_stats = {}
    
    for alliance_name in player_df['alliance_name'].unique():
        if pd.isna(alliance_name):
            continue
            
        alliance_players = player_df[player_df['alliance_name'] == alliance_name]
        
        # Calculate totals
        total_members = len(alliance_players)
        total_power = alliance_players['power'].fillna(0).sum()
        
        # Calculate total troops - parse from troops_json for each alliance member
        total_troops = 0
        if 'troops_json' in alliance_players.columns:
            for _, player in alliance_players.iterrows():
                if pd.notna(player['troops_json']):
                    try:
                        troops_dict = json.loads(player['troops_json'])
                        for troop_name, count in troops_dict.items():
                            # Skip string fields
                            if isinstance(count, str):
                                continue
                            if hasattr(count, 'item'):
                                numeric_count = count.item()
                            else:
                                numeric_count = count
                            if isinstance(numeric_count, (int, float)) and not pd.isna(numeric_count):
                                total_troops += numeric_count
                    except:
                        continue
        elif 'troops' in alliance_players.columns:
            total_troops = alliance_players['troops'].fillna(0).sum()
        elif 'defending_troops' in alliance_players.columns:
            total_troops = alliance_players['defending_troops'].fillna(0).sum()
        
        # Calculate total resources
        resource_columns = ['resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food']
        total_resources = {}
        for col in resource_columns:
            if col in alliance_players.columns:
                total_resources[col] = alliance_players[col].fillna(0).sum()
        
        alliance_stats[alliance_name] = {
            'total_members': total_members,
            'total_power': total_power,
            'total_troops': total_troops,
            'total_resources': total_resources
        }
    
    return alliance_stats

def create_alliance_tab(filtered_df):
    """Create the Alliance tab with alliance analytics"""
    
    if not filtered_df.empty:
        st.markdown("### Alliance Analytics")
        
        # Find the latest data with comprehensive CSV format
        latest_data = None
        for i in range(len(filtered_df) - 1, -1, -1):
            data = filtered_df.iloc[i]
            if 'raw_player_data' in data and data['raw_player_data'] is not None:
                latest_data = data
                break
        
        if latest_data is None:
            st.warning("No comprehensive CSV data found. This feature requires comprehensive CSV format.")
            return
        
        player_df = latest_data['raw_player_data']
        
        if 'alliance_name' not in player_df.columns:
            st.warning("Alliance data not available in current report format.")
            return
        
        # Create a cache key based on the data source (date + player count)
        cache_key = f"alliance_stats_{latest_data.get('date', 'unknown')}_{len(player_df)}"
        
        # Check if we have cached stats for this data
        if 'alliance_stats_cache' in st.session_state and st.session_state['alliance_stats_cache']['key'] == cache_key:
            current_stats = st.session_state['alliance_stats_cache']['stats']
        else:
            # Calculate alliance statistics for current data
            current_stats = calculate_alliance_stats(player_df)
            # Cache the results
            st.session_state['alliance_stats_cache'] = {
                'key': cache_key,
                'stats': current_stats
            }
        
        if not current_stats:
            st.warning("No alliance data found.")
            return
        
        # Calculate alliance statistics for previous day (for daily gains)
        previous_stats = None
        for i in range(len(filtered_df) - 2, -1, -1):
            data = filtered_df.iloc[i]
            if 'raw_player_data' in data and data['raw_player_data'] is not None:
                previous_player_df = data['raw_player_data']
                previous_stats = calculate_alliance_stats(previous_player_df)
                break
        
        # Initialize favorite alliances from file
        if 'favorite_alliances' not in st.session_state:
            st.session_state['favorite_alliances'] = load_favorite_alliances()
        
        # Create alliance selection dropdown with favorites at top
        alliance_names = sorted(current_stats.keys())
        
        # Prepend favorites to the dropdown list with star prefix
        dropdown_options = []
        for fav in st.session_state['favorite_alliances']:
            if fav in alliance_names:
                dropdown_options.append(f"⭐ {fav}")
        
        # Add remaining alliances
        for alliance in alliance_names:
            if alliance not in st.session_state['favorite_alliances']:
                dropdown_options.append(alliance)
        
        selected_alliance_display = st.selectbox(
            "Select an Alliance:",
            options=dropdown_options,
            index=0 if dropdown_options else None
        )
        
        # Remove star prefix to get actual alliance name
        if selected_alliance_display:
            selected_alliance = selected_alliance_display.replace("⭐ ", "") if selected_alliance_display.startswith("⭐ ") else selected_alliance_display
        else:
            selected_alliance = None
        
        if selected_alliance:
            current_data = current_stats[selected_alliance]
            
            # Add to favorites button
            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.markdown(f"#### {selected_alliance}")
            with col_right:
                is_favorited = selected_alliance in st.session_state['favorite_alliances']
                if is_favorited:
                    if st.button("⭐ Remove", key="toggle_fav"):
                        st.session_state['favorite_alliances'].remove(selected_alliance)
                        save_favorite_alliances(st.session_state['favorite_alliances'])
                        st.success(f"Removed {selected_alliance} from favorites")
                else:
                    if st.button("⭐ Add", key="toggle_fav"):
                        if len(st.session_state['favorite_alliances']) < 5:
                            st.session_state['favorite_alliances'].append(selected_alliance)
                            save_favorite_alliances(st.session_state['favorite_alliances'])
                            st.success(f"Added {selected_alliance} to favorites")
                        else:
                            st.warning("Maximum 5 favorites allowed")
            
            # Calculate daily gains if previous data exists
            daily_gains = {}
            if previous_stats and selected_alliance in previous_stats:
                prev_data = previous_stats[selected_alliance]
                daily_gains['members'] = current_data['total_members'] - prev_data['total_members']
                daily_gains['power'] = current_data['total_power'] - prev_data['total_power']
                daily_gains['troops'] = current_data['total_troops'] - prev_data['total_troops']
                
                for resource in current_data['total_resources']:
                    daily_gains[resource] = current_data['total_resources'][resource] - prev_data['total_resources'].get(resource, 0)
            
            # Display alliance name
            st.markdown(f"#### {selected_alliance}")
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Members",
                    f"{current_data['total_members']:,}",
                    delta=format_change(daily_gains.get('members', 0)) if daily_gains else None
                )
            
            with col2:
                st.metric(
                    "Total Power",
                    format_number(current_data['total_power']),
                    delta=format_change(daily_gains.get('power', 0)) if daily_gains else None
                )
            
            with col3:
                st.metric(
                    "Total Troops",
                    format_number(current_data['total_troops']),
                    delta=format_change(daily_gains.get('troops', 0)) if daily_gains else None
                )
            
            st.markdown("---")
            st.markdown("#### Total Resources")
            
            # Display resource metrics
            resource_cols = st.columns(5)
            resource_names = ['resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food']
            resource_display_names = ['Gold', 'Lumber', 'Stone', 'Metal', 'Food']
            
            for i, (resource, display_name) in enumerate(zip(resource_names, resource_display_names)):
                if resource in current_data['total_resources']:
                    with resource_cols[i]:
                        st.metric(
                            display_name,
                            format_number(current_data['total_resources'][resource]),
                            delta=format_change(daily_gains.get(resource, 0)) if daily_gains else None
                        )
            
            st.markdown("---")
            
            # Show alliance member list
            st.markdown(f"#### Alliance Members ({current_data['total_members']})")
            
            alliance_members = player_df[player_df['alliance_name'] == selected_alliance].copy()
            
            # Prepare member data for display
            display_columns = ['username', 'power', 'resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food']
            available_columns = [col for col in display_columns if col in alliance_members.columns]
            
            if available_columns:
                member_table = alliance_members[available_columns].copy()
                
                # Sort by power (descending)
                member_table = member_table.sort_values('power', ascending=False)
                
                # Rename columns for better display
                column_rename_map = {
                    'username': 'Player Name',
                    'power': 'Power',
                    'resource_gold': 'Gold',
                    'resource_lumber': 'Lumber',
                    'resource_stone': 'Stone',
                    'resource_metal': 'Metal',
                    'resource_food': 'Food'
                }
                
                member_table = member_table.rename(columns=column_rename_map)
                
                # Format power and resource columns
                if 'Power' in member_table.columns:
                    member_table['Power'] = member_table['Power'].apply(lambda x: f"{x:,}" if pd.notna(x) else '0')
                
                for resource in ['Gold', 'Lumber', 'Stone', 'Metal', 'Food']:
                    if resource in member_table.columns:
                        member_table[resource] = member_table[resource].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x != 0 else '0')
                
                st.dataframe(member_table, use_container_width=True, hide_index=True)
    
    else:
        st.info("No data available for alliance analysis")
