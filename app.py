import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from PIL import Image

# Import player recruitment page
try:
    from player_recruitment_page import PlayerRecruitmentPage
except ImportError:
    PlayerRecruitmentPage = None

# Configure page
st.set_page_config(
    page_title="Latics Portal",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check URL parameters for navigation
query_params = st.query_params
if 'page' in query_params:
    current_page = query_params['page']
else:
    current_page = 'Opposition Research'

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = current_page

# Custom CSS for styling
st.markdown("""
<style>
    /* Dark theme styling - remove all default margins/padding */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove any top spacing from Streamlit containers */
    .stApp > div:first-child {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stApp > div:first-child > div:first-child {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Header styling */
    .team-header {
        background: linear-gradient(90deg, rgba(116, 6, 181, 0.1) 0%, rgba(28, 121, 209, 0.1) 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Section styling */
    .stat-section {
        background: linear-gradient(135deg, rgba(116, 6, 181, 0.05) 0%, rgba(0, 0, 0, 0.2) 100%);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin-bottom: 15px;
        backdrop-filter: blur(5px);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid;
        margin-bottom: 10px;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
        margin-top: 0px;
        text-decoration: underline;
        text-decoration-color: #8B5CF6;
        text-underline-offset: 4px;
    }
    
    /* Adjust body for fixed header */
    body {
        padding-top: 90px !important;
    }
    
    /* Allow normal Streamlit container behavior */
    .main .block-container {
        padding-top: 90px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1600px !important;
        margin: 0 auto !important;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom selectbox */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 10px;
    }
    
    /* Header styling for full-width */
    .header-container {
        background: linear-gradient(90deg, #1758B1 0%, #134a8a 100%);
        border-bottom: 3px solid #134a8a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-top: 0;
        margin-bottom: 0;
        padding: 0.75rem 2rem;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        height: auto;
        min-height: 70px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
    }
    
    /* Header navigation styling */
    .header-nav {
        width: 100%;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0;
    }
    
    /* Header logo section */
    .header-logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        backdrop-filter: blur(10px);
        flex-shrink: 0;
        height: fit-content;
    }
    
    .header-logo img {
        height: 35px;
        width: auto;
    }
    
    .header-club-name {
        color: white;
        font-size: 1rem;
        font-weight: 700;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    /* Header search bar */
    .header-search {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 300px;
        max-width: 30vw;
        display: flex;
        align-items: center;
    }
    
    .header-search input {
        width: 100%;
        padding: 0.5rem 1rem;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        background: rgba(255,255,255,0.1);
        color: white;
        font-size: 0.9rem;
        outline: none;
        transition: all 0.3s ease;
    }
    
    .header-search input::placeholder {
        color: rgba(255,255,255,0.6);
    }
    
    .header-search input:focus {
        border-color: rgba(255,255,255,0.6);
        background: rgba(255,255,255,0.15);
    }
    
    /* Header navigation buttons */
    .header-nav-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-shrink: 0;
        height: fit-content;
    }
    
    .header-nav-button {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        background: rgba(255,255,255,0.95);
        color: #1758B1;
        border: none;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-bottom: 2px solid transparent;
        white-space: nowrap;
        user-select: none;
        min-height: 36px;
        height: 36px;
        max-height: 36px;
        box-sizing: border-box;
        justify-content: center;
        flex-shrink: 0;
        min-width: fit-content;
    }
    
    .header-nav-button:hover {
        background: rgba(255,255,255,1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid rgba(23, 88, 177, 0.3);
    }
    
    .header-nav-button.active {
        background: rgba(255,255,255,1);
        color: #1758B1;
        border: 2px solid #1758B1;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .header-nav-button-icon {
        margin-right: 8px;
        font-size: 1rem;
    }
    
    /* Content styling - apply to individual sections */
    .chart-container {
        margin: 1rem 2rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Mobile responsive styles */
    @media (max-width: 1024px) {
        .header-container {
            height: auto;
            min-height: 90px;
            padding: 0.75rem 1rem;
        }
        
        .header-nav {
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: flex-start;
        }
        
        .header-logo {
            order: 1;
            flex: 0 0 auto;
        }
        
        .header-nav-section {
            order: 2;
            flex: 0 0 auto;
            gap: 0.5rem;
        }
        
        .header-search {
            position: static;
            transform: none;
            order: 3;
            flex: 1 0 100%;
            margin: 0.75rem 0 0 0;
            max-width: none;
            width: 100%;
        }
        
        .header-nav-button {
            padding: 6px 10px;
            font-size: 0.8rem;
            min-height: 36px;
            height: 36px;
            max-height: 36px;
            box-sizing: border-box;
            justify-content: center;
            flex-shrink: 0;
        }
        
        body {
            padding-top: 130px !important;
        }
        
        .main .block-container {
            padding-top: 130px !important;
        }
    }
    
    @media (max-width: 768px) {
        .header-container {
            padding: 0.5rem 0.75rem;
            min-height: 100px;
        }
        
        .header-nav {
            gap: 0.5rem;
        }
        
        .header-logo {
            padding: 0.4rem 0.75rem;
        }
        
        .header-logo img {
            height: 28px !important;
        }
        
        .header-club-name {
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .header-nav-button {
            padding: 5px 8px;
            font-size: 0.7rem;
            border-radius: 4px;
            min-height: 36px;
            height: 36px;
            max-height: 36px;
            box-sizing: border-box;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .header-nav-button-icon {
            margin-right: 4px;
            font-size: 0.8rem;
        }
        
        .header-search input {
            padding: 0.5rem 0.75rem;
            font-size: 0.85rem;
            border-radius: 15px;
        }
        
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 140px !important;
        }
        
        body {
            padding-top: 140px !important;
        }
    }
    
    @media (max-width: 480px) {
        .header-container {
            padding: 0.4rem 0.5rem;
            min-height: 110px;
        }
        
        .header-nav {
            gap: 0.4rem;
        }
        
        .header-logo {
            gap: 0.4rem;
            padding: 0.3rem 0.5rem;
        }
        
        .header-logo img {
            height: 24px !important;
        }
        
        .header-club-name {
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .header-nav-section {
            gap: 0.25rem;
            flex-wrap: wrap;
        }
        
        .header-nav-button {
            padding: 4px 6px;
            font-size: 0.65rem;
            border-radius: 3px;
            min-height: 36px;
            height: 36px;
            max-height: 36px;
            box-sizing: border-box;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .header-nav-button-icon {
            margin-right: 2px;
            font-size: 0.7rem;
        }
        
        .header-search {
            margin: 0.5rem 0 0 0;
        }
        
        .header-search input {
            font-size: 0.8rem;
            padding: 0.4rem 0.6rem;
            border-radius: 12px;
        }
        
        .main .block-container {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
            padding-top: 150px !important;
        }
        
        body {
            padding-top: 150px !important;
        }
    }
    
    /* Extra small mobile optimization */
    @media (max-width: 320px) {
        .header-container {
            padding: 0.3rem 0.4rem;
            min-height: 120px;
        }
        
        .header-logo {
            padding: 0.2rem 0.4rem;
        }
        
        .header-logo img {
            height: 20px !important;
        }
        
        .header-club-name {
            font-size: 0.7rem;
        }
        
        .header-nav-button {
            padding: 3px 5px;
            font-size: 0.6rem;
        }
        
        .header-nav-button-icon {
            display: none;
        }
        
        .header-search input {
            font-size: 0.75rem;
            padding: 0.35rem 0.5rem;
        }
        
        .main .block-container {
            padding-top: 160px !important;
        }
        
        body {
            padding-top: 160px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

class FootballDashboard:
    def __init__(self):
        self.data = self.load_data()
        self.teams = sorted([team['team'] for team in self.data['teams']])
        
        # Define sections and metrics (mapped to CSV columns)
        self.sections = {
            'buildUp': {
                'title': 'Build Up',
                'color': '#7406B5',
                'metrics': [
                    {'name': 'Retain Possession', 'key': 'Possession'},
                    {'name': 'Directness', 'key': 'Long pass %'},
                    {'name': 'Build Up Safety', 'key': 'Low losses'},
                    {'name': 'Def -> Mid 3rd Progression', 'key': 'Progressive pass success %'},
                    {'name': 'Mid -> Final 3rd Progression', 'key': 'Final third pass success %'},
                    {'name': 'Final 3rd Entries', 'key': 'Total box entries'}
                ]
            },
            'chanceCreation': {
                'title': 'Chance Creation',
                'color': '#D50033',
                'metrics': [
                    {'name': 'Wide Crosses', 'key': 'Box entry via cross'},
                    {'name': '1v1 Dribbles', 'key': 'Box entry via run'},
                    {'name': 'Interplay in 10 space', 'key': 'Deep completed passes'},
                    {'name': 'Att Transition', 'key': 'Total counterattacks'},
                    {'name': 'Set-piece efficiency', 'key': 'Set piece shot %'},
                ]
            },
            'press': {
                'title': 'Press',
                'color': '#1C79D1',
                'metrics': [
                    {'name': 'Press Intensity', 'key': 'PPDA'},
                    {'name': 'Press Efficiency', 'key': 'Oppo Progressive pass success %'},
                    {'name': 'High Regains', 'key': 'High recoveries'},
                    {'name': 'Central Regains', 'key': 'Med recoveries'},
                    {'name': 'Def Transition', 'key': 'Oppo Total counterattacks'}
                ]
            },
            'block': {
                'title': 'Block',
                'color': '#1A988B',
                'metrics': [
                    {'name': 'Final Third Restriction', 'key': 'Oppo Final third pass success %'},
                    {'name': 'Chance Restriction', 'key': 'Oppo Positional attacks leading to shot %'},
                    {'name': 'Aerial Dominance', 'key': 'Aerial duel success %'},
                    {'name': 'Def Set-piece Efficiency', 'key': 'Oppo Set piece shot %'},
                ]
            }
        }
    
    @st.cache_data
    def load_data(_self):
        """Load team stats from CSV file and calculate percentiles"""
        try:
            # Read CSV file
            df = pd.read_csv('leagueone.csv')
            
            # Calculate percentiles for each numeric column
            percentile_df = df.copy()
            for col in df.columns:
                if col != 'Team' and pd.api.types.is_numeric_dtype(df[col]):
                    # Check if this is an opponent stat or PPDA (where lower is better)
                    if col.startswith('Oppo') or col == 'PPDA':
                        # For opponent stats and PPDA, calculate inverse percentiles
                        # Handle zero/negative values by adding small epsilon
                        safe_values = df[col].replace(0, 0.001)  # Replace 0 with small value
                        safe_values = safe_values.abs()  # Ensure positive values
                        inverse_values = 1 / safe_values
                        percentile_df[f'{col}_percentile'] = inverse_values.rank(pct=True) * 100
                    else:
                        # Normal percentile calculation for regular stats
                        percentile_df[f'{col}_percentile'] = df[col].rank(pct=True) * 100
            
            # Convert to the expected format
            teams = []
            for _, row in percentile_df.iterrows():
                team_stats = {}
                for col in df.columns:
                    if col != 'Team' and pd.api.types.is_numeric_dtype(df[col]):
                        team_stats[col] = {
                            'value': row[col],
                            'percentile': row[f'{col}_percentile']
                        }
                
                teams.append({
                    'team': row['Team'],
                    'stats': team_stats
                })
            
            return {'teams': teams}
            
        except FileNotFoundError:
            st.error("team_stats.csv file not found!")
            return {"teams": []}
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return {"teams": []}
    
    def get_base64_image(self, image_path):
        """Convert image to base64 string for embedding in HTML"""
        import os
        try:
            # Try current directory first (for deployment)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img_bytes = img_file.read()
                    img_b64 = base64.b64encode(img_bytes).decode()
                    return img_b64
            # Fallback to local path
            elif os.path.exists(f'/Users/as/Personal projects/wigan/{image_path}'):
                with open(f'/Users/as/Personal projects/wigan/{image_path}', 'rb') as img_file:
                    img_bytes = img_file.read()
                    img_b64 = base64.b64encode(img_bytes).decode()
                    return img_b64
        except Exception as e:
            st.warning(f"Could not load image: {e}")
        return ""
    
    def get_team_logo(self, team_name):
        """Get team logo based on team name"""
        # Convert team name to lowercase and replace spaces with nothing for filename
        logo_filename = team_name.lower().replace(' ', '').replace('fc', '').replace('town', '').replace('united', '').replace('city', '') + '.png'
        return self.get_base64_image(logo_filename)
    
    def get_team_data(self, team_name):
        """Get data for a specific team"""
        for team in self.data['teams']:
            if team['team'] == team_name:
                return team
        return None
    
    def get_league_rank(self, metric_key, team_name):
        """Calculate league rank for a metric"""
        values = []
        for team in self.data['teams']:
            if metric_key in team['stats']:
                values.append((team['stats'][metric_key]['value'], team['team']))
        
        # Sort by value (descending for most metrics)
        reverse_sort = True
        # For these metrics, lower is better
        lower_is_better_metrics = [
            'Oppo xG', 'PPDA', 'Oppo Total counterattacks', 'Oppo Set piece shot %',
            'Low losses', 'Med Losses', 'High losses', 'Oppo Goals', 'Conceded goals',
            'Oppo Total shots', 'Oppo SOT against', 'Oppo Total box entries',
            'Oppo Box entry via run', 'Oppo Box entry via cross', 'Oppo Penalty area touches',
            'Oppo Positional attacks leading to shot %', 'Oppo Final third pass success %'
        ]
        
        if metric_key in lower_is_better_metrics:
            reverse_sort = False
            
        values.sort(key=lambda x: x[0], reverse=reverse_sort)
        
        for rank, (value, name) in enumerate(values, 1):
            if name == team_name:
                return rank
        return len(values)
    
    def get_ordinal_suffix(self, number):
        """Get ordinal suffix (st, nd, rd, th) for a number"""
        if 10 <= number % 100 <= 20:
            return "th"
        else:
            suffix_map = {1: "st", 2: "nd", 3: "rd"}
            return suffix_map.get(number % 10, "th")
    
    def get_percentile_color(self, percentile):
        """Get color based on percentile using red-green scale"""
        if percentile >= 75:
            return '#32CD32'  # Green (top quartile)
        elif percentile >= 50:
            return '#FFD700'  # Gold (above average)
        elif percentile >= 25:
            return '#FF6B35'  # Orange-red (below average)
        else:
            return '#DC143C'  # Dark red (bottom quartile)
    
    def get_rank_color(self, rank, total_teams=24):
        """Get color based on league rank (1st = green, last = red)"""
        # Convert rank to percentile (1st = 100th percentile, last = 0th percentile)
        percentile = ((total_teams - rank + 1) / total_teams) * 100
        
        if percentile >= 75:
            return '#32CD32'  # Green (top quartile)
        elif percentile >= 50:
            return '#FFD700'  # Gold (above average)
        elif percentile >= 25:
            return '#FF6B35'  # Orange-red (below average)
        else:
            return '#DC143C'  # Dark red (bottom quartile)
    
    def get_section_rating(self, team_name, section_key):
        """Calculate median percentile rating for a section"""
        team_data = self.get_team_data(team_name)
        if not team_data:
            return 0
            
        percentiles = []
        for metric in self.sections[section_key]['metrics']:
            if metric['key'] in team_data['stats']:
                percentiles.append(team_data['stats'][metric['key']]['percentile'])
        
        if not percentiles:
            return 0
            
        percentiles.sort()
        middle = len(percentiles) // 2
        
        if len(percentiles) % 2 == 0:
            return round((percentiles[middle - 1] + percentiles[middle]) / 2)
        else:
            return round(percentiles[middle])
    
    def create_gauge_chart(self, value, title, color):
        """Create a gauge chart for section ratings"""
        # Color based on percentile performance (higher percentile = better = green)
        if value >= 75:
            gauge_color = '#32CD32'  # Green (top quartile)
        elif value >= 50:
            gauge_color = '#FFD700'  # Gold (above average)
        elif value >= 25:
            gauge_color = '#FF6B35'  # Orange-red (below average)
        else:
            gauge_color = '#DC143C'  # Dark red (bottom quartile)
            
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 11, 'color': 'white'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': gauge_color},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.3)",
                'steps': [
                    {'range': [0, 25], 'color': "rgba(220, 20, 60, 0.2)"},
                    {'range': [25, 50], 'color': "rgba(255, 107, 53, 0.2)"},
                    {'range': [50, 75], 'color': "rgba(255, 215, 0, 0.2)"},
                    {'range': [75, 100], 'color': "rgba(50, 205, 50, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 2},
                    'thickness': 0.75,
                    'value': 90
                }
            },
            number = {'font': {'size': 12, 'color': 'white'}}
        ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "white"},
            height=100,
            margin=dict(l=5, r=5, t=20, b=5)
        )
        
        return fig
    
    def create_bar_chart(self, metrics_data, color, team_name):
        """Create horizontal bar chart for metrics"""
        if not metrics_data:
            return go.Figure()
            
        team_data = self.get_team_data(team_name)
        if not team_data:
            return go.Figure()
        
        names = []
        values = []
        percentiles = []
        ranks = []
        
        for metric in metrics_data:
            if metric['key'] in team_data['stats']:
                names.append(metric['name'])
                values.append(team_data['stats'][metric['key']]['value'])
                percentiles.append(team_data['stats'][metric['key']]['percentile'])
                ranks.append(self.get_league_rank(metric['key'], team_name))
        
        # Reverse the order to show metrics in reverse
        names = names[::-1]
        values = values[::-1]
        percentiles = percentiles[::-1]
        ranks = ranks[::-1]
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars with percentile-based color scale (higher percentile = better = green)
        fig.add_trace(go.Bar(
            x=percentiles,
            y=names,
            orientation='h',
            marker=dict(
                color=percentiles,
                colorscale=[[0, '#DC143C'], [0.25, '#FF6B35'], [0.5, '#FFD700'], [0.75, '#90EE90'], [1.0, '#32CD32']],
                cmin=0,
                cmax=100,
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=[f"{perc:.0f}" for perc in percentiles],
            textposition='outside',
            textfont=dict(color='white', size=12),
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "white"},
            height=260,
            margin=dict(l=10, r=50, t=5, b=5),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,255,255,0.1)',
                range=[0, 100],
                title=dict(text="Percentile Rank", font=dict(color='white', size=11)),
                tickfont=dict(color='white', size=10)
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(color='white', size=10)
            ),
            showlegend=False,
            bargap=0.3
        )
        
        return fig
    

    
    def render_sidebar(self):
        """Render the navigation sidebar"""
        with st.sidebar:
            # Sidebar styling
            st.markdown("""
            <style>
            .stSidebar {
                background: linear-gradient(135deg, #1758B1 0%, #134a8a 100%) !important;
                width: 140px !important;
                min-width: 140px !important;
                max-width: 140px !important;
            }
            .stSidebar > div:first-child {
                background: linear-gradient(135deg, #1758B1 0%, #134a8a 100%) !important;
                width: 140px !important;
                min-width: 140px !important;
                max-width: 140px !important;
                padding: 0.75rem !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
            }
            .stSidebar .element-container {
                width: 100% !important;
                display: flex !important;
                justify-content: center !important;
            }
            .stButton {
                width: 100% !important;
                display: flex !important;
                justify-content: center !important;
            }
            .stButton > button {
                padding: 6px 8px !important;
                margin: 3px 0 !important;
                background: rgba(255,255,255,0.95) !important;
                color: #1758B1 !important;
                border: none !important;
                border-radius: 4px !important;
                font-size: 0.7rem !important;
                font-weight: 500 !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
                white-space: nowrap !important;
                width: 110px !important;
                text-align: center !important;
                height: 32px !important;
                min-height: 32px !important;
                max-height: 32px !important;
                border: 1px solid transparent !important;
                box-sizing: border-box !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            .stButton > button:hover {
                background: rgba(255,255,255,1) !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
                border: 1px solid rgba(255,255,255,0.5) !important;
                transform: translateY(-1px) !important;
                width: 110px !important;
                height: 32px !important;
                min-height: 32px !important;
                max-height: 32px !important;
            }
            /* Mobile specific button sizing */
            @media (max-width: 768px) {
                .stButton > button {
                    width: 110px !important;
                    height: 32px !important;
                    min-height: 32px !important;
                    max-height: 32px !important;
                    font-size: 0.7rem !important;
                    padding: 6px 8px !important;
                }
                .stButton > button:hover {
                    width: 110px !important;
                    height: 32px !important;
                    min-height: 32px !important;
                    max-height: 32px !important;
                }
            }
            .sidebar-logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.25rem;
                background: rgba(255,255,255,0.1);
                padding: 0.4rem;
                border-radius: 6px;
                backdrop-filter: blur(10px);
                margin-bottom: 0.75rem;
                flex-direction: column;
            }
            .sidebar-logo img {
                height: 18px;
                width: auto;
            }
            .sidebar-club-name {
                color: white;
                font-size: 0.6rem;
                font-weight: 600;
                text-shadow: 0 1px 3px rgba(0,0,0,0.3);
                margin: 0;
                text-align: center;
                line-height: 1.1;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Sidebar logo and title
            logo_b64 = self.get_base64_image("wigan.png")
            st.markdown(f"""
            <div class="sidebar-logo">
                {f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else '<div style="font-size: 1.2rem;">⚽</div>'}
                <div class="sidebar-club-name">LATICS PORTAL</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation buttons
            if st.button("Opposition", key="sidebar_nav_opposition", use_container_width=True):
                st.session_state.current_page = "Opposition Research"
                st.rerun()
                
            if st.button("Recruitment", key="sidebar_nav_player", use_container_width=True):
                st.session_state.current_page = "Player Recruitment"
                st.rerun()
                
            if st.button("Game Review", key="sidebar_nav_analysis", use_container_width=True):
                st.session_state.current_page = "Post-Match Analysis"
                st.rerun()
    
    def render_header(self):
        """Render the header with logo and search bar only"""
        # Header with full-width background
        st.markdown("""
        <div class='header-container'>
            <div class='header-nav' style='justify-content: center; gap: 2rem;'>
                <div class='header-logo'>
                    {}
                    <div class='header-club-name'>LATICS PORTAL</div>
                </div>
                <div class='header-search' style='position: static; transform: none; width: 350px; max-width: none;'>
                    <input type='text' placeholder='Search teams, players, stats...' />
                </div>
            </div>
        </div>
        """.format(
            f'<img src="data:image/png;base64,{self.get_base64_image("wigan.png")}">' 
            if self.get_base64_image("wigan.png") else '<div style="font-size: 1.5rem; margin-right: 0.5rem;">⚽</div>'
        ), unsafe_allow_html=True)
    def render_section(self, section_key, selected_team):
        """Render a stats section with bar chart"""
        section = self.sections[section_key]
        
        st.markdown(f"""
        <div class="section-title" style="color: white; font-size: 1.2rem; margin-bottom: 10px; margin-top: 0px; font-weight: 600;">{section['title']}</div>
        """, unsafe_allow_html=True)
        
        # Create and display bar chart
        fig = self.create_bar_chart(section['metrics'], section['color'], selected_team)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    
    def run(self):
        """Main dashboard runner with navigation"""
        # Update session state with current page from URL
        query_params = st.query_params
        if 'page' in query_params:
            st.session_state.current_page = query_params['page']
        
        # Render sidebar navigation
        self.render_sidebar()
        
        # Header (always shown)
        with st.container():
            self.render_header()
        
        # Show different pages based on session state
        if st.session_state.current_page == 'Player Recruitment':
            if PlayerRecruitmentPage:
                player_page = PlayerRecruitmentPage()
                player_page.run()
            else:
                st.error("Player recruitment page not available")
        elif st.session_state.current_page == 'Post-Match Analysis':
            st.markdown("""
            <div style="text-align: center; margin-top: 4rem;">
                <h1 style="color: white; font-size: 2.5rem; margin-bottom: 1rem;">Post-Match Analysis</h1>
                <p style="color: rgba(255,255,255,0.7); font-size: 1.2rem;">Coming Soon...</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Default to Opposition Research
            self.run_opposition_research()
    
    def run_opposition_research(self):
        """Run the original opposition research page"""
        if not self.teams:
            st.error("No team data available!")
            return
        
        # Main content in Streamlit's default container (with margins)
        with st.container():
            # Create columns for logo, team selector and headline stats
            col1, col2, col3 = st.columns([1, 1, 3])
            
            # Initialize selected_team variable
            selected_team = None
            
            with col1:
                # Team logo (bigger and on far left)
                # We'll populate this after team selection
                pass
            
            with col2:
                # Team selector dropdown - smaller and vertically centered
                st.markdown("<div style='padding-top: 2.5rem;'></div>", unsafe_allow_html=True)
                selected_team = st.selectbox(
                    "Team",
                    self.teams,
                    index=0,
                    key="team_selector",
                    label_visibility="collapsed"
                )
            
            with col3:
                # Headline stats will be populated after team selection
                pass
            
            # Now populate the logo and stats based on selection
            with col1:
                if selected_team:
                    team_logo = self.get_team_logo(selected_team)
                    if team_logo:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                            <img src="data:image/png;base64,{team_logo}" 
                                 style="height: 120px; width: auto; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
                        </div>
                        """, unsafe_allow_html=True)
            
            with col3:
                if selected_team:
                    # Get team data for headline stats
                    team_data = self.get_team_data(selected_team)
                    if team_data and 'xG' in team_data['stats'] and 'Oppo xG' in team_data['stats']:
                        xg_rank = self.get_league_rank('xG', selected_team)
                        oppo_xg_rank = self.get_league_rank('Oppo xG', selected_team)
                        xg_percentile = team_data['stats']['xG']['percentile']
                        oppo_xg_percentile = team_data['stats']['Oppo xG']['percentile']
                        
                        # Get colors based on percentile
                        xg_color = self.get_percentile_color(xg_percentile)
                        oppo_xg_color = self.get_percentile_color(oppo_xg_percentile)
                        
                        # Create three columns for the stats boxes
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        
                        # Calculate xG difference and get league rank for it
                        xpts_value = team_data['stats']['xG']['value'] - team_data['stats']['Oppo xG']['value']
                        
                        # Calculate xG difference for all teams to get proper ranking
                        xg_diff_values = []
                        for team in self.data['teams']:
                            if 'xG' in team['stats'] and 'Oppo xG' in team['stats']:
                                team_xg_diff = team['stats']['xG']['value'] - team['stats']['Oppo xG']['value']
                                xg_diff_values.append((team_xg_diff, team['team']))
                        
                        # Sort by xG difference (descending - higher is better)
                        xg_diff_values.sort(key=lambda x: x[0], reverse=True)
                        
                        # Find rank for selected team
                        xg_diff_rank = 1
                        for rank, (value, team_name_in_list) in enumerate(xg_diff_values, 1):
                            if team_name_in_list == selected_team:
                                xg_diff_rank = rank
                                break
                        
                        # Determine zone based on rank position
                        if xg_diff_rank <= 2:
                            zone_text = "Promotion"
                            zone_color = "#32CD32"  # Green
                        elif xg_diff_rank <= 6:
                            zone_text = "Play Off"
                            zone_color = "#FFD700"  # Gold
                        elif xg_diff_rank <= 11:
                            zone_text = "Top Half"
                            zone_color = "#87CEEB"  # Light blue
                        elif xg_diff_rank <= 17:
                            zone_text = "Mid Table"
                            zone_color = "#FFA500"  # Orange
                        elif xg_diff_rank <= 20:
                            zone_text = "Relegation Threatened"
                            zone_color = "#FF6347"  # Tomato
                        else:
                            zone_text = "Relegation"
                            zone_color = "#DC143C"  # Red
                        
                        # Color based on rank
                        if xg_diff_rank <= 6:
                            xpos_color = "#32CD32"  # Green for top positions
                        elif xg_diff_rank <= 11:
                            xpos_color = "#FFD700"  # Gold for good positions
                        elif xg_diff_rank <= 17:
                            xpos_color = "#FFA500"  # Orange for mid table
                        else:
                            xpos_color = "#DC143C"  # Red for poor positions
                        
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
                                ">Expected Goals</div>
                                <div style="
                                    font-size: 1.6rem;
                                    color: {xg_color};
                                    font-weight: 800;
                                    margin-bottom: 0.2rem;
                                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                                ">{xg_rank}{self.get_ordinal_suffix(xg_rank)}</div>
                                <div style="
                                    font-size: 0.8rem;
                                    color: rgba(255, 255, 255, 0.9);
                                    font-weight: 600;
                                ">{team_data['stats']['xG']['value']:.2f}</div>
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
                                ">xG Conceded</div>
                                <div style="
                                    font-size: 1.6rem;
                                    color: {oppo_xg_color};
                                    font-weight: 800;
                                    margin-bottom: 0.2rem;
                                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                                ">{oppo_xg_rank}{self.get_ordinal_suffix(oppo_xg_rank)}</div>
                                <div style="
                                    font-size: 0.8rem;
                                    color: rgba(255, 255, 255, 0.9);
                                    font-weight: 600;
                                ">{team_data['stats']['Oppo xG']['value']:.2f}</div>
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
                                ">xPOSITION</div>
                                <div style="
                                    font-size: 1.6rem;
                                    color: {xpos_color};
                                    font-weight: 800;
                                    margin-bottom: 0.2rem;
                                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                                ">{xg_diff_rank}{self.get_ordinal_suffix(xg_diff_rank)}</div>
                                <div style="
                                    font-size: 0.8rem;
                                    color: {zone_color};
                                    font-weight: 600;
                                ">{zone_text}</div>
                            </div>
                            ''', unsafe_allow_html=True)
            
            if selected_team:
                # Add spacing before charts
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                
                # Render stats sections in a 2x2 grid
                col1, col2 = st.columns(2)
                
                with col1:
                    self.render_section('buildUp', selected_team)
                    self.render_section('press', selected_team)
                
                with col2:
                    self.render_section('chanceCreation', selected_team)
                    self.render_section('block', selected_team)

if __name__ == "__main__":
    dashboard = FootballDashboard()
    dashboard.run()