# -!- coding: utf-8 -!-
from pyecharts import options as opts
from pyecharts.charts import Bar
import pandas as pd
import numpy as np
import jieba.analyse
import matplotlib.pyplot as plt
import os
from pyecharts.charts import Line
from pyecharts.charts import WordCloud
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号


def vaccination(df):
    temp_vaccination = df.groupby(['iso_code'])['total_vaccinations_per_hundred'].agg('sum')
    y = np.trunc(list(temp_vaccination.values)).astype(int).tolist()
    c = (
        Bar()
        .add_xaxis(list(temp_vaccination.index))
        .add_yaxis("每 100 人接种的 COVID-19 疫苗总数", y, color='#41678D')
        .set_global_opts(
                title_opts=opts.TitleOpts(title="各国总人口中每 100 人接种的 COVID-19 疫苗总数"),
                legend_opts=opts.LegendOpts(selected_mode="mutiple", orient="vertical", pos_right="30px"),
                datazoom_opts=opts.DataZoomOpts(),
            )
        .render("line_base.html")
    )


def get_content(dir, Filelist, content):
    try:
        if os.path.isfile(dir):
            Filelist.append(dir)
            f = open(dir, encoding="utf-8")
            txt = f.read()
            print(txt)
            content.append(txt)
            f.close()
        elif os.path.isdir(dir):
            for s in os.listdir(dir):
                new_dir = os.path.join(dir, s)
                get_content(new_dir, Filelist, content)
    except Exception as e:
        print(e)
    return content


def word_cloud(data):
    cut_words = ""
    for line in data:
        line = str(line)
        seg_list = jieba.cut(line, cut_all=False)
        cut_words += (" ".join(seg_list))
    jieba.analyse.set_stop_words('hit_stopwords.txt')   # 停用词词典

    keywords = jieba.analyse.extract_tags(cut_words,
                                          topK=150, withWeight=True)
    # keyword本身包含两列数据
    ss = pd.DataFrame(keywords, columns=['词语', '重要性'])
    # ------------------------------------数据可视化------------------------------------
    plt.figure(figsize=(10, 6))
    plt.title('TF-IDF Ranking')
    fig = plt.axes()
    plt.barh(range(len(ss['重要性'][:25][::-1])), ss['重要性'][:25][::-1])
    fig.set_yticks(np.arange(len(ss['重要性'][:25][::-1])))
    fig.set_yticklabels(ss['词语'][:25][::-1])
    fig.set_xlabel('Importance')
    plt.savefig('重要性.jpg')
    plt.show()

    (
        WordCloud()
            .add(series_name="热点分析", data_pair=keywords, word_size_range=[6, 66])
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="热点分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
            .render("basic_wordcloud.html")
    )


def covert_currency(x):  # 1定义改变货币的函数
    if type(x) == float:
        return x
    elif x:
        if '--' in x:
            return ''
        return x.replace(',',  '')
    else:
        return x

def economy_analyse():
    df = pd.read_csv('WEOOct2021all.csv')
    df = df[df['WEO Subject Code'] == 'NGDP_R']
    fj_str = df['2020'].apply(lambda x: covert_currency(x))
    df['2020'] = pd.to_numeric(fj_str)
    fj_str = df['2019'].apply(lambda x: covert_currency(x))
    df['2019'] = pd.to_numeric(fj_str)
    fj_str = df['2018'].apply(lambda x: covert_currency(x))
    df['2018'] = pd.to_numeric(fj_str)
    df['20_19'] = df['2020'] - df['2019']
    df['20_18'] = df['2020'] - df['2018']
    df = df.fillna(0)
    df['2020'] = df['2020'].astype('int')
    df = df[['ISO', '2020']]
    df.rename(columns={'ISO': 'iso_code'}, inplace=True)
    data = pd.read_csv('owid-covid-data.csv')
    temp = data.groupby(['iso_code'])['total_vaccinations_per_hundred'].agg('sum')
    temp = temp.fillna(0)
    df = pd.merge(df, temp, on=['iso_code'])
    df['total_vaccinations_per_hundred'] = df['total_vaccinations_per_hundred'].astype('int')
    print(df)
    b = (
        Bar()
            .add_xaxis(list(df['iso_code']))
            .add_yaxis("每 100 人接种的 COVID-19 疫苗总数", list(df['total_vaccinations_per_hundred']))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="各国总人口中每 100 人接种的 COVID-19 疫苗总数"),
            legend_opts=opts.LegendOpts(selected_mode="mutiple", orient="vertical", pos_right="30px"),
            datazoom_opts=opts.DataZoomOpts(),
        )
    )
    c = (
        Line()
        .add_xaxis(list(df['iso_code']))
        .add_yaxis("人均GDPlog值", list(df['2020']), color='#41678D')
        .set_global_opts(
        title_opts=opts.TitleOpts(title="GDP_R"),
        datazoom_opts=opts.DataZoomOpts())
    )
    b.overlap(c)
    b.render("overlap_bar_line.html")


if __name__ == '__main__':
    economy_analyse()
    data = pd.read_csv('owid-covid-data.csv')
    print(data.groupby(['iso_code'])['total_vaccinations_per_hundred'].agg('sum'))
    vaccination(data)
    list = get_content(r'E:\python-work\综合课设3\china_policy\china_policy', [], [])
    word_cloud(list)