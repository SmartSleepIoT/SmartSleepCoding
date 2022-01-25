from sleepQuality import *
import plotly.graph_objects as go

title_fontsize = 35
x_align = 0.5


def addApneaLimits(f, limit_line_texts, timestamps):
    limit_line_texts[-1] = 'No apnea limit'
    f.add_trace(go.Scatter(x=timestamps, y=[1] * len(timestamps),
                           mode='lines+text',
                           name='No apnea limit',
                           line={
                               'width': 5,
                               'dash': 'dot'
                           },
                           text=limit_line_texts,
                           textposition="top center"
                           )
                )
    limit_line_texts[-1] = 'Mild apnea limit'
    f.add_trace(go.Scatter(x=timestamps, y=[3.5] * len(timestamps),
                           mode='lines+text',
                           name='Mild apnea limit',
                           line={
                               'width': 5,
                               'dash': 'dot'
                           },
                           text=limit_line_texts,
                           textposition="top center"
                           )
                )
    limit_line_texts[-1] = 'Moderate apnea limit'
    f.add_trace(go.Scatter(x=timestamps, y=[8] * len(timestamps),
                           mode='lines+text',
                           name='Moderate apnea limit',
                           line={
                               'width': 5,
                               'dash': 'dot'
                           },
                           text=limit_line_texts,
                           textposition="top center"
                           )
                )
    limit_line_texts[-1] = 'Severe apnea limit'
    f.add_trace(go.Scatter(x=timestamps, y=[11] * len(timestamps),
                           mode='lines+text',
                           name='Severe apnea limit',
                           line={
                               'width': 5,
                               'dash': 'dot'
                           },
                           text=limit_line_texts,
                           textposition="top center"
                           )
                )


def onenight_combined_fig(timestamps: list, parameters: list, parameter_names: list, night_nr: int):
    param = parameters[0]
    name = parameter_names[0]

    limit_line_texts = [''] * len(timestamps)

    f = go.Figure()
    # add the apnea limits
    addApneaLimits(f, limit_line_texts, timestamps)

    f.add_trace(go.Scatter(x=timestamps, y=param,
                           mode='lines+markers',
                           name=name
                           )
                )

    for i in range(1, len(parameters)):
        param = parameters[i]
        name = parameter_names[i]
        f.add_trace(go.Scatter(x=timestamps, y=param, mode='lines+markers', name=name))

    f.update_layout(
        title={
            'text': f'Night {night_nr}',
            'font': {
                'size': title_fontsize,
            },
            'x': x_align
        },
        xaxis_title="Timestamp",
        yaxis_title="Parameter value"
    )

    return f


def alltime_combined_fig(nights: int, y_data: list, parameter_names: list):
    param = y_data[0]
    name = parameter_names[0]
    x_data = list(range(nights))

    limit_line_texts = [''] * len(x_data)

    f = go.Figure()

    addApneaLimits(f, limit_line_texts, x_data)

    f.add_trace(go.Scatter(x=x_data, y=param,
                           mode='lines+markers',
                           name=name
                           )
                )

    for i in range(1, len(parameter_names)):
        param = y_data[i]
        name = parameter_names[i]

        f.add_trace(go.Scatter(x=x_data, y=param,
                               mode='lines+markers',
                               name=name
                               )
                    )

    f.update_layout(
        title={
            'text': f'History',
            'font': {
                'size': title_fontsize,
            },
            'x': x_align
        },
        xaxis_title="Night",
        yaxis_title="Parameter value"
    )

    return f


def show_graph_for_one_night(night_i: int):
    onenight_snores, onenight_x_timestamps = get_list_snore_for_night(night_i)
    onenight_heartrates = get_list_heartrates_mean_for_night(night_i)
    onenight_apneas = get_list_apnea_score_for_night(night_i)

    onenight_apneas = [score / nr for (score, nr) in onenight_apneas]

    data1 = [onenight_snores, onenight_heartrates, onenight_apneas]

    if onenight_snores and onenight_heartrates and onenight_apneas:
        f = onenight_combined_fig(onenight_x_timestamps, data1, names, night_i + 1)
        f.show()


def sleepQualityGraph(scores: list):
    f = go.Figure()
    f.add_trace(go.Scatter(x=list(range(len(scores))), y=scores,
                           name='Sleep Quality Score',
                           mode='lines+markers'

    ))

    f.update_layout(
        title={
            'text': f'Sleep Quality',
            'font': {
                'size': title_fontsize,
            },
            'x': x_align
        },
        xaxis_title="Night",
        yaxis_title="Score"
    )
    return f


if __name__ == '__main__':
    nr_nights = get_nr_nights()
    time_interval = 1
    names = ["Snores", "Heartrate", "Apnea"]

    print('Choose your option:')
    print('\t1 - for a specific night graph')
    print('\t2 - for entire history graph')
    print('\t3 - for all nights, separate graphs for each night')
    print('\t4 - for sleep quality score')

    option = int(input('Your option: '))

    if option == 1:
        night_index = int(input('The night index: '))  # the i-th night to create the graph for
        show_graph_for_one_night(night_index)

    elif option == 2:     # graph for all nights (entire history)
        alltime_snores = get_list_snores()
        alltime_heartrates = get_list_heartrates()
        alltime_apneas = get_list_apnea_scores()
        alltime_slept_times = get_list_time_slept()

        alltime_apneas = [score / nr for (score, nr) in alltime_apneas]

        names.append("Time slept")
        data2 = [alltime_snores, alltime_heartrates, alltime_apneas, alltime_slept_times]

        if alltime_snores and alltime_heartrates and alltime_apneas and alltime_slept_times:
            fig = alltime_combined_fig(nr_nights, data2, names)
            fig.show()

    elif option == 3:
        for night_idx in range(nr_nights):
            show_graph_for_one_night(night_idx)

    elif option == 4:
        sleepQuality = sleepQualityEachNight()
        fig = sleepQualityGraph(sleepQuality)
        fig.show()

    else:
        print('Wrong option!')
