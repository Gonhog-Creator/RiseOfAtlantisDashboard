import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

def extract_buildings_data(df):
    """Extract buildings data from comprehensive CSV format"""
    buildings_data = {}
    
    if 'buildings_metadata' in df.columns:
        # Parse buildings metadata from comprehensive CSV format
        for _, row in df.iterrows():
            if pd.notna(row['buildings_metadata']):
                try:
                    buildings_metadata = row['buildings_metadata']
                    
                    # Handle both dict format and string format
                    if isinstance(buildings_metadata, str):
                        # Handle format: "CityName(level)city:[building1:1,building2:2]"
                        # Or "CityName(level)[city]:[building1:1,building2:2]"
                        # Multiple settlements separated by '|': "Settlement1...]:[buildings]|Settlement2...]:[buildings]"
                        
                        # First split by '|' to get individual settlements
                        individual_settlements = buildings_metadata.split('|')
                        
                        for settlement_metadata in individual_settlements:
                            # Try splitting by ']:[' first (new format with brackets)
                            if ']:[' in settlement_metadata:
                                settlement_parts = settlement_metadata.split(']:[')
                            else:
                                # Try splitting by ':[' (format without brackets around type)
                                settlement_parts = settlement_metadata.split(':[')
                            
                            if len(settlement_parts) >= 2:
                                # First part has settlement name and type
                                settlement_info = settlement_parts[0]
                                # Second part has buildings
                                buildings_str = settlement_parts[1].rstrip(']')
                                
                                # Extract settlement type from format "Name(level)type" or "Name(level)[type]"
                                if '[' in settlement_info:
                                    settlement_type = settlement_info.split('[')[1].rstrip(']')
                                elif ')' in settlement_info:
                                    # Format: "Name(level)type"
                                    parts = settlement_info.split(')')
                                    if len(parts) >= 2:
                                        settlement_type = parts[1]
                                    else:
                                        settlement_type = 'city'
                                else:
                                    settlement_type = 'city'  # Default to city for old format
                                
                                # Parse buildings from the string
                                if buildings_str:
                                    for building in buildings_str.split(','):
                                        if ':' in building:
                                            building_name, level = building.split(':')
                                            building_name = building_name.strip()
                                            level = int(level.strip())
                                            
                                            # Skip fortresses in outposts (they don't have fortresses)
                                            if settlement_type == 'outpost' and building_name == 'fortress':
                                                continue
                                            
                                            # Track both unique players and total instances
                                            if building_name not in buildings_data:
                                                buildings_data[building_name] = {'players': set(), 'levels': [], 'total_instances': 0}
                                            buildings_data[building_name]['players'].add(row['account_id'])  # Track unique player
                                            buildings_data[building_name]['total_instances'] += 1  # Count all instances
                                            buildings_data[building_name]['levels'].append(level)  # Keep levels for distribution
                    elif isinstance(buildings_metadata, dict):
                        # Handle dict format
                        for city_info in buildings_metadata.values():
                            if ':' in city_info:
                                buildings_list = city_info.split(':')[1].strip('[]')
                                for building in buildings_list.split(','):
                                    if ':' in building:
                                        building_name, level = building.split(':')
                                        building_name = building_name.strip()
                                        level = int(level.strip())
                                        if building_name not in buildings_data:
                                            buildings_data[building_name] = {'players': set(), 'levels': [], 'total_instances': 0}
                                        buildings_data[building_name]['players'].add(row['account_id'])
                                        buildings_data[building_name]['total_instances'] += 1
                                        buildings_data[building_name]['levels'].append(level)
                except Exception as e:
                    continue
    
    return buildings_data

def create_buildings_tab(filtered_df):
    """Create the Buildings tab with interactive building level analysis"""
    
    if not filtered_df.empty:
        st.markdown("### Buildings Building Analytics")
        
        # Find the latest data with buildings information (comprehensive CSV)
        latest_buildings_data = None
        for i in range(len(filtered_df) - 1, -1, -1):  # Iterate backwards to find latest with building data
            data = filtered_df.iloc[i]
            if 'raw_player_data' in data and data['raw_player_data'] is not None:
                latest_buildings_data = data
                break
        
        if latest_buildings_data is None:
            st.warning("No comprehensive CSV data found. This feature requires comprehensive CSV format.")
            return
        
        latest_data = latest_buildings_data
        
        # Extract buildings data from raw player data
        buildings_data = {}
        if 'raw_player_data' in latest_data:
            player_df = latest_data['raw_player_data']
            if isinstance(player_df, pd.DataFrame) and not player_df.empty:
                buildings_data = extract_buildings_data(player_df)
            else:
                st.warning(f"Raw player data is not a valid DataFrame: {type(player_df)}")
        else:
            st.warning("No raw_player_data found in latest data. This feature requires the comprehensive CSV format.")
        
        if buildings_data:
            
            # Building overview
            st.markdown("#### Stats Building Overview")
            
            if buildings_data:
                # Calculate building statistics
                building_stats = {}
                # Buildings that can have multiple instances per player (count all instances)
                multi_instance_buildings = {'home', 'garrison', 'farm', 'mine', 'quarry', 'lumbermill', 'silo', 'house'}
                
                for building_name, data in buildings_data.items():
                    if data and 'players' in data:
                        # Use total_instances for multi-instance buildings, unique players for single-instance
                        if building_name in multi_instance_buildings:
                            count = data.get('total_instances', 0)
                        else:
                            count = len(data['players'])
                        
                        building_stats[building_name] = {
                            'total_count': count,
                            'level_distribution': {}
                        }
                        
                        # Count buildings by level
                        for level in data['levels']:
                            level_key = f"Level {level}"
                            building_stats[building_name]['level_distribution'][level_key] = \
                                building_stats[building_name]['level_distribution'].get(level_key, 0) + 1
                
                # Create building tiles with images
                building_image_map = {
                    'dragon_keep': 'dragon_keep.webp',
                    'factory': 'factory.webp',
                    'fangtooth_cache': 'fangtooth_cache.webp',
                    'fangtooth_factory': 'fangtooth_factory.webp',
                    'farm': 'farm.webp',
                    'fortress': 'fortress.webp',
                    'fountain_of_life': 'foutain_of_life.webp',
                    'garrison': 'garrison.webp',
                    'home': 'home.webp',
                    'lumbermill': 'lumbermill.webp',
                    'metalsmith': 'metalsmith.webp',
                    'mine': 'mine.webp',
                    'muster_point': 'muster_point.webp',
                    'quarry': 'quarry.webp',
                    'rookery': 'rookery.webp',
                    'science_center': 'science_center.webp',
                    'sentinel': 'sentinel.webp',
                    'storage_vault': 'storage_vault.webp',
                    'theater': 'theater.webp',
                    'wall': 'wall.webp'
                }
                
                if building_stats:
                    # Sort buildings by total count
                    sorted_buildings = sorted(building_stats.items(), key=lambda x: x[1]['total_count'], reverse=True)
                    
                    # Display building tiles in a responsive grid
                    cols_per_row = 6  # Increased from 4 to use more screen width
                    for i in range(0, len(sorted_buildings), cols_per_row):
                        cols = st.columns(min(cols_per_row, len(sorted_buildings) - i))
                        for j, (building_name, stats) in enumerate(sorted_buildings[i:i + cols_per_row]):
                            with cols[j]:
                                image_file = building_image_map.get(building_name, 'home.webp')
                                image_path = f"Images/{image_file}"
                                
                                try:
                                    st.image(image_path, width=70)
                                except:
                                    st.write(f"🏠")
                                
                                st.markdown(f"**{building_name.replace('_', ' ').title()}**")
                                st.metric("Total Count", stats['total_count'])
                
                # Interactive building selector
                st.markdown("#### Interactive Interactive Building Analysis")
                
                if building_stats:
                    # Building selection
                    building_names = list(building_stats.keys())
                    selected_building = st.selectbox(
                        "Select a building to analyze:",
                        building_names,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if selected_building:
                        stats = building_stats[selected_building]
                        
                        # Display building statistics
                        col1 = st.columns(1)[0]
                        
                        with col1:
                            st.metric("Total Count", stats['total_count'])
                        
                        # Level distribution chart
                        st.markdown(f"##### Trends {selected_building.replace('_', ' ').title()} Level Distribution")
                        
                        level_dist = stats['level_distribution']
                        if level_dist:
                            # Extract numeric level for sorting and display
                            level_data = []
                            for level_key, count in level_dist.items():
                                # Extract numeric part from "Level 1", "Level 2", etc.
                                level_num = int(level_key.replace('Level ', ''))
                                level_data.append({'Level': level_num, 'Count': count})
                            
                            level_df = pd.DataFrame(level_data)
                            level_df = level_df.sort_values('Level')
                            
                            fig_level = px.bar(
                                level_df,
                                x='Level',
                                y='Count',
                                title=f"Distribution of {selected_building.replace('_', ' ').title()} Levels"
                            )
                            fig_level.update_layout(
                                xaxis_title="Building Level",
                                yaxis_title="Number of Buildings",
                                height=400
                            )
                            st.plotly_chart(fig_level, use_container_width=True)
        
        # Individual Player Building Analysis
        st.markdown("---")
        st.markdown("### 🏗️ Individual Player Building Analysis")
        
        if 'raw_player_data' in latest_data:
            player_df = latest_data['raw_player_data']
            
            if isinstance(player_df, pd.DataFrame) and not player_df.empty:
                # Create player selection dropdown
                player_options = []
                if 'username' in player_df.columns:
                    player_options = [(f"{row['username']} ({row['account_id'][:8]}...)", row['account_id']) 
                                     for _, row in player_df.iterrows() 
                                     if pd.notna(row.get('username'))]
                else:
                    player_options = [(f"{row['account_id'][:8]}...", row['account_id']) 
                                     for _, row in player_df.iterrows()]
                
                if player_options:
                    player_options.sort(key=lambda x: x[0])
                    selected_player = st.selectbox(
                        "Select a player to view their buildings:",
                        options=[option[0] for option in player_options]
                    )
                    
                    if selected_player:
                        # Get the selected player's account ID
                        selected_account_id = next(option[1] for option in player_options if option[0] == selected_player)
                        
                        # Get the selected player's data
                        player_row = player_df[player_df['account_id'] == selected_account_id]
                        
                        if not player_row.empty:
                            player_data = player_row.iloc[0]
                            
                            # Display player info
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                player_name = player_data.get('username', selected_account_id[:8] + "...")
                                st.metric("Player", player_name)
                            with col2:
                                alliance = player_data.get('alliance_name', 'None')
                                st.metric("Alliance", alliance)
                            with col3:
                                power = player_data.get('power', 0)
                                st.metric("Power", f"{int(power):,}")
                            
                            # Parse buildings metadata
                            buildings_metadata = player_data.get('buildings_metadata')
                            
                            if pd.notna(buildings_metadata):
                                try:
                                    # Parse all buildings for this player
                                    player_buildings = []
                                    
                                    if isinstance(buildings_metadata, str):
                                        # Handle new format with settlement type: "CityName(level)[type]:[building1:1,building2:2]"
                                        # Or old format: "CityName(level):[building1:1,building2:2]"
                                        # Split by ']:[' to get individual settlements
                                        settlement_parts = buildings_metadata.split(']:[')
                                        
                                        for i, settlement_part in enumerate(settlement_parts):
                                            # Initialize buildings_str to avoid reference before assignment
                                            buildings_str = None
                                            name_part = ''
                                            settlement_type = 'city'
                                            
                                            # First part has settlement name and type
                                            if i == 0:
                                                # This is the first settlement (before the first ']:[')
                                                # Check if it contains the new format with [type]
                                                if '[' in settlement_part:
                                                    # New format: "CityName(level)[type]"
                                                    name_part = settlement_part.split('[')[0]
                                                    settlement_type = settlement_part.split('[')[1].rstrip(']')
                                                else:
                                                    # Old format: "CityName(level)"
                                                    name_part = settlement_part
                                                    settlement_type = 'city'  # Default to city for old format
                                                
                                                # Get the buildings from the next part
                                                if i + 1 < len(settlement_parts):
                                                    buildings_str = settlement_parts[i + 1].rstrip(']')
                                            else:
                                                # This is a buildings list from previous settlement
                                                buildings_str = settlement_part.rstrip(']')
                                                # Get next settlement name if available
                                                if i + 1 < len(settlement_parts):
                                                    next_part = settlement_parts[i + 1]
                                                    if '[' in next_part:
                                                        name_part = next_part.split('[')[0]
                                                        settlement_type = next_part.split('[')[1].rstrip(']')
                                                    else:
                                                        name_part = next_part
                                                        settlement_type = 'city'
                                            
                                            # Parse buildings from the string
                                            if buildings_str:
                                                for building in buildings_str.split(','):
                                                    if ':' in building:
                                                        building_name, level = building.split(':')
                                                        building_name = building_name.strip()
                                                        level = int(level.strip())
                                                        
                                                        # Skip fortresses in outposts (they don't have fortresses)
                                                        if settlement_type == 'outpost' and building_name == 'fortress':
                                                            continue
                                                        
                                                        player_buildings.append({
                                                            'City': f"{name_part} ({settlement_type})",
                                                            'Building': building_name.replace('_', ' ').title(),
                                                            'Level': level
                                                        })
                                    elif isinstance(buildings_metadata, dict):
                                        # Handle dict format
                                        for city_name, city_info in buildings_metadata.items():
                                            if ':' in city_info:
                                                buildings_str = city_info.split(':')[1].strip('[]')
                                                for building in buildings_str.split(','):
                                                    if ':' in building:
                                                        building_name, level = building.split(':')
                                                        building_name = building_name.strip()
                                                        level = int(level.strip())
                                                        
                                                        player_buildings.append({
                                                            'City': city_name,
                                                            'Building': building_name.replace('_', ' ').title(),
                                                            'Level': level
                                                        })
                                    
                                    if player_buildings:
                                        # Display buildings in a table
                                        buildings_df = pd.DataFrame(player_buildings)
                                        
                                        # Group by building type and show summary
                                        st.markdown("#### Building Summary")
                                        building_summary = buildings_df.groupby('Building').agg({
                                            'Level': ['count']
                                        }).reset_index()
                                        building_summary.columns = ['Building', 'Count']
                                        building_summary = building_summary.sort_values('Count', ascending=False)
                                        
                                        st.dataframe(building_summary, use_container_width=True)
                                        
                                        # Show building level distribution chart
                                        st.markdown("#### Building Level Distribution")
                                        level_dist = buildings_df.groupby('Level').size().reset_index(name='Count')
                                        level_dist = level_dist.sort_values('Level')
                                        
                                        fig_player_buildings = px.bar(
                                            level_dist,
                                            x='Level',
                                            y='Count',
                                            title=f"Building Level Distribution for {player_name}",
                                            color='Count',
                                            color_continuous_scale='viridis'
                                        )
                                        fig_player_buildings.update_layout(
                                            xaxis_title="Building Level",
                                            yaxis_title="Number of Buildings",
                                            height=400
                                        )
                                        st.plotly_chart(fig_player_buildings, use_container_width=True)
                                    else:
                                        st.warning("No buildings found for this player")
                                except Exception as e:
                                    st.error(f"Error parsing buildings data: {e}")
                            else:
                                st.warning("No buildings data available for this player")
                else:
                    st.warning("No players available for selection")
        else:
            st.info("Player data not available for individual building analysis")
    
    else:
        st.info("No data available for building analysis")
