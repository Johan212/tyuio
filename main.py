import justpy as jp
import time
import asyncio
import modules
import pandas as pd
import sqlite3

chart_def = """
{
    chart: {
        type: 'spline'
    },
    title: {
        text: 'Average fruit consumption during one week'
    },
    legend: {
        layout: 'horizontal',
        align: 'left',
        verticalAlign: 'top',
        x: 5,
        y: 0,
        floating: true,
        borderWidth: 1,
        backgroundColor: '#FFFFFF'
    },
    xAxis: {
        categories: [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ],
        plotBands: [{ // visualize the weekend

            color: 'rgba(68, 170, 213, .2)'
        }]
    },
    yAxis: {
        title: {
            text: ''
        }
    },
    tooltip: {
        shared: true,
        valueSuffix: ' V'
    },
    credits: {
        enabled: false
    },
    plotOptions: {
        areaspline: {
            fillOpacity: 0.5
        }
    },
    series: [{
        name: '',
        data: []
    }]
}"""

wp = jp.QuasarPage(tailwind=True, delete_flag=False, title="Axpert", favicon="test.ico")

box1 = jp.QDiv(a=wp, classes="flex flex-row")
a = jp.Div(a=box1, text="Active Power W", classes="flex-auto text-center text-black p-2 text-xl")
jp.Br(a=a)
avalue = jp.QCircularProgress(a=a, min=0, max=220, show_value="", size="200px", font_size="20px",
                              thickness="0.30", color="teal", track_color="grey-3", angle=180,
                              classses="q-ma-md")
b = jp.Div(a=box1, text="Battery Voltage V", classes="flex-auto text-center text-black p-2 text-xl")
jp.Br(a=b)
bvalue = jp.QCircularProgress(a=b, min=0, max=57, show_value="", size="200px", font_size="20px",
                              thickness="0.30", color="teal", track_color="grey-3", angle=180,
                              classses="q-ma-md")
c = jp.Div(a=box1, text="PV Input Voltage V", classes="flex-auto text-center text-black p-2 text-xl")
jp.Br(a=c)
cvalue = jp.QCircularProgress(a=c, min=0, max=100, show_value="", size="200px", font_size="20px",
                              thickness="0.30", color="teal", track_color="grey-3", angle=180,
                              classses="q-ma-md")
d = jp.Div(a=box1, text="Battery Capacity %", classes="flex-auto text-center text-black p-2 text-xl")
jp.Br(a=d)
dvalue = jp.QCircularProgress(a=d, min=0, max=100, show_value="", size="200px", font_size="20px",
                              thickness="0.30", color="teal", track_color="grey-3", angle=180,
                              classses="q-ma-md")

hc = jp.HighCharts(a=wp, options=chart_def)
hc.options.title.text = "Inverter"
hc.options.subtitle.text = ""
hc.options.xAxis.title.text = "Date"
hc.options.yAxis.title.text = ""

modu = modules.Modules()

try:
    modu.create_table()
    modu.data_collect()
except sqlite3.OperationalError as err:
    print(err)


async def clock_counter():
    global saved_data
    result = []
    tes = modu.get_last_entrys()
    for i in tes:
        dict1 = dict({'Date': i[0], 'Battery': i[12], 'Active Power': i[10]})
        result.append(dict1)
    df = pd.DataFrame(result)
    if df['Date'] is None:
        pass
    else:
        df.set_index('Date', inplace=True)
    timer = 0
    modu.data_collect()
    while True:
        test_data = modu.serial_coms()
        if test_data != "None" and test_data[3] != "N":
            # print("Coms Succes")
            modu.retrieve_data()
            avalue.value = int(modu.ac_output_active_power[1:4])
            bvalue.value = float(modu.battery_voltage)
            cvalue.value = float(modu.pv_input_voltage)
            dvalue.value = int(modu.battery_capacity)
        secon = int(time.strftime("%S", time.localtime()))
        minit = int(time.strftime("%M", time.localtime()))
        if minit in range(1, 60, 2):
            tes = modu.get_last_entrys()
            for i in tes:
                hc.options.series = i[12]
                dict1 = dict({'Date': i[0], 'Battery': i[12], 'Active Power': i[10]})
                result.append(dict1)
        df = pd.DataFrame(result)
        if df.empty:
            pass
        else:
            df.set_index('Date', inplace=True)
            print(df)
            # print("Its empty")
            hc.options.xAxis.categories = list(df.index)
            hc_data = [{"name": v1, "data": [v2 for v2 in df[v1]]} for v1 in df.columns]
            hc.options.series = hc_data
            print('wow')
        print(f"Minute : {minit} Second : {secon}")
        if minit not in [0, 10, 20, 30, 40, 50] or secon not in [0, 1, 2, 3, 4, 5, 6]:
            result = []
        if minit in [0, 10, 20, 30, 40, 50, 60] and secon in [0, 1, 2, 3, 4, 5, 6]:
            modu.data_collect()
            print("save")
        jp.run_task(wp.update())
        await asyncio.sleep(1)


async def clock_init():
    jp.run_task(clock_counter())


async def clock_test():
    return wp


jp.justpy(clock_test, startup=clock_init, host="192.168.88.50", port=8002)
