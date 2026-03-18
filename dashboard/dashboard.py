import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio  
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State
import joblib
import os

pio.templates.default = "plotly_dark"

discontinued_sports_df = pd.read_csv('../../include/datasets/discontinued_sports.csv')
medalists_age_df = pd.read_csv('../../include/datasets/medalists_age.csv')
olympiad_summry_df = pd.read_csv('../../include/datasets/olympiad_summry.csv')
sports_summry_df = pd.read_csv('../../include/datasets/sports_summry.csv')

models_dict = {}
try:
    models_dict['dt'] = joblib.load('../../include/models/decision_tree.pkl')
    models_dict['knn'] = joblib.load('../../include/models/knn.pkl')
    models_dict['lr'] = joblib.load('../../include/models/logistic_regression.pkl')
    models_dict['rf'] = joblib.load('../../include/models/random_forest.pkl')
    models_dict['nb'] = joblib.load('../../include/models/naive_bayes.pkl')
    models_dict['svm'] = joblib.load('../../include/models/svm.pkl')
except Exception as e:
    print(f"⚠️ Some models could not be loaded: {e}")

# Graph 1
fig1 = px.bar(discontinued_sports_df, x='contest_year', y='number_of_olympics', title='Number of Olympics per Contest Year for Discontinued Sports')
fig1.update_layout(xaxis_tickangle=-45, xaxis_title='Contest Year', yaxis_title='Number of Olympics')

# Graph 2
discontinued_sports_melted = discontinued_sports_df.melt(id_vars=['discipline'], value_vars=['gold_medals', 'silver_medals', 'bronze_medals'], var_name='medal_type', value_name='medal_count')
color_map_disc_medals = {'gold_medals': 'gold', 'silver_medals': 'silver', 'bronze_medals': '#cd7f32'} 
fig2 = px.bar(discontinued_sports_melted, x='discipline', y='medal_count', color='medal_type', color_discrete_map=color_map_disc_medals, title='Medal Distribution for Discontinued Sports', barmode='group')
fig2.update_layout(xaxis_tickangle=-45, legend_title_text='Medal Type', xaxis_title='Discipline', yaxis_title='Number of Medals')

# Graph 3
fig3 = px.bar(medalists_age_df, x='sport', y='age', title='Age of Medalists by Sport', color='age', color_continuous_scale=px.colors.sequential.Plasma)
fig3.update_layout(xaxis_tickangle=-45, xaxis_title='Sport', yaxis_title='Age of Medalist', yaxis_range=[0, 100])

# Graph 4
fig4 = px.histogram(medalists_age_df, x='age', nbins=20, title='Age Distribution of Olympic Medalists', color_discrete_sequence=px.colors.sequential.Plasma)
fig4.update_layout(xaxis_title='Age of Medalist', yaxis_title='Number of Medalists')

# Graph 5
season_colors = {'Summer': '#ff4d4d', 'Winter': '#4da6ff'} 
fig5 = px.bar(olympiad_summry_df.sort_values(by='games_year'), x='games_year', y='total_events', color='season', color_discrete_map=season_colors, title='Total Events per Olympic Games (by Year and Season)', barmode='group')
fig5.update_layout(xaxis_tickangle=-45, xaxis_title='Olympic Year', yaxis_title='Number of Total Events', legend_title_text='Season')

# Graph 6 
olympiad_summry_df_temp = olympiad_summry_df.copy()
olympiad_summry_df_temp['games_year_str'] = olympiad_summry_df_temp['games_year'].astype(str)
olympiad_summry_df_temp['country_year'] = olympiad_summry_df_temp['host_country'] + " - " + olympiad_summry_df_temp['games_year_str']
country_total_events = olympiad_summry_df_temp.groupby('host_country')['total_events'].sum().reset_index()
country_total_events_sorted = country_total_events.sort_values(by='total_events', ascending=False)
olympiad_summry_df_temp['host_country'] = pd.Categorical(olympiad_summry_df_temp['host_country'], categories=country_total_events_sorted['host_country'], ordered=True)
sorted_olympiad_summry_df = olympiad_summry_df_temp.sort_values(by=['host_country', 'games_year'])
fig6 = px.bar(sorted_olympiad_summry_df, x='country_year', y='total_events', title='Total Events per Olympic Games by Host Country', color='total_events', color_continuous_scale=px.colors.sequential.Plasma)
fig6.update_xaxes(categoryorder='array', categoryarray=sorted_olympiad_summry_df['country_year'])
fig6.update_layout(xaxis_tickangle=-90, xaxis_title='Host Country and Olympic Year', yaxis_title='Number of Total Events', width=1200)

# Graph 7
olympiad_summry_melted = olympiad_summry_df.melt(id_vars=['host_country', 'host_city', 'games_year'], value_vars=['number_of_gold_medals', 'number_of_silver_medals', 'number_of_bronze_medals'], var_name='medal_type', value_name='medal_count')
color_map_olympiad_medals = {'number_of_gold_medals': 'gold', 'number_of_silver_medals': 'silver', 'number_of_bronze_medals': '#cd7f32'}
fig7 = px.bar(olympiad_summry_melted, x='host_country', y='medal_count', color='medal_type', color_discrete_map=color_map_olympiad_medals, title='Medal Distribution for Olympiad Sports According to Host Countries', barmode='group', hover_data=['host_city', 'games_year'])
fig7.update_layout(xaxis_tickangle=-45, legend_title_text='Medal Type', xaxis_title='Host Country', yaxis_title='Number of Medals')

# Graph 8
comparison_status_df = olympiad_summry_df[['games_year', 'number_of_gold_medals', 'total_medals', 'athlete_with_most_medals', 'athlete_with_most_medals_country', 'athlete_with_most_gold_medals', 'athlete_with_most_gold_medals_country']].copy()
comparison_status_df['athlete_match'] = (comparison_status_df['athlete_with_most_medals'] == comparison_status_df['athlete_with_most_gold_medals'])
comparison_status_df['country_match'] = (comparison_status_df['athlete_with_most_medals_country'] == comparison_status_df['athlete_with_most_gold_medals_country'])
def get_comparison_status(row):
    if row['athlete_match'] and row['country_match']: return 'Same Athlete & Country'
    elif row['athlete_match']: return 'Same Athlete, Different Country'
    elif row['country_match']: return 'Different Athlete, Same Country'
    else: return 'Different Athlete & Country'
comparison_status_df['comparison_status'] = comparison_status_df.apply(get_comparison_status, axis=1)
status_counts_per_year = comparison_status_df.groupby(['games_year','number_of_gold_medals', 'total_medals', 'comparison_status', 'athlete_with_most_medals', 'athlete_with_most_medals_country']).size().reset_index(name='count')
comparison_colors = {'Same Athlete & Country': '#00cc66', 'Different Athlete, Same Country': '#3399ff', 'Different Athlete & Country': '#ff4d4d'}
fig8 = px.bar(status_counts_per_year, x='games_year', y='count', color='comparison_status', color_discrete_map=comparison_colors, title='Comparison of Top Medalist vs. Top Gold Medalist', barmode='stack')
fig8.update_layout(xaxis_tickangle=-45, xaxis_title='Olympic Year', yaxis_title='Number of Olympic Games')

# Graph 9
medal_trends_df = olympiad_summry_df.melt(id_vars=['games_year', 'season'], value_vars=['number_of_gold_medals', 'number_of_silver_medals', 'number_of_bronze_medals'], var_name='medal_type', value_name='medal_count').sort_values(by='games_year')
medal_type_colors = {'number_of_gold_medals': 'gold', 'number_of_silver_medals': 'silver', 'number_of_bronze_medals': '#cd7f32'}
fig9 = px.line(medal_trends_df, x='games_year', y='medal_count', color='medal_type', color_discrete_map=medal_type_colors, title='Trends of Olympic Medals Over Time', hover_data=['season'])
fig9.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Medals')

# Graph 10
fig10 = px.scatter(olympiad_summry_df, x='total_events', y='total_medals', color='season', hover_name='host_city', hover_data=['games_year', 'host_country'], title='Total Events vs. Total Medals', size='total_medals', color_discrete_map=season_colors)
fig10.update_layout(xaxis_title='Number of Total Events', yaxis_title='Total Number of Medals')

# Graph 11
host_country_counts = olympiad_summry_df['host_country'].value_counts().reset_index()
host_country_counts.columns = ['host_country', 'number_of_times_hosted']
fig11 = px.bar(host_country_counts.sort_values(by='number_of_times_hosted', ascending=False), x='host_country', y='number_of_times_hosted', color='number_of_times_hosted', color_continuous_scale=px.colors.sequential.Viridis, title='Frequency of Olympic Games Hosted by Country')
fig11.update_layout(xaxis_tickangle=-45, xaxis_title='Host Country', yaxis_title='Number of Times Hosted')

# Graph 12
fig12 = px.bar(sports_summry_df.sort_values(by='total_medals', ascending=False), x='discipline', y='total_medals', color='season', title='Total Medals per Discipline', color_discrete_map=season_colors)
fig12.update_layout(xaxis_tickangle=-45, xaxis_title='Sport Discipline', yaxis_title='Total Number of Medals')

# Graph 13
sports_medals_melted = sports_summry_df.melt(id_vars=['discipline', 'season'], value_vars=['number_of_gold_medals', 'number_of_silver_medals', 'number_of_bronze_medals'], var_name='medal_type', value_name='medal_count')
fig13 = px.bar(sports_medals_melted, x='discipline', y='medal_count', color='medal_type', color_discrete_map=medal_type_colors, title='Medal Distribution per Discipline', barmode='group')
fig13.update_layout(xaxis_tickangle=-45, xaxis_title='Sport Discipline', yaxis_title='Number of Medals')

# Graph 14
fig14 = px.bar(sports_summry_df.sort_values(by='number_of_olympics', ascending=False), x='discipline', y='number_of_olympics', color='season', title='Olympic Games Appearances per Discipline', color_discrete_map=season_colors)
fig14.update_layout(xaxis_tickangle=-45, xaxis_title='Sport Discipline', yaxis_title='Number of Olympic Appearances')

# Graph 15
fig15 = px.scatter(sports_summry_df, x='number_of_olympics', y='total_medals', color='season', size='total_medals', hover_name='discipline', title='Olympic Appearances vs. Total Medals per Discipline', color_discrete_map=season_colors)
fig15.update_layout(xaxis_title='Number of Olympic Appearances', yaxis_title='Total Number of Medals')

ml_detailed_data = {
    'Algorithm': ['Logistic Regression', 'KNN', 'Decision Tree', 'Random Forest', 'GaussianNB', 'SVC'],
    'Accuracy (%)': [92.86, 85.71, 85.71, 85.71, 85.71, 78.57],
    'Recall (Discontinued)': [67.0, 67.0, 67.0, 67.0, 67.0, 0.0],
    'Precision (Discontinued)': [100.0, 67.0, 67.0, 67.0, 67.0, 0.0],
    'F1-Score (%)': [92.30, 85.71, 85.71, 85.71, 85.71, 69.14]
}            

importances = active_model.feature_importances_ * 100

ml_df = pd.DataFrame(ml_detailed_data).set_index('Algorithm')
fig16 = px.imshow(ml_df, text_auto='.2f', aspect="auto", color_continuous_scale='RdYlGn', title='🤖 AI Models Performance Heatmap (Strengths vs Weaknesses)')
fig16.update_layout(xaxis_title="Evaluation Metrics", yaxis_title="Machine Learning Models", height=500)

figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13, fig14, fig15, fig16]
for fig in figures:
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

app = Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Olympic Games Data Dashboard</title>
        <style>
            body { margin: 0; padding: 0; background-color: #121212; }
            .Select-control { background-color: #333 !important; border: 1px solid #555 !important; color: white !important;}
            .Select-menu-outer { background-color: #333 !important; color: white !important; }
            .is-focused:not(.is-open) > .Select-control { border-color: #4da8da !important; box-shadow: none !important; }
            .Select-value-label { color: white !important; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>{%config%}{%scripts%}{%renderer%}</footer>
    </body>
</html>
'''

BG_COLOR = '#121212'       
CARD_COLOR = '#1e1e1e'     
TEXT_COLOR = '#e0e0e0'     
HEADING_COLOR = '#4da8da'  

card_style = {
    'width': '48%', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 
    'marginBottom': '20px', 'backgroundColor': CARD_COLOR, 'borderRadius': '10px'
}

app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': BG_COLOR, 'color': TEXT_COLOR, 'minHeight': '100vh'},
    children=[
        html.H1("🏅 Olympic Games Data Dashboard", style={'textAlign': 'center', 'color': HEADING_COLOR, 'marginBottom': '30px', 'fontWeight': 'bold'}),

        # --- Data Analysis Sections ---
        html.H2("Discontinued Sports Analysis", style={'marginTop': '20px', 'color': HEADING_COLOR, 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}),
        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
            html.Div(style=card_style, children=dcc.Graph(figure=fig1)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig2))
        ]),

        html.H2("Medalists Age Analysis", style={'marginTop': '40px', 'color': HEADING_COLOR, 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}),
        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
            html.Div(style=card_style, children=dcc.Graph(figure=fig3)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig4))
        ]),

        html.H2("Olympiad Summary Analysis", style={'marginTop': '40px', 'color': HEADING_COLOR, 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}),
        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
            html.Div(style=card_style, children=dcc.Graph(figure=fig5)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig7)),
            html.Div(style={'width': '100%', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'marginBottom': '20px', 'backgroundColor': CARD_COLOR, 'borderRadius': '10px'}, children=dcc.Graph(figure=fig6)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig8)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig9)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig10)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig11))
        ]),

        html.H2("Sports Summary Analysis", style={'marginTop': '40px', 'color': HEADING_COLOR, 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}),
        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
            html.Div(style=card_style, children=dcc.Graph(figure=fig12)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig13)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig14)),
            html.Div(style=card_style, children=dcc.Graph(figure=fig15))
        ]),

        html.H2("🤖 Machine Learning & AI Predictions", style={'marginTop': '40px', 'color': HEADING_COLOR, 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}),
        
        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
            html.Div(style={'width': '100%', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'marginBottom': '20px', 'backgroundColor': CARD_COLOR, 'borderRadius': '10px'}, children=dcc.Graph(figure=fig16))
        ]),

        html.Div(style={'width': '100%', 'padding': '30px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'marginBottom': '40px', 'backgroundColor': CARD_COLOR, 'borderRadius': '10px', 'textAlign': 'center'}, children=[
            html.H3("🔮 AI Continuity Predictor", style={'color': '#00cc66'}),
            html.P("Choose a model and enter sport statistics. Total medals will be calculated automatically.", style={'fontSize': '18px'}),
            
            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '30px'}, children=[
                html.Div(style={'width': '40%'}, children=[
                    html.Label("Select AI Model:", style={'display': 'block', 'marginBottom': '10px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='model-selector',
                        options=[
                            {'label': '🏆 Logistic Regression', 'value': 'lr'},
                            {'label': '🌲 Random Forest', 'value': 'rf'},
                            {'label': '🌳 Decision Tree', 'value': 'dt'},
                            {'label': '📍 K-Nearest Neighbors', 'value': 'knn'},
                            {'label': '📊 Naive Bayes', 'value': 'nb'},
                            {'label': '📉 Support Vector Machine', 'value': 'svm'}
                        ],
                        value='lr', 
                        clearable=False
                    )
                ]),
                html.Div(style={'width': '30%'}, children=[
                    html.Label("Select Season:", style={'display': 'block', 'marginBottom': '10px', 'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='input-season',
                        options=[{'label': '☀️ Summer', 'value': 1}, {'label': '❄️ Winter', 'value': 0}],
                        value=1,
                        clearable=False
                    )
                ])
            ]),

            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '15px', 'marginBottom': '20px', 'flexWrap': 'wrap'}, children=[
                dcc.Input(id='input-olympics', type='number', placeholder='Num of Olympics', style={'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #555', 'backgroundColor': '#333', 'color': 'white'}),
                dcc.Input(id='input-gold', type='number', placeholder='Gold Medals', style={'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #555', 'backgroundColor': '#333', 'color': 'white'}),
                dcc.Input(id='input-silver', type='number', placeholder='Silver Medals', style={'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #555', 'backgroundColor': '#333', 'color': 'white'}),
                dcc.Input(id='input-bronze', type='number', placeholder='Bronze Medals', style={'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #555', 'backgroundColor': '#333', 'color': 'white'}),
            ]),
            
            html.Button('Predict & Open Brain 🚀', id='predict-button', n_clicks=0, style={'padding': '12px 24px', 'fontSize': '18px', 'backgroundColor': HEADING_COLOR, 'color': '#fff', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
            
            html.Div(id='ml-output-container', style={'marginTop': '30px', 'padding': '20px', 'borderRadius': '8px', 'minHeight': '60px'}, children=[
                html.H3(id='ml-output', style={'margin': '0', 'fontSize': '24px'})
            ]),

            html.Div(id='model-brain-graph-container', style={'marginTop': '20px', 'display': 'none'}, children=[
                dcc.Graph(id='model-brain-graph') 
            ])
        ])
    ]
)

@app.callback(
    Output('ml-output', 'children'),
    Output('ml-output-container', 'style'),
    Output('model-brain-graph', 'figure'),
    Output('model-brain-graph-container', 'style'),
    Input('predict-button', 'n_clicks'),
    State('model-selector', 'value'), 
    State('input-season', 'value'),
    State('input-olympics', 'value'),
    State('input-gold', 'value'),
    State('input-silver', 'value'),
    State('input-bronze', 'value')
)
def predict_sport(n_clicks, selected_model_key, season, olympics, gold, silver, bronze):
    base_style = {'marginTop': '30px', 'padding': '20px', 'borderRadius': '8px', 'transition': '0.3s'}
    empty_fig = go.Figure()
    
    if n_clicks > 0:
        if selected_model_key not in models_dict or models_dict[selected_model_key] is None:
            return "⚠️ Error: Model file is missing!", {**base_style, 'backgroundColor': 'rgba(255, 77, 77, 0.1)', 'color': '#ff4d4d', 'border': '1px solid #ff4d4d'}, empty_fig, {'display': 'none'}
            
        if None in [olympics, gold, silver, bronze]:
            return "⚠️ Please fill all input fields!", {**base_style, 'backgroundColor': 'rgba(255, 204, 0, 0.1)', 'color': '#ffcc00', 'border': '1px solid #ffcc00'}, empty_fig, {'display': 'none'}
        
        total_medals = gold + silver + bronze
        feature_names = ['Season', 'Num Olympics', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals']
        features_df = pd.DataFrame([[season, olympics, gold, silver, bronze, total_medals]], columns=['season', 'number_of_olympics', 'number_of_gold_medals', 'number_of_silver_medals', 'number_of_bronze_medals', 'total_medals'])
        
        active_model = models_dict[selected_model_key]
        prediction = active_model.predict(features_df)[0]
        model_name = selected_model_key.upper()
        
        try:
            prob = active_model.predict_proba(features_df)[0][1] * 100
        except:
            prob = 90.0 if prediction == 1 else 10.0
            
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "indicator"}, {"type": "bar"}]], column_widths=[0.4, 0.6], horizontal_spacing=0.15)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=prob,
            title={'text': "Risk Probability", 'font': {'size': 20, 'color': '#e0e0e0'}},
            number={'suffix': "%", 'font': {'size': 40, 'color': '#ff4d4d' if prob > 50 else '#00cc66'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "rgba(255,255,255,0.05)",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [0, 50], 'color': "rgba(0, 204, 102, 0.3)"},
                    {'range': [50, 100], 'color': "rgba(255, 77, 77, 0.3)"}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': prob}
            }
        ), row=1, col=1)
        
        if hasattr(active_model, 'coef_'):
            impacts = active_model.coef_[0] * features_df.iloc[0].values
            colors = ['#ff4d4d' if c > 0 else '#00cc66' for c in impacts]
            fig.add_trace(go.Bar(
                x=impacts, y=feature_names, orientation='h',
                marker=dict(color=colors, line=dict(color='white', width=1)),
                text=[f"{c:.2f}" for c in impacts], textposition='outside'
            ), row=1, col=2)
            fig.update_xaxes(title_text="Feature Impact (Red=Pushes to Discontinue, Green=Saves Sport)", row=1, col=2)
            
        elif hasattr(active_model, 'feature_importances_'):
            importances = active_model.feature_importances_ * 100
            fig.add_trace(go.Bar(
                x=importances, y=feature_names, orientation='h',
                marker=dict(color='#4da8da', line=dict(color='white', width=1)),
                text=[f"{i:.1f}%" for i in importances], textposition='outside'
            ), row=1, col=2)
            fig.update_xaxes(title_text="Model's Attention / Focus (%)", row=1, col=2)
            
        else:
            vals = features_df.iloc[0].values
            fig.add_trace(go.Bar(
                x=vals, y=feature_names, orientation='h',
                marker=dict(color='#bb86fc', line=dict(color='white', width=1)),
                text=[str(v) for v in vals], textposition='outside'
            ), row=1, col=2)
            fig.update_xaxes(type="log", title_text="Input Profile (Log Scale - Distance Based Math)", row=1, col=2)

        fig.update_layout(
            title={'text': f"🧠 Inside the Brain of {model_name}", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 24}},
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=450, margin=dict(l=20, r=40, t=80, b=20)
        )
        
        if prediction == 1:
            msg = f"❌ [{model_name}]: High risk! This sport is likely to be DISCONTINUED."
            style = {**base_style, 'backgroundColor': 'rgba(255, 77, 77, 0.1)', 'color': '#ff4d4d', 'border': '1px solid #ff4d4d'}
        else:
            msg = f"✅ [{model_name}]: Safe! This sport is likely to remain ACTIVE."
            style = {**base_style, 'backgroundColor': 'rgba(0, 204, 102, 0.1)', 'color': '#00cc66', 'border': '1px solid #00cc66'}
            
        return msg, style, fig, {'marginTop': '40px', 'display': 'block', 'backgroundColor': '#1e1e1e', 'padding': '20px', 'borderRadius': '10px'}
    
    return "", base_style, empty_fig, {'display': 'none'}

if __name__ == '__main__':
    app.run(debug=True)
