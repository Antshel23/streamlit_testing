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

# Configure page
st.set_page_config(
    page_title="Yeovil Town FC Portal",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    
    /* Allow normal Streamlit container behavior */
    .main .block-container {
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1400px !important;
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
        background: linear-gradient(90deg, #3B913F 0%, #2d7a30 100%);
        border-bottom: 3px solid #2d7a30;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-top: -1rem;
        margin-bottom: 2rem;
        padding: 1rem 2rem;
    }
    
    /* Header navigation styling */
    .header-nav {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    /* Header logo section */
    .header-logo {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255,255,255,0.1);
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .header-logo img {
        height: 50px;
        width: auto;
    }
    
    .header-club-name {
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    /* Header navigation buttons */
    .header-nav-section {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex: 1;
        justify-content: center;
    }
    
    .header-nav-title {
        color: rgba(255,255,255,0.9);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-right: 1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        white-space: nowrap;
    }
    
    .header-nav-buttons {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .header-nav-button {
        display: flex;
        align-items: center;
        padding: 10px 16px;
        background: rgba(255,255,255,0.95);
        color: #2d7a30;
        border: none;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-bottom: 3px solid transparent;
        white-space: nowrap;
    }
    
    .header-nav-button:hover {
        background: rgba(255,255,255,1);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-bottom-color: #2d7a30;
    }
    
    .header-nav-button.active {
        background: rgba(255,255,255,1);
        color: #2d7a30;
        border-bottom-color: #3B913F;
        font-weight: 700;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    .header-nav-button-icon {
        margin-right: 8px;
        font-size: 1rem;
    }
    
    /* Content styling */
    .content-section {
        padding: 1rem 0;
    }
    
    /* Mobile responsive styles */
    @media (max-width: 1024px) {
        .header-nav {
            flex-direction: column;
            gap: 1.5rem;
            padding: 1.5rem;
        }
        
        .header-nav-section {
            justify-content: flex-start;
            flex-wrap: wrap;
        }
        
        .header-nav-buttons {
            justify-content: center;
        }
        
        .header-container {
            margin-left: calc(-50vw + 50%);
            margin-top: -1rem;
            margin-bottom: 2rem;
            padding: 1rem;
        }
        
        .header-nav {
            padding: 1rem;
        }
    }
    
    @media (max-width: 768px) {
        .header-nav {
            padding: 1rem;
            gap: 1rem;
        }
        
        .header-logo {
            padding: 0.5rem 1rem;
        }
        
        .header-logo img {
            height: 40px !important;
        }
        
        .header-club-name {
            font-size: 1rem;
        }
        
        .header-nav-button {
            padding: 8px 12px;
            font-size: 0.85rem;
        }
        
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        .header-container {
            margin-left: calc(-50vw + 50%);
            margin-top: -1rem;
            margin-bottom: 2rem;
        }
    }
    
    @media (max-width: 480px) {
        .header-nav {
            padding: 0.75rem;
        }
        
        .header-logo {
            gap: 0.5rem;
            padding: 0.5rem 0.75rem;
        }
        
        .header-logo img {
            height: 35px !important;
        }
        
        .header-club-name {
            font-size: 0.9rem;
        }
        
        .header-nav-buttons {
            gap: 0.5rem;
        }
        
        .header-nav-button {
            padding: 6px 10px;
            font-size: 0.8rem;
        }
        
        .main .block-container {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }
        
        .header-container {
            margin-left: calc(-50vw + 50%);
            margin-top: -1rem;
            margin-bottom: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class FootballDashboard:
    def __init__(self):
        self.data = self.load_data()
        self.teams = sorted([team['team'] for team in self.data['teams']])
        
        # Define sections and metrics (matching your React component)
        self.sections = {
            'buildUp': {
                'title': 'Build Up',
                'color': '#7406B5',
                'metrics': [
                    {'name': 'Possession', 'key': 'Possession'},
                    {'name': 'Long Ball %', 'key': 'Long pass %'},
                    {'name': 'Build Up Safety', 'key': 'Losses low %'},
                    {'name': 'Def/Mid 3rd Progression', 'key': 'Progressive pass success %'},
                    {'name': 'Final 3rd Progression', 'key': 'Final third pass success %'},
                    {'name': 'Final 3rd Entries', 'key': 'Final third entries'}
                ]
            },
            'chanceCreation': {
                'title': 'Chance Creation',
                'color': '#D50033',
                'metrics': [
                    {'name': 'xG', 'key': 'xG'},
                    {'name': 'Wide Crosses', 'key': 'Box entry via cross'},
                    {'name': '1v1 Dribbles', 'key': 'Box entry via run'},
                    {'name': 'Interplay in 10 space', 'key': 'Deep completed passes'},
                    {'name': 'Att Transition', 'key': 'Total counterattacks'},
                    {'name': 'Set-piece efficiency', 'key': 'Set piece shot %'}
                ]
            },
            'press': {
                'title': 'Press',
                'color': '#1C79D1',
                'metrics': [
                    {'name': 'Press Intensity', 'key': 'PPDA'},
                    {'name': 'Press Efficiency', 'key': 'Oppo Progressive pass success %'},
                    {'name': 'High Regains', 'key': 'Recoveries high %'},
                    {'name': 'Central Regains', 'key': 'Recoveries med %'},
                    {'name': 'Def Transition', 'key': 'Oppo Total counterattacks'}
                ]
            },
            'block': {
                'title': 'Block',
                'color': '#1A988B',
                'metrics': [
                    {'name': 'xG Conceded', 'key': 'Oppo xG'},
                    {'name': 'Final Third Restriction', 'key': 'Oppo Final third pass success %'},
                    {'name': 'Chance Restriction', 'key': 'Oppo open play attacks per final third entry'},
                    {'name': 'Aerial Dominance', 'key': 'Aerial duel success %'},
                    {'name': 'Def Set-piece Efficiency', 'key': 'Oppo set piece shot %'}
                ]
            }
        }
    
    @st.cache_data
    def load_data(_self):
        """Load team stats from JSON file"""
        try:
            with open('team_stats.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("team_stats.json file not found!")
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
            elif os.path.exists(f'/Users/as/Personal projects/yeovil/{image_path}'):
                with open(f'/Users/as/Personal projects/yeovil/{image_path}', 'rb') as img_file:
                    img_bytes = img_file.read()
                    img_b64 = base64.b64encode(img_bytes).decode()
                    return img_b64
        except Exception as e:
            st.warning(f"Could not load image: {e}")
        return ""
    
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
        if metric_key in ['Oppo xG', 'PPDA', 'Oppo Total counterattacks', 'Oppo set piece shot %']:
            reverse_sort = False  # Lower is better for these metrics
            
        values.sort(key=lambda x: x[0], reverse=reverse_sort)
        
        for rank, (value, name) in enumerate(values, 1):
            if name == team_name:
                return rank
        return len(values)
    
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
    

    
    def render_section(self, section_key, selected_team):
        """Render a stats section with bar chart"""
        section = self.sections[section_key]
        
        st.markdown(f"""
        <h3 class="section-title" style="color: white; font-size: 1.2rem; margin-bottom: 10px; margin-top: 0px;">{section['title']}</h3>
        """, unsafe_allow_html=True)
        
        # Create and display bar chart
        fig = self.create_bar_chart(section['metrics'], section['color'], selected_team)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    
    def render_header(self):
        """Render the header with logo and navigation"""
        # Header with full-width background
        st.markdown("""
        <div class='header-container'>
            <div class='header-nav'>
                <div class='header-logo'>
                    {}
                    <div class='header-club-name'>YEOVIL TOWN FC</div>
                </div>
                <div class='header-nav-section'>
                    <div class='header-nav-title'>Analytics Portal</div>
                    <div class='header-nav-buttons'>
                        <div class='header-nav-button active'>
                            <span class='header-nav-button-icon'>🔍</span>
                            Opposition Research
                        </div>
                        <div class='header-nav-button'>
                            <span class='header-nav-button-icon'>👥</span>
                            Player Recruitment
                        </div>
                        <div class='header-nav-button'>
                            <span class='header-nav-button-icon'>📊</span>
                            Post-Match Analysis
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """.format(
            f'<img src="data:image/png;base64,{self.get_base64_image("yeovil.png")}">' 
            if self.get_base64_image("yeovil.png") else '<div style="font-size: 2rem; margin-right: 0.5rem;">⚽</div>'
        ), unsafe_allow_html=True)
    
    def run(self):
        """Main dashboard runner"""
        if not self.teams:
            st.error("No team data available!")
            return
        
        # Header in its own container (full width)
        with st.container():
            self.render_header()
        
        # Main content in Streamlit's default container (with margins)
        with st.container():
            st.markdown('<div class="content-section">', unsafe_allow_html=True)
            
            # Main content area with title
            st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h1 style='color: white; margin: 0; font-size: 2.2rem; font-weight: 700;'>
                    Opposition Research Dashboard
                </h1>
                <div style='color: rgba(255,255,255,0.8); font-size: 1rem; margin-top: 0.5rem;'>
                    Comprehensive analysis and scouting intelligence
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Team selector
            selected_team = st.selectbox(
                "Select Team",
                self.teams,
                index=0,
                key="team_selector"
            )
            
            if selected_team:
                # Render stats sections in a 2x2 grid
                col1, col2 = st.columns(2)
                
                with col1:
                    self.render_section('buildUp', selected_team)
                    self.render_section('press', selected_team)
                
                with col2:
                    self.render_section('chanceCreation', selected_team)
                    self.render_section('block', selected_team)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard = FootballDashboard()
    dashboard.run()