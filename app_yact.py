#app.py
from flask import (Flask, render_template, request, url_for,
                    make_response, jsonify, flash, redirect,
                    session
                  )
from werkzeug import secure_filename

from apps.yact import yactcore
import tempfile
import os
import traceback
import pandas as pd
from uuid import uuid1

from common.fileds import FileDS
from apps.yact.cql import cqlStmt3

from flask_wtf import FlaskForm
from wtforms import TextField, RadioField, SelectField

import common.logutil as log
if os.path.isfile('STABLE'):
  logger = log.getLogger('flaskapps')
else:
  logger = log.getLogger('flaskapps-dev')

RELATIVE_PATH = 'apps/yact/'
app = Flask(__name__, static_folder=RELATIVE_PATH+'static', template_folder=RELATIVE_PATH+'templates')
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = RELATIVE_PATH + 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

DF_store = {}
DB = FileDS('diskdb.db')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def gen_key():
  return str(uuid1()).split('-')[0]

def prep_df(df):
  df = df.rename(columns={c: c.replace(' ', '_') for c in df.columns})
  df = df.rename(columns={c: c.replace('.', '_') for c in df.columns})
  return df

def pp_to_sql(parsed, table_name):
    cols = ','.join(parsed.sliceby)
    trendby = parsed.trendby if parsed.trendby else ''
    comma = ',' if trendby else ''
    agg_col = parsed.get('agg_fn', 'sum') + '(' + parsed.chart_val + ')'
    where = ' '.join(parsed.filter[0]) if parsed.filter else ''

    return """
        select
        {cols},
        {trendby}{comma}
        {agg_col}
        from {table_name}
        {where}
        group by
        {cols}
        {trendby}
    """.format(**locals())

def printlocals(**kwargs):
  for k,v in kwargs.items():
    if not k.startswith('__'):
      print '{0}=>{1}'.format(k, v)

@app.route('/')
def index():
  if 'key' not in session:
    session['key'] = gen_key()
  return render_template('index.html')

@app.route('/yact', methods=['GET','POST'])
def yact():
  if 'key' not in session:
    session['key'] = gen_key()
  if request.method == 'POST':
    if request.form.get('btnupload') == 'upload':
      file = request.files['file']
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding='utf-8')
        yactcore.df = df
        table_name = 't' + session['key']
        DB.load_dataset(table_name, os.path.join(app.config['UPLOAD_FOLDER'], filename))
        response = '<div>{0} loaded</div>'.format(filename)
        return render_template('yact.html', filename=filename)
    else:
      cql = request.form.get('cql')
      table_name = 't' + session['key']
      parsed = cqlStmt3.parseString(cql)
      sql = pp_to_sql(parsed, table_name)
      df = DB.query_to_df(sql)

      if len(parsed.chart_name) > 1:
          chart_type = parsed.chart_name[1]
          chart_subtype = parsed.chart_name[0]
      else:
          chart_type = parsed.chart_name[0]
          chart_subtype = None
      trend_by = parsed.trendby
      agg_by = list(parsed.sliceby)
      if len(agg_by) > 2:
          agg_by = agg_by[:2]

      agg_col = parsed.chart_val
      if "agg_fn" in parsed:
          agg_fn = parsed.agg_fn

      #printlocals(**locals())

      chart_options = dict(
        df=df,
        chart_type=chart_type,
        chart_subtype=chart_subtype,
        trend_by=trend_by,
        agg_by=agg_by,
        agg_col=agg_col,
        agg_fn=agg_fn,
        chart_lib='plotly',
        output_type='div',
        include_plotlyjs=False
      )
      div = yactcore.create_chart(**chart_options)
      logger.debug(div)
      return jsonify(result=div, cql=cql)
  return render_template('yact.html')


if __name__ == '__main__':

  if os.path.isfile('STABLE'):
    app.run('0.0.0.0', port=5000, debug=True)
  else:
    app.run('0.0.0.0', port=8890, debug=True)
