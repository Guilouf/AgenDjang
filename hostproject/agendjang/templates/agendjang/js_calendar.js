// template dynamic js, why not,

function getCookie(name) {
    /*from django docs. parse cookie*/
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// wrapper for ajax put
function put(url, data, callback) {
    $.ajax({
        url: url,  // leave trailing /
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: callback,
    });
}

// $.post ajax is somewhat more buggy... even with json flag
function post(url, data, callback) {
    $.ajax({
        url: url,  // leave trailing /
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: callback,
    });
}

function remove(url, callback) {
    $.ajax({
        url: url,
        type: 'DELETE',
        contentType: 'application/json',
        success: callback,
    });
}

function djangoDate(date) {
    /* Build a fixed-format datetime string for the Django API from a native Date,
    using local time components, even when the date has no meaningful time part
    (e.g. midnight from a day click)
    => 2017-11-28T13:00:00
    */
    const pad = n => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
        `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function postDaterange(start, end, taskId, callback) {
    let postDateRange = {
            start_date: djangoDate(start),
            end_date: djangoDate(end),
            task: taskId,
        };
    post("{% url 'agendjang:api:dateranges-list'%}", postDateRange, callback)
}

function putDaterange(event, endOverride) {
    /*Modyfy daterange according to event data. endOverride lets eventDrop force
    a computed end date without mutating the (read-only) FullCalendar event.*/
    let daterange = {
        start_date: djangoDate(event.start),
        end_date: djangoDate(endOverride || event.end),
        task: event.extendedProps.taskId,
    };

    // jquery .put doesnt exist.. put wrapper
    put("{% url 'agendjang:api:dateranges-list'%}"+event.id+'/', daterange,
        function(data) {}
    );
}

function deleteDateRange(dateRangeId) {
    remove("{% url 'agendjang:api:dateranges-list'%}"+dateRangeId+'/',
        function(data) {}
    );
}

function postTaskFormData(date) {
    let formData = new FormData(document.querySelector('form'))

    // a task created by clicking a day spans the full day (24h = allDay, per the API's own convention)
    let end = new Date(date);
    end.setDate(end.getDate() + 1);

    let xhr = new XMLHttpRequest();
    xhr.responseType = 'json';  // allow to convert formData to json automatically
    xhr.onreadystatechange = function() {  // callback
    if (xhr.readyState === XMLHttpRequest.DONE) {
        let taskId = xhr.response.id
            // call function defined in parent window
            window.parent.postDaterange(date, end, taskId, function(response) {
                location.reload()  // refresh page
            })
        }
    }
    xhr.open("POST", "{% url 'agendjang:api:tasks-list' %}");
    xhr.send(formData)
}

$(document).ready(function() {  // called when page is completely loaded

    // send cookie value to request header
    $.ajaxSetup({
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    });

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: true,  // event on the calendar can be modified
        droppable: true, // allow external event drop
        forceEventDuration: true, // if not all day and no end date, create default end date
        slotLabelFormat: { hour: 'numeric', minute: '2-digit', omitZeroMinute: true, meridiem: false },  //24h date format
        firstDay: 1, // start monday

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        views: { // like general option, but only apply to specific views
            timeGridWeek: {
                dayHeaderFormat: { weekday: 'short', month: 'numeric', day: 'numeric' },
            },
        },

        events: "{% url 'agendjang:api:events-list'%}", // fullcalendar handles the call format

        dateClick: function(info) {
            const dayDate = info.date;

            $('#task_dialog').data('ajaxCall', function (){postTaskFormData(dayDate)});
            $('#task_dialog').find('.dialog-content').load("create_task", function() { // relative url, resolver useless
                // modify input button to send AJAX request
                $('#task_input')
                    .attr('onclick', '$(\'#task_dialog\').data(\'ajaxCall\')()')
                    .attr('type', 'button')
                    .val('SubmitAjax')  // rename field
            });
            document.querySelector('#task_dialog').showModal();
        },

        eventClick: function(info) {
            const event = info.event;
            $('#task_dialog')
                // callback called when pressing dialog unlink date button
                .data('deleteDate', function () {
                    deleteDateRange(event.id)  // remove event in db
                    event.remove();  // rm event in calendar
                    document.querySelector('#task_dialog').close() // closes dialog
                });
            $('#task_dialog').find('.dialog-content')
                .load("update_task/"+event.extendedProps.taskId, function () {
                    // add unlink button to dialog
                    $('#task_dialog').find('.dialog-content')
                        .append("<input type=\"button\" value=\"Unlink the date\"" +
                            " onclick=\"$(\'#task_dialog\').data(\'deleteDate\')()\" />")
                }); // relative url, resolver useless
            document.querySelector('#task_dialog').showModal();
        },

        // when dragndrop finished and datetime changed (internal event dragndrop)
        eventDrop: function(info) {
            const event = info.event;
            let end = event.end;
            if (event.allDay) {  // in our data model, an event is considered all day if it last 24hours
                // in fullcalendar, an allDay event just takes into account "start" and "allDay=true"
                end = new Date(event.start);
                end.setDate(end.getDate() + 1);
            }
            putDaterange(event, end)
        },

        // when timestamp resize is finished and time changed
        eventResize: function(info) {
            putDaterange(info.event)
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(info) {
            const event = info.event;

            // post a new daterange, but if form is cancelled it's keeped in db
            postDaterange(event.start, event.end, event.extendedProps.taskId, function(response) {
                // FullCalendar already auto-inserted its own client-side copy of this event on drop;
                // remove it before refetching, otherwise both it and the server's authoritative
                // version would be shown side by side until the next full page load
                event.remove();
                calendar.refetchEvents();
            });
        },

    });
    calendar.render();

    // makes tasks in the tag sidebar draggable onto the calendar
    new FullCalendar.Draggable(document.getElementById('tags'), {
        itemSelector: '.task_div',
        eventData: function(eventEl) {
            return {
                title: eventEl.dataset.title,
                extendedProps: { taskId: eventEl.dataset.taskId },
            };
        }
    });

});
