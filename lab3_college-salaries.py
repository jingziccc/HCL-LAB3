# Import the required libraries
import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import plotly.express as px
# Read the datasets
df_degrees = pd.read_csv(
    '.\\dataset\\college-salaries\\degrees-that-pay-back.csv', encoding='MacRoman')
df_colleges = pd.read_csv(
    '.\\dataset\\college-salaries\\salaries-by-college-type.csv', encoding='MacRoman')
df_regions = pd.read_csv(
    '.\\dataset\\college-salaries\\salaries-by-region.csv', encoding='MacRoman')

# Initialize the app

app = dash.Dash(__name__)
# 消除美元与分隔符，使之数据能进行运算
df_regions_without_notation = pd.read_csv(
    '.\\dataset\\college-salaries\\salaries-by-region.csv', encoding='MacRoman')
df_degrees_without_notation = pd.read_csv(
    '.\\dataset\\college-salaries\\degrees-that-pay-back.csv', encoding='MacRoman')
df_colleges_without_notation = pd.read_csv(
    '.\\dataset\\college-salaries\\salaries-by-college-type.csv')
stages = {'Starting Median Salary', 'Mid-Career Median Salary', 'Mid-Career 10th Percentile Salary',
          'Mid-Career 25th Percentile Salary', 'Mid-Career 75th Percentile Salary', 'Mid-Career 90th Percentile Salary'}
dfs = [df_regions_without_notation,
       df_degrees_without_notation, df_colleges_without_notation]
for stage in stages:
    for df in dfs:
        df[stage] = df[stage].str.replace('$', '')
        df[stage] = df[stage].str.replace(',', '').astype(float)

fig_bubble = px.scatter(
    df_degrees_without_notation, x="Starting Median Salary", y="Mid-Career Median Salary",
    size="Percent change from Starting to Mid-Career Salary", color="Undergraduate Major")

df = pd.read_csv('.\\dataset\\college-salaries\\salaries-by-college-type.csv')
fig_pie = px.pie(df, names='School Type')

# 转换数据格式
# df_melt = df_colleges_without_notation.melt(
#     id_vars=['School Type'], value_vars=['Starting Median Salary',
#                                         'Mid-Career 10th Percentile Salary',
#                                         'Mid-Career 25th Percentile Salary',
#                                         'Mid-Career 75th Percentile Salary',
#                                         'Mid-Career 90th Percentile Salary'],
#     var_name='Attribute', value_name='Value')

# # 创建散点图
# fig_scatter = px.scatter(df_melt, x='Attribute', y='Value', color='School Type',
#                  title='Salary by Attribute and School Type')
# App layout
app.layout = html.Div([
    # 创建table切换显示三张表
    html.Div(children='College Salaries', style={
             'textAlign': 'center', 'fontSize': 30}),
    html.Hr(),
    html.Div([
        dcc.RadioItems(
            options=[
                {'label': 'Degrees', 'value': 'degrees'},
                {'label': 'Colleges', 'value': 'colleges'},
                {'label': 'Regions', 'value': 'regions'}
            ],
            value='degrees',
            id='table-selector',
            labelStyle={'display': 'inline-block', 'text-align': 'center'}
        )
    ]),
    html.Br(),
    dash_table.DataTable(id='display-table', page_size=8),
    dcc.Graph(figure=fig_pie),
    # 柱状图显示不同region的工资情况，附加选择框
    html.Div([
        html.P("Stage:", style={'display': 'inline-block'}),
        dcc.Dropdown(
            id='stages',
            options=['Starting Median Salary', 'Mid-Career Median Salary', 'Mid-Career 10th Percentile Salary',
                     'Mid-Career 25th Percentile Salary', 'Mid-Career 75th Percentile Salary', 'Mid-Career 90th Percentile Salary'],
            value='Starting Median Salary', clearable=False)
    ]),
    dcc.Graph(id="barGraph"),
    # 显示不同SchoolType时不同工资的函数关系
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='xaxis_column',
                options=['Starting Median Salary', 'Mid-Career Median Salary', 'Mid-Career 10th Percentile Salary',
                         'Mid-Career 25th Percentile Salary', 'Mid-Career 75th Percentile Salary', 'Mid-Career 90th Percentile Salary'],
                value='Starting Median Salary', clearable=False,
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='xaxis_type',
                inline=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis_column',
                options=['Starting Median Salary', 'Mid-Career Median Salary', 'Mid-Career 10th Percentile Salary',
                         'Mid-Career 25th Percentile Salary', 'Mid-Career 75th Percentile Salary', 'Mid-Career 90th Percentile Salary'],
                value='Mid-Career Median Salary', clearable=False,
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='yaxis_type',
                inline=True
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),
    # 显示不同专业的工资情况
    dcc.Graph(figure=fig_bubble, id='bubbleGraph'),

    #       该散点图没啥含义
    #    dcc.Graph(figure=fig_scatter),



])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis_column', 'value'),
    Input('yaxis_column', 'value'),
    Input('xaxis_type', 'value'),
    Input('yaxis_type', 'value'),
)
def update_graph(xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type,):
    fig = px.scatter(df_colleges_without_notation,
                     x=xaxis_column_name, y=yaxis_column_name, color='School Type')
    fig.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')
    return fig


@app.callback(
    # Output(component_id='my-first-graph-final', component_property='figure'),
    Output("barGraph", "figure"),
    Input("stages", "value")
)
def update_pieGraph(stage):
    df = df_regions_without_notation.groupby(
        'Region')[stage].mean().reset_index()
    fig = px.histogram(df, x='Region', y=stage,
                       title='Average Salary by Region')
    fig.update_layout(
        title={
            'text': 'Average Salary by Region',
            'x': 0.5,  # 将标题的x位置设置为0.5以实现居中对齐
            'xanchor': 'center'  # 设置标题的水平对齐方式为居中
        }
    )
    return fig

# Callback to update the table based on the selected radio button


@app.callback(
    dash.dependencies.Output('display-table', 'data'),
    dash.dependencies.Input('table-selector', 'value')
)
def update_table(value):
    if value == 'degrees':
        return df_degrees.to_dict('records')
    elif value == 'colleges':
        return df_colleges.to_dict('records')
    elif value == 'regions':
        return df_regions.to_dict('records')


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
