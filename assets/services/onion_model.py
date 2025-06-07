from utils.logging_config import get_logger

logger = get_logger(__name__)


def override_config_for_testing(original_config):
    """Temporary override to fix the filtering issue"""
    logger.info("=== APPLYING TEMPORARY CONFIG OVERRIDE ===")
    logger.info(f"Original config: {original_config}")

    # Create a working config
    working_config = original_config.copy()
    working_config["primary_positive_indicator"] = ""  # Remove filter
    working_config["invalid_phrases_exact"] = []  # Remove filter
    working_config["invalid_phrases_contain"] = []  # Remove filter

    logger.info(f"New config: {working_config}")
    return working_config


config_params = {
    "num_floors": 4,
    "top_n_heuristic_entrances": 5,
    "primary_positive_indicator": "",  # ← CHANGED: Remove filter
    "invalid_phrases_exact": [],  # ← CHANGED: Remove filter
    "invalid_phrases_contain": [],  # ← CHANGED: Remove filter
    "same_door_scan_threshold_seconds": 10,
    "ping_pong_threshold_minutes": 1,
}
# processing/onion_model.py
"""
Core onion model processing implementation - DEBUG VERSION
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

from config.settings import REQUIRED_INTERNAL_COLUMNS
from core.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


def run_onion_model_processing(
    raw_df: pd.DataFrame,
    config_params: Dict[str, Any],
    confirmed_official_entrances: Optional[List[str]] = None,
    detailed_door_classifications: Optional[Dict[str, Any]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Main function to run onion model processing on access control data

    Args:
        raw_df: Raw access control DataFrame
        config_params: Configuration parameters
        confirmed_official_entrances: List of confirmed entrance door IDs
        detailed_door_classifications: Detailed door classifications

    Returns:
        Tuple of (enriched_df, device_attributes_df, path_viz_data_df, all_paths_df)
    """
    try:
        logger.info(f"=== DEBUG: Starting onion model processing ===")
        logger.info(f"DEBUG: Raw data shape: {raw_df.shape}")
        logger.info(f"DEBUG: Raw data columns: {list(raw_df.columns)}")
        logger.info(f"DEBUG: Config params: {config_params}")
        logger.info(f"DEBUG: Confirmed entrances: {confirmed_official_entrances}")
        logger.info(f"DEBUG: Detailed classifications: {detailed_door_classifications}")

        logger.info(f"Starting onion model processing for {len(raw_df)} records")

        # Step 1: Clean and prepare data
        logger.info(f"\n=== Step 1: Cleaning data ===")
        cleaned_df = clean_access_data(raw_df, config_params)
        logger.info(f"DEBUG: Cleaned data shape: {cleaned_df.shape}")

        if len(cleaned_df) == 0:
            logger.info("ERROR: No data remaining after cleaning!")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Step 2: Identify entrances and calculate device depths
        logger.info(f"\n=== Step 2: Calculating device attributes ===")
        device_attributes = calculate_device_attributes(
            cleaned_df,
            config_params,
            confirmed_official_entrances,
            detailed_door_classifications,
        )
        logger.info(f"DEBUG: Device attributes shape: {device_attributes.shape}")
        logger.info(
            f"DEBUG: Device attributes columns: {list(device_attributes.columns)}"
        )

        if len(device_attributes) == 0:
            logger.info("ERROR: No device attributes calculated!")
            return cleaned_df, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Step 3: Generate user paths and transitions
        logger.info(f"\n=== Step 3: Generating user paths ===")
        all_paths_df = generate_user_paths(cleaned_df, device_attributes)
        logger.info(f"DEBUG: All paths shape: {all_paths_df.shape}")
        logger.info(
            f"DEBUG: All paths columns: {list(all_paths_df.columns) if not all_paths_df.empty else 'EMPTY'}"
        )

        if len(all_paths_df) == 0:
            logger.info("WARNING: No user paths generated!")

        # Step 4: Prepare visualization data
        logger.info(f"\n=== Step 4: Preparing visualization data ===")
        path_viz_data = prepare_path_visualization_data(all_paths_df)
        logger.info(f"DEBUG: Path viz data shape: {path_viz_data.shape}")
        logger.info(
            f"DEBUG: Path viz data columns: {list(path_viz_data.columns) if not path_viz_data.empty else 'EMPTY'}"
        )

        if len(path_viz_data) == 0:
            logger.info("WARNING: No visualization data prepared!")

        # Step 5: Enrich original data with processing results
        logger.info(f"\n=== Step 5: Enriching data ===")
        enriched_df = enrich_data_with_results(cleaned_df, device_attributes)
        logger.info(f"DEBUG: Enriched data shape: {enriched_df.shape}")

        logger.info(f"\n=== FINAL RESULTS ===")
        logger.info(f"Enriched DF: {enriched_df.shape}")
        logger.info(f"Device Attributes: {device_attributes.shape}")
        logger.info(f"Path Viz Data: {path_viz_data.shape}")
        logger.info(f"All Paths: {all_paths_df.shape}")

        logger.info("Onion model processing completed successfully")

        return enriched_df, device_attributes, path_viz_data, all_paths_df

    except Exception as e:
        logger.info(f"ERROR in run_onion_model_processing: {str(e)}")
        logger.error(f"Error in onion model processing: {str(e)}")
        raise DataProcessingError(f"Onion model processing failed: {str(e)}")


def clean_access_data(df: pd.DataFrame, config_params: Dict[str, Any]) -> pd.DataFrame:
    """Clean and filter access control data"""
    logger.info(f"DEBUG: Starting clean_access_data with {len(df)} records")
    logger.info("Cleaning access data")

    # Get column names with error handling
    try:
        timestamp_col = REQUIRED_INTERNAL_COLUMNS[
            "Timestamp"
        ]  # 'Timestamp (Event Time)'
        eventtype_col = REQUIRED_INTERNAL_COLUMNS[
            "EventType"
        ]  # 'EventType (Access Result)'
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]  # 'DoorID (Device Name)'
        userid_col = REQUIRED_INTERNAL_COLUMNS["UserID"]  # 'UserID (Person Identifier)'
    except (KeyError, NameError) as e:
        raise DataProcessingError(f"Required column constants not found: {str(e)}")

    logger.info(
        f"DEBUG: Using columns - timestamp: '{timestamp_col}', eventtype: '{eventtype_col}', doorid: '{doorid_col}', userid: '{userid_col}'"
    )

    cleaned_df = df.copy()

    # Validate that required columns exist
    missing_columns = []
    for col in [timestamp_col, eventtype_col, doorid_col, userid_col]:
        if col not in cleaned_df.columns:
            missing_columns.append(col)

    if missing_columns:
        raise DataProcessingError(
            f"Missing required columns: {missing_columns}. Available columns: {list(cleaned_df.columns)}"
        )

    logger.info(f"DEBUG: Before filtering - {len(cleaned_df)} records")

    # Filter by primary positive indicator
    primary_indicator = config_params.get(
        "primary_positive_indicator", "ACCESS GRANTED"
    )
    logger.info(f"DEBUG: Filtering by primary indicator: '{primary_indicator}'")

    if primary_indicator:
        before_count = len(cleaned_df)
        cleaned_df = cleaned_df[
            cleaned_df[eventtype_col].str.contains(primary_indicator, na=False)
        ]
        logger.info(
            f"DEBUG: After primary indicator filter: {len(cleaned_df)} records (removed {before_count - len(cleaned_df)})"
        )

    # Remove invalid phrases
    invalid_exact = config_params.get("invalid_phrases_exact", [])
    logger.info(f"DEBUG: Removing invalid exact phrases: {invalid_exact}")
    for phrase in invalid_exact:
        before_count = len(cleaned_df)
        cleaned_df = cleaned_df[cleaned_df[eventtype_col] != phrase]
        logger.info(
            f"DEBUG: After removing '{phrase}': {len(cleaned_df)} records (removed {before_count - len(cleaned_df)})"
        )

    invalid_contain = config_params.get("invalid_phrases_contain", [])
    logger.info(f"DEBUG: Removing invalid contain phrases: {invalid_contain}")
    for phrase in invalid_contain:
        before_count = len(cleaned_df)
        cleaned_df = cleaned_df[
            ~cleaned_df[eventtype_col].str.contains(phrase, na=False)
        ]
        logger.info(
            f"DEBUG: After removing contains '{phrase}': {len(cleaned_df)} records (removed {before_count - len(cleaned_df)})"
        )

    # Remove duplicate scans (same door, same user, within threshold)
    threshold_seconds = config_params.get("same_door_scan_threshold_seconds", 10)
    logger.info(f"DEBUG: Duplicate scan threshold: {threshold_seconds} seconds")
    if threshold_seconds > 0:
        before_count = len(cleaned_df)
        cleaned_df = remove_duplicate_scans(cleaned_df, threshold_seconds)
        logger.info(
            f"DEBUG: After duplicate removal: {len(cleaned_df)} records (removed {before_count - len(cleaned_df)})"
        )

    # Sort by timestamp
    cleaned_df = cleaned_df.sort_values(timestamp_col).reset_index(drop=True)

    # Show sample of remaining data
    if len(cleaned_df) > 0:
        logger.info(f"DEBUG: Sample of cleaned data:")
        logger.info(cleaned_df[[doorid_col, userid_col, eventtype_col]].head())
        logger.info(f"DEBUG: Unique doors: {cleaned_df[doorid_col].nunique()}")
        logger.info(f"DEBUG: Unique users: {cleaned_df[userid_col].nunique()}")
    else:
        logger.info("WARNING: No data remaining after cleaning!")

        logger.info(f"Cleaned data: {len(cleaned_df)} records remaining")
    return cleaned_df


def remove_duplicate_scans(df: pd.DataFrame, threshold_seconds: int) -> pd.DataFrame:
    """Remove duplicate scans within threshold"""
    try:
        timestamp_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]
        userid_col = REQUIRED_INTERNAL_COLUMNS["UserID"]
    except (KeyError, NameError) as e:
        raise DataProcessingError(f"Required column constants not found: {str(e)}")

    df_sorted = df.sort_values([userid_col, doorid_col, timestamp_col])

    # Calculate time difference between consecutive scans for same user/door
    df_sorted["time_diff"] = df_sorted.groupby([userid_col, doorid_col])[
        timestamp_col
    ].diff()
    df_sorted["time_diff_seconds"] = df_sorted["time_diff"].dt.total_seconds()

    # Keep first scan and any scan that's beyond the threshold
    mask = (df_sorted["time_diff_seconds"].isna()) | (
        df_sorted["time_diff_seconds"] > threshold_seconds
    )

    result = df_sorted[mask].drop(["time_diff", "time_diff_seconds"], axis=1)
    return result.reset_index(drop=True)


def calculate_device_attributes(
    df: pd.DataFrame,
    config_params: Dict[str, Any],
    confirmed_entrances: Optional[List[str]] = None,
    detailed_classifications: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Calculate device attributes including depth and entrance status"""
    try:
        # Get column names with error handling
        try:
            doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]  # 'DoorID (Device Name)'
            userid_col = REQUIRED_INTERNAL_COLUMNS[
                "UserID"
            ]  # 'UserID (Person Identifier)'
        except (KeyError, NameError) as e:
            raise DataProcessingError(f"Required column constants not found: {str(e)}")

        logger.info(f"DEBUG: Expected doorid_col = '{doorid_col}'")
        logger.info(f"DEBUG: Available columns in df = {list(df.columns)}")

        # Validate column exists
        if doorid_col not in df.columns:
            raise DataProcessingError(
                f"Required column '{doorid_col}' not found in dataframe. Available columns: {list(df.columns)}"
            )

        # Get unique doors
        unique_doors = df[doorid_col].unique()
        logger.info(
            f"DEBUG: Found {len(unique_doors)} unique doors: {list(unique_doors)}"
        )

        device_attrs = []

        for door_id in unique_doors:
            # Create attribute dict with simple string keys (not display names)
            door_data = df[df[doorid_col] == door_id]
            attr = {
                "DoorID": door_id,  # Use simple key name
                "EventCount": len(door_data),
                "UniqueUsers": door_data[userid_col].nunique(),
            }

            logger.info(
                f"DEBUG: Door '{door_id}' - Events: {attr['EventCount']}, Users: {attr['UniqueUsers']}"
            )

            # Apply detailed classifications if provided
            if detailed_classifications and door_id in detailed_classifications:
                classification = detailed_classifications[door_id]
                attr["Floor"] = classification.get("floor", "1")
                attr["IsOfficialEntrance"] = classification.get("is_ee", False)
                attr["IsStaircase"] = classification.get("is_stair", False)
                attr["SecurityLevel"] = classification.get("security", "green")
                logger.info(
                    f"DEBUG: Applied detailed classification for '{door_id}': {classification}"
                )
            else:
                # Default values
                attr["Floor"] = "1"
                attr["IsOfficialEntrance"] = door_id in (confirmed_entrances or [])
                attr["IsStaircase"] = False
                attr["SecurityLevel"] = "green"
                logger.info(f"DEBUG: Applied default classification for '{door_id}'")

            # Calculate device depth (simplified heuristic)
            if attr["IsOfficialEntrance"]:
                attr["FinalGlobalDeviceDepth"] = 1
            else:
                # Simple heuristic based on event count (more events = closer to entrance)
                attr["FinalGlobalDeviceDepth"] = min(
                    3, max(1, 4 - int(attr["EventCount"] / 100))
                )

            # Determine if globally critical (placeholder logic)
            attr["IsGloballyCritical"] = (
                attr["SecurityLevel"] == "red" and attr["FinalGlobalDeviceDepth"] >= 2
            )

            logger.info(
                f"DEBUG: Final attributes for '{door_id}': Depth={attr['FinalGlobalDeviceDepth']}, IsEntrance={attr['IsOfficialEntrance']}"
            )
            device_attrs.append(attr)

        device_attrs_df = pd.DataFrame(device_attrs)
        logger.info(
            f"DEBUG: Created device_attrs_df with columns: {list(device_attrs_df.columns)}"
        )
        logger.info(f"DEBUG: Device attributes summary:")
        logger.info(
            device_attrs_df[
                ["DoorID", "EventCount", "FinalGlobalDeviceDepth", "IsOfficialEntrance"]
            ]
        )

        # Calculate most common next door for each device
        if "DoorID" in device_attrs_df.columns:
            device_attrs_df["MostCommonNextDoor"] = device_attrs_df["DoorID"].apply(
                lambda door: calculate_most_common_next_door(df, door)
            )

        logger.info(f"Calculated attributes for {len(device_attrs_df)} devices")
        return device_attrs_df

    except Exception as e:
        logger.info(f"ERROR in calculate_device_attributes: {str(e)}")
        raise DataProcessingError(f"Failed to calculate device attributes: {str(e)}")


def calculate_most_common_next_door(df: pd.DataFrame, door_id: str) -> str:
    """Calculate the most common next door for a given door"""
    try:
        # Get column names with error handling
        timestamp_col = REQUIRED_INTERNAL_COLUMNS[
            "Timestamp"
        ]  # 'Timestamp (Event Time)'
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]  # 'DoorID (Device Name)'
        userid_col = REQUIRED_INTERNAL_COLUMNS["UserID"]  # 'UserID (Person Identifier)'
    except (KeyError, NameError) as e:
        logger.warning(f"Required column constants not found: {str(e)}")
        return ""

    # Validate columns exist
    required_cols = [timestamp_col, doorid_col, userid_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing columns for next door calculation: {missing_cols}")
        return ""

    # Get all visits to this door
    door_visits = df[df[doorid_col] == door_id].copy()

    if len(door_visits) == 0:
        return ""

    next_doors = []

    for _, visit in door_visits.iterrows():
        user_id = visit[userid_col]
        visit_time = visit[timestamp_col]

        # Find next door visited by same user within reasonable time window (1 hour)
        user_subsequent = df[
            (df[userid_col] == user_id)
            & (df[timestamp_col] > visit_time)
            & (df[timestamp_col] <= visit_time + pd.Timedelta(hours=1))
            & (df[doorid_col] != door_id)
        ].sort_values(timestamp_col)

        if not user_subsequent.empty:
            next_door = user_subsequent.iloc[0][doorid_col]
            next_doors.append(next_door)

    if next_doors:
        # Return most common next door
        next_door_counts = pd.Series(next_doors).value_counts()
        return str(next_door_counts.index[0])

    return ""


def generate_user_paths(
    df: pd.DataFrame, device_attributes: pd.DataFrame
) -> pd.DataFrame:
    """Generate user movement paths between doors"""
    try:
        logger.info(f"DEBUG: Starting generate_user_paths with {len(df)} records")

        # Get column names with error handling
        try:
            timestamp_col = REQUIRED_INTERNAL_COLUMNS[
                "Timestamp"
            ]  # 'Timestamp (Event Time)'
            doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]  # 'DoorID (Device Name)'
            userid_col = REQUIRED_INTERNAL_COLUMNS[
                "UserID"
            ]  # 'UserID (Person Identifier)'
        except (KeyError, NameError) as e:
            raise DataProcessingError(f"Required column constants not found: {str(e)}")

        logger.info(f"DEBUG: generate_user_paths - doorid_col = '{doorid_col}'")
        logger.info(f"DEBUG: generate_user_paths - df.columns = {list(df.columns)}")
        logger.info(
            f"DEBUG: generate_user_paths - device_attributes.columns = {list(device_attributes.columns)}"
        )

        # Validate columns exist
        required_cols = [timestamp_col, doorid_col, userid_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise DataProcessingError(
                f"Missing columns for path generation: {missing_cols}"
            )

        paths = []
        users_processed = 0
        paths_found = 0

        # Group by user and generate paths
        for user_id, user_data in df.groupby(userid_col):
            users_processed += 1
            user_data_sorted = user_data.sort_values(timestamp_col)

            if users_processed <= 5:  # Debug first 5 users
                logger.info(
                    f"DEBUG: Processing user {user_id} with {len(user_data_sorted)} events"
                )
                logger.info(f"DEBUG: User events: {list(user_data_sorted[doorid_col])}")

            for i in range(len(user_data_sorted) - 1):
                current_door = user_data_sorted.iloc[i][doorid_col]
                next_door = user_data_sorted.iloc[i + 1][doorid_col]
                current_time = user_data_sorted.iloc[i][timestamp_col]
                next_time = user_data_sorted.iloc[i + 1][timestamp_col]

                # Only consider paths within reasonable time window
                time_diff = (next_time - current_time).total_seconds()

                if (
                    time_diff <= 3600 and current_door != next_door
                ):  # Within 1 hour and different doors
                    paths.append(
                        {
                            "UserID": user_id,
                            "SourceDoor": current_door,
                            "TargetDoor": next_door,
                            "TimestampStart": current_time,
                            "TimestampEnd": next_time,
                            "TransitionSeconds": time_diff,
                        }
                    )
                    paths_found += 1

                    if paths_found <= 10:  # Debug first 10 paths
                        logger.info(
                            f"DEBUG: Path {paths_found}: {current_door} -> {next_door} ({time_diff:.0f}s)"
                        )

        logger.info(
            f"DEBUG: Processed {users_processed} users, found {paths_found} valid paths"
        )

        paths_df = pd.DataFrame(paths)

        if not paths_df.empty:
            logger.info(f"DEBUG: Created paths_df with {len(paths_df)} rows")

            # Calculate transition frequencies
            transition_counts = (
                paths_df.groupby(["SourceDoor", "TargetDoor"])
                .size()
                .reset_index(name="TransitionFrequency")
            )
            logger.info(f"DEBUG: Transition counts shape: {transition_counts.shape}")

            paths_df = paths_df.merge(
                transition_counts, on=["SourceDoor", "TargetDoor"]
            )
            logger.info(f"DEBUG: After merge, paths_df shape: {paths_df.shape}")

            # Add depth information - use 'DoorID' column from device_attributes
            if "DoorID" in device_attributes.columns:
                device_depth_map = device_attributes.set_index("DoorID")[
                    "FinalGlobalDeviceDepth"
                ].to_dict()
                logger.info(f"DEBUG: Device depth map: {device_depth_map}")
            else:
                logger.info(
                    f"WARNING: 'DoorID' column not found in device_attributes. Available: {list(device_attributes.columns)}"
                )
                device_depth_map = {}

            paths_df["SourceDepth"] = paths_df["SourceDoor"].map(device_depth_map)
            paths_df["TargetDepth"] = paths_df["TargetDoor"].map(device_depth_map)
            paths_df["is_to_inner_default"] = (
                paths_df["TargetDepth"] > paths_df["SourceDepth"]
            )

            logger.info(f"DEBUG: Final paths_df columns: {list(paths_df.columns)}")
            logger.info(f"DEBUG: Sample paths:")
            logger.info(
                paths_df[["SourceDoor", "TargetDoor", "TransitionFrequency"]].head()
            )
        else:
            logger.info("WARNING: No paths generated!")

        logger.info(f"Generated {len(paths_df)} user path records")
        return paths_df

    except Exception as e:
        logger.info(f"ERROR in generate_user_paths: {str(e)}")
        raise DataProcessingError(f"Failed to generate user paths: {str(e)}")


def prepare_path_visualization_data(all_paths_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare path data for visualization"""
    logger.info(
        f"DEBUG: Starting prepare_path_visualization_data with {len(all_paths_df)} paths"
    )

    if all_paths_df.empty:
        logger.info("DEBUG: No paths to visualize, returning empty DataFrame")
        return pd.DataFrame(columns=["Door1", "Door2", "PathWidth"])

    # Create undirected path weights
    paths_df = all_paths_df.copy()
    paths_df["CanonicalPair"] = paths_df.apply(
        lambda row: tuple(sorted([row["SourceDoor"], row["TargetDoor"]])), axis=1
    )

    logger.info(
        f"DEBUG: Created canonical pairs, sample: {paths_df['CanonicalPair'].head().tolist()}"
    )

    # Aggregate by canonical pairs
    path_weights = (
        paths_df.groupby("CanonicalPair")["TransitionFrequency"].sum().reset_index()
    )
    path_weights.rename(columns={"TransitionFrequency": "PathWidth"}, inplace=True)

    logger.info(f"DEBUG: Path weights shape: {path_weights.shape}")
    logger.info(f"DEBUG: Sample path weights:")
    logger.info(path_weights.head())

    # Split canonical pairs back to Door1, Door2
    if not path_weights.empty:
        split_pairs = pd.DataFrame(
            path_weights["CanonicalPair"].tolist(),
            index=path_weights.index,
            columns=["Door1", "Door2"],
        )
        path_viz_df = pd.concat([split_pairs, path_weights[["PathWidth"]]], axis=1)
        logger.info(f"DEBUG: Final visualization data shape: {path_viz_df.shape}")
        logger.info(f"DEBUG: Sample visualization data:")
        logger.info(path_viz_df.head())
    else:
        path_viz_df = pd.DataFrame(columns=["Door1", "Door2", "PathWidth"])
        logger.info("DEBUG: No path weights generated")

    logger.info(f"Prepared {len(path_viz_df)} path visualization records")
    return path_viz_df


def enrich_data_with_results(
    df: pd.DataFrame, device_attributes: pd.DataFrame
) -> pd.DataFrame:
    """Enrich original data with processing results"""
    try:
        # Get column names with error handling
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]  # 'DoorID (Device Name)'
        timestamp_col = REQUIRED_INTERNAL_COLUMNS[
            "Timestamp"
        ]  # 'Timestamp (Event Time)'
    except (KeyError, NameError) as e:
        raise DataProcessingError(f"Required column constants not found: {str(e)}")

    # Validate columns exist
    if doorid_col not in df.columns:
        raise DataProcessingError(
            f"Required column '{doorid_col}' not found in dataframe"
        )

    enriched_df = df.copy()

    # Add device attributes - make sure device_attributes uses the same column name
    if "DoorID" in device_attributes.columns:
        device_info = device_attributes.set_index("DoorID")[
            ["FinalGlobalDeviceDepth", "IsOfficialEntrance", "Floor", "SecurityLevel"]
        ].to_dict("index")
    else:
        logger.warning(
            f"Device attributes missing expected column 'DoorID'. Available: {list(device_attributes.columns)}"
        )
        device_info = {}

    # Add device attributes to enriched dataframe
    enriched_df["DeviceDepth"] = enriched_df[doorid_col].map(
        lambda x: device_info.get(x, {}).get("FinalGlobalDeviceDepth", 0)
    )
    enriched_df["IsEntrance"] = enriched_df[doorid_col].map(
        lambda x: device_info.get(x, {}).get("IsOfficialEntrance", False)
    )
    enriched_df["Floor"] = enriched_df[doorid_col].map(
        lambda x: device_info.get(x, {}).get("Floor", "1")
    )
    enriched_df["SecurityLevel"] = enriched_df[doorid_col].map(
        lambda x: device_info.get(x, {}).get("SecurityLevel", "green")
    )

    # Add date-based columns for analysis
    if timestamp_col in enriched_df.columns:
        enriched_df["Date"] = enriched_df[timestamp_col].dt.date
        enriched_df["Hour"] = enriched_df[timestamp_col].dt.hour
        enriched_df["DayOfWeek"] = enriched_df[timestamp_col].dt.day_name()

    # Add movement classification
    enriched_df["EventType_UserDay"] = "MOVEMENT"  # Simplified classification

    logger.info(f"Enriched data with {len(enriched_df)} records")
    return enriched_df


if __name__ == "__main__":
    # quick smoke-test or sample config here
    pass
