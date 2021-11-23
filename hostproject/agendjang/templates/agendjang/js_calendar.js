// template dynamic js, why not,

// wrapper for ajax put
function put(url_, data_, callback_) {
    $.ajax({
        url: url_,  // leave trailing /
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data_),
        success: callback_,
    });
}

// $.post ajax is somewhat more buggy... even with json flag
function post(url_, data_, callback_) {
    $.ajax({
        url: url_,  // leave trailing /
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data_),
        success: callback_,
    });
}

function remove(url_, callback_) {
    $.ajax({
        url: url_,
        type: 'DELETE',
        contentType: 'application/json',
        success: callback_,
    });
}

function django_date(date_) {
    /* Wrapper for moment.js(used by fullcal),
     here the date have always the same format even if hours missing
    => 2017-11-28T13:00:00
    'T' is escaped because of a bug https://github.com/moment/moment/issues/4081
    */
    return date_.format('YYYY-MM-DD[T]HH:mm:ss');
}

function f_post_daterange(start, end, taskId, callback_) {
    let post_daterange = {
            start_date: django_date(start),
            end_date: django_date(end),
            task: taskId,
        };
    post("{% url 'api:dateranges-list'%}", post_daterange, callback_)
}

function put_daterange(event) {
    /*Modyfy daterange according to event data*/
    let daterange = {
        start_date: django_date(event.start),
        end_date: django_date(event.end),
        task: event.taskId,
    };

    // jquery .put doesnt exist.. put wrapper
    put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
        function(data) {}
    );
}

function deleteDateRange(dateRangeId) {
    remove("{% url 'api:dateranges-list'%}"+dateRangeId+'/',
        function(data) {}
    );
}

function postTaskFormData(datee) {
    let formData = new FormData(document.querySelector('form'))

    let xhr = new XMLHttpRequest();
    xhr.responseType = 'json';  // allow to convert formData to json automatically
    xhr.onreadystatechange = function() {  // callback
    if (xhr.readyState === XMLHttpRequest.DONE) {
        let taskId = xhr.response.id
            // call function defined in parent window
            window.parent.f_post_daterange(datee, datee, taskId, function(response) {
                location.reload()  // refresh page
            })
        }
    }
    xhr.open("POST", "{% url 'api:tasks-list' %}");
    xhr.send(formData)
}

$(document).ready(function() {  // called when page is completely loaded

    //load the accordiion UI for the accord class
    $(".accord").accordion({ collapsible: true, active: false }); // keep open multiple sections

    $('#calendar').fullCalendar({
        editable: true,  // event on the calendar can be modified
        droppable: true, // allow external event drop
        forceEventDuration: true, // if not all day and no end date, create default end date
        slotLabelFormat: 'H(:mm)',  //24h date format
        firstDay: 1, // start monday

        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay,listWeek'
        },
        views: { // like general option, but only apply to specific views
            week: {
                columnFormat: 'ddd D/M', // overrides also for month view
            },
        },

        events: "{% url 'api:events-list'%}", // fullcalendar handles the call format

        dayClick: function(datee) {

            $('#task_dialog').data('ajaxCall', function (){postTaskFormData(datee)}).load("create_task", function() { // relative url, resolver useless
                $('#task_dialog').dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
                // modify input button to send AJAX request
                $('#task_input')
                    .attr('onclick', '$(\'#task_dialog\').data(\'ajaxCall\')()')
                    .attr('type', 'button')
                    .val('SubmitAjax')  // rename field
            });
        },

        eventClick: function(event) {
            $('#task_dialog')
                // callback called when pressing dialog unlink date button
                .data('deleteDate', function () {
                    deleteDateRange(event.id)  // remove event in db
                    $("#calendar").fullCalendar('removeEvents', event.id);  // rm event in calendar
                    $('#task_dialog').dialog('close') // closes dialog
                })
                .load("update_task/"+event.taskId, function () {
                    // add unlink button to dialog
                    $('#task_dialog')
                        .append("<input type=\"button\" value=\"Unlink the date\"" +
                            " onclick=\"$(\'#task_dialog\').data(\'deleteDate\')()\" />")
                }) // relative url, resolver useless
                .dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
        },

        // when dragndrop finished and datetime changed (internal event dragndrop)
        eventDrop: function(event, delta, revertFunc) {
            if (event.allDay) {  // in our data model, an event is considered all day if it last 24hours
                // in fullcalendar, an allDay event just takes into account "start" and "allDay=true"
                event.end = new moment(event.start)
                event.end.add(1, 'days')
            }
            put_daterange(event)
        },

        // when timestamp resize is finished and time changed
        eventResize: function(event, delta, revertFunc) {
            put_daterange(event)
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(event, view) {

            // post a new daterange, but if form is cancelled it's keeped in db
            f_post_daterange(event.start, event.end, event.taskId, function(response) {
                event.id = response['id']; // id of event is id of daterange
                $('#calendar').fullCalendar('updateEvent', event);
            });
        },

    })

});
