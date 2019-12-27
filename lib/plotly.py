import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import pandas as pd
import helper


def show_events_hist(col_sm, title):
    data_canada = helper.getEventFreq()
    fig = px.bar(data_canada, x='event_name', y='freq', height=300)
    html_div = plot(fig, output_type='div')
    html_data = html_template(html_div, col_sm, title)

    return html_data


def show_chain_cost(**args):

    type = args.get('type','')
    size = args.get('size',12)
    title = args.get('title','none')
    date_from = args.get('date_from',None)
    date_to = args.get('date_to',None)

    pd.set_option('display.max_colwidth', -1)
    df = helper.getEventsLineCnt(
        type=type,
        date_from = date_from,
        date_to = date_to
    )

    def to_html_line(x):
        x_html = []
        for v in x.split(','):
            x_html.append('''  <button class='btn btn-danger' style='background-image :-webkit-gradient(linear,left top,left bottom,from({color} ),to({color} )) '> {name} </button>'''.format(
                    color = helper.screnn_colors[v],
                    name = helper.screnn_mapeer[v]
                )
            )
        return '<span class="glyphicon glyphicon-arrow-right"></span>'.join(x_html)

    df.event_line = df.event_line.map(to_html_line)

    df['cnt_perc'] = (df.cnt/df.cnt.sum())*100

    df.columns = ['порядок переходов', 'частота','частота %']
    html_div = df.to_html(classes='table',escape = False)
    html_data = html_template(html_div, size, title=title)

    return html_data


def transitionFrequency(type, size, title, date_from, date_to):

    df = helper.transitionFrequency(type, date_from, date_to)

    fig = px.bar(df, x='Кол-во переходов', y='Частота', height=300)
    html_div = plot(fig, output_type='div')
    html_data = html_template(html_div, size, title)

    return html_data



def html_template(html_div, col_sm, title):
    html_data = '''
        <div class="col-sm-{col_sm}"  > 
            <div class="panel-group py-5 " >
                <div class="panel panel-primary filter_main"  >
                  <div class="panel-heading">{title}</div>
                  <div class="panel-body" id="DistributionFreq" style=" min-height: 550px;max-height: 550px;overflow-x: scroll;">
                      {html_div}
                  </div>
                </div>
            </div>
        </div>
        '''.format(html_div=html_div, col_sm=col_sm, title=title)

    return html_data
