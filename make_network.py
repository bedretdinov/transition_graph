from database import CHData,SqliteConn
import pandas as pd
from tqdm import tqdm
import datetime
import numpy as np



flag = False
for day in range(1,60):
    print('get data from clickhouse day:{day} '.format(day=day))
    df = CHData.Query('''
        SELECT
               os_name,
               concat(toString(appmetrica_device_id),toString(session_id)) as id,
               session_id,
               appmetrica_device_id,
               event_datetime,
               event_name,
               date,
               JSONExtractString(event_json, 'screen')                    as screen,
               JSONExtractString(event_json, 'name')                      as name,
               JSONExtractString(event_json, 'action')                    as action,
               JSONExtractString(event_json, 'block_name')                as block_name
        FROM analytics.appmetrica_events
        WHERE date = today()-{day} AND event_name='hide_screen'
        AND isNotNull(session_id)
        ORDER BY toDateTime(event_datetime)
    '''.format(day=day))

    df = df.set_index(['appmetrica_device_id','id'])


    print('write to sql')

    if(flag==False):
        mode = 'replace'
        flag = True
    else:
        mode = 'append'

    print('mode ',mode)

    df.to_sql("sesions", SqliteConn, if_exists=mode, chunksize=15000)








flag = False
print('calculate events')
appmetrica_device_id = pd.read_sql_query('''
    SELECT
        DISTINCT appmetrica_device_id
    FROM sesions 
''', SqliteConn).appmetrica_device_id

dataNetwork = []
dataChain = []
for appid in tqdm(appmetrica_device_id):
    item = pd.read_sql_query('''
            SELECT
                   os_name,
                   session_id,
                   appmetrica_device_id,
                   event_name,
                   screen,
                   trim(name) as name,
                   action,
                   block_name,
                   event_datetime
            FROM sesions
            WHERE appmetrica_device_id = '{appid}'
            AND trim(name)!=''
            ORDER BY event_datetime ASC
    '''.format(appid=appid), SqliteConn)

    for sessid in item.session_id.unique():
        sesion_data = item[item['session_id'] == sessid]


        if (sesion_data.shape[0] < 2):
            continue

        if (sesion_data[sesion_data.name == 'checkout_thankyou_screen'].shape[0] != 0):
            type = 'order'
        else:
            type = 'dead'

        first_val = True
        event_line = []
        iteration_val = sesion_data.name.values.tolist()
        event_datetime = sesion_data.event_datetime.values.tolist()
        for event, next_event, start_time, end_time in zip(
                iteration_val,
                iteration_val[1:],
                event_datetime,
                event_datetime[1:]
        ):
            if(next_event=='checkout_thankyou_screen'):
                event_line.append(next_event)
                break

            if(event!=next_event):
                if(first_val):
                    event_line.append(event)
                    event_line.append(next_event)
                    first_val = False
                else:
                    event_line.append(next_event)

        dataChain.append({
            'event_line':",".join(event_line),
            'event_len': len(event_line),
            'event_unique_len': len(np.unique(event_line)),
            'session_start': sesion_data.event_datetime.max(),
            'session_end':  sesion_data.event_datetime.min(),
            'os_name':  sesion_data.os_name.values[0],
            'type':type
        })

        iteration_val = sesion_data.name.values.tolist()
        event_datetime = sesion_data.event_datetime.values.tolist()
        for event, next_event, start_time, end_time in zip(
                iteration_val,
                iteration_val[1:],
                event_datetime,
                event_datetime[1:]
        ):

            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

            delayed_second = (end_time-start_time).total_seconds()

            if (event == 'checkout_thankyou_screen'):
                break

            dataNetwork.append({
                'from': event,
                'to': next_event,
                'session_id': sessid,
                'appid': appid,
                'delayed_second': delayed_second,
                'date': str(sesion_data.event_datetime.max()).split(' ')[0],
                'os_name': sesion_data.os_name.values[0],
                'type': type,
            })


            if(len(dataNetwork)>5000):

                if (flag == False):
                    mode = 'replace'
                    flag = True
                else:
                    mode = 'append'

                pd.DataFrame(dataNetwork).to_sql("events_chains", SqliteConn, if_exists=mode, chunksize=100000)
                pd.DataFrame(dataChain).to_sql("events_line", SqliteConn, if_exists=mode, chunksize=100000)
                dataNetwork = []


pd.DataFrame(dataNetwork).to_sql("events_chains", SqliteConn, if_exists=mode, chunksize=100000)
pd.DataFrame(dataChain).to_sql("events_line", SqliteConn, if_exists=mode, chunksize=100000)




print('create index')

c = SqliteConn.cursor()

# Create index
c.execute('''CREATE INDEX idx_combine_1
ON events_line (type,event_line,session_start);''')

# Create index
c.execute('''CREATE INDEX idx_combine_2
ON events_line (type,session_start);''')

# Create index
c.execute('''CREATE INDEX idx_event_len
ON events_line (event_len);''')

# Create index
c.execute(''' CREATE INDEX idx_event_line
ON events_line (event_line); ''')

# Create index
c.execute(''' CREATE INDEX idx_os_name
ON events_line (os_name); ''')

# Create index
c.execute(''' CREATE INDEX idx_session_start
ON events_line (session_start); ''')

# Create index
c.execute(''' CREATE INDEX idx_from
ON events_chains (`from`); ''')

# Create index
c.execute(''' CREATE INDEX idx_to
ON events_chains (`to`); ''')

# Create index
c.execute(''' CREATE INDEX idx_eh_os_name
ON events_chains (os_name); ''')

# Create index
c.execute(''' CREATE INDEX idx_type
ON events_chains (type); ''')

# Create index
c.execute(''' CREATE INDEX idx_conbine_1
ON events_chains (`from`,`to`,type); ''')

# Create index
c.execute(''' CREATE INDEX idx_conbine_2
ON events_chains (`from`,`to`,type,os_name); ''')

# Save (commit) the changes
SqliteConn.commit()