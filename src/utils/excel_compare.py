"""
Excel workbook comparison utilities.
"""
import pandas as pd
from datetime import datetime
import os
from ..utils.config_utils import get_app_directory
from ..utils.dialog_utils import show_error


def compare_sheets(df1, df2):
    """Compare two dataframes and return differences."""
    # Find rows in df2 that aren't in df1 (added)
    added = df2.merge(df1, how='outer', indicator=True).query('_merge == "left_only"')
    if not added.empty:
        added = added.drop('_merge', axis=1)
    
    # Find rows in df1 that aren't in df2 (removed)
    removed = df1.merge(df2, how='outer', indicator=True).query('_merge == "left_only"')
    if not removed.empty:
        removed = removed.drop('_merge', axis=1)
    
    # Find modified rows
    common_cols = df1.columns.intersection(df2.columns)
    modified = pd.DataFrame()
    if not common_cols.empty:
        merged = df1.merge(df2, on=common_cols, how='inner', suffixes=('_1', '_2'))
        modified = merged[merged.apply(
            lambda x: any(x[f'{col}_1'] != x[f'{col}_2']
                        for col in common_cols),
            axis=1
        )]
    
    return {
        'added': added,
        'removed': removed,
        'modified': modified
    }


def save_comparison_snapshot(comparison_data, snapshot_name=None):
    """Save a comparison snapshot for future reference."""
    snapshots_dir = os.path.join(
        get_app_directory(),
        "logs",
        "comparisons",
        "snapshots"
    )
    
    if not snapshot_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"comparison_snapshot_{timestamp}.csv"
    
    snapshot_path = os.path.join(snapshots_dir, snapshot_name)
    
    try:
        # Convert comparison data to a format suitable for storage
        snapshot_df = pd.DataFrame()
        
        if not comparison_data['added'].empty:
            added_df = comparison_data['added'].copy()
            added_df['change_type'] = 'added'
            snapshot_df = pd.concat([snapshot_df, added_df])
        
        if not comparison_data['removed'].empty:
            removed_df = comparison_data['removed'].copy()
            removed_df['change_type'] = 'removed'
            snapshot_df = pd.concat([snapshot_df, removed_df])
        
        if not comparison_data['modified'].empty:
            modified_df = comparison_data['modified'].copy()
            modified_df['change_type'] = 'modified'
            snapshot_df = pd.concat([snapshot_df, modified_df])
        
        snapshot_df.to_csv(snapshot_path, index=False)
        return snapshot_path
    except Exception as e:
        show_error("Error", f"Failed to save comparison snapshot: {str(e)}")
        return None


def load_comparison_snapshot(snapshot_path):
    """Load a previously saved comparison snapshot."""
    try:
        df = pd.read_csv(snapshot_path)
        
        # Separate the changes back into categories
        added = df[df['change_type'] == 'added'].drop('change_type', axis=1)
        removed = df[df['change_type'] == 'removed'].drop('change_type', axis=1)
        modified = df[df['change_type'] == 'modified'].drop('change_type', axis=1)
        
        return {
            'added': added,
            'removed': removed,
            'modified': modified
        }
    except Exception as e:
        show_error("Error", f"Failed to load comparison snapshot: {str(e)}")
        return None


def compare_workbooks(wb1_path, wb2_path):
    """Compare two Excel workbooks and return the differences."""
    try:
        # Read all sheets from both workbooks
        sheets1 = pd.read_excel(wb1_path, sheet_name=None)
        sheets2 = pd.read_excel(wb2_path, sheet_name=None)
        
        # Compare sheet names
        sheets_only_in_1 = set(sheets1.keys()) - set(sheets2.keys())
        sheets_only_in_2 = set(sheets2.keys()) - set(sheets1.keys())
        common_sheets = set(sheets1.keys()) & set(sheets2.keys())
        
        # Compare contents of common sheets
        sheet_differences = {}
        for sheet_name in common_sheets:
            differences = compare_sheets(
                sheets1[sheet_name],
                sheets2[sheet_name]
            )
            if any(not df.empty for df in differences.values()):
                sheet_differences[sheet_name] = differences
        
        return {
            'sheets_only_in_1': sheets_only_in_1,
            'sheets_only_in_2': sheets_only_in_2,
            'sheet_differences': sheet_differences
        }
    except Exception as e:
        show_error("Error", f"Failed to compare workbooks: {str(e)}")
        return None


def _format_unique_sheets(sheets, workbook_name):
    """Format sheets that exist in only one workbook."""
    if not sheets:
        return []
    
    lines = [f"Sheets only in {workbook_name}:"]
    lines.extend(f"  - {sheet}" for sheet in sorted(sheets))
    lines.append("")
    return lines


def _format_sheet_differences(sheet_name, diffs):
    """Format differences within a single sheet."""
    lines = [f"\nSheet: {sheet_name}"]
    
    for diff_type, label in [
        ('added', 'Added rows:'),
        ('removed', 'Removed rows:'),
        ('modified', 'Modified rows:')
    ]:
        if not diffs[diff_type].empty:
            lines.append(f"  {label}")
            lines.append(str(diffs[diff_type]))
    
    return lines


def format_comparison_results(results):
    """Format comparison results for display."""
    if not results:
        return "Error: Could not generate comparison"
    
    lines = []
    
    # Add sheets unique to each workbook
    lines.extend(_format_unique_sheets(
        results['sheets_only_in_1'], 
        "first workbook"
    ))
    lines.extend(_format_unique_sheets(
        results['sheets_only_in_2'],
        "second workbook"
    ))
    
    # Add differences in common sheets
    if results['sheet_differences']:
        lines.append("Differences in common sheets:")
        for sheet_name, diffs in results['sheet_differences'].items():
            lines.extend(_format_sheet_differences(sheet_name, diffs))
    
    # If no differences found
    if not any([
        results['sheets_only_in_1'],
        results['sheets_only_in_2'],
        results['sheet_differences']
    ]):
        lines.append("No differences found between workbooks.")
    
    return "\n".join(lines)
