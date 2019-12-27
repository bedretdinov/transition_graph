function loadToTable(response)
{

    preloader.hide()

     var titles = {}

     for( k in response.nodeDataArray){
         titles[response.nodeDataArray[k]['id']] = response.nodeDataArray[k]['text']
     }


     var htmlTable = ''

    htmlTable+='<thead class="thead-dark">'
    htmlTable+='<tr>'
    htmlTable+='<th>Переход с</th>'
    htmlTable+='<th>Переход на </th>'
    htmlTable+='<th>Среднее время задержки</th>'
    htmlTable+='<th>Кол-во переходов</th>'
    htmlTable+='<th>Кол-во переходов в процентах</th>'
    htmlTable+='<th>Уникальных пользователей</th>'
    htmlTable+='<th>процент уникальных пользователей от всех</th>'
    htmlTable+='</tr>'
    htmlTable+='</thead>'
    htmlTable+='<tbody>'


     for (k in response.linkDataArray){
        htmlTable+='<tr>'
            htmlTable+='<td>'+titles[response.linkDataArray[k]['from']]+'</td>'
            htmlTable+='<td>'+titles[response.linkDataArray[k]['to']]+'</td>'
            htmlTable+='<td>'+response.linkDataArray[k]['avg_delay']+'</td>'
            htmlTable+='<td>'+response.linkDataArray[k]['frequency']+'</td>'
            htmlTable+='<td>'+response.linkDataArray[k]['frequency_percent']+'</td>'
            htmlTable+='<td>'+response.linkDataArray[k]['unique_devices']+'</td>'
            htmlTable+='<td>'+response.linkDataArray[k]['unique_devices_percent']+'</td>'
        htmlTable+='</tr>'
     }
     htmlTable+='</tbody>'

     jQuery('#records_table').html(htmlTable);
}