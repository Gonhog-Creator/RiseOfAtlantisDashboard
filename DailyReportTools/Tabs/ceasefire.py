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
    """Create the Ceasefire tab with player and resource analysis"""
    
    if not filtered_df.empty:
        st.markdown("### :lock: Attack Prevention Analysis")
        
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
        player_data['has_ceasefire'] = player_data['active_effects'].fillna('').astype(str).apply(
            lambda x: any(effect in x for effect in attack_prevention_effects)
        )
        
        ceasefire_players = player_data[player_data['has_ceasefire']].copy()
        
        if ceasefire_players.empty:
            st.info("No players currently have attack prevention effects.")
            return
        
        # Summary statistics
        total_players = len(player_data)
        ceasefire_count = len(ceasefire_players)
        ceasefire_percentage = (ceasefire_count / total_players * 100) if total_players > 0 else 0
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Players",
                f"{total_players:,}"
            )
        
        with col2:
            st.metric(
                "Players with Attack Prevention",
                f"{ceasefire_count:,}",
                f"{ceasefire_percentage:.1f}%"
            )
        
        with col3:
            # Calculate total protected resources
            resource_columns = ['resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food']
            total_protected = 0
            for col in resource_columns:
                if col in ceasefire_players.columns:
                    total_protected += ceasefire_players[col].fillna(0).sum()
            
            st.metric(
                "Total Protected Resources",
                format_number(total_protected)
            )
            
            st.markdown("---")
        
        # Player details table
        st.markdown("### :bust_in_silhouette: Players with Attack Prevention")
        
        # Prepare player data for display
        display_columns = ['username', 'power', 'resource_gold', 'resource_lumber', 'resource_stone', 'resource_metal', 'resource_food', 'resource_ruby']
        available_columns = [col for col in display_columns if col in ceasefire_players.columns]
        
        if available_columns:
            player_table = ceasefire_players[available_columns].copy()
            
            # Sort by power (descending)
            player_table = player_table.sort_values('power', ascending=False)
            
            # Rename columns for better display
            column_rename_map = {
                'username': 'Player Name',
                'power': 'Power',
                'resource_gold': 'Gold',
                'resource_lumber': 'Lumber', 
                'resource_stone': 'Stone',
                'resource_metal': 'Metal',
                'resource_food': 'Food',
                'resource_ruby': 'Ruby'
            }
            
            player_table = player_table.rename(columns=column_rename_map)
            
            # Format resource columns
            resource_display_columns = ['Gold', 'Lumber', 'Stone', 'Metal', 'Food', 'Ruby']
            for col in resource_display_columns:
                if col in player_table.columns:
                    player_table[col] = player_table[col].apply(lambda x: format_number(x) if pd.notna(x) else '0')
            
            # Format power column
            if 'Power' in player_table.columns:
                player_table['Power'] = player_table['Power'].apply(lambda x: format_number(x) if pd.notna(x) else '0')
            
            st.dataframe(player_table, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Resource distribution pie charts
        st.markdown("### :pie_chart: Resource Distribution Analysis")
        
        # Create pie charts for each resource type (except rubies)
        resource_info = {
            'resource_gold': {'name': 'Gold', 'color': '#FFD700'},
            'resource_lumber': {'name': 'Lumber', 'color': '#8B4513'},
            'resource_stone': {'name': 'Stone', 'color': '#808080'},
            'resource_metal': {'name': 'Metal', 'color': '#C0C0C0'},
            'resource_food': {'name': 'Food', 'color': '#FF6347'}
        }
        
        # Create 2x3 grid for pie charts
        for i, (col, info) in enumerate(resource_info.items()):
            if col in ceasefire_players.columns:
                # Get top players by this resource (for cleaner pie chart)
                player_resource_data = ceasefire_players[['username', col]].copy()
                player_resource_data[col] = player_resource_data[col].fillna(0)
                player_resource_data = player_resource_data[player_resource_data[col] > 0]
                player_resource_data = player_resource_data.sort_values(col, ascending=False)
                
                # Take top 10 players and group others as "Others"
                top_players = player_resource_data.head(10)
                others_amount = player_resource_data.iloc[10:][col].sum() if len(player_resource_data) > 10 else 0
                
                # Prepare data for pie chart
                labels = [f"{row['username']}" for _, row in top_players.iterrows()]
                values = [row[col] for _, row in top_players.iterrows()]
                
                if others_amount > 0:
                    labels.append('Others')
                    values.append(others_amount)
                
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    textinfo='label+percent',
                    textposition='outside',
                    textfont_size=10,
                    showlegend=True
                )])
                
                total_protected = ceasefire_players[col].fillna(0).sum()
                fig.update_layout(
                    title=f"{info['name']} Among Protected Players<br><span style='font-size:12px;color:gray;'>{format_number(total_protected)} total protected</span>",
                    height=350,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10)
                    ),
                    margin=dict(r=150)  # Add right margin for legend
                )
                
                # Display in columns
                if i % 2 == 0:
                    col_left, col_right = st.columns(2)
                
                if i % 2 == 0:
                    with col_left:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    with col_right:
                        st.plotly_chart(fig, use_container_width=True)
        
        # Resource summary table
        st.markdown("---")
        st.markdown("### :bar_chart: Resource Control Summary")
        
        summary_data = []
        for col, info in resource_info.items():
            if col in ceasefire_players.columns:
                protected = ceasefire_players[col].fillna(0).sum()
                total = player_data[col].fillna(0).sum()
                percentage = (protected / total * 100) if total > 0 else 0
                
                summary_data.append({
                    'Resource': info['name'],
                    'Protected': format_number(protected),
                    'Total': format_number(total),
                    'Percentage': f"{percentage:.1f}%",
                    'Players': len(ceasefire_players[ceasefire_players[col].fillna(0) > 0])
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("No data available for ceasefire analysis.")
