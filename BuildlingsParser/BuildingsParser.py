import yaml
import pandas as pd

def parse_buildings_yaml_to_excel(yaml_file_path, output_excel_path):
    """
    Parse YAML file containing building data and export to Excel format.
    
    Columns:
    1: Building
    2: Building Level  
    3-7: Resource Costs (Food, Lumber, Stone, Metal, Gold)
    8: Duration
    9: Power
    """
    
    # Load YAML data
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    # Define standard resource types
    resource_types = ['food', 'lumber', 'stone', 'metal', 'gold']
    
    # Prepare data for DataFrame
    rows = []
    
    for building_type, building_data in data.items():
        try:
            # Skip non-building entries
            if not isinstance(building_data, dict) or 'id' not in building_data:
                continue
            
            # Determine max level from requirements, generations, or max_level
            max_level = building_data.get('max_level', 1)
            
            # Check if there are levels beyond max_level in requirements or generations
            if 'requirements' in building_data and isinstance(building_data['requirements'], dict):
                max_level = max(max_level, max(building_data['requirements'].keys()))
            if 'generations' in building_data and isinstance(building_data['generations'], dict):
                max_level = max(max_level, max(building_data['generations'].keys()))
            
            for level in range(1, max_level + 1):
                row = {
                    'Building': building_type.title(),
                    'Building Level': level
                }
                
                # Add resource costs
                req_data = building_data.get('requirements', {}).get(level, {})
                if isinstance(req_data, dict):
                    resources = req_data.get('resources', {})
                    
                    for resource in resource_types:
                        row[f'{resource.capitalize()}'] = resources.get(resource, 0)
                    
                    # Add duration
                    row['Duration'] = req_data.get('duration', 0)
                else:
                    # Default values if no requirements data
                    for resource in resource_types:
                        row[f'{resource.capitalize()}'] = 0
                    row['Duration'] = 0
                
                # Add power from rewards
                rewards_data = building_data.get('rewards', {})
                power_value = rewards_data.get(level, {}).get('power', 0)
                
                row['Power'] = power_value
                
                rows.append(row)
        except Exception as e:
            print(f"Error processing {building_type} level {level if 'level' in locals() else 'unknown'}: {e}")
            continue
    
    # Create DataFrame with specific column order
    df = pd.DataFrame(rows)
    
    # Ensure columns are in the correct order
    column_order = ['Building', 'Building Level', 'Food', 'Lumber', 'Stone', 'Metal', 'Gold', 'Duration', 'Power']
    df = df.reindex(columns=column_order, fill_value=0)
    
    # Save to Excel
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Buildings_Data', index=False)
        
        # Adjust column widths for better readability
        worksheet = writer.sheets['Buildings_Data']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Excel file saved to: {output_excel_path}")
    print(f"Total rows processed: {len(df)}")
    print(f"Columns: {', '.join(column_order)}")
    
    return df

if __name__ == '__main__':
    yaml_file = 'buildings-live.yaml'
    excel_output = 'Buildings_Output.xlsx'
    
    try:
        df = parse_buildings_yaml_to_excel(yaml_file, excel_output)
        print("\nFirst few rows of the generated data:")
        print(df.head())
    except Exception as e:
        print(f"Error processing file: {e}")
        print("Make sure the YAML file exists and is properly formatted.")
