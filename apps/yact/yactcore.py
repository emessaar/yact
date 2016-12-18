#yact.py

import pandas as pd

from plotly import offline as po
import plotly.graph_objs as go

#supported charts
# line
# marked line
# scatter
# bar
# stacked bar
# grouped bar
# hbar
# stacked hbar
# grouped hbar

PLOTLY_API = {
    'line': 'go.Scatter',
    'scatter': 'go.Scatter',
    'bar': 'go.Bar',
    'hbar': 'go.Bar',
    'pie': 'go.Pie',
}

# plotly entry function
def _create_plotly_chart(**kwargs):
    #print '_create_plotly_chart:', locals()
    output_type = kwargs['output_type']
    include_plotlyjs = kwargs['include_plotlyjs']
    data, layout = _create_plotly_traces_layout(**kwargs)
    # print '------'
    # print data
    # print '------'
    # print layout
    fig = dict(data=data, layout=layout)
    div = po.plot(fig, show_link=False, output_type=output_type, include_plotlyjs=include_plotlyjs)
    return div

def _create_plotly_traces_layout(**kwargs):
    #print '_create_plotly_traces_layout:', locals()
    chart_fn = kwargs['chart_fn']
    chart_fn = eval(chart_fn)
    agg_by = kwargs['agg_by']
    agg_fn = kwargs['agg_fn']
    agg_col = kwargs['agg_col']
    chart_type = kwargs['chart_type']
    chart_subtype = kwargs.get('chart_subtype', '')
    df = kwargs['df']
    traces = []
    layout = go.Layout()
    if chart_subtype and len(agg_by) == 2:
        xcol1 = agg_by[0]
        xcol2 = agg_by[1]
        ycol = '{0}({1})'.format(agg_fn, agg_col)
        for name_ in df[xcol2].unique():

            df2 = df[ df[xcol2] == name_ ]

            chart_params = dict(x=df2[xcol1], y=df2[ycol], name=name_)

            if chart_type == 'line':
                chart_params['mode'] = kwargs['chart_subtype']
            elif chart_type == 'hbar':
                chart_params['orientation'] = 'h'

            trace = chart_fn(**chart_params)
            traces.append(trace)

        layout = go.Layout(barmode=chart_subtype)
    else:
        xcol = agg_by[0]
        ycol = '{0}({1})'.format(agg_fn, agg_col)
        traces.append(chart_fn(x=df[xcol], y=df[ycol]))

    return traces, layout


CHART_LIB_ENTRY_FN = {
    'plotly': _create_plotly_chart
}

# entry function
def create_chart(**kwargs):
    #print 'create_chart:', locals()
    try:
        chart_lib = kwargs['chart_lib']
        chart_type = kwargs['chart_type']
        chart_lib_entry_fn = CHART_LIB_ENTRY_FN[chart_lib]
        chart_fn = PLOTLY_API[chart_type]
        fargs = dict(kwargs)
        fargs.update(dict(chart_fn=chart_fn))
        return chart_lib_entry_fn(**fargs)
    except KeyError:
        raise ValueError('Unsupported charting lib requested', chart_lib)


if __name__ == '__main__':
    pass
