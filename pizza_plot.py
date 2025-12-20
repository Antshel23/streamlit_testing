import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, FontManager
import numpy as np

def get_blue_shade(value):
    """Return a blue color that darkens with higher values (0-100)."""
    # Define shades of blue
    min_blue = np.array([173, 216, 230])  # (LightSkyBlue)
    max_blue = np.array([20, 20, 132])      # (DarkBlue)

    # Interpolate color intensity into hexadecimal based on value (0-100)
    color = min_blue + (max_blue - min_blue) * (value / 100)
    return f"#{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}"

def plot_player(df, player_name, position_group, team_name):
    """
    Create a radar plot for a specific player
    
    Parameters:
    - df: DataFrame with player data
    - player_name: Name of the player
    - position_group: Position group from your data
    - team_name: Team name
    """
    
    # Filter data for the specific player
    player_data = df[
        (df['player_name'] == player_name) &
        (df['team_name'] == team_name)
    ]

    if player_data.empty:
        print(f"N/A: Player {player_name} not found for {team_name}.")
        return None

    # Position-specific percentile columns for radar plots
    position_columns = {
        'Full Back': [
            "obv_defensive_action_percentile", "dribbled_past_percentile", "successful_crosses_percentile",
            "op_xa_percentile", "obv_pass_percentile", "dribbles_percentile",
            "obv_dribble_carry_percentile"
        ],
        'Central Midfield': [
            "aggressive_actions_percentile", "ball_recoveries_percentile", "obv_defensive_action_percentile",
            "deep_progressions_percentile", "successful_long_balls_percentile", "obv_pass_percentile",
            "op_xa_percentile", "through_balls_percentile", "obv_dribble_carry_percentile", "np_xg_percentile"
        ]
    }
    
    # Fall back DEFAULT columns if position not found
    default_columns = [
        "tackles_percentile", "interceptions_percentile", "dribbles_percentile",
        "key_passes_percentile", "xa_percentile", "np_xg_percentile",
        "passes_percentile", "successful_passes_percentile", "aerials_percentile",
        "ball_recoveries_percentile"
    ]

    # Select columns based on position
    selected_columns = position_columns.get(position_group, default_columns)
    
    # Get percentile values for selected columns
    values = player_data[selected_columns].values.flatten()

    # Format values into integers
    formatted_values = [int(round(v)) if not np.isnan(v) else 0 for v in values]

    # Create readable parameter names for displaying MFs on plot
    param_names = {
        "aggressive_actions_percentile": "Aggressive Actions",
        "ball_recoveries_percentile": "Ball Recoveries", 
        "obv_defensive_action_percentile": "Defensive OBV",
        "deep_progressions_percentile": "Deep Progressions",
        "successful_long_balls_percentile": "Successful Long Balls",
        "obv_pass_percentile": "Pass OBV",
        "op_xa_percentile": "OP xA",
        "through_balls_percentile": "Through Balls",
        "obv_dribble_carry_percentile": "Dribble OBV",
        "np_xg_percentile": "Non-pen xG"
    }
    
    params = [param_names.get(col, col.replace('_percentile', '').replace('_', ' ').title()) 
              for col in selected_columns]

    # Create colors based on percentile values
    slice_colors = [get_blue_shade(value) for value in formatted_values]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0E1118")

    # Create pizza plot
    baker = PyPizza(
        params=params,
        background_color="#2b2b2b",
        straight_line_color="#2b2b2b",
        straight_line_lw=1,
        last_circle_lw=0,
        other_circle_lw=0,
        inner_circle_size=20
    )

    baker.make_pizza(
        formatted_values,
        ax=ax,
        color_blank_space="same",
        slice_colors=slice_colors,
        value_colors=["#FFFFFF"] * len(selected_columns),
        value_bck_colors=["#2b2b2b"] * len(selected_columns),
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
        kwargs_params=dict(color="#FFFFFF", fontsize=10.5, va="center"),
        kwargs_values=dict(color="#FFFFFF", fontsize=11, zorder=3, 
                           bbox=dict(edgecolor="#FFFFFF", facecolor="#2b2b2b", 
                                   boxstyle="round,pad=0.2", lw=1))
    )

    # Add title and subtitle
    fig.text(0.515, 0.975, player_name, size=22, ha="center", 
             fontproperties=FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf').prop, 
             color="#FFFFFF")
    
    fig.text(0.515, 0.933, f"{team_name} | 25/26 | {position_group}", size=18, ha="center", 
             fontproperties=FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab[wght].ttf').prop, 
             color="#FFFFFF")

    return fig