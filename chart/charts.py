'''
Draw the last 30 days prediction and real price chart
'''


def connect_db():
    import MySQLdb
    # Connect the database
    db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='hl4su3ao4', db='bitcoin_historical_price', port=3306, charset='utf8')
    cursor = db.cursor()
    db.autocommit(True)
    return db


def generate_all_chart(db):
    import pyecharts.options as opts
    from pyecharts.charts import Line

    date_list, prediction_list, real_list = get_all_data(db=db)

    (
        Line()
        .add_xaxis(xaxis_data=date_list)
        .add_yaxis(
            series_name="Prediction",
            y_axis=prediction_list,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="Real",
            y_axis=real_list,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Bitcoin Prediction"),
            datazoom_opts=opts.DataZoomOpts(type_="slider", range_start=95, range_end=100),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        .render("templates/bitcoin_all_predict.html")
    )


def get_all_data(db):
    import pandas as pd

    sql_str = f'''SELECT date, prediction FROM `prediction`;'''
    raw_data = pd.read_sql_query(sql_str, db)
    date_list = list(raw_data['date'])
    prediction_list = list(raw_data['prediction'])

    sql_str = f'''SELECT r.real FROM `result` as r;'''
    raw_data = pd.read_sql_query(sql_str, db)
    
    return date_list, prediction_list, list(raw_data['real'])


def generate_30_chart(db):
    import pyecharts.options as opts
    from pyecharts.charts import Line

    date_list, prediction_list, real_list = get_data(db=db)

    (
        Line()
        .add_xaxis(xaxis_data=date_list)
        .add_yaxis(
            series_name="Prediction",
            y_axis=prediction_list,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="Real",
            y_axis=real_list,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Bitcoin Prediction"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
       .render("templates/bitcoin_30_predict.html")
    )


def get_data(db):
    import pandas as pd

    sql_str = f'''SELECT * FROM `result` where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(`date`);'''
    raw_data = pd.read_sql_query(sql_str, db)
    return list(raw_data['date']), list(raw_data['prediction']), list(raw_data['real'])


def main():
    from datetime import datetime

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    db = connect_db()

    generate_30_chart(db=db)
    generate_all_chart(db=db)

    print(f'{now}: Chart Done')

    db.close()


if __name__ == '__main__':
    main()
