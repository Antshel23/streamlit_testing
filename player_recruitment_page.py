import streamlit as st
import pandas as pd
import numpy as np
import base64
import matplotlib.pyplot as plt
from pizza_plot import plot_player
import io

class PlayerRecruitmentPage:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Load players data from CSV"""
        try:
            self.df = pd.read_csv('players.csv')
            print(f"Loaded {len(self.df)} player records")
        except FileNotFoundError:
            st.error("players.csv file not found!")
            self.df = pd.DataFrame()
    
    def get_base64_image(self, image_path):
        """Convert image to base64 string"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            return None
    
    def get_player_data(self, player_name):
        """Get data for a specific player"""
        player_data = self.df[self.df['player_name'] == player_name]
        if not player_data.empty:
            return player_data.iloc[0]
        return None
    
    def render_header(self):
        """Render the same header as the main page"""
        # Get base64 logo
        logo_b64 = self.get_base64_image("burton.png")
        
        st.markdown(f"""
        <div class="header-container">
            <div class='header-layout'>
                <div class='header-logo-section'>
                    {f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else '<div style="font-size: 1.5rem; margin-right: 0.5rem;">⚽</div>'}
                </div>
                <div class='header-search-section'>
                    <input type='text' placeholder='Search teams, players, stats...' />
                </div>
                <div class='header-nav-section'>
                    <div class='header-nav-button'>
                        <span class='header-nav-button-icon'>📊</span>
                        Opposition Research
                    </div>
                    <div class='header-nav-button active'>
                        <span class='header-nav-button-icon'>👤</span>
                        Player Recruitment
                    </div>
                    <div class='header-nav-button'>
                        <span class='header-nav-button-icon'>📊</span>
                        Post-Match Analysis
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_pizza_plot(self, player_name, team_name, position_group):
        """Create a pizza plot for the player and return as base64"""
        if self.df.empty:
            return None
        
        try:
            # Import here to modify the plot function
            import pandas as pd
            import matplotlib.pyplot as plt
            from mplsoccer import PyPizza, FontManager
            import numpy as np
            
            # Filter data for the specific player
            player_data = self.df[
                (self.df['player_name'] == player_name) &
                (self.df['team_name'] == team_name)
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

            # Create readable parameter names
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

            # Create colors based on percentile values using red-yellow-green-blue scale
            # Thresholds: 0-25 (red), 25-60 (yellow), 60-80 (green), 80-100 (wigan blue)
            def get_performance_color(value):
                """Get color based on percentile using the exact colorscale from bar charts"""
                # Colorscale: [[0, '#DC143C'], [0.25, '#FF6B35'], [0.5, '#FFD700'], [0.75, '#90EE90'], [1.0, '#32CD32']]
                # Map 0-100 percentile to the exact gradient used in bar charts
                
                # Normalize value to 0-1 range for colorscale interpolation
                normalized = value / 100.0
                
                if normalized <= 0.25:
                    # Interpolate between '#DC143C' (dark red) and '#FF6B35' (orange-red)
                    intensity = normalized / 0.25
                    start_color = np.array([220, 20, 60])    # #DC143C
                    end_color = np.array([255, 107, 53])     # #FF6B35
                elif normalized <= 0.5:
                    # Interpolate between '#FF6B35' (orange-red) and '#FFD700' (gold)
                    intensity = (normalized - 0.25) / 0.25
                    start_color = np.array([255, 107, 53])   # #FF6B35
                    end_color = np.array([255, 215, 0])      # #FFD700
                elif normalized <= 0.75:
                    # Interpolate between '#FFD700' (gold) and '#90EE90' (light green)
                    intensity = (normalized - 0.5) / 0.25
                    start_color = np.array([255, 215, 0])    # #FFD700
                    end_color = np.array([144, 238, 144])    # #90EE90
                else:
                    # Interpolate between '#90EE90' (light green) and '#32CD32' (lime green)
                    intensity = (normalized - 0.75) / 0.25
                    start_color = np.array([144, 238, 144])  # #90EE90
                    end_color = np.array([50, 205, 50])      # #32CD32
                
                # Linear interpolation between colors
                color = start_color + (end_color - start_color) * intensity
                return f"#{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}"

            # Create performance colors for slice values
            slice_colors = [get_performance_color(value) for value in formatted_values]

            # Create figure with main page background gradient
            # Using the same gradient as the main page CSS
            main_page_bg = "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)"
            # For matplotlib, we'll use the middle color of the gradient
            bg_color = "#1a1a2e"  # Middle color from main page gradient
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            fig.patch.set_facecolor(bg_color)

            # Create pizza plot with smaller inner circle
            baker = PyPizza(
                params=params,
                background_color="#1a1a1a",  # Darker background
                straight_line_color="#ffffff",
                straight_line_lw=0,
                last_circle_lw=5,
                other_circle_lw=1,
                inner_circle_size=0  # Much smaller inner circle
            )

            baker.make_pizza(
                formatted_values,
                ax=ax,
                color_blank_space=["#1a1a1a"] * len(selected_columns),
                slice_colors=slice_colors,  # Performance colors for slices
                value_colors=["#FFFFFF"] * len(selected_columns),
                value_bck_colors=["#1a1a1a"] * len(selected_columns),  # Match darker background
                blank_alpha=0.98,  # Higher alpha for darker background
                kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=2),
                kwargs_params=dict(color="#FFFFFF", fontsize=12, va="center"),
                kwargs_values=dict(color="#FFFFFF", fontsize=12, zorder=3, 
                                   bbox=dict(edgecolor="#FFFFFF", facecolor="#2b2b2b", 
                                           boxstyle="round,pad=0.2", lw=2))
            )
            
            # Convert to base64 with main page background
            buf = io.BytesIO()
            fig.savefig(buf, format='png', facecolor=bg_color, edgecolor='none', 
                       bbox_inches='tight', dpi=150, transparent=False, pad_inches=0)
            buf.seek(0)
            
            # Encode to base64
            plot_base64 = base64.b64encode(buf.read()).decode()
            plt.close(fig)
            
            return plot_base64
            
        except Exception as e:
            st.error(f"Error creating pizza plot: {str(e)}")
            return None
    
    def render_player_profile(self, player_name):
        """Render player profile with picture, logo, and single line text"""
        player_data = self.get_player_data(player_name)
        
        if player_data is None:
            st.error(f"Player {player_name} not found!")
            return
        
        # Extract key data
        team_name = player_data['team_name']
        position_group = player_data['position_group']
        
        # Section title for Player Info
        st.markdown("""
        <div style="color: white; font-size: 1.2rem; margin-bottom: 10px; margin-top: 0px; 
                    font-weight: 600; text-decoration: underline; text-decoration-color: #8B5CF6; 
                    text-underline-offset: 4px;">Player Info</div>
        """, unsafe_allow_html=True)
        
        # Single row: player picture | club logo | name | club | position text
        # Create columns for player face, badge, then 3 headlines (name, club, position)
        # Using same structure as working row in app.py
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            # Player face (bigger and on far left)
            player_img_b64 = self.get_base64_image("charlie_webster.png")
            if player_img_b64:
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                    <img src="data:image/png;base64,{player_img_b64}" 
                         style="height: 120px; width: 120px; border-radius: 50%; object-fit: cover; 
                                box-shadow: 0 8px 25px rgba(0,0,0,0.3); border: 3px solid rgba(255,255,255,0.3);">
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Club badge
            club_logo_b64 = self.get_base64_image("burton.png")
            if club_logo_b64:
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                    <img src="data:image/png;base64,{club_logo_b64}" 
                         style="height: 120px; width: auto; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            # 3 headlines (name, club, position) - mimicking the stat boxes structure
            # Create three columns for the headlines
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                    border-radius: 15px;
                    padding: 0.8rem 0.6rem;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    transition: transform 0.2s ease;
                ">
                    <div style="
                        font-size: 0.8rem;
                        font-weight: 500;
                        color: rgba(255, 255, 255, 0.8);
                        margin-bottom: 0.4rem;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    ">Player Name</div>
                    <div style="
                        font-size: 1.6rem;
                        color: white;
                        font-weight: 800;
                        margin-bottom: 0.2rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    ">{player_name}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with stat_col2:
                st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                    border-radius: 15px;
                    padding: 0.8rem 0.6rem;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    transition: transform 0.2s ease;
                ">
                    <div style="
                        font-size: 0.8rem;
                        font-weight: 500;
                        color: rgba(255, 255, 255, 0.8);
                        margin-bottom: 0.4rem;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    ">Club</div>
                    <div style="
                        font-size: 1.6rem;
                        color: white;
                        font-weight: 800;
                        margin-bottom: 0.2rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    ">{team_name}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with stat_col3:
                st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                    border-radius: 15px;
                    padding: 0.8rem 0.6rem;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    transition: transform 0.2s ease;
                ">
                    <div style="
                        font-size: 0.8rem;
                        font-weight: 500;
                        color: rgba(255, 255, 255, 0.8);
                        margin-bottom: 0.4rem;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    ">Position</div>
                    <div style="
                        font-size: 1.6rem;
                        color: white;
                        font-weight: 800;
                        margin-bottom: 0.2rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    ">{position_group}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Add spacing before sections
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # Create two columns for radar and scout report
        radar_col, report_col = st.columns([1, 1])
        
        with radar_col:
            # Section title with underline (like app.py)
            st.markdown("""
            <div style="color: white; font-size: 1.2rem; margin-bottom: 10px; margin-top: 0px; 
                        font-weight: 600; text-decoration: underline; text-decoration-color: #8B5CF6; 
                        text-underline-offset: 4px;">Radar</div>
            """, unsafe_allow_html=True)
            
            # Radar plot
            pizza_plot_b64 = self.create_pizza_plot(player_name, team_name, position_group)
            
            if pizza_plot_b64:
                st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center;">
                    <img src="data:image/png;base64,{pizza_plot_b64}" 
                         style="width: 100%; max-width: 600px; background: transparent;
                                border: 3px solid white; border-radius: 15px; padding: 10px;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Could not generate performance radar chart")
        
        with report_col:
            # Section title with underline (like app.py)
            st.markdown("""
            <div style="color: white; font-size: 1.2rem; margin-bottom: 10px; margin-top: 0px; 
                        font-weight: 600; text-decoration: underline; text-decoration-color: #8B5CF6; 
                        text-underline-offset: 4px;">Scout Report</div>
            """, unsafe_allow_html=True)
            
            # Three report boxes: In Possession, Out of Possession, Summary
            # In Possession box
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                        border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
                        border: 1px solid rgba(255, 255, 255, 0.15);">
                <h4 style="color: white; margin-bottom: 0.5rem; font-size: 1rem;">In Possession</h4>
                <textarea style="width: 100%; height: 80px; background: rgba(255,255,255,0.05); 
                                border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; 
                                color: white; padding: 0.5rem; font-size: 0.9rem; resize: vertical;"
                          placeholder="..."></textarea>
            </div>
            """, unsafe_allow_html=True)
            
            # Out of Possession box
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                        border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
                        border: 1px solid rgba(255, 255, 255, 0.15);">
                <h4 style="color: white; margin-bottom: 0.5rem; font-size: 1rem;">Out of Possession</h4>
                <textarea style="width: 100%; height: 80px; background: rgba(255,255,255,0.05); 
                                border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; 
                                color: white; padding: 0.5rem; font-size: 0.9rem; resize: vertical;"
                          placeholder="..."></textarea>
            </div>
            """, unsafe_allow_html=True)
            
            # Summary box
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(20, 25, 40, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
                        border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
                        border: 1px solid rgba(255, 255, 255, 0.15);">
                <h4 style="color: white; margin-bottom: 0.5rem; font-size: 1rem;">Summary</h4>
                <textarea style="width: 100%; height: 80px; background: rgba(255,255,255,0.05); 
                                border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; 
                                color: white; padding: 0.5rem; font-size: 0.9rem; resize: vertical;"
                          placeholder="..."></textarea>
            </div>
            """, unsafe_allow_html=True)
            
            # Add Scout Report button
            if st.button("Submit", use_container_width=True, key=f"scout_report_{player_name}"):
                st.success(f"✅ Scout report submitted for {player_name}!")
                st.balloons()
    
    def run(self):
        """Main method to run the player recruitment page"""
        # Add CSS for consistent styling and mobile responsiveness
        st.markdown("""
        <style>
            /* Navigation button styling - consistent with main page */
            div[data-testid="column"] .stButton > button {
                background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
                color: white !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                font-weight: 600 !important;
                padding: 10px 16px !important;
                font-size: 0.9rem !important;
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
                height: auto !important;
                min-height: 40px !important;
            }
            
            div[data-testid="column"] .stButton > button:hover {
                background: linear-gradient(135deg, #9333EA 0%, #8B5CF6 100%) !important;
                border: 1px solid rgba(255,255,255,0.4) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
            }
            
            /* Consistent padding with main page */
            .main .block-container {
                padding-top: 80px !important;
            }
            
            /* Mobile-specific padding reduction */
            @media (max-width: 768px) {
                .main .block-container {
                    padding-top: 70px !important;
                }
                
                .stMarkdown > div {
                    margin-bottom: 1rem !important;
                }
                
                .stColumns > div {
                    padding: 0.5rem 0 !important;
                }
                
                .element-container {
                    margin-bottom: 0.8rem !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Main content
        # Charlie Webster profile
        self.render_player_profile("Charlie Webster")